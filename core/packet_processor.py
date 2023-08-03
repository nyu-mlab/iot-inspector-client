import time
import scapy.all as sc
import core.global_state as global_state
import core.model as model
import core.common as common
import core.networking as networking
import traceback
from core.tls_processor import extract_sni
import core.friendly_organizer as friendly_organizer


# How often to write the flow statistics to the database (in seconds)
FLOW_WRITE_INTERVAL = 2

# Temporarily holds the flow statistics; maps <src_device_mac_addr, dst_device_mac_addr, src_ip_addr, dst_ip_addr, src_port, dst_port, protocol> -> a dictionary with keys <start_ts, end_ts, byte_count, packet_count>
flow_dict = {}

# Timestamp of the last time the flow_dict was written to db
flow_dict_last_db_write_ts = {'_': 0}


def process_packet():

    pkt = global_state.packet_queue.get()

    try:
        process_packet_helper(pkt)

    except Exception as e:
        common.log('[Pkt Processor] Error processing packet: ' + str(e) + ' for packet: ' + str(pkt) + '\n' + traceback.format_exc())


def process_packet_helper(pkt):

    # Write pending flows to database if the flow_dict has not been updated for FLOW_WRITE_INTERVAL sec
    if time.time() - flow_dict_last_db_write_ts['_'] > FLOW_WRITE_INTERVAL:
        write_pending_flows_to_db()
        flow_dict_last_db_write_ts['_'] = time.time()

    # ====================
    # Process individual packets and terminate
    # ====================

    if sc.ARP in pkt:
        return process_arp(pkt)

    if sc.DHCP in pkt:
        return process_dhcp(pkt)

    # Must have Ether frame and IP frame.
    if not (sc.Ether in pkt and sc.IP in pkt):
        return

    # Ignore traffic to and from this host's IP
    if global_state.host_ip_addr in (pkt[sc.IP].src, pkt[sc.IP].dst):
        return

    # DNS
    if sc.DNS in pkt:
        return process_dns(pkt)

    # ====================
    # Process flows and their first packets
    # ====================

    process_client_hello(pkt)

    # Process flow
    return process_flow(pkt)


def process_arp(pkt):
    """
    Updates ARP cache upon receiving ARP packets, only if the packet is not
    spoofed.

    """
    if not ((pkt.op == 1 or pkt.op == 2)):
        return

    if pkt.hwsrc == global_state.host_mac_addr:
        return

    if pkt.psrc == '0.0.0.0':
        return

    ip_addr = pkt.psrc
    mac_addr = pkt.hwsrc

    # Update the devices table
    has_updated = False
    with model.write_lock:
        with model.db:
            device = model.Device.get_or_none(mac_addr=mac_addr)
            if device is None:
                # Never seen this device before, so create one
                model.Device.create(mac_addr=mac_addr, ip_addr=ip_addr)
                has_updated = True
            else:
                # Update the IP address if different
                if device.ip_addr != ip_addr:
                    device.ip_addr = ip_addr
                    device.save()
                    has_updated = True

    # Update the ARP cache
    global_state.arp_cache.update(ip_addr, mac_addr)
    if has_updated:
        common.log(f'[Pkt Processor] Updated ARP cache: {ip_addr} -> {mac_addr}')


def process_dns(pkt):

    src_mac_addr = pkt[sc.Ether].src
    dst_mac_addr = pkt[sc.Ether].dst

    # Find the device that makes this DNS request or response
    if global_state.host_mac_addr == src_mac_addr:
        device_mac_addr = dst_mac_addr
    elif global_state.host_mac_addr == dst_mac_addr:
        device_mac_addr = src_mac_addr
    else:
        return

    # This device cannot be the gateway
    try:
        gateway_mac_addr = global_state.arp_cache.get_mac_addr(global_state.gateway_ip_addr)
    except KeyError:
        return
    if device_mac_addr == gateway_mac_addr:
        return

    # Parse hostname
    try:
        hostname = pkt[sc.DNSQR].qname.decode('utf-8').lower()
    except Exception:
        return

    # Remove trailing dot from hostname
    if hostname[-1] == '.':
        hostname = hostname[0:-1]

    # Parse DNS response to extract IP addresses in A records
    ip_set = set()
    if sc.DNSRR in pkt and pkt[sc.DNS].an:
        for ix in range(pkt[sc.DNS].ancount):
            # Extracts A-records
            if pkt[sc.DNSRR][ix].type == 1:
                # Extracts IPv4 addr in A-record
                ip = pkt[sc.DNSRR][ix].rdata
                if networking.is_ipv4_addr(ip):
                    ip_set.add(ip)
                    # Write to cache
                    with global_state.global_state_lock:
                        global_state.hostname_dict[ip] = hostname

    # If we don't have an IP address, that's fine. We'll still store the domain queried, setting the IP address to empty.
    if not ip_set:
        ip_set.add('')

    # Write to domain-IP mapping to database
    created = False
    with model.write_lock:
        with model.db:
            for ip_addr in ip_set:
                _, created = model.Hostname.get_or_create(
                    device_mac_addr=device_mac_addr,
                    hostname=hostname,
                    ip_addr=ip_addr,
                    data_source='dns'
                )

    if created:
        common.log(f'[Pkt Processor] DNS: Device {device_mac_addr}: {hostname} -> {ip_set}')


def process_flow(pkt):

    # Must have TCP or UDP layer
    if sc.TCP in pkt:
        protocol = 'tcp'
        layer = sc.TCP
    elif sc.UDP in pkt:
        protocol = 'udp'
        layer = sc.UDP
    else:
        return

    # Parse packet
    src_mac_addr = pkt[sc.Ether].src
    dst_mac_addr = pkt[sc.Ether].dst
    src_ip_addr = pkt[sc.IP].src
    dst_ip_addr = pkt[sc.IP].dst
    src_port = pkt[layer].sport
    dst_port = pkt[layer].dport

    # No broadcast
    if dst_mac_addr == 'ff:ff:ff:ff:ff:ff' or dst_ip_addr == '255.255.255.255':
        return

    inspector_host_mac_addr = global_state.host_mac_addr

    # Find the actual MAC address that the Inspector host pretends to be if this
    # is a local communication; otherwise, assume that Inspector pretends to be
    # the gateway
    if src_mac_addr == inspector_host_mac_addr:
        try:
            src_mac_addr = global_state.arp_cache.get_mac_addr(src_ip_addr)
        except KeyError:
            src_mac_addr = ''
    elif dst_mac_addr == inspector_host_mac_addr:
        try:
            dst_mac_addr = global_state.arp_cache.get_mac_addr(dst_ip_addr)
        except KeyError:
            dst_mac_addr = ''
    else:
        return

    # Save the flow into a temporary flow queue
    flow_key = (
        src_mac_addr, dst_mac_addr, src_ip_addr, dst_ip_addr, src_port, dst_port, protocol
    )

    flow_stat_dict = flow_dict.setdefault(flow_key, {
        'start_ts': time.time(),
        'end_ts': time.time(),
        'byte_count': 0,
        'pkt_count': 0
    })
    flow_stat_dict['end_ts'] = time.time()
    flow_stat_dict['byte_count'] += len(pkt)
    flow_stat_dict['pkt_count'] += 1


def write_pending_flows_to_db():
    """Write flows in the flow_dict into the database (Flow table)"""

    with model.write_lock:
        with model.db:
            for flow_key, flow_stat_dict in flow_dict.items():

                # Unpack the flow key
                src_mac_addr, dst_mac_addr, src_ip_addr, dst_ip_addr, src_port, dst_port, protocol = flow_key

                # Find the country in both directions
                src_country = ''
                dst_country = ''
                if src_mac_addr == '' and src_ip_addr != '':
                    src_country = friendly_organizer.get_country_from_ip_addr(src_ip_addr)
                if dst_mac_addr == '' and dst_ip_addr != '':
                    dst_country = friendly_organizer.get_country_from_ip_addr(dst_ip_addr)

                # Fill in the hostname information
                src_hostname = friendly_organizer.get_hostname_from_ip_addr(src_ip_addr, in_memory_only=True)
                dst_hostname = friendly_organizer.get_hostname_from_ip_addr(dst_ip_addr, in_memory_only=True)

                # Fill out the registered domain info and tracker company info per hostname
                src_reg_domain = ''
                dst_reg_domain = ''
                src_tracker_company = ''
                dst_tracker_company = ''
                if src_hostname:
                    src_reg_domain = friendly_organizer.get_reg_domain(src_hostname)
                    src_tracker_company = friendly_organizer.get_tracker_company(src_hostname)
                if dst_hostname:
                    dst_reg_domain = friendly_organizer.get_reg_domain(dst_hostname)
                    dst_tracker_company = friendly_organizer.get_tracker_company(dst_hostname)

                # Write to database
                model.Flow.create(
                    start_ts=flow_stat_dict['start_ts'],
                    end_ts=flow_stat_dict['end_ts'],
                    src_device_mac_addr=src_mac_addr,
                    dst_device_mac_addr=dst_mac_addr,
                    src_port=src_port,
                    dst_port=dst_port,
                    src_ip_addr=src_ip_addr,
                    dst_ip_addr=dst_ip_addr,
                    src_country=src_country,
                    dst_country=dst_country,
                    src_hostname=src_hostname,
                    dst_hostname=dst_hostname,
                    src_reg_domain=src_reg_domain,
                    dst_reg_domain=dst_reg_domain,
                    src_tracker_company=src_tracker_company,
                    dst_tracker_company=dst_tracker_company,
                    protocol=protocol,
                    byte_count=flow_stat_dict['byte_count'],
                    packet_count=flow_stat_dict['pkt_count']
                )

    common.log('[Pkt Processor] Wrote {} flows to database. Pending packet_queue size: {}'.format(
        len(flow_dict), global_state.packet_queue.qsize()
    ))

    # Clear the flow_dict
    flow_dict.clear()


def process_dhcp(pkt):

    # Must be a DHCP Request broadcast
    if pkt[sc.Ether].dst != 'ff:ff:ff:ff:ff:ff':
        return

    try:
        option_dict = dict(
            [t for t in pkt[sc.DHCP].options if isinstance(t, tuple)]
        )
    except Exception:
        return

    try:
        device_hostname = option_dict.setdefault('hostname', '').decode('utf-8')
        if device_hostname == '':
            return
    except Exception:
        return

    device_mac = pkt[sc.Ether].src

    # Ignore DHCP responses from this host
    if device_mac == global_state.host_mac_addr:
        return

    # Update the devices table
    with model.write_lock:
        with model.db:
            device = model.Device.get_or_none(mac_addr=device_mac)
            if device is None:
                # Never seen this device before, so create one
                model.Device.create(mac_addr=device_mac, ip_addr='', dhcp_hostname=device_hostname)
            else:
                # Update the hostname if different
                if device.dhcp_hostname != device_hostname:
                    device.dhcp_hostname = device_hostname
                    device.save()

    common.log(f'[Pkt Processor] DHCP: Device {device_mac}: {device_hostname}')


def process_client_hello(pkt):
    """Extracts the SNI field from the ClientHello packet."""

    # Make sure that the Inspector host should be the destination of this packet
    if pkt[sc.Ether].dst != global_state.host_mac_addr:
        return

    sni = extract_sni(pkt)
    if not sni:
        return

    sni = sni.lower()

    # Write the SNI hostname to the `hostname` table of the database
    created = False
    with model.write_lock:
        with model.db:
            _, created = model.Hostname.get_or_create(
                device_mac_addr=pkt[sc.Ether].src,
                hostname=sni,
                ip_addr=pkt[sc.IP].dst,
                data_source='sni'
            )

    # Write to local cache
    with global_state.global_state_lock:
        global_state.hostname_dict[pkt[sc.IP].dst] = sni

    if created:
        common.log(f'[Pkt Processor] TLS: Device {pkt[sc.Ether].src}: {sni}')

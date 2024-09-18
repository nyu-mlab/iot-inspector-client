import time
import scapy.all as sc
import core.global_state as global_state
import core.common as common
from core.oui_parser import get_vendor
import core.networking as networking
import traceback
from core.tls_processor import extract_sni


def process_packet():

    pkt = global_state.packet_queue.get()

    try:
        process_packet_helper(pkt)

    except Exception as e:
        common.log('[Pkt Processor] Error processing packet: ' + str(e) + ' for packet: ' + str(pkt) + '\n' + traceback.format_exc())


def process_packet_helper(pkt):

    # ====================
    # Process individual packets and terminate
    # ====================

    if sc.ARP in pkt:
        return process_arp(pkt)

    # Must have Ether frame and IP frame.
    if not (sc.Ether in pkt and sc.IP in pkt):
        return

    # Ignore traffic to and from this host's IP
    if global_state.host_ip_addr in (pkt[sc.IP].src, pkt[sc.IP].dst):
        return

    # DNS
    if sc.DNS in pkt:
        return process_dns(pkt)

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

    # Check if the mapping is already in the arp cache
    need_to_update = False
    try:
        cached_mac_addr = global_state.arp_cache.get_mac_addr(ip_addr)
    except KeyError:
        need_to_update = True
    else:
        if cached_mac_addr != mac_addr:
            need_to_update = True

    if need_to_update:
        global_state.arp_cache.update(ip_addr, mac_addr)
        common.log(f'[Pkt Processor] ARP: {ip_addr} -> {mac_addr}')



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

    hostname = networking.get_reg_domain(hostname)

    # Update the recent hostname cache
    with global_state.global_state_lock:
        global_state.recent_hostnames_dict.setdefault(device_mac_addr, dict())[hostname] = int(time.time())

    device_mac_addr = f'{get_vendor(device_mac_addr)} ({device_mac_addr})'

    common.log(f'[Pkt Processor] DNS: Device {device_mac_addr}: {hostname}')



def process_client_hello(pkt):
    """Extracts the SNI field from the ClientHello packet."""

    # Make sure that the Inspector host should be the destination of this packet
    if pkt[sc.Ether].dst != global_state.host_mac_addr:
        return

    sni = extract_sni(pkt)
    if not sni:
        return

    sni = sni.lower()
    sni = networking.get_reg_domain(sni)
    device_mac_addr = pkt[sc.Ether].src

    # Update the recent hostname cache
    with global_state.global_state_lock:
        global_state.recent_hostnames_dict.setdefault(device_mac_addr, dict())[sni] = int(time.time())

    device_mac_addr = f'{get_vendor(device_mac_addr)} ({device_mac_addr})'

    common.log(f'[Pkt Processor] TLS: Device {device_mac_addr}: {sni}')



def process_flow(pkt):

    # Must have TCP or UDP layer
    if sc.TCP not in pkt and sc.UDP not in pkt:
        return

    # Parse packet
    src_mac_addr = pkt[sc.Ether].src
    dst_mac_addr = pkt[sc.Ether].dst
    dst_ip_addr = pkt[sc.IP].dst

    # No broadcast
    if dst_mac_addr == 'ff:ff:ff:ff:ff:ff' or dst_ip_addr == '255.255.255.255':
        return

    current_ts = int(time.time())

    with global_state.global_state_lock:

        # Record the number of outgoing packets
        packet_counter_dict = global_state.outgoing_packet_counter_dict.setdefault(src_mac_addr, dict())
        packet_count = packet_counter_dict.setdefault(current_ts, 0)
        packet_count += 1
        packet_counter_dict[current_ts] = packet_count

        # Record the number of outgoing bytes
        byte_counter_dict = global_state.outgoing_byte_counter_dict.setdefault(src_mac_addr, dict())
        byte_count = byte_counter_dict.setdefault(current_ts, 0)
        byte_count += len(pkt)
        byte_counter_dict[current_ts] = byte_count

        source_vendor = get_vendor(src_mac_addr)
        src_mac_addr = f'{source_vendor} ({src_mac_addr})'

        destination_vendor = get_vendor(dst_mac_addr)
        dst_mac_addr = f'{destination_vendor} ({dst_mac_addr})'





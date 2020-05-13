"""
Processes individual packets.

"""
from host_state import HostState
import scapy.all as sc
import scapy.layers.http as http
import utils
import hashlib
import time
import re
from syn_scan import SYN_SCAN_SEQ_NUM, SYN_SCAN_SOURCE_PORT


# pylint: disable=no-member


class PacketProcessor(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)
        self._host_state = host_state

    def process_packet(self, pkt):

        utils.safe_run(self._process_packet_helper, args=[pkt])

    def _process_packet_helper(self, pkt):

        if sc.ARP in pkt:
            return self._process_arp(pkt)

        if sc.DHCP in pkt:
            return self._process_dhcp(pkt)

        # SYN-ACK response to SYN scans
        if sc.TCP in pkt and pkt[sc.TCP].flags == 'SA' and sc.IP in pkt:
            tcp_layer = pkt[sc.TCP]
            if tcp_layer.dport == SYN_SCAN_SOURCE_PORT and tcp_layer.ack == SYN_SCAN_SEQ_NUM + 1:
                return self._process_syn_scan(pkt)

        # Must have Ether frame and IP frame.
        if not (sc.Ether in pkt and sc.IP in pkt):
            return

        src_mac = pkt[sc.Ether].src
        dst_mac = pkt[sc.Ether].dst

        src_oui = utils.get_oui(src_mac)
        dst_oui = utils.get_oui(dst_mac)

        # Include only devices for internal testing (if set)
        if utils.TEST_OUI_LIST:
            if not (src_oui in utils.TEST_OUI_LIST or
                    dst_oui in utils.TEST_OUI_LIST):
                return

        # Ignore traffic to and from this host's IP
        if self._host_state.host_ip in (pkt[sc.IP].src, pkt[sc.IP].dst):
            return

        # DNS
        if sc.DNS in pkt:
            self._process_dns(pkt)

        # Commented out the following. We want to see traffic between device and gateway.
        # # Ignore traffic to and from the gateway's IP
        # if self._host_state.gateway_ip in (pkt[sc.IP].src, pkt[sc.IP].dst):
        #    return

        # TCP/UDP
        if sc.TCP in pkt:
            protocol = 'tcp'
        elif sc.UDP in pkt:
            protocol = 'udp'
        else:
            return

        return self._process_tcp_udp_flow(pkt, protocol)

    def _process_arp(self, pkt):
        """
        Updates ARP cache upon receiving ARP packets, only if the packet is not
        spoofed.

        """
        try:
            if pkt.op == 2 and pkt.hwsrc != self._host_state.host_mac:
                self._host_state.set_ip_mac_mapping(pkt.psrc, pkt.hwsrc)

        except AttributeError:
            return

    def _process_syn_scan(self, pkt):
        """
        Receives SYN scan response from devices.

        """
        src_mac = pkt[sc.Ether].src
        device_id = utils.get_device_id(src_mac, self._host_state)
        device_port = pkt[sc.TCP].sport

        with self._host_state.lock:
            port_list = self._host_state.pending_syn_scan_dict.setdefault(device_id, [])
            if device_port not in port_list:
                port_list.append(device_port)
                utils.log('[SYN Scan Debug] Device {} ({}): Port {}'.format(
                    pkt[sc.IP].src, device_id, device_port
                ))

    def _process_dhcp(self, pkt):
        """
        Extracts the client hostname from DHCP Request packets.

        """
        try:
            option_dict = dict(
                [t for t in pkt[sc.DHCP].options if isinstance(t, tuple)]
            )

        except Exception:
            return

        try:
            device_hostname = option_dict.setdefault('hostname', '').decode('utf-8')
        except Exception:
            device_hostname = ''
        resolver_ip = option_dict.setdefault('name_server', '')

        with self._host_state.lock:

            if device_hostname:

                # Must be a DHCP Request broadcast
                if pkt[sc.Ether].dst != 'ff:ff:ff:ff:ff:ff':
                    return

                device_mac = pkt[sc.Ether].src
                device_id = utils.get_device_id(device_mac, self._host_state)

                self._host_state.pending_dhcp_dict[device_id] = device_hostname
                utils.log('[UPLOAD] DHCP Hostname:', device_hostname)

            if resolver_ip:

                # DHCP Offer broadcast
                if pkt[sc.Ether].dst == 'ff:ff:ff:ff:ff:ff':
                    device_id = 'broadcast'

                # DHCP ACK from router to device. The following block may not
                # actually be called at all, because the router is likely to
                # send the ACK packet directly to the device (rather than arp
                # spoofed)
                else:
                    device_ip = pkt[sc.IP].dst
                    try:
                        device_mac = self._host_state.ip_mac_dict[device_ip]
                    except KeyError:
                        return
                    device_id = utils.get_device_id(
                        device_mac, self._host_state)

                self._host_state.pending_resolver_dict[device_id] = \
                    resolver_ip

                utils.log(
                    '[UPLOAD] DHCP Resolver:', device_id, '-', resolver_ip)

    def _process_dns(self, pkt):

        src_mac = pkt[sc.Ether].src
        dst_mac = pkt[sc.Ether].dst

        src_ip = pkt[sc.IP].src
        dst_ip = pkt[sc.IP].dst

        # Find device ID
        if pkt[sc.DNS].qr == 0:
            # DNS request
            if dst_mac == self._host_state.host_mac:
                device_mac = src_mac
                resolver_ip = dst_ip
            else:
                return
        else:
            # DNS response
            if src_mac == self._host_state.host_mac:
                device_mac = dst_mac
                resolver_ip = src_ip
            else:
                return

        device_id = utils.get_device_id(device_mac, self._host_state)

        # Parse domain
        try:
            domain = pkt[sc.DNSQR].qname.decode('utf-8').lower()
        except Exception:
            return

        # Remove trailing dot from domain
        if domain[-1] == '.':
            domain = domain[0:-1]

        # Parse DNS response
        ip_set = set()
        if sc.DNSRR in pkt and pkt[sc.DNS].an:
            for ix in range(pkt[sc.DNS].ancount):
                # Extracts A-records
                if pkt[sc.DNSRR][ix].type == 1:
                    # Extracts IPv4 addr in A-record
                    ip = pkt[sc.DNSRR][ix].rdata
                    if utils.is_ipv4_addr(ip):
                        ip_set.add(ip)

        with self._host_state.lock:
            dns_key = (device_id, domain, resolver_ip, 0)
            current_ip_set = self._host_state \
                .pending_dns_dict.setdefault(dns_key, set())
            ip_set = ip_set | current_ip_set
            self._host_state.pending_dns_dict[dns_key] = ip_set

    def _process_tcp_udp_flow(self, pkt, protocol):

        if protocol == 'tcp':
            layer = sc.TCP
        elif protocol == 'udp':
            layer = sc.UDP
        else:
            return

        # Parse packet
        src_mac = pkt[sc.Ether].src
        dst_mac = pkt[sc.Ether].dst
        src_ip = pkt[sc.IP].src
        dst_ip = pkt[sc.IP].dst
        src_port = pkt[layer].sport
        dst_port = pkt[layer].dport

        # No broadcast
        if dst_mac == 'ff:ff:ff:ff:ff:ff' or dst_ip == '255.255.255.255':
            return

        # Only look at flows where this host pretends to be the gateway
        host_mac = self._host_state.host_mac

        # Extract TCP sequence and ack numbers for us to estimate flow size
        # later
        tcp_seq = None
        tcp_ack = None

        try:
            tcp_layer = pkt[sc.TCP]
            tcp_seq = tcp_layer.seq
            if tcp_layer.ack > 0:
                tcp_ack = tcp_layer.ack
        except Exception:
            pass
       
        # Determine flow direction
        if src_mac == host_mac:
            direction = 'inbound'
            device_mac = dst_mac
            device_port = dst_port
            remote_ip = src_ip
            remote_port = src_port
        elif dst_mac == host_mac:
            direction = 'outbound'
            device_mac = src_mac
            device_port = src_port
            remote_ip = dst_ip
            remote_port = dst_port
        else:
            return

        # Anonymize device mac
        device_id = utils.get_device_id(device_mac, self._host_state)

        # Get remote device_id for internal book-keeping purpose
        remote_device_id = ''
        remote_ip_is_inspector_host = 0 # True (1) or False (0)
        try:
            with self._host_state.lock:
                real_remote_device_mac = self._host_state.ip_mac_dict[remote_ip]
                remote_device_id = utils.get_device_id(real_remote_device_mac, self._host_state)
                if remote_ip == self._host_state.host_ip:
                    remote_ip_is_inspector_host = 1
        except Exception:
            pass

        # Construct flow key
        flow_key = (
            device_id, device_port, remote_ip, remote_port, protocol
        )
        flow_key_str = ':'.join([str(item) for item in flow_key])

        flow_ts = time.time()

        # Initialize flow_stats. Note: TCP byte counts may include out-of-order
        # packets and RSTs. On the other hand, TCP sequence number shows how
        # many unique bytes are transmitted in a flow; this number does not
        # consider the size of headers (Eth + IP + TCP = 66 bytes in my
        # experiment), out-of-order packets, or RSTs.
        flow_stats = {
            'inbound_byte_count': 0,
            'inbound_tcp_seq_min_max': (None, None),
            'inbound_tcp_ack_min_max': (None, None),
            'outbound_byte_count': 0,
            'outbound_tcp_seq_min_max': (None, None),
            'outbound_tcp_ack_min_max': (None, None),
            'syn_originator': None,
            'internal_remote_device_id': remote_device_id,
            'internal_first_packet_originator': '',
            'internal_remote_ip_is_inspector_host': remote_ip_is_inspector_host,
            'internal_inbound_pkt_count': 0,
            'internal_outbound_pkt_count': 0,
            'internal_flow_ts_min': flow_ts,
            'internal_flow_ts_max': flow_ts,
            'internal_flow_key': flow_key_str
        }
        with self._host_state.lock:
            flow_stats = self._host_state.pending_flow_dict \
                .setdefault(flow_key, flow_stats)

        # Identify who sent out the first UDP packet in this flow
        if flow_stats['internal_first_packet_originator'] == '':
            if direction == 'inbound':
                flow_stats['internal_first_packet_originator'] = 'remote'
            else:
                flow_stats['internal_first_packet_originator'] = 'local'

        # Construct flow_stats
        flow_stats[direction + '_byte_count'] += len(pkt)
        flow_stats[direction + '_tcp_seq_min_max'] = utils.get_min_max_tuple(
            flow_stats[direction + '_tcp_seq_min_max'], tcp_seq)
        flow_stats[direction + '_tcp_ack_min_max'] = utils.get_min_max_tuple(
            flow_stats[direction + '_tcp_ack_min_max'], tcp_ack)
        flow_stats['internal_' + direction + '_pkt_count'] += 1
        flow_stats['internal_flow_ts_max'] = flow_ts

        # Who initiated the SYN packet
        syn_originator = None
        try:
            if pkt[sc.TCP].flags == 2:
                if src_ip == remote_ip:
                    syn_originator = 'remote'
                else:
                    syn_originator = 'local'
        except Exception:
            pass
        
        if syn_originator and flow_stats['syn_originator'] is None:
            flow_stats['syn_originator'] = syn_originator

        # Extract UA and Host
        if remote_port == 80 and protocol == 'tcp':
            self._process_http(pkt, device_id, remote_ip)

        # Extract SNI from TLS client handshake
        if protocol == 'tcp':
            self._process_tls(pkt, device_id)

        with self._host_state.lock:
            self._host_state.byte_count += len(pkt)

    def _process_http(self, pkt, device_id, remote_ip):
        self._process_http_user_agent(pkt, device_id)
        self._process_http_host(pkt, device_id, remote_ip)

    def _process_http_user_agent(self, pkt, device_id):

        try:
            ua = pkt[http.HTTPRequest].fields['User_Agent'].decode('utf-8')
        except Exception as e:
            return
        
        with self._host_state.lock:
            self._host_state \
                .pending_ua_dict \
                .setdefault(device_id, set()) \
                .add(ua)

        utils.log('[UPLOAD] User-Agent:', ua)

    def _process_http_host(self, pkt, device_id, remote_ip):

        try:
            http_host = pkt[http.HTTPRequest].fields['Host'].decode('utf-8')
        except Exception as e:
            return
        
        device_port = pkt[sc.TCP].sport

        with self._host_state.lock:
            self._host_state \
                .pending_dns_dict \
                .setdefault(
                    (device_id, http_host, 'http-host', device_port), set()) \
                .add(remote_ip)

        utils.log('[UPLOAD] HTTP host:', http_host)

    def _process_tls(self, pkt, device_id):
        """Analyzes client hellos and parses SNI and fingerprints."""

        tls_dict = get_tls_dict(pkt, self._host_state)

        if not tls_dict:
            return

        tls_dict['device_id'] = device_id

        # Upload SNI
        if 'client_hello' in tls_dict and tls_dict['client_hello']['sni']:

            sni = tls_dict['client_hello']['sni']
            remote_ip = tls_dict['client_hello']['remote_ip']
            device_port = tls_dict['client_hello']['device_port']

            with self._host_state.lock:
                self._host_state \
                    .pending_dns_dict \
                    .setdefault(
                        (device_id, sni, 'sni', device_port),
                        set())\
                    .add(remote_ip)

            utils.log('[UPLOAD] SNI:', sni)

        # Upload fingerprint dict
        with self._host_state.lock:
            self._host_state.pending_tls_dict_list.append(tls_dict)


def is_grease(int_value):
    """
    Returns if a value is GREASE.

    See https://tools.ietf.org/html/draft-ietf-tls-grease-01

    """
    hex_str = hex(int_value)[2:].lower()
    if len(hex_str) < 4:
        return False

    first_byte = hex_str[0:2]
    last_byte = hex_str[-2:]

    return (
        first_byte[1] == 'a' and
        last_byte[1] == 'a' and
        first_byte == last_byte
    )


def get_tls_dict(pkt, host_state):
    """
    Referenced papers:

     - https://tlsfingerprint.io/static/frolov2019.pdf
     - https://zakird.com/papers/https_interception.pdf
     - https://conferences.sigcomm.org/imc/2018/papers/imc18-final193.pdf

    """
    tls_dict = {}

    for ix in range(3, 100):

        try:
            layer = pkt[ix]
        except IndexError:
            break

        if layer.name == 'TLS Client Hello':
            tls_dict['client_hello'] = get_client_hello(pkt, layer)

        if layer.name == 'TLS Server Hello':
            tls_dict['server_hello'] = get_server_hello(pkt, layer, host_state)

        if layer.name == 'TLS Certificate List':
            if pkt[sc.IP].src in host_state.get_ip_mac_dict_copy():
                tls_dict['client_cert'] = get_client_cert(pkt, layer)

    return tls_dict


def get_client_hello(pkt, layer):

    extensions = getattr(layer, 'extensions', [])
    extension_types = []
    sni = None

    # Remove GREASE values from cipher_suites
    cipher_suites = getattr(layer, 'cipher_suites', [])
    length_before_removing_grease = len(cipher_suites)
    cipher_suites = [v for v in cipher_suites if not is_grease(v)]
    length_after_removing_grease = len(cipher_suites)
    cipher_suite_uses_grease = \
        (length_before_removing_grease != length_after_removing_grease)

    # Extract SNI, per
    # https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#tls-extensiontype-values-1
    extension_uses_grease = False
    for ex in extensions:
        try:
            # Remove grease values
            if is_grease(ex.type):
                extension_uses_grease = True
                continue
            extension_types.append(ex.type)
            if ex.type == 0:
                sni = str(ex.server_names[0].data)
        except Exception:
            pass

    version = getattr(layer, 'version', None)

    return {
        'type': 'client_hello',
        'version': version,
        'cipher_suites': cipher_suites,
        'cipher_suite_uses_grease': cipher_suite_uses_grease,
        'compression_methods':
            getattr(layer, 'compression_methods', None),
        'extension_types': extension_types,
        'extension_details': repr(extensions),
        'extension_uses_grease': extension_uses_grease,
        'sni': sni,
        'remote_ip': pkt[sc.IP].dst,
        'remote_port': pkt[sc.TCP].dport,
        'device_ip': pkt[sc.IP].src,
        'device_port': pkt[sc.TCP].sport,
        'client_ts': time.time()
    }


def get_server_hello(pkt, layer, host_state):

    if pkt[sc.IP].src in host_state.get_ip_mac_dict_copy():
        device_ip = pkt[sc.IP].src
        remote_ip = pkt[sc.IP].dst
        device_port = pkt[sc.TCP].sport
        remote_port = pkt[sc.TCP].dport
    else:
        device_ip = pkt[sc.IP].dst
        remote_ip = pkt[sc.IP].src
        device_port = pkt[sc.TCP].dport
        remote_port = pkt[sc.TCP].sport

    return {
        'type': 'server_hello',
        'version': getattr(layer, 'version', None),
        'cipher_suite': getattr(layer, 'cipher_suite', None),
        'device_ip': device_ip,
        'device_port': device_port,
        'remote_ip': remote_ip,
        'remote_port': remote_port,
        'client_ts': time.time()
    }


def get_client_cert(pkt, layer):

    layer_str = repr(layer)

    pubkey = ''
    signature = ''

    match = re.search(r'( pubkey=<[^>]+>)', layer_str)
    if match:
        pubkey = hashlib.sha256(match.group(1)).hexdigest()

    match = re.search(r'( signature=<[^>]+>)', layer_str)
    if match:
        signature = hashlib.sha256(match.group(1)).hexdigest()

    return {
        'type': 'client_cert',
        'pubkey': pubkey,
        'signature': signature,
        'hash': hashlib.sha256(layer_str).hexdigest(),
        'remote_ip': pkt[sc.IP].dst,
        'remote_port': pkt[sc.TCP].dport,
        'device_ip': pkt[sc.IP].src,
        'device_port': pkt[sc.TCP].sport,
        'client_ts': time.time()
    }

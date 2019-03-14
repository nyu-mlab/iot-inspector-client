"""
Processes individual packets.

"""
from host_state import HostState
import scapy_ssl_tls.ssl_tls as ssl_tls # noqa
import scapy_http.http as http
import scapy.all as sc
import utils
import hashlib


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

        # Ignore traffic to and from the gateway's IP
        if self._host_state.gateway_ip in (pkt[sc.IP].src, pkt[sc.IP].dst):
            return

        # Get gateway's MAC
        try:
            with self._host_state.lock:
                gateway_mac = self._host_state.ip_mac_dict[
                    self._host_state.gateway_ip
                ]
        except KeyError:
            return

        # Communication must be between this host's MAC (acting as a gateway)
        # and a non-gateway device
        host_mac = self._host_state.host_mac
        this_host_as_gateway = (
            (src_mac == host_mac and dst_mac != gateway_mac) or
            (dst_mac == host_mac and src_mac != gateway_mac)
        )
        if not this_host_as_gateway:
            return

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

    def _process_dhcp(self, pkt):
        """
        Extracts the client hostname from DHCP Request packets.

        """
        try:
            if pkt[sc.Ether].dst != 'ff:ff:ff:ff:ff:ff':
                return

            device_mac = pkt[sc.Ether].src

            device_hostname = dict(
                [t for t in pkt[sc.DHCP].options if isinstance(t, tuple)]
            )['hostname']

        except Exception:
            return

        device_id = utils.get_device_id(device_mac, self._host_state)
        with self._host_state.lock:
            self._host_state.pending_dhcp_dict[device_id] = \
                device_hostname

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
            domain = pkt[sc.DNSQR].qname.lower()
        except AttributeError:
            return

        # Remove trailing dot from domain
        if domain.endswith('.'):
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
            dns_key = (device_id, domain, resolver_ip)
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
        host_gateway_inbound = (src_mac == host_mac)
        host_gateway_outbound = (dst_mac == host_mac)
        if not (host_gateway_inbound or host_gateway_outbound):
            return

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

        # Construct flow key
        flow_key = (
            device_id, device_port, remote_ip, remote_port, protocol
        )

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
            'outbound_tcp_ack_min_max': (None, None)
        }
        with self._host_state.lock:
            flow_stats = self._host_state.pending_flow_dict \
                .setdefault(flow_key, flow_stats)

        # Construct flow_stats
        flow_stats[direction + '_byte_count'] += len(pkt)
        flow_stats[direction + '_tcp_seq_min_max'] = utils.get_min_max_tuple(
            flow_stats[direction + '_tcp_seq_min_max'], tcp_seq)
        flow_stats[direction + '_tcp_ack_min_max'] = utils.get_min_max_tuple(
            flow_stats[direction + '_tcp_ack_min_max'], tcp_ack)

        # Extract UA and Host
        if remote_port == 80 and protocol == 'tcp':
            self._process_http(pkt, device_id, remote_ip)

        # Extract SNI from TLS client handshake
        if protocol == 'tcp' and direction == 'outbound':
            self._process_tls(pkt, device_id, remote_ip)

        with self._host_state.lock:
            self._host_state.byte_count += len(pkt)

    def _process_http(self, pkt, device_id, remote_ip):

        self._process_http_user_agent(pkt, device_id)
        self._process_http_host(pkt, device_id, remote_ip)

    def _process_http_user_agent(self, pkt, device_id):

        try:
            ua = pkt[http.HTTPRequest].fields['User-Agent']
        except Exception:
            return

        with self._host_state.lock:
            self._host_state \
                .pending_ua_dict \
                .setdefault(device_id, set()) \
                .add(ua)

        utils.log('[UPLOAD] User-Agent:', ua)

    def _process_http_host(self, pkt, device_id, remote_ip):

        try:
            http_host = pkt[http.HTTPRequest].fields['Host']
        except Exception:
            return

        with self._host_state.lock:
            self._host_state \
                .pending_dns_dict \
                .setdefault((device_id, http_host, 'http-host'), set()) \
                .add(remote_ip)

        utils.log('[UPLOAD] HTTP host:', http_host)

    def _process_tls(self, pkt, device_id, remote_ip):
        """Analyzes client hellos and parses SNI and fingerprints."""

        fingerprint = get_tls_fingerprint(pkt)

        if not fingerprint:
            return

        fingerprint['device_id'] = device_id

        # Upload SNI
        if fingerprint['sni']:

            with self._host_state.lock:
                self._host_state \
                    .pending_dns_dict \
                    .setdefault((device_id, fingerprint['sni'], 'sni'), set())\
                    .add(remote_ip)

            utils.log('[UPLOAD] SNI:', fingerprint['sni'])

        # Upload fingerprint dict
        with self._host_state.lock:
            self._host_state.pending_tls_dict[fingerprint['hash']] = \
                fingerprint


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


def get_tls_fingerprint(pkt):
    """
    Referenced papers:

     - https://tlsfingerprint.io/static/frolov2019.pdf
     - https://zakird.com/papers/https_interception.pdf

    """
    fingerprint = {}

    for ix in range(3, 100):

        try:
            layer = pkt[ix]
        except IndexError:
            break

        if layer.name == 'TLS Client Hello':

            extensions = getattr(layer, 'extensions', [])
            extension_types = []
            sni = None

            # Remove GREASE values from cipher_suites
            cipher_suites = getattr(layer, 'cipher_suites', [])
            cipher_suites = [v for v in cipher_suites if not is_grease(v)]

            # Extract SNI, per
            # https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#tls-extensiontype-values-1
            for ex in extensions:
                try:
                    # Remove grease values
                    if is_grease(ex.type):
                        continue
                    extension_types.append(ex.type)
                    if ex.type == 0:
                        sni = str(ex.server_names[0].data)
                except Exception:
                    pass

            version = getattr(layer, 'version', None)

            fingerprint_hash = hashlib.sha256(
                str(version) +
                str(set(cipher_suites)) +
                str(set(extension_types))
            ).hexdigest()[0:10]

            fingerprint.update({
                'hash': fingerprint_hash,
                'version': version,
                'cipher_suites': cipher_suites,
                'compression_methods':
                    getattr(layer, 'compression_methods', None),
                'extension_types': extension_types,
                'extension_details': repr(extensions),
                'sni': sni
            })
            break

    return fingerprint

"""
Processes individual packets.

"""
from host_state import HostState
import scapy.all as sc
import utils


class PacketProcessor(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)
        self._host_state = host_state

    def process_packet(self, pkt):

        with self._host_state.lock:
            self._host_state.packet_count += 1

        if sc.ARP in pkt:
            return self._process_arp(pkt)

        # Must have Ether frame.
        if sc.Ether not in pkt:
            return

        # No broadcast
        if sc.IP not in pkt:
            return

        # DNS response
        if sc.DNS in pkt and sc.DNSRR in pkt and pkt[sc.DNS].an:
            return self._process_dns(pkt)

        # TCP/UDP
        if sc.TCP in pkt:
            return self._process_tcp_udp(pkt, 'tcp')
        if sc.UDP in pkt:
            return self._process_tcp_udp(pkt, 'udp')

    def _process_arp(self, pkt):
        """
        Updates ARP cache upon receiving ARP packets, only if the packet is not
        spoofed.

        """
        try:
            if pkt.op == 2 and pkt.hwsrc != self._host_state.host_mac:
                self._host_state.set_ip_mac_mapping(pkt.psrc, pkt.hwsrc)
                utils.log('[ARP] Added:', pkt.psrc, '->', pkt.hwsrc)

        except AttributeError:
            pass

    def _process_dns(self, pkt):

        domain = pkt[sc.DNS].qd.qname
        device_mac = pkt[sc.Ether].dst

        # No DNS requests from this host
        if device_mac == self._host_state.host_mac:
            return

        # Remove trailing dot from domain
        if domain.endswith('.'):
            domain = domain[0:-1]

        ip_set = set()
        for ix in range(pkt[sc.DNS].ancount):
            # Extracts A-records
            if pkt[sc.DNSRR][ix].type == 1:
                # Extracts IPv4 addr in A-record
                ip = pkt[sc.DNSRR][ix].rdata
                if utils.is_ipv4_addr(ip):
                    ip_set.add(ip)

        with self._host_state.lock:
            self._host_state.pending_dns_responses.append({
                'domain': domain,
                'ip_set': ip_set
            })

    def _process_tcp_udp(self, pkt, protocol):

        if protocol == 'tcp':
            layer = sc.TCP
        elif protocol == 'udp':
            layer = sc.UDP
        else:
            return

        pkt_dict = {
            'length': len(pkt),
            'protocol': protocol,
            'src_mac': pkt[sc.Ether].src,
            'dst_mac': pkt[sc.Ether].dst,
            'src_ip': pkt[sc.IP].src,
            'dst_ip': pkt[sc.IP].dst,
            'src_port': pkt[layer].sport,
            'dst_port': pkt[layer].dport,
        }

        # No broadcast
        if pkt_dict['dst_mac'] == 'ff:ff:ff:ff:ff:ff':
            return
        if pkt_dict['dst_ip'] == '255.255.255.255':
            return

        host_mac = self._host_state.host_mac
        ip_prefix = self._host_state.ip_prefix

        # Only look at flows where this host pretends to be the gateway
        host_gateway_inbound = pkt_dict['src_mac'] == host_mac and \
            pkt_dict['dst_ip'].startswith(ip_prefix)
        host_gateway_outbound = pkt_dict['dst_mac'] == host_mac and \
            pkt_dict['src_ip'].startswith(ip_prefix)
        if not (host_gateway_inbound or host_gateway_outbound):
            return

        # Reformat pkt to use the device vs remote notation
        if pkt_dict['src_mac'] == host_mac:
            pkt_dict = {
                'direction': 'inbound',
                'length': len(pkt),
                'protocol': protocol,
                'device_mac': pkt_dict['dst_mac'],
                'device_ip': pkt_dict['dst_ip'],
                'remote_ip': pkt_dict['src_ip'],
                'remote_port': pkt_dict['src_port']
            }
        elif pkt_dict['dst_mac'] == host_mac:
            pkt_dict = {
                'direction': 'outbound',
                'length': len(pkt),
                'protocol': protocol,
                'device_mac': pkt_dict['src_mac'],
                'device_ip': pkt_dict['src_ip'],
                'remote_ip': pkt_dict['dst_ip'],
                'remote_port': pkt_dict['dst_port']
            }
        else:
            return

        # Ignore gateway
        is_gateway_traffic = self._host_state.gateway_ip in (
            pkt_dict['device_ip'], pkt_dict['remote_ip']
        )
        if is_gateway_traffic:
            return

        # Send data to cloud
        with self._host_state.lock:
            self._host_state.pending_pkts.append(pkt_dict)

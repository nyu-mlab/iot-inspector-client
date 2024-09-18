"""
Discovers local devices via ARP scanning. Populates the devices table with devices. Constantly updates the default routes.

By default, all devices are inspected.

"""
import scapy.all as sc
import core.global_state as global_state
import core.common as common
import core.networking as networking


def start_arp_scanner():

    # Update routes
    networking.update_network_info()

    # Sends an ARP request to every IP address on the network
    ip_range = networking.get_network_ip_range()
    common.log(f'[ARP Scanner] Scanning {len(ip_range)} IP addresses.')

    for ip in ip_range:

        host_mac = global_state.host_mac_addr

        arp_pkt = sc.Ether(src=host_mac, dst="ff:ff:ff:ff:ff:ff") / \
            sc.ARP(pdst=ip, hwsrc=host_mac, hwdst="ff:ff:ff:ff:ff:ff")

        sc.sendp(arp_pkt, iface=sc.conf.iface, verbose=0)

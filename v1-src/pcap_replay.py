"""
Loads pcaps. Rewrites destination MAC, so that IoT Inspector can read
these packets. For internal testing only.

"""
import scapy.all as sc
import sys


ORIGINAL_GATEWAY_MAC_LIST = [
    'b8:27:eb:00:bd:7e',
    'b8:27:eb:5d:95:57',
    'b8:27:eb:55:e8:2b',
    'b8:27:eb:f7:a1:45'
]

NEW_GATEWAY_MAC = '8c:85:90:d4:49:66'


def main():

    itr_list = []
    for pcap_file in sys.argv[1:]:
        itr_list.append(sc.PcapReader(pcap_file))

    while itr_list:

        itr = itr_list.pop(0)

        try:
            pkt = itr.next()
        except StopIteration:
            continue

        itr_list.append(itr)
        rewrite_pkt(pkt)


def rewrite_pkt(pkt):

    if sc.Ether not in pkt:
        return

    mac_pkt = pkt[sc.Ether]

    if mac_pkt.src in ORIGINAL_GATEWAY_MAC_LIST:
        mac_pkt.src = NEW_GATEWAY_MAC

    elif mac_pkt.dst in ORIGINAL_GATEWAY_MAC_LIST:
        mac_pkt.dst = NEW_GATEWAY_MAC
    else:
        return

    sc.sendp(pkt, verbose=0)


if __name__ == '__main__':
    main()

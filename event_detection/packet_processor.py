import logging
import scapy.all as sc
import libinspector.global_state as global_state


logger = logging.getLogger(__name__)

def start():

    pkt = global_state.packet_queue.get()

    try:
        process_packet_helper(pkt)

    except Exception as e:
        logger.error(f'[Pkt Processor] Error processing packet: {e} for packet: {pkt}\n{traceback.format_exc()}')


def process_packet_helper(pkt):

    # ====================
    # Process individual packets and terminate
    # ====================

    if sc.ARP in pkt:
        return None

    if sc.DHCP in pkt:
        return None
    
    # Must have Ether frame and IP frame.
    if not (sc.Ether in pkt and sc.IP in pkt):
        return


    # Ignore traffic to and from this host's IP. Hopefully we don't hit this statement because the sniff filter already excludes this host's IP.
    if global_state.host_ip_addr in (pkt[sc.IP].src, pkt[sc.IP].dst):
        logger.debug(f'[Pkt Processor] Ignoring packet to/from host IP: {pkt.summary()}')
        return

    # DNS
    if sc.DNS in pkt:
        return None

    print(f'[Pkt Processor] Processing packet: {pkt.summary()}')
    # # ====================
    # # Process flows and their first packets
    # # ====================

    # logger.debug(f'[Pkt Processor] Processing packet: {pkt.summary()}')

    # process_client_hello(pkt)

    # # Process flow
    # return process_flow(pkt)

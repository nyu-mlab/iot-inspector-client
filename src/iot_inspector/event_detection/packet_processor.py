import logging
import scapy.all as sc
import traceback
import libinspector.global_state as libinspector_state
from . import global_state


logger = logging.getLogger(__name__)

# data structure to hold seen packets for retransmission detection 
seen_packets = set()

# In our current pipeline design, the packet processor is responsible
# for filtering out irrelevant packets and putting relevant packets into
# the flow queue for burst processing. The burst processor will then 
# assemble bursts from the flow queue and put completed bursts into 
# the pending burst queue for feature generation and inference.

# following function is not used in the current pipeline design, 
# but we keep it here for potential future use when we want to 
# do some packet-level feature extraction or processing before burst assembly. 
def start():
    pkt = global_state.packet_queue.get()
    try:
        process_packet_helper(pkt)
    except Exception as e:
        logger.error(f'[Pkt Processor] Error processing packet: {e} for packet: {pkt}\n{traceback.format_exc()}')


def filter_packet(pkt: sc.Packet):

    # ====================
    # Process individual packets and terminate
    # ====================

    if sc.ARP in pkt:
        return None

    if sc.DHCP in pkt:
        return None
    
    # Must have Ether frame and IP frame.
    if not (sc.Ether in pkt and sc.IP in pkt):
        return None


    # Ignore traffic to and from this host's IP. Hopefully we don't hit this statement because the sniff filter already excludes this host's IP.
    if libinspector_state.host_ip_addr in (pkt[sc.IP].src, pkt[sc.IP].dst):
        logger.debug(f'[Pkt Processor] Ignoring packet to/from host IP: {pkt.summary()}')
        return None

    # DNS
    if sc.DNS in pkt:
        return None
    
    # Ignore TCP retransmissions
    if sc.TCP in pkt :
        if process_retransmission(pkt):
            # logger.info(f'[Pkt Processor] Ignoring TCP retransmission packet: {pkt.summary()}')
            return None
    
    # Ignore duplicate UDP packets    
    if sc.UDP in pkt:
        if is_duplicate_udp(pkt):
            # logger.info(f'[Pkt Processor] Ignoring duplicate UDP packet: {pkt.summary()}')
            return None

    # print(f'[Pkt Processor] Processing packet: {pkt.summary()}')
    # Put the packet into the flow queue for further processing
    # the flow queue is processed by the burst processor thread
    return pkt


def process_packet_helper(pkt: sc.Packet):
    filtered_pkt = filter_packet(pkt)
    if filtered_pkt is None:
        return

    # Put the packet into the flow queue for further processing
    # the flow queue is processed by the burst processor thread
    global_state.flow_queue.put(filtered_pkt)


# # Packet deduplication and retransmission detection
def process_retransmission(pkt: sc.Packet):
    global seen_packets

    if len(seen_packets) > 5000:
        seen_packets = set(list(seen_packets)[-1000:])  

    try:
        packet_hash = hash((pkt[sc.IP].src, pkt[sc.IP].dst, pkt[sc.TCP].seq, pkt[sc.TCP].ack))
    except AttributeError:
        # If the packet is not TCP, we don't need to check for retransmission
        logger.debug("[Packet Processor] Not a TCP packet - retransmission check skipped")
        return False
    
    if packet_hash in seen_packets:
        # packet is a duplicate retransmission
        return True
    else:
        seen_packets.add(packet_hash)
        return False
    
# Check packet deduplication for UDP packets
def is_duplicate_udp(pkt: sc.Packet) -> bool:
    global seen_packets
   
    if len(seen_packets) > 5000:
        # Keep the last 20% packets
        seen_packets = set(list(seen_packets)[-1000:])  

    try:
        packet_hash = hash(
            (pkt[sc.IP].src,
            pkt[sc.IP].dst,
            pkt[sc.UDP].sport, 
            pkt[sc.UDP].dport, 
            bytes(pkt.payload))
        )
    except AttributeError:
        # If the packet is not TCP or UDP, we don't need to check for retransmission
        logger.debug("[Packet Processor] Not a TCP or UDP packet - retransmission check skipped")
        return False

    if packet_hash in seen_packets:
        # packet is a duplicate
        return True
    else:
        # packet is not a duplicate, add to seen packets
        seen_packets.add(packet_hash)
        return False
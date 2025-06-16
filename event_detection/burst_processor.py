import scapy.all as sc
import logging
import traceback
from . import global_state


logger = logging.getLogger(__name__)


def start():

    pkt = global_state.packet_queue.get()

    try:
        process_burst(pkt)

    except Exception as e:
        logger.error(f'[Burst Processor] Error processing packet: {e} for packet: {pkt}\n{traceback.format_exc()}')



# Note: This fiunction proess packet for activity detection
# ==========================================================================================
# Process packet to burst; Input: packet; Output: none
# Technical debt: processing same packet twice: can be merged with process_packets, 
# discuss with Danny with potential isuses
# BUG: process re-transmission and duplicate packets, potential cause of misclassification
# ==========================================================================================

def process_burst(pkt):
    print(f"Processing burst {pkt.summary()}")
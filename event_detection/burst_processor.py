import scapy.all as sc
import logging
import traceback
import ipaddress

import libinspector.global_state as libinspector_state
import libinspector.networking as networking

from . import global_state
from . import utils



logger = logging.getLogger(__name__)

# Storage for Time of the first packet of a burst
# Key: (ip_proto, src_ip_addr, src_port, dst_ip_addr, dst_port, src_mac_addr)
# Value: time_epoch of the first packet in the burst
burst_dict_start_time = {}

# Burst window size in seconds
BURST_WRITE_INTERVAL = 1

burst_dict_all_burst = {}  # key (flow key) -> {key (time) -> [[packet element]]}




def start():
    # get a packet from the flow queue (no duplicate/arp/dhcp/dns packet)
    pkt = global_state.flow_queue.get()
    # process the packet to burst
    try:
        process_burst(pkt)
    except Exception as e:
        logger.error(f'[Burst Processor] Error processing packet: {e} for packet: {pkt}\n{traceback.format_exc()}')



# Note: This fiunction proess packet for activity detection
# ==========================================================================================
# Process packet to burst; Input: packet; Output: none
# Technical debt: libinspector.core lib do some minimal packet processing, 
# but we need to do more here.
# ==========================================================================================

def process_burst(pkt):
    # Note: Packets must have TCP or UDP layer 
    # Note: WE only consider packets which has either TCP layer or UDP layer 
    if sc.TCP in pkt:
        protocol = 'TCP'
        layer = sc.TCP
    elif sc.UDP in pkt:
        protocol = 'UDP'
        layer = sc.UDP
    else:
        return

    # =================================================================
    # Parse packet informations
    # =================================================================
    # frame_number = 0              # not useful for feature generation
    # time_delta = 0                # will be canculated lated
    # stream = 0                    # not useful for feature generation
    time_epoch = pkt.time           # packet current time, to be used to generate time_delta for consecutive packets
    frame_len = len(pkt)            # size of packet
    ip_proto = pkt[sc.IP].proto     # protocol number: 6 (TCP), 17 (UDP)  
    
    # ########################### REMOVE #####################################
    # todo: check if _ws_protocol and _ws_expert needed or not
    _ws_protocol = ''               # highest layer in the protocol
    try:
        highest_layer = pkt.lastlayer()
        _ws_protocol = getattr(highest_layer, 'name', str(highest_layer))
        # todo: check if highest layer captures the TLS versions; for now it is not 
    except: 
        _ws_protocol = protocol
    # ############################# END ######################################

    # Get MAC, IP addresses, port numbers 
    src_mac_addr = pkt[sc.Ether].src
    dst_mac_addr = pkt[sc.Ether].dst
    src_ip_addr = pkt[sc.IP].src
    dst_ip_addr = pkt[sc.IP].dst
    src_port = pkt[layer].sport
    dst_port = pkt[layer].dport

    # Note: Ignoring broscasting messes
    # Note: Maynot appropriate for anomaly detection 
    if dst_mac_addr == 'ff:ff:ff:ff:ff:ff' or dst_ip_addr == '255.255.255.255':
        return
    
    # Note: validating correct ip_address
    # Note: Maynot appropriate for anomaly detection 
    if utils.validate_ip_address(src_ip_addr)==False or utils.validate_ip_address(dst_ip_addr)==False:
            return
    
    # Finding host MAC address
    inspector_host_mac_addr = libinspector_state.host_mac_addr

    # Find the actual MAC address that the Inspector host pretends to be if this is a 
    # local communication; otherwise, assume that Inspector pretends to be the gateway
    if src_mac_addr == inspector_host_mac_addr:
        try:
            src_mac_addr = networking.get_mac_address_from_ip(src_ip_addr)
        except KeyError:
            src_mac_addr = ''
    elif dst_mac_addr == inspector_host_mac_addr:
        try:
            dst_mac_addr = networking.get_mac_address_from_ip(dst_ip_addr)
        except KeyError:
            dst_mac_addr = ''
    else:
        return
    
    # extract hostnames
    # Note: North Eastern (BehavIoT) use different method for finding the hostname
    # BehavIoT Method: look DNS, SNI for hostnames; if found: return else: use dig -x ip_address 
    # todo Ask libinspectoe team; ask NYU to find host name
    src_hostname = utils.get_hostname_from_ip_addr(src_ip_addr)
    dst_hostname = utils.get_hostname_from_ip_addr(dst_ip_addr)

    # Check if the source and destination hostnames are empty
    # If the hostname is not found, we use SNI to find the hostname
    if src_hostname == '':
        # code block for SNI checking; 
        try:
            src_hostname = pkt[sc.TLS].server_name.decode('utf-8')
        except (AttributeError, UnicodeDecodeError):
            logger.debug(f"[Burst Processor] No SNI found for source IP: {src_ip_addr}")
            src_hostname = ''
            
    if dst_hostname == '':
        try:
            dst_hostname = pkt[sc.TLS].server_name.decode('utf-8')
        except (AttributeError, UnicodeDecodeError):
            logger.debug(f"[Burst Processor] No SNI found for destination IP: {dst_ip_addr}")
            dst_hostname = ''


    # Note: Key is different from IoT Inspector: inspector use different sets of 7 elements, different order
    # Used to idenfy flow which current packets belong to
    flow_key = (ip_proto, src_ip_addr, src_port, dst_ip_addr, dst_port, src_mac_addr)
    hostname = dst_hostname.lower()
    
    #  check if local packet or incoming packet 
    # if ipaddress.ip_address(dst_ip_addr).is_private and ipaddress.ip_address(src_ip_addr).is_private == False: # incoming packet 
    if dst_hostname == '(local network)' and src_hostname != '(local network)': # incoming packet from local network
        flow_key = (ip_proto, dst_ip_addr, dst_port, src_ip_addr, src_port, dst_mac_addr)
        hostname = src_hostname.lower()
        
    # if ipaddress.ip_address(dst_ip_addr).is_private and ipaddress.ip_address(src_ip_addr).is_private: # incoming local packet
    elif dst_hostname == '(local network)' and src_hostname == '(local network)': # incoming local packet
        if ipaddress.ip_address(dst_ip_addr) > ipaddress.ip_address(src_ip_addr):
            flow_key = (ip_proto, dst_ip_addr, dst_port, src_ip_addr, src_port, dst_mac_addr)
            hostname = src_hostname.lower()

    # get the start time for the burst (aka flow)
    burst_start_time = burst_dict_start_time.setdefault(flow_key, time_epoch)  

    # clean previously stored burst packets if threshold has been passed
    if (time_epoch - burst_start_time) > BURST_WRITE_INTERVAL:
        # clean temp dicts 
        pop_time = burst_dict_start_time.pop(flow_key, 0)  # start time of burst 
        pop_burst = burst_dict_all_burst.pop((flow_key, burst_start_time), [])  # list if packets

        # writing burst in file/db
        # process_pending_burst(flow_key, pop_time, pop_burst)
        global_state.pending_burst_queue.put((flow_key, pop_time, pop_burst))

    # append the current packet with burst packets 
    burst_dict_all_burst.setdefault((flow_key, burst_start_time), []).append([time_epoch, frame_len, _ws_protocol, hostname, ip_proto, src_ip_addr, src_port, dst_ip_addr, dst_port, dst_mac_addr])

    # clear all the burst if current time pass the threshold
    for key in burst_dict_all_burst:
        if (time_epoch - key[1]) > BURST_WRITE_INTERVAL:
            # clean temp dicts 
            pop_time = burst_dict_start_time.pop(key[0], 0)
            pop_burst = burst_dict_all_burst.pop((key[0], key[1]), [])

            # writing burst in file/db
            # process_pending_burst(key[0], pop_time, pop_burst)
            global_state.pending_burst_queue.put((key[0], pop_time, pop_burst))
    
    # print(f"Processing burst {pkt.summary()}")
    # print(f"burst_dict_start_time: {burst_dict_start_time}")
    # print(f"burst_dict_all_burst: {burst_dict_all_burst}")
    # print("")
    return 
            
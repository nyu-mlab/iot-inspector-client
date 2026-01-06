from . import global_state
import logging
import traceback
import ipaddress

import pandas as pd
from scipy.stats import kurtosis
from scipy.stats import skew
from statsmodels import robust

logger = logging.getLogger(__name__)

def start():
    # get a packet from the flow queue (no duplicate/arp/dhcp/dns packet)
    flow_key, pop_time, pop_burst = global_state.pending_burst_queue.get()

    logger.info(f'[Feature Generation]: {flow_key} \t {pop_time} \t {pop_burst}')
    # process the burst to feature
    try:
        process_pending_burst(flow_key, pop_time, pop_burst)
    except Exception as e:
        logger.error(f'[Feature Generation] Error processing packet: {e} for packet: {flow_key}\n{traceback.format_exc()}')



# # define the expected features of a burst 
# cols_feat = [ "meanBytes", "minBytes", "maxBytes", "medAbsDev",
#              "skewLength", "kurtosisLength", "meanTBP", "varTBP", "medianTBP", "kurtosisTBP",
#              "skewTBP", "network_total", "network_in", "network_out", "network_external", "network_local",
#             "network_in_local", "network_out_local", "meanBytes_out_external",
#             "meanBytes_in_external", "meanBytes_out_local", "meanBytes_in_local", "device", "state", "event", "start_time", "protocol", "hosts"]

# process a burst from the queue to extract features

def process_pending_burst(flow_key, pop_time, pop_burst):
    # create a header for storing the burst into a dataframe corresponding to burst element
    # [time_epoch, frame_len, _ws_protocol, hostname, ip_proto, src_ip_addr, src_port, dst_ip_addr, dst_port, dst_mac_addr]
    header = ["ts","frame_len","protocol","host", "trans_proto", "ip_src", "srcport", "ip_dst", "dstport","mac_addr"]

    # check number of packets in the burst discart if 
    # burst has only one packet
    if len(pop_burst) < 2: 
        return
    
    # ----------------------------------------------------
    # compute features from burst of packetes and flow key
    # ----------------------------------------------------
    pd_burst = pd.DataFrame(pop_burst, columns=header)
    pd_burst.frame_len = pd_burst.frame_len.astype(int)
    pd_burst.ts = pd_burst.ts.astype(float)

    # Calculate the time difference (delta) between consecutive rows and
    # Set the first value of time_delta to 0
    pd_burst['ts_delta'] = pd_burst['ts'].diff()
    pd_burst.loc[0, 'ts_delta'] = 0.0      
    pd_burst.ts_delta = pd_burst.ts_delta.astype(float)

    # compute_tbp_features
    start_time = pd_burst.ts.min()
    meanBytes = pd_burst.frame_len.mean()
    minBytes = pd_burst.frame_len.min()
    maxBytes = pd_burst.frame_len.max()
    medAbsDev = robust.mad(pd_burst.frame_len)
    if medAbsDev < 1e-10:
        skewL = 0
        kurtL = 0
    else:
        skewL = skew(pd_burst.frame_len)
        kurtL = kurtosis(pd_burst.frame_len)

    # p = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    # percentiles = np.percentile(pd_burst.frame_len, p)
    meanTBP = pd_burst.ts_delta.mean()
    varTBP = pd_burst.ts_delta.var()
    medTBP = pd_burst.ts_delta.median()
    if varTBP < 1e-10:
        kurtT = 0
        skewT = 0
    else:
        kurtT = kurtosis(pd_burst.ts_delta)
        skewT = skew(pd_burst.ts_delta)

    # compute # of packet related features
    network_in = 0 # Network going to target device.
    network_out = 0 # Network going from target device 
    # network_both = 0 # Network going to/from target device.
    network_external = 0 # Network not going to just 192.168.10.248.
    network_local = 0
    network_in_local = 0 # 
    network_out_local = 0 #
    # anonymous_source_destination = 0
    network_total = 0
    meanBytes_out_external = 0 
    meanBytes_in_external = 0 
    meanBytes_out_local = 0 
    meanBytes_in_local = 0 

    # target devices meta information 
    my_device_mac = flow_key[-1]
    my_device_addr = flow_key[1]
    external_destination_addr = flow_key[3]
    local_destination_device = ''

    # todo: check if not needed ; updated values with known knowledge above 

    for j, m in zip(pd_burst.ip_dst, pd_burst.mac_addr):
        if m == my_device_mac:
            continue
        elif ipaddress.ip_address(j).is_private==True:  # router IPs
            local_destination_device = m
            break
    

    for i, j, f_len, k_host in zip(pd_burst.ip_src, pd_burst.ip_dst, pd_burst.frame_len, pd_burst.host):
        network_total += 1
        
        if ipaddress.ip_address(i).is_private==True and (ipaddress.ip_address(j).is_private==False): 
            # source addr; outbound packet 
            network_out += 1
            network_external += 1
            meanBytes_out_external += f_len
            
        elif ipaddress.ip_address(j).is_private==True and (ipaddress.ip_address(i).is_private==False): 
            # destation addr; inbound packet 
            network_in += 1
            network_external += 1
            meanBytes_in_external += f_len

        elif i == my_device_addr and (ipaddress.ip_address(j).is_private==True) : 
            # local outgoing packet 
            network_out_local += 1
            network_local += 1
            meanBytes_out_local+= f_len

        elif (ipaddress.ip_address(i).is_private==True) and j == my_device_addr: 
            # local inbound packet 
            network_in_local += 1
            network_local += 1
            meanBytes_in_local += f_len

        elif k_host == '(local network)': 
            network_local += 1           
        else:
            pass

    meanBytes_out_external = meanBytes_out_external/network_out if network_out else 0
    meanBytes_in_external = meanBytes_in_external/network_in if network_in else 0
    meanBytes_out_local = meanBytes_out_local/network_out_local if network_out_local else 0
    meanBytes_in_local = meanBytes_in_local/network_in_local if network_in_local else 0


    # host is either from the host column, or the destination IP if host doesn't exist
    hosts = set([ str(host) for i, host in enumerate(pd_burst.host.fillna("")) ])
    protocol = set([str(proto) for i, proto in enumerate(pd_burst.protocol.fillna(""))])

    if ('DNS' in protocol) or ('DHCP' in protocol) or ('NTP' in protocol) or ('SSDP' in protocol) or ('MDNS' in protocol):
        pass
    else:
        if pd_burst.trans_proto[0] == 6:
            protocol = set(['TCP'])
        elif pd_burst.trans_proto[0] == 17:
            protocol = set(['UDP'])
    if network_total == network_local: 
        # hosts = set(['local'])
        hosts = set([str(local_destination_device)])
    
    host_output = ";".join([x for x in hosts if x!= ""])
    # merge hostnames
    if host_output.startswith('ec') and (host_output.endswith('compute.amazonaws.com') or host_output.endswith('compute-1.amazonaws.com')):
            host_output = '*.compute.amazonaws.com'
    if host_output == '':
        if str(external_destination_addr) == '':
            logger.debug(f'[Feature Generation]: host error {my_device_mac} \t {external_destination_addr}')
            # Note: commented these 2 lines from original Northeastern project
            # print('Error:', device_name, state, event)
            # exit(1)   
        host_output = str(external_destination_addr)

    d = [ meanBytes, minBytes, maxBytes, medAbsDev, skewL, 
         kurtL, meanTBP, varTBP, medTBP, kurtT,
         skewT, network_total, network_in, network_out, network_external, 
         network_local, network_in_local, network_out_local, meanBytes_out_external, meanBytes_in_external, 
         meanBytes_out_local, meanBytes_in_local, my_device_mac, 'unctrl', 'unctrl',
         start_time, ";".join([x for x in protocol if x!= ""]), host_output ]

    store_burst_in_db(d)
    return
        

# store processed burst features (data) into database
# input: a data point
# output: None
def store_burst_in_db(data):
    # Note: for now storing in a queue, later store in database
    # todo: check if packets are captured while not inspecting
    # todo: implement idle burst processor
    # make to lock safe
    """
    Adds a data to the data queue.

    with global_state.global_state_lock:
        if not global_state.is_inspecting:
            return

     # check if device is idle, if idle store in a separate
    if global_state.devices_state.get(data[-6], {'is_idle': 0})['is_idle']:
        # @idle_burst_processor.py stores the idle burst in CSV file
        global_state.idle_burst_queue.put(data)

    else:
        global_state.burst_queue.put(data)
    """
    
    global_state.processed_burst.put(data)

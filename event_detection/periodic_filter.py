import logging
import os
import traceback

from . import global_state
from .utils import protocol_transform, host_transform, get_mac_address_list
from .ttl_cache import ttl_cache

import numpy as np
import scipy as sp
import pickle

logger = logging.getLogger(__name__)

def start():
    # get standardized busrt feature from the queue
    burst, device_name, model_name = global_state.ss_burst_queue.get()

    try:
        # print('[Periodic Filter] Processing burst for device: ' + str(device_name) + ' model: ' + str(model_name))
        periodic_filter_burst_helper(burst, device_name, model_name)
    except Exception as e:
        logger.error('[Periodic Filter] Error processing burst: ' + str(e) + ' for burst: ' + str(burst) + '\n' + traceback.format_exc())


def periodic_filter_burst_helper(burst, device_name, model_name):
    """
    Filter out periodic bursts from the standardized burst features.
    Args:
        burst (tuple): A tuple containing burst features.
    Returns:
        None: The function processes the burst and does not return anything.
    """
    
    
    # # define the expected features of a burst 
    # cols_feat = [ "meanBytes", "minBytes", "maxBytes", "medAbsDev",
    #             "skewLength", "kurtosisLength", "meanTBP", "varTBP",
    #             "medianTBP", "kurtosisTBP", "skewTBP", "network_total",
    #             "network_in", "network_out", "network_external", "network_local",
    #             "network_in_local", "network_out_local", "meanBytes_out_external", "meanBytes_in_external",
    #             "meanBytes_out_local", "meanBytes_in_local",
    #             "device", "state", "event", "start_time", "protocol", "hosts"]


    # Get periods from fingerprinting files
    periodic_tuple, host_set = get_periods(model_name) 

    if periodic_tuple == 'unknown':
        logger.error(
            '[Burst Periodic-filter] Failed loading periodic events: ' + ' for device: '\
                + str(device_name) + " " + str(burst))
        return


    # test_data = burst
    test_feature = burst[:-6]
    # test_data_numpy = np.array(burst)
    test_feature = np.array(test_feature, dtype=float)
    test_protocols = burst[-2]
    test_hosts = burst[-1]
    test_protocols = protocol_transform(test_protocols)
    
    # TODO: test if host transformation is working
    test_hosts = host_transform(test_hosts)

    # Filter local and DNS/NTP. 
    if test_protocols == 'DNS' or test_protocols == 'MDNS' or test_protocols == 'NTP' or test_protocols == 'SSDP' or test_protocols == 'DHCP':
        return 
    # else: filter_dns.append(True)

    # Filter local
    # todo update local mac list 
    local_mac_list = ['ff:ff:ff:ff:ff:ff', '192.168.1.1', '192.168.0.1']
    mac_dic = get_mac_address_list()


    if test_hosts in mac_dic or test_hosts in local_mac_list or test_hosts=='multicast' or ':' in test_hosts:
        return

    # """
    # For each tuple: 
    # """

    aperiodic_event = True

    for tup in periodic_tuple:
        tmp_host = tup[0]
        tmp_proto = tup[1]
        if tmp_host == '':
            continue

        # todo: remove this hardcosing checking
        if tmp_host == 'n-devs.tplinkcloud.com':
            tmp_host_model = 'devs.tplinkcloud.com'
        else:
            tmp_host_model = tmp_host

        # common.event_log('[Burst Periodic-filter] Loading Model for ' + device_name + ' : ' + test_hosts + ' ' + test_protocols + ' ' + tmp_host + ' ' + tmp_proto)
        # check if filtering needed
        # todo: we can make this faster by using dictionary for periodic_tuple
        if tmp_host.startswith('*'):
            matched_suffix = test_hosts.endswith(tmp_host[2:])
        else:
            matched_suffix = False

        if (test_hosts == tmp_host or matched_suffix) and test_protocols == tmp_proto:
            filter_test = True  
        else:
            filter_test = False

        if filter_test == False:
            if (test_hosts.endswith('.'.join(tmp_host.split('.')[-3:]))) and test_protocols == tmp_proto:
                filter_test = True    

        # if filtering not needed
        if filter_test == False:
            continue

        # Note: update model names perodically
        # dname = device_name_mapping(device_name)
        

        model_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '..', 'models', 'filter_apr20', 'filter', model_name + tmp_host_model + tmp_proto + '.model'
        )

        # common.event_log('[Burst Periodic-filter] Condition matched ' + test_hosts + ' ' + test_protocols + ' ' + tmp_host + ' ' + tmp_proto)
        """
        Load trained models
        """
        try:
            model = pickle.load(open(model_file, 'rb'))['trained_model']
        except Exception as e: 
            logger.warning('[Periodic Filter] Model loading error: ' + str(e))
            continue
        
        try:
            y_new = dbscan_predict(model, test_feature)
            # common.event_log('[Burst Periodic-filter] DB_Scan Success ' + str (y_new))
        except Exception as e:
            logger.error('[Periodic Filter] DB_Scan Failed ' + str (e))


        # Do we want to filter it out? 
        if y_new >= 0:
            # periodic event 
            aperiodic_event = False
            break
    
    if aperiodic_event:
        store_processed_burst_in_db(burst, device_name, model_name)
        logger.info('[Periodic Filter] non-periodic event found ' + device_name + ' : ' + test_hosts + ' ' + test_protocols)

    return 



@ttl_cache(maxsize=128, ttl=300)
def get_periods(model_name):
    # Load periodic fingerprints
    model_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..',  'models', 'freq_period', 'fingerprints',
        model_name + '.txt'
        )
    
    if os.path.exists(model_dir):
        with open(model_dir, 'r') as file:
            periodic_tuple = []
            host_set = set()

            for line in file:
                tmp = line.split()
                # print(tmp)
                try:
                    tmp_proto = tmp[0]
                    tmp_host = tmp[1]
                    tmp_period = tmp[2]
                except:
                    # print(tmp)# exit(1)
                    return ('unknown', 'unknown')
                
                if tmp_host == '#' or tmp_host  == ' ':
                    tmp_host = ''

                periodic_tuple.append((tmp_host, tmp_proto, tmp_period))
                host_set.add(tmp_host)

        return (periodic_tuple, host_set)
        
    return ('unknown', 'unknown')


def dbscan_predict(dbscan_model, x_new, metric=sp.spatial.distance.euclidean):
    y_new = -1 
    # Find a core sample closer than EPS
    for i, x_core in enumerate(dbscan_model.components_):
        # print(metric(x_new, x_core))
        # common.event_log('[Burst Periodic-filter] DB_Scan: \n Feature = ' + str (x_new) + "\n Core = " + str(x_core))
        if metric(x_new, x_core) < (dbscan_model.eps): 
            # Assign label of x_core to x_new
            y_new = dbscan_model.labels_[dbscan_model.core_sample_indices_[i]]
            break

    return y_new


# store standardized processed burst features (data) into database
# input: a data point
# output: None
def store_processed_burst_in_db(data, device_name=None, model_name=None):
    # todo: for now storing in a queue, later store in database
    # make to lock safe
    """
    Adds a data to the data queue.
    """
    # with global_state.global_state_lock:
    #     if not global_state.is_inspecting:
    #         return

    global_state.filtered_burst_queue.put((data, device_name, model_name))


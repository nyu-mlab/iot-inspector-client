from . import global_state
import logging
import traceback
import sys


logger = logging.getLogger(__name__)

# define the expected features of a burst 
cols_feat = [ "meanBytes", "minBytes", "maxBytes", "medAbsDev",
             "skewLength", "kurtosisLength", "meanTBP", "varTBP",
             "medianTBP", "kurtosisTBP", "skewTBP", "network_total",
             "network_in", "network_out", "network_external", "network_local",
            "network_in_local", "network_out_local", "meanBytes_out_external", "meanBytes_in_external",
            "meanBytes_out_local", "meanBytes_in_local",
            "device", "state", "event", "start_time", "protocol", "hosts"]


def start():
    # get busrt feature from the processed burst queue
    burst = global_state.processed_burst.get()

    try:
        print(f'[Feature Standardization] Writing Feature: {burst[-6]} \t Memory size{sys.getsizeof(burst)} \n')
        # standardize_burst_feature(burst)
    except Exception as e:
        logger.error('[Feature Standardization] Error processing burst: ' + str(e) + ' for burst: ' + str(burst) + '\n' + traceback.format_exc())



'''

# pre-process burst file with pre-trained SS and PCA model 
# Note: we are using latest model of sk_learn, but the models are traied on 1.3.0 version 
# mismatch of version, might lead to breaking code or invalid results. 
# todo: train ss/pca models with latest version of numpy, sklean 

def standardize_burst_feature(burst):
    print('[Burst Pre-Processor] Before processing burst: ' + str(burst))

    # get device name from MAC address
    device_name = get_product_name_by_mac(burst[-6])

    # load data to a dataframe 
    X_feature = pd.DataFrame([burst], columns=cols_feat)
    X_feature = X_feature.drop(['device', 'state', 'event' ,'start_time', 'protocol', 'hosts'], axis=1).fillna(-1)
    X_feature = np.array(X_feature)

    ss_pca_model = get_ss_pca_model(device_name)

    if ss_pca_model == "Model Unknown":
        common.event_log('[Burst Pre-Processor] Process unsuccessful: ' + str(device_name) + ' SS PCA not exist')
        return
    
    try:
        ss = ss_pca_model['ss']
        X_feature = ss.transform(X_feature)
    except Exception as e:
        common.log('[Burst Pre-Processor] Process failed, device name: ' + str(device_name) + " " + str(e))

    X_feature = np.append(X_feature, burst[-6:])

    # todo: send processed data to next step 
    common.log('[Burst Pre-Processor] Burst stored for: ' + str(device_name) + ' ' + burst[-1] + ' ' + burst[-2])

    store_processed_burst_in_db(X_feature)
    
    return 

'''
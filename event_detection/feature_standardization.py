import logging
import traceback
import sys
import os

from . import global_state
from .utils import get_product_name_by_mac
from .ttl_cache import ttl_cache
from .model_selection import find_best_match

import pandas as pd
import numpy as np
import pickle

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
        standardize_burst_feature(burst)
    except Exception as e:
        logger.error('[Feature Standardization] Error processing burst: ' + str(e) + ' for burst: ' + str(burst) + '\n' + traceback.format_exc())


# Fetches the ss and pca model from MAC address.
# Args:
#     mac_address (str): The MAC address of the device.
# Returns:
#     pickle model file 
# todo: write a function to map the device name to model file name 
# todo: update every 10 mins, or clean memory every 10 mis 
# @ttl_lru_cache(ttl_seconds=300, maxsize=128)
@ttl_cache(maxsize=128, ttl=300)
def get_ss_pca_model(device_name):
    if device_name == 'unknown':
        return ("unknown", "unknown")

    # Note: the model is choosen from the available pre-trained models 
    # todo: update threashold for matching device name with model name
    _, model_name = find_best_match(device_name)

    if model_name == 'unknown':
        logger.warning('[Feature Standardization] Model not found: ' + str(device_name))
        return ("unknown", "unknown")

    # Load ss and pca file
    model_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), '..', 'models', 'SS_PCA', model_name + '.pkl'
        )
    

    if os.path.exists(model_dir):
        with open(model_dir, 'rb') as file:
            return (pickle.load(file), model_name)
        return ("unknown", "unknown")
        
    return ("unknown", "unknown")



# pre-process burst file with pre-trained SS and PCA model 
# Note: we are using latest model of sk_learn, but the models are traied on 1.3.0 version 
# mismatch of version, might lead to breaking code or invalid results. 
# todo: train ss/pca models with latest version of numpy, sklean 

def standardize_burst_feature(burst):
    # get device name from MAC address
    device_name = get_product_name_by_mac(burst[-6])
    logger.info('[Feature Standardization] Processing burst for device name: ' + device_name+ " mac: " + str(burst[-6]))

    # load data to a dataframe 
    X_feature = pd.DataFrame([burst], columns=cols_feat)
    X_feature = X_feature.drop(['device', 'state', 'event' ,'start_time', 'protocol', 'hosts'], axis=1).fillna(-1)
    X_feature = np.array(X_feature)

    ss_pca_model, model_name = get_ss_pca_model(device_name)

    if ss_pca_model == "unknown":
        logger.warning('[Feature Standardization] Process unsuccessful for device mac: ' + str(burst[-6]) + ' SS PCA not exist')
        return
    
    try:
        ss = ss_pca_model['ss']
        X_feature = ss.transform(X_feature)
    except Exception as e:
        logger.warning('[Feature Standardization] Transformation failed, device name: ' + str(device_name) + " " + str(e))

    X_feature = np.append(X_feature, burst[-6:])

    # todo: send processed data to next step 
    
    logger.info('[Feature Standardization] Burst stored for: ' + str(device_name) + ' ' + burst[-1] + ' ' + burst[-2])
    store_processed_burst_in_db(X_feature, device_name, model_name)
    
    return 


# store standardized processed burst features (data) into database
# input: a data point, output: None
# TODO: incorporate idle device in the burst
# idea: create a different queue for idle device, and process them separately
def store_processed_burst_in_db(data, device_name, model_name):
    # Note: for now storing in a queue, later store in database
    # make to lock safe
    """
    Adds a data to the data queue.
    """
    global_state.ss_burst_queue.put((data, device_name, model_name))
        
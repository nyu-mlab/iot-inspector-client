import logging
import os
import traceback

from . import global_state
from .ttl_cache import ttl_cache

import numpy as np
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)


def start():

    burst, device_name, model_name = global_state.filtered_burst_queue.get()

    # print('[Predict-Event] Processing burst for device: ' + str(device_name) + ' model: ' + str(model_name))

    try:
        predict_event_helper(burst, device_name, model_name)

    except Exception as e:
        logger.warning('[Predict-Event] Error: ' + str(e) + ' for burst: ' + str(burst) + '\n' + traceback.format_exc())

# define the expected features of a burst 
# cols_feat = [ "meanBytes", "minBytes", "maxBytes", "medAbsDev",
#              "skewLength", "kurtosisLength", "meanTBP", "varTBP",
#              "medianTBP", "kurtosisTBP", "skewTBP", "network_total",
#              "network_in", "network_out", "network_external", "network_local",
#             "network_in_local", "network_out_local", "meanBytes_out_external", "meanBytes_in_external",
#             "meanBytes_out_local", "meanBytes_in_local",
#             "device", "state", "event", "start_time", "protocol", "hosts"]

def predict_event_helper(burst, dname=None, model_name=None):
    logger.info('[Predict-Event] Processing burst for device: ' + str(dname) + ' data: ' + str(burst[:-6]))
    
    X_test = burst[:-6]

    # # Note: removed hard coding 
    # if test_hosts == 'n-devs.tplinkcloud.com':
    #     test_hosts = 'devs.tplinkcloud.com'

    """
    Predict
    """
    positive_label_set, list_models = get_list_of_models(dname, model_name)

    if positive_label_set == '' or len(positive_label_set) == 0:
        logger.info('[Predict-Event] unknown event detected: ' + str(dname))
        return
    
    # comment if not running 
    X_test = np.array([X_test], dtype=float)
    predictions = []
    try:
        for trained_model in list_models:
            y_predicted = trained_model.predict(X_test) 
            y_proba = trained_model.predict_proba(X_test)
            predictions.append(y_predicted[0])
            logger.info('[Predict-Event] predicting: ' + ' for device : ' + str(dname) + ' y_predicted: ' + str(y_predicted) + ' y_proba: ' + str(y_proba) + ' events: ' + str(positive_label_set))
    except Exception as e:
            logger.warning('[Predict-Event] predict error: ' + ' for device : ' + str(dname) + ' error: ' + str(e))
    # positive_label_set = list(positive_label_set)


    try: 
        event = str(list(positive_label_set)[predictions.index(1)])
        logger.info('[Predict-Event] Success: ' + ' for device : ' + str(dname) + ' event: ' + event )
        store_events_in_db(burst[-6], burst[-3], event)
    except:
        logger.warning('[Predict-Event] Success: ' + ' for device : ' + str(dname) + ' event: periodic/unexpected event')
    return




# Fetches the event models model from MAC address.
# Args:
#     mac_address (str): The MAC address of the device.
# Returns:
#     pickle model file 
# todo: write a function to map the device name to model file name 
# todo: update every 10 mins, or clean memory every 10 mis 

@ttl_cache(maxsize=128, ttl=300)
def get_list_of_models(device_name: str, model_name: str | None = None):
    # device_name = get_product_name_by_mac(mac_address)

    positive_label_set = []
    list_models = []

    if device_name == 'unknown':
        logger.warning('[Predict Event] device not found: ' + str(device_name))
        return ('', '')
    
    # _, model_name = find_best_match(device_name)
    if model_name is None or model_name == 'unknown':
        logger.warning('[Predict Event] device not found: ' + str(device_name))
        return ('', '')

    # Load event models
    model_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', 'models', 'binary', 'rf', model_name)
    
    if not os.path.exists(model_dir):
        logger.warning('[Predict Event] event model not found: ' + str(model_dir))
        return ('', '')
    
    for f1 in os.listdir(model_dir):
        # positive_label_set.append('_'.join(f1.split('_')[1:-1]))
        positive_label_set.append('_'.join(f1.split('.')[0].split('_')[1:]))

        list_models.append(pickle.load(open(os.path.join(model_dir, f1), 'rb')))
    
    positive_label_set = set(positive_label_set)

    return (positive_label_set, list_models)

def store_events_in_db(device, time, event):
    # todo: for now storing in a queue, later store in database
    # make to lock safe
    """
    Adds a data to the data queue.
    """
    global_state.filtered_event_queue.put((device, datetime.fromtimestamp(float(time)), event))
    logger.info('[Predict-Event] Stored event in DB: ' + str((device, datetime.fromtimestamp(float(time)), event)))
    print(f"[Predict-Event] Stored event in DB: {device}, {datetime.fromtimestamp(float(time))}, {event}")


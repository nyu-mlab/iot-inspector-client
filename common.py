import datetime
import time
import threading
import json


config_file_name = 'config.json'
config_lock = threading.Lock()
config_dict = {}


def get_human_readable_time(timestamp=None):
    """
    Convert a timestamp to a human-readable time format.

    Args:
        timestamp (float): The timestamp to convert.

    Returns:
        str: Human-readable time string.
    """
    if timestamp is None:
        timestamp = time.time()
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')



def initialize_config_dict():
    """
    Initialize the configuration dictionary by reading from the config file.
    If the file does not exist, it will create an empty dictionary.
    """
    if config_dict:
        return

    try:
        with open(config_file_name, 'r') as f:
            config_dict.update(json.load(f))
    except FileNotFoundError:
        pass

    config_dict['app_start_time'] = time.time()



def config_get(key, default=None):
    """
    Get a configuration value.

    Args:
        key (str): The configuration key.
        default: The default value if the key is not found.

    Returns:
        The configuration value or the default value.
    """
    with config_lock:

        initialize_config_dict()

        if key in config_dict:
            return config_dict[key]

        # If the key is not found, return the default value
        if default is not None:
            return default

        raise KeyError(f"Key '{key}' not found in configuration.")



def config_get_prefix(key_prefix):
    """
    Get all configuration values that start with a given prefix.

    Args:
        key_prefix (str): The prefix to filter keys.

    Returns:
        dict: A dictionary of configuration values that match the prefix.
    """
    with config_lock:

        initialize_config_dict()

        return {
            k: v
            for k, v in config_dict.items()
            if k.startswith(key_prefix)
        }



def config_set(key, value):
    """
    Set a configuration value.

    Args:
        key (str): The configuration key.
        value: The value to set.
    """
    with config_lock:

        initialize_config_dict()

        config_dict[key] = value

        # Write the updated config_dict to the file
        with open(config_file_name, 'w') as f:
            json.dump(config_dict, f, indent=2, sort_keys=True)


def get_device_custom_name(mac_address):
    """
    Get the custom name for a device based on its MAC address.

    Args:
        mac_address (str): The MAC address of the device.

    Returns:
        str: The custom name of the device or an empty string if not set.
    """
    try:
        device_custom_name = config_get(f'device_custom_name_{mac_address}')
    except KeyError:
        # Use the last part of the MAC address as the name suffix
        device_custom_name = mac_address.split(':')[-1].upper()
        device_custom_name = f'Unnamed Device {device_custom_name}'

    return device_custom_name


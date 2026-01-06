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

        # Initialize the config_dict if it's empty; just read from disk
        if not config_dict:
            try:
                with open(config_file_name, 'r') as f:
                    config_dict.update(json.load(f))
            except FileNotFoundError:
                pass
            config_dict['app_start_time'] = time.time()

        if key in config_dict:
            return config_dict[key]

        # If the key is not found, return the default value
        if default is not None:
            return default

        raise KeyError(f"Key '{key}' not found in configuration.")


def config_set(key, value):
    """
    Set a configuration value.

    Args:
        key (str): The configuration key.
        value: The value to set.
    """
    with config_lock:
        config_dict[key] = value

        # Write the updated config_dict to the file
        with open(config_file_name, 'w') as f:
            json.dump(config_dict, f, indent=2, sort_keys=True)
import re
from typing import List, Dict, Any
import requests
import time
import functools
import logging
import os
import json
from .. import common


logger = logging.getLogger("client")
# Define the common TXT record keys that hold the best, most human-readable name,
# in order of preference (most descriptive first).
# Keys prioritized from most human-friendly to most technical/model-based.
# 'DN' and 'fn' are generally the safest bets for a human-readable name.
PREFERRED_NAME_KEYS: List[str] = [
    'DN',           # Device Name (common in Google Cast/AirPlay)
    'fn',           # Friendly Name (common in AirPlay)
    'name',         # General Name
    'integrator',   # Ecosystem owner (e.g., Roku)
    'mn',           # Model Name (Thread/Matter)
    'model',        # Hardware Model (General)
    'md',           # Model Description
    'n'             # Node/General Name (Last resort)
]

def _extract_instance_name(device_name: str) -> str:
    """
    Extracts the clean, human-readable instance name from the full mDNS string.

    Example: "GoogleTV6541._androidtvremote2._tcp.local." -> "GoogleTV6541"
    """
    # Split by '.' (dot)
    parts = device_name.split('.')
    # The instance name is always the first part.
    if parts:
        return parts[0].strip()
    return ""


def _is_human_friendly(value: str) -> bool:
    """
    Applies heuristics to determine if a string is likely a human-friendly name
    vs. a cryptic ID, hash, or binary string.
    """
    if not isinstance(value, str) or not value.strip():
        return False

    clean_value = value.strip()

    # Heuristic 1: Maximum Length Check (Catching UUIDs, Hashes, Public Keys)
    # Human-assigned names are rarely longer than 35 characters.
    if len(clean_value) > 40:
        return False

    # Heuristic 2: Check for Unprintable/Binary Characters
    # If the string contains non-printable ASCII characters, it is likely raw binary/garbage.
    if any(c < ' ' or c > '~' for c in clean_value):
        # Allow common exceptions like newlines/tabs if they somehow made it in,
        # but primarily check for binary zeros or high-range non-ASCII
        return False

    # Heuristic 3: Hexadecimal Density Check (Catching MACs, Short Hashes, IDs)
    # A human name should contain mostly letters and spaces, not just A-F and 0-9.

    # Count hex characters (0-9, a-f, A-F)
    hex_chars_count = len(re.findall(r'[0-9a-fA-F]', clean_value))
    total_chars = len(clean_value)

    # Calculate the ratio of hex characters to the total length.
    # If over 80% of characters are hexadecimal, it's probably an ID, not a name.
    if total_chars > 0 and hex_chars_count / total_chars > 0.8:
        return False

    # Heuristic 4: Digit Density Check (New Requirement)
    # If more than 50% of characters are digits, it is likely a version or ID.
    digit_chars_count = len(re.findall(r'[0-9]', clean_value))
    if digit_chars_count / total_chars > 0.5:
        return False

    # Final check: Must contain at least one letter to be a good name.
    if not re.search(r'[a-zA-Z]', clean_value) and total_chars > 5:
        return False

    return True


def guess_device_name_from_mdns_list(mdns_device_list: List[Dict[str, Any]]) -> str:
    """
    Analyzes a list of mDNS JSON entries to find the most human-readable device name.

    Prioritizes names found in TXT records (device_properties) over the
    raw service instance name.

    Args:
        mdns_device_list: A list of mDNS dictionaries, e.g.,
                          meta_data.get('mdns_json', []).

    Returns:
        The best guess for the device's name, or an empty string if nothing useful is found.
    """
    best_name = ""

    # 1. Search through all entries for a highly preferred TXT key
    for entry in mdns_device_list:
        properties = entry.get('device_properties', {})

        # Check preferred keys in order
        for key in PREFERRED_NAME_KEYS:
            name_candidate = properties.get(key, '').strip()

            # If we find a non-empty name, use it immediately and stop searching.
            if name_candidate:
                if _is_human_friendly(name_candidate):
                    # Found a good name! Return it.
                    return name_candidate

        # 2. If no TXT key was found, fall back to the cleanest part of the device_name.
        # This is the lowest priority, so we just store the first one found as a fallback.
        if not best_name:
            device_name = entry.get('device_name', '').strip()
            if device_name:
                best_name = _extract_instance_name(device_name)

    return best_name


def api_worker_thread():
    """
    A worker thread to periodically clear the cache of call_predict_api.
    """
    logger.info("[Device ID API] Starting worker thread to periodically call the API for each device.")
    time.sleep(2)
    while True:
        # Getting inputs and calling API
        for device_dict in common.get_all_devices():
            meta_data = common.get_device_metadata(device_dict['mac_address'])
            mdns_device_list = meta_data.get('mdns_json', [])
            mdns_device_name = guess_device_name_from_mdns_list(mdns_device_list)
            oui_vendor = meta_data.get('oui_vendor', '').strip()
            remote_hostnames = common.get_remote_hostnames(device_dict['mac_address'])
            custom_name_key = f"device_custom_name_{device_dict['mac_address']}"
            try:
                # Note I am passing the metadata as a string because functions with cache cannot take dicts
                # as a dict is mutable, and the cache would not work as expected.
                api_output = call_predict_api(json.dumps(meta_data), remote_hostnames, device_dict['mac_address'])
                common.config_set(f'device_details@{device_dict["mac_address"]}', api_output)
                if "Vendor" in api_output:
                    custom_name = api_output["Vendor"]
                    if api_output["Vendor"] != "":
                        common.config_set(custom_name_key, custom_name)
            except Exception as e:
                logger.info("[Device ID API] Exception when calling API: %s", str(e))
            finally:
                # If API is down, just try using OUI vendor if no custom name is set in config.json
                if mdns_device_name:
                    # Prioritize the full mDNS name as it's the most descriptive identifier
                    final_device_name = mdns_device_name
                elif oui_vendor:
                    # Fall back to the OUI vendor name if mDNS data is absent
                    final_device_name = oui_vendor
                else:
                    # Use the final generic fallback name
                    final_device_name = 'Unknown Device, likely a Mobile Phone'
                common.config_set(custom_name_key, final_device_name)
        time.sleep(15)
        logger.info("[Device ID API] 15 seconds passed, will start calling API for each device if needed.")


@functools.cache
def call_predict_api(meta_data_string: str, remote_hostnames: str,
                     mac_address: str, url="http://159.65.184.153:8080/predict") -> dict:
    """
    Call the predicting API with the given fields.
    This takes the MAC Address of an inspected device
    and checks the `devices` table, where iot inspector core collected meta-data
    based on SSDP discovery.
    Please see Page 11 Table A.1. We explain how to get the data from IoT Inspector:
    1. oui_friendly: we use the OUI database from IoT Inspector Core
    2. dhcp_hostname: this is extracted from the 'devices' table, check meta-data and look for 'dhcp_hostname' key.
    3. remote_hostnames: IoT Inspector collects this information the DHCP hostname via either DNS or SNI
    Args:
        meta_data_string (str): Device Metadata, User Agent info, OUI info, DHCP hostname, etc. in string format
        remote_hostnames (str): The remote hostnames the device has contacted
        mac_address (str): The MAC address of the device we want to use AI to get more info about
        url (str): The API endpoint.
    Returns:
        dict: The response text from the API.
    """
    api_key = os.environ.get("API_KEY", "momo")
    device_tracked_key = f'tracked@{mac_address}'
    meta_data = json.loads(meta_data_string)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    data = {
        "prolific_id": common.config_get("prolific_id", ""),
        "mac_address": mac_address,
        "current_time" : common.get_human_readable_time(),
        "device_category": common.config_get("device_category", ''),
        "device_name": common.config_get("device_name", ''),
        "activity_label": common.config_get("activity_label", ''),
        "fields": {
            "oui_friendly": meta_data.get("oui_vendor", ""),
            "dhcp_hostname": meta_data.get("dhcp_hostname", ""),
            "remote_hostnames": remote_hostnames,
            "user_agent_info": meta_data.get("user_agent_info", ""),
            "mdns_info": meta_data.get("mdns_json", ""),
            "ssdp_info": meta_data.get("ssdp_json", ""),
            "user_labels": "",
            "talks_to_ads": common.config_get(device_tracked_key, False)
        }
    }
    non_empty_field_values = [
        field_value
        for field_name, field_value in data["fields"].items()
        if field_name != "talks_to_ads" and bool(field_value)
    ]
    if len(non_empty_field_values) < 2:
        logger.warning(
            "[Device ID API] Fewer than two string fields in data are non-empty; refusing to call API. Wait until IoT Inspector collects more data.")
        raise RuntimeError(
            "Fewer than two string fields in data are non-empty; refusing to call API. Wait until IoT Inspector collects more data.")

    if common.config_get("debug", default=False):
        logger.info("[Device ID API] Calling API with data: %s", json.dumps(data, indent=4))

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"[Device ID API] API request failed: {e}")
        raise RuntimeError("API request failed, not caching this result.")

    logger.info("[Device ID API] API query successful!")
    return result

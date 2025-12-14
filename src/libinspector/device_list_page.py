import streamlit as st
import time
import libinspector.global_state
import common
import logging
import functools
import os
import requests
import json
from typing import List, Dict, Any

logger = logging.getLogger("client")


def show():
    """
    Creating a page that shows what devices have been discovered so far
    """
    toast_obj = st.toast('Discovering devices...')
    show_list(toast_obj)


# Define the common TXT record keys that hold the best, most human-readable name,
# in order of preference (most descriptive first).
PREFERRED_NAME_KEYS = ['fn', 'n', 'name', 'md', 'model']


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
        for device_dict in get_all_devices():
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
                custom_key_name = common.config_get(custom_name_key, default='')
                if custom_key_name == '' or custom_key_name == 'UNKNOWN':
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


def get_all_devices() -> list[dict]:
    """
    Get the list of devices from the database.

    Returns:
        list[dict]: A list of device dictionaries.
    """
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock

    # Get the list of devices from the database
    sql = """
        SELECT * FROM devices
        WHERE is_gateway = 0
    """
    device_list = []
    with rwlock:
        for device_dict in db_conn.execute(sql):
            device_list.append(dict(device_dict))
    return device_list


def get_device_data(mac_address: str) -> dict:
    """
    Get the device details for a specific device by MAC address.

    Returns:
        mac_address (str): The MAC address of the device.
    """
    sql = """
        SELECT * FROM devices
        WHERE mac_address = ?
    """
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    with rwlock:
        row = db_conn.execute(sql, (mac_address,)).fetchone()
    if row:
        return dict(row)
    else:
        return dict()


def show_list(toast_obj: st.toast):
    """
    The main page that creates a "card" for each device that was found via IoT Inspector
    """
    human_readable_time = common.get_human_readable_time()
    st.markdown(f'Last Page Refresh: {human_readable_time}')

    device_list = get_all_devices()
    if not device_list:
        st.warning('We are still scanning the network for devices. Please wait a moment. This page will refresh automatically.')
        time.sleep(5)
        st.rerun()

    # Create a card entry for the discovered device
    for device_dict in device_list:
        st.markdown('---')
        c1, c2 = st.columns([6, 4], gap='small')
        with c1:
            show_device_bar_graph(device_dict)
        # Set whether a device is to be inspected, favorite, or blocked
        with c2:
            toggle_device_fragment(device_dict["mac_address"])

    # Create a pop-up showing if any new devices were found
    prev_device_count = st.session_state.get('prev_device_count', 0)
    if len(device_list) > prev_device_count:
        toast_obj.toast(f'Discovered {len(device_list) - prev_device_count} new device(s)!', icon=':material/add_circle:')
        st.session_state['prev_device_count'] = len(device_list)
        time.sleep(1.5)  # Give the user a moment to read the toast


def update_device_inspected_status(device_dict: dict):
    """
    Update the 'is_inspected' status of a device in the database based on user interaction.
    Args:
        device_dict (dict): information about the device, from the 'devices' table
    """
    # Check if the user has previously inspected this device
    device_inspected_config_key = f'device_is_inspected_{device_dict["mac_address"]}'
    is_inspected = common.config_get(device_inspected_config_key, False)

    # Update the inspected status in the database if it is different
    if is_inspected != (device_dict['is_inspected'] == 1):
        # Note, on start time, the is_inspected sets to 0 for all devices, then changes to 1 once the user clicks the Inspect button
        logger.info(f"[Device List Page] Updating 'is_inspected' status for device to {is_inspected}")
        db_conn, rwlock = libinspector.global_state.db_conn_and_lock
        with rwlock:
            sql = """
                UPDATE devices
                SET is_inspected = ?
                WHERE mac_address = ?
            """
            db_conn.execute(sql, (is_inspected, device_dict['mac_address']))


@st.fragment(run_every=1)
def show_device_bar_graph(device_dict: dict):
    """
    Show the upload/download bar graph for a device.

    Args:
        device_dict (dict): information about the device, from the 'devices' table
    """
    # Get the Bar Graph data for upload/download
    device_upload, device_download = common.bar_graph_data_frame(int(time.time()))

    # Extra information on the device's metadata, e.g., OUI
    metadata_dict = json.loads(device_dict['metadata_json'])    # Get the device's custom name as set by the user
    device_custom_name = common.get_device_custom_name(device_dict['mac_address'])
    device_detail_url = f"/device_details?device_mac_address={device_dict['mac_address']}"
    title_text = f'**[{device_custom_name}]({device_detail_url})**'
    st.markdown(title_text)
    caption = f'{device_dict["ip_address"]} | {device_dict["mac_address"]}'
    if "oui_vendor" in metadata_dict:
        caption += f' | {metadata_dict["oui_vendor"]}'

    api_output = common.config_get(f'device_details@{device_dict["mac_address"]}', default={})
    if "Vendor" in api_output or "Explanation" in api_output:
        vendor = api_output.get("Vendor", "")
        explanation = api_output.get("Explanation", "")
        if vendor or explanation:
            caption += f"| Vendor: {vendor} | Explanation: {explanation}"
    st.caption(caption, help='IP address, MAC address, manufacturer OUI, and Device Identification API output')

    # --- Add bar charts for upload/download ---
    chart_col_upload, chart_col_download = st.columns(2)
    with chart_col_upload:
        device_upload_graph = device_upload[device_upload['mac_address'] == device_dict["mac_address"]]
        common.plot_traffic_volume(device_upload_graph,
                                   "Upload Traffic (sent by device) in the last 60 seconds")
    with chart_col_download:
        device_download_graph = device_download[device_download['mac_address'] == device_dict["mac_address"]]
        common.plot_traffic_volume(device_download_graph,
                                   "Download Traffic (sent by device) in the last 60 seconds")


@st.fragment(run_every=3)
def toggle_device_fragment(mac_address: str):
    # Maps short options to long options for display
    option_dict = {
        'inspected': ':material/troubleshoot: Inspected',
        'favorite': ':material/favorite: Favorite',
        'blocked': ':material/block: Blocked'
    }

    device_data = get_device_data(mac_address)
    update_device_inspected_status(device_data)

    # Reverse the option_dict to map long options back to short options
    option_reversed_dict = {v: k for k, v in option_dict.items()}

    # Read the device's favorite and blocked status from the config
    device_is_favorite_config_key = f'device_is_favorite_{mac_address}'
    device_is_favorite = common.config_get(device_is_favorite_config_key, False)

    device_is_blocked_config_key = f'device_is_blocked_{mac_address}'
    device_is_blocked = common.config_get(device_is_blocked_config_key, False)

    # Create a list of default options based on the device's status
    default_option_list = []
    device_inspected_config_key = f'device_is_inspected_{mac_address}'
    is_inspected = common.config_get(device_inspected_config_key, False)
    if is_inspected:
        default_option_list.append(option_dict['inspected'])
    if device_is_favorite:
        default_option_list.append(option_dict['favorite'])
    if device_is_blocked:
        default_option_list.append(option_dict['blocked'])

    def _device_options_changed_callback():
        # The long options selected by the user
        selected_list = st.session_state[f'device_options_{mac_address}']

        # Transform the long options back to short options
        selected_list = [option_reversed_dict[option] for option in selected_list]

        # Reset the device's status based on the selected options
        common.config_set(device_is_favorite_config_key, 'favorite' in selected_list)
        common.config_set(device_is_blocked_config_key, 'blocked' in selected_list)
        common.config_set(device_inspected_config_key, 'inspected' in selected_list)

    # Create a list of options to display
    st.pills(
        'Options',
        options=option_dict.values(),
        selection_mode='multi',
        default=default_option_list,
        label_visibility='collapsed',
        key=f"device_options_{mac_address}",
        on_change=_device_options_changed_callback
    )
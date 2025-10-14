import streamlit as st
import time
import json
import libinspector.global_state
import common
import logging
import functools
import os
import requests

logger = logging.getLogger("client")


def show():
    """
    Creating a page that shows what devices have been discovered so far
    """
    toast_obj = st.toast('Discovering devices...')
    show_list(toast_obj)


def worker_thread():
    """
    A worker thread to periodically clear the cache of call_predict_api.
    """
    logger.info("[Device ID API] Starting worker thread to periodically call the API for each device.")
    while True:
        time.sleep(15)
        db_conn, rwlock = libinspector.global_state.db_conn_and_lock
        # Get the list of devices from the database
        sql = """
              SELECT * \
              FROM devices
              WHERE is_gateway = 0 \
              """
        device_list = []
        with rwlock:
            for device_dict in db_conn.execute(sql):
                device_list.append(dict(device_dict))
        logger.info("[Device ID API] 15 seconds passed, will start calling API for each device if needed.")

        # Getting inputs and calling API
        for device_dict in device_list:
            dhcp_hostname, oui_vendor = common.get_device_metadata(device_dict['mac_address'])
            remote_hostnames = common.get_remote_hostnames(device_dict['mac_address'])
            try:
                api_output = call_predict_api(dhcp_hostname, oui_vendor, remote_hostnames, device_dict['mac_address'])
                common.config_set(f'device_details@{device_dict["mac_address"]}', api_output)
                if "Vendor" in api_output:
                    # Update name based on API
                    custom_name_key = f"device_custom_name_{device_dict['mac_address']}"
                    custom_name = api_output["Vendor"]
                    if api_output["Vendor"] != "":
                        common.config_set(custom_name_key, custom_name)
            except RuntimeError:
                continue


@functools.cache
def call_predict_api(dhcp_hostname: str, oui_vendor: str, remote_hostnames: str,
                     mac_address: str, url="https://dev-id-1.tailcedbd.ts.net/predict") -> dict:
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
        dhcp_hostname (str): The DHCP hostname of the device we want to use AI to get more info about
        oui_vendor (str): The OUI vendor of the device we want to use AI to get more info about
        remote_hostnames (str): The remote hostnames the device has contacted
        mac_address (str): The MAC address of the device we want to use AI to get more info about
        url (str): The API endpoint.
    Returns:
        dict: The response text from the API.
    """
    api_key = os.environ.get("API_KEY", "momo")
    device_tracked_key = f'tracked@{mac_address}'

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    data = {
        "prolific_id": common.config_get("prolific_id", ""),
        "mac_address": mac_address,
        "fields": {
            "oui_friendly": oui_vendor,
            "dhcp_hostname": dhcp_hostname,
            "remote_hostnames": remote_hostnames,
            "user_agent_info": "",
            "netdisco_info": "",
            "user_labels": "",
            "talks_to_ads": common.config_get(device_tracked_key, False)
        }
    }
    non_empty_field_values = [
        field_value
        for field_name, field_value in data["fields"].items()
        if field_name != "talks_to_ads" and bool(field_value)
    ]
    # TODO: We should make this 2 fields eventually...
    if len(non_empty_field_values) < 1:
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


@st.fragment(run_every=1)
def show_list(toast_obj: st.toast):
    """
    The main page that creates a "card" for each device that was found via IoT Inspector
    """
    human_readable_time = common.get_human_readable_time()
    st.markdown(f'Updated: {human_readable_time}')

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

    if not device_list:
        st.warning('We are still scanning the network for devices. Please wait a moment. This page will refresh automatically.')

    # Create a card entry for the discovered device
    for device_dict in device_list:
        st.markdown('---')
        show_device_card(device_dict)

    # Create a pop-up showing if any new devices were found
    prev_device_count = st.session_state.get('prev_device_count', 0)
    if len(device_list) > prev_device_count:
        toast_obj.toast(f'Discovered {len(device_list) - prev_device_count} new device(s)!', icon=':material/add_circle:')
        st.session_state['prev_device_count'] = len(device_list)
        time.sleep(1.5)  # Give the user a moment to read the toast


def show_device_card(device_dict: dict):
    """
    Process the data for a discovered device into a list of cards.

    Args:
        device_dict (dict): information about the device, from the 'devices' table
    """
    # Check if the user has previously inspected this device
    device_inspected_config_key = f'device_is_inspected_{device_dict["mac_address"]}'
    is_inspected = common.config_get(device_inspected_config_key, False)

    # Update the inspected status in the database if it is different
    if is_inspected != (device_dict['is_inspected'] == 1):
        db_conn, rwlock = libinspector.global_state.db_conn_and_lock
        with rwlock:
            sql = """
                UPDATE devices
                SET is_inspected = ?
                WHERE mac_address = ?
            """
            db_conn.execute(sql, (is_inspected, device_dict['mac_address']))

    # Extra information on the device's metadata, e.g., OUI
    metadata_dict = json.loads(device_dict['metadata_json'])

    # Get the device's custom name as set by the user
    device_custom_name = common.get_device_custom_name(device_dict['mac_address'])

    c1, c2 = st.columns([6, 4], gap='small')

    # show high level information, IP, Mac, OUI
    with c1:
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
        now = int(time.time())
        df_upload_bar_graph, df_download_bar_graph = common.bar_graph_data_frame(device_dict['mac_address'], now)
        common.plot_traffic_volume(df_upload_bar_graph, now, "Upload Traffic (sent by device) in the last 60 seconds")
        common.plot_traffic_volume(df_download_bar_graph, now,"Download Traffic (received by device) in the last 60 seconds")

    # Set whether a device is to be inspected, favorite, or blocked
    with c2:
        # Maps short options to long options for display
        option_dict = {
            'inspected': ':material/troubleshoot: Inspected',
            'favorite': ':material/favorite: Favorite',
            'blocked': ':material/block: Blocked'
        }

        # Reverse the option_dict to map long options back to short options
        option_reversed_dict = {v: k for k, v in option_dict.items()}

        # Read the device's favorite and blocked status from the config
        device_is_favorite_config_key = f'device_is_favorite_{device_dict["mac_address"]}'
        device_is_favorite = common.config_get(device_is_favorite_config_key, False)

        device_is_blocked_config_key = f'device_is_blocked_{device_dict["mac_address"]}'
        device_is_blocked = common.config_get(device_is_blocked_config_key, False)

        # Create a list of default options based on the device's status
        default_option_list = []
        if is_inspected:
            default_option_list.append(option_dict['inspected'])
        if device_is_favorite:
            default_option_list.append(option_dict['favorite'])
        if device_is_blocked:
            default_option_list.append(option_dict['blocked'])

        def _device_options_changed_callback():

            # The long options selected by the user
            selected_list = st.session_state[f'device_options_{device_dict["mac_address"]}']

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
            key=f"device_options_{device_dict['mac_address']}",
            on_change=_device_options_changed_callback
        )

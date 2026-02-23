import streamlit as st
import time
import libinspector.global_state
import common
import logging
import json


logger = logging.getLogger(__name__)


def show():
    """
    Creating a page that shows what devices have been discovered so far
    """
    toast_obj = st.toast('Discovering devices...')
    show_list(toast_obj)


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

    device_list = common.get_all_devices()
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
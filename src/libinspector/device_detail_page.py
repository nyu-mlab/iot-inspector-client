from typing import Any
import pandas
import streamlit as st
import libinspector.global_state
import pandas as pd
import datetime
import common
import time
from queue import Queue
import requests
import base64
import scapy.all as sc
import json
import os


_labeled_activity_packet_queue = Queue()


def show():
    """
    This function is the main entry point for the device details page.
    http://localhost:33721/device_details?device_mac_address=<mac-address>

    At the very top, it will show a list of devices to select from.

    If no device is selected, it will show a warning message.

    If a device is selected, the following is rendered:
    - activity inference (currently a placeholder function)
    - device details (A bar chart of traffic volume in the last 60 seconds, and a table of network flows)
    """
    device_mac_address = show_device_list()

    if not device_mac_address:
        st.warning("No device selected. Please select a device to view details.")
        return

    label_activity_workflow(device_mac_address)
    show_device_details(device_mac_address)


# TODO: Maybe have an undo button?
def label_activity_workflow(mac_address: str):
    """
    Workflow for labeling activity of the selected device.

    Steps:
    1. User must grant explicit permission to send data externally (shown once per session).
    2. Only one labeling session can be active at a time.
    3. User clicks "Label" button (resets previous labeling state).
    4. User selects an activity from a dropdown.
    5. User clicks "Start" button.
    6. A countdown from 5 to 1 is shown.
    7. The start epoch time is recorded.
    8. User performs the activity on the device.
    9. User clicks "Labeling Complete" button.
    10. The end epoch time is recorded.
    11. The selected activity, start, and end epoch times are displayed.
    12. User can click "Reset Labeling" to start a new labeling session.
    13. The activity label, MAC address, start, and end times are saved to the config file.
    """
    # Permission check (only once per session)
    if not st.session_state.get('external_data_permission_granted', False):
        st.warning(
            "As part of this research project, only the network activity of the device you select will be shared with NYU mLab, and only while you are labeling an activity. "
            "By entering your Prolific ID and continuing, you agree to share this data for research and compensation. "
            "**Please enter your correct Prolific ID to ensure you receive payment for your participation.**"
        )
        prolific_id = st.text_input("Enter your Prolific ID to continue:", key="prolific_id_input")
        if st.button("Continue"):
            if prolific_id.strip():
                st.session_state['external_data_permission_granted'] = True
                st.session_state['prolific_id'] = prolific_id.strip()
                st.rerun()
            else:
                st.warning("Prolific ID is required to proceed.")
        return

    # Helper to reset session state
    def reset_labeling_state():
        st.session_state['labeling'] = False
        st.session_state['countdown'] = False
        st.session_state['start_time'] = None
        st.session_state['end_time'] = None
        st.session_state['activity_label'] = None
        st.session_state['labeling_in_progress'] = False
        st.session_state['device_mac'] = None

    # Initialize session state if not present
    for key in ['labeling', 'countdown', 'start_time', 'end_time', 'activity_label', 'labeling_in_progress',
                'device_mac']:
        if key not in st.session_state:
            st.session_state[key] = None if key in ['start_time', 'end_time', 'activity_label', 'device_mac'] else False

    if st.button("Label"):
        if st.session_state['labeling_in_progress']:
            st.warning("A labeling session is already in progress. Please complete or reset it before starting a new one.")
        else:
            reset_labeling_state()
            st.session_state['labeling'] = True
            st.session_state['labeling_in_progress'] = True

    if st.session_state['labeling']:
        activity_json = os.path.join(os.path.dirname(__file__), 'data', 'activity.json')
        with open(activity_json, 'r') as f:
            activity_data = json.load(f)

        # Category selection
        categories = list(activity_data.keys())
        selected_category = st.selectbox("Select device category", categories)

        # Device selection
        devices = list(activity_data[selected_category].keys())
        selected_device = st.selectbox("Select device", devices)

        # Activity label selection
        activity_labels = activity_data[selected_category][selected_device]
        selected_label = st.selectbox("Select activity label", activity_labels)

        st.session_state['device_label'] = selected_device
        st.session_state['activity_label'] = selected_label
        if st.button("Start"):
            st.session_state['countdown'] = True
            st.session_state['labeling'] = False

    if st.session_state['countdown']:
        countdown_placeholder = st.empty()
        for i in range(5, 0, -1):
            countdown_placeholder.write(f"Starting in {i} seconds...")
            time.sleep(1)
        countdown_placeholder.empty()
        st.session_state['start_time'] = int(time.time())
        st.session_state['countdown'] = False
        # Start saving packets for this activity into an internal queue
        with libinspector.global_state.global_state_lock:
            libinspector.global_state.custom_packet_callback_func = save_labeled_activity_packets
            libinspector.global_state.labeling_target_mac = mac_address

    if st.session_state['start_time'] and not st.session_state['end_time']:
        st.write("Labeling in progress...")
        if st.button("Labeling Complete"):
            # Stop saving packets for this activity
            with libinspector.global_state.global_state_lock:
                libinspector.global_state.custom_packet_callback_func = None

            pending_packet_list = []
            while not _labeled_activity_packet_queue.empty():
                pending_packet_list.append(_labeled_activity_packet_queue.get())

            st.write(f"Total packets captured for labeling: {len(pending_packet_list)}")
            st.session_state['end_time'] = int(time.time())
            try:
                if len(pending_packet_list) > 0:
                    remote_host = common.config_get("packet_collector_host", 'mlab.cyber.nyu.edu')
                    remote_port = common.config_get("packet_collect_port", '443')
                    api_path = "/iot_inspector_data_capture/label_packets"
                    api_url = f"https://{remote_host}:{remote_port}{api_path}"
                    st.write(f"Sending labeled packets to API endpoint: {api_url}")
                    response = requests.post(
                        api_url,
                        json={
                            "packets": [
                                base64.b64encode(pkt).decode('utf-8') for pkt in pending_packet_list
                            ],
                            "prolific_id": st.session_state['prolific_id'],
                            "mac_address": mac_address,
                            "device_name": st.session_state['device_label'],
                            "activity_label": st.session_state['activity_label'],
                            "start_time": st.session_state['start_time'],
                            "end_time": st.session_state['end_time']
                        },
                        timeout=10
                    )
                    if response.status_code == 200:
                        st.success("Labeled packets successfully sent to the server.")
                        pending_packet_list.clear()
                    else:
                        st.error(f"Failed to send labeled packets. Server responded with status code {response.status_code}.")
                else:
                    st.error("No packets were captured for labeling.")
            except requests.RequestException as e:
                st.error(f"An error occurred while sending labeled packets: {e}")
            label_info = {
                "mac_address": mac_address,
                "activity_label": st.session_state['activity_label'],
                "start_time": st.session_state['start_time'],
                "end_time": st.session_state['end_time']
            }
            labels = common.config_get("labels", default=[])
            labels.append(label_info)
            common.config_set("labels", labels)
            reset_labeling_state()


def save_labeled_activity_packets(pkt):
    """
    Save the packet into a queue if it matches the device's MAC address we want to label activity for.

    Args:
        pkt: The network packet (scapy packet) to process.
    """
    mac_address = None
    with libinspector.global_state.global_state_lock:
        mac_address = libinspector.global_state.labeling_target_mac

    if mac_address and (pkt[sc.Ether].src == mac_address or pkt[sc.Ether].dst == mac_address):
        # We check both source and destination MAC to capture all relevant traffic
        _labeled_activity_packet_queue.put(pkt.original)


@st.cache_data(show_spinner=False)
def get_device_info(mac_address: str, _db_conn, _rwlock) -> dict[Any, Any] | None:
    """
    Fetches device info from the database with caching.

    Args:
        mac_address (str): The MAC address of the device to query. This is used
                           as the primary cache key.
        _db_conn: The database connection object. This is not used as part of
                  the cache key because it is not hashable.
        _rwlock: The read-write lock object. This is also not used as part of
                 the cache key because it is not hashable.

    Returns:
        dict: A dictionary containing the device's information, or None if not found.
    """
    sql = """
        SELECT * FROM devices
        WHERE mac_address = ?
    """
    with _rwlock:
        device_row = _db_conn.execute(sql, (mac_address,)).fetchone()
    # Convert the sqlite3.Row object to a standard dictionary to make it serializable
    if device_row:
        return dict(device_row)
    return None


def process_network_flows(df: pandas.DataFrame):
    """
    Helper function used for both upload and download for 'show_device_details'.

    Args:
        df: The Dataframe with SQL results to process and display.
    """
    if df.empty:
        st.warning("No network flows found for this device.")
        return

    df['first_seen'] = pd.to_datetime(df['first_seen'], unit='s')
    df['last_seen'] = pd.to_datetime(df['last_seen'], unit='s')
    local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    df['first_seen'] = df['first_seen'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)
    df['last_seen'] = df['last_seen'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)

    df['inferred_activity'] = None
    df['confirmation'] = False
    df = df.reset_index(drop=True)

    st.markdown("#### Network Flows")
    st.data_editor(df, width='content')


@st.fragment(run_every=1)
def show_device_details(mac_address: str):
    """
    This function has three things to show:
    - At the very top, it shows the device's custom name, MAC address, and IP address.
    - A bar chart of traffic volume in the last 60 seconds
    - A table of network flows with the following columns:
        - timestamp
        - src_info (a column that shows the source hostname, or IP if no hostname is available)
        - dest_info (a column that shows the destination hostname, or IP if no hostname is available)
        - byte_count
        - inferred_activity (a column that can be used for labeling)
        - confirmation (a column that can be used for confirming the inferred activity)

    Args:
        mac_address (str): The MAC address of the device to show details for.
    """

    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    device_custom_name = common.get_device_custom_name(mac_address)
    device_dict = get_device_info(mac_address, db_conn, rwlock)

    if not device_dict:
        st.error(f"No device found with MAC address: {mac_address}")
        return

    st.markdown(f"### {device_custom_name}")
    st.caption(f"MAC Address: {mac_address} | IP Address: {device_dict['ip_address']}")

    now = int(time.time())
    df_upload_bar_graph, df_download_bar_graph = common.bar_graph_data_frame(mac_address, now)
    sixty_seconds_ago = now - 60

    # Upload traffic (sent by device)
    sql_upload_hosts =  """
                 SELECT MIN(timestamp) AS first_seen,
                        MAX(timestamp) AS last_seen,
                        COALESCE(dest_hostname, dest_ip_address) AS dest_info,
                        SUM(byte_count) * 8 AS Bits
                 FROM network_flows
                 WHERE src_mac_address = ?
                   AND timestamp >= ?
                 GROUP BY dest_info
                 ORDER BY last_seen DESC
                 """

    # Download traffic (received by device)
    sql_download_hosts =  """
                 SELECT MIN(timestamp) AS first_seen,
                        MAX(timestamp) AS last_seen,
                        COALESCE(src_hostname, src_ip_address) AS src_info,
                        SUM(byte_count) * 8 AS Bits
                 FROM network_flows
                 WHERE dest_mac_address = ?
                   AND timestamp >= ?
                 GROUP BY src_info
                 ORDER BY last_seen DESC
                 """

    with rwlock:
        df_upload_host_table = pd.read_sql_query(sql_upload_hosts, db_conn, params=(mac_address, sixty_seconds_ago))
        df_download_host_table = pd.read_sql_query(sql_download_hosts, db_conn, params=(mac_address, sixty_seconds_ago))

    common.plot_traffic_volume(df_upload_bar_graph, now, "Upload Traffic (sent by device) in the last 60 seconds")
    process_network_flows(df_upload_host_table)

    common.plot_traffic_volume(df_download_bar_graph, now, "Download Traffic (received by device) in the last 60 seconds")
    process_network_flows(df_download_host_table)


def show_device_list():
    """
    This is shown at the top of the Device details page.
    This page allows you to change IoT device selection.
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

    if not device_list:
        st.warning("No devices found. Please inspect a device first.")
        st.stop()

    # Show a dropdown to select a device; each option shows both the device's MAC address and IP address
    device_options = [f"{common.get_device_custom_name(device['mac_address'])} - {device['ip_address']} - {device['mac_address']}" for device in device_list]
    device_options.insert(0, "(Select a device)")  # Add a placeholder option

    device_mac_address = st.query_params.get('device_mac_address', None)
    selected_index = 0
    if device_mac_address:
        # If a device MAC address is already selected, find its index in the options
        for i, option in enumerate(device_options):
            if option.endswith(device_mac_address):
                selected_index = i
                break

    def _selected_device_changed_callback():
        selected_device = st.session_state['selected_device']
        if selected_device == "(Select a device)":
            st.query_params['device_mac_address'] = None
        else:
            # Extract the MAC address from the selected option
            selected_device_mac_address = selected_device.split(" - ")[-1]
            st.query_params['device_mac_address'] = selected_device_mac_address

    st.selectbox(
        "Select a device to view details:",
        device_options,
        index=selected_index,
        key='selected_device',
        on_change=_selected_device_changed_callback
    )

    return device_mac_address




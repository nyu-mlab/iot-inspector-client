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
import logging
from collections import deque

_labeling_event_deque = deque()
_labeled_activity_packet_queue = Queue()
logger = logging.getLogger("client")


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
    # The logic for displaying the API message has been moved into this fragment,
    display_api_status()
    if not device_mac_address:
        st.warning("No device selected. Please select a device to view details.")
        return

    label_activity_workflow(device_mac_address)
    show_device_details(device_mac_address)


@st.fragment(run_every=10)
def display_api_status():
    """
    Continuously checks the global 'api_message' configuration variable
    and displays the corresponding Streamlit notification (success, error, or warning).
    This fragment runs every 10 seconds, ensuring the user sees updates from the
    background thread (label_thread) in real-time.
    """
    # Use st.empty() to ensure the message appears in the same place and is cleared on next run
    status_placeholder = st.empty()
    api_message = common.config_get('api_message', default='')

    if len(api_message) != 0:
        msg_type, msg = api_message.split('|', 1)
        if msg_type == 'success':
            status_placeholder.success(f"✅ {msg}")
        elif msg_type == 'error':
            status_placeholder.error(f"❌ {msg}")
        elif msg_type == 'warning':
            status_placeholder.warning(f"⚠️ {msg}")


def label_thread():
    """
    This thread continuously checks for labeled packets to send to the server.
    It runs every 15 seconds, and if the labeling session has ended, it processes
    and sends the packets in the queue to the remote API endpoint.
    """
    pending_packet_list = []
    logger.info("[Packets] Labeling Packets Thread started.")
    while True:
        time.sleep(15)
        logger.info("[Packets] Will check if there are labeled packets to send...")
        # 1. Check if labeling session has ended
        if len(_labeling_event_deque) == 0:
            logger.info("[Packets] There is no labeling event ready. Not sending packets.")
            continue
        else:
            logger.info(f"[Packets] Found labeling event, the queue is of size {len(_labeling_event_deque)}")

        # Make sure end time is NOT a none
        end_time = _labeling_event_deque[0].get('end_time', None)
        if end_time is None:
            logger.info("[Packets] End time hasn't been set yet, The labeling session is still ongoing. Not sending packets yet.")
            continue

        # If the labeling session is still ongoing, skip sending
        if time.time() <= end_time:
            logger.info("[Packets] Labeling session not complete yet. The end time is still in the future.")
            continue

        # 2. Process and empty the queue
        while not _labeled_activity_packet_queue.empty():
            packet = _labeled_activity_packet_queue.get()
            dt_object = datetime.datetime.fromtimestamp(packet.time)
            timestamp_str = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            logger.info(f"[Packets] Packet reports time-stamp of {timestamp_str}")
            packet_metadata = {
                "time": packet.time,
                "raw_data": base64.b64encode(packet.original).decode('utf-8')
            }
            pending_packet_list.append(packet_metadata)

        payload = _labeling_event_deque.popleft()
        payload['packets'] = pending_packet_list


        device_name = payload.get('device_name', 'Unknown Device')
        activity_label = payload.get('activity_label', 'Unknown Activity')
        duration = payload.get('end_time', 0) - payload.get('start_time', 0)
        label_data = f"Device: {device_name}, Activity: {activity_label}, Duration: {duration} seconds, Packets: {len(pending_packet_list)}"

        # 3. API Sending Logic - results are saved to api_message for display
        try:
            if len(pending_packet_list) > 0:
                logger.info(
                f"[Packets] {time.strftime('%Y-%m-%d %H:%M:%S')} - Packets to be sent: {len(pending_packet_list)}")
                remote_host = common.config_get("packet_collector_host", 'mlab.cyber.nyu.edu')
                remote_port = common.config_get("packet_collect_port", '443')
                api_path = "/iot_inspector_data_capture/label_packets"
                api_url = f"https://{remote_host}:{remote_port}{api_path}"

                # NOTE: We avoid st.write here, save the info to session_state instead
                response = requests.post(
                    api_url,
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    logger.info(f"[Packets] {time.strftime('%Y-%m-%d %H:%M:%S')} - All packets sent successfully. \n {label_data}")
                    display_message = f"Labeled packets successfully | {label_data}"
                    common.config_set('api_message', f"success|{display_message}")
                else:
                    logger.info(f"[Packets] {time.strftime('%Y-%m-%d %H:%M:%S')} - API Failed, packets NOT sent!.")
                    common.config_set('api_message', f"error|Failed to send labeled packets. Server status: {response.status_code}. {len(pending_packet_list)} Packets were not sent.")
            else:
                logger.info(f"[Packets] {time.strftime('%Y-%m-%d %H:%M:%S')} - No packets found to be labeled.")
                common.config_set('api_message', "error|No packets were captured for labeling.")
        except requests.RequestException as e:
            logger.info(f"[Packets] {time.strftime('%Y-%m-%d %H:%M:%S')} - An error occurred during API transmission: {e}")
            common.config_set('api_message', f"error|An error occurred during API transmission: {e}")
        finally:
            pending_packet_list.clear()


def reset_labeling_state():
    """
    Resets all state variables related to a labeling session.
    """
    st.session_state['countdown'] = False
    st.session_state['show_labeling_setup'] = False
    st.session_state['start_time'] = None
    st.session_state['end_time'] = None
    st.session_state['device_name'] = None
    st.session_state['activity_label'] = None


def _collect_packets_callback():
    """
    Executed when 'Start' is clicked. Sets the flag to trigger the countdown
    and packet start logic in the main function.
    """
    logger.info("[Packets] Start button clicked, initiating countdown and add to Label Deque...")
    st.session_state['countdown'] = True

    labeling_event = {
        "prolific_id": common.config_get('prolific_id', ''),
        "device_name": st.session_state['device_name'],
        "activity_label": st.session_state['activity_label'],
        "mac_address": st.session_state['mac_address'],
    }
    _labeling_event_deque.append(labeling_event)


def _send_packets_callback():
    """
    Executed when the 'Labeling Complete' button is clicked.
    Handles stopping packet collection and sending data to the server.
    """
    if not common.config_get('labeling_in_progress', default=False):
        common.config_set('api_message', "warning|No labeling session in progress. Please start a labeling session first.")
        return

    if common.config_get('packet_count', 0) == 0:
        st.warning("[Packets] No packets were captured for labeling.")
        logger.warning("[Packets] No packets were captured for labeling.")
        return

    logger.info("[Packets] Collect the end time and prep for packet collection.")
    if len(_labeling_event_deque) == 0:
        logger.warning("[Packets] No labeling event found in the queue when trying to set end time.")
    else:
        _labeling_event_deque[-1]['end_time'] = int(time.time())
        st.session_state['end_time'] = _labeling_event_deque[-1]['end_time']
    common.config_set('labeling_in_progress', False)
    common.config_set('packet_count', 0)
    reset_labeling_state()


def update_device_inspected_status(mac_address: str):
    """
    Manually update to inspected status so that all the packets can be collected for the MAC Address.
    Args:
        mac_address (str): The MAC address of the device to update.
    """
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    with rwlock:
        sql = """
            UPDATE devices
            SET is_inspected = ?
            WHERE mac_address = ?
        """
        db_conn.execute(sql, (1, mac_address))
    device_inspected_config_key = f'device_is_inspected_{mac_address}'
    common.config_set(device_inspected_config_key, True)


def label_activity_workflow(mac_address: str):
    """
    Manages the interactive, state-driven workflow for labeling network activity in Streamlit.
    This function orchestrates the entire user labeling process, enforcing a strict sequential order
    (Label -> Start -> Complete) using Streamlit's session state and dynamic button disabling.
    It handles user consent, activity selection persistence, the 5-second countdown to start
    packet capture, and uses an in-place placeholder to display real-time status messages
    (success, error, warning) from the API submission.

    This is passed to the start and send callbacks for packet filtering and API submission.

    Steps of the Workflow:
    1. Permission Check: Ensures explicit user consent for external data sharing via a Prolific ID entry.
    2. State Initialization: Initializes all necessary session state variables (e.g., 'start_time', 'activity_label').
    3. Start/Reset: Displays the 'Label' button, which resets any previous session and activates the activity selection UI.
    4. Activity Selection: Allows the user to select the device category, device, and specific activity label. This UI remains visible and persistent throughout the collection phase for user reference.
    5. Control Buttons: Displays 'Start' and 'Labeling Complete' buttons with dynamic 'disabled' states to enforce the correct sequence.
    6. Countdown: Executes a 5-second blocking countdown in the main thread after 'Start' is clicked and before packet collection begins.
    7. Packet Collection: Starts packet capture by setting a global callback function (save_labeled_activity_packets) for the specified mac_address.
    8. Status Display: Uses a st.empty() placeholder and the api_message state variable to display feedback immediately beneath the control buttons for superior UX.
    9. Final Summary: Upon session completion, displays the recorded activity label, device name, and duration.

    Args:
        mac_address (str): The MAC address of the device targeted for the activity labeling.
    """
    # --- 1. Initialize State ---
    for key in ['countdown', 'show_labeling_setup', 'start_time', 'end_time', 'device_name', 'activity_label']:
        if key not in st.session_state:
            st.session_state[key] = None if key in ['start_time', 'end_time', 'device_name', 'activity_label'] else False

    # --- 2. Initial "Label" Button / State Check ---
    session_active = common.config_get('labeling_in_progress', default=False)

    if st.button(
            "Label",
            disabled=session_active or st.session_state['end_time'] is not None,
            help="Click to start labeling an activity for this device. This will reset any previous labeling state."
    ):
        if len(_labeling_event_deque) > 0:
            st.warning("A previous labeling session is still active. Try again in 15 seconds when the previous session's packets should have been sent.")
            return
        update_device_inspected_status(mac_address)
        # Keep labeling_in_progress=True until the very end, controlled by config_get/set
        common.config_set('labeling_in_progress', True)
        common.config_set('api_message', '')
        st.session_state['show_labeling_setup'] = True
        st.rerun()  # Rerun to show setup menu

    # --- 3. Label Setup UI (Persists through collection) ---
    if st.session_state['show_labeling_setup'] or st.session_state['start_time']:
        st.subheader("1. Select Activity")

        activity_json = os.path.join(os.path.dirname(__file__), 'data', 'activity.json')
        try:
            with open(activity_json, 'r') as f:
                activity_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            st.error("Error loading activity definitions. Check 'data/activity.json'.")
            return

        # Use the status of the session (running or done) to control if the select boxes are disabled
        is_currently_labeling = st.session_state['start_time'] is not None and st.session_state['end_time'] is None
        categories = list(activity_data.keys())
        selected_category = st.selectbox("Select device category",
                                         categories,
                                         key="category_select",
                                         disabled=is_currently_labeling)

        devices = list(activity_data[selected_category].keys())
        selected_device = st.selectbox("Select device", devices,
                                       key="device_select",
                                       disabled=is_currently_labeling)

        activity_labels = activity_data[selected_category][selected_device]
        activity_labels.append("Idle Time: No Activity, just background traffic for 2 minutes")
        selected_label = st.selectbox("Select activity label",
                                      activity_labels,
                                      key="label_select",
                                      disabled=is_currently_labeling)

        # Update state on selection changes, unless running
        if not is_currently_labeling:
            st.session_state['device_name'] = selected_device
            st.session_state['activity_label'] = selected_label
            st.session_state['mac_address'] = mac_address

        st.subheader("2. Control Collection")
        col1, col2 = st.columns(2)
        with col1:
            # "Start" button is enabled only when setup is complete and not yet started.
            st.button(
                "Start",
                on_click=_collect_packets_callback,
                disabled=is_currently_labeling or st.session_state['countdown'],  # Disable if running or counting down
                help="Click to start collecting packets for labeling. You will have 5 seconds to prepare before packet collection starts."
            )

        with col2:
            # "Labeling Complete" button is enabled only when collection is active.
            st.button(
                "Labeling Complete",
                on_click=_send_packets_callback,
                disabled=not is_currently_labeling,  # Enable only when actively labeling (start_time is set, end_time is not)
                help="Click to stop collecting packets and send the labeled packets to NYU mLab."
            )

    # --- 4. Countdown Logic (Blocking, happens between Start and Collection) ---
    if st.session_state['countdown']:
        _labeling_event_deque[-1]['start_time'] = int(time.time())
        st.session_state['start_time'] = _labeling_event_deque[-1]['start_time']
        countdown_placeholder = st.empty()
        for i in range(5, 0, -1):
            countdown_placeholder.write(f"**Starting packet capture in {i} seconds...**")
            time.sleep(1)
        countdown_placeholder.empty()

        # Start packet capture after countdown
        st.session_state['countdown'] = False
        logger.info("[Packets] The start time is set, packet collection is now ACTIVE.")
        st.info("Packet collection is **ACTIVE**. Perform the activity on your device now.")
        st.info(
            f"Currently labeling **{st.session_state['activity_label']}** on **{st.session_state['device_name']}**.")
        st.rerun()  # Rerun to update button state and message


def save_labeled_activity_packets(pkt):
    """
    Save the packet into a queue if it matches the device's MAC address we want to label activity for.

    Args:
        pkt: The network packet (scapy packet) to process.
    """
    if len(_labeling_event_deque) == 0:
        return

    # TODO: Think with Danny, but say the first label in the queue is done,
    # TODO: how do I know if it isn't label event 1, 2, 3, or ..., n that actually needs this packet?
    # TODO: maybe have config store a point to element in the deque that is being labeled?
    # TODO: For now, I am sticking to one element in the deque at a time.
    mac_address = _labeling_event_deque[0].get('mac_address', None)
    start_time = _labeling_event_deque[0].get('start_time', None)
    end_time = _labeling_event_deque[0].get('end_time', None)

    # start_time must be set and not after the packet time
    if start_time is None:
        return

    # Confirm if packet is not before start_time
    if pkt.time < start_time:
        return

    # if end_time is set, ensure packet is not after end_time
    if end_time is not None:
        if pkt.time > end_time:
            return

    # We check both source and destination MAC to capture all relevant traffic
    if mac_address and (pkt[sc.Ether].src == mac_address or pkt[sc.Ether].dst == mac_address):
        # We also check if the timestamp is correct
        _labeled_activity_packet_queue.put(pkt)
        packet_count = common.config_get('packet_count', 0)
        packet_count += 1
        common.config_set('packet_count', packet_count)


@st.cache_data(show_spinner=False)
def get_device_info(mac_address: str) -> dict[Any, Any] | None:
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
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    with rwlock:
        device_row = db_conn.execute(sql, (mac_address,)).fetchone()
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
    st.markdown("#### Network Flows")
    st.data_editor(df, width='content')



@st.cache_data(ttl=5, show_spinner=False)
def get_host_flow_tables(mac_address: str, sixty_seconds_ago: int):
    """
    The flow table is cached for 5 seconds (TTL). This drastically reduces the
    database calls for the heaviest part of the UI, improving performance and stability.

    This function fetches the upload/download host table data, cached for 5 seconds.
    """
    # Upload traffic (sent by device)
    sql_upload_hosts = """
                       SELECT DATETIME(MIN(timestamp), 'unixepoch', 'localtime') AS first_seen,
                              DATETIME(MAX(timestamp), 'unixepoch', 'localtime') AS last_seen,
                              COALESCE(dest_hostname, dest_ip_address)           AS dest_info,
                              ROUND(SUM(byte_count) / 1024.0, 2)                 AS KiloBytes
                       FROM network_flows
                       WHERE src_mac_address = ?
                         AND timestamp >= ?
                       GROUP BY dest_info
                       ORDER BY last_seen DESC \
                       """

    # Download traffic (received by device)
    sql_download_hosts = """
                         SELECT DATETIME(MIN(timestamp), 'unixepoch', 'localtime') AS first_seen,
                                DATETIME(MAX(timestamp), 'unixepoch', 'localtime') AS last_seen,
                                COALESCE(src_hostname, src_ip_address)             AS src_info,
                                ROUND(SUM(byte_count) / 1024.0, 2)                 AS KiloBytes
                         FROM network_flows
                         WHERE dest_mac_address = ?
                           AND timestamp >= ?
                         GROUP BY src_info
                         ORDER BY last_seen DESC \
                         """

    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    with rwlock:
        df_upload_host_table = pd.read_sql_query(sql_upload_hosts, db_conn, params=[mac_address, sixty_seconds_ago])
        df_download_host_table = pd.read_sql_query(sql_download_hosts, db_conn, params=[mac_address, sixty_seconds_ago])

    return df_upload_host_table, df_download_host_table


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
    device_dict = get_device_info(mac_address)

    if not device_dict:
        st.error(f"No device found with MAC address: {mac_address}")
        return

    st.markdown(f"### {device_custom_name}")
    st.caption(f"MAC Address: {mac_address} | IP Address: {device_dict['ip_address']}")

    now = int(time.time())
    df_upload_bar_graph, df_download_bar_graph = common.bar_graph_data_frame(mac_address, now)
    sixty_seconds_ago = now - 60
    df_upload_host_table, df_download_host_table = get_host_flow_tables(mac_address, sixty_seconds_ago)

    common.plot_traffic_volume(df_upload_bar_graph, "Upload Traffic (sent by device) in the last 60 seconds")
    process_network_flows(df_upload_host_table)

    common.plot_traffic_volume(df_download_bar_graph, "Download Traffic (received by device) in the last 60 seconds")
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

    is_labeling_active = common.config_get('labeling_in_progress', default=False)

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
        on_change=_selected_device_changed_callback,
        disabled=is_labeling_active
    )

    if is_labeling_active:
        st.warning(
            "⚠️ **Device selection is locked** while a labeling session is in progress.")

    return device_mac_address


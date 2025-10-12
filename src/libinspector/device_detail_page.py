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

    if not device_mac_address:
        st.warning("No device selected. Please select a device to view details.")
        return

    label_activity_workflow(device_mac_address)
    show_device_details(device_mac_address)


def reset_labeling_state():
    """Resets all state variables related to a labeling session."""
    common.config_set('labeling_in_progress', False)
    st.session_state['countdown'] = False
    st.session_state['start_time'] = None
    st.session_state['end_time'] = None
    # We keep activity_label and device_label until the end, so only reset these:
    # st.session_state['activity_label'] = None
    # st.session_state['device_label'] = None
    st.session_state['show_labeling_setup'] = False
    st.session_state['api_message'] = None


def _collect_packets_callback():
    """
    Executed when 'Start' is clicked. Sets the flag to trigger the countdown
    and packet start logic in the main function.
    """
    logger.info("[Packets] Start button clicked, initiating countdown...")
    st.session_state['countdown'] = True
    # st.rerun() will be triggered by Streamlit after the callback completes


def _send_packets_callback(mac_address: str):
    """
    Executed when the 'Labeling Complete' button is clicked.
    Handles stopping packet collection and sending data to the server.
    Args:
        mac_address (str): The MAC address of the device being labeled.
    """
    if not common.config_get('labeling_in_progress', default=False):
        st.session_state['api_message'] = "warning|No labeling session in progress. Please start a labeling session first."
        return

    logger.info("[Packets] Starting to send labeled packets...")

    # 1. Stop packet collection
    with libinspector.global_state.global_state_lock:
        libinspector.global_state.custom_packet_callback_func = None
        libinspector.global_state.labeling_target_mac = None

    # 2. Process and empty the queue
    pending_packet_list = []
    while not _labeled_activity_packet_queue.empty():
        pending_packet_list.append(_labeled_activity_packet_queue.get())

    st.session_state['end_time'] = int(time.time())

    # 3. API Sending Logic - results are saved to api_message for display
    try:
        if len(pending_packet_list) > 0:
            remote_host = common.config_get("packet_collector_host", 'mlab.cyber.nyu.edu')
            remote_port = common.config_get("packet_collect_port", '443')
            api_path = "/iot_inspector_data_capture/label_packets"
            api_url = f"https://{remote_host}:{remote_port}{api_path}"

            # NOTE: We avoid st.write here, save the info to session_state instead

            response = requests.post(
                api_url,
                json={
                    "packets": [
                        base64.b64encode(pkt).decode('utf-8') for pkt in pending_packet_list
                    ],
                    "prolific_id": st.session_state.get('prolific_id', 'unknown'),
                    "mac_address": mac_address,
                    "device_name": st.session_state.get('device_label'),
                    "activity_label": st.session_state.get('activity_label'),
                    "start_time": st.session_state.get('start_time'),
                    "end_time": st.session_state['end_time']
                },
                timeout=10
            )
            if response.status_code == 200:
                st.session_state['api_message'] = f"success| {len(pending_packet_list)} Labeled packets successfully sent to the server."
            else:
                st.session_state[
                    'api_message'] = f"error|Failed to send labeled packets. Server status: {response.status_code}."
        else:
            st.session_state['api_message'] = "error|No packets were captured for labeling."

    except requests.RequestException as e:
        st.session_state['api_message'] = f"error|An error occurred during API transmission: {e}"
    # st.rerun() will occur after this, showing the results.


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
    8. Status Display: Uses an st.empty() placeholder and the api_message state variable to display feedback immediately beneath the control buttons for superior UX.
    9. Final Summary: Upon session completion, displays the recorded activity label, device name, and duration.

    Args:
        mac_address (str): The MAC address of the device targeted for the activity labeling.
    """
    # --- 1. Permission Check ---
    if not st.session_state.get('external_data_permission_granted', False):
        # ... (Permission Check UI remains here) ...
        # [Content truncated for clarity, assuming original code is here]
        st.warning(
            "As part of this research project, only the network activity of the device you select will be shared with NYU mLab, and only while you are labeling an activity. "
            "By entering your Prolific ID and continuing, you agree to share this data for research and compensation. "
            "**Please confirm your Prolific ID is correct to ensure you receive payment for your participation.**"
        )
        prolific_id = common.config_get("prolific_id", "")
        if st.button("Continue", help="Click to confirm you have read and agree to the above statement."):
            if prolific_id.strip():
                st.session_state['external_data_permission_granted'] = True
                st.session_state['prolific_id'] = prolific_id
                st.rerun()
            else:
                st.warning("Prolific ID is required to proceed.")
        return

    # --- 2. Initialize State ---
    for key in ['start_time', 'end_time', 'activity_label', 'device_label', 'countdown',
                'api_message', 'show_labeling_setup']:
        if key not in st.session_state:
            st.session_state[key] = None if key in ['start_time', 'end_time', 'activity_label', 'device_label',
                                                    'api_message'] else False

    # --- 3. Initial "Label" Button / State Check ---
    session_active = common.config_get('labeling_in_progress', default=False)

    if st.button(
            "Label",
            disabled=session_active or st.session_state['end_time'] is not None,
            help="Click to start labeling an activity for this device. This will reset any previous labeling state."
    ):
        reset_labeling_state()
        # Keep labeling_in_progress=True until the very end, controlled by config_get/set
        common.config_set('labeling_in_progress', True)
        st.session_state['show_labeling_setup'] = True
        st.rerun()  # Rerun to show setup menu

    # --- 4. Label Setup UI (Persists through collection) ---
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
        is_running = st.session_state['start_time'] is not None and st.session_state['end_time'] is None

        categories = list(activity_data.keys())
        selected_category = st.selectbox("Select device category",
                                         categories,
                                         key="category_select",
                                         disabled=is_running)

        devices = list(activity_data[selected_category].keys())
        selected_device = st.selectbox("Select device", devices,
                                       key="device_select",
                                       disabled=is_running)

        activity_labels = activity_data[selected_category][selected_device]
        selected_label = st.selectbox("Select activity label",
                                      activity_labels,
                                      key="label_select",
                                      disabled=is_running)

        # Update state on selection changes, unless running
        if not is_running:
            st.session_state['device_label'] = selected_device
            st.session_state['activity_label'] = selected_label
        else:
            st.info(
                f"Currently labeling **{st.session_state['activity_label']}** on **{st.session_state['device_label']}**.")

        st.subheader("2. Control Collection")
        col1, col2 = st.columns(2)
        with col1:
            # "Start" button is enabled only when setup is complete and not yet started.
            st.button(
                "Start",
                on_click=_collect_packets_callback,
                disabled=is_running or st.session_state['countdown'],  # Disable if running or counting down
                help="Click to start collecting packets for labeling. You will have 5 seconds to prepare before packet collection starts."
            )

        with col2:
            # "Labeling Complete" button is enabled only when collection is active.
            st.button(
                "Labeling Complete",
                on_click=_send_packets_callback,
                args=(mac_address,),
                disabled=not is_running,  # Enable only when actively labeling (start_time is set, end_time is not)
                help="Click to stop collecting packets and send the labeled packets to NYU mLab."
            )

        # --- MESSAGE PLACEMENT FIX (Issue 1) ---
        # Define the placeholder right below the buttons
        status_placeholder = st.empty()

        # Check and display API message on rerun
        if st.session_state.get('api_message'):
            msg_type, msg = st.session_state['api_message'].split('|', 1)
            if msg_type == 'success':
                status_placeholder.success(f"✅ {msg}")
            elif msg_type == 'error':
                status_placeholder.error(f"❌ {msg}")
            elif msg_type == 'warning':
                status_placeholder.warning(f"⚠️ {msg}")

    # --- 5. Countdown Logic (Blocking, happens between Start and Collection) ---
    if st.session_state['countdown']:
        countdown_placeholder = st.empty()
        for i in range(5, 0, -1):
            countdown_placeholder.write(f"**Starting packet capture in {i} seconds...**")
            time.sleep(1)
        countdown_placeholder.empty()

        # Start packet capture after countdown
        st.session_state['start_time'] = int(time.time())
        st.session_state['countdown'] = False
        with libinspector.global_state.global_state_lock:
            libinspector.global_state.custom_packet_callback_func = save_labeled_activity_packets
            libinspector.global_state.labeling_target_mac = mac_address
        st.info("Packet collection is **ACTIVE**. Perform the activity on your device now.")
        st.rerun()  # Rerun to update button state and message

    # --- 6. Final Results and Display ---
    if st.session_state['end_time']:
        st.header("Labeling Session Complete")
        st.markdown(f"**Device:** `{st.session_state.get('device_label')}`")
        st.markdown(f"**Activity:** `{st.session_state.get('activity_label')}`")
        duration = st.session_state['end_time'] - (st.session_state['start_time'] or st.session_state['end_time'])
        st.markdown(f"**Duration:** {duration} seconds")
        st.button("Reset Labeling",
                  on_click=reset_labeling_state,
                  help="Click to reset the labeling session and start over.")


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
        logger.info(f"[Packets] {time.strftime('%Y-%m-%d %H:%M:%S')} - Labeled packets in queue: {_labeled_activity_packet_queue.qsize()}")


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




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
from typing import Deque, Dict, Any

import event_detection.global_state

_labeling_event_deque : Deque[Dict[str, Any]] = deque()
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

    device_dict = get_device_info(device_mac_address)
    if not device_dict:
        st.error(f"No device found with MAC address: {device_mac_address}")
        return
    
    ip_address = device_dict['ip_address']
    show_cool_down()
    label_activity_workflow(device_mac_address, ip_address)
    device_custom_name = common.get_device_custom_name(device_mac_address)

    st.markdown(f"### {device_custom_name}")
    st.caption(f"MAC Address: {device_mac_address} | IP Address: {ip_address}")
    show_device_bar_graph(device_mac_address)
    show_device_network_flow(device_mac_address)


@st.cache_data
def _load_json_data(filename: str) -> dict:
    """
    Loads JSON data from a file in the 'data' directory and caches the result.
    The cache is unique for each distinct filename provided.

    Args:
        filename: The name of the JSON file (e.g., 'activity.json').

    Returns:
        The dictionary content of the file, or an empty dictionary upon failure.
    """
    # NOTE: os.path.dirname(__file__) only works if this code is in a file,
    # not interactively in a shell/notebook. This is standard practice for module code.
    data_path = os.path.join(os.path.dirname(__file__), 'data', filename)

    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # FileNotFoundError is common for optional config files, log as warning
        logger.warning(f"Configuration file not found: {data_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {data_path}: {e}")
        return {}


def generate_label_progress_table(current_label_status: dict):
    """
    Takes the API response string (which is a dictionary string of labeled files),
    parses it, and displays it as a clean Streamlit table.

    Example input data_string:
    "{'Amazon Echo Spot:Idle Time...': 1, 'Amazon Plug:Android LAN On...': 4, ...}"
    """
    data_rows = []

    for full_label, count in current_label_status.items():
        # Split only on the first colon to correctly separate Device from the rest of the Label
        try:
            device, activity_label = full_label.split(':', 1)
        except ValueError:
            # Handle cases where the key might be malformed (shouldn't happen with the Python parser)
            device = "N/A"
            activity_label = full_label

        data_rows.append({
            "Device": device.strip(),
            "Activity Label": activity_label.strip(),
            "Labels Completed": count
        })

    if not data_rows:
        return

    # Create and sort the DataFrame
    df = pd.DataFrame(data_rows)
    df = df.sort_values(by=["Device", "Activity Label"])

    st.markdown("#### Progress Summary")
    st.dataframe(
        df,
        width='content',
        hide_index=True,
        column_order=("Device", "Activity Label", "Labels Completed"),
        column_config={
            "Labels Completed": st.column_config.NumberColumn(
                "Labels Completed",
                help="Total number of PCAP files successfully labeled for this device and activity.",
                format="%d",
            )
        }
    )


@st.fragment(run_every=1)
def show_active_labeling_status(mac_address: str, settings_data: dict):
    """
    Shows a continuous timer and status bar while a labeling session is active.
    This fragment runs every second to provide real-time feedback.
    """
    is_currently_labeling = common.config_get('labeling_in_progress', default=False)
    start_time = st.session_state.get('start_time')
    end_time = st.session_state.get('end_time')

    if is_currently_labeling and start_time is not None and end_time is None:
        elapsed_seconds = int(time.time() - start_time)

        # For visual effect, cap the progress bar at a duration (e.g., 2 minutes)
        max_duration_visual = settings_data.get("max_idle_time_seconds", 600)
        progress_value = min(elapsed_seconds / max_duration_visual, 1.0)

        # Ensure the container visually pops
        with st.container(border=True):
            st.markdown("#### ⏱️ Active Labeling Session")
            col_t1, col_t2 = st.columns([1, 3])
            with col_t1:
                st.metric("Time Elapsed", f"{elapsed_seconds} seconds")
            with col_t2:
                st.info(f"**Device:** {st.session_state.get('device_name', 'N/A')}")
                st.info(f"**Activity:** {st.session_state.get('activity_label', 'N/A')}")

            # Use a progress bar that cycles when it reaches the visual max
            progress_text = f"Collecting packets... (Max visual duration {max_duration_visual} seconds)"
            if progress_value >= 1.0:
                 progress_text = f"Collecting packets... Timer exceeded {max_duration_visual} seconds"

            st.progress(progress_value, text=progress_text)
            st.caption(f"Traffic for MAC: `{mac_address}` is being queued.")

    elif end_time is not None and start_time is not None:
        # Show a summary after completion until the 'Label' button is pressed again
        duration = end_time - start_time
        st.success(f"✅ Session Completed! Collected **{duration} seconds** of activity.")


@st.fragment(run_every=10)
def show_cool_down():
    """
    Let users know how much time they have until they can start labeling again.
    Once the cooldown is complete, the Start button is re-enabled.
    """
    settings_data = _load_json_data("settings.json")
    cooldown_seconds = settings_data.get("labeling_cooldown_seconds", 60)
    last_end_time = common.config_get('last_label_end_time', 0)
    # If never labeled before, skip cooldown
    if last_end_time == 0:
        return
    time_since_last_label = time.time() - last_end_time
    is_on_cooldown = time_since_last_label < cooldown_seconds

    if is_on_cooldown:
        st.session_state['cooldown_in_progress'] = True
        remaining_time = int(cooldown_seconds - time_since_last_label)
        st.warning(f"⏳ **Cooldown active:** Please wait {remaining_time} more seconds before starting a new labeling session.")
    else:
        # ONLY rerun if we were previously 'on cooldown'. This prevents the infinite rerun loop
        if st.session_state.get('cooldown_in_progress', False):
            st.session_state['cooldown_in_progress'] = False
            # This triggers the rest of the GUI to become 'live' again
            st.rerun()


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

    progress_data_dict = common.config_get('label_progress_data', default={})
    if len(progress_data_dict) != 0:
        st.subheader("Current Labeling Progress")
        generate_label_progress_table(progress_data_dict)


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

        end_dt_object = datetime.datetime.fromtimestamp(end_time)
        end_timestamp_str = end_dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        start_dt_object = datetime.datetime.fromtimestamp(_labeling_event_deque[0].get('start_time', None))
        start_timestamp_str = start_dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        logger.info(f"[Packets] Labeling session has started at {start_timestamp_str}")
        # 2. Process and empty the queue
        while not _labeling_event_deque[0]["packet_queue"].empty():
            packet = _labeling_event_deque[0]["packet_queue"].get()
            dt_object = datetime.datetime.fromtimestamp(packet.time)
            timestamp_str = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            logger.info(f"[Packets] Packet reports time-stamp of {timestamp_str}")
            packet_metadata = {
                "time": packet.time,
                "raw_data": base64.b64encode(packet.original).decode('utf-8')
            }
            pending_packet_list.append(packet_metadata)
        logger.info(f"[Packets] Labeling session has ended at {end_timestamp_str}")

        payload = _labeling_event_deque.popleft()
        payload['packets'] = pending_packet_list

        # REMOVE the non-serializable Queue object before sending the payload
        if 'packet_queue' in payload:
            del payload['packet_queue']

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
                remote_port = common.config_get("packet_collector_port", '443')
                api_path = "/iot_inspector_data_capture/label_packets"
                api_url = f"https://{remote_host}:{remote_port}{api_path}"

                # NOTE: We avoid st.write here, save the info to session_state instead
                response = requests.post(
                    api_url,
                    json=payload,
                    timeout=30
                )
                if response.status_code == 200:
                    logger.info(f"[Packets] {time.strftime('%Y-%m-%d %H:%M:%S')} - All packets sent successfully. \n {label_data}")
                    current_pcap_directory_information = response.json()['message']
                    common.config_set('label_progress_data', current_pcap_directory_information)

                    display_message = f"Labeled packets successfully | {label_data}"
                    common.config_set('api_message', f"success|{display_message}")

                else:
                    error_message = response.json()['message']
                    logger.info(f"[Packets] {time.strftime('%Y-%m-%d %H:%M:%S')} - API Failed, packets NOT sent!. Message: {error_message}")
                    common.config_set('api_message', f"error|Failed to send labeled packets. Server status: {response.status_code} | Message: {error_message}")
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
    common.config_set('packet_count', 0)
    common.config_set('labeling_in_progress', False)
    st.session_state['countdown'] = False
    st.session_state['show_labeling_setup'] = False
    st.session_state['start_time'] = None
    st.session_state['end_time'] = None
    st.session_state['device_name'] = None
    st.session_state['activity_label'] = None
    st.session_state['device_category'] = None
    st.session_state['confirm_duplicate'] = False


def _collect_packets_callback():
    """
    Executed when 'Start' is clicked. Sets the flag to trigger the countdown
    and packet start logic in the main function.
    """
    logger.info("[Packets] Start button clicked, initiating countdown and add to Label Deque...")
    st.session_state['countdown'] = True

    labeling_event = {
        "prolific_id": common.config_get('prolific_id', ''),
        "device_category": st.session_state['device_category'],
        "device_name": st.session_state['device_name'],
        "activity_label": st.session_state['activity_label'],
        "mac_address": st.session_state['mac_address'],
        "packet_queue": Queue()
    }
    _labeling_event_deque.append(labeling_event)

    # Check if it is a duplicate labeling event
    last_category = common.config_get('last_labeled_category', default="")
    last_device = common.config_get('last_labeled_device', default="")
    last_label = common.config_get('last_labeled_label', default="")
    if (st.session_state['device_category'] == last_category and
        st.session_state['device_name'] == last_device and
        st.session_state['activity_label'] == last_label):

        logger.info("A duplicate labeling occurred!")
        consecutive_duplicate_count = common.config_get('consecutive_duplicate_count', default=0)
        consecutive_duplicate_count += 1
        common.config_set('consecutive_duplicate_count', consecutive_duplicate_count)


def _cancel_label_callback():
    """
    Executed when the 'Cancel current labeling session' button is clicked.
    Handles stopping packet collection and resetting state.
    """
    if not common.config_get('labeling_in_progress', default=False):
        common.config_set('api_message', "warning|No labeling session in progress. Please start a labeling session first.")
        return

    logger.info("[Packets] Labeling session canceled by user.")
    if len(_labeling_event_deque) > 0:
        logger.info("[Packets] Removing labeling event from the queue due to cancellation.")
        _labeling_event_deque.pop()
    common.config_set('api_message', "warning|Labeling session has been canceled. No packets were sent.")
    reset_labeling_state()


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
        st.warning("No labeling event found in the queue when trying to set end time.")
        return
    else:
        # Set a minimum end time of 1 minute after start time to ensure idle activity is captured
        user_end_time = int(time.time())
        user_end_dt_object = datetime.datetime.fromtimestamp(user_end_time)
        user_end_timestamp_str = user_end_dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        logger.info(f"[Packets] User requested end time at {user_end_timestamp_str}")
        # Set to 0 if you are letting users fully decide when to send a recording.
        # For maximum recording, I'm setting it for a day maximum allowed time
        minimum_recording_time = common.config_get("minimum_record_time_seconds", 0)
        maximum_recording_time = common.config_get("maximum_record_time_seconds", 86400)
        _labeling_event_deque[-1]['end_time'] = max(_labeling_event_deque[-1]['start_time'] + minimum_recording_time,
                                                    min(user_end_time,
                                                        _labeling_event_deque[-1]['start_time'] + maximum_recording_time))
        st.session_state['end_time'] = _labeling_event_deque[-1]['end_time']
    common.config_set('last_label_end_time', st.session_state['end_time'])
    logger.info("[Packets] Labeling session ended, packets will be sent in the background thread.")
    reset_labeling_state()

    # Reset the duplicate count if this label is different from the last one
    last_category = common.config_get('last_labeled_category', default="")
    last_device = common.config_get('last_labeled_device', default="")
    last_label = common.config_get('last_labeled_label', default="")
    if (_labeling_event_deque[-1].get('device_category', '') != last_category or
        _labeling_event_deque[-1].get('device_name', '') != last_device or
        _labeling_event_deque[-1].get('activity_label', '') != last_label):
        logger.info("[Packets] Activity selection is different from last labeled activity, resetting duplicate count.")
        common.config_set('consecutive_duplicate_count', 0)

    common.config_set('last_labeled_category', _labeling_event_deque[-1].get('device_category'))
    common.config_set('last_labeled_device', _labeling_event_deque[-1].get('device_name'))
    common.config_set('last_labeled_label', _labeling_event_deque[-1].get('activity_label'))


def _confirm_mapping_callback(mac_address: str, current_device: str, ip_address: str):
    """
    Saves the confirmed mapping and clears the pending state.
    Args:
        mac_address (str): The MAC address being confirmed.
        current_device (str): The device name being confirmed.
        ip_address (str): The IP Address of the device being confirmed.
    """
    labels_for_device = {
        'device_mac': mac_address,
        'device_ip': ip_address,
        'device_name': current_device,
        'current_time': int(time.time()),
        'current_time_string': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    common.config_set(f"label@{current_device}", labels_for_device)
    # Also save a reverse lookup for conflict detection
    common.config_set(f"mac_to_device@{mac_address}", current_device)
    logger.info(f"Create mapping of {current_device} to {mac_address}")
    st.toast(f"✅ Mapping confirmed for {current_device}")


def _resolve_conflict_callback(mac_address: str, current_device: str):
    """
    Logs the conflict error and deletes the old mapping to allow a fresh start.
    Args:
        mac_address (str): The MAC address with the conflict.
        current_device (str): The device name the user is trying to map to.
    """
    old_device = common.config_get(f"mac_to_device@{mac_address}")
    logger.error(
        f"User reported mapping conflict: MAC {mac_address} was {old_device}, now {current_device}. Deleting cache.")

    # TODO: Create POST request, delete old mapping on server side as well.

    # Delete the old mappings
    if old_device:
        common.config_set(f"label@{old_device}", {})
    common.config_set(f"mac_to_device@{mac_address}", "")
    st.toast("⚠️ Previous mapping deleted. Confirm the correct device mapping next time.")
    reset_labeling_state()


def _cancel_mapping_callback():
    """
    Simply force a selection change or clear query params to 'reset' the page
    """
    st.toast("Cancel labeling due to labeling mismatch detected!")
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


def label_activity_workflow(mac_address: str, ip_address: str):
    """
    Manages the interactive, state-driven workflow for labeling network activity in Streamlit.
    This function orchestrates the entire user labeling process, enforcing a strict sequential order
    (Label -> Start -> Complete) using Streamlit's session state and dynamic button disabling.
    It handles user consent, activity selection persistence, the 5-second countdown to start
    packet capture, and uses a placeholder to display real-time status messages
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
        ip_address (str): The IP address of the device targeted for the activity labeling.
    """
    # --- 1. Initialize State ---
    settings_data = _load_json_data("settings.json")
    maximum_duplicate_labels = settings_data.get("max_duplicate_labels", 2)
    for key in ['countdown', 'show_labeling_setup', 'start_time', 'end_time', 'device_name', 'activity_label', 'confirm_duplicate', 'cooldown_in_progress']:
        if key not in st.session_state:
            st.session_state[key] = None if key in ['start_time', 'end_time', 'device_name', 'activity_label'] else False

    # --- 2. Initial "Label" Button / State Check ---
    session_active = common.config_get('labeling_in_progress', default=False)

    if st.button(
            "Label",
            disabled=session_active or st.session_state['cooldown_in_progress'] or st.session_state['end_time'] is not None,
            help="Click to start labeling an activity for this device. This will reset any previous labeling state."
    ):
        if not settings_data:
            st.error("Error loading settings definitions. Check logs.")
            return
        device_oui_vendor = common.config_get(f"oui@{mac_address}", default="Unknown Vendor")
        is_whitelisted = False
        for vendor in settings_data.get("Allowed Vendors", []):
            # Check if the device name contains the vendor name (case-insensitive)
            if vendor.lower() in device_oui_vendor.lower():
                is_whitelisted = True
                break

        if not is_whitelisted and not common.config_get("debug", default=False):
            vendor_list = ", ".join(settings_data.get("Allowed Vendors", []))
            st.warning(
                f"🚨 **Device not whitelisted for labeling!**\n\n"
                f"The device's vendor **'{device_oui_vendor}'** does not appear to be from an allowed vendor. "
                f"Only devices from the following vendors are currently allowed for labeling: **{vendor_list}**. "
                f"Please select a whitelisted device or ensure the device name is correctly configured."
            )
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

        activity_data = _load_json_data("activity.json")
        if not activity_data:
            st.error("Error loading activity definitions. Check logs.")
            return
        # Use the status of the session (running or done) to control if the select boxes are disabled
        # Note that start_time is only set by the 'Start' button click
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
        max_idle_time = settings_data.get("max_idle_time_seconds", 600)
        idle_key = f"Idle Time: No Activity, just background traffic for {max_idle_time} seconds"
        if idle_key not in activity_labels:
            activity_labels.append(idle_key)
        selected_label = st.selectbox("Select activity label",
                                      activity_labels,
                                      key="label_select",
                                      disabled=is_currently_labeling)

        # Update state on selection changes, unless running
        if not is_currently_labeling:
            st.session_state['device_category'] = selected_category
            st.session_state['device_name'] = selected_device
            st.session_state['activity_label'] = selected_label
            st.session_state['mac_address'] = mac_address

        # CHECK 1: CONFIRM THAT MAC/IP MAPS TO CORRECT DEVICE!
        # TODO: Technically you can have two or more MAC address that are Echos, etc. but for now, lets keep it simple.
        # Confirm correlation between label and device name
        current_device = st.session_state['device_name']
        labels_for_device = common.config_get(f"label@{current_device}", default={})
        existing_device_for_mac = common.config_get(f"mac_to_device@{mac_address}", default='')

        if existing_device_for_mac and existing_device_for_mac != current_device:
            st.error("🛑 **Device Mapping Conflict!**")
            st.warning(f"""
                This MAC address (`{mac_address}`) / IP (`{ip_address}`) was previously 
                confirmed as a **{existing_device_for_mac}**. 
                You are now trying to label it as a **{current_device}**.
            """)
            col1, col2 = st.columns(2)
            with col1:
                st.button(
                    "Fix it: Clear old identity",
                    on_click=_resolve_conflict_callback,
                    args=(mac_address, current_device),
                    help="Click if you mislabeled the device name previously.",
                    use_container_width=True
                )
            with col2:
                st.button("Cancel Labeling",
                          on_click=_cancel_mapping_callback,
                          help="Click to cancel labeling.",
                          use_container_width=True)
            # Stop execution here so they can't start labeling with a conflict
            return

        # --- 2. First-time Confirmation (Device name never seen before) ---
        elif not labels_for_device:
            st.info(f"ℹ️ **First-time Labeling for {current_device}**")
            st.warning(f"""
                Please confirm that this device is indeed a **{current_device}** with:
                - **IP:** `{ip_address}`
                - **MAC:** `{mac_address}`
                - You can confirm this by either checking Device settings under Wi-Fi for IP address, 
                or any app that you are connecting to interact with the device.
            """)
            col1, col2 = st.columns(2)
            with col1:
                st.button(
                    "Yes, Confirm",
                    on_click=_confirm_mapping_callback,
                    args=(mac_address, current_device, ip_address),
                    type="primary",
                    use_container_width=True
                )
            with col2:
                st.button("Cancel Labeling",
                          on_click=_cancel_mapping_callback,
                          use_container_width=True,
                          help="Click to cancel labeling.")
            st.caption("Note: Mislabeling physical devices will invalidate your data submission.")
            # Stop execution until they click the button
            return

        # --- 3. Routine Check (Device name matches the recorded MAC) ---
        elif labels_for_device.get('device_mac') != mac_address:
            st.error(
                f"❌ **Label Mismatch!** This `{current_device}` label is already tied to a different physical device "
                f"(MAC: `{labels_for_device.get('device_mac')}`). Please select the correct device name.")
            return

        # CHECK 2: DUPLICATE LABELING DETECTION
        last_category = common.config_get('last_labeled_category', default="")
        last_device = common.config_get('last_labeled_device', default="")
        last_label = common.config_get('last_labeled_label', default="")

        consecutive_duplicate_count = common.config_get('consecutive_duplicate_count', default=0)
        requires_confirmation = False

        # Check if the duplicate count is at or above the threshold
        # Remember, maximum_duplicate_labels is the number of allowed duplicates, so say you want 5 labels
        # You should set maximum_duplicate_labels=4
        if consecutive_duplicate_count >= maximum_duplicate_labels:
            logger.info("Maximum duplicate labeling attempts exceeded, requiring user confirmation.")
            requires_confirmation = True
            st.warning(f"""
            ⚠️ **Warning: You selected the same activity combination as the last {consecutive_duplicate_count + 1} successful submission(s)!**
            (Category: `{last_category}`, Device: `{last_device}`, Activity: `{last_label}`)
            Are you sure you want to collect this activity again? To label a different activity, please adjust the selections above. 
            ** Mislabeled data may risk payment for your Prolific submission. **
            """)

            # Use a checkbox for explicit confirmation
            st.session_state['confirm_duplicate'] = st.checkbox(
                "Yes, I confirm I want to label this exact activity again.",
                key="duplicate_confirm_checkbox",
                value=st.session_state['confirm_duplicate'] # maintain state across rerun
            )

        st.subheader("2. Control Collection")
        show_active_labeling_status(mac_address, settings_data)
        col1, col2, col3 = st.columns(3)
        with col1:
            # Determine if the start button should be disabled
            start_disabled = is_currently_labeling or st.session_state['countdown']

            # If it's a duplicate label, it must also be confirmed
            if requires_confirmation:
                start_disabled = start_disabled or not st.session_state['confirm_duplicate']

            # "Start" button is enabled only when setup is complete and not yet started.
            st.button(
                "Start",
                on_click=_collect_packets_callback,
                disabled=start_disabled,
                help="Click to start collecting packets for labeling. You will have 5 seconds to prepare before packet collection starts."
            )

        with col2:
            # "Cancel" button is enabled only during labeling, should someone made a mistake undo it
            st.button(
                "Cancel current labeling session",
                on_click=_cancel_label_callback,
                disabled=not is_currently_labeling,
                help="Click to cancel the current labeling session. This will stop packet collection and discard any collected packets."
            )

        with col3:
            # If it's a duplicate label, it must also be confirmed
            label_disabled = not is_currently_labeling
            if requires_confirmation:
                label_disabled = label_disabled or not st.session_state['confirm_duplicate']

            # "Labeling Complete" button is enabled only when collection is active.
            st.button(
                "Labeling Complete",
                on_click=_send_packets_callback,
                disabled=label_disabled,  # Enable only when actively labeling (start_time is set, end_time is not)
                help="Click to stop collecting packets and send the labeled packets to NYU mLab."
            )

    # --- 4. Countdown Logic (Blocking, happens between Start and Collection) ---
    if st.session_state['countdown']:
        _labeling_event_deque[-1]['start_time'] = int(time.time())
        st.session_state['start_time'] = _labeling_event_deque[-1]['start_time']
        countdown_placeholder = st.empty()
        for i in range(5, 0, -1):
            if i == 5:
                countdown_placeholder.markdown(f"**Prepare Activity Now!** Packet capture starts in **{i} seconds...**")
            elif i == 1:
                countdown_placeholder.markdown("**GO!** Begin the activity **NOW!**")
            else:
                countdown_placeholder.markdown(f"**Get Ready!** Capture starts in **{i} seconds...**")
            time.sleep(1)
        countdown_placeholder.empty()

        # Start packet capture after countdown
        st.session_state['countdown'] = False
        logger.info("[Packets] The start time is set, packet collection is now ACTIVE.")
        st.rerun()  # Rerun to update button state and message


def save_labeled_activity_packets(pkt):
    """
    Save the packet into a queue if it matches the device's MAC address we want to label activity for.

    Args:
        pkt: The network packet (scapy packet) to process.
    """

    # Note: (Jakaria) I need to save a copy of the packet, for event inference
    event_detection.global_state.packet_queue.put(pkt)

    if len(_labeling_event_deque) == 0:
        return

    mac_address = _labeling_event_deque[-1].get('mac_address', None)
    start_time = _labeling_event_deque[-1].get('start_time', None)
    end_time = _labeling_event_deque[-1].get('end_time', None)

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
        _labeling_event_deque[-1]["packet_queue"].put(pkt)
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


def process_network_flows(df: pd.DataFrame, chart_title: str):
    """
    Helper function used for both upload and download for 'show_device_details'.

    Args:
        df: The Dataframe with SQL results to process and display.
        chart_title: The title to display above the chart.
    """
    if df.empty:
        st.warning("No network flows found for this device.")
        return
    st.markdown(chart_title)
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
def show_device_bar_graph(mac_address: str):
    """
    Show a bar graph of traffic volume for the device in the last 60 seconds, split by upload (sent) and download (received).
    """
    now = int(time.time())
    device_upload, device_download = common.bar_graph_data_frame(now)

    device_upload_graph = device_upload[device_upload['mac_address'] == mac_address]
    common.plot_traffic_volume(device_upload_graph, "Upload Traffic (sent by device) in the last 60 seconds",
                               full_width=True)

    device_download_graph = device_download[device_download['mac_address'] == mac_address]
    common.plot_traffic_volume(device_download_graph, "Download Traffic (received by device) in the last 60 seconds",
                               full_width=True)


@st.fragment(run_every=1)
def show_device_network_flow(mac_address: str):
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
    now = int(time.time())
    sixty_seconds_ago = now - 60
    df_upload_host_table, df_download_host_table = get_host_flow_tables(mac_address, sixty_seconds_ago)
    process_network_flows(df_upload_host_table, "#### Upload Network Hosts (sent by device) in the last 60 seconds")
    process_network_flows(df_download_host_table, "#### Download Network Hosts (received by device) in the last 60 seconds")
    display_inferred_events(mac_address)


def display_inferred_events(mac_address: str):
    """
    Snapshot the queue without consuming it so other threads remain unaffected
    """
    q = event_detection.global_state.filtered_event_queue
    with q.mutex:
        events_snapshot = list(q.queue)

    # 1. Fetch current list from config (under your new key)
    current_event_list = common.config_get("event_list", [])

    # 2. Build a set of "seen" fingerprints (Time + Event)
    # This prevents adding the exact same event at the exact same time twice.
    seen = {(e['Time'], e['Event']) for e in current_event_list}

    rows = []
    for item in events_snapshot:
        if not isinstance(item, tuple) or len(item) != 3:
            continue

        device, ts, event = item
        if device == mac_address:
            rows.append({"Time": ts, "Event": event})
            if (ts, event) not in seen:
                seen.add((ts, event))

    # 3. Update the config only if there's new data
    current_event_list.extend(seen)
    # Optional: Keep it tidy by sorting by timestamp
    current_event_list.sort(key=lambda x: x['Time'])
    common.config_set("event_list", current_event_list)

    if not rows:
        st.info("No inferred events yet for this device.")
        return

    # rows.sort(key=lambda r: r["_ts"] if isinstance(r["_ts"], (int, float)) else 0, reverse=True)
    df = pd.DataFrame(rows)[["Time", "Event"]]

    st.markdown("#### Inferred Events")
    st.data_editor(df, hide_index=True, width='content')



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
            "⚠️ **Device selection is locked** while a labeling session is in progress. Do NOT close this window!!")

    return device_mac_address


import datetime
import os
import time
import threading
import json
import functools
import requests
import libinspector.global_state
from libinspector.privacy import is_ad_tracked
import pandas as pd
from typing import Any
import streamlit as st
import logging
import re

config_file_name = 'config.json'
config_lock = threading.Lock()
config_dict = {}

logger = logging.getLogger("client")
warning_text = (
    "⚠️ **IoT Inspector Warning**\n\n"
    "This tool monitors network traffic using techniques such as ARP spoofing. "
    "Such activity may be detected as a network attack. By proceeding, you confirm "
    "that you own the network or have permission from your IT administrator to run this tool.\n\n"
    "**Please note:**\n"
    "- Your network may be slowed or disrupted — if this happens, simply close IoT Inspector.\n"
    "- Metadata of your network traffic (e.g., which IPs/domains your devices communicate with) is shared anonymously with NYU researchers during the labeling stage."
)

def show_warning():
    """
    Displays a warning message to the user about network monitoring and ARP spoofing.
    Uses Streamlit to show the warning and manages acceptance state via query parameters.

    @return: bool
        True if the warning is still being shown (user has not accepted).
        False if the user has accepted the warning and can proceed.
    """
    current_id = config_get("prolific_id", "")

    # --- GATE 1: PROLIFIC ID CHECK (Must be valid to proceed to confirmation) ---
    if is_prolific_id_valid(current_id):
        # --- SHOW CONFIRMATION UI (Only reached if ID is valid but warning is unaccepted) ---
        st.subheader("1. Prolific ID Confirmation")
        st.info(f"Your currently stored ID is: `{current_id}`")

        # Allows the user to change the ID, which forces them back through GATE 1
        if st.button("Change Prolific ID", help="Clicking this will clear your stored ID and return you to the ID entry form."):
            config_set("prolific_id", "")  # Clear the stored ID
            st.rerun()

        if not config_get("suppress_warning", False):
            st.markdown("---")
            st.subheader("2. Network Monitoring Warning")
            st.markdown(warning_text)

            if st.button("OK, I understand and wish to proceed", help="Clicking this confirms that you understand the warning and wish to proceed."):
                config_set("suppress_warning", True)
                st.rerun()

        return not is_prolific_id_valid(config_get("prolific_id", ""))
    else:
        # ID is missing or invalid -> BLOCK and show input form
        st.subheader("Prolific ID Required")
        st.warning("Please enter your Prolific ID to proceed. This ID is essential for data labeling.")

        with st.form("prolific_id_form"):
            input_id = st.text_input(
                "Enter your Prolific ID (1-50 Alphanumeric Characters):",
                value="",
                key="prolific_id_input"
            ).strip()

            submitted = st.form_submit_button("Submit ID")

            if submitted:
                if is_prolific_id_valid(input_id):
                    config_set("prolific_id", input_id)
                    st.success("Prolific ID accepted. Please review the details below.")
                    st.rerun()  # Rerun to jump to the confirmation step (GATE 2)
                else:
                    st.error("Invalid Prolific ID. Must be 1-50 alphanumeric characters.")

        return True  # BLOCK: ID check still needs resolution.


def is_prolific_id_valid(prolific_id: str) -> bool:
    """
    Performs sanity checks on the Prolific ID:
    1. Not empty.
    2. Length between 1 and 50 characters (inclusive).
    3. Contains only alphanumeric characters (A-Z, a-z, 0-9).
    Args:
        prolific_id (str): The Prolific ID to validate.

    Returns:
        bool: True if the ID is non-empty, 1-50 characters long, and alphanumeric; False otherwise.
    """
    if not prolific_id or not isinstance(prolific_id, str):
        return False

    # 2. Length check
    if not 1 <= len(prolific_id) <= 50:
        return False

    # 3. Alphanumeric check using regex (ensures no special characters)
    if not re.fullmatch(r'^[a-zA-Z0-9]+$', prolific_id):
        return False

    return True


def bar_graph_data_frame(mac_address: str, now: int):
    sixty_seconds_ago = now - 60
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock

    sql_upload_chart = """
                       SELECT timestamp, SUM (byte_count) * 8 AS Bits
                       FROM network_flows
                       WHERE src_mac_address = ?
                         AND timestamp >= ?
                       GROUP BY timestamp
                       ORDER BY timestamp DESC
                       """

    sql_download_chart = """
                         SELECT timestamp, SUM (byte_count) * 8 AS Bits
                         FROM network_flows
                         WHERE dest_mac_address = ?
                           AND timestamp >= ?
                         GROUP BY timestamp
                         ORDER BY timestamp DESC
                         """

    with rwlock:
        df_upload_bar_graph = pd.read_sql_query(sql_upload_chart, db_conn,
                                                params=(mac_address, sixty_seconds_ago))
        df_download_bar_graph = pd.read_sql_query(sql_download_chart, db_conn,
                                                  params=(mac_address, sixty_seconds_ago))
    return df_upload_bar_graph, df_download_bar_graph


def plot_traffic_volume(df: pd.DataFrame, now: int, chart_title: str):
    """
    Plots the traffic volume over time.

    Args:
        df (pd.DataFrame): DataFrame containing 'Time' and 'Bits' columns.
        now: The current epoch time from which the sql query was executed
        chart_title: The title to display above the chart.
    """
    if df.empty:
        st.caption("No traffic data to display in chart.")
    else:
        st.markdown(f"#### {chart_title}")
        df['seconds_ago'] = now - df['timestamp'].astype(int)
        df = df.set_index('seconds_ago').reindex(range(0, 60), fill_value=0).reset_index()
        st.bar_chart(df.set_index('seconds_ago')['Bits'], width='content')


def get_device_metadata(mac_address: str):
    """
    Retrieve the DHCP hostname and OUI vendor for a device from the database.

    Args:
        mac_address (str): The MAC address of the device.

    Returns:
        tuple: (dhcp_hostname, oui_vendor) as strings. Returns empty strings if not found.
    """
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    sql = """
        SELECT metadata_json FROM devices
        WHERE mac_address = ?
    """
    with rwlock:
        row = db_conn.execute(sql, (mac_address,)).fetchone()
        if row:
            metadata = json.loads(row['metadata_json'])
            dhcp_hostname = metadata.get('dhcp_hostname', "")
            oui_vendor = metadata.get('oui_vendor', "")
        else:
            dhcp_hostname = ""
            oui_vendor = ""
    return dhcp_hostname, oui_vendor


def get_remote_hostnames(mac_address: str):
    """
    Retrieve all distinct remote hostnames associated with a device's MAC address from network flows.

    Args:
        mac_address (str): The MAC address of the device.

    Returns:
        str: A '+'-joined string of hostnames, or an empty string if none are found.
    """
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    sql = """
        SELECT DISTINCT hostname
        FROM (
            SELECT src_hostname AS hostname FROM network_flows
            WHERE src_mac_address = ?
            UNION
            SELECT dest_hostname AS hostname FROM network_flows
            WHERE src_mac_address = ?
        ) AS combined
        WHERE hostname IS NOT NULL
    """
    with rwlock:
        rows = db_conn.execute(sql, (mac_address, mac_address)).fetchall()
    hostnames = [row['hostname'] for row in rows if row['hostname']]
    is_tracked = any(is_ad_tracked(hostname) for hostname in hostnames)
    config_set(f'tracked@{mac_address}', is_tracked)
    remote_hostnames = '+'.join(hostnames) if hostnames else ""
    return remote_hostnames


@st.cache_data(show_spinner=False)
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
        "prolific_id": config_get("prolific_id", ""),
        "mac_address": mac_address,
        "fields": {
            "oui_friendly": oui_vendor,
            "dhcp_hostname": dhcp_hostname,
            "remote_hostnames": remote_hostnames,
            "user_agent_info": "",
            "netdisco_info": "",
            "user_labels": "",
            "talks_to_ads": config_get(device_tracked_key, False)
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

    logger.info("[Device ID API] Calling API with data: %s", json.dumps(data, indent=4))

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"[Device ID API] API request failed: {e}")
        raise RuntimeError("API request failed, not caching this result.")

    logger.info("[Device ID API] API query successful!")
    config_set(f'device_details@{mac_address}', result)
    return result


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


def config_get(key, default=None) -> Any:
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


def config_get_prefix(key_prefix: str):
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


def config_set(key: str, value: Any):
    """
    Set a configuration value.

    Args:
        key (str): The configuration key.
        value (Any): The value to set, can be str, bool, etc.
    """
    with config_lock:
        initialize_config_dict()
        config_dict[key] = value

        # Write the updated config_dict to the file
        with open(config_file_name, 'w') as f:
            json.dump(config_dict, f, indent=2, sort_keys=True)


def get_device_custom_name(mac_address: str) -> str:
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


@functools.cache
def get_sql_query(sql_file_name: str) -> str:
    """
    Get the SQL query from a file.

    Args:
        sql_file_name (str): The name of the SQL file.

    Returns:
        str: The SQL query as a string read from a file
    """
    with open(sql_file_name, 'r') as f:
        return f.read().strip()
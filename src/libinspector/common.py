import datetime
import time
import threading
import json
import functools
import pandas as pd
import typing
import streamlit as st
import logging
import re
import matplotlib.pyplot as plt
import libinspector.global_state
from libinspector.privacy import is_ad_tracked


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

def remove_warning():
    """
    Remove the warning screen by setting the suppress_warning flag in the config.
    This lasts for the duration of this IoT Inspector session.
    """
    config_set("suppress_warning", True)


def reset_prolific_id():
    """
    Clear the stored Prolific ID, forcing the user to re-enter it.
    """
    config_set("prolific_id", "")


def show_warning():
    """
    Displays a warning message to the user about network monitoring and ARP spoofing.
    Uses Streamlit to show the warning and manages acceptance state via query parameters.

    @return: bool
        True if the warning is still being shown (user has not accepted).
        False if the user has accepted the warning and can proceed.
    """
    current_id = config_get("prolific_id", "")
    st.subheader("1. Prolific ID Confirmation")
    if current_id != "":
        st.info(f"Your currently stored ID is: `{current_id}`")
        st.button("Change Prolific ID",
                  on_click=reset_prolific_id,
                  help="Clicking this will clear your stored ID and return you to the ID entry form.")

    # --- GATE 1: PROLIFIC ID CHECK (Must be valid to proceed to confirmation) ---
    if is_prolific_id_valid(current_id):
        # Check if the warning is NOT suppressed. If it's not suppressed, we show the UI
        # and MUST return True (Block execution) until the user clicks the button.
        if not config_get("suppress_warning", False):
            st.markdown("---")
            st.subheader("2. Network Monitoring Warning")
            st.markdown(warning_text)

            st.button("OK, I understand and wish to proceed",
                      on_click=remove_warning,
                      help="Clicking this confirms that you understand the warning and wish to proceed.")

            # Since the warning is displayed and unaccepted, we must block.
            return True

        # If we reach here, ID is valid AND suppress_warning is True.
        return False
    else:
        # ID is missing or invalid -> BLOCK and show input form
        st.subheader("Prolific ID Required")
        st.warning("Please enter your Prolific ID to proceed. "
                   "This ID is essential for data labeling and your payment. "
                   "If you are NOT part of the study, please input an arbitrary alphanumeric ID.")

        with st.form("prolific_id_form"):
            input_id = st.text_input(
                "Enter your Prolific ID:",
                value="",
                key="prolific_id_input"
            ).strip()
            submitted = st.form_submit_button("Submit ID", help="Submit your Prolific ID to proceed.")

            if submitted:
                if is_prolific_id_valid(input_id):
                    # 1. Set the valid ID
                    config_set("prolific_id", input_id)
                    st.success("Prolific ID accepted. Please review the details below.")

                    # 2. Rerun the script. In the next run, is_prolific_id_valid(current_id)
                    #    will be True, and the user jumps to the warning acceptance (Gate 2).
                    st.rerun()
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


@st.cache_data(ttl=1, show_spinner=False)
def bar_graph_data_frame(now: int):
    """
    Retrieves and processes network flow data for ALL non-gateway devices
    for the last 60 seconds, performing zero-filling directly in the SQL query.

    Args:
        now (int): The current epoch timestamp.
    Returns:
        (pd.DataFrame, pd.DataFrame): DataFrames for upload and download traffic,
                                      containing 'mac_address', 'seconds_ago', and 'Bits'.
    """
    sixty_seconds_ago = now - 60
    # Parameters array: [?1/now, ?2/sixty_seconds_ago]
    params = [now, sixty_seconds_ago]

    # --- SQL for Upload Chart: Includes mac_address and Zero-Filling for all devices ---
    sql_upload_chart = """
    WITH RECURSIVE seq(s) AS (
      -- Generate 60 time slots (0 to 59 seconds ago)
      SELECT 0
      UNION ALL
      SELECT s + 1 FROM seq WHERE s < 59
    ),
    device_macs AS (
        -- Select all non-gateway MAC addresses to include in the template
        SELECT mac_address FROM devices WHERE is_gateway = 0
    ),
    zero_fill_template AS (
        -- Create a template of (MAC, seconds_ago) for every device (60 * N rows)
        SELECT T1.mac_address, T2.s AS seconds_ago
        FROM device_macs T1, seq T2
    ),
    agg AS (
      -- Aggregate ACTUAL traffic, grouped by source MAC and seconds_ago
      SELECT src_mac_address AS mac_address,
             CAST((?1 - timestamp) AS INTEGER) AS seconds_ago,
             SUM(byte_count) * 8 AS Bits
      FROM network_flows
      WHERE timestamp >= ?2
      GROUP BY src_mac_address, seconds_ago
    )
    -- Join the template (ensuring zero fill) with the aggregated data
    SELECT z.mac_address,
           z.seconds_ago,
           COALESCE(a.Bits, 0) AS Bits
    FROM zero_fill_template z
    LEFT JOIN agg a
      ON z.mac_address = a.mac_address AND z.seconds_ago = a.seconds_ago
    ORDER BY z.mac_address, z.seconds_ago DESC
    """

    # --- SQL for Download Chart: Includes mac_address and Zero-Filling for all devices ---
    sql_download_chart = """
    WITH RECURSIVE seq(s) AS (
      SELECT 0
      UNION ALL
      SELECT s + 1 FROM seq WHERE s < 59
    ),
    device_macs AS (
        SELECT mac_address FROM devices WHERE is_gateway = 0
    ),
    zero_fill_template AS (
        SELECT T1.mac_address, T2.s AS seconds_ago
        FROM device_macs T1, seq T2
    ),
    agg AS (
      -- Aggregate ACTUAL traffic, grouped by destination MAC and seconds_ago
      SELECT dest_mac_address AS mac_address,
             CAST((?1 - timestamp) AS INTEGER) AS seconds_ago,
             SUM(byte_count) * 8 AS Bits
      FROM network_flows
      WHERE timestamp >= ?2
      GROUP BY dest_mac_address, seconds_ago
    )
    SELECT z.mac_address,
           z.seconds_ago,
           COALESCE(a.Bits, 0) AS Bits
    FROM zero_fill_template z
    LEFT JOIN agg a
      ON z.mac_address = a.mac_address AND z.seconds_ago = a.seconds_ago
    ORDER BY z.mac_address, z.seconds_ago DESC
    """

    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    with rwlock:
        df_upload_bar_graph = pd.read_sql_query(sql_upload_chart, db_conn, params=params)
        df_download_bar_graph = pd.read_sql_query(sql_download_chart, db_conn, params=params)

    return df_upload_bar_graph, df_download_bar_graph


def plot_traffic_volume(df: pd.DataFrame, chart_title: str, full_width: bool = False):
    """
    Plots the traffic volume over time. The bar goes from right to left,
    like Task Manager in Windows.

    Args:
        df (pd.DataFrame): DataFrame containing 'Time' and 'Bits' columns.
        chart_title: The title to display above the chart.
        full_width: Whether to use full width for the chart (True) or a smaller size (False).
    """
    if df.empty:
        st.caption("No traffic data to display in chart.")
        return

    # 1. Prepare data and sort: Sort by seconds_ago descending.
    # This places the older data on the left and the most recent data on the right.
    df_plot = df.drop(columns=['mac_address'])
    df_plot = df_plot.sort_values(by='seconds_ago', ascending=False).reset_index(drop=True)

    # 2. Create the Matplotlib figure
    if full_width:
        # Larger figure size for full-page view
        fig, ax = plt.subplots(figsize=(16, 5))
    else:
        # Smaller figure size for two-column view (like in the card)
        fig, ax = plt.subplots(figsize=(10, 4))

    # 3. Create the bar chart
    # Use the index as the x-position, and 'Bits' as the height.
    bars = ax.bar(df_plot.index, df_plot['Bits'], color='#1f77b4')  # Streamlit blue

    # Optional: Add clear labels to the bars for visual clarity
    for bar in bars:
        # Only label the tallest bars to prevent clutter
        if bar.get_height() > df_plot['Bits'].max() * 0.1:
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height(),
                    f'{bar.get_height():.0f}',
                    ha='center', va='bottom', fontsize=8)

    # 4. Set labels and title
    ax.set_title(chart_title, fontsize=14)
    ax.set_ylabel('Traffic Volume (Bits)', fontsize=10)

    # Set X-axis ticks to show the actual 'seconds_ago' values
    # We select a few points to label to keep the axis clean.
    tick_positions = df_plot.index[::max(1, len(df_plot) // 8)]
    # Ensure tick labels are formatted as 'Xs'
    tick_labels = [f"{s}s" for s in df_plot['seconds_ago'].iloc[tick_positions]]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=8)
    ax.set_xlabel('Time (Seconds Ago)', fontsize=10)

    # Clean up the plot
    plt.tight_layout()

    # 5. Display the Matplotlib figure using st.pyplot
    st.pyplot(fig, clear_figure=True, width="content")
    # Important: close the figure to free up memory
    plt.close(fig)


def get_device_metadata(mac_address: str) -> dict:
    """
    Retrieve the DHCP hostname and OUI vendor for a device from the database.

    Args:
        mac_address (str): The MAC address of the device.
    Returns:
        dict: A dictionary containing the device's metadata, or an empty dictionary if not found.
    """
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    sql = """
        SELECT metadata_json FROM devices
        WHERE mac_address = ?
    """
    with rwlock:
        row = db_conn.execute(sql, (mac_address,)).fetchone()
        if row:
            meta_data = json.loads(row['metadata_json'])
            logger.info(f"Parsed Metadata: {json.dumps(meta_data, indent=4)}")  # Check the parsed dictionary
            return meta_data
        else:
            return dict()


def get_remote_hostnames(mac_address: str) -> str:
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
    return datetime.datetime.fromtimestamp(timestamp).strftime("%b %d,%Y %I:%M:%S%p")


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


def config_get(key, default=None) -> typing.Any:
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


def config_set(key: str, value: typing.Any):
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
            json.dump(config_dict, f, indent=4, sort_keys=True)


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
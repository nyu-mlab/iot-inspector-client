from typing import Any
import pandas
import streamlit as st
import libinspector.global_state
import pandas as pd
import datetime
import common
import time


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

    show_device_details(device_mac_address)


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
    st.data_editor(df, use_container_width=True)


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
            device_mac_address = selected_device.split(" - ")[-1]
            st.query_params['device_mac_address'] = device_mac_address

    st.selectbox(
        "Select a device to view details:",
        device_options,
        index=selected_index,
        key='selected_device',
        on_change=_selected_device_changed_callback
    )

    return device_mac_address




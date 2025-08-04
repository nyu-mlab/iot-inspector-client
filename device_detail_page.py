from typing import Any

import streamlit as st
import libinspector.global_state
import pandas as pd
import datetime
import common


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

    activity_inference(device_mac_address)
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


@st.fragment(run_every=1)
def activity_inference(mac_address):
    """

    """
    return


@st.fragment(run_every=1)
def show_device_details(mac_address):
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
    """

    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    device_custom_name = common.get_device_custom_name(mac_address)
    device_dict = get_device_info(mac_address, db_conn, rwlock)

    if not device_dict:
        st.error(f"No device found with MAC address: {mac_address}")
        return

    st.markdown(f"### {device_custom_name}")
    st.caption(f"MAC Address: {mac_address} | IP Address: {device_dict['ip_address']}")

    sql = """
        SELECT
            timestamp,
            src_ip_address, src_hostname,
            dest_ip_address, dest_hostname,
            byte_count
        FROM network_flows
        WHERE src_mac_address = ? OR dest_mac_address = ?
        ORDER BY timestamp DESC
        LIMIT 100;
    """

    with rwlock:
        df = pd.read_sql_query(sql, db_conn, params=(mac_address, mac_address))

    if df.empty:
        st.warning("No network flows found for this device.")
        return

    # Convert the timestamp to a human-readable format
    # Convert Unix timestamp to datetime in UTC, then convert to local time
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.reset_index(drop=True)  # Reset the index for better display

    # Combine the src/dest IP and hostname into a single column for better readability
    df['src_info'] = df.apply(lambda row: f"{row['src_hostname']}" if row['src_hostname'] else row['src_ip_address'], axis=1)
    df['dest_info'] = df.apply(lambda row: f"{row['dest_hostname']}" if row['dest_hostname'] else row['dest_ip_address'], axis=1)
    # These are the columns in the Network Flow table
    df = df[['timestamp', 'src_info', 'dest_info', 'byte_count']]

    # I think this is to be used for labeling?
    df['inferred_activity'] = None

    # Prepare data for the bar chart (last 60 seconds)
    # Ensure 'timestamp' is in datetime format for comparison
    df_chart = df.copy()
    df_chart['timestamp_dt'] = pd.to_datetime(df_chart['timestamp']) # Re-convert to datetime if it was stringified for display

    # Get the most recent timestamp
    if not df_chart.empty:
        # Use the current time in the local timezone as the reference for "now"
        now_local = pd.Timestamp.now(tz=local_timezone)
        # Filter for the last 60 seconds from now_local
        time_60_seconds_ago = now_local - pd.Timedelta(seconds=60)
        # Ensure df_chart['timestamp_dt'] is also localized to the same timezone for comparison
        df_chart['timestamp_dt'] = df_chart['timestamp_dt'].dt.tz_localize(local_timezone, ambiguous='infer', nonexistent='shift_forward')
        df_last_60_seconds = df_chart[(df_chart['timestamp_dt'] >= time_60_seconds_ago) & (df_chart['timestamp_dt'] <= now_local)]

        if not df_last_60_seconds.empty:
            # Group by second and sum byte_count
            traffic_by_second = df_last_60_seconds.groupby(pd.Grouper(key='timestamp_dt', freq='s'))['byte_count'].sum().reset_index()
            traffic_by_second = traffic_by_second.rename(columns={'timestamp_dt': 'Time', 'byte_count': 'Bytes'})

            st.markdown("#### Traffic Volume (Last 60 Seconds)")
            st.bar_chart(traffic_by_second.set_index('Time')['Bytes'], use_container_width=True)
        else:
            st.caption("No traffic data in the last 60 seconds to display in chart.")
    else:
        st.caption("No traffic data to display in chart.")

    # Show the network flows in a table; I assume we can capture the changes to confirm/labels here?
    st.markdown("#### Network Flows")
    df['confirmation'] = False # Add a confirmation column with default False values
    edited_df = st.data_editor(df, use_container_width=True)


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




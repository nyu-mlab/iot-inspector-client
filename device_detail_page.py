import streamlit as st
import libinspector.global_state
import pandas as pd
import datetime



def show():

    device_mac_address = show_device_list()

    activity_inference(device_mac_address)
    show_device_details(device_mac_address)


def activity_inference(mac_address):



    return



@st.fragment(run_every=1)
def show_device_details(mac_address):

    st.markdown(f"### {mac_address}")

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
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
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
    df = df[['timestamp', 'src_info', 'dest_info', 'byte_count']]

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
            traffic_by_second = df_last_60_seconds.groupby(pd.Grouper(key='timestamp_dt', freq='S'))['byte_count'].sum().reset_index()
            traffic_by_second = traffic_by_second.rename(columns={'timestamp_dt': 'Time', 'byte_count': 'Bytes'})

            st.markdown("#### Traffic Volume (Last 60 Seconds)")
            st.bar_chart(traffic_by_second.set_index('Time')['Bytes'], use_container_width=True)
        else:
            st.caption("No traffic data in the last 60 seconds to display in chart.")
    else:
        st.caption("No traffic data to display in chart.")

    # Show the network flows in a table
    st.markdown("#### Network Flows")
    df['confirmation'] = False # Add confirmation column with default False values
    edited_df = st.data_editor(df, use_container_width=True)


def show_device_list():

    db_conn, rwlock = libinspector.global_state.db_conn_and_lock

    # Get the list of devices from the database
    sql = """
        SELECT * FROM devices
        WHERE is_inspected = 1 AND is_gateway = 0
    """
    device_list = []
    with rwlock:
        for device_dict in db_conn.execute(sql):
            device_list.append(dict(device_dict))

    if not device_list:
        st.warning("No devices found. Please inspect a device first.")
        st.stop()

    # Show a dropdown to select a device; each option shows both the device's MAC address and IP address
    device_options = [f"{device['mac_address']} ({device['ip_address']})" for device in device_list]
    device_options.insert(0, "(Select a device)")  # Add a placeholder option

    device_mac_address = st.query_params.get('device_mac_address', None)
    if device_mac_address:
        # If a device MAC address is already selected, find its index in the options
        selected_index = next((i for i, option in enumerate(device_options) if option.startswith(device_mac_address)), 0)

    selected_device = st.selectbox("Select a device to view details:", device_options, index=selected_index if device_mac_address else 0)

    if selected_device and selected_device != "(Select a device)":
        # Extract the MAC address from the selected option
        device_mac_address = selected_device.split(" ")[0]
        st.query_params['device_mac_address'] = device_mac_address
        return device_mac_address

    st.info("Please select a device to view its details.")
    st.stop()



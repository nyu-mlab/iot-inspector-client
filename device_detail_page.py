import streamlit as st
import libinspector.global_state
import pandas as pd
import datetime



def show():

    show_device_list()

    # Get the device MAC address from the query parameters
    try:
        device_mac_address = st.query_params['device_mac_address']
    except KeyError:
        pass
    else:
        show_device_details(device_mac_address)



def show_device_details(mac_address):

    st.markdown(f"### {mac_address}")

    sql = """
        SELECT
            timestamp,
            src_ip_address, src_hostname, src_mac_address,
            dest_ip_address, dest_hostname, dest_mac_address,
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
    # Show the network flows in a table
    st.markdown("#### Network Flows")
    st.dataframe(df, use_container_width=True)


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
        mac_address = selected_device.split(" ")[0]
        st.query_params['device_mac_address'] = mac_address
    else:
        st.info("Please select a device to view its details.")
        st.stop()



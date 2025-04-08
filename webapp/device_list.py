import streamlit as st
import functools
import time
import json
import libinspector.core
import libinspector.global_state

import common


def show():

    start_inspector_once()

    db_conn, rwlock = libinspector.global_state.db_conn_and_lock

    # Get the list of devices from the database
    sql = """
        SELECT * FROM devices
    """
    device_list = []
    with rwlock:
        for device_dict in db_conn.execute(sql):
            device_list.append(dict(device_dict))

    for device_dict in device_list:
        with st.container(border=True):
            show_device_card(device_dict)

    human_readable_time = common.get_human_readable_time()
    st.markdown(f'Updated: {human_readable_time}')

    time.sleep(2)
    st.rerun()


def show_device_card(device_dict):

    # Check if the user has previously inspected this device
    config_key = f'device_is_inspected_{device_dict["mac_address"]}'
    is_inspected = common.config_get(config_key, False)

    # Update the inspected status in the database if it is different
    if is_inspected != (device_dict['is_inspected'] == 1):
        db_conn, rwlock = libinspector.global_state.db_conn_and_lock
        with rwlock:
            sql = """
                UPDATE devices
                SET is_inspected = ?
                WHERE mac_address = ?
            """
            db_conn.execute(sql, (is_inspected, device_dict['mac_address']))

    # Extra information on the device's metadata, e.g., OUI
    metadata_dict = json.loads(device_dict['metadata_json'])

    left_col, right_col = st.columns([0.8, 0.2])

    with left_col:

        st.markdown(f'#### Unnamed Device')
        st.caption(f'IP Address: `{device_dict["ip_address"]}` -- MAC Address: `{device_dict["mac_address"]}` -- OUI: {metadata_dict["oui_vendor"]}')

    with right_col:
        if is_inspected:
            toggle_text = 'Being monitored'
        else:
            toggle_text = 'Not being monitored'
        st.toggle(
            label=toggle_text,
            value=is_inspected,
            key=f"device_inspected_toggle_{device_dict['mac_address']}",
            on_change=common.config_set,
            args=(config_key, not is_inspected),
        )


@functools.lru_cache(maxsize=1)
def start_inspector_once():
    """Initialize the Inspector core only once."""

    with st.spinner("Starting Inspector Core Library..."):
        libinspector.core.start_threads()
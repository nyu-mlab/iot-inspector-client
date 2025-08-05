import streamlit as st
import functools
import time
import json
import libinspector.global_state

import common


def show():

    toast_obj = st.toast('Discovering devices...')

    show_list(toast_obj)


@st.fragment(run_every=1)
def show_list(toast_obj):

    human_readable_time = common.get_human_readable_time()
    st.markdown(f'Updated: {human_readable_time}')

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
        st.warning('We are still scanning the network for devices. Please wait a moment. This page will refresh automatically.')

    for device_dict in device_list:
            st.markdown('---')
            show_device_card(device_dict)

    prev_device_count = st.session_state.get('prev_device_count', 0)
    if len(device_list) > prev_device_count:
        toast_obj.toast(f'Discovered {len(device_list) - prev_device_count} new device(s)!', icon=':material/add_circle:')
        st.session_state['prev_device_count'] = len(device_list)
        time.sleep(1.5)  # Give the user a moment to read the toast



def show_device_card(device_dict):

    # Check if the user has previously inspected this device
    device_inspected_config_key = f'device_is_inspected_{device_dict["mac_address"]}'
    is_inspected = common.config_get(device_inspected_config_key, False)

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

    # Get the device's custom name as set by the user
    device_custom_name = common.get_device_custom_name(device_dict['mac_address'])

    c1, c2 = st.columns([6, 4], gap='small')

    with c1:

        device_detail_url = f"/device_details?device_mac_address={device_dict['mac_address']}"
        title_text = f'**[{device_custom_name}]({device_detail_url})**'
        st.markdown(title_text)
        caption = f'{device_dict["ip_address"]} | {device_dict["mac_address"]}'
        if metadata_dict["oui_vendor"]:
            caption += f' | {metadata_dict["oui_vendor"]}'
        st.caption(caption, help='IP address, MAC address, and manufacturer OUI')

    with c2:

        # Maps short options to long options for display
        option_dict = {
            'inspected': ':material/troubleshoot: Inspected',
            'favorite': ':material/favorite: Favorite',
            'blocked': ':material/block: Blocked'
        }

        # Reverse the option_dict to map long options back to short options
        option_reversed_dict = {v: k for k, v in option_dict.items()}

        # Read the device's favorite and blocked status from the config
        device_is_favorite_config_key = f'device_is_favorite_{device_dict["mac_address"]}'
        device_is_favorite = common.config_get(device_is_favorite_config_key, False)

        device_is_blocked_config_key = f'device_is_blocked_{device_dict["mac_address"]}'
        device_is_blocked = common.config_get(device_is_blocked_config_key, False)

        # Create a list of default options based on the device's status
        default_option_list = []
        if is_inspected:
            default_option_list.append(option_dict['inspected'])
        if device_is_favorite:
            default_option_list.append(option_dict['favorite'])
        if device_is_blocked:
            default_option_list.append(option_dict['blocked'])

        def _device_options_changed_callback():

            # The long options selected by the user
            selected_list = st.session_state[f'device_options_{device_dict["mac_address"]}']

            # Transform the long options back to short options
            selected_list = [option_reversed_dict[option] for option in selected_list]

            # Reset the device's status based on the selected options
            common.config_set(device_is_favorite_config_key, 'favorite' in selected_list)
            common.config_set(device_is_blocked_config_key, 'blocked' in selected_list)
            common.config_set(device_inspected_config_key, 'inspected' in selected_list)

        # Create a list of options to display
        st.pills(
            'Options',
            options=option_dict.values(),
            selection_mode='multi',
            default=default_option_list,
            label_visibility='collapsed',
            key=f"device_options_{device_dict['mac_address']}",
            on_change=_device_options_changed_callback
        )


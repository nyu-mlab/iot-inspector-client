import os
import signal
import time
import streamlit as st
import core.model as model
import peewee
import core.deferred_action as deferred_action
import core.global_state as global_state
import core.config as config
import ui.common as common



def show():

    with st.sidebar:

        st.markdown('## 🔎 IoT Inspector')

        # Show a checkbox to show whether we are sharing data with NYU or not
        st.checkbox(
            'Get additional insights and donate data to NYU researchers',
            value=config.get('should_donate_data', default_config_value=False),
            help='If checked, you will be able to get advanced statistics about your devices, and Inspector will be donating your data with NYU researchers.',
            key='should_donate_data',
            on_change=set_donate_checkbox_callback
        )

        # Show a checkbox to show whether we are inspecting traffic or not
        with global_state.global_state_lock:
            st.session_state['should_inspect_traffic'] = global_state.is_inspecting

        st.checkbox(
            'Inspect Traffic',
            key='should_inspect_traffic',
            help='If unchecked, Inspector will temporarily suspends traffic inspection',
            on_change=set_inspect_traffic_checkbox_callback,
        )

        # If any of the rename boxes are visible, stop auto-freshing
        auto_refresh = True
        for (k, v) in st.session_state.items():
            if k.startswith('rename_box_visibility_') and v:
                auto_refresh = False
                break

        # Show a checkbox to enable auto-refreshing for at most five minutes
        auto_refresh = st.checkbox(
            'Auto Refresh',
            value=auto_refresh,
            help='If checked, Inspector will automatically refresh the page every 2 seconds for up to five minutes.',
            key='page_auto_refresh'
        )

        try:
            upload_Mbps, download_Mbps = deferred_action.execute(
                func=get_overall_bandwidth_consumption,
                ttl=5
            )
        except deferred_action.NoResultYet:
            upload_Mbps = 0
            download_Mbps = 0

        upload_Mbps = common.get_human_readable_byte_count(upload_Mbps * 1000000, bitrate=True)
        download_Mbps = common.get_human_readable_byte_count(download_Mbps * 1000000, bitrate=True)

        st.markdown('## 📊 Overall Statistics\n' +
                   f' * Inspected devices: {get_inspected_device_count()}\n' +
                   f' * Overall upload: {download_Mbps}\n' +
                   f' * Overall download: {upload_Mbps}')


        st.divider()

        qualtrics_id = config.get('qualtrics_id', '')
        if qualtrics_id:
            st.caption(f'Qualtrics UID: {qualtrics_id}')

        st.button(
            'Quit IoT Inspector',
            use_container_width=True,
            on_click=confirm_quit
        )


def set_donate_checkbox_callback():

    should_donate_data = st.session_state['should_donate_data']
    config.set('should_donate_data', should_donate_data)

    # Show the consent in the refresh
    if should_donate_data:
        config.set('has_consented_to_data_donation', 'not_set')
    else:
        config.set('donation_start_ts', 0)



@st.cache_data(ttl=2, show_spinner=False)
def get_inspected_device_count():
    """Count the number of inspected devices."""

    with model.db:
        return model.Device.select().where(model.Device.is_inspected == 1).count()



def get_overall_bandwidth_consumption(time_window=10):
    """Returns the overall bandwidth consumption in Mbps."""

    upload_Mbps = 0
    download_Mbps = 0

    with model.db:

        max_ts = int(time.time())

        upload_bytes = model.Flow.select(
            peewee.fn.Sum(model.Flow.byte_count)
            ).where(
                (model.Flow.src_device_mac_addr != '') &
                (model.Flow.dst_device_mac_addr == '') &
                (model.Flow.end_ts > max_ts - time_window)
            ).scalar()

        download_bytes = model.Flow.select(
            peewee.fn.Sum(model.Flow.byte_count)
            ).where(
                (model.Flow.dst_device_mac_addr != '') &
                (model.Flow.src_device_mac_addr == '') &
                (model.Flow.end_ts > max_ts - time_window)
            ).scalar()

    if upload_bytes:
        upload_Mbps = upload_bytes * 8.0 / 1000000.0 / time_window
    if download_bytes:
        download_Mbps = download_bytes * 8.0 / 1000000.0 / time_window

    return (upload_Mbps, download_Mbps)



def set_inspect_traffic_checkbox_callback():

    with global_state.global_state_lock:
        global_state.is_inspecting = st.session_state['should_inspect_traffic']



def confirm_quit():

    st.markdown('### Are you sure to quit IoT Inspector?')

    c1, c2 = st.columns(2)

    with c1:
        st.button('Yes', on_click=quit, use_container_width=True)

    with c2:
        st.button('No', use_container_width=True)

    st.stop()



def quit():
    """ Stop the Streamlit server"""

    st.markdown('## 🔎 IoT Inspector has terminated.')
    st.markdown('Feel free to close this window or relaunch IoT Inspector.')

    time.sleep(5)

    # Get the current process ID
    pid = os.getpid()

    # Kill the process
    os.kill(pid, signal.SIGTERM)

    st.stop()
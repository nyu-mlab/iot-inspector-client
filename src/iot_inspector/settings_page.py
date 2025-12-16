import streamlit as st
import os
import signal
import common
import libinspector
import libinspector.packet_collector as packet_collector


def exit_application_callback():
    """
    Kill the IoT Inspector application, background threads, and parent shell.
    """
    if packet_collector.inspector_is_running():
        st.warning("IoT Inspector closing... Please wait a moment.")
        with libinspector.global_state.global_state_lock:
            libinspector.global_state.is_running = False
    else:
        st.info("IoT Inspector was already not running.")
    libinspector.core.clean_up()
    os.kill(os.getpid(), signal.SIGTERM)


def show():
    """
    Display the settings for IoT Inspector
    """
    with st.container(border=True):
        st.toggle(
            "Enable debug mode for IoT Inspector, if you are a developer (Not Recommended for Prolific users)",
            key='enable_debug_mode',
            value=common.config_get('debug', False),
            help="Toggle ON if you are debugging IoT Inspector, otherwise leave it OFF. This is for NYU Researchers and Developers only.",
            on_change=lambda: common.config_set('debug', st.session_state['enable_debug_mode'])
        )

    st.button(
        "🛑 Exit Application",
        type="primary",
        on_click=exit_application_callback,
        help="Gracefully close the IoT Inspector application. This stops all background processes (threads, Streamlit, and PowerShell)"
    )
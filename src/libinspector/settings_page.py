import streamlit as st
import os
import signal
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
    st.markdown('Settings!')

    st.button(
        "🛑 Exit Application",
        type="primary",
        on_click=exit_application_callback,
        help="Gracefully close the IoT Inspector application. This stops all background processes (threads, Streamlit, and PowerShell)"
    )
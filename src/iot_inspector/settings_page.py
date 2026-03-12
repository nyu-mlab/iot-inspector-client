import streamlit as st
import os
import signal
import common
import libinspector


def exit_application_callback():
    """
    Kill the IoT Inspector application, background threads, and parent shell.
    """
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
        st.divider()
        st.toggle(
            "Enable Device Event Detection",
            key='enable_event_inference',
            value=common.config_get('event_inference', False),
            help="Toggle ON if you want IoT Inspector to run its event inference pipeline. This can be resource intensive, so we recommend leaving it OFF if you are not interested in seeing the 'Inferred Events' tab!",
            on_change=lambda: common.config_set(
                'event_inference',
                st.session_state.get('enable_event_inference', False)
            )
        )
        st.divider()

    st.button(
        "🛑 Exit Application",
        type="primary",
        on_click=exit_application_callback,
        help="Gracefully close the IoT Inspector application. This stops all background processes (threads, Streamlit, and PowerShell)"
    )
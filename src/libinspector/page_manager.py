"""
Constructs all the pages in a single module.

"""
import streamlit as st
import device_list_page
import device_detail_page
import settings_page
import overview_page
import functools
import common
import libinspector.core
import threading
import libinspector.global_state


def get_page(title, material_icon, show_page_func):
    icon = f":material/{material_icon}:"
    url_path = title.lower().replace(' ', '_')

    def _show_page_func_wrapper():
        # Add the participant ID to every URL
        try:
            pid = st.session_state['pid']
        except KeyError:
            pass
        else:
            st.query_params['pid'] = pid

        initialize_page()

        st.markdown(f"## {icon} {title}")

        show_page_func()

    return st.Page(
        _show_page_func_wrapper,
        title=title,
        icon=icon,
        url_path=url_path,
    )


def initialize_page():

    # Set the page properties
    st.set_page_config(
        page_title="IoT Inspector",
        page_icon=":material/online_prediction:",
        layout="wide",  # Set the page layout to wide
        initial_sidebar_state="auto",
        menu_items={}
    )

    # If true, block further execution
    if common.show_warning():
        st.stop()

    # Hide the default Streamlit menu and footer
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    start_inspector_once()


@functools.lru_cache(maxsize=1)
def start_inspector_once():
    """Initialize the Inspector core only once."""
    with st.spinner("Starting Inspector Core Library..."):
        # Just in case someone closes labeling window without finishing
        # Same with the general warning
        common.config_set("suppress_warning", False)
        common.config_set("labeling_in_progress", False)
        common.config_set("api_message", "")
        libinspector.core.start_threads()
        api_thread = threading.Thread(
            name="Device API Thread",
            target=device_list_page.worker_thread,
            daemon=True,
        )
        api_thread.start()
        label_thread = threading.Thread(
            name="Device Label Thread",
            target=device_detail_page.label_thread,
            daemon=True
        )
        label_thread.start()
        with libinspector.global_state.global_state_lock:
            libinspector.global_state.custom_packet_callback_func = device_detail_page.save_labeled_activity_packets


device_list_page_obj = get_page(
    title='Device List',
    material_icon='list_alt',
    show_page_func=device_list_page.show
)

device_detail_page_obj = get_page(
    title='Device Details',
    material_icon='monitoring',
    show_page_func=device_detail_page.show
)

overview_page_obj = get_page(
    title='Overall Statistics',
    material_icon='dashboard',
    show_page_func=overview_page.show
)

settings_page_obj = get_page(
    title='Settings',
    material_icon='settings',
    show_page_func=settings_page.show
)
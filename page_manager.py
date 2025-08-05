"""
Constructs all the pages in a single module.

"""
import streamlit as st
import device_list_page, device_detail_page, settings_page, overview_page
import functools
import libinspector.core



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
        libinspector.core.start_threads()



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
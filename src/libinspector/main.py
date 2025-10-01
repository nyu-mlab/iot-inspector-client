import logging
import streamlit as st
import os
import sys
import importlib

import webapp.sidebar as sidebar
import webapp.navbar as navbar

LOG_FILE = os.path.join('iot-inspector-client.log')
client_logger = logging.getLogger("client")
client_logger.setLevel(logging.DEBUG)

# Remove existing handlers for clean setup
client_logger.handlers.clear()

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
client_logger.addHandler(file_handler)

# Use client_logger for your own logging
client_logger.info("Client logger initialized.")


def main():

    initial_configuration()

    sidebar.show()
    navbar.show()

    current_page_name = st.query_params.get("current_page", "device_list")

    try:
        # Dynamically import the module
        module = importlib.import_module(f"webapp.{current_page_name}")
        # Call the `show` method of the imported module
        module.show()
    except ModuleNotFoundError:
        st.error(f"Page '{current_page_name}' not found.")
        st.stop()
    except AttributeError:
        st.error(f"Page '{current_page_name}' does not have a 'show' method.")
        st.stop()


def initial_configuration():
    """
    Initial configurations for the application.

    """
    # Make sure we are running as root
    if os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)

    # Set the page properties
    st.set_page_config(
        page_title="IoT Inspector",
        page_icon=":material/troubleshoot:",
        layout="wide",  # Set the page layout to wide
        initial_sidebar_state="expanded",
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


if __name__ == "__main__":
    main()

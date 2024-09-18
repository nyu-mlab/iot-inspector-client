import sys
sys.path.insert(0, '../')

import streamlit as st
import signal
import time


# Make sure that npcap is installed for windows
from core.common import get_os
import os
if get_os() == 'windows':
    npcap_path = os.path.join(os.environ['WINDIR'], 'System32', 'Npcap')
    if not os.path.isdir(npcap_path):
        # Show an error message
        print('\n' * 20)
        print('Please install Npcap from https://npcap.com/dist/npcap-1.76.exe before using IoT Inspector.')
        st.markdown('## Error starting IoT Inspector')
        st.error('Please install Npcap from https://npcap.com/dist/npcap-1.76.exe before using IoT Inspector.')
        st.markdown('Npcap is necessary for IoT Inspector to capture and analyze network traffic.')
        st.markdown('Once you install Npcap, please restart IoT Inspector.')

        my_bar = st.progress(1.0, text='IoT Inspector will close in 30 seconds')

        for t in range(30):
            time.sleep(1)
            time_left = 30 - t
            my_bar.progress(time_left / 30.0, text=f'IoT Inspector will automatically close in {time_left} seconds')

        # Get the current process ID
        pid = os.getpid()

        # Kill the process
        os.kill(pid, signal.SIGTERM)

        st.stop()


import core.start

core.start.start_threads()

import sidebar
import consent
import survey
import functools

import core.config as config



def show(page_title='', page_subtitle=''):

    st.set_page_config(
        page_title="IoT Inspector",
        page_icon="🔎",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "https://www.extremelycoolapp.com/bug",
            'About': "# This is a header. This is an *extremely* cool app!"
        }
    )

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    consent.show()
    survey.show()
    sidebar.show()

    if page_title:
        st.markdown('## ' + page_title)

    if page_subtitle:
        st.caption(page_subtitle)

    started_using_inspector()



@functools.lru_cache(maxsize=1)
def started_using_inspector():
    """
    Marked the beginning of using Inspector. Called exactly once. Used to determine whether to show the survey.

    """
    config.set('has_used_inspector', True)

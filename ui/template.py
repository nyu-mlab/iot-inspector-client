import sys
sys.path.insert(0, '../')

import streamlit as st
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

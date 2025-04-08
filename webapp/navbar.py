import streamlit as st
from collections import OrderedDict


def show():

    # Maps the current_page_name to the corresponding human readable name for the
    # navigation bar
    nav_dict = OrderedDict([
        ('device_list', 'Device List'),
        ('overview', 'Overall Network Activities'),
        ('device_details', 'Device Activities'),
        ('history', 'Historical Records'),
        ('settings', 'Settings'),
        ('about', 'About')
    ])

    current_page_name = st.pills(
        label='Navigation menu',
        label_visibility='hidden',
        options=nav_dict.keys(),
        format_func=lambda x: nav_dict[x],
        selection_mode='single',
        default=st.session_state.get("current_page", "device_list"),
        key='navbar',
        on_change=lambda:
            st.session_state.update({
                'current_page': st.session_state.navbar
            })
    )

    # Set the current page name in the session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = current_page_name

    st.markdown(f"## {nav_dict[st.session_state.current_page]}")  # Display the current page name

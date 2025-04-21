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
        default=st.query_params.get("current_page", "device_list"),
        key='navbar',
        on_change=lambda:
            st.query_params.update({
                'current_page': st.session_state['navbar']
            })
    )

    if st.query_params.get("current_page", None):
        st.query_params['current_page'] = current_page_name

    st.markdown(f"## {nav_dict[current_page_name]}")  # Display the current page title

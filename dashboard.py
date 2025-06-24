import streamlit as st
import page_manager
import common
import sidebar


nav_menu_list = [
    page_manager.device_list_page_obj,
    page_manager.overview_page_obj,
    page_manager.device_detail_page_obj,
    page_manager.settings_page_obj
]


st.logo('./static/images/inspector-logo.png', size='large')

pg = st.navigation(nav_menu_list)
pg.run()

with st.sidebar:
    sidebar.show()





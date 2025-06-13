import streamlit as st
import page_manager
import common


nav_menu_list = [
    page_manager.device_list_page_ref,
    page_manager.device_detail_page_ref,
    page_manager.settings_page_ref
]




st.logo('./static/images/inspector-logo.png', size='large')

pg = st.navigation(nav_menu_list)
pg.run()

import streamlit as st
import page_manager
import sidebar
import os


nav_menu_list = [
    page_manager.device_list_page_obj,
    page_manager.overview_page_obj,
    page_manager.device_detail_page_obj,
    page_manager.settings_page_obj
]

script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, 'static', 'images', 'inspector-logo.png')
st.logo(logo_path, size='large')

pg = st.navigation(nav_menu_list)
pg.run()

with st.sidebar:
    sidebar.show()

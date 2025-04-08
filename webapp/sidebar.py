import streamlit as st


def show():

    with st.sidebar:
        return show_sidebar()


def show_sidebar():

    st.markdown('## 🔎 IoT Inspector')

    st.markdown('General statistics about the IoT device')
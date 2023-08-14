import streamlit as st


def togggle_session_state_value(session_key, default_value=False):

    if session_key in st.session_state:
        st.session_state[session_key] = not st.session_state[session_key]
    else:
        st.session_state[session_key] = default_value

    return st.session_state[session_key]


def get_session_state_value(session_key, default_value=False):
    if session_key in st.session_state:
        return st.session_state[session_key]
    else:
        st.session_state[session_key] = default_value
        return default_value


def get_human_readable_byte_count(value, bitrate=True):

    if bitrate:
        if value < 1000:
            return f'{value:.1f} bps'
        if value < 1000000:
            return f'{value / 1000:.1f} Kbps'
        if value < 1000000000:
            return f'{value / 1000000:.1f} Mbps'
        return f'{value / 1000000000:.1f} Gbps'

    if value < 1000:
        return f'{value:.0f} B'
    if value < 1000000:
        return f'{value / 1000:.0f} KB'
    if value < 1000000000:
        return f'{value / 1000000:.0f} MB'
    return f'{value / 1000000000:.0f} GB'
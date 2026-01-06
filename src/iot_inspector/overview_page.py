import libinspector.global_state
import streamlit as st
import time


def show():
    """
    A Banner that shows this is the IoT Inspector overview page
    """
    st.write("This is the overview page.")
    show_high_level_stats()


@st.fragment(run_every=2)
def show_high_level_stats():
    """
    This page shows the following high level stats:
    - Number of inspected devices
    - Number of bytes transferred over the past 10 seconds
    """

    db_conn, rwlock = libinspector.global_state.db_conn_and_lock

    # Find the number of inspected devices
    sql = """
        SELECT COUNT(*) FROM devices
        WHERE is_inspected = 1
    """
    with rwlock:
        inspected_device_count = db_conn.execute(sql).fetchone()[0]

    # Calculate the number of bytes transferred over the past ten seconds
    sql = """
        SELECT SUM(byte_count) FROM network_flows
        WHERE timestamp >= ?
    """
    ts_ten_seconds_ago = int(time.time() - 10)
    with rwlock:
        bytes_transferred = db_conn.execute(sql, (ts_ten_seconds_ago,)).fetchone()[0] or 0

    c1, c2 = st.columns([1, 1], gap='small')
    with c1:
        st.metric(
            "Devices",
            inspected_device_count,
            border=True,
            help="Number of devices that are being inspected."
        )
    with c2:
        st.metric(
            "Data Use",
            f"{bytes_transferred:,} bytes", border=True)

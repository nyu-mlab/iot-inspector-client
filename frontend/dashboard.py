import sys
sys.path.insert(0, '../')

import streamlit as st
import pandas as pd
import core.start
import core.global_state
from core.oui_parser import get_vendor
import frontend.traffic_simulator
import plotly.express as px
import time
import math



SIMULATE_TRAFFIC = False


if SIMULATE_TRAFFIC:
    frontend.traffic_simulator.start_simulation()
else:
    core.start.start_threads()


# Get the byte counter: device_mac_addr -> {ts -> byte_count}
with core.global_state.global_state_lock:
    outgoing_byte_counter_dict = core.global_state.outgoing_byte_counter_dict.copy()


# Stick the byte counter into a dataframe; show the last minute
cut_off_ts = time.time() - 60

byte_counter_df = []
for (device_mac_addr, ts_dict) in outgoing_byte_counter_dict.items():
    for (ts, byte_count) in ts_dict.items():
        if ts < cut_off_ts or byte_count == 0:
            continue
        if SIMULATE_TRAFFIC:
            device_alias = device_mac_addr
        else:
            mac_suffix = device_mac_addr[-2:].upper()
            vendor = get_vendor(device_mac_addr)
            device_alias = f'{vendor} Device {mac_suffix}'
        byte_counter_df.append({'device_alias': device_alias, 'ts': ts, 'byte_count': byte_count * 8 / 1000000})
        if 'ordered_device_list' not in st.session_state:
            st.session_state['ordered_device_list'] = []
        if device_alias not in st.session_state['ordered_device_list']:
            st.session_state['ordered_device_list'].append(device_alias)

if len(byte_counter_df) == 0:
    st.write('No data to display')
    time.sleep(1)
    st.rerun()

byte_counter_df = pd.DataFrame(byte_counter_df)

# Pivot
byte_counter_df = pd.pivot_table(byte_counter_df, values='byte_count', index='ts', columns='device_alias', aggfunc='sum', fill_value=0).reset_index()

# Make sure that the time is every second
current_ts = int(time.time())
time_range = range(current_ts - 60, current_ts + 1)
time_range_df = pd.DataFrame(time_range, columns=['ts'])

byte_counter_df = time_range_df.merge(byte_counter_df, on='ts', how='left').fillna(0)

# Convert the index into proper datetime
byte_counter_df['ts'] = pd.to_datetime(byte_counter_df['ts'], unit='s')

st.markdown('# Upload Traffic in the Last Minute')

device_list = [
    device for device in st.session_state['ordered_device_list']
    if device in byte_counter_df.columns
]

for (ix, device) in enumerate(device_list):

    if device not in byte_counter_df.columns:
        continue

    is_last_device = (ix == len(device_list) - 1)

    st.markdown(f'**{device}**')

    device_df = byte_counter_df[['ts', device]]
    max_y = math.ceil(max(device_df[device].max(), 1))

    # Create the scatter plot with Plotly Express
    fig = px.bar(
        device_df,
        x='ts',
        y=device
    )

    fig.update_traces(marker=dict(color='blue'), hoverinfo='skip')

    # Customize the layout
    fig.update_layout(
        showlegend=False,  # Removes the legend
        hovermode=False,  # Disables hover mode entirely
        height=60 + (100 if is_last_device else 0),
        xaxis_title=None,
        yaxis_title='Mbps',
        yaxis_range=[0, max_y],
        yaxis=dict(tickvals=[0, max_y]),
        xaxis_showticklabels=is_last_device,
        yaxis_showticklabels=True,
        margin=dict(t=10, b=100 if is_last_device else 20)
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, config={'displayModeBar': False, 'staticPlot': True})

time.sleep(1)
st.rerun()
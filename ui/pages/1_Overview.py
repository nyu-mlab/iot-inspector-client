import time
import streamlit as st
import template
import core.model as model
import ui.common as common
import analysis.traffic_rate as traffic_rate
import plotly.express as px
import core.deferred_action as deferred_action
import core.global_state as global_state
import pandas as pd
import urllib.parse
import ui.donation_box as donation_box



# Generated from https://colordesigner.io/random-color-generator
COLORS = ['#bf2c1c', '#2e1591', '#ea09d0', '#56db39', '#ddd14b', '#cec10c', '#68f43d', '#c6ef0e', '#076361', '#30ba72', '#56eab6', '#f4904e', '#3947dd', '#db6c60', '#c605b3', '#da63ed', '#609b18', '#ff54b7', '#c6e52d', '#a3061b', '#f7252f', '#ef5689', '#b650d8', '#27ea3e', '#ac08dd', '#c510ce', '#c4d321', '#3474a8', '#15d86a', '#d862e5', '#430c9b', '#e863b3', '#5cd6a9', '#a032ef', '#dee064', '#487ec4', '#57d644', '#e54c00', '#137200', '#b44ce8']



@st.cache_data(ttl=2, show_spinner=False)
def get_device_list():
    """Returns a list of all device names, IP addresses, and MAC addresses."""

    device_list = []

    with model.db:

        query = model.Device.select() \
            .where(model.Device.is_inspected == 1) \
            .order_by(model.Device.favorite_time.desc(), model.Device.id)

        for device in query:

            product_name = device.product_name
            if not product_name:
                product_name = 'Unnamed Device'

            device_list.append('{} | {} | {}'.format(
                product_name,
                device.ip_addr,
                device.mac_addr
            ))

    return device_list


def get_color_for_type(type_name):

    # Hardcoded colors for some types
    if type_name == '(others)':
        return '#bdbdbd'
    if type_name.startswith('('):
        return '#636363'

    # Rotate colors
    if 'color_map' not in st.session_state:
        st.session_state['color_map'] = dict()

    color_map = st.session_state['color_map']
    color_ix = color_map.setdefault(type_name, len(color_map))
    return COLORS[color_ix % len(COLORS)]



def main():

    st.markdown('## Overview')
    st.caption('All your device activities at a glance.')

    st.divider()

    st.markdown('#### What are all the devices doing over time?')
    st.caption('Top device activities over the last 30 seconds')

    show_activity_graph(
        last_n_seconds=30,
    )

    st.divider()

    left_col, right_col = st.columns([0.7, 0.3])

    with left_col:
        st.markdown('#### Who are my devices talking to?')
        st.caption(f'All entities contacted by my devices over the last 30 seconds')

    with right_col:
        graph_type = st.radio(
            'Display information by',
            ['Domains', 'Advertising', 'Countries'],
            horizontal=True,
            key='graph_group_by_type'
            # label_visibility='hidden'
        )
        group_by_col = 'reg_domain'
        if graph_type == 'Domains':
            group_by_col = 'reg_domain'
        elif graph_type == 'Advertising':
            group_by_col = 'tracker_company'
        elif graph_type == 'Countries':
            group_by_col = 'country'

        show_empty = st.checkbox(
            'Show unknown values', value=False)

        st.checkbox('Sort by Upload', key='sort_by_upload', value=True)

    donation_box.show_on_device_activities()

    show_data_usage_table(
        last_n_seconds=30,
        group_by_col=group_by_col,
        show_empty=show_empty
    )

    with st.empty():
        st.info('You have reached the bottom of the list.')

    return



def show_pending_job_count(pending_job_count):

    st.info(f'Analyzing the data; {pending_job_count} task(s) remaining...', icon="⏳")



@st.cache_data(ttl=1, show_spinner=False)
def show_activity_graph(last_n_seconds=20):

    try:
        upload_df, download_df = deferred_action.execute(
            func=traffic_rate.get_all_device_rate,
            args=(last_n_seconds, ),
            ttl=2
        )
    except deferred_action.NoResultYet as pending_job_count:
        show_pending_job_count(pending_job_count)
        return

    options = [
        {
            'type_name': 'upload',
            'df': upload_df,
        },
        {
            'type_name': 'download',
            'df': download_df,
        }
    ]

    cols = st.columns(2)

    for option in options:

        column = cols.pop(0)

        chart_data_df = option['df']

        # No data overall
        if chart_data_df is None:
            with column:
                show_no_data(option['type_name'])
            continue

        # Each column should have a consistent color
        color_map = dict()
        for col in list(chart_data_df.columns)[0:-1]:
            color_map[col] = get_color_for_type(col)

        fig = px.bar(
            chart_data_df,
            x='Time',
            y=list(chart_data_df.columns)[0:-1],
            color_discrete_map=color_map
        )

        fig.update_layout(
            height=300,
            barmode='stack',
            xaxis=dict(title=None, showticklabels=False),
            yaxis=dict(title=f'{option["type_name"].capitalize()} (Mbps)', showticklabels=True),
            margin=dict(l=0, r=50, t=0, b=0),
            legend_title_text='Devices',
            legend=dict(
                orientation='h',  # Set the orientation to horizontal
                yanchor='bottom',  # Anchor the legend to the bottom
                y=1.02,  # Adjust the vertical position
                xanchor='right',  # Anchor the legend to the right
                x=1  # Adjust the horizontal position
            ),
        )
        with column:
            st.plotly_chart(fig, use_container_width=True)


@st.cache_data(ttl=2, show_spinner=False)
def get_all_device_data_usage(last_n_seconds=20, group_by_col='hostname', show_empty=False):

    # Gather data usage from all devices

    device_list = []
    with model.db:
        for device in model.Device.select():
            device_list.append(device)

    data_df_list = []

    for device in device_list:
        try:
            data_df = deferred_action.execute(
                func=traffic_rate.get_data_usage,
                args=(device.mac_addr, last_n_seconds, group_by_col, show_empty),
                ttl=5
            )
        except deferred_action.NoResultYet:
            continue
        if data_df is not None:
            data_df['mac_addr'] = device.mac_addr
            data_df_list.append(data_df)

    if len(data_df_list) == 0:
        return None

    data_df = pd.concat(data_df_list)

    # Group by entity
    return data_df.groupby('Entity').agg({
        'Data Uploaded (MB)': 'sum',
        'Data Downloaded (MB)': 'sum',
        'mac_addr': set
    }).rename(columns={'mac_addr': 'mac_addr_set'}).reset_index()



def show_data_usage_table(last_n_seconds=20, group_by_col='reg_domain', show_empty=False):

    data_df = get_all_device_data_usage(last_n_seconds, group_by_col, show_empty)
    if data_df is None:
        return show_no_data()

    row_widths = [0.2, 0.15, 0.15, 0.5]

    # Row header
    cols = st.columns(row_widths)


    with cols[1]:
        heading = '###### Uploaded'
        if st.session_state['sort_by_upload']:
            heading += ' ▿'
        st.markdown(heading)

    with cols[2]:
        heading = '###### Downloaded'
        if not st.session_state['sort_by_upload']:
            heading += ' ▿'
        st.markdown(heading)

    with cols[3]:
        st.markdown('###### Devices')

    upload_max = data_df['Data Uploaded (MB)'].max()
    download_max = data_df['Data Downloaded (MB)'].max()

    if st.session_state['sort_by_upload']:
        data_df = data_df.sort_values(by='Data Uploaded (MB)', ascending=False)
    else:
        data_df = data_df.sort_values(by='Data Downloaded (MB)', ascending=False)

    # Fetch a dict of known device product names
    device_product_name_dict = dict()
    with model.db:
        for device in model.Device.select():
            product_name = device.product_name
            if product_name:
                device_product_name_dict[device.mac_addr] = product_name

    # Actual table
    for (_, row) in data_df.iterrows():

        entity = f'{row["Entity"]}'
        if entity == '(unknown)' and not show_empty:
            continue

        cols = st.columns(row_widths)
        st.divider()

        with cols[0]:
            st.markdown(entity)

        with cols[1]:
            if upload_max > 0:
                upload_value = row['Data Uploaded (MB)']
                upload_percent = int(upload_value * 100.0 / upload_max)
                with st.empty():
                    upload_value = common.get_human_readable_byte_count(upload_value * 1000000, bitrate=False)
                    st.progress(upload_percent, text=upload_value)

        with cols[2]:
            if download_max > 0:
                download_value = row['Data Downloaded (MB)']
                download_percent = int(download_value * 100.0 / download_max)
                with st.empty():
                    download_value = common.get_human_readable_byte_count(download_value * 1000000, bitrate=False)
                    st.progress(download_percent, text=download_value)

        with cols[3]:
            named_device_list = []
            unnamed_device_list = []

            # Find the product name for each device
            for mac_addr in row['mac_addr_set']:
                try:
                    product_name = device_product_name_dict[mac_addr]
                except KeyError:
                    unnamed_device_list.append(mac_addr)
                else:
                    named_device_list.append((product_name, mac_addr))

            # Sort by product name
            named_device_list.sort(key=lambda x: x[0])

            # Output text that links to details of the device (named)
            named_device_text_list = []
            for (product_name, mac_addr) in named_device_list:
                params = urllib.parse.urlencode({'mac_addr': mac_addr})
                url = f'{global_state.BASE_PATH}/Device_Details?{params}'
                named_device_text_list.append(f'[{product_name}]({url})')

            with st.empty():
                if named_device_text_list:
                    st.markdown(', '.join(named_device_text_list))

            # Output text that links to details of the device (unnamed)
            unnamed_device_text_list = []
            for mac_addr in unnamed_device_list:
                params = urllib.parse.urlencode({'mac_addr': mac_addr})
                url = f'{global_state.BASE_PATH}/Device_Details?{params}'
                product_name = 'Device ' + mac_addr[-5:].replace(':', '')
                unnamed_device_text_list.append(f'[{product_name}]({url})')

            with st.empty():
                if unnamed_device_text_list:
                    st.markdown(', '.join(unnamed_device_text_list))



def show_no_data(type_name=''):

    if type_name == '':
        type_name = 'receiving/send'

    st.info(f'No data yet. Maybe the device is not actively {type_name}ing data?', icon="⏳")



template.show()

main()


# Auto-refresh
if 'page_auto_refresh' in st.session_state and st.session_state['page_auto_refresh']:
    time.sleep(4)
    st.rerun()



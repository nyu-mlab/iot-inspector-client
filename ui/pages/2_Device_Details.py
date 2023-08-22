import time
import streamlit as st
import template
import core.model as model
import analysis.traffic_rate as traffic_rate
import plotly.express as px
import core.deferred_action as deferred_action
import core.config as config
import ui.common as common
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
            .order_by(model.Device.favorite_time.desc(), model.Device.product_name.desc(), model.Device.id)

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


def save_device_name_callback(device_mac_addr):

    with model.write_lock:
        with model.db:
            # Update the product_name field of the device, given the mac_addr
            query = model.Device \
                .update(product_name=st.session_state[f'device_name_{device_mac_addr}']) \
                .where(model.Device.mac_addr == device_mac_addr)
            query.execute()


def show_device_details(mac_addr):

    with model.db:
        device = model.Device.get_or_none(model.Device.mac_addr == mac_addr)

    if not device:
        st.error('Device not found in database.')
        return

    product_name = device.product_name
    if not product_name:
        product_name = 'Unnamed Device'

    c1, c2 = st.columns([0.6, 0.4])
    c1.markdown(f'## {product_name}')

    # Show possible device identity if the data is available and the user has not set the product name yet
    if device.friendly_product and device.product_name == '':
        c1.caption(
            f'Possible identity: {device.friendly_product}',
            help='This is the product name that we inferred from the device\'s network traffic.'
        )

    c1.caption(f'IP address: {device.ip_addr} | MAC address: {device.mac_addr}')
    c2.text_input(
        'Rename this device',
        device.product_name,
        placeholder='company and product name',
        on_change=save_device_name_callback,
        args=(device.mac_addr, ),
        key=f'device_name_{device.mac_addr}'
    )

    st.divider()

    c1, c2 = st.columns([0.6, 0.4])
    with c1:
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
            'Show unknown values', value=True)

    with c2:

        time_range_labels = [
            'Last 30 seconds',
            'Last 1 minute',
            'Last 5 minutes',
            'Last 10 minutes',
            'Last 30 minutes',
            'Last 1 hour',
            'Last 3 hours',
            # 'Last 6 hours',
            # 'Last 12 hours',
            # 'Last 24 hours'
        ]

        time_range_values = [
            30,
            60,
            60 * 5,
            60 * 10,
            60 * 30,
            60 * 60,
            60 * 60 * 3,
            # 60 * 60 * 6,
            # 60 * 60 * 12,
            # 60 * 60 * 24
        ]

        time_range_str = st.select_slider(
            'Filter time range ',
            options=time_range_labels,
        )
        ix = time_range_labels.index(time_range_str)
        time_range = time_range_values[ix]

    st.divider()

    donation_box.show_on_device_activities()

    st.markdown('#### What is this device doing over time?')

    st.caption(f'Top entities contacted by this device over the {time_range_str.lower()}:')

    show_activity_graph(
        mac_addr,
        last_n_seconds=time_range,
        group_by_col=group_by_col,
        show_empty=show_empty
    )

    st.divider()

    st.markdown('#### Who is this device talking to?')

    st.caption(f'All entities contacted by this device over the {time_range_str.lower()}:')

    # If no entities are marked as suspicious, nudge the user
    config_key = f'device_details@{mac_addr}@{group_by_col}'
    thumbs_down_dict = config.get(config_key, {})
    if len(thumbs_down_dict) == 0:
        st.info(
            body='Help our research! If you think an entity is suspicious, please mark with "Want to Block". The NYU researchers will use this information to improve the anomaly detection system.',
            icon="💡"
        )

    show_data_usage_table(
        mac_addr,
        last_n_seconds=time_range,
        group_by_col=group_by_col,
        show_empty=show_empty
    )

    st.divider()

    return



def show_pending_job_count(pending_job_count):

    st.info(f'Analyzing the data; {pending_job_count} task(s) remaining...', icon="⏳")



@st.cache_data(ttl=1, show_spinner=False)
def show_activity_graph(mac_addr, last_n_seconds=20, group_by_col='reg_domain', show_empty=True):

    try:
        upload_df, download_df = deferred_action.execute(
            func=traffic_rate.get_activities,
            args=(mac_addr, last_n_seconds, group_by_col, show_empty),
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
            legend_title_text=st.session_state['graph_group_by_type'],
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


def show_data_usage_table(mac_addr, last_n_seconds=20, group_by_col='reg_domain', show_empty=True):

    try:
        data_df = deferred_action.execute(
            func=traffic_rate.get_data_usage,
            args=(mac_addr, last_n_seconds, group_by_col, show_empty),
            ttl=5
        )
    except deferred_action.NoResultYet as pending_job_count:
        show_pending_job_count(pending_job_count)
        return

    row_widths = [0.3, 0.25, 0.25, 0.2]

    # Row header
    cols = st.columns(row_widths)

    with cols[0]:
        st.checkbox('Sort by Upload', key='sort_by_upload', value=True)

    with cols[1]:
        heading = '##### Uploaded'
        if st.session_state['sort_by_upload']:
            heading += ' ▿'
        st.markdown(heading)

    with cols[2]:
        heading = '##### Downloaded'
        if not st.session_state['sort_by_upload']:
            heading += ' ▿'
        st.markdown(heading)

    with cols[3]:
        st.markdown('##### Want to block?')

    upload_max = data_df['Data Uploaded (MB)'].max()
    download_max = data_df['Data Downloaded (MB)'].max()

    if st.session_state['sort_by_upload']:
        data_df = data_df.sort_values(by='Data Uploaded (MB)', ascending=False)
    else:
        data_df = data_df.sort_values(by='Data Downloaded (MB)', ascending=False)

    # Load preferences for the thumbs up/down; maps entity to True if thumbs down
    config_key = f'device_details@{mac_addr}@{group_by_col}'
    thumbs_down_dict = config.get(config_key, {})

    # Actual table
    for (_, row) in data_df.iterrows():

        cols = st.columns(row_widths)

        with cols[0]:

            entity = f'{row["Entity"]}'
            try:
                if thumbs_down_dict[row['Entity']]:
                    entity += ' 🚩'
            except KeyError:
                pass
            st.markdown(entity)

        with cols[1]:
            if upload_max > 0:
                upload_value = row['Data Uploaded (MB)']
                upload_percent = int(upload_value * 100.0 / upload_max)
                upload_value = common.get_human_readable_byte_count(upload_value * 1000000, bitrate=False)
                st.progress(upload_percent, text=upload_value)

        with cols[2]:
            if download_max > 0:
                download_value = row['Data Downloaded (MB)']
                download_percent = int(download_value * 100.0 / download_max)
                download_value = common.get_human_readable_byte_count(download_value * 1000000, bitrate=False)
                st.progress(download_percent, text=download_value)

        with cols[3]:
            icon = '　'
            try:
                if thumbs_down_dict[row['Entity']]:
                    icon = '⛔️'
            except KeyError:
                pass
            if '(unknown)' in row['Entity']:
                continue
            st.button(
                icon,
                key='thumbs_down_' + row['Entity'],
                help='Click if you feel this entity should be blocked, because it is suspicious. Your information will be shared with the NYU researchers (if enabled).',
                on_click=thumbs_down_callback,
                args=(config_key, thumbs_down_dict, row['Entity']),
            )


def thumbs_down_callback(config_key, thumbs_down_dict, entity):

    if entity in thumbs_down_dict:
        thumbs_down_dict[entity] = not thumbs_down_dict[entity]
    else:
        thumbs_down_dict[entity] = True

    config.set(config_key, thumbs_down_dict)



def show_no_data(type_name=''):

    st.info(f'No data yet. Maybe the device is not actively {type_name}ing data?', icon="⏳")





template.show()

mac_addr = None
pre_selected_index = 0

default_option = '(Select a device below)'
device_list = [default_option] + get_device_list()

query_params = st.experimental_get_query_params()
if 'mac_addr' in query_params:
    mac_addr = query_params['mac_addr'][0]
    for (ix, device_description) in enumerate(device_list):
        if mac_addr in device_description:
            pre_selected_index = ix
            break

option = st.selectbox(
    'Select a device',
    device_list,
    label_visibility='hidden',
    index=pre_selected_index
)

if option != default_option:
    mac_addr = option.split('|')[-1].strip()

with st.empty():
    if mac_addr:
        with st.container():
            show_device_details(mac_addr)
    else:
        st.info('No device selected.')


# Auto-refresh
if 'page_auto_refresh' in st.session_state and st.session_state['page_auto_refresh']:
    time.sleep(4)
    st.experimental_rerun()



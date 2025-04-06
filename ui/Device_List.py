import time
import streamlit as st
import template
import ui.common as common
import core.model as model
import analysis.traffic_rate as traffic_rate
import core.global_state as global_state
import urllib.parse
import plotly.express as px
import plotly.io as pio
import core.deferred_action as deferred_action
import donation_box



template.show(
    'Device List',
    'A list of Internet-connected devices on your network.'
)


def show_no_data(type_name=''):

    st.info(f'No data yet. Maybe the device is not actively {type_name}ing data?', icon="⏳")



def show_pending_job_count(pending_job_count):

    st.info(f'Analyzing the data; {pending_job_count} task(s) remaining...', icon="⏳")



def get_chart(device_mac_addr):

    try:
        upload_df, download_df = deferred_action.execute(
            func=traffic_rate.get_traffic_rate_df,
            kwargs=dict(last_n_seconds=30),
            ttl=2
        )
    except deferred_action.NoResultYet as pending_job_count:
        show_pending_job_count(pending_job_count)
        return

    options = [
        {
            'type_name': 'upload',
            'df': upload_df,
            'color': '#fc8d59'
        },
        {
            'type_name': 'download',
            'df': download_df,
            'color': '#91bfdb'
        }
    ]

    columns = st.columns(2)

    for option in options:

        with columns.pop(0):
            with st.empty():

                try:
                    fig = deferred_action.execute(
                        func=make_chart,
                        args=(option, device_mac_addr),
                        ttl=2,
                        custom_function_key=f'device_list_make_chart_{device_mac_addr}_{option["type_name"]}'
                    )
                except deferred_action.NoResultYet as pending_job_count:
                    show_pending_job_count(pending_job_count)
                    continue
                if fig is None:
                    show_no_data(option['type_name'])
                    continue

                st.image(fig, use_column_width=True)



def make_chart(option, device_mac_addr):

    chart_data_df = option['df']

    # No data yet
    if chart_data_df is None:
        return None

    # No data for this device
    chart_data_df = chart_data_df[chart_data_df['device_mac_addr'] == device_mac_addr]
    if len(chart_data_df) == 0:
        return None

    max_bandwidth = chart_data_df['Bandwidth (Mbps)'].max() * 1000000
    max_bandwidth = common.get_human_readable_byte_count(max_bandwidth, bitrate=True)

    fig = px.bar(chart_data_df, x='Time', y='Bandwidth (Mbps)')
    fig.update_traces(marker_color=option['color'])
    fig.update_layout(
        height=100,
        xaxis=dict(title=None, showticklabels=False),
        yaxis=dict(title=None, showticklabels=False),
        margin=dict(l=0, r=0, t=0, b=0),
        annotations=[
                dict(
                    text=f'{max_bandwidth} {option["type_name"]}',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=1,
                    font=dict(size=15, color='rgba(0, 0, 0, 0.4)')
                )
            ]
    )

    return pio.to_image(fig, format='png', width=200, height=100)



def show_device(device: model.Device):

    # Do not show gateway
    if device.ip_addr == global_state.gateway_ip_addr:
        return

    product_name = device.product_name
    if not product_name:
        product_name = 'Unnamed Device ' + device.mac_addr[-5:].replace(':', '')

    if device.is_inspected:
        params = urllib.parse.urlencode({'mac_addr': device.mac_addr})
        st.markdown(f'#### [{product_name}]({global_state.BASE_PATH}/Device_Details?{params})')
    else:
        st.markdown(f'#### {product_name}')

    # Show possible device identity if the data is available and the user has not set the product name yet
    if device.friendly_product and device.product_name == '':
        st.caption(
            f'Possible identity: {device.friendly_product}',
            help='This is the product name that we inferred from the device\'s network traffic.'
        )

    # Show recently contacted domains
    recently_contacted_domains = get_recently_contacted_domains(device.mac_addr)
    st.caption(
        f'Recently contacted: {recently_contacted_domains}',
        help='The top domains that the device has recently contacted.'
    )

    c1, c2, c3 = st.columns([0.3, 0.4, 0.3])

    with c1:

        st.caption(f'{device.ip_addr} | {device.mac_addr}')

        c11, c12 = st.columns(2)
        rename_box = st.empty()

        c11.button(
            'Rename',
            key=f'rename_{device.mac_addr}',
            use_container_width=True,
            on_click=lambda x: toggle_rename_box_visibility_callback(x),
            args=(device.mac_addr,)
        )

        with c12:
            st.button(
                'Set icon',
                key=f'icon_{device.mac_addr}',
                use_container_width=True,
                disabled=True
            )

        if common.get_session_state_value(f'rename_box_visibility_{device.mac_addr}'):
            with rename_box.container():
                st.text_input(
                    'Device name',
                    device.product_name,
                    placeholder='company and product name',
                    on_change=save_device_name_callback,
                    args=(device.mac_addr, rename_box),
                    key=f'device_name_{device.mac_addr}'
                )
                # st.info('ℹ️ Auto-refresh is disabled.')

    with c2:
        get_chart(device.mac_addr)

    with c3:
        with global_state.global_state_lock:
            inspect_check_box_disabled = not global_state.is_inspecting
        st.checkbox(
            'Inspect',
            value=True if device.is_inspected == 1 else False,
            key=f'inspected_{device.mac_addr}',
            help='If checked, Inspector will capture and analyze network traffic from this device.',
            on_change=set_device_inspected_callback,
            args=(device.mac_addr,),
            disabled=inspect_check_box_disabled
        )
        st.checkbox(
            'Pin to top',
            value=True if device.favorite_time > 0 else False,
            key=f'favorite_{device.mac_addr}',
            help='If checked, Inspector will display the device first.',
            on_change=set_device_favorite_callback,
            args=(device.mac_addr,)
        )


@st.cache_data(ttl=5, show_spinner=False)
def get_recently_contacted_domains(mac_addr):

    try:
        data_df = deferred_action.execute(
            func=traffic_rate.get_data_usage,
            args=(mac_addr, 300, 'reg_domain', False),
            ttl=15
        )
    except deferred_action.NoResultYet:
        return '(unknown)'

    if data_df is None:
        return '(unknown)'

    top_upload_domains = data_df \
        .sort_values(by='Data Uploaded (MB)', ascending=False) \
        .head(2)['Entity']

    top_download_domains = data_df \
        .sort_values(by='Data Downloaded (MB)', ascending=False) \
        .head(2)['Entity']

    top_domains = set(top_upload_domains) | set(top_download_domains)

    # Remove parenthesized domains
    top_domains = [d for d in top_domains if not d.startswith('(')]
    top_domains.sort()

    # Remove duplicated domains like 'X.com' and 'X.com?'
    for d in list(top_domains):
        if '?' in d:
            d_without_question_mark = d.replace('?', '')
            if d_without_question_mark in top_domains:
                top_domains.remove(d)

    if top_domains:
        return ', '.join(top_domains)
    return '(unknown)'


def toggle_rename_box_visibility_callback(device_mac_addr):

    rename_box_name = f'rename_box_visibility_{device_mac_addr}'
    new_visibility = common.togggle_session_state_value(rename_box_name, True)

    # Make all other rename boxes invisible
    if new_visibility:
        for k in st.session_state:
            if k.startswith('rename_box_visibility_') and k != rename_box_name:
                st.session_state[k] = False


def save_device_name_callback(device_mac_addr, rename_box):

    rename_box.markdown('Saving to database...')

    with model.write_lock:
        with model.db:
            # Update the product_name field of the device, given the mac_addr
            query = model.Device \
                .update(product_name=st.session_state[f'device_name_{device_mac_addr}']) \
                .where(model.Device.mac_addr == device_mac_addr)
            query.execute()

    st.session_state[f'rename_box_visibility_{device_mac_addr}'] = False
    rename_box.empty()


def set_device_inspected_callback(device_mac_addr):

    if st.session_state[f'inspected_{device_mac_addr}']:
        is_inspected = 1
    else:
        is_inspected = 0

    with model.write_lock:
        with model.db:
            model.Device.update(is_inspected=is_inspected).where(model.Device.mac_addr == device_mac_addr).execute()


def set_device_favorite_callback(device_mac_addr):

    if st.session_state[f'favorite_{device_mac_addr}']:
        favorite_time = time.time()
    else:
        favorite_time = 0

    with model.write_lock:
        with model.db:
            model.Device.update(favorite_time=favorite_time).where(model.Device.mac_addr == device_mac_addr).execute()



donation_box.show_on_device_list(location='below')

with model.db:
    device_list = model.Device.select().order_by(model.Device.favorite_time.desc(), model.Device.product_name.desc(), model.Device.id)

prev_device = None

device_count = len(device_list)

for (ix, device) in enumerate(device_list):

    # Show a separator between favorite and non-favorite devices
    if prev_device is not None:
        if prev_device.favorite_time > 0 and device.favorite_time == 0:
            st.markdown('---')

    if device_count > 15 and ix == int(device_count / 2):
        donation_box.show_on_device_list(location='above and below')

    show_device(device)
    prev_device = device

donation_box.show_on_device_list(location='above')

auto_refresh = True

for (k, v) in st.session_state.items():
    if k.startswith('rename_box_visibility_') and v:
        auto_refresh = False
        break

if auto_refresh:
    # Auto-refresh
    if 'page_auto_refresh' in st.session_state and st.session_state['page_auto_refresh']:
        time.sleep(2)
        st.rerun()


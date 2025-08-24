import streamlit as st
import common



def show():

    with st.container(border=True):
        st.toggle(
            "Connect to the IoT Inspector Cloud for enhanced features (Recommended)",
            key='connect_to_nyu_inspector_cloud',
            value=common.config_get('connect_to_nyu_inspector_cloud', False),
            help="Toggle ON if you need help with identifying devices and detecting anonymous devices and activities, but provided that you are okay with IoT Inspector sharing anonymous data with New York University researchers.",
            on_change=lambda: common.config_set('connect_to_nyu_inspector_cloud', st.session_state['connect_to_nyu_inspector_cloud'])
    )

    show_favorite_device_list()




@st.fragment(run_every=2)
def show_favorite_device_list():

    favorite_device_list = []

    for (k, v) in common.config_get_prefix('device_is_favorite_').items():
        if v:
            mac_address = k.split('_')[-1]
            favorite_device_list.append(mac_address)

    if not favorite_device_list:
        return

    bullet_text = '#### Favorite Devices\n'

    for device_mac_address in favorite_device_list:
        device_custom_name = common.get_device_custom_name(device_mac_address)
        detail_url = f"/device_details?device_mac_address={device_mac_address}"
        bullet_text += f' - [{device_custom_name}]({detail_url})\n'

    st.markdown(bullet_text)


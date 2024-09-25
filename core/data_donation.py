"""
Donates data.

"""
import core.config as config
import core.model as model
import core.global_state as global_state
import core.networking as networking
import core.common as common
import core.anonymization as anonymization
import time



def start():

    # Check if data donation is enabled; if the donation start time is not set,
    # then data donation is not enabled.
    if config.get('donation_start_ts', default_config_value=0) == 0:
        return

    # Get the user_key from the server
    user_key = config.get('user_key', '')
    if not user_key:
        try:
            user_key = common.http_request(
                method='get',
                args=[global_state.USER_KEY_URL],
                field_to_extract='user_key'
            )
        except IOError:
            return
        else:
            config.set('user_key', user_key)

    try:
        donation_option = config.get('has_consented_to_data_donation')
    except KeyError:
        return

    if donation_option in ('donation_with_survey', 'donation_only'):
        donate_network_data(user_key)

    if donation_option == 'donation_with_survey':
        donate_survey_data(user_key)



def donate_network_data(user_key):

    # Determine the start and end times of data donation
    end_time = time.time()
    start_time = max(
        config.get('donation_start_ts', 0),
        config.get('last_donation_ts', 0)
    )

    # Slice the flows based on these times
    with model.db:
        q = model.Flow().select().where(
            (model.Flow.start_ts >= start_time) &
            (model.Flow.end_ts <= end_time)
        )

    # Maps MAC address to {remote_hostname_set, remote_ip_addr_set}
    pending_donation_dict = {}

    # Extract the relevant info
    for flow in q:
        for direction in ('src', 'dst'):

            local_prefix = direction
            remote_prefix = 'dst' if direction == 'src' else 'src'

            # Extract key information to donate
            local_device_mac_addr = getattr(flow, f'{local_prefix}_device_mac_addr')
            remote_ip_addr = getattr(flow, f'{remote_prefix}_ip_addr')
            remote_hostname = getattr(flow, f'{remote_prefix}_hostname')

            # Make sure that the mac address is in the ARP table
            try:
                global_state.arp_cache.get_ip_addr(local_device_mac_addr)
            except KeyError:
                continue

            # Temporarily store this info in memory
            info = pending_donation_dict.setdefault(local_device_mac_addr, {
                'remote_hostname_set': set(),
                'remote_ip_addr_set': set()
            })
            if remote_hostname:
                info['remote_hostname_set'].add(remote_hostname)
            if remote_ip_addr and not networking.is_private_ip_addr(remote_ip_addr):
                info['remote_ip_addr_set'].add(remote_ip_addr)

    # Maps MAC address to {entity_type: {entity_name_set}}, where every
    # entity_name in the set is suspicious
    suspicious_dict = {}

    # Get all the suspicious annotations
    for config_key, thumbs_down_dict in config.items():
        if not config_key.startswith('device_details@'):
            continue
        _, _mac_addr, entity_type = config_key.split('@')
        # Extract the suspicious entities
        for entity_name, is_suspicious in thumbs_down_dict.items():
            if is_suspicious:
                suspicious_dict \
                    .setdefault(_mac_addr, dict()) \
                    .setdefault(entity_type, []) \
                    .append(entity_name)

    # Upload and donate data
    for local_device_mac_addr, info in pending_donation_dict.items():

        remote_hostname_list = list(info['remote_hostname_set'])
        remote_ip_addr_list = list(info['remote_ip_addr_set'])

        # Anonymize the MAC address
        device_id = anonymization.get_device_id(local_device_mac_addr)

        # Extract the OUI
        mac_oui = local_device_mac_addr.replace(':', '').lower()[0:6]

        # Extract the user-defined device label
        user_device_label = ''
        with model.db:
            try:
                device = model.Device.get(model.Device.mac_addr == local_device_mac_addr)
            except model.Device.DoesNotExist:
                pass
            else:
                user_device_label = device.product_name

        # Prepare the data for upload
        data = {
            'device_id': device_id,
            'mac_oui': mac_oui,
            'user_device_label': user_device_label,
            'remote_hostname_list': remote_hostname_list,
            'remote_ip_addr_list': remote_ip_addr_list
        }

        # Include what entities are suspicious for this device
        try:
            data.update({
                'suspicious': suspicious_dict[local_device_mac_addr]
            })
        except KeyError:
            pass

        # Upload the data to `DATA_DONATION_URL` via HTTP POST
        try:
            common.http_request(
                method='post',
                args=[global_state.DATA_DONATION_URL + f'/{user_key}'],
                kwargs=dict(json=data, timeout=30)
            )

        except IOError:
            return

        config.set('last_donation_ts', end_time)

    common.log(f'[Data Donation] Donated data for {len(pending_donation_dict)} devices')



def donate_survey_data(user_key):

    # Get the qualtrics ID
    qualtrics_id = config.get('qualtrics_id', '')
    if not qualtrics_id:
        return

    # Exit if we have uploaded this ID already
    has_uploaded_qualtrics_id = config.get('has_uploaded_qualtrics_id', False)
    if has_uploaded_qualtrics_id:
        return

    # Upload the data to `DATA_DONATION_URL` via HTTP POST
    data = {
        'qualtrics_id': qualtrics_id
    }
    try:
        common.http_request(
            method='post',
            args=[global_state.DATA_DONATION_URL + f'/{user_key}'],
            kwargs=dict(json=data, timeout=30)
        )

    except IOError:
        return

    # Indicate that we have uploaded the qualtrics ID
    config.set('has_uploaded_qualtrics_id', True)
    common.log(f'[Data Donation] Donated survey data.')

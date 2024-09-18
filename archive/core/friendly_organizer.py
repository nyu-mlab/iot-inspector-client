"""
Add friendly names to entities.

"""
import core.model as model
import core.common as common
import core.global_state as global_state
import core.networking as networking
import core.config as config
import core.anonymization as anonymization
from core.oui_parser import get_vendor
from core.ttl_cache import ttl_cache
import os
import geoip2.database
import functools
import tldextract
import json


ip_country_parser = geoip2.database.Reader(
    os.path.join(
        common.get_python_code_directory(), '..', 'data', 'maxmind-country.mmdb'
    )
)

tracker_directory = os.path.join(
    common.get_python_code_directory(), '..', 'data'
)

# Source: https://github.com/duckduckgo/tracker-blocklists/tree/main
tracker_json_list = [
    os.path.join(tracker_directory, 'tds.json'),
    os.path.join(tracker_directory, 'apple-tds.json'),
    os.path.join(tracker_directory, 'android-tds.json')
]



def add_product_info_to_devices():

    updated_row_count = 0

    # Find all distinct MAC addresses for which the is_inspected field is 1
    with model.db:
        q = model.Device.select(model.Device.mac_addr) \
            .group_by(model.Device.mac_addr) \
            .where(model.Device.is_inspected == 1)
        mac_addr_list = [device.mac_addr for device in q]

    # For each MAC address, find the corresponding product name
    inferred_product_name_dict = dict()
    for mac_addr in mac_addr_list:
        friendly_names = []
        product_name = infer_product_name(mac_addr)
        oui_vendor = get_vendor(mac_addr)
        if product_name:
            friendly_names.append(product_name.split('/')[-1])
        if oui_vendor:
            friendly_names.append(oui_vendor)
        if not friendly_names:
            continue
        inferred_product_name_dict[mac_addr] = ' / '.join(friendly_names)

    # Update the database with the inferred product names into the `friendly_product` field
    with model.write_lock:
        with model.db:
            for mac_addr, product_name in inferred_product_name_dict.items():
                row_count = model.Device.update(
                    friendly_product=product_name
                ).where(model.Device.mac_addr == mac_addr
                ).execute()
                updated_row_count += row_count

    common.log(f'[Friendly Organizer] Updated {updated_row_count} rows of product info.')



def infer_product_name(device_mac_addr: str) -> str:

    # Ask NYU server, but first we make sure that we're donating data
    if config.get('donation_start_ts', 0) == 0:
        return ''

    # Also we make sure that the user_key has been set
    user_key = config.get('user_key', '')
    if not user_key:
        return ''

    # Anonymize the MAC address
    device_id = anonymization.get_device_id(device_mac_addr)

    # Send an HTTP GET request to the NYU server and ask
    url = global_state.DEVICE_INSIGHTS_URL + f'/{user_key}/{device_id}'
    try:
        return common.http_request(
            method='get',
            field_to_extract='product_name',
            args=[url],
            kwargs=dict(timeout=10)
        )
    except IOError:
        return ''



@ttl_cache(maxsize=8192, ttl=15)
def get_hostname_from_ip_addr(ip_addr: str, in_memory_only=False) -> str:
    """
    Returns the hostname associated with an IP address.

    Returns an empty string if the hostname is not found.

    """
    if networking.is_private_ip_addr(ip_addr):
        return '(local network)'

    # Ask the in-memory cache
    try:
        with global_state.global_state_lock:
            return global_state.hostname_dict[ip_addr]
    except KeyError:
        pass

    if in_memory_only:
        return ''

    # Ask the database
    try:
        with model.db:
            hostname = model.Hostname.get(model.Hostname.ip_addr == ip_addr).hostname
            if hostname:
                # Save the hostname value in memory
                with global_state.global_state_lock:
                    global_state.hostname_dict[ip_addr] = hostname
                return hostname
    except model.Hostname.DoesNotExist:
        pass

    # Ask NYU server, but first we make sure that we're donating data
    if config.get('donation_start_ts', 0) == 0:
        return ''

    # Also we make sure that the user_key has been set
    user_key = config.get('user_key', '')
    if not user_key:
        return ''

    # Send an HTTP GET request to the NYU server and ask
    url = global_state.IP_INSIGHTS_URL + f'/{user_key}/{ip_addr}'
    hostname = ''
    try:
        hostname = common.http_request(
            method='get',
            field_to_extract='hostname',
            args=[url],
            kwargs=dict(timeout=10)
        )
    except IOError:
        pass

    if not hostname:
        return ''

    # Remove trailing dots
    if hostname.endswith('.'):
        hostname = hostname[:-1]

    # Add question mark to denoate uncertainty only if the hostname is not parenthesized
    if '(' not in hostname and '?' not in hostname:
        hostname += '?'

    # Save the hostname value in memory
    with global_state.global_state_lock:
        global_state.hostname_dict[ip_addr] = hostname

    return hostname



def add_hostname_info_to_flows():
    """
    Adds hostname, reg_domain, and tracker_company to flows retroactively.

    """
    updated_row_count = 0

    for direction in ['src', 'dst']:

        ip_addr_col = getattr(model.Flow, f'{direction}_ip_addr')
        hostname_col = getattr(model.Flow, f'{direction}_hostname')
        mac_addr_col = getattr(model.Flow, f'{direction}_device_mac_addr')

        ip_addr_list = list()

        # Find all distinct IP addresses for which the hostname field is empty

        with model.db:
            q = model.Flow.select(ip_addr_col) \
                .group_by(ip_addr_col) \
                .where((ip_addr_col != '') & (hostname_col == '') & (mac_addr_col == ''))
            ip_addr_list = [getattr(flow, f'{direction}_ip_addr') for flow in q]

        # For each IP address, find the corresponding hostname and update the
        # reg_domain and tracker_company fields

        for ip_addr in ip_addr_list:
            # Find the hostname from various sources; could be a slow operation
            hostname = get_hostname_from_ip_addr(ip_addr)
            if not hostname:
                continue
            reg_domain = get_reg_domain(hostname)
            tracker_company = get_tracker_company(reg_domain)
            with model.write_lock:
                with model.db:
                    row_count = model.Flow.update(
                        **{
                            f'{direction}_hostname': hostname,
                            f'{direction}_reg_domain': reg_domain,
                            f'{direction}_tracker_company': tracker_company
                        }
                    ).where(
                        (ip_addr_col == ip_addr) &
                        (hostname_col == '') &
                        (mac_addr_col == '')
                    ).execute()
                    updated_row_count += row_count

    common.log(f'[Friendly Organizer] Updated {updated_row_count} rows of hostname info.')


@functools.lru_cache(maxsize=8192)
def get_country_from_ip_addr(remote_ip_addr):
    """Returns country for IP."""

    if networking.is_private_ip_addr(remote_ip_addr):
        return '(local network)'

    try:
        country = ip_country_parser.country(remote_ip_addr).country.name
        if country:
            return country
    except Exception:
        pass

    return ''


def parse_tracking_json(json_contents):

    block_list_dict = dict()

    for domain, info in json_contents['trackers'].items():
        tracker_company = info['owner']['displayName']
        if tracker_company:
            block_list_dict[domain] = tracker_company

    return block_list_dict



@functools.lru_cache(maxsize=1)
def initialize_ad_tracking_db():
    """
    Initializes the AdTracker table with the default list of trackers. Ran only once at startup.

    """

    # If the AdTracker table is empty, initialize it with the default list
    with model.db:

        if model.AdTracker.select().count() > 0:
            return

        block_list_dict = dict()

        # Load trackers from file; may be outdated -- TODO: Update these lists
        # in future versions
        for tracker_json_file in tracker_json_list:
            with open(tracker_json_file, 'r') as f:
                block_list_dict.update(parse_tracking_json(json.load(f)))

        # Add trackers to database
        for hostname, tracker_company in block_list_dict.items():
            model.AdTracker.create(
                hostname=hostname,
                tracker_company=tracker_company
            )


@functools.lru_cache(maxsize=8192)
def get_tracker_company(hostname: str) -> str:
    """
    Returns the tracker company for a given hostname; if not a tracking company, returns an empty string

    """
    initialize_ad_tracking_db()

    uncertain = '?' in hostname
    hostname = hostname.replace('?', '')

    try:
        company =  model.AdTracker.get(model.AdTracker.hostname == hostname).tracker_company
    except model.AdTracker.DoesNotExist:
        return ''
    else:
        if uncertain:
            company += '?'
        return company


@functools.lru_cache(maxsize=8192)
def get_reg_domain(full_domain):

    if not full_domain:
        return ''

    if full_domain == '(local network)':
        return full_domain

    reg_domain = tldextract.extract(full_domain.replace('?', '')) \
        .registered_domain

    if reg_domain:
        if '?' in full_domain:
            reg_domain += '?'
        return reg_domain

    return full_domain

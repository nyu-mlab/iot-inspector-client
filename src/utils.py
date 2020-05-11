"""
Misc functions.

"""
import server_config
import os
import requests
import scapy.all as sc
import time
import threading
import traceback
import datetime
import sys
import re
import json
import uuid
import hashlib
import netaddr
import netifaces
import ipaddress
import subprocess


IPv4_REGEX = re.compile(r'[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}')

sc.conf.verb = 0

# If non empty, then only devices with the following MAC addresses with be
# inspected. Do not populate this list in production. For internal testing.
TEST_OUI_LIST = [
    # 'd83134',  # Roku
    # '74f61c',  # Danny's Pixel phone
]


# Make sure Inspector's directory exits
home_dir = os.path.join(os.path.expanduser('~'), 'princeton-iot-inspector')
if not os.path.isdir(home_dir):
    os.mkdir(home_dir)


def is_ipv4_addr(value):

    return IPv4_REGEX.match(value)


def get_user_config():
    """Returns the user_config dict."""

    user_config_file = os.path.join(
        os.path.expanduser('~'),
        'princeton-iot-inspector',
        'iot_inspector_config.json'
    )

    try:
        with open(user_config_file) as fp:
            return json.load(fp)

    except Exception:
        pass

    while True:
        user_key = requests.get(server_config.NEW_USER_URL).text.strip()

        # Make sure we're not getting server's error messages
        if len(user_key) == 32:
            break

        time.sleep(1)

    user_key = user_key.replace('-', '')
    secret_salt = str(uuid.uuid4())

    with open(user_config_file, 'w') as fp:
        config_dict = {
            'user_key': user_key,
            'secret_salt': secret_salt
        }
        json.dump(config_dict, fp)

    return config_dict


class TimeoutError(Exception):
    pass


_lock = threading.Lock()


def log(*args):

    log_str = '[%s] ' % datetime.datetime.today()
    log_str += ' '.join([str(v) for v in args])

    log_file_path = os.path.join(
        os.path.expanduser('~'),
        'princeton-iot-inspector',
        'iot_inspector_logs.txt'
    )

    with open(log_file_path, 'a') as fp:
        fp.write(log_str + '\n')

def get_gateway_ip(timeout=10):
    """Returns the IP address of the gateway."""

    return get_default_route(timeout)[0]


def get_host_ip(timeout=10):
    """Returns the host's local IP (where IoT Inspector client runs)."""

    return get_default_route(timeout)[2]


def _get_routes():

    while True:

        sc.conf.route.resync()
        routes = sc.conf.route.routes
        if routes:
            return routes

        time.sleep(1)


def get_default_route():
    """Returns (gateway_ip, iface, host_ip)."""

    while True:

        routes = _get_routes()
        # Look for network = 0.0.0.0, netmask = 0.0.0.0
        for default_route in routes:
            if default_route[0] == 0 and default_route[1] == 0:
                return default_route[2:5]

        log('get_default_route: retrying')
        time.sleep(1)

def get_network_ip_range_windows():
    default_iface = get_default_route()
    iface_filter = default_iface[1]
    print(default_iface)
    ip_set = set()
    iface_ip = iface_filter.ip
    iface_guid = iface_filter.guid
    for k, v in netifaces.ifaddresses(iface_guid).items():
        if v[0]['addr'] == iface_ip:
            netmask = v[0]['netmask']
            break
  
    network = netaddr.IPAddress(iface_ip)
    cidr = netaddr.IPAddress(netmask).netmask_bits()
    subnet = netaddr.IPNetwork('{}/{}'.format(network, cidr))
  
    return ip_set


def get_network_ip_range():
    """
        Gets network IP range for the default interface specified
        by scapy.conf.iface
    """
    ip_set = set()
    default_route = get_default_route()

    iface_str = ''
    if sys.platform.startswith('win'):
        iface_info = sc.conf.iface
        iface_str = iface_info.guid
    else:
        iface_str = sc.conf.iface

    netmask = None
    for k, v in netifaces.ifaddresses(iface_str).items():
        if v[0]['addr'] == default_route[2]:
            netmask = v[0]['netmask']
            break

    # Netmask is None when user runs VPN.
    if netmask is None:
        return set()

    gateway_ip = netaddr.IPAddress(default_route[0])
    cidr = netaddr.IPAddress(netmask).netmask_bits()
    subnet = netaddr.IPNetwork('{}/{}'.format(gateway_ip, cidr))

    for ip in subnet:
        ip_set.add(str(ip))

    return ip_set


def get_my_mac():
    """Returns the MAC addr of the default route interface."""

    mac_set = get_my_mac_set(iface_filter=get_default_route()[1])
    return mac_set.pop()


def get_my_mac_set(iface_filter=None):
    """Returns a set of MAC addresses of the current host."""

    out_set = set()
    if sys.platform.startswith("win"):
        from scapy.arch.windows import NetworkInterface
        if type(iface_filter) == NetworkInterface:
            out_set.add(iface_filter.mac)

    for iface in sc.get_if_list():
        if iface_filter is not None and iface != iface_filter:
            continue
        try:
            mac = sc.get_if_hwaddr(iface)
        except Exception as e:
            continue
        else:
            out_set.add(mac)

    return out_set


class _SafeRunError(object):
    """Used privately to denote error state in safe_run()."""

    def __init__(self):
        pass


def restart_upon_crash(func, args=[], kwargs={}):
    """Restarts func upon unexpected exception and logs stack trace."""

    while True:

        result = safe_run(func, args, kwargs)

        if isinstance(result, _SafeRunError):
            time.sleep(1)
            continue

        return result


def safe_run(func, args=[], kwargs={}):
    """Returns _SafeRunError() upon failure and logs stack trace."""

    try:
        return func(*args, **kwargs)

    except Exception as e:

        err_msg = '=' * 80 + '\n'
        err_msg += 'Time: %s\n' % datetime.datetime.today()
        err_msg += 'Function: %s %s %s\n' % (func, args, kwargs)
        err_msg += 'Exception: %s\n' % e
        err_msg += str(traceback.format_exc()) + '\n\n\n'

        with _lock:
            sys.stderr.write(err_msg + '\n')
            log(err_msg)

        return _SafeRunError()


def get_device_id(device_mac, host_state):

    device_mac = str(device_mac).lower().replace(':', '')
    s = device_mac + str(host_state.secret_salt)

    return 's' + hashlib.sha256(s.encode('utf-8')).hexdigest()[0:10]

def smart_max(v1, v2):
    """
        Returns max value even if one value is None.

        Python cannot compare None and int, so build a wrapper
        around it.
    """
    if v1 is None:
        return v2

    if v2 is None:
        return v1

    return max(v1, v2)


def smart_min(v1, v2):
    """
    Returns min value even if one of the value is None.

    By default min(None, x) == None per Python default behavior.

    """

    if v1 is None:
        return v2

    if v2 is None:
        return v1

    return min(v1, v2)


def get_min_max_tuple(min_max_tuple, value):
    """
    Returns a new min_max_tuple with value considered.

    For example:

        min_max_tuple = (2, 3)
        print get_min_max_tuple(min_max_tuple, 4)

    We get back (2, 4).

    """
    min_v, max_v = min_max_tuple

    min_v = smart_min(min_v, value)
    max_v = smart_max(max_v, value)

    return (min_v, max_v)


def get_oui(mac):

    return mac.replace(':', '').lower()[0:6]


def get_os():
    """Returns 'mac', 'linux', or 'windows'. Raises RuntimeError otherwise."""

    os_platform = sys.platform

    if os_platform.startswith('darwin'):
        return 'mac'

    if os_platform.startswith('linux'):
        return 'linux'

    if os_platform.startswith('win'):
        return 'windows'

    raise RuntimeError('Unsupported operating system.')


def open_browser_on_windows(url):

    try:
        subprocess.call(['start', '', url], shell=True)    
    except Exception:
        pass
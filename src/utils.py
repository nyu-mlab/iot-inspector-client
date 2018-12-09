"""
Misc functions.

"""
import server_config
import os
import urllib2
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


IPv4_REGEX = re.compile(r'[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}')

sc.conf.verb = 0


def is_ipv4_addr(value):

    return IPv4_REGEX.match(value)


def get_user_config():
    """Returns the user_config dict."""

    user_config_file = os.path.join(
        os.path.expanduser('~'),
        'iot_insepctor_config.json'
    )

    try:
        with open(user_config_file) as fp:
            return json.load(fp)

    except Exception:
        pass

    try:
        user_key = urllib2.urlopen(server_config.NEW_USER_URL).read()
    except IOError:
        raise IOError('Unable to create new user.')

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
        'iot_insepctor_logs.txt'
    )

    with open(log_file_path, 'a') as fp:
        print >> fp, log_str


def get_gateway_ip(timeout=10):
    """Returns the IP address of the gateway."""

    return get_default_route(timeout)[0]


def get_host_ip(timeout=10):
    """Returns the host's local IP (where IoT Inspector client runs)."""

    return get_default_route(timeout)[2]


def get_default_route(timeout=10):
    """Returns (gateway_ip, iface, host_ip)."""

    start_time = time.time()

    while time.time() - start_time <= timeout:

        sc.conf.route.resync()

        # Look for network = 0.0.0.0, netmask = 0.0.0.0
        for default_route in sc.conf.route.routes:
            if default_route[0] == 0 and default_route[1] == 0:
                return default_route[2:5]

        log('get_default_route: retrying')
        time.sleep(1)

    raise TimeoutError('get_default_route timed out')


def get_my_mac():
    """Returns the MAC addr of the default route interface."""

    mac_set = get_my_mac_set(iface_filter=get_default_route()[1])
    return mac_set.pop()


def get_my_mac_set(iface_filter=None):
    """Returns a set of MAC addresses of the current host."""

    out_set = set()

    for iface in sc.get_if_list():
        if iface_filter is not None and iface != iface_filter:
            continue
        try:
            mac = sc.get_if_hwaddr(iface)
        except Exception:
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

    except Exception, e:

        err_msg = '=' * 80 + '\n'
        err_msg += 'Time: %s\n' % datetime.datetime.today()
        err_msg += 'Function: %s %s %s\n' % (func, args, kwargs)
        err_msg += 'Exception: %s\n' % e
        err_msg += str(traceback.format_exc()) + '\n\n\n'

        with _lock:
            print >> sys.stderr, err_msg
            log(err_msg)

        return _SafeRunError()


def get_device_id(device_mac, host_state):

    device_mac = str(device_mac).lower().replace(':', '')
    s = device_mac + str(host_state.secret_salt)

    return hashlib.sha256(s).hexdigest()[0:10]

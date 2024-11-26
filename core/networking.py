import ipaddress
import socket
import subprocess
import sys
import time
import core.common as common
import core.global_state as global_state
import core.model as model
import core.networking as networking
import scapy.all as sc
import netifaces
import netaddr
import threading



class ARPCache(object):
    """Stores a mapping between IP and MAC addresses"""

    def __init__(self):
        # Initialize the variables
        self._ip_mac_cache = {}
        self._mac_ip_cache = {}
        self._lock = threading.Lock()
        # Load previous ARP cache from the database
        with model.db:
            for device in model.Device.select():
                self._ip_mac_cache[device.ip_addr] = device.mac_addr
                self._mac_ip_cache[device.mac_addr] = device.ip_addr

    def update(self, ip_addr:str , mac_addr: str):
        """Updates the cache with the given IP and MAC addresses."""
        with self._lock:
            self._ip_mac_cache[ip_addr] = mac_addr
            self._mac_ip_cache[mac_addr] = ip_addr

    def get_mac_addr(self, ip_addr) -> str:
        """Returns the MAC address for the given IP address."""
        with self._lock:
            return self._ip_mac_cache[ip_addr]

    def get_ip_addr(self, mac_addr) -> str:
        """Returns the IP address for the given MAC address."""
        with self._lock:
            return self._mac_ip_cache[mac_addr]


def update_network_info():
    """Updates the network info in global_state."""

    t = get_default_route()
    with global_state.global_state_lock:
        global_state.gateway_ip_addr = t[0]
        global_state.host_active_interface = t[1]
        global_state.host_ip_addr = t[2]
        global_state.host_mac_addr = get_my_mac()
        global_state.arp_cache = networking.ARPCache()

    common.log(f'[Networking] Gateway IP address: {global_state.gateway_ip_addr}, Host Interface: {global_state.host_active_interface}, Host IP address: {global_state.host_ip_addr}, Host MAC address: {global_state.host_mac_addr}')



def get_default_route():
    """Returns (gateway_ip, iface, host_ip)."""
    # Discover the active/preferred network interface
    # by connecting to Google's public DNS server
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))
            iface_ip = s.getsockname()[0]
    except socket.error:
        sys.stderr.write('IoT Inspector cannot run without network connectivity.\n')
        sys.exit(1)

    while True:
        routes = _get_routes()
        default_route = None
        for route in routes:
            if route[4] == iface_ip and route[2] != '0.0.0.0':
                # Reassign scapy's default interface to the one we selected
                sc.conf.iface = route[3]
                default_route = route[2:5]
                break
        if default_route:
            break

        common.log('get_default_route: retrying')
        time.sleep(1)


    # If we are using windows, conf.route.routes table doesn't update.
    # We have to update routing table manually for packets
    # to pick the correct route.
    if sys.platform.startswith('win'):
        for i, route in enumerate(routes):
            # if we see our selected iface, update the metrics to 0
            if route[3] == default_route[1]:
                routes[i] = (*route[:-1], 0)

    return default_route


def _get_routes():

    while True:

        sc.conf.route.resync()
        routes = sc.conf.route.routes
        if routes:
            return routes

        time.sleep(1)


def get_my_mac():
    """Returns the MAC addr of the default route interface."""

    mac_set = get_my_mac_set(iface_filter=get_default_route()[1])
    my_mac_addr = mac_set.pop()
    return my_mac_addr


def get_my_mac_set(iface_filter=None):
    """Returns a set of MAC addresses of the current host."""

    out_set = set()

    for iface in sc.get_if_list():
        if iface_filter is not None and len(iface) > 1 and iface in iface_filter:
            try:
                mac = sc.get_if_hwaddr(iface_filter)
            except Exception as e:
                continue
            else:
                out_set.add(mac)

    return out_set


def get_network_ip_range():
    """
    Gets network IP range for the default interface.
    Returns a set of IP addresses.

    """
    ip_set = set()
    default_route = get_default_route()

    assert default_route[1] == sc.conf.iface, "incorrect sc.conf.iface"

    iface_str = ''
    if sys.platform.startswith('win'):
        iface_info = sc.conf.iface
        iface_str = iface_info.guid
    else:
        iface_str = sc.conf.iface

    netmask = None
    for k, v in netifaces.ifaddresses(str(iface_str)).items():
        if v[0]['addr'] == default_route[2]:
            netmask = v[0]['netmask']
            break

    if netmask is None:
        return set()

    gateway_ip = netaddr.IPAddress(default_route[0])
    cidr = netaddr.IPAddress(netmask).netmask_bits()
    subnet = netaddr.IPNetwork('{}/{}'.format(gateway_ip, cidr))

    for ip in subnet:
        ip_set.add(str(ip))

    return ip_set



def is_private_ip_addr(ip_addr):
    """Returns True if the given IP address is a private local IP address."""

    ip_addr = ipaddress.ip_address(ip_addr)
    return not ip_addr.is_global



def is_ipv4_addr(ip_string: str) -> bool:
    """Checks if ip_string is a valid IPv4 address."""

    try:
        socket.inet_aton(ip_string)
        return True
    except socket.error:
        return False


def enable_ip_forwarding():

    os_platform = common.get_os()

    if os_platform == 'mac':
        cmd = ['/usr/sbin/sysctl', '-w', 'net.inet.ip.forwarding=1']
    elif os_platform == 'linux':
        cmd = ['sysctl', '-w', 'net.ipv4.ip_forward=1']
    elif os_platform == 'windows':
        cmd = ['powershell', 'Set-NetIPInterface', '-Forwarding', 'Enabled']

    assert subprocess.call(cmd) == 0


def disable_ip_forwarding():

    os_platform = common.get_os()

    if os_platform == 'mac':
        cmd = ['/usr/sbin/sysctl', '-w', 'net.inet.ip.forwarding=0']
    elif os_platform == 'linux':
        cmd = ['sysctl', '-w', 'net.ipv4.ip_forward=0']
    elif os_platform == 'windows':
        cmd = ['powershell', 'Set-NetIPInterface', '-Forwarding', 'Disabled']

    assert subprocess.call(cmd) == 0

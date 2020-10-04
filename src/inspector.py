"""
Entry point for Inspector UI.

"""
import utils
from host_state import HostState
from packet_processor import PacketProcessor
from arp_scan import ArpScan
from syn_scan import SynScan
from packet_capture import PacketCapture
from arp_spoof import ArpSpoof
from data_upload import DataUploader
from netdisco_wrapper import NetdiscoWrapper
import subprocess
import sys
import logging
import server_config


WINDOWS_STARTUP_TEXT = """

======================================
Princeton IoT Inspector for Windows 10
======================================

We have also opened a new browser window for you to view the IoT Inspector report. If you don't see a new browser window, use the following private link:

{0}/user/{1}

To stop IoT Inspector, simply close this window or hit Control + C.

Questions? Email us at iot-inspector@lists.cs.princeton.edu.

"""


def start():
    """
    Initializes inspector by spawning a number of background threads.
    
    Returns the host state once all background threats are started.
    
    """
    # Read from home directory the user_key. If non-existent, get one from
    # cloud.
    config_dict = utils.get_user_config()

    utils.log('[MAIN] Starting.')

    # Set up environment
    state = HostState()
    state.user_key = config_dict['user_key'].replace('-', '')
    state.secret_salt = config_dict['secret_salt']
    state.host_mac = utils.get_my_mac()
    state.gateway_ip, _, state.host_ip = utils.get_default_route()

    assert utils.is_ipv4_addr(state.gateway_ip)
    assert utils.is_ipv4_addr(state.host_ip)

    state.packet_processor = PacketProcessor(state)

    utils.log('Initialized:', state.__dict__)

    # Continously discover devices
    arp_scan_thread = ArpScan(state)
    arp_scan_thread.start()

    # Continously discover ports via SYN scans
    syn_scan_thread = SynScan(state)
    syn_scan_thread.start()

    # Continuously gather SSDP data
    netdisco_thread = NetdiscoWrapper(state)
    netdisco_thread.start()

    # Continuously capture packets
    packet_capture_thread = PacketCapture(state)
    packet_capture_thread.start()

    # Continously spoof ARP
    if '--no_spoofing' not in sys.argv:
        arp_spoof_thread = ArpSpoof(state)
        arp_spoof_thread.start()

    # Continuously upload data
    data_upload_thread = DataUploader(state)
    data_upload_thread.start()

    # Suppress scapy warnings
    try:
        logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    except Exception:
        pass

    # Suppress flask messages
    try:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
    except Exception:
        pass

    # Insert a dash every four characters to make user-key easier to type
    pretty_user_key = ''
    for (ix, char) in enumerate(state.user_key):
        if (ix > 0) and (ix % 4 == 0):
            pretty_user_key += '-'
        pretty_user_key += char

    print('\n' * 100)

    os_platform = utils.get_os()    

    print(WINDOWS_STARTUP_TEXT.format(server_config.BASE_URL, pretty_user_key))

    # Open a browser window on Windows 10. Note that a new webpage will be
    # opened in a non-privileged mode. TODO: Not sure how to do the same
    # for macOS, as the "open" call on macOS will open a browser window
    # in privileged mode.
    if os_platform == 'windows':
        utils.open_browser_on_windows('{0}/user/{1}'.format(server_config.BASE_URL, pretty_user_key))
    elif os_platform == 'linux':
        utils.open_browser_on_linux('{0}/user/{1}'.format(server_config.BASE_URL, pretty_user_key))


    return state


def enable_ip_forwarding():

    os_platform = utils.get_os()

    if os_platform == 'mac':
        cmd = ['/usr/sbin/sysctl', '-w', 'net.inet.ip.forwarding=1']
    elif os_platform == 'linux':
        cmd = ['sysctl', '-w', 'net.ipv4.ip_forward=1']
    elif os_platform == 'windows':
        cmd = ['powershell', 'Set-NetIPInterface', '-Forwarding', 'Enabled']

    assert subprocess.call(cmd) == 0


def disable_ip_forwarding():

    os_platform = utils.get_os()

    if os_platform == 'mac':
        cmd = ['/usr/sbin/sysctl', '-w', 'net.inet.ip.forwarding=0']
    elif os_platform == 'linux':
        cmd = ['sysctl', '-w', 'net.ipv4.ip_forward=0']
    elif os_platform == 'windows':
        cmd = ['powershell', 'Set-NetIPInterface', '-Forwarding', 'Disabled']

    assert subprocess.call(cmd) == 0

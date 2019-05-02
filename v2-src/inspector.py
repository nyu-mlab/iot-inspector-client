"""
Entry point for Inspector UI.

"""
import utils
from host_state import HostState
from packet_processor import PacketProcessor
from arp_scan import ArpScan
from packet_capture import PacketCapture
from arp_spoof import ArpSpoof
from data_upload import DataUploader
from netdisco import NetdiscoWrapper
import subprocess
import sys
import logging


def start(webserver_context):

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

    webserver_context['host_state'] = state

    assert utils.is_ipv4_addr(state.gateway_ip)
    assert utils.is_ipv4_addr(state.host_ip)

    state.packet_processor = PacketProcessor(state)

    utils.log('Initialized:', state.__dict__)

    # Continously discover devices
    arp_scan_thread = ArpScan(state)
    arp_scan_thread.start()

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

    if state.persistent_mode:
        # Insert a dash every four characters to make user-key easier to type
        pretty_user_key = ''
        for (ix, char) in enumerate(state.user_key):
            if (ix > 0) and (ix % 4 == 0):
                pretty_user_key += '-'
            pretty_user_key += char

        path = 'persistent/' + pretty_user_key
        caution = 'This is your private link. Do not share.'
    else:
        path = ''
        caution = ''

    print '\n' * 100
    print """
        ===========================
          Princeton IoT Inspector
        ===========================

        View the IoT Inspector report at:

        https://inspector.cs.princeton.edu/{0}

        {1}

        Hit Control + C to terminate this process and stop data collection.

    """.format(path, caution)


def enable_ip_forwarding():

    os_platform = utils.get_os()

    if os_platform == 'mac':
        cmd = ['/usr/sbin/sysctl', '-w', 'net.inet.ip.forwarding=1']
    elif os_platform == 'linux':
        cmd = ['sysctl', '-w', 'net.ipv4.ip_forward=1']

    assert subprocess.call(cmd) == 0


def disable_ip_forwarding():

    os_platform = utils.get_os()

    if os_platform == 'mac':
        cmd = ['/usr/sbin/sysctl', '-w', 'net.inet.ip.forwarding=0']
    elif os_platform == 'linux':
        cmd = ['sysctl', '-w', 'net.ipv4.ip_forward=0']

    assert subprocess.call(cmd) == 0

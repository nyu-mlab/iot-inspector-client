"""
Entry point for Inspector UI.

"""
import os
import utils
from elevate import elevate
import webbrowser
import server_config
import ui
from host_state import HostState
from packet_processor import PacketProcessor
from arp_scan import ArpScan
from packet_capture import PacketCapture
from arp_spoof import ArpSpoof
from data_upload import DataUploader
import subprocess
import sys


LAUNCH_WEB_BROWSER_UPON_START = True


def main():

    # Read from home directory the user_key. If non-existent, get one from
    # cloud.
    config_dict = utils.get_user_config()

    # Where user would see report
    url = server_config.REPORT_URL.format(user_key=config_dict['user_key'])

    # Open a web browser only if non-root
    if not is_root() and LAUNCH_WEB_BROWSER_UPON_START:
        if 'no_browser' not in sys.argv:
            webbrowser.open_new_tab(url)

    # Run as root
    elevate()
    assert is_root()

    utils.log('[MAIN] Starting.')

    # Set up environment
    state = HostState()
    state.user_key = config_dict['user_key']
    state.secret_salt = config_dict['secret_salt']
    state.host_mac = utils.get_my_mac()
    state.gateway_ip, _, state.host_ip = utils.get_default_route()

    assert utils.is_ipv4_addr(state.gateway_ip)
    assert utils.is_ipv4_addr(state.host_ip)

    state.ip_prefix = '.'.join(state.gateway_ip.split('.')[0:3]) + '.'
    state.packet_processor = PacketProcessor(state)

    utils.log('Initialized:', state.__dict__)

    # Enable kernal forwarding.
    os_platform = sys.platform
    if os_platform.startswith('darwin'):
        cmd = ['/usr/sbin/sysctl', '-w', 'net.inet.ip.forwarding=1']
    elif os_platform.startswith('linux'):
        cmd = ['sysctl', '-w', 'net.ipv4.ip_forward=1']
    else:
        raise RuntimeError('Unsupported platform.')

    assert subprocess.call(cmd) == 0

    # Continously discover devices
    arp_scan_thread = ArpScan(state)
    arp_scan_thread.start()

    # Continuously capture packets
    packet_capture_thread = PacketCapture(state)
    packet_capture_thread.start()

    # Continously spoof ARP
    arp_spoof_thread = ArpSpoof(state)
    arp_spoof_thread.start()

    # Continuously upload data
    data_upload_thread = DataUploader(state)
    data_upload_thread.start()

    # UI
    try:
        ui.start_main_ui(url, state)
    except KeyboardInterrupt:
        pass

    # Disable kernal forwarding.
    if os_platform.startswith('darwin'):
        cmd = ['/usr/sbin/sysctl', '-w', 'net.inet.ip.forwarding=0']
    elif os_platform.startswith('linux'):
        cmd = ['sysctl', '-w', 'net.ipv4.ip_forward=0']
    assert subprocess.call(cmd) == 0

    utils.log('[MAIN] Done.')


def is_root():

    return os.getuid() == 0


if __name__ == '__main__':
    utils.safe_run(main)

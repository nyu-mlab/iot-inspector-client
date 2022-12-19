import ctypes
import os
import signal
import sys
import time

import inspector
import scapy.all as sc
import server_config
import utils

import rumps
import subprocess
import Foundation
from Foundation import NSSearchPathForDirectoriesInDomains


class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        app_support_path = NSSearchPathForDirectoriesInDomains(14, 1, 1).objectAtIndex_(0)
        subprocess.call(['mkdir', '-p', app_support_path])
        super(AwesomeStatusBarApp, self).__init__("Home Data Inspector", quit_button=None)
        self.menu = ["Open dashboard", "Stop inspection and quit"]
        self.host_state = initialize()

    @rumps.clicked("Open dashboard")
    def dashboard(self, _):
        print('Opening dashboard...')
        subprocess.Popen('open http://localhost:3000/', shell=True)

    @rumps.clicked("Stop inspection and quit")
    def quit(self, _):
        clean_up(self.host_state)
        rumps.quit_application()



def initialize():

    sc.load_layer("http")
    # The whole process should be run as root.
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin:
        sys.stderr.write('Please run as root.\n')
        sys.exit(1)

    # Check for Windows
    if utils.get_os() == 'windows':

        # Check Npcap installation
        npcap_path = os.path.join(
            os.environ['WINDIR'], 'System32', 'Npcap'
        )
        if not os.path.exists(npcap_path):
            sys.stderr.write("IoT Inspector cannot run without installing Npcap.\n")
            sys.stderr.write("For details, visit " + server_config.NPCAP_ERROR_URL)
            utils.open_browser(server_config.NPCAP_ERROR_URL)
            sys.exit(1)

    # Check presence of non-Ethernet network adapters, (e.g., VPN)
    if not utils.check_ethernet_network():
        sys.stderr.write('IoT Inspector cannot run on non-Ethernet network adapters, (e.g., VPN)\n')
        sys.stderr.write("For details, visit " + server_config.NETMASK_ERROR_URL)
        utils.open_browser(server_config.NETMASK_ERROR_URL)
        sys.exit(1)

    utils.log('[Main] Terminating existing processes.')
    if not kill_existing_inspector():
        utils.log('[Main] Unable to end existing process. Exiting.')
        return

    utils.log('[Main] Starting inspector.')
    inspector.enable_ip_forwarding()

    # We don't wrap the function below in safe_run because, well, if it crashes,
    # it crashes.
    host_state = inspector.start()
    return host_state


def wait_for_termination(host_state):

    # Waiting for termination
    while True:
        with host_state.lock:
            if host_state.quit:
                break
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            print('')
            break


def clean_up(host_state):

    utils.log('[Main] Restoring ARP...')

    with host_state.lock:
        host_state.spoof_arp = False

    for t in range(3):
        print('Cleaning up ({})...'.format(10 - t))
        time.sleep(1)

    inspector.disable_ip_forwarding()

    utils.log('[Main] Quit.')

    print('\n' * 100)
    print("""
        Princeton IoT Inspector has terminated.

        Feel free to close this window.

    """)

    # Remove PID file
    try:
        os.remove(get_pid_file())
    except Exception:
        pass


def get_pid_file():

    pid_file = os.path.join(
        os.path.expanduser('~'),
        'princeton-iot-inspector',
        'iot_inspector_pid.txt'
    )

    return pid_file


def kill_existing_inspector():

    pid_file = get_pid_file()

    try:
        with open(pid_file) as fp:
            pid = int(fp.read().strip())
    except Exception:
        pass
    else:
        # Kill existing process
        killed = False
        for _ in range(60):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                killed = True
                break
            else:
                time.sleep(1)
                utils.log('[Main] Waiting for existing process to end.')
        if not killed:
            return False

    with open(pid_file, 'w') as fp:
        fp.write(str(os.getpid()))

    return True


if __name__ == '__main__':
    AwesomeStatusBarApp().run()

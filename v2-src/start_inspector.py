import os
import inspector
import sys
import utils
import signal
import time
import ctypes
import scapy.all as sc

def main():
    sc.load_layer("http")
    # The whole process should be run as root.
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin:
        sys.stderr.write('Please run as root.\n')
        sys.exit(1)

    # Check for Npcap installation on Windows
    if utils.get_os() == 'windows':
        npcap_path = os.path.join(
            os.environ['WINDIR'], 'System32', 'Npcap'
        )
        if not os.path.exists(npcap_path):
            sys.stderr.write("IoT Inspector cannot run without installing Npcap.\n")
            sys.stderr.write("Please install Npcap here: https://nmap.org/dist/nmap-7.80-setup.exe\n")
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

    utils.log('[Main] Restoring ARP...')

    with host_state.lock:
        host_state.spoof_arp = False

    for t in range(10):
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
    main()

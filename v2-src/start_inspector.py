import os
import inspector
import sys
import utils
import signal
import webserver
import time
import scapy.all as sc


def main():
    sc.load_layer("http")
    # The whole process should be run as root.
    if os.getuid() != 0:
        sys.stderr.write('Please run as root.\n')
        sys.exit(1)

    utils.log('[Main] Terminating existing processes.')
    if not kill_existing_inspector():
        utils.log('[Main] Unable to end existing process. Exiting.')
        return

    utils.log('[Main] Starting webserver.')
    webserver.start_thread()

    utils.log('[Main] Starting inspector.')
    inspector.enable_ip_forwarding()
    utils.safe_run(inspector.start, args=(webserver.context,))

    while not webserver.context['quit']:
        host_state = webserver.context['host_state']
        if host_state:
            with host_state.lock:
                if host_state.quit:
                    break
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            print('')
            break

    utils.log('[Main] Restoring ARP...')

    host_state = webserver.context['host_state']
    if host_state:
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


def kill_existing_inspector():

    pid_file = os.path.join(
        os.path.expanduser('~'),
        'princeton-iot-inspector',
        'iot_inspector_pid.txt'
    )

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

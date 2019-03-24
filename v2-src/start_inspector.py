import os
from elevate import elevate
import inspector
import sys
import utils
import signal
import webserver
import time


def main():

    # The whole process should be run as root.
    elevate_process()
    assert os.getuid() == 0

    utils.log('[HTTP] Terminating existing processes.')
    if not kill_existing_inspector():
        utils.log('[HTTP] Unable to end existing process. Exiting.')
        return

    utils.log('[HTTP] Starting webserver.')
    webserver.start_thread()

    utils.log('[HTTP] Starting inspector.')
    inspector.enable_ip_forwarding()
    utils.safe_run(inspector.start, args=(webserver.context,))

    while not webserver.context['quit']:
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            break

    inspector.disable_ip_forwarding()

    utils.log('[HTTP] Quit.')


def kill_existing_inspector():

    pid_file = os.path.join(
        os.path.expanduser('~'),
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
                utils.log('[HTTP] Waiting for existing process to end.')
        if not killed:
            return False

    with open(pid_file, 'w') as fp:
        fp.write(str(os.getpid()))

    return True


def elevate_process():
    """TODO: Not tested on Windows."""

    os_platform = sys.platform
    if os_platform.startswith('linux'):
        elevate(graphical=False)
    else:
        elevate()


if __name__ == '__main__':
    main()

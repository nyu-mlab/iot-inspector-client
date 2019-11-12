"""
Periodically start netdisco and extract naming info about the network.

"""
import threading
import os
import stat
import utils
import requests
import subprocess
import json
import time
from netdisco.discovery import NetworkDiscovery

BASE_BINARY_PATH = 'https://github.com/noise-lab/netdisco-python-wrapper/raw/master/release/device_identifier_{os}'  # noqa


DOWNLOAD_CHUNK_SIZE = 1024 * 1024


class NetdiscoWrapper(object):

    def __init__(self, host_state):

        self._host_state = host_state
        self._os = utils.get_os()
        self._netdisco_path = self._get_netdisco_path()

    def start(self):

        th = threading.Thread(target=self._start_thread)
        th.daemon = True
        th.start()

    def _start_thread(self):

        while True:
            if len(self._host_state.get_ip_mac_dict_copy()) > 0:
                utils.safe_run(self._run_netdisco)
                time.sleep(10)
            else:
                time.sleep(1)
                continue

    def _get_netdisco_path(self):

        exe_name = 'iot-inspector-netdisco'

        return os.path.join(
            os.path.expanduser('~'),
            'princeton-iot-inspector',
            exe_name)

    def _run_netdisco(self):

        netdis = NetworkDiscovery()
        netdis.scan()

        for device_type in netdis.discover():
            device_info = netdis.get_info(device_type)[0]
            device_ip = device_info['host']
            device_info['device_type'] = device_type 
            
            # Find MAC based on IP
            try:
                with self._host_state.lock:
                    device_mac = self._host_state.ip_mac_dict[device_ip]
            except KeyError:
                continue 

            # Get device_id based on MAC
            device_id = utils.get_device_id(device_mac, self._host_state)

            # Submit for upload lter
            with self._host_state.lock:
                self._host_state.pending_netdisco_dict \
                    .setdefault(device_id, []).append(device_info)

def test():
    n = NetdiscoWrapper(None)
    n._download_netdisco_binary()


if __name__ == '__main__':
    test()

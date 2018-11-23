"""
Anonymizes and uploads DNS and flow data to cloud.

"""
import time
import threading
import utils
import urllib
import urllib2
import json
import server_config
import hashlib
from host_state import HostState


UPLOAD_INTERVAL = 5


class DataUploader(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)
        self._host_state = host_state

        self._lock = threading.Lock()
        self._active = True

        self._thread = threading.Thread(target=self._upload_thread)
        self._thread.daemon = True

    def _upload_thread(self):

        while True:

            time.sleep(UPLOAD_INTERVAL)

            with self._lock:
                if not self._active:
                    return

            utils.safe_run(self._upload_data)

    def _upload_data(self):

        # Remove all pending tasks
        with self._host_state.lock:

            dns_responses = self._host_state.pending_dns_responses
            pkts = self._host_state.pending_pkts

            self._host_state.pending_dns_responses = []
            self._host_state.pending_pkts = []

        # Aggregate all DNS responses. Build a mapping of domain -> ip_list.
        dns_dict = {}
        for record in dns_responses:
            ip_set = dns_dict.setdefault(record['domain'], set())
            dns_dict[record['domain']] = ip_set | record['ip_set']
        for domain in dns_dict:
            dns_dict[domain] = list(dns_dict[domain])

        # Aggregate all pkts into flows.  Maps (device_id, device_oui,
        # device_ip) ->  (remote_ip, remote_port, direction, protocol) ->
        # length.
        flow_dict = {}
        byte_count = 0
        for pkt in pkts:

            device_mac = pkt['device_mac']
            device_oui = device_mac.replace(':', '').lower()[0:6]
            device_id = self._get_device_id(device_mac)
            device_key = (device_id, device_oui, pkt['device_ip'])

            device_flow_dict = flow_dict.setdefault(device_key, {})

            flow_key = (
                pkt['remote_ip'], pkt['remote_port'],
                pkt['direction'], pkt['protocol']
            )
            device_flow_dict.setdefault(flow_key, 0)
            device_flow_dict[flow_key] += pkt['length']

            byte_count += pkt['length']

        utils.log('[UPLOAD] DNS:', dns_dict)
        utils.log('[UPLOAD] Flows:', flow_dict)

        # Report stats to UI
        with self._host_state.lock:
            self._host_state.status_text.set(
                'Currently capturing ' +
                '{:,}'.format(int(byte_count / 1000.0 / UPLOAD_INTERVAL)) +
                ' KB/s of traffic\nacross ' +
                '{}'.format(len(flow_dict)) +
                ' active devices on your local network.\n'
            )

    def start(self):

        with self._lock:
            self._active = True

        self._thread.start()

        utils.log('[Data] Start uploading data.')

    def stop(self):

        utils.log('[Data] Stopping.')

        with self._lock:
            self._active = False

        self._thread.join()

        utils.log('[Data] Stopped.')

    def _get_device_id(self, device_mac):

        s = str(device_mac) + str(self._host_state.secret_salt)

        return hashlib.sha256(s).hexdigest()[0:10]

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

        self._last_upload_ts = time.time()

    def _upload_thread(self):

        while True:

            time.sleep(UPLOAD_INTERVAL)

            with self._lock:
                if not self._active:
                    return

            utils.safe_run(self._upload_data)

    def _prepare_upload_data(self):

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
            device_key = json.dumps((device_id, device_oui, pkt['device_ip']))

            device_flow_dict = flow_dict.setdefault(device_key, {})

            flow_key = json.dumps((
                pkt['remote_ip'], pkt['remote_port'],
                pkt['direction'], pkt['protocol']
            ))
            device_flow_dict.setdefault(flow_key, 0)
            device_flow_dict[flow_key] += pkt['length']

            byte_count += pkt['length']

        return (dns_dict, flow_dict, byte_count)

    def _upload_data(self):

        (dns_dict, flow_dict, byte_count) = self._prepare_upload_data()

        # Prepare POST
        user_key = self._host_state.user_key
        url = server_config.SUBMIT_URL.format(user_key=user_key)
        post_data = urllib.urlencode({
            'dns': json.dumps(dns_dict),
            'flows': json.dumps(flow_dict)
        })

        # Try uploading across 5 attempts
        for attempt in range(5):

            status_text = 'Uploading data to cloud...\n'
            if attempt > 0:
                status_text += ' (Attempt {} of 5)'.format(attempt + 1)
                self._update_ui_status(status_text)

            utils.log('[UPLOAD]', status_text)

            response = urllib2.urlopen(url, post_data).read()
            utils.log('[UPLOAD] Gets back server response:', response)
            if response.strip() == 'SUCCESS':
                break
            time.sleep((attempt + 1) ** 2)

        # Report stats to UI
        current_ts = time.time()
        delta_sec = current_ts - self._last_upload_ts
        self._last_upload_ts = current_ts

        self._update_ui_status(
            'Currently capturing ' +
            '{:,}'.format(int(byte_count / 1000.0 / delta_sec)) +
            ' KB/s of traffic\nacross ' +
            '{}'.format(len(flow_dict)) +
            ' active devices on your local network.\n'
        )

        utils.log('[UPLOAD] DNS:', ' '.join(dns_dict.keys()))

    def _update_ui_status(self, value):

        with self._host_state.lock:
            self._host_state.status_text.set(value)

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

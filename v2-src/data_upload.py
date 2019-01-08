"""
Anonymizes and uploads DNS and flow data to cloud.

"""
import time
import datetime
import threading
import utils
import requests
import json
import server_config
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

        # Loop until initialized
        while True:
            if utils.safe_run(self._upload_initialization):
                break
            self._update_ui_status(
                'Please sign the consent form in the browser window.'
            )
            time.sleep(2)

        with self._host_state.lock:
            self._host_state.has_consent = True

        self._update_ui_status(
            'Continuously analyzing your network.\n'
        )

        # Continuously upload data
        while True:

            with self._host_state.lock:
                if not self._host_state.is_inspecting_traiffc:
                    time.sleep(2)
                    continue

            time.sleep(UPLOAD_INTERVAL)

            with self._lock:
                if not self._active:
                    return

            utils.safe_run(self._upload_data)

    def _upload_initialization(self):

        if not self._check_consent_form():
            return False

        return self._update_utc_offset()

    def _update_utc_offset(self):

        ts = time.time()

        utc_offset = int(
            (datetime.datetime.fromtimestamp(ts) -
                datetime.datetime.utcfromtimestamp(ts)).total_seconds()
        )

        utc_offset_url = server_config.UTC_OFFSET_URL.format(
            user_key=self._host_state.user_key,
            offset_seconds=utc_offset
        )

        utils.log('[DATA] Update UTC offset:', utc_offset_url)
        status = requests.get(utc_offset_url).text.strip()
        utils.log('[DATA] Update UTC offset status:', status)

        return 'SUCCESS' == status

    def _check_consent_form(self):

        check_consent_url = server_config.CHECK_CONSENT_URL.format(
            user_key=self._host_state.user_key
        )

        utils.log('[DATA] Check consent:', check_consent_url)
        status = requests.get(check_consent_url).text.strip()
        utils.log('[DATA] Check consent status:', status)

        return 'True' == status

    def _prepare_upload_data(self):

        # Remove all pending tasks
        with self._host_state.lock:

            dns_responses = self._host_state.pending_dns_responses
            dns_requests = self._host_state.pending_dns_requests
            pkts = self._host_state.pending_pkts
            ua_list = list(self._host_state.ua_set)

            self._host_state.pending_dns_responses = []
            self._host_state.pending_dns_requests = []
            self._host_state.pending_pkts = []
            self._host_state.ua_set = set()

        # Aggregate all DNS responses. Build a mapping of domain -> ip_list.
        dns_dict = {}
        for record in dns_responses:
            ip_set = dns_dict.setdefault(record['domain'], set())
            dns_dict[record['domain']] = ip_set | record['ip_set']
        for domain in dns_dict:
            dns_dict[domain] = list(dns_dict[domain])

        # DNS requests without responses (in case ARP spoofing fails)
        for domain in set(dns_requests):
            if domain not in dns_dict:
                dns_dict[domain] = ['']

        # Aggregate all pkts into flows.  Maps (device_id, device_oui,
        # device_ip) ->  (remote_ip, remote_port, direction, protocol) ->
        # length.
        flow_dict = {}
        byte_count = 0
        for pkt in pkts:

            device_mac = pkt['device_mac']
            device_oui = device_mac.replace(':', '').lower()[0:6]
            device_id = utils.get_device_id(device_mac, self._host_state)
            if device_id not in self._host_state.device_whitelist:
                continue

            device_key = json.dumps((device_id, device_oui, pkt['device_ip']))
            device_flow_dict = flow_dict.setdefault(device_key, {})

            flow_key = json.dumps((
                pkt['remote_ip'], pkt['remote_port'],
                pkt['direction'], pkt['protocol']
            ))
            device_flow_dict.setdefault(flow_key, 0)
            device_flow_dict[flow_key] += pkt['length']

            byte_count += pkt['length']

        # Collect arp_cache
        ip_mac_dict = self._host_state.get_ip_mac_dict_copy()
        arp_cache = []
        for (ip, mac) in ip_mac_dict.iteritems():
            arp_cache.append({
                'device_ip': ip,
                'device_id': utils.get_device_id(mac, self._host_state),
                'device_oui': mac.replace(':', '').lower()[0:6]
            })

        # Turn device_mac into device_id in ua_list
        ua_list = [
            (utils.get_device_id(mac, self._host_state), ua)
            for (mac, ua) in ua_list
        ]

        return (dns_dict, flow_dict, byte_count, arp_cache, ua_list)

    def _upload_data(self):

        (dns_dict, flow_dict, byte_count, arp_cache, ua_list) = \
            self._prepare_upload_data()

        delta_sec = time.time() - self._last_upload_ts

        # Prepare POST
        user_key = self._host_state.user_key
        url = server_config.SUBMIT_URL.format(user_key=user_key)
        post_data = {
            'dns': json.dumps(dns_dict),
            'flows': json.dumps(flow_dict),
            'arp_cache': json.dumps(arp_cache),
            'ua_list': json.dumps(ua_list),
            'client_version': self._host_state.client_version,
            'duration': str(delta_sec)
        }

        # Try uploading across 5 attempts
        for attempt in range(5):

            status_text = 'Uploading data to cloud...\n'
            if attempt > 0:
                status_text += ' (Attempt {} of 5)'.format(attempt + 1)
                self._update_ui_status(status_text)

            utils.log('[UPLOAD]', status_text)

            response = requests.post(url, data=post_data).text
            utils.log('[UPLOAD] Gets back server response:', response)

            # Update whitelist
            try:
                response_dict = json.loads(response)
                if response_dict['status'] == 'SUCCESS':
                    self._last_upload_ts = time.time()
                    with self._host_state.lock:
                        self._host_state.device_whitelist = \
                            response_dict['whitelist']
                    break
            except Exception:
                pass
            time.sleep((attempt + 1) ** 2)

        # Report stats to UI
        self._update_ui_status(
            'Currently analyzing ' +
            '{:,}'.format(int(byte_count / 1000.0 / delta_sec)) +
            ' KB/s of traffic\nacross ' +
            '{}'.format(len(flow_dict)) +
            ' active devices on your local network.\n'
        )

        utils.log('[UPLOAD] DNS:', ' '.join(dns_dict.keys()))

        utils.log(
            '[UPLOAD] Total packets in past epoch:',
            self._host_state.packet_count
        )
        with self._host_state.lock:
            self._host_state.packet_count = 0

    def _update_ui_status(self, value):

        utils.log('[DATA] Update UI:', value)

        with self._host_state.lock:
            if self._host_state.status_text:
                self._host_state.status_text = value

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

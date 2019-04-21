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
import traceback


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
            time.sleep(2)

        with self._host_state.lock:
            self._host_state.has_consent = True

        self._update_ui_status(
            'Continuously analyzing your network.\n'
        )

        # Continuously upload data
        while True:

            # If /is_inspecting_traffic was called too long ago, exit.
            with self._host_state.lock:
                last_ui_contact_ts = self._host_state.last_ui_contact_ts
                if last_ui_contact_ts:
                    time_delta = time.time() - last_ui_contact_ts
                    if time_delta > 15:
                        self._host_state.quit = True
                        return

            if not self._host_state.is_inspecting():
                self._update_ui_status('Paused inspection.')
                with self._host_state.lock:
                    self._clear_host_state_pending_data()
                time.sleep(2)
                continue

            time.sleep(UPLOAD_INTERVAL)

            with self._lock:
                if not self._active:
                    return

            utils.safe_run(self._upload_data)

    def _upload_initialization(self):
        """Returns True if successfully initialized."""

        # Send client's timezone to server
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

    def _clear_host_state_pending_data(self):

        self._host_state.pending_dhcp_dict = {}
        self._host_state.pending_resolver_dict = {}
        self._host_state.pending_dns_dict = {}
        self._host_state.pending_flow_dict = {}
        self._host_state.pending_ua_dict = {}
        self._host_state.pending_tls_dict = {}
        self._host_state.pending_netdisco_dict = {}

    def _prepare_upload_data(self):
        """Returns (window_duration, a dictionary of data to post)."""

        window_duration = time.time() - self._last_upload_ts

        # Remove all pending tasks
        with self._host_state.lock:

            dns_dict = self._host_state.pending_dns_dict
            dhcp_dict = self._host_state.pending_dhcp_dict
            resolver_dict = self._host_state.pending_resolver_dict
            flow_dict = self._host_state.pending_flow_dict
            ua_dict = self._host_state.pending_ua_dict
            ip_mac_dict = self._host_state.ip_mac_dict
            tls_dict = self._host_state.pending_tls_dict
            netdisco_dict = self._host_state.pending_netdisco_dict

            self._clear_host_state_pending_data()

            self._last_upload_ts = time.time()

        # Turn IP -> MAC dict into device_id -> (ip, device_oui) dict, ignoring
        # gateway's IP.
        device_dict = {}
        for (ip, mac) in ip_mac_dict.iteritems():
            # Never include the gateway
            if ip == self._host_state.gateway_ip:
                continue
            device_id = utils.get_device_id(mac, self._host_state)
            oui = utils.get_oui(mac)
            device_dict[device_id] = (ip, oui)

        # Process flow_stats
        for flow_key in flow_dict:

            flow_stats = flow_dict[flow_key]

            # Compute unique byte count during this window using seq number
            for direction in ('inbound', 'outbound'):
                flow_stats[direction + '_tcp_seq_range'] = get_seq_diff(
                    flow_stats[direction + '_tcp_seq_min_max']
                )
                flow_stats[direction + '_tcp_ack_range'] = get_seq_diff(
                    flow_stats[direction + '_tcp_ack_min_max']
                )

                # We use the original byte count or the sequence number as the
                # final byte count (whichever is larger), although we should
                # note the caveats of using TCP seq numbers to estimate flow
                # size in packet_processor.py.
                flow_stats[direction + '_byte_count'] = max(
                    flow_stats[direction + '_byte_count'],
                    flow_stats[direction + '_tcp_seq_range']
                )

            # Fill in missing byte count (e.g., due to failure of ARP spoofing)
            if flow_stats['inbound_byte_count'] == 0:
                outbound_seq_diff = flow_stats['outbound_tcp_ack_range']
                if outbound_seq_diff:
                    flow_stats['inbound_byte_count'] = outbound_seq_diff
            if flow_stats['outbound_byte_count'] == 0:
                inbound_seq_diff = flow_stats['inbound_tcp_ack_range']
                if inbound_seq_diff:
                    flow_stats['outbound_byte_count'] = inbound_seq_diff

            # Keep only the byte count fields
            flow_dict[flow_key] = {
                'inbound_byte_count': flow_stats['inbound_byte_count'],
                'outbound_byte_count': flow_stats['outbound_byte_count']
            }

        return (window_duration, {
            'dns_dict': jsonify_dict(dns_dict),
            'flow_dict': jsonify_dict(flow_dict),
            'device_dict': jsonify_dict(device_dict),
            'ua_dict': jsonify_dict(ua_dict),
            'dhcp_dict': jsonify_dict(dhcp_dict),
            'resolver_dict': jsonify_dict(resolver_dict),
            'client_version': self._host_state.client_version,
            'tls_dict': jsonify_dict(tls_dict),
            'netdisco_dict': jsonify_dict(netdisco_dict),
            'duration': str(window_duration),
            'client_ts': str(int(time.time()))
        })

    def _upload_data(self):

        # Prepare POST
        user_key = self._host_state.user_key
        url = server_config.SUBMIT_URL.format(user_key=user_key)
        (window_duration, post_data) = self._prepare_upload_data()

        if window_duration < 1:
            return

        # Try uploading across 5 attempts
        for attempt in range(5):

            status_text = 'Uploading data to cloud...\n'
            if attempt > 0:
                status_text += ' (Attempt {} of 5)'.format(attempt + 1)
                self._update_ui_status(status_text)

            utils.log('[UPLOAD]', status_text)

            # Upload data via POST
            response = requests.post(url, data=post_data).text
            utils.log('[UPLOAD] Gets back server response:', response)

            # Update whitelist
            try:
                response_dict = json.loads(response)
                if response_dict['status'] == 'success':
                    with self._host_state.lock:
                        self._host_state.device_whitelist = \
                            response_dict['inspected_devices']
                    break
            except Exception:
                utils.log('[UPLOAD] Failed. Retrying:', traceback.format_exc())
            time.sleep((attempt + 1) ** 2)

        # Report stats to UI
        with self._host_state.lock:
            byte_count = self._host_state.byte_count
            self._host_state.byte_count = 0

        self._update_ui_status(
            'Currently analyzing ' +
            '{:,}'.format(int(byte_count * 8.0 / 1000.0 / window_duration)) +
            ' Kbps of traffic.'
        )

        utils.log(
            '[UPLOAD] Total bytes in past epoch:',
            byte_count
        )

    def _update_ui_status(self, value):

        utils.log('[DATA] Update UI:', value)

        with self._host_state.lock:
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


def get_seq_diff(seq_tuple):
    """Returns the difference between two TCP sequence numbers."""

    (seq_min, seq_max) = seq_tuple

    if None in (seq_min, seq_max) or 0 in (seq_min, seq_max):
        return None

    # Seq wrap-around
    diff = seq_max - seq_min
    if diff < 0:
        diff += 2 ** 32

    return diff


def jsonify_dict(input_dict):
    """
    Returns a new dict where all the keys are jsonified as string, and all the
    values are turned into lists if they are sets.

    """
    output_dict = {}

    for (k, v) in input_dict.iteritems():
        if isinstance(k, tuple):
            k = json.dumps(k)
        if isinstance(v, set):
            v = list(v)
        output_dict[k] = v

    return json.dumps(output_dict)

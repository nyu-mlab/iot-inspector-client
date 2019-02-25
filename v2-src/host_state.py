"""
Global shared state about the host.

"""
import threading
import utils
import time


CLIENT_VERSION = '0.1'


class HostState(object):

    def __init__(self):

        self.host_ip = None
        self.host_mac = None
        self.gateway_ip = None
        self.packet_processor = None
        self.user_key = None
        self.secret_salt = None
        self.client_version = CLIENT_VERSION

        # The following objects might be modified concurrently.
        self.lock = threading.Lock()
        self.ip_mac_dict = {}  # IP -> MAC
        self.pending_dhcp_dict = {}  # device_id -> hostname
        self.pending_dns_dict = {}  # (device_id, domain) -> ip_set
        self.pending_flow_dict = {}  # flow_key -> flow_stats
        self.pending_ua_dict = {}  # device_id -> ua_set
        self.pending_tls_dict = {}  # hash -> fingerprint
        self.status_text = None
        self.device_whitelist = []
        self.has_consent = False
        self.byte_count = 0
        self.is_inspecting_traffic = True
        self.fast_arp_scan = True  # Persists for first 5 mins

        # Constantly checks for IP changes on this host
        thread = threading.Thread(target=self.update_ip_thread)
        thread.daemon = True
        thread.start()

    def set_ip_mac_mapping(self, ip, mac):

        with self.lock:
            self.ip_mac_dict[ip] = mac

    def get_ip_mac_dict_copy(self):

        with self.lock:
            return dict(self.ip_mac_dict)

    def is_inspecting(self):

        with self.lock:
            return self.is_inspecting_traffic

    def update_ip_thread(self):

        while True:

            try:
                self.gateway_ip, _, self.host_ip = utils.get_default_route()
            except Exception:
                pass

            time.sleep(15)

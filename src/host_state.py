"""
Global shared state about the host.

"""
import threading


CLIENT_VERSION = '0.1'


class HostState(object):

    def __init__(self):

        self.host_ip = None
        self.host_mac = None
        self.gateway_ip = None
        self.ip_prefix = None
        self.packet_processor = None
        self.user_key = None
        self.secret_salt = None
        self.client_version = CLIENT_VERSION

        # The following objects might be modified concurrently.
        self.lock = threading.Lock()
        self.ip_mac_dict = {}
        self.pending_dns_responses = []
        self.pending_pkts = []
        self.status_text = None
        self.device_whitelist = []
        self.has_consent = False
        self.packet_count = 0
        self.ui_is_ready = False

    def set_ip_mac_mapping(self, ip, mac):

        with self.lock:
            self.ip_mac_dict[ip] = mac

    def get_ip_mac_dict_copy(self):

        with self.lock:
            return dict(self.ip_mac_dict)

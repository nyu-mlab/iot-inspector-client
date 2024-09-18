"""
Maintains the global state in a singleton design pattern.

"""
import threading
import queue
import os


DEBUG = False

# If there is a file called "DEBUG.txt" in the ".." directory outside of the
# repo, then turn on the DEBUG mode.
if os.path.isfile(os.path.join(os.path.dirname(__file__), '..', '..', 'DEBUG.txt')):
    DEBUG = True

# Path to URL, i.e., http://localhost:33761{BASE_PATH}
BASE_PATH = '/inspector_dashboard'

# Should be held whenever accessing the global state's variables.
global_state_lock = threading.Lock()

# Network interface to sniff and send packets.
active_network_interface = ''

# Whether the application is running or not. True by default; if false, the
# entire application shuts down.
is_running = True

# Whether inspection mode is enabled or not. True by default; if not, stops all
# inspection. Does not change the is_inspected state in the devices table.
is_inspecting = True

# Network variables
host_ip_addr = ''
host_mac_addr = ''
host_active_interface = ''
gateway_ip_addr = ''

# Maps IP addresses to MAC addresses
arp_cache = None

# Make sure that only one single instance of Inspector core is running
inspector_started = [False]
inspector_started_ts = 0

# A queue that holds packets to be processed
packet_queue = queue.Queue()

# A dictionary that maps IP addresses to hostnames
hostname_dict = dict()

# Where to upload donated data
INSPECTOR_DATA_DONATION_SERVER = 'https://inspector.engineering.nyu.edu/backend_api'
if DEBUG:
    INSPECTOR_DATA_DONATION_SERVER = 'http://dannys-macbook-air:39402/backend_api'

DATA_DONATION_URL = INSPECTOR_DATA_DONATION_SERVER + '/donate_data'
IP_INSIGHTS_URL = INSPECTOR_DATA_DONATION_SERVER + '/get_hostname_from_ip'
DEVICE_INSIGHTS_URL = INSPECTOR_DATA_DONATION_SERVER + '/get_product_name'
USER_KEY_URL = INSPECTOR_DATA_DONATION_SERVER + '/get_user_key'
DELETE_DATA_URL = INSPECTOR_DATA_DONATION_SERVER + '/delete_donated_data'


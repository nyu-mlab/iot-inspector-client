"""
Generates mock data into both SQLite databases in real time.

Usage: python3 generate_mock_data.py

This will dynamically generate two database files, network_traffic.db and
configs.db, to the current working directory. If you're developing the GraphQL
server, you should be reading/writing the two database files in the same
directory, too.

This script does not terminate. It continuously writes network traffic data (as
if Inspector were really running). You can hit Control + C to kill the script.
You can run the script again to continue generating more data. Running the
script again only appends more data to the database. If you want a clean start,
simply delete the database files.

The data generated is random but seeded. In other words, even though the data is
random, it is deterministically random. If you want a different set of random
numbers, change the `random.seed(0)` statement to use a different seed.

By default, this script generates 10 mock devices. To change this number, set
the `MOCK_DEVICE_COUNT` acoordingly.

"""
import sqlite3
import random
import time
from common_functions import insert_many, round_down
import subprocess


# If the call below fails, run this script with sudo (which means that you'd
# also need to run yarn with sudo).
assert subprocess.call('mkdir -p /Applications/inspector/', shell=True) == 0
TRAFFIC_DB_PATH = '/Applications/inspector/network_traffic.db'
CONFIG_DB_PATH = '/Applications/inspector/configs.db'


# Initialize the DB connections
traffic_db = sqlite3.connect(TRAFFIC_DB_PATH, isolation_level=None)
traffic_db.execute('pragma journal_mode=wal;')
traffic_db.row_factory = sqlite3.Row

config_db = sqlite3.connect(CONFIG_DB_PATH, isolation_level=None)
config_db.execute('pragma journal_mode=wal;')
config_db.row_factory = sqlite3.Row


# Make sure that our results are reproducible
random.seed(0)

# How many random devices to generate
MOCK_DEVICE_COUNT = 10

# Mock vendors
VENDOR_LIST = ['Google', 'Amazon', 'Philips', 'Samsung', 'LG', 'GE', 'Facebook']

# Mock device types
DEVICE_TYPE_LIST = ['camera', 'vacuum', 'tv', 'fridge', 'speaker', 'light', 'plug', 'toilet', 'oven']

# Mock domains
DOMAIN_LIST = ['google', 'amazonaws', 'amazon', 'apple', 'facebook', 'doubleclick', 'microsoft', 'samsung', 'netflix']

# Mock countries
COUNTRY_LIST = ['US', 'DE', 'UK', 'CN', 'JP', 'KR']


def main():

    print('Preparing tables.')

    # Reset tables
    config_db.execute('DROP TABLE IF EXISTS device_info')
    traffic_db.execute('DROP TABLE IF EXISTS devices')

    # Initialize tables
    with open('network_traffic.schema.sql') as fp:
        traffic_db.executescript(fp.read())
    with open('configs.schema.sql') as fp:
        config_db.executescript(fp.read())

    # Insert a single row in the user_configs table if it is not already there
    if len(list(config_db.execute('SELECT * FROM user_configs LIMIT 1'))) == 0:
        insert_many(
            config_db,
            'user_configs',
            [{'id': 0}]
        )

    device_id_list = []

    try:
        while True:

            # Continuously generate new devices until max
            new_device_id_list = []
            if len(device_id_list) < MOCK_DEVICE_COUNT:
                new_device_id_list = generate_mock_devices()
                device_id_list += new_device_id_list

            # Generate fake traffic from all devices for 10 seconds

            generate_mock_traffic(new_device_id_list, device_id_list)

    except KeyboardInterrupt:
        print('Done.')
        return


def generate_mock_devices(new_device_count=2):
    """
    Populates the device_info table with 2 mock devices at a time.

    Returns a list of the newly created mock device IDs.

    """
    # Prepare mock device IDs
    device_id_list = []
    for _ in range(new_device_count):
        device_id = 's' + str(random.randint(1000, 9999))
        device_id_list.append(device_id)

    insert_many(
        config_db, 'device_info',
        [
            {'device_id': device_id, 'is_inspected': 1}
            for device_id in device_id_list
        ]
    )

    print('Created two new devices.')

    return device_id_list


def generate_mock_traffic(new_device_id_list, device_id_list):
    """
    Generates mock traffic forever, until the user kills this process.

    The traffic will appear from devices in the device_id_list, generated in
    generate_mock_devices().

    """
    # Prepopulates new devices
    device_list = []
    for device_id in new_device_id_list:
        device_list.append({
            'device_id': device_id,
            'ip': '10.0.{}.{}'.format(random.randint(2, 255), random.randint(2, 255)),
            'mac': ':'.join([str(random.randint(0, 9)) + str(random.randint(0, 9)) for _ in range(6)]),
            'auto_name': random.choice(VENDOR_LIST) + ' ' + random.choice(DEVICE_TYPE_LIST),
            'last_updated_ts': time.time()
        })

    # Insert the mock devices into the devices table
    insert_many(traffic_db, 'devices', device_list)

    # Generate flows continuously
    print('Generating flows for 10 seconds')
    start_ts = time.time()
    prev_ts = None
    while time.time() - start_ts < 10:
        sleep_time = random.randint(10, 15) / 10.0
        time.sleep(sleep_time)
        current_ts = time.time()
        random.shuffle(device_id_list)
        if prev_ts is None:
            window_size = 9999999
        else:
            window_size = current_ts - prev_ts
        for device_id in device_id_list:
            generate_mock_traffic_helper(device_id, current_ts, window_size)
        prev_ts = current_ts



def generate_mock_traffic_helper(device_id, ts, window_size):
    """
    Generate traffic for device_id

    """
    remote_ip_last_digit = random.randint(2, 254)

    # Generate counterparty
    remote_ip = '100.100.100.' + str(remote_ip_last_digit)
    remote_hostname = ''

    # If we have seen this counterparty IP before, get the hostname
    query = 'SELECT * FROM counterparties WHERE remote_ip = ?'
    for row in traffic_db.execute(query, (remote_ip, )):
        remote_hostname = row['hostname']

    # Otherwise, create a new record with probability = 0.25, because
    # realistically Inspector may not be able to determine the hostname for
    # every counterparty IP address
    if random.random() < 0.25 and remote_hostname == '':
        remote_hostname = random.choice(DOMAIN_LIST) + '.com'
        insert_many(traffic_db, 'counterparties', [{
            'remote_ip': remote_ip,
            'hostname': remote_hostname,
            'device_id': device_id,
            'source': 'dns',
            'ts': ts
        }])

    # Generate the flow
    counterparty_port = random.choice([80, 443, 8080])
    counterparty_is_ad_tracking = 0
    if remote_hostname:
        if (remote_ip_last_digit % 5) == 0:
            counterparty_is_ad_tracking = 1
    flow_dict = {
        'device_id': device_id,
        'device_port': random.randint(10000, 65000),
        'counterparty_ip': remote_ip,
        'counterparty_port': counterparty_port,
        'counterparty_hostname': remote_hostname,
        'counterparty_country': random.choice(COUNTRY_LIST),
        'counterparty_is_ad_tracking': counterparty_is_ad_tracking,
        'uses_weak_encryption': (0 if counterparty_port == 443 else 1),
        'ts': ts,
        'ts_mod_60': round_down(ts, 60),
        'ts_mod_600': round_down(ts, 600),
        'ts_mod_3600': round_down(ts, 3600),
        'window_size': window_size,
        'inbound_byte_count': random.randint(0, 200),
        'outbound_byte_count': random.randint(0, 50),
        'inbound_packet_count': random.randint(0, 20),
        'outbound_packet_count': random.randint(0, 5)
    }
    insert_many(traffic_db, 'flows', [flow_dict])

    # Set the device update time
    traffic_db.execute("""
        UPDATE devices
        SET last_updated_ts = ?
        WHERE device_id = ?
    """, (ts, device_id))


if __name__ == '__main__':
    main()
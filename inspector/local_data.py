import sqlite3
import os
from common_functions import insert_many, round_down
import time
import oui_parser
import geoip2.database


# How often to write to DB
UPLOAD_INTERVAL = 2


TRAFFIC_DB_PATH = '/Applications/inspector/network_traffic.db'
CONFIG_DB_PATH = '/Applications/inspector/configs.db'


ip_country_parser = geoip2.database.Reader('maxmind-country.mmdb')



def write_data(post_data):

    # Flows: read and write
    traffic_db = sqlite3.connect(TRAFFIC_DB_PATH, isolation_level=None)
    traffic_db.execute('pragma journal_mode=wal;')
    traffic_db.row_factory = sqlite3.Row

    # Configurations: read oly
    config_db = sqlite3.connect(CONFIG_DB_PATH, isolation_level=None)
    config_db.execute('pragma journal_mode=wal;')
    config_db.row_factory = sqlite3.Row

    handle_device_dict(post_data, traffic_db, config_db)

    # Get a list of existing devices
    device_id_set = set()
    for row in traffic_db.execute('SELECT DISTINCT device_id FROM devices'):
        device_id_set.add(row['device_id'])

    handle_dns_dict(post_data, traffic_db, config_db, device_id_set)
    handle_flow_dict(post_data, traffic_db, config_db, device_id_set)



def initialize_tables():
    """
    Creates the initial DB tables if the DB files do not exist yet.

    """
    if not os.path.isfile(TRAFFIC_DB_PATH):
        with open('network_traffic.schema.sql') as fp:
            with sqlite3.connect(TRAFFIC_DB_PATH) as traffic_db:
                traffic_db.executescript(fp.read())

    if not os.path.isfile(CONFIG_DB_PATH):
        with open('configs.schema.sql') as fp:
            with sqlite3.connect(CONFIG_DB_PATH) as config_db:
                config_db.executescript(fp.read())

                # Insert a single row in the user_configs table if it is not already there
                if len(list(config_db.execute('SELECT * FROM user_configs LIMIT 1'))) == 0:
                    insert_many(
                        config_db,
                        'user_configs',
                        [{'id': 0}]
                    )


def handle_device_dict(post_data, traffic_db, config_db):
    """
    device_dict: device_id -> (device_ip, device_oui)
    """
    try:
        device_dict = post_data['device_dict']
    except KeyError:
        return

    ts = int(time.time())

    for (device_id, (device_ip, device_oui)) in device_dict.items():

        result = traffic_db.execute("""
            SELECT COUNT(*) AS device_count
            FROM devices
            WHERE device_id = ?
        """, (device_id, )).fetchone()

        # Existing device: update the last_updated_ts
        if result['device_count'] > 0:
            traffic_db.execute("""
                UPDATE devices
                SET
                    ip = ?,
                    last_updated_ts = ?
                WHERE
                    device_id = ?
            """, (device_ip, ts, device_id))

        # Insert new device
        else:
            traffic_db.execute("""
                INSERT INTO devices (
                    device_id,
                    ip,
                    mac,
                    auto_name,
                    last_updated_ts
                )
                VALUES (?, ?, ?, ?, ?)
            """, (device_id, device_ip, device_oui + '0' * 6, oui_parser.get_vendor(device_oui), ts))


def handle_dns_dict(post_data, traffic_db, config_db, device_id_set):
    """
    dns_dict: (device_id, domain) -> ip_set

    """
    try:
        dns_dict = post_data['dns_dict']
    except KeyError:
        return

    ts = int(time.time())

    insert_list = []

    for ((device_id, domain, data_source, _), ip_set) in dns_dict.items():
        for ip in ip_set:
            if device_id in device_id_set:
                insert_list.append({
                    'remote_ip': ip,
                    'hostname': domain,
                    'device_id': device_id,
                    'source': 'dns',
                    'ts': ts
                })

    insert_many(traffic_db, 'counterparties', insert_list)


def handle_flow_dict(post_data, traffic_db, config_db, device_id_set):
    """
    flow_dict:
        flow_key -> flow_stats, where flow_key =
          (device_id, device_port, remote_ip, remote_port, protocol),
          and flow_stats is a dict of {inbound_byte_count, outbound_byte_count}
    """
    try:
        flow_dict = post_data['flow_dict']
    except KeyError:
        return

    ts = int(time.time())

    flow_insert_list = []

    # Set of updated device_ids
    updated_device_ids = set()

    for (flow_key, flow_stats) in flow_dict.items():
        flow_dict = _parse_single_flow(flow_key, flow_stats, post_data)
        if flow_dict :
            device_id = flow_dict['device_id']
            if device_id in device_id_set:
                flow_insert_list.append(flow_dict)
                updated_device_ids.add(device_id)

    # Write flow to db in bulk
    if flow_insert_list:
        insert_many(traffic_db, 'flows', flow_insert_list)

    # Update device update ts
    for device_id in updated_device_ids:
        traffic_db.execute("""
            UPDATE devices
            SET last_updated_ts = ?
            WHERE device_id = ?
        """, (ts, device_id))


def _parse_single_flow(flow_key, flow_stats, post_data):

    (device_id, device_port, remote_ip, remote_port, protocol) = flow_key

    ts = int(time.time())
    flow_dict = {
        'device_id': device_id,
        'device_port': device_port,
        'counterparty_ip': remote_ip,
        'counterparty_port': remote_port,
        'counterparty_hostname': remote_ip,
        'counterparty_friendly_name': remote_ip,
        'counterparty_country': get_country(remote_ip),
        'transport_layer_protocol': protocol,
        'uses_weak_encryption': (1 if remote_port == 80 else 0),
        'ts': ts,
        'ts_mod_60': round_down(ts, 60),
        'ts_mod_600': round_down(ts, 600),
        'ts_mod_3600': round_down(ts, 3600),
        'window_size': post_data['duration'],
        'inbound_byte_count': flow_stats['inbound_byte_count'],
        'outbound_byte_count': flow_stats['outbound_byte_count'],
        'inbound_packet_count': 1,
        'outbound_packet_count': 1
    }

    return flow_dict


def get_country(remote_ip):
    """Returns country for IP."""

    country = None
    try:
        country = ip_country_parser.country(remote_ip).country.iso_code

    except Exception:
        pass

    if country:
        return country

    return ''

"""
Schemas for SQLite database.

"""

# Key-value store for global settings and state
KV_STORE_TABLE = """
    CREATE TABLE IF NOT EXISTS kv_store (
        key_id INTEGER PRIMARY KEY,
        key TEXT,
        value TEXT
    );

    CREATE INDEX IF NOT EXISTS kv_store_key 
    ON kv_store (key);
"""

# Stores device related info
DEVICE_TABLE = """
    CREATE TABLE IF NOT EXISTS devices (
        device_id TEXT PRIMARY KEY,
        ip TEXT,
        mac TEXT,
        is_inspected INTEGER,
        is_blocked INTEGER,
        user_device_name TEXT,
        tag_list TEXT,
        dhcp_hostname TEXT,
        netdisco_list TEXT,
        user_agent_list TEXT,  
        syn_scan_port_list TEXT,
        resolver_ip TEXT,
        last_updated_ts INTEGER
    );

"""


# Overview statistics of flows
FLOW_OVERVIEW_TABLE = """
    CREATE TABLE IF NOT EXISTS flow_overview (
        device_id TEXT PRIMARY KEY,
        device_port INTEGER,
        counterparty_id TEXT, 
        counterparty_ip TEXT,        
        counterparty_port INTEGER,
        transport_layer_protocol TEXT,
        flow_key TEXT, -- Hash of <device_ip, device_port, counterparty_ip, counterparty_port, transport protocol>
        counterparty_hostname TEXT,
        counterparty_country TEXT,
        counterparty_is_ad_tracking INTEGER,
        uses_no_encryption INTEGER,
        uses_weak_encryption INTEGER,
        extra_info_list TEXT
    );
"""

# Details of individual flows
FLOW_WINDOW_TABLE = """
    CREATE TABLE IF NOT EXISTS flow_window (
        flow_key TEXT PRIMARY KEY,
        window_min_ts INTEGER,
        window_max_ts INTEGER,
        inbound_byte_count INTEGER,
        outbound_byte_count INTEGER,
        inbound_packet_count INTEGER,
        outbound_packet_count INTEGER,
        
    )
"""


# Stores IP-Hostname mappings from DNS, HTTP Host, and SNI
HOSTNAME_IP_TABLE = """

"""

def initialize_db():
    """
    Initializes schemas, tables, and indexes. Fills default values.

    
    """
    pass


def create_tables():
    pass


def create_default_values():
    
    # e.g., secret salt, gateway ip, host ip, mac, network, mask, version

    pass

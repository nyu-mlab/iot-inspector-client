/*

    Schema for the network_traffic database.

    Captures all network traffic, readable and writable by the Python driver, but
    only readable by the GraphQL server.

    This database includes the following tables:
    - devices: all devices scanned
    - flows: aggregated stats on captured traffic
    - counterparties: identities of remote IP addresses
    - tls: TLS statistics (not used for front-end)

    Data types:
    - All lists are JSON encoded.
    - All timestamps (`ts`) are represented as UNIX Epochs.
    - All boolean fields are represented as 1 for true and 0 for false.
    - If a field is optional, the value could be NULL.

    See the system design diagram here:
    https://drive.google.com/file/d/1NPmysXA42BwZnroqAikgl_3HbTHSimJH/view

    Examples of usage:
    https://xd.adobe.com/view/250bfa62-c34a-4356-9cf3-dedf1313c814-7058/screen/5a8b945a-9d7d-4095-87a8-82f8be6716ec/

 */


/*
    Inspector creates a new row when it discovers a device on the network.
    Inspector may update an existing row when it detects a device state change
    (e.g., IP changes) during Inspector's regular network rescans.
 */
CREATE TABLE IF NOT EXISTS devices (
    -- Row ID
    id INTEGER PRIMARY KEY,
    -- ID of device
    device_id TEXT NOT NULL,
    -- Latest IP address of device
    ip TEXT NOT NULL,
    -- MAC address of device
    mac TEXT NOT NULL,
    -- List of DHCP hostname sniffed
    dhcp_hostname_list TEXT DEFAULT "[]" NOT NULL,
    -- List of unique netdisco scan results
    netdisco_list TEXT DEFAULT "[]" NOT NULL,
    -- List of user agents sniffed via HTTP
    user_agent_list TEXT DEFAULT "[]" NOT NULL,
    -- List of ports that respond to Inspector's SYN scan
    syn_scan_port_list TEXT DEFAULT "[]" NOT NULL,
    -- Automatically inferred name of device; if a user already manually provide a name in the `device_info` table, Inspector will automatically replace fill in the manual value into `auto_name`.
    auto_name TEXT DEFAULT "" NOT NULL,
    -- Last time this record is updated
    last_updated_ts REAL NOT NULL
);

/*
    Inspector creates a new row when it sees a new flow between a device and a
    counterparty (which could be a host on the Internet or another device on the
    same network), or an existing flow continues beyond the (default) 1 second
    window. Inspector may update an existing row when it obtains more
    information about the flow (e.g., the hostname of the counterparty).

    For example, if Device X communicates with https://google.com over 3
    seconds, you'll see three separate rows, all of which show Device X with
    some random device port communicating with the counterparty Google at
    counterport port 443; one row 0-1 seconds, one row 1-2 seconds, and one row 2-3 seconds.
*/
CREATE TABLE IF NOT EXISTS flows (
    -- Row ID
    id INTEGER PRIMARY KEY,
    -- ID of device. Same as the device_id in the devices table. We're not using
    -- the foreign key constraints here because a user may decide to delete a
    -- flow/device.
    device_id TEXT NOT NULL,
    -- Port of flow on device
    device_port INTEGER DEFAULT 0 NOT NULL,
    -- IP address of counterparty
    counterparty_ip TEXT NOT NULL,
    -- Port of counterparty
    counterparty_port INTEGER DEFAULT 0 NOT NULL,
    -- Optional, hostname of counterparty
    counterparty_hostname TEXT DEFAULT "" NOT NULL,
    -- Optional, user-friendly name of the counterparty
    counterparty_friendly_name TEXT DEFAULT "" NOT NULL,
    -- Two-letter country code of counterparty
    counterparty_country TEXT DEFAULT "" NOT NULL,
    -- Boolean: whether the counterparty is an ad/tracking service
    counterparty_is_ad_tracking INTEGER DEFAULT 0 NOT NULL,
    -- ID of the counterparty if the counterparty is a local device; empty
    -- string if the counterparty is on the Internet (rather than on the local
    -- network)
    counterparty_local_device_id TEXT DEFAULT "" NOT NULL,
    -- "tcp", "udp", or "" if neither TCP nor UDP
    transport_layer_protocol TEXT DEFAULT "" NOT NULL,
    -- Boolean: whether the flow uses weak encryption
    uses_weak_encryption INTEGER DEFAULT 0 NOT NULL,
    -- timestamp for the start of this flow; expressed at UNIX Epoch
    ts REAL NOT NULL,
    -- timestamps rounded to the nearest minute
    ts_mod_60 REAL NOT NULL,
    -- timestamps rounded to the nearest 10 minutes
    ts_mod_600 REAL NOT NULL,
    -- timestamps rounded to the nearest 60 minutes
    ts_mod_3600 REAL NOT NULL,
    -- duration of this window in seconds; typically around 1 sec
    window_size REAL NOT NULL,
    -- Number of bytes coming into device from counterparty
    inbound_byte_count INTEGER DEFAULT 0 NOT NULL,
    -- Number of bytes going out of device into counterparty
    outbound_byte_count INTEGER DEFAULT 0 NOT NULL,
    -- Number of packets coming into device
    inbound_packet_count INTEGER DEFAULT 0 NOT NULL,
    -- Number of bytes going out of device into counterparty
    outbound_packet_count INTEGER DEFAULT 0 NOT NULL
);


/*
    Maps each remote counterparty to a named entity, e.g., hostname.
*/
CREATE TABLE IF NOT EXISTS counterparties (
    -- Row ID
    id INTEGER PRIMARY KEY,
    -- Remote IP address of the counterparty
    remote_ip TEXT NOT NULL,
    -- Hostname of the IP address
    hostname  TEXT NOT NULL,
    -- On which device we observe this mapping
    device_id TEXT NOT NULL,
    -- Data source for this mapping: "dns", "sni", or "http_host"
    source TEXT NOT NULL,
    -- Resolver if data_source == "dns"
    resolver_ip TEXT DEFAULT "" NOT NULL,
    -- Timestamp when we observe this mapping
    ts REAL NOT NULL
);
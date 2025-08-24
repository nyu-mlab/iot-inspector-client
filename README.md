# IoT Inspector 3

Simply run `./start.bash`. It will take care of all the dependencies.

If the underlying Inspector core library is updated, please run the following first:

```bash
uv cache clean
uv lock --upgrade-package libinspector
uv sync
```


# Developer Guide

If you are developing IoT Inspector, please read this section.

## Database Schema

When presenting network stats, IoT Inspector reads from an internal SQLite database.

You should always read from the database using the following approach:

```python
import libinspector
db_conn, rwlock = libinspector.global_state.db_conn_and_lock
with rwlock:
    db_conn.execute("SELECT * FROM devices")
```

The schema is as follows:

```sql
CREATE TABLE devices (
    mac_address TEXT PRIMARY KEY,
    ip_address TEXT NOT NULL,
    is_inspected INTEGER DEFAULT 0,
    is_gateway INTEGER DEFAULT 0,
    updated_ts INTEGER DEFAULT 0,
    metadata_json TEXT DEFAULT '{}'
)

CREATE TABLE hostnames (
    ip_address TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    updated_ts INTEGER DEFAULT 0,
    data_source TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}'
)

CREATE TABLE network_flows (
    timestamp INTEGER,
    src_ip_address TEXT,
    dest_ip_address TEXT,
    src_hostname TEXT,
    dest_hostname TEXT,
    src_mac_address TEXT,
    dest_mac_address TEXT,
    src_port TEXT,
    dest_port TEXT,
    protocol TEXT,
    byte_count INTEGER DEFAULT 0,
    packet_count INTEGER DEFAULT 0,
    metadata_json TEXT DEFAULT '{}',
    PRIMARY KEY (
            timestamp,
            src_mac_address, dest_mac_address,
            src_ip_address, dest_ip_address,
            src_port, dest_port,
            protocol
        )
)
```
# IoT Inspector 3
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![libinspector_test](https://github.com/nyu-mlab/iot-inspector-client/actions/workflows/inspector_test.yaml/badge.svg)](https://github.com/nyu-mlab/iot-inspector-client/actions/workflows/inspector_test.yaml)[![codecov](https://codecov.io/gh/nyu-mlab/iot-inspector-client/graph/badge.svg?token=SFZ2QUJWQW)](https://codecov.io/gh/nyu-mlab/iot-inspector-client)

Simply run `./start.bash` for Linux/Mac and `start.bat` for Windows. It will take care of all the dependencies.

If the underlying dependencies is updated, please run the following first:

```bash
uv cache clean
uv lock
uv sync
```

# User guide
Please review the [User Guide](https://github.com/nyu-mlab/iot-inspector-client/wiki) for instructions how to run IoT Inspector. 

# Developer Guide

If you are developing IoT Inspector, please read this section.

## Database Schema

When presenting network stats, IoT Inspector reads from an internal SQLite database. 
To see how the packet collector and database is implemented, look at the [IoT Inspector Core package](https://github.com/nyu-mlab/inspector-core-library).

You should always read from the database using the following approach:

```python
import libinspector.global_state
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
);

CREATE TABLE hostnames (
    ip_address TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    updated_ts INTEGER DEFAULT 0,
    data_source TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}'
);

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
);
```

# IoT Inspector Helper Scripts
We also include two scripts to help with development and debugging.

## Anonymize
After installing IoT Inspector, you can run the following command:
```bash
anonymize -i <input_pcap_file> -o <output_pcap_file>
```

Here is the help output
```text
anonymize -h
usage: anonymize [-h] [-i INPUT_FILE] [-o OUTPUT]

Anonymize MACs and filter specific control packets (DHCP, SSDP, MDNS) from a PCAP file.

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input INPUT_FILE
                        The path to the input PCAP file.
  -o OUTPUT, --output OUTPUT
                        The path to save the anonymized PCAP file (default: sanitized_output.pcap).
```

The output PCAP file will have all 
* MAC addresses anonymized 
* all DHCP, SSDP, and MDNS packets removed. 

This is useful for sharing PCAP files without revealing sensitive information.

## PCAP Time Series
After installing IoT Inspector, you can run the following command:
```bash
time-series -i <PCAP_FILE> -m <TARGET_MAC> -o <OUTPUT_PNG_FILE> --b <BIN_SIZE_IN_SECONDS>
```

Here is the help output
```text
usage: time_series [-h] -i INPUT_FILE -m TARGET_MAC [-o OUTPUT] [--interval INTERVAL]

Analyze PCAP file to plot upload and download traffic over time for a specific MAC address.

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input INPUT_FILE
                        The path to the input PCAP file.
  -m TARGET_MAC, --target-mac TARGET_MAC
                        The MAC address of the device to analyze (e.g., 'aa:bb:cc:dd:ee:ff').
  -o OUTPUT, --output OUTPUT
                        The path to save the output plot PNG file (default: traffic_timeseries.png).
  -b BIN_SIZE, --bin BIN_SIZE
                        The width of time bins in seconds for aggregating traffic data (default: 0.05 seconds).
```

The output will be a PNG file showing the upload and download traffic over time for the specified MAC address. This is useful for visualizing traffic patterns of a device in a PCAP file.

The output should look something like this on the console.
```text
INFO: Starting analysis for: TEST.pcap
INFO: Target MAC for analysis: 44:3d:54:e3:4b:6e
INFO: Time bin size: 0.05 seconds
INFO: Read 2392 packets. Starting data processing...
INFO: Generating plot...
INFO: Successfully saved plot to 'traffic_timeseries.png'
```
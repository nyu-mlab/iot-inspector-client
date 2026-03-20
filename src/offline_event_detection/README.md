# Offline Event Detection

This module runs the event detection pipeline on a saved PCAP file without starting the IoT Inspector UI.

## Usage

Run from the repository root:

```bash
PYTHONPATH=src python -m offline_event_detection \
  --pcap /path/to/capture.pcap \
  --device-mac aa:bb:cc:dd:ee:ff \
  --device-name "Amazon Plug"
```

If you know the exact model folder name, you can pass it directly:

```bash
PYTHONPATH=src python -m offline_event_detection \
  --pcap /path/to/capture.pcap \
  --device-mac aa:bb:cc:dd:ee:ff \
  --model-name amazon_plug
```

## Arguments

- --pcap: Path to the PCAP file.
- --device-mac: MAC address of the device that produced the capture.
- --device-name: Human-readable device name to match a model.
- --model-name: Exact model folder name to use.
- --max-packets: Optional limit on packets to process.
- --log-level: Logging level (DEBUG, INFO, WARNING, ERROR).

## Output

The command prints summary statistics and detected events as tab-separated rows:

```
<device>\t<timestamp>\t<event>
```

# IoT Inspector 2 (testing)

An open-source tool for capturing, analyzing, and visualizing the network activities of your smart home devices. It does not require special hardware or changes to your network. Simply run IoT Inspector and you'll see the results instantly.

IoT Inspector is a research project by researchers from New York University.


## Running Inspector

### Running from the source code

The instructions below have been tested on macOS Ventura:

First, download the source code.

```
git clone https://github.com/nyu-mlab/iot-inspector-client.git
cd iot-inspector-client
git switch inspector2
git pull origin inspector2
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

To run, do the following

```
source env/bin/activate
cd ui
./start.bash

```

## Developing for IoT Inspector

To learn how Inspector scans the network and captures the traffic, look at the `core/start.py` file. The relevant modules include `arp_scanner.py`, `arp_spoofer.py`, and `packet_*.py`.

To learn how Inspector constructs the user interface, follow the `ui/start.bash` command.

Dependencies: Inspector depends on these packages: pandas peewee scapy requests geoip2 netifaces netaddr streamlit plotly tldextract kaleido

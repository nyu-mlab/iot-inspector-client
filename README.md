# IoT Inspector 2

An open-source tool for capturing, analyzing, and visualizing the network activities of your smart home devices. It does not require special hardware or changes to your network. Simply run IoT Inspector and you'll see the results instantly.

IoT Inspector is a research project by researchers from New York University.

See our [documentation](https://github.com/nyu-mlab/iot-inspector-client/wiki).

## Getting started

### Download and install

See [this page](https://github.com/nyu-mlab/iot-inspector-client/wiki/Download-&-Install) if you want to run our precompiled binaries.


### Running from the source code

You will need Python and Git already set up on your system. You'll also need to be familiar with terminals.

#### Tested on macOS Ventura

Run the following in your terminal:

```
git clone https://github.com/nyu-mlab/iot-inspector-client.git
cd iot-inspector-client
python3 -m venv env
source env/bin/activate
pip install -r requirements-general.txt
```

To run, do the following

```
source env/bin/activate
cd ui
./start.bash

```

#### Tested on Windows 10 & 11 with Python 3.8

Run the following in your terminal:

```
git clone https://github.com/nyu-mlab/iot-inspector-client.git
cd iot-inspector-client
python.exe -m venv env
env/Script/activate.bat
pip install -r requirements.txt
```

If you have a more modern version of Python (say Python 3.11), try replacing the last line above with:

```
pip install -r requirements-general.txt
```

To run, do the following in an terminal with administrator's priviledge:

```
env/Script/activate.bat
cd ui
streamlit.exe run Device_List.py --server.port 33761 --browser.gatherUsageStats false --server.headless true --server.baseUrlPath "inspector_dashboard"

```



## Developing for IoT Inspector

To learn how Inspector scans the network and captures the traffic, look at the `core/start.py` file. The relevant modules include `arp_scanner.py`, `arp_spoofer.py`, and `packet_*.py`.

To learn how Inspector constructs the user interface, follow the `ui/start.bash` command.

For details, see our [documentation](https://github.com/nyu-mlab/iot-inspector-client/wiki).

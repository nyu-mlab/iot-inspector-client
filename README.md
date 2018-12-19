# Princeton IoT Inspector Client Software

## Ubuntu 18.04

### Installation

First, execute the following commands in your terminal to download the source code.

1. `git clone git@github.com:noise-lab/iot-inspector-client.git`
2. `cd iot-inspector-client/src`

Next, install the prerequisits

1. `sudo apt install python-pip python-tk`
2. `sudo pip install virtualenv`
3. `pip install elevate scapy netaddr scapy-ssl_tls scapy-http`

### Running IoT Inspector

Run `python start_inspector.py` and enter the `sudo` password as prompted on the command line.

At the same time, a browser window will appear that allows you to view the inspection report.

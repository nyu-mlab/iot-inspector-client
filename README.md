# Princeton IoT Inspector Client Software

## Ubuntu 18.04

### Installation

Install the prerequisits.

1. `sudo apt install python-pip python-tk git`
2. `sudo pip install virtualenv`

### Running IoT Inspector

1. `git clone git@github.com:noise-lab/iot-inspector-client.git`
2. `cd iot-inspector-client/src`

If this is the first time running IoT Inspector, do the following:

3. `virtualenv env`
4. `source env/bin/activate`
5. `pip install elevate scapy netaddr scapy-ssl_tls scapy-http`
6. `python start_inspector.py`

If this is not the first time, do the following

3. `source env/bin/activate`
4. `python start_inspector.py`

Once you run `python start_inspector.py`, you will be prompted to enter your `sudo` password on the command line. At the same time, a browser window will appear that allows you to view the inspection report.

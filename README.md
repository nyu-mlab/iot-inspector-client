# Princeton IoT Inspector Client Software

## Ubuntu 18.04

### Installation

Install the prerequisits.

1. `sudo apt install python-pip python-tk git`
2. `sudo pip install virtualenv`

### Running IoT Inspector

1. `git clone https://github.com/noise-lab/iot-inspector-client.git`
2. `cd iot-inspector-client/src`

If this is the first time running IoT Inspector, do the following:

3. `virtualenv env`
4. `source env/bin/activate`
5. `pip install elevate netaddr`
6. `pip install scapy`
7. `pip install scapy-http`
8. `pip install scapy-ssl_tls`
9. `python start_inspector.py`

(Do not combine Steps 5 through 8 into a single `pip install`, as doing so will result in the SSL_TLS package not being properly installed.)

If this is not the first time, do the following

3. `source env/bin/activate`
4. `python start_inspector.py`

Once you run `python start_inspector.py`, you will be prompted to enter your `sudo` password on the command line. At the same time, a browser window will appear that allows you to view the inspection report.

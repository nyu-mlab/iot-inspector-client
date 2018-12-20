# Princeton IoT Inspector Client Software

## Mac

1. Download the app: https://iot-inspector.princeton.edu/downloads/inspector_mac.zip
2. Double-click on the downloaded zip file to uncompress it.
3. You'll see an uncompressed file, `start_inspector.app`.


## Ubuntu

Tested on Ubuntu 17.10 and 18.04.

### Installation

1. Download the installation script: `wget https://raw.githubusercontent.com/noise-lab/iot-inspector-client/master/ubuntu-install.sh`
2. Run the installation script: `bash ubuntu-install.sh`

### Running IoT Inspector

1. Enter IoT Inspector's director: `cd iot-inspector-client`
2. Start IoT Inspector: `bash ubuntu-start-inspector.sh`

Once you run `python start_inspector.py`, you will be prompted to enter your `sudo` password on the command line. At the same time, a browser window will appear that allows you to view the inspection report.

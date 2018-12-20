# Princeton IoT Inspector

IoT Inspector is a standalone desktop app that lets you analyze your home IoT devices. It allows you to determine

* who your IoT devices are communicating with
* when the communication happens
* how many bytes are sent and received over time

These features will help you identify potential problems, including

* security problems (e.g., your camera sending out lots of traffic even when you are not using it)
* privacy problems (e.g., your smart TV contacting advertising or tracking companies as you watch TV)
* performance problems (e.g., identifying who is using up the most bandwidth in your home network)

For details, see https://iot-inspector.princeton.edu/.

<br><br><br><br>

## Getting Started on Mac OS

Tested on macOS High Sierra.

### Installation

1. Download the app: https://iot-inspector.princeton.edu/downloads/inspector_mac.zip
2. Double-click on the downloaded zip file to uncompress it.
3. You'll see an uncompressed file, "start_inspector.app", as shown below:

<img src="https://iot-inspector.princeton.edu/static/instructions/mac/1.png" width="400" />

4. Right click on the file and click "Open" from the menu:

<img src="https://iot-inspector.princeton.edu/static/instructions/mac/2.png" width="400" />

5. Click the "Open" button on the dialog box:

<img src="https://iot-inspector.princeton.edu/static/instructions/mac/3.png" width="400" />

6. You'll be prompted to enter the admin password for IoT Inspector to work.

### Running IoT Inspector

Note that the next time you run IoT Inspector, you can simply double-click on the "start_inspector.app" icon (Step 3) while skipping Steps 4 and 5.

<br><br><br><br>

## Getting Started on Ubuntu

Tested on Ubuntu 17.10 and 18.04.

### Installation

1. Download the installation script: `wget https://raw.githubusercontent.com/noise-lab/iot-inspector-client/master/ubuntu-install.sh`
2. Run the installation script: `bash ubuntu-install.sh`

### Running IoT Inspector

1. Enter IoT Inspector's director: `cd iot-inspector-client`
2. Start IoT Inspector: `bash ubuntu-start-inspector.sh`

Once you run `python start_inspector.py`, you will be prompted to enter your `sudo` password on the command line. At the same time, a browser window will appear that allows you to view the inspection report.

<br><br><br><br>

## Getting Started on Windows

We are still working on a Windows 10 version. Stay tuned.

# IoT Inspector

IoT Inspector is a standalone desktop app that lets you analyze your home IoT devices. It allows you to determine

* who your IoT devices are communicating with
* when the communication happens
* how many bytes are sent and received over time

These features will help you identify potential problems on your home network, including

* security problems (e.g., your camera sending out lots of traffic even when you are not using it)
* privacy problems (e.g., your smart TV contacting advertising or tracking companies as you watch TV)
* performance problems (e.g., identifying who is using up the most bandwidth in your home network)

For details, see https://iotinspector.org.

# Running IoT Inspector

## Binaries

You can download the latest pre-compiled binaries from https://iotinspector.org.

## From source code

If you are uncomfortable executing our pre-compiled binaries (as some anti-virus products may flag IoT Inspector as malware), you can directly run IoT Inspector from the source code. After all, IoT Inspector is written in pure Python 3. 

### Linux and macOS

Make sure you have Python 3. Do the following from the command line:

```
$ git clone https://github.com/noise-lab/iot-inspector-client.git
$ cd iot-inspector-client/src
$ sudo su # Make sure that everything below is run as root
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ python start_inspector.py
```

If you're on Ubuntu 20, you might encounter an error where `Python.h` is not found. In this case, run the following before doing `pip install -r requirements.txt`:

```
sudo apt-get install python3-dev
```



### Windows 10 PowerShell or WSL

Make sure to first install [Npcap](https://nmap.org/dist/nmap-7.80-setup.exe). 

If you use the command line or PowerShell, make sure to open it using the Admin mode.

```
> git clone https://github.com/noise-lab/iot-inspector-client.git
> cd iot-inspector-client\src
> pip install -r requirements-windows.txt
> python start_inspector.py
```

If you're on WSL, do the following:

```
$ git clone https://github.com/noise-lab/iot-inspector-client.git
$ cd iot-inspector-client/src
$ pip install -r requirements-windows.txt
$ sudo python start_inspector.py
```


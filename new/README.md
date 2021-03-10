# New IoT Inspector

Home for the New IoT Inspector.

## Getting started

1. Set up a Python3 virtual environment.

    ```
    python3 -m venv env
    source env/bin/activate
    ```

2. Install the required packages.

    ```
    pip install -r requirements.txt
    ```

3. Develop in your favorite editor.

4. To test, you need to run as root. Do the following:

	```
	sudo su
	source env/bin/activate
	python start_inspector.py
	```
	
## Design	
	
The New IoT Inspector tool is designed to NOT share any user data with
the Internet. On its own, it is able to capture and analyze packets,
as well as presenting the traffic through a local HTTP server.
However, for more advanced features, users need to consent to IoT
Inspector sending certain data, for example, to identify devices or
destination hosts.



	
## Documentation for the API

We show two APIs in this section. 

- The first API is provided by the New IoT Inspector. It is only meant
  for the tool to visualize its traffic. This API is not public
  facing. An HTTP server listens on `localhost:45678` that provides
  the API, and another Flask thread would visualize the traffic
  obtained from the API.
  
- The second API is provided by the researchers. It is meant for the
  New IoT Inspector client to identify devices and destination
  hosts. This API is public facing, but users would have to provide
  consent.

### HTTP API built into the New IoT Inspector

This API is for visualizing the network traffic.

* `/is_ready`: Checks if IoT Inspector is ready to interface with the AR app.

* `/get_device_list`: Returns a list of devices and constantly changes.

* `/enable_inspection/<device_id>`: Instructs IoT Inspector to start collecting network traffic from a given `device_id`.

* `/get_traffic`: Returns network traffic from every inspected device between the last time you called this API and now.

* `/disable_inspection/<device_id>`: Instructs IoT Inspector to stop collecting network traffic from a given `device_id`.

* `/disable_all_inspection`: Stop collecting traffic for all devices.

* `/shutdown`: Stops inspecting all traffic and quits IoT Inspector Local.

* `/block_device/<device_id>/<start_unix_ts>/<stop_unix_ts>`: Sends wrong spoofed ARP packets to `device_id` (effectively blocking the device) between two UNIX timestamps (epoch). You can call this function multiple times to update the start and stop timestamps.

* `/unblock_device/<device_id>`: Unblocks that device.

* `/list_blocked_devices`: Shows a list of blocked `device_id`s.



### HTTP API provided by the researchers' IoT Inspector Server

This API is provided by the researchers and is meant to facilitate
device and destination identification.

* `/get_user_key`: Returns a unique user-key for subsequent operations
  (below).
  
* `/infer_device_identity`: Infers the identity of a device. Users
  need to `POST` the following parameters. With the exception of
  `user_key`, all parameters are optional.
  * `user_key`: string.
  * `oui`: Device OUI; string.
  * `hostnames`: A JSON-encoded list of hostnames that the device
    communicates with.
  * `netdisco`: A JSON-encoded string provided by Netdisco.
  * `dhcp_hostname`: A string.
  
* `/infer_dest_identity`:
Infers the identity of a device. Users
  need to `POST` the following parameters. With the exception of
  `user_key` and `ip`, all parameters are optional.
  * `user_key`: string.
  * `ip`: string; IP address that a device communicates with.
  * `hostname`: string; name of the host that the device communicates with.


# About

Problems? Email Prof. Danny Y. Huang at `dhuang@nyu.edu`.

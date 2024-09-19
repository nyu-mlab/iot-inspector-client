# Inspector for Hidden Device Detection

This is an experimental version with just the core functionalities of device
traffic capture and visualization. Meant to be easy to modify with additional
functionalities to detect hidden devices.

To test the core networking functionalities, run the following command on Bash:

`sudo rm user-data/inspector.log; sudo python -m core.start`

This will start the program and log the network traffic to
`user-data/inspector.log`. You can then manually examine the log file to see
what devices are ARP spoofed and what registered domain names each device is
communicating with.

For visualization, all network data is stored in memory in the following data
structures:

 * `core.global_state.outgoing_packet_counter_dict`, which counts the number of
   packets sent by each device. This data structure maps device_mac_addr -> {ts
   -> packet_count}

 * `core.global_state.outgoing_byte_counter_dict`, which counts the number of
   bytes sent by each device. This data structure maps device_mac_addr -> {ts
    -> byte_count}

 * `core.global_state.recent_hostnames_dict`, which stores the most recent
   domain names each device has communicated with. This data structure maps
   device_mac_addr -> {hostname -> ts}

To visualize the network traffic, run the following command on Bash:

``sudo rm -f user-data/inspector.log; ./start.bash``
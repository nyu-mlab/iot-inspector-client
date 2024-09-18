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

To visualize the network traffic, run the following command on Bash:

`TODO`
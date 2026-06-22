# inspector-go

a small Go rewrite of [IoT Inspector](https://github.com/nyu-mlab/iot-inspector-client).
It finds the devices on your network, optionally inspects one, and shows live
upload/download charts in a web dashboard. Everything stays on your machine.

## Build

Make sure to have the latest `go` first before running the build below; see https://go.dev/dl/.

```
go build -o inspector ./cmd/inspector
```

Needs libpcap: preinstalled on macOS, `apt install libpcap-dev` on Linux,
[Npcap](https://npcap.com) on Windows.

## Run

```
sudo ./inspector -serve :8080                       # discover devices → http://localhost:8080
sudo ./inspector -inspect all -serve :8080          # also capture traffic
sudo ./inspector -inspect <mac> -record dev.pcap    # save one device's packets to a pcap
./inspector -db live.db -browse                     # view a saved run (no root)
./inspector -pcap file.pcap -host-mac <mac>         # replay a capture offline
```

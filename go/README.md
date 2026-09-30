# inspector-go

a small Go rewrite of [IoT Inspector](https://github.com/nyu-mlab/iot-inspector-client).
It finds the devices on your network, optionally inspects one, and shows live
upload/download charts in a web dashboard. Everything stays on your machine.

## Download

No Go needed: run `start-go.bat` (Windows) or `./start-go.bash` (Mac/Linux) from
the repo root, or grab a binary from a `go-v*` [release](https://github.com/nyu-mlab/iot-inspector-client/releases)
and check it against `SHA256SUMS`. The macOS binary isn't notarized, so a
browser download is blocked by Gatekeeper until you run
`xattr -d com.apple.quarantine inspector-darwin-universal` (the launcher avoids this).

## Build

Requires Go 1.22 or newer (older toolchains will fail to build); get it from https://go.dev/dl/.

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

Add `-duration 10m` to stop cleanly after a set time, and `-version` to print the build.

## Releasing

Push a `go-v*` tag from master (e.g. `git tag go-v1.0.0 && git push upstream go-v1.0.0`).
The [go-release](../.github/workflows/go-release.yml) workflow builds Linux
(amd64/arm64, static libpcap), macOS (universal, 11+) and Windows (amd64)
binaries and publishes them with `SHA256SUMS`. The launchers pick up the newest
`go-v*` release automatically.

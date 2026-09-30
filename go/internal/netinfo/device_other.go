//go:build !windows

package netinfo

import "net"

// pcapDeviceName returns the name to hand pcap.OpenLive. On Unix the OS
// interface name (en0, wlan0) is also the pcap device name, so use it directly.
func pcapDeviceName(iface *net.Interface, _ net.IP) string {
	return iface.Name
}

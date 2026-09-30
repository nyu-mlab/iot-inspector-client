//go:build windows

package netinfo

import (
	"net"

	"github.com/google/gopacket/pcap"
)

// pcapDeviceName maps a Windows interface to its Npcap device name. Npcap opens
// devices by \Device\NPF_{GUID}, not the friendly name (Wi-Fi, Ethernet) that
// net.Interface reports, so match on the host IP the interface carries. Falls
// back to the friendly name if enumeration fails or nothing matches.
func pcapDeviceName(iface *net.Interface, hostIP net.IP) string {
	devs, err := pcap.FindAllDevs()
	if err != nil {
		return iface.Name
	}
	for _, dev := range devs {
		for _, addr := range dev.Addresses {
			if addr.IP.Equal(hostIP) {
				return dev.Name
			}
		}
	}
	return iface.Name
}

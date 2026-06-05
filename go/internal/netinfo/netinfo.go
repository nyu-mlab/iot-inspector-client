// Package netinfo discovers the active interface, host IP/MAC, subnet, and
// gateway, and toggles IP forwarding. Mirrors libinspector/networking.py.
package netinfo

import (
	"fmt"
	"net"
	"os/exec"
	"runtime"

	"github.com/jackpal/gateway"

	"github.com/nyu-mlab/inspector-go/internal/state"
)

// Discover fills in the interface, host IP/MAC, subnet, and gateway IP on s.
// The gateway MAC is learned later from ARP traffic, not here.
func Discover(s *state.State) error {
	gwIP, err := gateway.DiscoverGateway()
	if err != nil {
		return fmt.Errorf("find gateway: %w", err)
	}

	iface, hostIP, hostNet, err := ifaceForGateway(gwIP)
	if err != nil {
		return err
	}

	s.Iface = iface.Name
	s.HostIP = hostIP
	s.HostMAC = iface.HardwareAddr
	s.HostNet = hostNet
	s.GatewayIP = gwIP
	return nil
}

// ifaceForGateway returns the interface whose subnet contains the gateway,
// along with the host's IPv4 on that interface and the subnet.
func ifaceForGateway(gwIP net.IP) (*net.Interface, net.IP, *net.IPNet, error) {
	ifaces, err := net.Interfaces()
	if err != nil {
		return nil, nil, nil, err
	}
	for i := range ifaces {
		iface := ifaces[i]
		if iface.Flags&net.FlagUp == 0 || iface.Flags&net.FlagLoopback != 0 {
			continue
		}
		addrs, err := iface.Addrs()
		if err != nil {
			continue
		}
		for _, addr := range addrs {
			ipnet, ok := addr.(*net.IPNet)
			if !ok || ipnet.IP.To4() == nil {
				continue
			}
			if ipnet.Contains(gwIP) {
				return &iface, ipnet.IP.To4(), ipnet, nil
			}
		}
	}
	return nil, nil, nil, fmt.Errorf("no interface found on the gateway's subnet (%s)", gwIP)
}

// EnableIPForwarding lets traffic we intercept flow through to the gateway so
// devices keep working while inspected. Per-OS; mirrors networking.py.
//
// TODO: on macOS this requires SIP-compatible sysctl and may need a pf rule;
// validate on a current macOS before relying on it (see README platform notes).
func EnableIPForwarding() error { return setIPForwarding(true) }
func DisableIPForwarding() error { return setIPForwarding(false) }

func setIPForwarding(on bool) error {
	switch runtime.GOOS {
	case "darwin":
		v := "0"
		if on {
			v = "1"
		}
		return exec.Command("sysctl", "-w", "net.inet.ip.forwarding="+v).Run()
	case "linux":
		v := "0"
		if on {
			v = "1"
		}
		return exec.Command("sysctl", "-w", "net.ipv4.ip_forward="+v).Run()
	case "windows":
		// Set-NetIPInterface toggles routing on all interfaces at runtime, with no
		// reboot (unlike the IPEnableRouter registry key). UNTESTED on Windows —
		// validate before relying on it.
		state := "Disabled"
		if on {
			state = "Enabled"
		}
		return exec.Command("powershell", "-Command", "Set-NetIPInterface -Forwarding "+state).Run()
	default:
		return fmt.Errorf("unsupported OS: %s", runtime.GOOS)
	}
}

// Hosts returns every usable host IP in the subnet, for ARP sweeping.
func Hosts(n *net.IPNet) []net.IP {
	var out []net.IP
	ip := n.IP.Mask(n.Mask).To4()
	if ip == nil {
		return out
	}
	for cur := cloneIP(ip); n.Contains(cur); inc(cur) {
		out = append(out, cloneIP(cur))
	}
	// drop network and broadcast addresses
	if len(out) > 2 {
		out = out[1 : len(out)-1]
	}
	return out
}

func cloneIP(ip net.IP) net.IP {
	c := make(net.IP, len(ip))
	copy(c, ip)
	return c
}

func inc(ip net.IP) {
	for i := len(ip) - 1; i >= 0; i-- {
		ip[i]++
		if ip[i] != 0 {
			break
		}
	}
}

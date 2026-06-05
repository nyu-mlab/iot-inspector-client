// Package state holds the shared runtime state, mirroring libinspector's
// global_state.py but without the module-level globals: a single *State is
// created in main and passed explicitly to each component.
package state

import (
	"net"
	"sync"
	"sync/atomic"

	"github.com/google/gopacket/pcap"

	"github.com/nyu-mlab/inspector-go/internal/store"
	"github.com/nyu-mlab/inspector-go/internal/traffic"
)

type State struct {
	mu sync.RWMutex

	Iface      string
	HostIP     net.IP
	HostMAC    net.HardwareAddr
	HostNet    *net.IPNet // the host's subnet, used for ARP sweeps
	GatewayIP  net.IP
	gatewayMAC net.HardwareAddr

	// arpCache maps an IP string to the MAC we've observed for it, learned
	// from ARP traffic. Replaces networking.get_mac_address_from_ip().
	arpCache map[string]net.HardwareAddr

	Handle  *pcap.Handle
	Store   *store.Store
	Traffic *traffic.Buffer // full-resolution rolling window for live charts (nil in browse mode)

	running atomic.Bool
}

func New(st *store.Store) *State {
	return &State{
		arpCache: make(map[string]net.HardwareAddr),
		Store:    st,
	}
}

func (s *State) Running() bool      { return s.running.Load() }
func (s *State) SetRunning(v bool)  { s.running.Store(v) }

// LearnARP records an IP→MAC mapping observed on the wire.
func (s *State) LearnARP(ip net.IP, mac net.HardwareAddr) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.arpCache[ip.String()] = mac
}

// LookupMAC returns the MAC for an IP, or false if we haven't seen it.
func (s *State) LookupMAC(ip net.IP) (net.HardwareAddr, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	mac, ok := s.arpCache[ip.String()]
	return mac, ok
}

func (s *State) GatewayMAC() (net.HardwareAddr, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.gatewayMAC, s.gatewayMAC != nil
}

func (s *State) SetGatewayMAC(mac net.HardwareAddr) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.gatewayMAC = mac
}

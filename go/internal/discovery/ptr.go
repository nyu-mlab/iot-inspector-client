package discovery

import (
	"context"
	"log"
	"net"
	"strings"
	"sync"
	"time"

	"github.com/nyu-mlab/inspector-go/internal/state"
)

// ReverseDNS actively resolves a PTR (reverse-DNS) record for each discovered
// device IP that has no hostname yet, storing the result with source "ptr".
//
// This fills the gap left by passive DHCP (processor.processDHCP): leases renew
// every 10-30 min but participants run the tool for ~5-10 min, so the DHCP
// hostname often never appears. Mirrors the nmap PTR scrape in
// routersense-raspberrypi-client/shell_command_wrapper.py, but via
// net.LookupAddr so there's no nmap dependency.
func ReverseDNS(s *state.State) {
	ips, err := s.Store.DeviceIPsWithoutHostname()
	if err != nil {
		log.Printf("[ptr] list devices: %v", err)
		return
	}

	var wg sync.WaitGroup
	sem := make(chan struct{}, 8) // bound concurrent lookups
	for _, ip := range ips {
		wg.Add(1)
		sem <- struct{}{}
		go func(ip string) {
			defer wg.Done()
			defer func() { <-sem }()

			ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
			defer cancel()
			names, err := net.DefaultResolver.LookupAddr(ctx, ip)
			if err != nil || len(names) == 0 {
				return // no PTR record, common on LANs
			}
			name := strings.TrimSuffix(strings.ToLower(names[0]), ".")
			if name == "" {
				return
			}
			if err := s.Store.UpsertHostname(ip, name, "ptr"); err == nil {
				log.Printf("[ptr] %s: %s", ip, name)
			}
		}(ip)
	}
	wg.Wait()
}

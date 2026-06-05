// Package arpspoof handles both discovery (ARP sweep, arp_scanner.py) and the
// spoof loop (arp_spoof.py). Both just craft and send ARP frames on the wire;
// replies are learned passively by the processor.
package arpspoof

import (
	"log"
	"net"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcap"

	"github.com/nyu-mlab/inspector-go/internal/netinfo"
	"github.com/nyu-mlab/inspector-go/internal/state"
)

var serOpts = gopacket.SerializeOptions{FixLengths: true}

// maxSweepHostBits caps active scanning: subnets larger than this (/20, ~4094
// hosts) are not swept. Sweeping a /16 would blast tens of thousands of ARP
// requests — rude on a shared network and it overflows the send buffer. On big
// subnets we rely on passive discovery (the processor learns every MAC it sees).
const maxSweepHostBits = 12

// Scan sends an ARP request for each host in the subnet so devices reveal their
// MACs, paced to avoid flooding the send buffer. Run periodically.
func Scan(s *state.State) {
	if s.HostNet == nil {
		return
	}
	ones, bits := s.HostNet.Mask.Size()
	if bits-ones > maxSweepHostBits {
		log.Printf("[arp_scan] subnet /%d is too large to sweep; using passive discovery only", ones)
		return
	}
	for _, target := range netinfo.Hosts(s.HostNet) {
		if target.Equal(s.HostIP) {
			continue
		}
		req := buildARP(layers.ARPRequest, s.HostMAC, s.HostIP, broadcastMAC, target)
		if err := send(s.Handle, s.HostMAC, broadcastMAC, req); err != nil {
			log.Printf("[arp_scan] stopping sweep at %s: %v", target, err)
			return
		}
		time.Sleep(2 * time.Millisecond) // pace sends
	}
}

// Spoof sends, for each inspected device, the two poisoning replies: one tells
// the gateway "victim is at <host MAC>", one tells the victim "gateway is at
// <host MAC>". Mirrors arp_spoof.send_spoofed_arp.
func Spoof(s *state.State) {
	devices, err := s.Store.InspectedDevices()
	if err != nil {
		log.Printf("[arp_spoof] list devices: %v", err)
		return
	}
	gwMAC, ok := s.GatewayMAC()
	if !ok {
		log.Printf("[arp_spoof] gateway MAC unknown yet; skipping round")
		return
	}

	for _, d := range devices {
		victimIP := net.ParseIP(d.IP).To4()
		victimMAC, err := net.ParseMAC(d.MAC)
		if err != nil || victimIP == nil || victimIP.Equal(s.GatewayIP) {
			continue
		}
		// → gateway: "victimIP is at hostMAC"
		toGW := buildARP(layers.ARPReply, s.HostMAC, victimIP, gwMAC, s.GatewayIP)
		_ = send(s.Handle, s.HostMAC, gwMAC, toGW)
		// → victim: "gatewayIP is at hostMAC"
		toVictim := buildARP(layers.ARPReply, s.HostMAC, s.GatewayIP, victimMAC, victimIP)
		_ = send(s.Handle, s.HostMAC, victimMAC, toVictim)
	}
}

func buildARP(op uint16, srcMAC net.HardwareAddr, srcIP net.IP, dstMAC net.HardwareAddr, dstIP net.IP) *layers.ARP {
	return &layers.ARP{
		AddrType:          layers.LinkTypeEthernet,
		Protocol:          layers.EthernetTypeIPv4,
		HwAddressSize:     6,
		ProtAddressSize:   4,
		Operation:         op,
		SourceHwAddress:   srcMAC,
		SourceProtAddress: srcIP.To4(),
		DstHwAddress:      dstMAC,
		DstProtAddress:    dstIP.To4(),
	}
}

func send(h *pcap.Handle, srcMAC, dstMAC net.HardwareAddr, arp *layers.ARP) error {
	eth := &layers.Ethernet{SrcMAC: srcMAC, DstMAC: dstMAC, EthernetType: layers.EthernetTypeARP}
	buf := gopacket.NewSerializeBuffer()
	if err := gopacket.SerializeLayers(buf, serOpts, eth, arp); err != nil {
		return err
	}
	return h.WritePacketData(buf.Bytes())
}

var broadcastMAC = net.HardwareAddr{0xff, 0xff, 0xff, 0xff, 0xff, 0xff}

// Restore sends correct ARP mappings on shutdown so victims recover quickly
// instead of waiting for their caches to time out. Best-effort.
func Restore(s *state.State) {
	devices, err := s.Store.InspectedDevices()
	if err != nil {
		return
	}
	gwMAC, ok := s.GatewayMAC()
	if !ok {
		return
	}
	for _, d := range devices {
		victimIP := net.ParseIP(d.IP).To4()
		victimMAC, err := net.ParseMAC(d.MAC)
		if err != nil || victimIP == nil {
			continue
		}
		for i := 0; i < 3; i++ { // a few times, packets get lost
			_ = send(s.Handle, gwMAC, victimMAC, buildARP(layers.ARPReply, gwMAC, s.GatewayIP, victimMAC, victimIP))
			_ = send(s.Handle, victimMAC, gwMAC, buildARP(layers.ARPReply, victimMAC, victimIP, gwMAC, s.GatewayIP))
			time.Sleep(100 * time.Millisecond)
		}
	}
}

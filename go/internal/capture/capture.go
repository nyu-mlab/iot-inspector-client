// Package capture opens the live pcap handle and feeds packets to a channel.
// Mirrors libinspector/packet_collector.py: the only job here is to read frames
// off the wire; all parsing happens in the processor.
package capture

import (
	"fmt"
	"net"

	"github.com/google/gopacket"
	"github.com/google/gopacket/pcap"

	"github.com/nyu-mlab/inspector-go/internal/record"
	"github.com/nyu-mlab/inspector-go/internal/state"
)

const (
	snapLen     = 65536
	promiscuous = true
)

// Open creates the live capture handle on the active interface and stores it on
// s. The BPF filter keeps ARP (no IP layer) plus all IPv4 traffic that does not
// involve this host — so we never capture our own forwarded copies.
func Open(s *state.State) (*pcap.Handle, error) {
	handle, err := pcap.OpenLive(s.Iface, snapLen, promiscuous, pcap.BlockForever)
	if err != nil {
		return nil, fmt.Errorf("open %s: %w", s.Iface, err)
	}
	filter := fmt.Sprintf("arp or (ip and not host %s)", s.HostIP)
	if err := handle.SetBPFFilter(filter); err != nil {
		handle.Close()
		return nil, fmt.Errorf("set filter %q: %w", filter, err)
	}
	s.Handle = handle
	return handle, nil
}

// OpenOffline opens a pcap file for replay. No interface and no root required —
// this drives the exact same processor path as live capture, which makes it the
// safe way to test parsing without touching the network.
func OpenOffline(path string) (*pcap.Handle, error) {
	h, err := pcap.OpenOffline(path)
	if err != nil {
		return nil, fmt.Errorf("open pcap %s: %w", path, err)
	}
	return h, nil
}

// Run reads packets until the handle is closed, sending each to out. If rec is
// non-nil, it also records packets that involve an inspected device (src or dst
// MAC) — so -record produces just that device's traffic, not the whole segment's
// broadcast/multicast chatter. Returns when the source is exhausted (handle
// closed during shutdown, or end of a replayed file).
func Run(s *state.State, out chan<- gopacket.Packet, rec *record.Recorder) {
	handle := s.Handle
	src := gopacket.NewPacketSource(handle, handle.LinkType())
	for pkt := range src.Packets() {
		if rec != nil {
			recordIfInspected(s, rec, pkt)
		}
		out <- pkt
	}
	close(out)
}

// recordIfInspected writes the packet to the pcap only if either ethernet
// endpoint is an inspected device. Reads the MACs straight from the frame header
// (dst = bytes 0–6, src = 6–12) to avoid a full decode on the hot path.
func recordIfInspected(s *state.State, rec *record.Recorder, pkt gopacket.Packet) {
	data := pkt.Data()
	if len(data) < 12 {
		return
	}
	dst := net.HardwareAddr(data[0:6]).String()
	src := net.HardwareAddr(data[6:12]).String()
	if s.IsInspectedMAC(src) || s.IsInspectedMAC(dst) {
		rec.Write(pkt)
	}
}

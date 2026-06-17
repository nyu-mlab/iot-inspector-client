// Package record writes captured packets to a .pcap file at full fidelity —
// every packet with its real timestamp — so an inspected device's traffic can be
// analyzed offline at any resolution (the lossless research artifact, vs. the
// 1-second flow summary in SQLite). This is what the original IoT Inspector's
// study collected.
package record

import (
	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcapgo"
	"os"
)

type Recorder struct {
	f *os.File
	w *pcapgo.Writer
	n int
}

// New creates a pcap file with the given link type (use handle.LinkType()).
func New(path string, linkType layers.LinkType) (*Recorder, error) {
	f, err := os.Create(path)
	if err != nil {
		return nil, err
	}
	w := pcapgo.NewWriter(f)
	if err := w.WriteFileHeader(65536, linkType); err != nil {
		f.Close()
		return nil, err
	}
	return &Recorder{f: f, w: w}, nil
}

// Write appends one packet, preserving its capture timestamp. Nil-safe (so the
// caller can pass a nil *Recorder when recording is off) and called only from the
// single capture goroutine, so it needs no lock.
func (r *Recorder) Write(pkt gopacket.Packet) {
	if r == nil {
		return
	}
	if err := r.w.WritePacket(pkt.Metadata().CaptureInfo, pkt.Data()); err == nil {
		r.n++
	}
}

// Count returns how many packets have been written.
func (r *Recorder) Count() int {
	if r == nil {
		return 0
	}
	return r.n
}

func (r *Recorder) Close() error {
	if r == nil {
		return nil
	}
	return r.f.Close()
}

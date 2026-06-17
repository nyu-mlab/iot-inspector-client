package capture

import (
	"net"
	"path/filepath"
	"testing"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"

	"github.com/nyu-mlab/inspector-go/internal/record"
	"github.com/nyu-mlab/inspector-go/internal/state"
)

// regression test for issue #298: -record must capture only the inspected
// device's traffic, not every device on the segment.
func TestRecordIfInspected(t *testing.T) {
	s := state.New(nil)
	s.SetInspectedMACs([]string{"02:00:00:00:00:0a"})

	rec, err := record.New(filepath.Join(t.TempDir(), "t.pcap"), layers.LinkTypeEthernet)
	if err != nil {
		t.Fatal(err)
	}

	dev, _ := net.ParseMAC("02:00:00:00:00:0a")   // the inspected device
	other, _ := net.ParseMAC("02:00:00:00:00:bb") // some other device
	gw, _ := net.ParseMAC("02:00:00:00:00:fe")

	frame := func(src, dst net.HardwareAddr) gopacket.Packet {
		buf := gopacket.NewSerializeBuffer()
		_ = gopacket.SerializeLayers(buf, gopacket.SerializeOptions{},
			&layers.Ethernet{SrcMAC: src, DstMAC: dst, EthernetType: layers.EthernetTypeIPv4},
			gopacket.Payload([]byte{1, 2, 3, 4}))
		p := gopacket.NewPacket(buf.Bytes(), layers.LayerTypeEthernet, gopacket.Default)
		p.Metadata().CaptureInfo = gopacket.CaptureInfo{
			Timestamp: time.Unix(1, 0), CaptureLength: len(buf.Bytes()), Length: len(buf.Bytes()),
		}
		return p
	}

	recordIfInspected(s, rec, frame(dev, gw))   // src is inspected  -> record
	recordIfInspected(s, rec, frame(gw, dev))   // dst is inspected  -> record
	recordIfInspected(s, rec, frame(other, gw)) // neither           -> skip

	_ = rec.Close()
	if rec.Count() != 2 {
		t.Fatalf("recorded %d packets, want 2 (only the inspected device's)", rec.Count())
	}
}

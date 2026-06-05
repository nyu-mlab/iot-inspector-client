package record

import (
	"io"
	"net"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcapgo"
)

func TestRecorderRoundTrip(t *testing.T) {
	path := filepath.Join(t.TempDir(), "out.pcap")

	rec, err := New(path, layers.LinkTypeEthernet)
	if err != nil {
		t.Fatal(err)
	}

	// a minimal ethernet frame
	mac1, _ := net.ParseMAC("02:00:00:00:00:01")
	mac2, _ := net.ParseMAC("02:00:00:00:00:02")
	buf := gopacket.NewSerializeBuffer()
	if err := gopacket.SerializeLayers(buf, gopacket.SerializeOptions{},
		&layers.Ethernet{SrcMAC: mac1, DstMAC: mac2, EthernetType: layers.EthernetTypeIPv4},
		gopacket.Payload([]byte{1, 2, 3, 4})); err != nil {
		t.Fatal(err)
	}
	data := buf.Bytes()

	for i := 0; i < 3; i++ {
		pkt := gopacket.NewPacket(data, layers.LayerTypeEthernet, gopacket.Default)
		pkt.Metadata().CaptureInfo = gopacket.CaptureInfo{
			Timestamp: time.Unix(1_700_000_000+int64(i), 0), CaptureLength: len(data), Length: len(data),
		}
		rec.Write(pkt)
	}
	if rec.Count() != 3 {
		t.Fatalf("Count = %d, want 3", rec.Count())
	}
	if err := rec.Close(); err != nil {
		t.Fatal(err)
	}

	// read it back with the pure-Go pcapgo reader (no libpcap/Npcap runtime needed)
	f, err := os.Open(path)
	if err != nil {
		t.Fatalf("reopen: %v", err)
	}
	defer f.Close()
	r, err := pcapgo.NewReader(f)
	if err != nil {
		t.Fatalf("parse pcap: %v", err)
	}
	n := 0
	for {
		if _, _, err := r.ReadPacketData(); err == io.EOF {
			break
		} else if err != nil {
			t.Fatalf("read: %v", err)
		}
		n++
	}
	if n != 3 {
		t.Fatalf("read back %d packets, want 3", n)
	}
}

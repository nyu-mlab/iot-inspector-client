// Command genpcap writes a tiny synthetic capture from the inspector's
// man-in-the-middle vantage point, for testing the replay path without root.
//
// It models one IoT device (192.168.1.50) behind the inspector host
// (192.168.1.2), talking to the gateway (192.168.1.1) and out to a remote
// server, and includes: the device's and gateway's ARP announcements, a DHCP
// request carrying the device hostname, a DNS response, a real TLS ClientHello
// (device→host), and the forwarded flow frame (host→gateway).
package main

import (
	"crypto/tls"
	"log"
	"net"
	"os"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcapgo"
)

var (
	hostMAC, _   = net.ParseMAC("02:00:00:00:00:01")
	deviceMAC, _ = net.ParseMAC("02:00:00:00:00:0a")
	gwMAC, _     = net.ParseMAC("02:00:00:00:00:fe")
	bcastMAC, _  = net.ParseMAC("ff:ff:ff:ff:ff:ff")
	mcastMAC, _  = net.ParseMAC("01:00:5e:00:00:fb") // IPv4 mDNS multicast

	mdnsIP = net.ParseIP("224.0.0.251").To4()

	hostIP   = net.ParseIP("192.168.1.2").To4()
	deviceIP = net.ParseIP("192.168.1.50").To4()
	gwIP     = net.ParseIP("192.168.1.1").To4()
	remoteIP = net.ParseIP("93.184.216.34").To4()
	dnsIP    = net.ParseIP("8.8.8.8").To4()

	sni = "api.example.com"
)

func main() {
	out := "testdata/mitm-sample.pcap"
	if len(os.Args) > 1 {
		out = os.Args[1]
	}
	if err := os.MkdirAll("testdata", 0o755); err != nil {
		log.Fatal(err)
	}

	hello := clientHello(sni)
	frames := [][]byte{
		arpReply(deviceMAC, deviceIP, hostMAC, hostIP), // device announces itself → learned
		arpReply(gwMAC, gwIP, hostMAC, hostIP),         // gateway announces itself → tagged
		dhcpRequest(),                                  // device hostname "smart-cam"
		dnsResponse(),                                  // api.example.com → 93.184.216.34
		mdnsResponse(),                                 // device multicasts its service info
		// ClientHello arriving at the MITM (device→host): yields the SNI mapping.
		tcpFrame(deviceMAC, hostMAC, deviceIP, remoteIP, hello),
		// Forwarded copy (host→gateway): this is the frame that records the flow.
		tcpFrame(hostMAC, gwMAC, deviceIP, remoteIP, hello),
	}

	f, err := os.Create(out)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	w := pcapgo.NewWriter(f)
	if err := w.WriteFileHeader(65536, layers.LinkTypeEthernet); err != nil {
		log.Fatal(err)
	}
	for i, data := range frames {
		ci := gopacket.CaptureInfo{
			Timestamp:     time.Unix(1700000000+int64(i), 0),
			CaptureLength: len(data),
			Length:        len(data),
		}
		if err := w.WritePacket(ci, data); err != nil {
			log.Fatal(err)
		}
	}
	log.Printf("wrote %s (%d packets)", out, len(frames))
}

// clientHello returns the raw bytes of a real TLS ClientHello with the given SNI,
// produced by Go's own TLS stack over an in-memory pipe.
func clientHello(server string) []byte {
	c, s := net.Pipe()
	go func() {
		_ = tls.Client(c, &tls.Config{ServerName: server, InsecureSkipVerify: true}).Handshake()
	}()
	_ = s.SetReadDeadline(time.Now().Add(2 * time.Second))
	buf := make([]byte, 8192)
	n, err := s.Read(buf)
	c.Close()
	s.Close()
	if err != nil {
		log.Fatalf("capture ClientHello: %v", err)
	}
	return buf[:n]
}

func serialize(ls ...gopacket.SerializableLayer) []byte {
	buf := gopacket.NewSerializeBuffer()
	opts := gopacket.SerializeOptions{FixLengths: true, ComputeChecksums: true}
	if err := gopacket.SerializeLayers(buf, opts, ls...); err != nil {
		log.Fatal(err)
	}
	return buf.Bytes()
}

func arpReply(srcMAC net.HardwareAddr, srcIP net.IP, dstMAC net.HardwareAddr, dstIP net.IP) []byte {
	eth := &layers.Ethernet{SrcMAC: srcMAC, DstMAC: dstMAC, EthernetType: layers.EthernetTypeARP}
	arp := &layers.ARP{
		AddrType: layers.LinkTypeEthernet, Protocol: layers.EthernetTypeIPv4,
		HwAddressSize: 6, ProtAddressSize: 4, Operation: layers.ARPReply,
		SourceHwAddress: srcMAC, SourceProtAddress: srcIP,
		DstHwAddress: dstMAC, DstProtAddress: dstIP,
	}
	return serialize(eth, arp)
}

func dhcpRequest() []byte {
	eth := &layers.Ethernet{SrcMAC: deviceMAC, DstMAC: bcastMAC, EthernetType: layers.EthernetTypeIPv4}
	ip := &layers.IPv4{Version: 4, IHL: 5, TTL: 64, Protocol: layers.IPProtocolUDP,
		SrcIP: net.IPv4zero.To4(), DstIP: net.IPv4bcast.To4()}
	udp := &layers.UDP{SrcPort: 68, DstPort: 67}
	_ = udp.SetNetworkLayerForChecksum(ip)
	dhcp := &layers.DHCPv4{
		Operation: layers.DHCPOpRequest, HardwareType: layers.LinkTypeEthernet,
		HardwareLen: 6, Xid: 0x12345678, ClientHWAddr: deviceMAC,
		Options: layers.DHCPOptions{
			layers.NewDHCPOption(layers.DHCPOptMessageType, []byte{byte(layers.DHCPMsgTypeRequest)}),
			layers.NewDHCPOption(layers.DHCPOptHostname, []byte("smart-cam")),
			layers.NewDHCPOption(layers.DHCPOptEnd, nil),
		},
	}
	return serialize(eth, ip, udp, dhcp)
}

func dnsResponse() []byte {
	eth := &layers.Ethernet{SrcMAC: hostMAC, DstMAC: deviceMAC, EthernetType: layers.EthernetTypeIPv4}
	ip := &layers.IPv4{Version: 4, IHL: 5, TTL: 64, Protocol: layers.IPProtocolUDP, SrcIP: dnsIP, DstIP: deviceIP}
	udp := &layers.UDP{SrcPort: 53, DstPort: 40000}
	_ = udp.SetNetworkLayerForChecksum(ip)
	dns := &layers.DNS{
		ID: 0xABCD, QR: true, RD: true, RA: true,
		Questions: []layers.DNSQuestion{{Name: []byte(sni), Type: layers.DNSTypeA, Class: layers.DNSClassIN}},
		Answers: []layers.DNSResourceRecord{{
			Name: []byte(sni), Type: layers.DNSTypeA, Class: layers.DNSClassIN, TTL: 300, IP: remoteIP,
		}},
	}
	return serialize(eth, ip, udp, dns)
}

func mdnsResponse() []byte {
	eth := &layers.Ethernet{SrcMAC: deviceMAC, DstMAC: mcastMAC, EthernetType: layers.EthernetTypeIPv4}
	ip := &layers.IPv4{Version: 4, IHL: 5, TTL: 255, Protocol: layers.IPProtocolUDP, SrcIP: deviceIP, DstIP: mdnsIP}
	udp := &layers.UDP{SrcPort: 5353, DstPort: 5353}
	_ = udp.SetNetworkLayerForChecksum(ip)
	dns := &layers.DNS{
		QR: true, AA: true,
		Answers: []layers.DNSResourceRecord{
			{
				Name: []byte("_googlecast._tcp.local"), Type: layers.DNSTypePTR, Class: layers.DNSClassIN,
				TTL: 120, PTR: []byte("smart-cam._googlecast._tcp.local"),
			},
			{
				Name: []byte("smart-cam._googlecast._tcp.local"), Type: layers.DNSTypeTXT, Class: layers.DNSClassIN,
				TTL: 120, TXTs: [][]byte{[]byte("md=SmartCam"), []byte("fn=Living Room Cam")},
			},
		},
	}
	return serialize(eth, ip, udp, dns)
}

func tcpFrame(srcMAC, dstMAC net.HardwareAddr, srcIP, dstIP net.IP, payload []byte) []byte {
	eth := &layers.Ethernet{SrcMAC: srcMAC, DstMAC: dstMAC, EthernetType: layers.EthernetTypeIPv4}
	ip := &layers.IPv4{Version: 4, IHL: 5, TTL: 64, Protocol: layers.IPProtocolTCP, SrcIP: srcIP, DstIP: dstIP}
	tcp := &layers.TCP{SrcPort: 51000, DstPort: 443, PSH: true, ACK: true, Seq: 1, Window: 2057}
	_ = tcp.SetNetworkLayerForChecksum(ip)
	return serialize(eth, ip, tcp, gopacket.Payload(payload))
}

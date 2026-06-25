// Package processor parses each captured packet and writes the result to the
// store. It is a direct port of libinspector/packet_processor.py: a type-switch
// over layers, one handler per protocol, each doing a single DB upsert.
package processor

import (
	"log"
	"net"
	"strings"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"

	"github.com/nyu-mlab/inspector-go/internal/oui"
	"github.com/nyu-mlab/inspector-go/internal/state"
)

type Processor struct {
	st *state.State
}

func New(st *state.State) *Processor { return &Processor{st: st} }

// Run consumes packets until the channel closes.
func (p *Processor) Run(in <-chan gopacket.Packet) {
	for pkt := range in {
		if m := p.st.Metrics; m != nil {
			start := time.Now()
			p.handle(pkt)
			m.Processed(time.Since(start))
		} else {
			p.handle(pkt)
		}
	}
}

func (p *Processor) handle(pkt gopacket.Packet) {
	// ARP and DHCP are terminal (process_packet_helper).
	if arp := pkt.Layer(layers.LayerTypeARP); arp != nil {
		p.processARP(arp.(*layers.ARP))
		return
	}
	if dhcp := pkt.Layer(layers.LayerTypeDHCPv4); dhcp != nil {
		p.processDHCP(pkt, dhcp.(*layers.DHCPv4))
		return
	}

	eth, _ := pkt.Layer(layers.LayerTypeEthernet).(*layers.Ethernet)
	ip4, _ := pkt.Layer(layers.LayerTypeIPv4).(*layers.IPv4)
	if eth == nil || ip4 == nil {
		return
	}

	// mDNS (multicast DNS on UDP 5353). gopacket doesn't auto-decode this port as
	// DNS, and it's multicast so the host isn't an endpoint — handle it separately,
	// associating by source IP.
	if udp, ok := pkt.Layer(layers.LayerTypeUDP).(*layers.UDP); ok && (udp.SrcPort == 5353 || udp.DstPort == 5353) {
		p.processMDNS(ip4.SrcIP, udp.Payload)
		return
	}

	if dns := pkt.Layer(layers.LayerTypeDNS); dns != nil {
		p.processDNS(eth, dns.(*layers.DNS))
		return
	}

	// Flow-bearing packets: try SNI + HTTP UA, then record the flow.
	p.processClientHello(eth, ip4, pkt)
	p.processHTTPUserAgent(eth, pkt)
	p.processFlow(eth, ip4, pkt)
}

func (p *Processor) processARP(arp *layers.ARP) {
	if arp.Operation != layers.ARPRequest && arp.Operation != layers.ARPReply {
		return
	}
	srcMAC := net.HardwareAddr(arp.SourceHwAddress).String()
	srcIP := ipStr(arp.SourceProtAddress)
	if srcMAC == p.hostMAC() || srcIP == "0.0.0.0" {
		return
	}

	mac := arp.SourceHwAddress
	p.st.LearnARP(arp.SourceProtAddress, mac)

	isGateway := srcIP == p.st.GatewayIP.String()
	if isGateway {
		p.st.SetGatewayMAC(mac)
	}
	if err := p.st.Store.UpsertDeviceSeen(srcMAC, srcIP, isGateway); err != nil {
		log.Printf("[arp] upsert: %v", err)
		return
	}
	// Attach the OUI vendor once.
	if vendor := oui.Vendor(srcMAC); vendor != "" {
		_ = p.st.Store.MergeDeviceMetadata(srcMAC, srcIP, map[string]any{"oui_vendor": vendor})
	}
}

func (p *Processor) processDHCP(pkt gopacket.Packet, dhcp *layers.DHCPv4) {
	eth, _ := pkt.Layer(layers.LayerTypeEthernet).(*layers.Ethernet)
	if eth == nil || eth.DstMAC.String() != broadcast {
		return // only client→broadcast requests carry the hostname we want
	}
	var hostname string
	for _, opt := range dhcp.Options {
		if opt.Type == layers.DHCPOptHostname {
			hostname = string(opt.Data)
			break
		}
	}
	if hostname == "" {
		return
	}
	mac := eth.SrcMAC.String()
	if mac == p.hostMAC() {
		return
	}
	// A DHCP request carries 0.0.0.0 as the client IP (no lease yet); don't let
	// that overwrite a real IP learned from ARP. The hostname is what we want here.
	ip := ipStr(dhcp.ClientIP)
	if ip == "0.0.0.0" {
		ip = ""
	}
	_ = p.st.Store.MergeDeviceMetadata(mac, ip, map[string]any{"dhcp_hostname": hostname})
}

func (p *Processor) processDNS(eth *layers.Ethernet, dns *layers.DNS) {
	// Identify the LAN device on the non-host side of the conversation.
	deviceMAC := p.peerMAC(eth)
	if deviceMAC == "" {
		return
	}
	for _, q := range dns.Questions {
		hostname := strings.TrimSuffix(strings.ToLower(string(q.Name)), ".")
		if hostname == "" {
			continue
		}
		var ips []string
		for _, ans := range dns.Answers {
			if ans.Type == layers.DNSTypeA && ans.IP != nil {
				ips = append(ips, ans.IP.String())
			}
		}
		if len(ips) == 0 {
			ips = []string{""} // still record the queried domain
		}
		for _, ip := range ips {
			_ = p.st.Store.UpsertHostname(ip, hostname, "dns")
		}
	}
}

// processMDNS decodes an mDNS response payload and records the service name and
// TXT properties against the device at srcIP. This is the passive counterpart to
// libinspector's active zeroconf browse (mdns_discovery.py): we don't query, we
// just parse the announcements devices multicast on their own.
func (p *Processor) processMDNS(srcIP net.IP, payload []byte) {
	var dns layers.DNS
	if err := dns.DecodeFromBytes(payload, gopacket.NilDecodeFeedback); err != nil {
		return
	}
	if !dns.QR { // responses only
		return
	}

	props := map[string]string{}
	var name string
	records := append(append([]layers.DNSResourceRecord{}, dns.Answers...), dns.Additionals...)
	for _, rr := range records {
		switch rr.Type {
		case layers.DNSTypeTXT:
			for _, txt := range rr.TXTs {
				if k, v, ok := strings.Cut(string(txt), "="); ok && k != "" {
					props[k] = v
				}
			}
		case layers.DNSTypePTR:
			if name == "" {
				name = string(rr.PTR)
			}
		case layers.DNSTypeSRV:
			if name == "" {
				name = string(rr.Name)
			}
		}
	}
	if name == "" && len(props) == 0 {
		return
	}
	if added, err := p.st.Store.AppendMDNSByIP(srcIP.String(), name, props); err == nil && added {
		log.Printf("[mdns] %s: %s", srcIP, name)
	}
}

func (p *Processor) processClientHello(eth *layers.Ethernet, ip4 *layers.IPv4, pkt gopacket.Packet) {
	if eth.DstMAC.String() != p.hostMAC() {
		return // only client→server ClientHellos, redirected to us
	}
	tcp, _ := pkt.Layer(layers.LayerTypeTCP).(*layers.TCP)
	if tcp == nil || len(tcp.Payload) == 0 {
		return
	}
	deviceMAC := eth.SrcMAC.String()

	// JA3 fingerprint — useful for device/stack identification even when there's
	// no SNI. Collected as a deduplicated set per device.
	if ja3 := extractJA3(tcp.Payload); ja3 != "" {
		if added, err := p.st.Store.AppendDeviceStringSet(deviceMAC, "ja3", ja3); err == nil && added {
			log.Printf("[ja3] %s: %s", deviceMAC, ja3)
		}
	}

	if sni := extractSNI(tcp.Payload); sni != "" {
		_ = p.st.Store.UpsertHostname(ip4.DstIP.String(), strings.ToLower(sni), "sni")
	}
}

func (p *Processor) processHTTPUserAgent(eth *layers.Ethernet, pkt gopacket.Packet) {
	tcp, _ := pkt.Layer(layers.LayerTypeTCP).(*layers.TCP)
	if tcp == nil || (tcp.DstPort != 80 && tcp.DstPort != 8080) || len(tcp.Payload) == 0 {
		return
	}
	payload := string(tcp.Payload)
	if !strings.HasPrefix(payload, "GET ") && !strings.HasPrefix(payload, "POST ") {
		return
	}
	for _, line := range strings.Split(payload, "\r\n") {
		if ua, ok := strings.CutPrefix(line, "User-Agent: "); ok && ua != "" {
			_ = p.st.Store.MergeDeviceMetadata(eth.SrcMAC.String(), "", map[string]any{"user_agent_info": strings.TrimSpace(ua)})
			return
		}
	}
}

func (p *Processor) processFlow(eth *layers.Ethernet, ip4 *layers.IPv4, pkt gopacket.Packet) {
	var protocol string
	var srcPort, dstPort, tcpSeq int
	switch {
	case pkt.Layer(layers.LayerTypeTCP) != nil:
		tcp := pkt.Layer(layers.LayerTypeTCP).(*layers.TCP)
		protocol, srcPort, dstPort, tcpSeq = "tcp", int(tcp.SrcPort), int(tcp.DstPort), int(tcp.Seq)
	case pkt.Layer(layers.LayerTypeUDP) != nil:
		udp := pkt.Layer(layers.LayerTypeUDP).(*layers.UDP)
		protocol, srcPort, dstPort = "udp", int(udp.SrcPort), int(udp.DstPort)
	default:
		return
	}

	if eth.DstMAC.String() == broadcast || ip4.DstIP.String() == "255.255.255.255" {
		return
	}

	// We are the man-in-the-middle, so one side's MAC is ours. Rewrite it to the
	// real device's MAC (looked up from the ARP cache) before recording.
	srcMAC, dstMAC := eth.SrcMAC, eth.DstMAC
	switch p.hostMAC() {
	case srcMAC.String():
		mac, ok := p.st.LookupMAC(ip4.SrcIP)
		if !ok {
			return
		}
		srcMAC = mac
	case dstMAC.String():
		mac, ok := p.st.LookupMAC(ip4.DstIP)
		if !ok {
			return
		}
		dstMAC = mac
	default:
		return // neither side is us; not a flow we relayed
	}

	if m := p.st.Metrics; m != nil {
		start := time.Now()
		_ = p.st.Store.UpsertFlow(time.Now().Unix(),
			ip4.SrcIP.String(), ip4.DstIP.String(), srcMAC.String(), dstMAC.String(),
			srcPort, dstPort, protocol, len(pkt.Data()), tcpSeq)
		m.DB(time.Since(start))
	} else {
		_ = p.st.Store.UpsertFlow(time.Now().Unix(),
			ip4.SrcIP.String(), ip4.DstIP.String(), srcMAC.String(), dstMAC.String(),
			srcPort, dstPort, protocol, len(pkt.Data()), tcpSeq)
	}

	// Also record the packet at full resolution (its real capture time) for the
	// live charts, so they aren't limited to the 1-second flow buckets above.
	if p.st.Traffic != nil {
		ts := pkt.Metadata().Timestamp
		if ts.IsZero() {
			ts = time.Now()
		}
		p.st.Traffic.Add(ts.UnixNano(), srcMAC.String(), dstMAC.String(), len(pkt.Data()))
	}
}

// peerMAC returns the MAC of the non-host side of an Ethernet frame, or "" if
// this host is neither endpoint.
func (p *Processor) peerMAC(eth *layers.Ethernet) string {
	host := p.hostMAC()
	switch host {
	case eth.SrcMAC.String():
		return eth.DstMAC.String()
	case eth.DstMAC.String():
		return eth.SrcMAC.String()
	default:
		return ""
	}
}

func (p *Processor) hostMAC() string {
	if p.st.HostMAC == nil {
		return ""
	}
	return p.st.HostMAC.String()
}

const broadcast = "ff:ff:ff:ff:ff:ff"

// ipStr formats a raw 4-byte IPv4 address (ARP/DHCP fields carry net.IP already
// elsewhere, but ARP SourceProtAddress is a []byte).
func ipStr(b []byte) string {
	if len(b) != 4 {
		return ""
	}
	return net.IP(b).String()
}

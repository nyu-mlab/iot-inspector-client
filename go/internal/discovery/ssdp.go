// Package discovery does active service discovery. SSDP (this file) sends a
// UPnP M-SEARCH and records responders; mDNS is handled passively in the
// processor. Port of ssdp_discovery.py.
package discovery

import (
	"bufio"
	"encoding/xml"
	"io"
	"log"
	"net"
	"net/http"
	"strings"
	"time"

	"github.com/nyu-mlab/inspector-go/internal/state"
)

const ssdpAddr = "239.255.255.250:1900"

// msearch is the UPnP discovery datagram (ssdp:all). CRLF line endings and the
// trailing blank line are required by the protocol.
var msearch = []byte(strings.Join([]string{
	"M-SEARCH * HTTP/1.1",
	"HOST: 239.255.255.250:1900",
	`MAN: "ssdp:discover"`,
	"MX: 3",
	"ST: ssdp:all",
	"", "",
}, "\r\n"))

// SSDP sends one M-SEARCH and records responding devices (by source IP) until
// timeout. No root required. For each responder it stores the response headers
// and, when a LOCATION is present, the parsed device-description XML — matching
// ssdp_discovery.py's {ssdp_response_dict, location_contents} shape.
func SSDP(s *state.State, timeout time.Duration) {
	raddr, err := net.ResolveUDPAddr("udp4", ssdpAddr)
	if err != nil {
		return
	}
	conn, err := net.ListenUDP("udp4", &net.UDPAddr{IP: net.IPv4zero, Port: 0})
	if err != nil {
		log.Printf("[ssdp] listen: %v", err)
		return
	}
	defer conn.Close()

	if _, err := conn.WriteToUDP(msearch, raddr); err != nil {
		log.Printf("[ssdp] send: %v", err)
		return
	}
	_ = conn.SetReadDeadline(time.Now().Add(timeout))

	seen := map[string]bool{}
	buf := make([]byte, 4096)
	for {
		n, addr, err := conn.ReadFromUDP(buf)
		if err != nil {
			break // deadline reached
		}
		ip := addr.IP.String()
		if seen[ip] {
			continue
		}
		seen[ip] = true

		headers := parseSSDP(string(buf[:n]))
		if len(headers) == 0 {
			continue
		}
		entry := map[string]any{"ssdp_response_dict": headers}
		if loc := headers["LOCATION"]; loc != "" {
			if contents := fetchLocationXML(loc); contents != nil {
				entry["location_contents"] = contents
			}
		}
		if err := s.Store.MergeDeviceMetadataByIP(ip, map[string]any{"ssdp_json": entry}); err != nil {
			log.Printf("[ssdp] store %s: %v", ip, err)
		}
	}
}

// fetchLocationXML GETs a UPnP device-description URL and parses it into a nested
// map. Returns nil on any error (the headers alone are still useful).
func fetchLocationXML(url string) any {
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return nil
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil
	}
	body, err := io.ReadAll(io.LimitReader(resp.Body, 1<<20)) // cap at 1 MB
	if err != nil {
		return nil
	}
	var root xmlNode
	if err := xml.Unmarshal(body, &root); err != nil {
		return nil
	}
	return xmlToMap(root)
}

// xmlNode captures arbitrary XML for generic conversion.
type xmlNode struct {
	XMLName xml.Name
	Content string    `xml:",chardata"`
	Nodes   []xmlNode `xml:",any"`
}

// xmlToMap mirrors ssdp_discovery.xml_to_dict: leaf elements become their text,
// branches become {tag: {childTag: ...}} with XML namespaces stripped.
func xmlToMap(n xmlNode) any {
	tag := localName(n.XMLName)
	if len(n.Nodes) == 0 {
		return strings.TrimSpace(n.Content)
	}
	inner := map[string]any{}
	for _, c := range n.Nodes {
		inner[localName(c.XMLName)] = xmlToMap(c)
	}
	return map[string]any{tag: inner}
}

func localName(n xml.Name) string { return n.Local }

// parseSSDP turns an SSDP/HTTP response into a header map (keys uppercased).
func parseSSDP(resp string) map[string]string {
	h := map[string]string{}
	sc := bufio.NewScanner(strings.NewReader(resp))
	for sc.Scan() {
		line := sc.Text()
		if i := strings.Index(line, ": "); i > 0 {
			h[strings.ToUpper(line[:i])] = line[i+2:]
		}
	}
	return h
}

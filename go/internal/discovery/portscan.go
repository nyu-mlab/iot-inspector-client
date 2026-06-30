package discovery

import (
	"errors"
	"io"
	"log"
	"net"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/nyu-mlab/inspector-go/internal/state"
)

const (
	dialTimeout     = 1 * time.Second
	readTimeout     = 1500 * time.Millisecond
	probeLen        = 16 // null bytes sent when a service offers no banner
	scanConcurrency = 12 // bound concurrent connections per device
)

// popularPorts is a small, high-signal set for device identification: remote
// admin, web UIs, cameras, printers, IoT brokers, and streaming boxes. Kept
// short on purpose so discovery stays fast (issue #303). Trimmed from the v1
// tcp_scanner's ~250-port list.
var popularPorts = []int{
	22,   // ssh
	23,   // telnet
	53,   // dns
	80,   // http
	443,  // https
	445,  // smb
	554,  // rtsp (cameras)
	631,  // ipp (printers)
	1883, // mqtt
	5000, // upnp / various
	7547, // tr-069 (routers)
	8008, // chromecast
	8060, // roku
	8080, // http-alt
	8443, // https-alt
	8883, // mqtt over tls
	9100, // jetdirect (printers)
}

// PortScan probes the popular ports on each inspected device and records, per
// open port, either a passive banner (the service announced itself) or how it
// reacted to a null-byte probe (data / closed / no_response / reset). Findings
// go to device metadata under "port_scan". Short timeouts and bounded
// concurrency keep it fast. Scoped to inspected devices and opt-in (-port-scan),
// since it makes active connections. Port of the v1 banner_grabber + tcp_scanner.
func PortScan(s *state.State) {
	devices, err := s.Store.InspectedDevices()
	if err != nil {
		log.Printf("[portscan] list devices: %v", err)
		return
	}
	for _, d := range devices {
		findings := map[string]any{}
		var mu sync.Mutex
		var wg sync.WaitGroup
		sem := make(chan struct{}, scanConcurrency)
		for _, port := range popularPorts {
			wg.Add(1)
			sem <- struct{}{}
			go func(port int) {
				defer wg.Done()
				defer func() { <-sem }()
				if res, open := probePort(d.IP, port); open {
					mu.Lock()
					findings[strconv.Itoa(port)] = res
					mu.Unlock()
				}
			}(port)
		}
		wg.Wait()
		if len(findings) == 0 {
			continue
		}
		if err := s.Store.MergeDeviceMetadataByIP(d.IP, map[string]any{"port_scan": findings}); err == nil {
			log.Printf("[portscan] %s: %d open port(s)", d.IP, len(findings))
		}
	}
}

// probePort connects to ip:port and, if open, returns a finding: a passive
// banner if the service speaks first, otherwise the reaction to a null-byte
// probe. open is false when the port is closed, filtered, or unreachable.
func probePort(ip string, port int) (map[string]any, bool) {
	conn, err := net.DialTimeout("tcp", net.JoinHostPort(ip, strconv.Itoa(port)), dialTimeout)
	if err != nil {
		return nil, false
	}
	defer conn.Close()
	res := map[string]any{}
	buf := make([]byte, 512)

	// 1. passive banner: read without sending; some services announce themselves.
	// Any bytes count as a banner even if the read also returned EOF (a service
	// that speaks then immediately closes).
	_ = conn.SetReadDeadline(time.Now().Add(readTimeout))
	if n, _ := conn.Read(buf); n > 0 {
		res["banner"] = sanitize(buf[:n])
		return res, true
	}

	// 2. active probe: send null bytes, record how the service reacts. The
	// zero-probe behavior is itself a signal even when there's no readable banner.
	_ = conn.SetWriteDeadline(time.Now().Add(dialTimeout))
	if _, err := conn.Write(make([]byte, probeLen)); err != nil {
		res["probe"] = "write_failed"
		return res, true
	}
	_ = conn.SetReadDeadline(time.Now().Add(readTimeout))
	n, err := conn.Read(buf)
	switch {
	case n > 0:
		res["probe"] = sanitize(buf[:n])
	case errors.Is(err, io.EOF):
		res["probe"] = "closed"
	case isTimeout(err):
		res["probe"] = "no_response"
	case err != nil && strings.Contains(strings.ToLower(err.Error()), "reset"):
		res["probe"] = "reset"
	default:
		res["probe"] = "error"
	}
	return res, true
}

func isTimeout(err error) bool {
	var ne net.Error
	return errors.As(err, &ne) && ne.Timeout()
}

// sanitize keeps printable bytes only and caps length, so a hostile or binary
// banner can't bloat or corrupt the metadata JSON.
func sanitize(b []byte) string {
	var sb strings.Builder
	for _, c := range b {
		if c == '\n' || c == '\t' || (c >= 0x20 && c < 0x7f) {
			sb.WriteByte(c)
		}
		if sb.Len() >= 200 {
			break
		}
	}
	return strings.TrimSpace(sb.String())
}

// Package web serves a live dashboard from the SQLite data: a device list and a
// per-device drill-down (contacted domains, ports, bytes, fingerprints, and
// discovery metadata). Server-rendered HTML with a short auto-refresh — no JS
// framework, so it stays transparent and works while a capture is running.
package web

import (
	"encoding/json"
	"net/http"
	"sort"
	"strings"
	"time"

	"github.com/nyu-mlab/inspector-go/internal/store"
	"github.com/nyu-mlab/inspector-go/internal/summary"
	"github.com/nyu-mlab/inspector-go/internal/traffic"
)

// chartBins is the number of points per chart over the 60s window. 600 ≈ 100ms
// per point — finer than the ~580px chart can show, so it's effectively maximum
// useful resolution. The underlying buffer keeps every packet; this only sets how
// finely we bin for display.
const chartBins = 600

type Server struct {
	st *store.Store
	tb *traffic.Buffer // full-resolution source for charts; nil in browse mode
}

func New(st *store.Store, tb *traffic.Buffer) *Server { return &Server{st: st, tb: tb} }

// series returns upload/download byte series for a device. Live (a buffer is
// present) → full-resolution, binned at chartBins. Browse (no buffer) → the
// 1-second flow buckets from SQLite.
func (s *Server) series(mac string, nowUnix int64) (up, down []int64) {
	if s.tb != nil {
		return s.tb.Series(mac, nowUnix*1e9, chartBins)
	}
	u, d := s.st.TrafficSeries(mac, nowUnix)
	return u[:], d[:]
}

// Handler returns the dashboard's HTTP routes.
func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/", s.handleIndex)
	mux.HandleFunc("/device", s.handleDevice)
	mux.HandleFunc("/inspect", s.handleInspect)
	mux.HandleFunc("/label", s.handleLabel)
	mux.HandleFunc("/api/state", s.handleAPIState)
	return mux
}

// deviceSummary composes the plain-language blurb for a device from its facts
// (#308) — deterministic and local, no model.
func (s *Server) deviceSummary(mac string, m map[string]any) string {
	vendor := str(m["vendor_confirmed"])
	if vendor == "" {
		vendor = str(m["oui_vendor"])
	}
	typ := str(m["type_confirmed"])
	if typ == "" {
		typ = inferType(m)
	}
	return summary.Describe(displayName(m), vendor, typ, s.topHostnames(mac, 5), portList(m))
}

// topHostnames returns the device's most-contacted destinations by bytes.
func (s *Server) topHostnames(mac string, n int) []string {
	rows, err := s.st.DB().Query(`
		SELECT COALESCE(NULLIF(f.dest_hostname,''), h.hostname, f.dest_ip_address) AS host, SUM(f.byte_count) b
		FROM network_flows f
		LEFT JOIN hostnames h ON h.ip_address = f.dest_ip_address
		WHERE f.src_mac_address = ?
		GROUP BY host ORDER BY b DESC LIMIT ?`, mac, n)
	if err != nil {
		return nil
	}
	defer rows.Close()
	var out []string
	for rows.Next() {
		var h string
		var b int64
		if rows.Scan(&h, &b) == nil && h != "" {
			out = append(out, h)
		}
	}
	return out
}

// portList renders the port_scan metadata (#303, when present) as "port (banner)".
func portList(m map[string]any) []string {
	ps, ok := m["port_scan"].(map[string]any)
	if !ok {
		return nil
	}
	var out []string
	for port, v := range ps {
		if info, ok := v.(map[string]any); ok {
			if b := str(info["banner"]); b != "" {
				out = append(out, port+" ("+b+")")
				continue
			}
		}
		out = append(out, port)
	}
	return out
}

// labelFields are the user-confirmable metadata keys (vendor and device type are
// independent inferences, so each is confirmed/edited separately).
var labelFields = map[string]bool{"vendor_confirmed": true, "type_confirmed": true, "name": true}

// handleLabel persists a user's confirmation/correction of an inferred field.
func (s *Server) handleLabel(w http.ResponseWriter, r *http.Request) {
	mac := r.URL.Query().Get("mac")
	field := r.URL.Query().Get("field")
	value := r.URL.Query().Get("value")
	if mac == "" || !labelFields[field] {
		http.Error(w, "bad label request", 400)
		return
	}
	_ = s.st.MergeDeviceMetadata(mac, "", map[string]any{field: value})
	w.WriteHeader(http.StatusNoContent)
}

// apiDevice is one device row in the live JSON the dashboard polls.
type apiDevice struct {
	MAC       string  `json:"mac"`
	IP        string  `json:"ip"`
	Name      string  `json:"name"`
	Gateway   bool    `json:"gateway"`
	Inspected bool    `json:"inspected"`
	Contacts  int     `json:"contacts"`
	Bytes     int64   `json:"bytes"`
	Up        []int64 `json:"up"`
	Down      []int64 `json:"down"`
	// two independent inferences, each separately confirmable
	VendorInferred  string `json:"vendorInferred"`
	VendorConfirmed string `json:"vendorConfirmed"`
	TypeInferred    string `json:"typeInferred"`
	TypeConfirmed   string `json:"typeConfirmed"`
}

// handleAPIState returns the full dashboard state as JSON; the page polls this
// every ~1.5s and redraws in place, so charts update smoothly without reloading.
func (s *Server) handleAPIState(w http.ResponseWriter, r *http.Request) {
	now := time.Now().Unix()
	rows, err := s.st.DB().Query(`SELECT mac_address, ip_address, is_gateway, is_inspected, metadata_json FROM devices`)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	defer rows.Close()

	type raw struct {
		mac, ip   string
		gw, insp  int
		m         map[string]any
	}
	var raws []raw
	for rows.Next() {
		var mac, ip, meta string
		var gw, insp int
		if err := rows.Scan(&mac, &ip, &gw, &insp, &meta); err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		raws = append(raws, raw{mac, ip, gw, insp, parseMeta(meta)})
	}

	// Assign stable neutral letters (Device A, B, …) to non-gateway devices by
	// MAC order, so a device keeps its letter regardless of traffic-based sorting.
	letters := map[string]string{}
	var macs []string
	for _, r := range raws {
		if r.gw == 0 {
			macs = append(macs, r.mac)
		}
	}
	sort.Strings(macs)
	for i, mac := range macs {
		letters[mac] = "Device " + letterFor(i)
	}

	var list []apiDevice
	for _, r := range raws {
		up, down := s.series(r.mac, now)
		var total int64
		for i := range up {
			total += up[i] + down[i]
		}
		var contacts int
		_ = s.st.DB().QueryRow(`SELECT COUNT(DISTINCT dest_ip_address) FROM network_flows WHERE src_mac_address = ?`, r.mac).Scan(&contacts)

		typeConfirmed := str(r.m["type_confirmed"])
		// Prefer a user-set name, then a confirmed type, then the neutral letter.
		name := str(r.m["name"])
		if name == "" {
			name = typeConfirmed
		}
		if name == "" {
			name = letters[r.mac]
		}
		list = append(list, apiDevice{
			MAC: r.mac, IP: r.ip, Name: name,
			Gateway: r.gw == 1, Inspected: r.insp == 1, Contacts: contacts, Bytes: total,
			Up: up, Down: down,
			VendorInferred:  str(r.m["oui_vendor"]),
			VendorConfirmed: str(r.m["vendor_confirmed"]),
			TypeInferred:    inferType(r.m),
			TypeConfirmed:   typeConfirmed,
		})
	}
	// Display order: gateways last, then a stable order by MAC so cards never
	// jump around as traffic shifts (issue #304). Letters are assigned in this
	// same MAC order, so Device A stays first and new devices append in place.
	sort.Slice(list, func(i, j int) bool {
		if list[i].Gateway != list[j].Gateway {
			return list[j].Gateway
		}
		return list[i].MAC < list[j].MAC
	})

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]any{
		"devices":   len(list),
		"inspected": s.st.InspectedCount(),
		"dataUse":   s.st.BytesSince(now - 10),
		"list":      list,
	})
}

func (s *Server) handleIndex(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	// The page is a shell; it polls /api/state and renders/updates client-side.
	render(w, indexTmpl, nil)
}

// handleInspect toggles inspection for a device, then redirects back. The live
// spoof loop reads is_inspected periodically, so this starts/stops capture.
func (s *Server) handleInspect(w http.ResponseWriter, r *http.Request) {
	mac := r.URL.Query().Get("mac")
	on := r.URL.Query().Get("on") == "1"
	if mac != "" {
		_ = s.st.SetInspectedStatus(mac, on)
	}
	back := r.Header.Get("Referer")
	if back == "" {
		back = "/"
	}
	http.Redirect(w, r, back, http.StatusSeeOther)
}

type contact struct {
	Host     string
	Bytes    int64
	Packets  int64
	Ports    string
	Protocol string
}

func (s *Server) handleDevice(w http.ResponseWriter, r *http.Request) {
	mac := r.URL.Query().Get("mac")
	if mac == "" {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	var ip, meta string
	var gw, insp int
	err := s.st.DB().QueryRow(`SELECT ip_address, is_gateway, is_inspected, metadata_json FROM devices WHERE mac_address = ?`, mac).Scan(&ip, &gw, &insp, &meta)
	if err != nil {
		http.Error(w, "device not found", 404)
		return
	}
	m := parseMeta(meta)
	up, down := s.series(mac, time.Now().Unix())

	rows, err := s.st.DB().Query(`
		SELECT COALESCE(NULLIF(dest_hostname, ''), dest_ip_address) AS host,
		       SUM(byte_count), SUM(packet_count),
		       GROUP_CONCAT(DISTINCT dest_port), protocol
		FROM network_flows
		WHERE src_mac_address = ?
		GROUP BY host
		ORDER BY SUM(byte_count) DESC
		LIMIT 200`, mac)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	defer rows.Close()
	var contacts []contact
	for rows.Next() {
		var c contact
		if err := rows.Scan(&c.Host, &c.Bytes, &c.Packets, &c.Ports, &c.Protocol); err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		contacts = append(contacts, c)
	}

	render(w, deviceTmpl, map[string]any{
		"MAC":       mac,
		"IP":        ip,
		"IsGateway": gw == 1,
		"Inspected": insp == 1,
		"Name":      displayName(m),
		"Vendor":    str(m["oui_vendor"]),
		"DHCP":      str(m["dhcp_hostname"]),
		"UserAgent": str(m["user_agent_info"]),
		"JA3":       strList(m["ja3"]),
		"MDNS":      prettyJSON(m["mdns_json"]),
		"SSDP":      prettyJSON(m["ssdp_json"]),
		"Contacts":  contacts,
		"Upload":    lineChart(up, "↑ Upload Traffic (sent by device) — last 60s"),
		"Download":  lineChart(down, "↓ Download Traffic (received) — last 60s"),
		"Summary": s.deviceSummary(mac, m), // plain-language blurb (#308)
	})
}

// --- helpers ---

func parseMeta(s string) map[string]any {
	m := map[string]any{}
	_ = json.Unmarshal([]byte(s), &m)
	return m
}

// nameOnly returns a human-assigned name (DHCP hostname or a non-service mDNS
// name), or "" if none — vendor is intentionally excluded.
func nameOnly(m map[string]any) string {
	if v := str(m["dhcp_hostname"]); v != "" {
		return v
	}
	if list, ok := m["mdns_json"].([]any); ok {
		for _, e := range list {
			if em, ok := e.(map[string]any); ok {
				n := str(em["device_name"])
				if n != "" && !strings.HasPrefix(n, "_") && !strings.Contains(n, "@") {
					return strings.TrimSuffix(n, ".local")
				}
			}
		}
	}
	return ""
}

// deviceLabel is the card title: the device's name, or "Unnamed Device XX"
// (last MAC octet) when unknown — matching the original IoT Inspector.
func deviceLabel(m map[string]any, mac string) string {
	if n := nameOnly(m); n != "" {
		return n
	}
	h := strings.ReplaceAll(mac, ":", "")
	if len(h) >= 2 {
		return "Unnamed Device " + strings.ToUpper(h[len(h)-2:])
	}
	return "Unknown"
}

// displayName is nameOnly with an OUI-vendor fallback (used on the detail page).
func displayName(m map[string]any) string {
	if n := nameOnly(m); n != "" {
		return n
	}
	return str(m["oui_vendor"])
}

// inferType is a best-effort *guess* at the device category from mDNS service
// types and the DHCP hostname — a suggestion for the user to confirm or correct,
// not ground truth. Returns "" when we have no signal.
func inferType(m map[string]any) string {
	hint := strings.ToLower(str(m["dhcp_hostname"]))
	if list, ok := m["mdns_json"].([]any); ok {
		for _, e := range list {
			if em, ok := e.(map[string]any); ok {
				hint += " " + strings.ToLower(str(em["device_name"]))
			}
		}
	}
	switch {
	case strings.Contains(hint, "echo"), strings.Contains(hint, "alexa"), strings.Contains(hint, "_spotify"), strings.Contains(hint, "homepod"):
		return "smart speaker"
	case strings.Contains(hint, "roku"), strings.Contains(hint, "_googlecast"), strings.Contains(hint, "_airplay"), strings.Contains(hint, "chromecast"), strings.Contains(hint, "appletv"), strings.Contains(hint, "firetv"):
		return "media / TV"
	case strings.Contains(hint, "iphone"), strings.Contains(hint, "ipad"), strings.Contains(hint, "android"), strings.Contains(hint, "pixel"), strings.Contains(hint, "_apple-mobdev"):
		return "phone / tablet"
	case strings.Contains(hint, "cam"), strings.Contains(hint, "ring"), strings.Contains(hint, "nest"):
		return "camera"
	case strings.Contains(hint, "_printer"), strings.Contains(hint, "_ipp"):
		return "printer"
	}
	return ""
}

// letterFor maps 0,1,2,… to A,B,…,Z,AA,AB,… for neutral device labels.
func letterFor(i int) string {
	if i < 26 {
		return string(rune('A' + i))
	}
	return string(rune('A'+i/26-1)) + string(rune('A'+i%26))
}

func str(v any) string {
	s, _ := v.(string)
	return s
}

func strList(v any) []string {
	list, ok := v.([]any)
	if !ok {
		return nil
	}
	out := make([]string, 0, len(list))
	for _, e := range list {
		if s, ok := e.(string); ok {
			out = append(out, s)
		}
	}
	return out
}

func prettyJSON(v any) string {
	if v == nil {
		return ""
	}
	b, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return ""
	}
	return string(b)
}

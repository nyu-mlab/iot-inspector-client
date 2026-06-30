// Package store is the SQLite layer. Schema is identical to libinspector's
// mem_db.py / the documented IoT Inspector schema, so existing analysis code
// and the cloud upload format stay compatible.
//
// SQLite allows exactly one writer at a time; we serialize writes with a mutex
// and do metadata-JSON merges in Go (read-modify-write) rather than via SQL
// json_patch, which keeps the queries trivial and the behavior obvious.
package store

import (
	"database/sql"
	"encoding/json"
	"strconv"
	"time"

	_ "modernc.org/sqlite" // pure-Go driver, no CGo
)

const schema = `
CREATE TABLE IF NOT EXISTS devices (
    mac_address   TEXT PRIMARY KEY,
    ip_address    TEXT NOT NULL DEFAULT '',
    is_inspected  INTEGER DEFAULT 0,
    is_gateway    INTEGER DEFAULT 0,
    updated_ts    INTEGER DEFAULT 0,
    metadata_json TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS hostnames (
    ip_address    TEXT PRIMARY KEY,
    hostname      TEXT NOT NULL,
    updated_ts    INTEGER DEFAULT 0,
    data_source   TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS network_flows (
    timestamp        INTEGER,
    src_ip_address   TEXT,
    dest_ip_address  TEXT,
    src_hostname     TEXT,
    dest_hostname    TEXT,
    src_mac_address  TEXT,
    dest_mac_address TEXT,
    src_port         TEXT,
    dest_port        TEXT,
    protocol         TEXT,
    byte_count       INTEGER DEFAULT 0,
    packet_count     INTEGER DEFAULT 0,
    metadata_json    TEXT DEFAULT '{}',
    PRIMARY KEY (timestamp, src_mac_address, dest_mac_address,
                 src_ip_address, dest_ip_address, src_port, dest_port, protocol)
);
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);`

type Store struct {
	db *sql.DB
	mu chan struct{} // 1-slot semaphore serializing writes
}

func Open(path string) (*Store, error) {
	// WAL + busy_timeout via DSN (every pooled conn) so dashboard reads stop colliding with the capture writer and dropping flows.
	dsn := path + "?_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)&_pragma=synchronous(NORMAL)"
	db, err := sql.Open("sqlite", dsn)
	if err != nil {
		return nil, err
	}
	if _, err := db.Exec(schema); err != nil {
		return nil, err
	}
	return &Store{db: db, mu: make(chan struct{}, 1)}, nil
}

func (s *Store) DB() *sql.DB  { return s.db }
func (s *Store) Close() error { return s.db.Close() }

// shareConsentKey is the settings row that gates research data upload (#306).
// Absent or anything other than "true" means no consent — uploads never happen.
const shareConsentKey = "share_consent"

// SetSetting upserts a key/value into the settings table.
func (s *Store) SetSetting(key, value string) error {
	s.lock()
	defer s.unlock()
	_, err := s.db.Exec(`
		INSERT INTO settings (key, value) VALUES (?, ?)
		ON CONFLICT(key) DO UPDATE SET value = excluded.value`, key, value)
	return err
}

// GetSetting returns the value for key, or "" if it isn't set.
func (s *Store) GetSetting(key string) (string, error) {
	var v string
	err := s.db.QueryRow(`SELECT value FROM settings WHERE key = ?`, key).Scan(&v)
	if err == sql.ErrNoRows {
		return "", nil
	}
	return v, err
}

// ShareConsent reports whether the user has explicitly consented to uploading
// raw captures to the research team. Defaults to false (opt-in only).
func (s *Store) ShareConsent() bool {
	v, _ := s.GetSetting(shareConsentKey)
	return v == "true"
}

// SetShareConsent persists the user's consent decision.
func (s *Store) SetShareConsent(on bool) error {
	return s.SetSetting(shareConsentKey, strconv.FormatBool(on))
}

// ExportMetadata returns the parsed identification data (devices and hostnames)
// as JSON — the "metadata" half of the #306 upload payload that accompanies the
// raw pcap.
func (s *Store) ExportMetadata() ([]byte, error) {
	type device struct {
		MAC       string         `json:"mac"`
		IP        string         `json:"ip"`
		Gateway   bool           `json:"gateway"`
		Inspected bool           `json:"inspected"`
		Metadata  map[string]any `json:"metadata"`
	}
	out := struct {
		Devices   []device          `json:"devices"`
		Hostnames map[string]string `json:"hostnames"`
	}{Hostnames: map[string]string{}}

	dr, err := s.db.Query(`SELECT mac_address, ip_address, is_gateway, is_inspected, metadata_json FROM devices`)
	if err != nil {
		return nil, err
	}
	for dr.Next() {
		var d device
		var gw, insp int
		var meta string
		if err := dr.Scan(&d.MAC, &d.IP, &gw, &insp, &meta); err != nil {
			dr.Close()
			return nil, err
		}
		d.Gateway, d.Inspected = gw == 1, insp == 1
		d.Metadata = map[string]any{}
		_ = json.Unmarshal([]byte(meta), &d.Metadata)
		out.Devices = append(out.Devices, d)
	}
	dr.Close()
	if err := dr.Err(); err != nil {
		return nil, err
	}

	hr, err := s.db.Query(`SELECT ip_address, hostname FROM hostnames`)
	if err != nil {
		return nil, err
	}
	defer hr.Close()
	for hr.Next() {
		var ip, h string
		if err := hr.Scan(&ip, &h); err != nil {
			return nil, err
		}
		out.Hostnames[ip] = h
	}
	return json.MarshalIndent(out, "", "  ")
}

func (s *Store) lock()   { s.mu <- struct{}{} }
func (s *Store) unlock() { <-s.mu }

type Device struct {
	MAC      string
	IP       string
	Metadata map[string]any
}

// UpsertDeviceSeen records a MAC/IP and (re)sets the gateway flag — the path
// taken from observed ARP packets (packet_processor.process_arp).
func (s *Store) UpsertDeviceSeen(mac, ip string, isGateway bool) error {
	s.lock()
	defer s.unlock()
	_, err := s.db.Exec(`
		INSERT INTO devices (mac_address, ip_address, updated_ts, is_gateway)
		VALUES (?, ?, ?, ?)
		ON CONFLICT(mac_address) DO UPDATE SET
			ip_address = excluded.ip_address,
			updated_ts = excluded.updated_ts,
			is_gateway = excluded.is_gateway`,
		mac, ip, time.Now().Unix(), b2i(isGateway))
	return err
}

// MergeDeviceMetadata does a read-modify-write merge of a device's metadata_json.
// Creates the row (with the given IP) if absent. Used for OUI vendor, DHCP
// hostname, user-agent, mDNS/SSDP fields.
func (s *Store) MergeDeviceMetadata(mac, ip string, patch map[string]any) error {
	s.lock()
	defer s.unlock()

	var raw string
	err := s.db.QueryRow(`SELECT metadata_json FROM devices WHERE mac_address = ?`, mac).Scan(&raw)
	meta := map[string]any{}
	switch err {
	case nil:
		_ = json.Unmarshal([]byte(raw), &meta)
	case sql.ErrNoRows:
		// fall through; we'll insert below
	default:
		return err
	}
	for k, v := range patch {
		meta[k] = v
	}
	blob, _ := json.Marshal(meta)

	_, err = s.db.Exec(`
		INSERT INTO devices (mac_address, ip_address, updated_ts, metadata_json)
		VALUES (?, ?, ?, ?)
		ON CONFLICT(mac_address) DO UPDATE SET
			metadata_json = excluded.metadata_json,
			ip_address    = CASE WHEN excluded.ip_address != '' THEN excluded.ip_address ELSE devices.ip_address END,
			updated_ts    = excluded.updated_ts`,
		mac, ip, time.Now().Unix(), string(blob))
	return err
}

// MergeDeviceMetadataByIP merges a patch into the metadata of every device with
// the given IP. Used by SSDP/mDNS discovery, which identify devices by IP rather
// than MAC. If no device with that IP is known yet, it's a no-op (we can't create
// a device without its MAC).
func (s *Store) MergeDeviceMetadataByIP(ip string, patch map[string]any) error {
	s.lock()
	defer s.unlock()

	rows, err := s.db.Query(`SELECT mac_address, metadata_json FROM devices WHERE ip_address = ?`, ip)
	if err != nil {
		return err
	}
	type row struct{ mac, meta string }
	var found []row
	for rows.Next() {
		var r row
		if err := rows.Scan(&r.mac, &r.meta); err == nil {
			found = append(found, r)
		}
	}
	rows.Close()

	for _, r := range found {
		meta := map[string]any{}
		_ = json.Unmarshal([]byte(r.meta), &meta)
		for k, v := range patch {
			meta[k] = v
		}
		blob, _ := json.Marshal(meta)
		if _, err := s.db.Exec(`UPDATE devices SET metadata_json = ?, updated_ts = ? WHERE mac_address = ?`,
			string(blob), time.Now().Unix(), r.mac); err != nil {
			return err
		}
	}
	return nil
}

// AppendMDNSByIP appends an mDNS entry to the device's mdns_json list (keyed by
// IP), deduplicating on device_name so the list doesn't grow without bound.
// Returns true if something new was added.
func (s *Store) AppendMDNSByIP(ip, name string, props map[string]string) (bool, error) {
	s.lock()
	defer s.unlock()

	var mac, raw string
	err := s.db.QueryRow(`SELECT mac_address, metadata_json FROM devices WHERE ip_address = ?`, ip).Scan(&mac, &raw)
	if err == sql.ErrNoRows {
		return false, nil // device not known yet
	}
	if err != nil {
		return false, err
	}

	meta := map[string]any{}
	_ = json.Unmarshal([]byte(raw), &meta)

	var list []map[string]any
	if existing, ok := meta["mdns_json"].([]any); ok {
		for _, e := range existing {
			if m, ok := e.(map[string]any); ok {
				if m["device_name"] == name {
					return false, nil // already have this service
				}
				list = append(list, m)
			}
		}
	}
	list = append(list, map[string]any{"device_name": name, "device_properties": props})
	meta["mdns_json"] = list

	blob, _ := json.Marshal(meta)
	_, err = s.db.Exec(`UPDATE devices SET metadata_json = ?, updated_ts = ? WHERE mac_address = ?`,
		string(blob), time.Now().Unix(), mac)
	return err == nil, err
}

// UpsertHostname records an IP→hostname mapping (DNS answer or TLS SNI).
func (s *Store) UpsertHostname(ip, hostname, source string) error {
	s.lock()
	defer s.unlock()
	_, err := s.db.Exec(`
		INSERT INTO hostnames (ip_address, hostname, updated_ts, data_source)
		VALUES (?, ?, ?, ?)
		ON CONFLICT(ip_address) DO UPDATE SET
			hostname    = excluded.hostname,
			updated_ts  = excluded.updated_ts,
			data_source = excluded.data_source`,
		ip, hostname, time.Now().Unix(), source)
	return err
}

// DeviceIPsWithoutHostname lists discovered device IPs that have no hostname row
// yet, so active PTR lookup only queries what's still unknown and stops once an
// IP resolves.
func (s *Store) DeviceIPsWithoutHostname() ([]string, error) {
	rows, err := s.db.Query(`
		SELECT ip_address FROM devices
		WHERE ip_address != ''
		  AND ip_address NOT IN (SELECT ip_address FROM hostnames)`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []string
	for rows.Next() {
		var ip string
		if err := rows.Scan(&ip); err != nil {
			return nil, err
		}
		out = append(out, ip)
	}
	return out, rows.Err()
}

// UpsertFlow increments byte/packet counts for a 5-tuple flow in the current
// 1-second bucket, tracking min/max TCP sequence numbers in metadata (mirrors
// process_flow, including its tcp_seq_min/max — used to estimate bytes on wire).
// tcpSeq is 0 for UDP.
func (s *Store) UpsertFlow(ts int64, srcIP, dstIP, srcMAC, dstMAC string, srcPort, dstPort int, protocol string, bytes, tcpSeq int) error {
	s.lock()
	defer s.unlock()
	_, err := s.db.Exec(`
		INSERT INTO network_flows (
			timestamp, src_ip_address, dest_ip_address, src_mac_address, dest_mac_address,
			src_port, dest_port, protocol, byte_count, packet_count, metadata_json
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, json_object('tcp_seq_min', ?, 'tcp_seq_max', ?))
		ON CONFLICT (timestamp, src_mac_address, dest_mac_address, src_ip_address,
		             dest_ip_address, src_port, dest_port, protocol)
		DO UPDATE SET
			byte_count   = byte_count + excluded.byte_count,
			packet_count = packet_count + 1,
			metadata_json = json_object(
				'tcp_seq_min', MIN(CAST(json_extract(network_flows.metadata_json, '$.tcp_seq_min') AS INTEGER), ?),
				'tcp_seq_max', MAX(CAST(json_extract(network_flows.metadata_json, '$.tcp_seq_max') AS INTEGER), ?))`,
		ts, srcIP, dstIP, srcMAC, dstMAC, strconv.Itoa(srcPort), strconv.Itoa(dstPort), protocol, bytes, tcpSeq, tcpSeq, tcpSeq, tcpSeq)
	return err
}

// AppendDeviceStringSet appends val to a deduplicated string list stored under
// metadata[key] for the device with the given MAC (used for JA3 fingerprints).
// Returns true if val was newly added.
func (s *Store) AppendDeviceStringSet(mac, key, val string) (bool, error) {
	s.lock()
	defer s.unlock()

	var raw string
	err := s.db.QueryRow(`SELECT metadata_json FROM devices WHERE mac_address = ?`, mac).Scan(&raw)
	if err == sql.ErrNoRows {
		return false, nil
	}
	if err != nil {
		return false, err
	}

	meta := map[string]any{}
	_ = json.Unmarshal([]byte(raw), &meta)

	var list []string
	if existing, ok := meta[key].([]any); ok {
		for _, e := range existing {
			if s, ok := e.(string); ok {
				if s == val {
					return false, nil // already present
				}
				list = append(list, s)
			}
		}
	}
	list = append(list, val)
	meta[key] = list

	blob, _ := json.Marshal(meta)
	_, err = s.db.Exec(`UPDATE devices SET metadata_json = ?, updated_ts = ? WHERE mac_address = ?`,
		string(blob), time.Now().Unix(), mac)
	return err == nil, err
}

// BackfillFlowHostnames fills src/dest hostname columns from the hostnames
// table (process_processor.update_hostnames_in_flows), run periodically.
func (s *Store) BackfillFlowHostnames() (int64, error) {
	s.lock()
	defer s.unlock()
	res, err := s.db.Exec(`
		UPDATE network_flows SET
			src_hostname  = (SELECT hostname FROM hostnames WHERE ip_address = src_ip_address),
			dest_hostname = (SELECT hostname FROM hostnames WHERE ip_address = dest_ip_address)
		WHERE src_hostname IS NULL OR dest_hostname IS NULL`)
	if err != nil {
		return 0, err
	}
	return res.RowsAffected()
}

// TrafficSeries returns per-second byte totals for the last 60 seconds for a
// device: upload (sent by the device) and download (received). Index 0 is the
// current second, 59 is 60s ago — matching the original's right-to-left chart.
func (s *Store) TrafficSeries(mac string, now int64) (up, down [60]int64) {
	fill := func(col string) [60]int64 {
		var arr [60]int64
		// col is a fixed internal value, never user input.
		rows, err := s.db.Query(`
			SELECT (? - timestamp) AS ago, SUM(byte_count)
			FROM network_flows
			WHERE timestamp > ? - 60 AND `+col+` = ?
			GROUP BY ago`, now, now, mac)
		if err != nil {
			return arr
		}
		defer rows.Close()
		for rows.Next() {
			var ago, b int64
			if rows.Scan(&ago, &b) == nil && ago >= 0 && ago < 60 {
				arr[ago] = b
			}
		}
		return arr
	}
	return fill("src_mac_address"), fill("dest_mac_address")
}

// InspectedCount returns how many devices are currently being inspected.
func (s *Store) InspectedCount() int {
	var n int
	_ = s.db.QueryRow(`SELECT COUNT(*) FROM devices WHERE is_inspected = 1`).Scan(&n)
	return n
}

// BytesSince returns total flow bytes recorded at or after ts (for the data-use metric).
func (s *Store) BytesSince(ts int64) int64 {
	var n sql.NullInt64
	_ = s.db.QueryRow(`SELECT SUM(byte_count) FROM network_flows WHERE timestamp >= ?`, ts).Scan(&n)
	return n.Int64
}

// SetInspectedStatus turns inspection on or off for a device (used by the
// dashboard toggle; the live spoof loop picks up the change within ~10s).
func (s *Store) SetInspectedStatus(mac string, on bool) error {
	s.lock()
	defer s.unlock()
	_, err := s.db.Exec(`UPDATE devices SET is_inspected = ? WHERE mac_address = ? AND is_gateway = 0`, b2i(on), mac)
	return err
}

// SetInspected flags a single device (by MAC) for spoofing+capture.
func (s *Store) SetInspected(mac string) error {
	s.lock()
	defer s.unlock()
	_, err := s.db.Exec(`UPDATE devices SET is_inspected = 1 WHERE mac_address = ? AND is_gateway = 0`, mac)
	return err
}

// InspectAll flags every non-gateway device not already inspected, returning how
// many were newly flagged.
func (s *Store) InspectAll() (int64, error) {
	s.lock()
	defer s.unlock()
	res, err := s.db.Exec(`UPDATE devices SET is_inspected = 1 WHERE is_gateway = 0 AND is_inspected = 0`)
	if err != nil {
		return 0, err
	}
	return res.RowsAffected()
}

// InspectedMACs returns the MAC addresses currently flagged for inspection.
func (s *Store) InspectedMACs() ([]string, error) {
	rows, err := s.db.Query(`SELECT mac_address FROM devices WHERE is_inspected = 1`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []string
	for rows.Next() {
		var mac string
		if err := rows.Scan(&mac); err != nil {
			return nil, err
		}
		out = append(out, mac)
	}
	return out, rows.Err()
}

// ClearInspected unflags every device, so a fresh -inspect spec is authoritative
// rather than accumulating with whatever a previous run on this DB inspected.
func (s *Store) ClearInspected() error {
	s.lock()
	defer s.unlock()
	_, err := s.db.Exec(`UPDATE devices SET is_inspected = 0`)
	return err
}

// InspectedDevices returns devices flagged for spoofing (is_inspected=1, not gateway).
func (s *Store) InspectedDevices() ([]Device, error) {
	rows, err := s.db.Query(`
		SELECT mac_address, ip_address FROM devices
		WHERE is_inspected = 1 AND is_gateway = 0 AND ip_address != '' AND mac_address != ''`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []Device
	for rows.Next() {
		var d Device
		if err := rows.Scan(&d.MAC, &d.IP); err != nil {
			return nil, err
		}
		out = append(out, d)
	}
	return out, rows.Err()
}

func b2i(b bool) int {
	if b {
		return 1
	}
	return 0
}

package store

import (
	"path/filepath"
	"strings"
	"testing"
)

func TestUpsertsAndReport(t *testing.T) {
	st, err := Open(filepath.Join(t.TempDir(), "test.db"))
	if err != nil {
		t.Fatalf("open: %v", err)
	}
	defer st.Close()

	const mac = "aa:bb:cc:dd:ee:ff"

	if err := st.UpsertDeviceSeen(mac, "192.168.1.5", false); err != nil {
		t.Fatal(err)
	}
	// Two separate merges must accumulate, not overwrite each other.
	if err := st.MergeDeviceMetadata(mac, "192.168.1.5", map[string]any{"oui_vendor": "Apple"}); err != nil {
		t.Fatal(err)
	}
	if err := st.MergeDeviceMetadata(mac, "", map[string]any{"dhcp_hostname": "iphone"}); err != nil {
		t.Fatal(err)
	}

	var ip, meta string
	err = st.DB().QueryRow(`SELECT ip_address, metadata_json FROM devices WHERE mac_address=?`, mac).Scan(&ip, &meta)
	if err != nil {
		t.Fatal(err)
	}
	if ip != "192.168.1.5" {
		t.Errorf("ip = %q, want 192.168.1.5 (empty-IP merge must not clobber it)", ip)
	}
	if !strings.Contains(meta, "Apple") || !strings.Contains(meta, "iphone") {
		t.Errorf("metadata = %q, want both oui_vendor and dhcp_hostname", meta)
	}

	// Hostname + flow + backfill round-trip.
	if err := st.UpsertHostname("93.184.216.34", "example.com", "dns"); err != nil {
		t.Fatal(err)
	}
	if err := st.UpsertFlow(1000, "192.168.1.5", "93.184.216.34", mac, "gw", 51000, 443, "tcp", 1200, 5000); err != nil {
		t.Fatal(err)
	}
	if err := st.UpsertFlow(1000, "192.168.1.5", "93.184.216.34", mac, "gw", 51000, 443, "tcp", 800, 5400); err != nil {
		t.Fatal(err)
	}
	n, err := st.BackfillFlowHostnames()
	if err != nil {
		t.Fatal(err)
	}
	if n == 0 {
		t.Error("BackfillFlowHostnames updated 0 rows, want >=1")
	}

	var bytes, packets int
	var destHost string
	err = st.DB().QueryRow(`SELECT byte_count, packet_count, dest_hostname FROM network_flows`).Scan(&bytes, &packets, &destHost)
	if err != nil {
		t.Fatal(err)
	}
	if bytes != 2000 || packets != 2 {
		t.Errorf("flow aggregation = %d bytes / %d packets, want 2000 / 2", bytes, packets)
	}
	if destHost != "example.com" {
		t.Errorf("dest_hostname = %q, want example.com", destHost)
	}
}

func TestDeviceIPsWithoutHostname(t *testing.T) {
	st, err := Open(filepath.Join(t.TempDir(), "test.db"))
	if err != nil {
		t.Fatalf("open: %v", err)
	}
	defer st.Close()

	if err := st.UpsertDeviceSeen("aa:aa:aa:aa:aa:aa", "192.168.1.10", false); err != nil {
		t.Fatal(err)
	}
	if err := st.UpsertDeviceSeen("bb:bb:bb:bb:bb:bb", "192.168.1.11", false); err != nil {
		t.Fatal(err)
	}
	if err := st.UpsertDeviceSeen("cc:cc:cc:cc:cc:cc", "", false); err != nil {
		t.Fatal(err) // no IP yet -> must be excluded
	}

	// Both IP'd devices start without a hostname.
	ips, err := st.DeviceIPsWithoutHostname()
	if err != nil {
		t.Fatal(err)
	}
	if got := strings.Join(ips, ","); !strings.Contains(got, "192.168.1.10") || !strings.Contains(got, "192.168.1.11") || strings.Contains(got, ",,") || len(ips) != 2 {
		t.Errorf("ips = %v, want exactly the two IP'd devices", ips)
	}

	// Once one resolves, it drops out.
	if err := st.UpsertHostname("192.168.1.10", "router.lan", "ptr"); err != nil {
		t.Fatal(err)
	}
	ips, err = st.DeviceIPsWithoutHostname()
	if err != nil {
		t.Fatal(err)
	}
	if len(ips) != 1 || ips[0] != "192.168.1.11" {
		t.Errorf("ips = %v, want only 192.168.1.11", ips)
	}
}

func TestShareConsent(t *testing.T) {
	st, err := Open(filepath.Join(t.TempDir(), "test.db"))
	if err != nil {
		t.Fatalf("open: %v", err)
	}
	defer st.Close()

	if st.ShareConsent() {
		t.Fatal("consent must default to false (opt-in only)")
	}
	if err := st.SetShareConsent(true); err != nil {
		t.Fatal(err)
	}
	if !st.ShareConsent() {
		t.Error("consent should be true after opt-in")
	}
	if err := st.SetShareConsent(false); err != nil {
		t.Fatal(err)
	}
	if st.ShareConsent() {
		t.Error("consent should be false after opt-out")
	}
}

func TestExportMetadata(t *testing.T) {
	st, err := Open(filepath.Join(t.TempDir(), "test.db"))
	if err != nil {
		t.Fatalf("open: %v", err)
	}
	defer st.Close()

	_ = st.UpsertDeviceSeen("aa:aa:aa:aa:aa:aa", "192.168.1.9", false)
	_ = st.MergeDeviceMetadata("aa:aa:aa:aa:aa:aa", "", map[string]any{"oui_vendor": "Acme"})
	_ = st.UpsertHostname("93.184.216.34", "example.com", "dns")

	b, err := st.ExportMetadata()
	if err != nil {
		t.Fatal(err)
	}
	js := string(b)
	for _, want := range []string{"aa:aa:aa:aa:aa:aa", "Acme", "example.com", "192.168.1.9"} {
		if !strings.Contains(js, want) {
			t.Errorf("export metadata missing %q\n%s", want, js)
		}
	}
}

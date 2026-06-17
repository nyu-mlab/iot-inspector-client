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

package report

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/nyu-mlab/inspector-go/internal/store"
)

func TestGenerate(t *testing.T) {
	dir := t.TempDir()
	st, err := store.Open(filepath.Join(dir, "t.db"))
	if err != nil {
		t.Fatal(err)
	}
	defer st.Close()

	const camMAC, rokuMAC, gwMAC = "aa:aa:aa:00:00:01", "bb:bb:bb:00:00:01", "cc:cc:cc:00:00:fe"
	_ = st.UpsertDeviceSeen(camMAC, "192.168.1.10", false)
	_ = st.UpsertDeviceSeen(rokuMAC, "192.168.1.11", false)
	_ = st.UpsertDeviceSeen(gwMAC, "192.168.1.1", true) // gateway -> excluded
	_ = st.MergeDeviceMetadata(camMAC, "", map[string]any{"oui_vendor": "Acme", "dhcp_hostname": "front-cam"})
	_ = st.MergeDeviceMetadata(rokuMAC, "", map[string]any{"oui_vendor": "Roku"})

	// cam: 5 KB up to a known host, 20 KB down. roku: a little up.
	_ = st.UpsertHostname("93.184.216.34", "example.com", "dns")
	_ = st.UpsertFlow(1000, "192.168.1.10", "93.184.216.34", camMAC, gwMAC, 50000, 443, "tcp", 5000, 1)
	_ = st.UpsertFlow(1000, "93.184.216.34", "192.168.1.10", gwMAC, camMAC, 443, 50000, "tcp", 20000, 1)
	_ = st.UpsertFlow(1000, "192.168.1.11", "8.8.8.8", rokuMAC, gwMAC, 51000, 53, "udp", 200, 0)
	if _, err := st.BackfillFlowHostnames(); err != nil {
		t.Fatal(err)
	}

	path := filepath.Join(dir, "report.html")
	if err := Generate(st, path); err != nil {
		t.Fatal(err)
	}
	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	html := string(b)

	for _, want := range []string{
		"front-cam",   // friendly name from dhcp hostname
		"example.com", // top destination (hostname, not raw ip)
		"KB",          // human-readable bytes
		"Uploaded",    // up/down columns
		"Downloaded",
	} {
		if !strings.Contains(html, want) {
			t.Errorf("report missing %q", want)
		}
	}
	// The raw "Flows" column must be gone.
	if strings.Contains(html, ">Flows<") {
		t.Error("report still shows the raw Flows column")
	}
	// Gateway excluded.
	if strings.Contains(html, gwMAC) {
		t.Error("gateway should not appear in the report")
	}
	// cam (25 KB) should sort above roku (200 B).
	if strings.Index(html, "front-cam") > strings.Index(html, "Roku") {
		t.Error("devices not ordered by total bytes (cam should precede roku)")
	}
}

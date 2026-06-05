package oui

import (
	"strings"
	"testing"
)

func TestVendor(t *testing.T) {
	// substring matches against the real IEEE registry entries
	contains := map[string]string{
		"fc:fb:fb:11:22:33": "Cisco",
		"B8-27-EB-aa-bb-cc": "Raspberry Pi", // case + dash separators
	}
	for mac, want := range contains {
		if got := Vendor(mac); !strings.Contains(got, want) {
			t.Errorf("Vendor(%q) = %q, want it to contain %q", mac, got, want)
		}
	}

	empty := []string{
		"02:00:00:00:00:00", // locally administered, not in the registry
		"short",             // malformed
	}
	for _, mac := range empty {
		if got := Vendor(mac); got != "" {
			t.Errorf("Vendor(%q) = %q, want empty", mac, got)
		}
	}
}

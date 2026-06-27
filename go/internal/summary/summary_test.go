package summary

import (
	"strings"
	"testing"
)

func TestDescribe(t *testing.T) {
	got := Describe("front-cam", "Wyze", "camera", []string{"a.com", "b.com"}, []string{"443", "554"})
	for _, want := range []string{"front-cam", "camera", "Wyze", "a.com", "b.com", "2 open ports", "443", "554"} {
		if !strings.Contains(got, want) {
			t.Errorf("summary missing %q\n%s", want, got)
		}
	}

	// Only a vendor known.
	if g := Describe("Device A", "Acme", "", nil, nil); !strings.Contains(g, "made by Acme") {
		t.Errorf("vendor-only summary = %q", g)
	}
	// Nothing known but the name.
	if g := Describe("Device B", "", "", nil, nil); !strings.Contains(g, "unidentified") {
		t.Errorf("unknown summary = %q", g)
	}
	// Singular port grammar.
	if g := Describe("x", "", "camera", nil, []string{"443"}); !strings.Contains(g, "1 open port (") {
		t.Errorf("singular port grammar = %q", g)
	}
	// Caps hostnames at 3.
	g := Describe("x", "", "", []string{"1", "2", "3", "4", "5"}, nil)
	if strings.Contains(g, "4") || strings.Contains(g, "5") {
		t.Errorf("should cap hostnames at 3: %q", g)
	}
}

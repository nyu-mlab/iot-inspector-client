package main

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"

	"github.com/nyu-mlab/inspector-go/internal/store"
)

// The consent gate is the load-bearing safety control for #306: raw captures
// must never leave the machine unless the user explicitly opted in AND an
// endpoint is configured.
func TestMaybeUploadGate(t *testing.T) {
	var hits int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt32(&hits, 1)
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	dir := t.TempDir()
	st, err := store.Open(filepath.Join(dir, "t.db"))
	if err != nil {
		t.Fatal(err)
	}
	defer st.Close()
	pcap := filepath.Join(dir, "c.pcap")
	if err := os.WriteFile(pcap, []byte("rawpackets"), 0o644); err != nil {
		t.Fatal(err)
	}

	// Consent OFF (the default): must NOT upload, even with an endpoint set.
	maybeUploadCapture(st, pcap, srv.URL, "")
	if n := atomic.LoadInt32(&hits); n != 0 {
		t.Fatalf("uploaded without consent (hits=%d) — gate is broken", n)
	}

	// Consent ON + endpoint: uploads.
	if err := st.SetShareConsent(true); err != nil {
		t.Fatal(err)
	}
	maybeUploadCapture(st, pcap, srv.URL, "")
	if n := atomic.LoadInt32(&hits); n != 1 {
		t.Errorf("expected exactly one upload after consent, got %d", n)
	}

	// Consent ON but no endpoint configured: must NOT upload.
	atomic.StoreInt32(&hits, 0)
	maybeUploadCapture(st, pcap, "", "")
	if n := atomic.LoadInt32(&hits); n != 0 {
		t.Errorf("uploaded with no endpoint (hits=%d)", n)
	}
}

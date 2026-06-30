package collect

import (
	"context"
	"io"
	"mime"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// An empty endpoint must error without sending anything.
func TestUploadNoEndpoint(t *testing.T) {
	if err := New("", "").Upload(context.Background(), "x.pcap", []byte("{}")); err == nil {
		t.Fatal("expected error with empty endpoint, got nil (must never send)")
	}
}

// With an endpoint, the pcap and metadata arrive as multipart parts, with the key.
func TestUpload(t *testing.T) {
	pcap := filepath.Join(t.TempDir(), "cap.pcap")
	if err := os.WriteFile(pcap, []byte("\xd4\xc3\xb2\xa1rawpackets"), 0o644); err != nil {
		t.Fatal(err)
	}

	var gotPcap, gotMeta, gotKey string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotKey = r.Header.Get("x-api-key")
		_, params, _ := mime.ParseMediaType(r.Header.Get("Content-Type"))
		mr := multipart.NewReader(r.Body, params["boundary"])
		for {
			part, err := mr.NextPart()
			if err == io.EOF {
				break
			}
			if err != nil {
				t.Error(err)
				break
			}
			b, _ := io.ReadAll(part)
			switch part.FormName() {
			case "pcap":
				gotPcap = string(b)
			case "metadata":
				gotMeta = string(b)
			}
		}
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	if err := New(srv.URL, "secret").Upload(context.Background(), pcap, []byte(`{"devices":[]}`)); err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(gotPcap, "rawpackets") {
		t.Errorf("server did not receive the pcap bytes, got %q", gotPcap)
	}
	if gotMeta != `{"devices":[]}` {
		t.Errorf("metadata = %q, want the json blob", gotMeta)
	}
	if gotKey != "secret" {
		t.Errorf("x-api-key = %q, want secret", gotKey)
	}
}

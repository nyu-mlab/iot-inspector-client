package processor

import (
	"crypto/tls"
	"net"
	"testing"
	"time"
)

// TestExtractSNI feeds a *real* TLS ClientHello (produced by Go's own TLS stack)
// through extractSNI and checks we recover the server name. net.Pipe is
// synchronous, so the client's first flight (the ClientHello) lands in one Read.
func TestExtractSNI(t *testing.T) {
	client, server := net.Pipe()
	defer client.Close()
	defer server.Close()

	go func() {
		c := tls.Client(client, &tls.Config{ServerName: "example.com", InsecureSkipVerify: true})
		_ = c.Handshake() // sends ClientHello, then errors when we don't reply — fine
	}()

	_ = server.SetReadDeadline(time.Now().Add(2 * time.Second))
	buf := make([]byte, 4096)
	n, err := server.Read(buf)
	if err != nil {
		t.Fatalf("read ClientHello: %v", err)
	}

	if got := extractSNI(buf[:n]); got != "example.com" {
		t.Fatalf("extractSNI = %q, want %q", got, "example.com")
	}
}

func TestExtractSNI_NotTLS(t *testing.T) {
	if got := extractSNI([]byte("GET / HTTP/1.1\r\n")); got != "" {
		t.Fatalf("extractSNI on non-TLS = %q, want empty", got)
	}
}

package processor

import (
	"crypto/tls"
	"net"
	"regexp"
	"testing"
	"time"
)

var hexMD5 = regexp.MustCompile(`^[0-9a-f]{32}$`)

func TestExtractJA3(t *testing.T) {
	hello := grabClientHello(t)

	got := extractJA3(hello)
	if !hexMD5.MatchString(got) {
		t.Fatalf("extractJA3 = %q, want a 32-char hex md5", got)
	}
	// Deterministic for the same ClientHello bytes.
	if again := extractJA3(hello); again != got {
		t.Fatalf("extractJA3 not stable: %q != %q", got, again)
	}
}

func TestExtractJA3_NotTLS(t *testing.T) {
	if got := extractJA3([]byte("not a tls record")); got != "" {
		t.Fatalf("extractJA3 on junk = %q, want empty", got)
	}
}

func TestIsGREASE(t *testing.T) {
	if !isGREASE(0x0a0a) || !isGREASE(0xfafa) {
		t.Error("GREASE values not detected")
	}
	if isGREASE(0x1301) { // a real TLS 1.3 cipher
		t.Error("real cipher flagged as GREASE")
	}
}

// grabClientHello returns the raw bytes of a real ClientHello via an in-memory pipe.
func grabClientHello(t *testing.T) []byte {
	t.Helper()
	client, server := net.Pipe()
	defer client.Close()
	defer server.Close()
	go func() {
		_ = tls.Client(client, &tls.Config{ServerName: "example.com", InsecureSkipVerify: true}).Handshake()
	}()
	_ = server.SetReadDeadline(time.Now().Add(2 * time.Second))
	buf := make([]byte, 4096)
	n, err := server.Read(buf)
	if err != nil {
		t.Fatalf("read ClientHello: %v", err)
	}
	return buf[:n]
}

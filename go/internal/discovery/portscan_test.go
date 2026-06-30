package discovery

import (
	"net"
	"strconv"
	"strings"
	"testing"
)

func listenerPort(t *testing.T, ln net.Listener) int {
	t.Helper()
	_, p, err := net.SplitHostPort(ln.Addr().String())
	if err != nil {
		t.Fatal(err)
	}
	port, _ := strconv.Atoi(p)
	return port
}

// A service that speaks first is captured as a passive banner.
func TestProbePortBanner(t *testing.T) {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer ln.Close()
	go func() {
		c, err := ln.Accept()
		if err != nil {
			return
		}
		_, _ = c.Write([]byte("SSH-2.0-OpenSSH_test\r\n"))
		c.Close()
	}()

	res, open := probePort("127.0.0.1", listenerPort(t, ln))
	if !open {
		t.Fatal("expected open port")
	}
	if b, _ := res["banner"].(string); !strings.Contains(b, "SSH-2.0-OpenSSH_test") {
		t.Errorf("banner = %v, want the SSH banner", res["banner"])
	}
}

// A silent service that closes after the null probe reads as "closed".
func TestProbePortActiveClose(t *testing.T) {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer ln.Close()
	go func() {
		c, err := ln.Accept()
		if err != nil {
			return
		}
		_, _ = c.Read(make([]byte, probeLen)) // read the probe, send nothing
		c.Close()
	}()

	res, open := probePort("127.0.0.1", listenerPort(t, ln))
	if !open {
		t.Fatal("expected open port")
	}
	if res["banner"] != nil {
		t.Errorf("did not expect a banner, got %v", res["banner"])
	}
	if res["probe"] != "closed" {
		t.Errorf("probe = %v, want closed", res["probe"])
	}
}

// A port with nothing listening is reported closed.
func TestProbePortClosed(t *testing.T) {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	port := listenerPort(t, ln)
	ln.Close() // free the port so the dial is refused

	if _, open := probePort("127.0.0.1", port); open {
		t.Error("expected closed port to report not-open")
	}
}

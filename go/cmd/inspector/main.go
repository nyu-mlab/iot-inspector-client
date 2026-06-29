// Command inspector is the offline IoT Inspector capture engine. It discovers
// devices on the LAN, ARP-spoofs the ones flagged for inspection, captures and
// parses their traffic into SQLite, and writes an HTML report on exit.
//
// Lifecycle mirrors libinspector/core.py: discover network → enable forwarding
// → start the capture/processor/scan/spoof loops → block until Ctrl-C → clean up.
//
// With -pcap, it instead replays a capture file through the identical processor
// path (no root, no network) — the safe way to test parsing.
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"runtime"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/google/gopacket"

	"github.com/nyu-mlab/inspector-go/internal/arpspoof"
	"github.com/nyu-mlab/inspector-go/internal/capture"
	"github.com/nyu-mlab/inspector-go/internal/discovery"
	"github.com/nyu-mlab/inspector-go/internal/netinfo"
	"github.com/nyu-mlab/inspector-go/internal/processor"
	"github.com/nyu-mlab/inspector-go/internal/record"
	"github.com/nyu-mlab/inspector-go/internal/report"
	"github.com/nyu-mlab/inspector-go/internal/state"
	"github.com/nyu-mlab/inspector-go/internal/store"
	"github.com/nyu-mlab/inspector-go/internal/traffic"
	"github.com/nyu-mlab/inspector-go/internal/web"
)

func main() {
	dbPath := flag.String("db", "inspector.db", "SQLite database path")
	reportPath := flag.String("report", "report.html", "HTML report written on exit")
	pcapFile := flag.String("pcap", "", "replay packets from this pcap file instead of live capture (no root)")
	hostMAC := flag.String("host-mac", "", "replay: MAC of the inspector/MITM host (the side traffic is relayed through)")
	hostIP := flag.String("host-ip", "", "replay: IP of the inspector host")
	gatewayIP := flag.String("gateway-ip", "", "replay: gateway IP (used to tag the gateway device)")
	inspect := flag.String("inspect", "", "live: MAC(s) to inspect (spoof+capture), comma-separated, or 'all'")
	serve := flag.String("serve", "", "serve the live web dashboard at this address (e.g. :8080)")
	browse := flag.Bool("browse", false, "view an existing -db in the dashboard without capturing (no root)")
	record := flag.String("record", "", "live: write every captured packet to this .pcap file (full-fidelity research artifact)")
	openReport := flag.Bool("open", true, "open the HTML report in a browser when it's written")
	flag.Parse()

	st, err := store.Open(*dbPath)
	if err != nil {
		log.Fatalf("open db: %v", err)
	}
	defer st.Close()

	s := state.New(st)

	switch {
	case *browse:
		runBrowse(s, *serve)
		return // browse blocks until Ctrl-C; no report on exit
	case *pcapFile != "":
		if err := runReplay(s, *pcapFile, *hostMAC, *hostIP, *gatewayIP); err != nil {
			log.Fatalf("replay: %v", err)
		}
	default:
		if err := runLive(s, *inspect, *serve, *record); err != nil {
			log.Fatalf("%v", err)
		}
	}

	if err := report.Generate(st, *reportPath); err != nil {
		log.Printf("report: %v", err)
	} else {
		log.Printf("wrote %s", *reportPath)
		if *openReport {
			openInBrowser(*reportPath)
		}
	}
}

// runReplay drives the processor over a pcap file. Because the live processor
// keys off the host MAC (this host is the man-in-the-middle), -host-mac should
// match the inspector host that captured the file; otherwise flow/SNI/DNS
// handlers that require the host as an endpoint stay quiet.
func runReplay(s *state.State, file, hostMAC, hostIP, gatewayIP string) error {
	if hostMAC != "" {
		mac, err := net.ParseMAC(hostMAC)
		if err != nil {
			return fmt.Errorf("bad -host-mac: %w", err)
		}
		s.HostMAC = mac
	}
	if hostIP != "" {
		s.HostIP = net.ParseIP(hostIP)
	}
	if gatewayIP != "" {
		s.GatewayIP = net.ParseIP(gatewayIP)
	}

	handle, err := capture.OpenOffline(file)
	if err != nil {
		return err
	}
	defer handle.Close()
	s.Handle = handle
	s.SetRunning(true)

	packets := make(chan gopacket.Packet, 1024)
	proc := processor.New(s)
	done := make(chan struct{})
	go func() { proc.Run(packets); close(done) }()

	capture.Run(s, packets, nil) // reads the whole file, then closes `packets`
	<-done

	if n, err := s.Store.BackfillFlowHostnames(); err == nil {
		log.Printf("[replay] done; filled %d flow rows with hostnames", n)
	}
	return nil
}

// runLive is the production path: discover, spoof, capture until Ctrl-C.
// inspect selects which devices to spoof+capture: "" (none, discovery only),
// "all", or a comma-separated MAC list.
func runLive(s *state.State, inspect, serveAddr, recordPath string) error {
	if os.Geteuid() != 0 {
		return fmt.Errorf("must run as root/admin (raw packet send + IP forwarding); use -pcap to replay a file without root")
	}

	// Full-resolution rolling window (last 60s) for the live charts, capped at
	// 500k samples (~tens of MB) so a traffic flood can't exhaust memory.
	s.Traffic = traffic.New(60*time.Second, 500_000)

	if serveAddr != "" {
		startWebServer(s, serveAddr)
	}

	if err := netinfo.Discover(s); err != nil {
		return fmt.Errorf("discover network: %w", err)
	}
	log.Printf("iface=%s host=%s gateway=%s", s.Iface, s.HostIP, s.GatewayIP)

	if err := netinfo.EnableIPForwarding(); err != nil {
		log.Printf("warning: could not enable IP forwarding: %v (devices may lose connectivity while inspected)", err)
	}

	handle, err := capture.Open(s)
	if err != nil {
		return fmt.Errorf("open capture: %w", err)
	}
	s.SetRunning(true)

	// Optional full-fidelity pcap recording of everything we capture.
	var rec *record.Recorder
	if recordPath != "" {
		rec, err = record.New(recordPath, handle.LinkType())
		if err != nil {
			return fmt.Errorf("open record file: %w", err)
		}
		log.Printf("recording captured packets to %s", recordPath)
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	packets := make(chan gopacket.Packet, 1024)
	proc := processor.New(s)

	var wg sync.WaitGroup
	wg.Add(2)
	go func() { defer wg.Done(); capture.Run(s, packets, rec) }() // closes `packets` when handle closes
	go func() { defer wg.Done(); proc.Run(packets) }()

	// Periodic background loops (core.py's SafeLoopThreads).
	go loop(ctx, 10*time.Second, func() { arpspoof.Scan(s) })
	go loop(ctx, 10*time.Second, func() { arpspoof.Spoof(s) })
	go loop(ctx, 120*time.Second, func() {
		if n, err := s.Store.BackfillFlowHostnames(); err == nil && n > 0 {
			log.Printf("[hostnames] filled %d flow rows", n)
		}
	})
	// Active SSDP discovery (mDNS is handled passively in the processor).
	go loop(ctx, 60*time.Second, func() { discovery.SSDP(s, 10*time.Second) })
	if inspect != "" {
		// Make -inspect authoritative: drop any inspection left over in this DB
		// from a previous run, so we spoof/record exactly what was asked for.
		if err := s.Store.ClearInspected(); err != nil {
			log.Printf("warning: could not reset prior inspection state: %v", err)
		}
		go loop(ctx, 5*time.Second, func() { applyInspect(s, inspect) })
	} else {
		log.Println("discovery-only (no -inspect): devices will be listed but not spoofed")
	}

	log.Println("running — Ctrl-C to stop")
	<-ctx.Done()

	// Shutdown: restore victims' ARP tables, stop capture, drain.
	log.Println("stopping…")
	s.SetRunning(false)
	arpspoof.Restore(s)
	handle.Close() // ends capture.Run, which closes `packets`, which ends proc.Run
	wg.Wait()

	if rec != nil {
		log.Printf("recorded %d packets to %s", rec.Count(), recordPath)
		_ = rec.Close()
	}
	if err := netinfo.DisableIPForwarding(); err != nil {
		log.Printf("warning: could not disable IP forwarding: %v", err)
	}
	return nil
}

// applyInspect flags the requested devices for inspection. Runs on a loop since
// devices are discovered over time, so "all" and named MACs are picked up as
// they appear.
func applyInspect(s *state.State, spec string) {
	if strings.EqualFold(spec, "all") {
		if n, err := s.Store.InspectAll(); err == nil && n > 0 {
			log.Printf("[inspect] now inspecting %d newly discovered device(s)", n)
		}
	} else {
		for _, mac := range strings.Split(spec, ",") {
			if mac = strings.TrimSpace(strings.ToLower(mac)); mac != "" {
				_ = s.Store.SetInspected(mac)
			}
		}
	}
	// keep the in-memory set (used to scope pcap recording) in sync with the DB
	if macs, err := s.Store.InspectedMACs(); err == nil {
		s.SetInspectedMACs(macs)
	}
}

// runBrowse serves the dashboard for an existing DB without capturing. No root
// needed — handy for exploring results after a run.
func runBrowse(s *state.State, addr string) {
	if addr == "" {
		addr = ":8080"
	}
	startWebServer(s, addr)
	log.Printf("browsing %s — Ctrl-C to stop", addr)
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	<-ctx.Done()
}

// startWebServer launches the dashboard in the background.
func startWebServer(s *state.State, addr string) {
	srv := &http.Server{Addr: addr, Handler: web.New(s.Store, s.Traffic).Handler()}
	go func() {
		log.Printf("dashboard at http://localhost%s", addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("web server: %v", err)
		}
	}()
}

// openInBrowser opens path with the OS default handler (issue #305). Best-effort:
// on a headless box the opener just won't exist, which is fine.
func openInBrowser(path string) {
	var cmd string
	var args []string
	switch runtime.GOOS {
	case "darwin":
		cmd = "open"
	case "windows":
		cmd, args = "cmd", []string{"/c", "start", ""}
	default:
		cmd = "xdg-open"
	}
	if err := exec.Command(cmd, append(args, path)...).Start(); err != nil {
		log.Printf("could not open report (%s); open %s manually", err, path)
	}
}

// loop runs fn immediately, then every interval, until ctx is cancelled.
func loop(ctx context.Context, interval time.Duration, fn func()) {
	t := time.NewTicker(interval)
	defer t.Stop()
	fn()
	for {
		select {
		case <-ctx.Done():
			return
		case <-t.C:
			fn()
		}
	}
}

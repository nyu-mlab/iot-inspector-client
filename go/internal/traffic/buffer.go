// Package traffic keeps a full-resolution, in-memory rolling window of recent
// packets (timestamp, src/dst MAC, size) so the live dashboard can chart traffic
// at any resolution — without the lossy 1-second binning the SQLite flows table
// uses. Only the last `window` is kept, and only for traffic we actually capture
// (inspected devices), so memory stays bounded.
package traffic

import (
	"sort"
	"sync"
	"time"
)

type sample struct {
	t        int64 // unix nanoseconds (packet capture time)
	src, dst string
	size     int
}

type Buffer struct {
	mu      sync.Mutex
	samples []sample // append-only, time-ordered; old entries trimmed from the front
	window  time.Duration
	maxLen  int
}

// New returns a buffer keeping `window` of history, hard-capped at maxLen samples
// (oldest dropped past the cap, so a traffic flood can't exhaust memory).
func New(window time.Duration, maxLen int) *Buffer {
	return &Buffer{window: window, maxLen: maxLen}
}

// Add records one packet. Called from the processor on the capture hot path, so
// it does the minimum: append under a lock, trim if over the hard cap.
func (b *Buffer) Add(tNano int64, src, dst string, size int) {
	b.mu.Lock()
	b.samples = append(b.samples, sample{tNano, src, dst, size})
	if len(b.samples) > b.maxLen {
		b.samples = b.samples[len(b.samples)-b.maxLen:]
	}
	b.mu.Unlock()
}

// Series bins the window into `bins` buckets for one device and returns upload
// (device as source) and download (device as dest) byte totals. Bin 0 is the
// most recent second-fraction; bin bins-1 is `window` ago — matching the chart's
// newest-on-the-right layout. Also trims samples older than the window.
func (b *Buffer) Series(mac string, nowNano int64, bins int) (up, down []int64) {
	up = make([]int64, bins)
	down = make([]int64, bins)
	start := nowNano - b.window.Nanoseconds()
	binNs := b.window.Nanoseconds() / int64(bins)
	if binNs <= 0 {
		binNs = 1
	}

	b.mu.Lock()
	// drop everything older than the window (samples are time-ordered)
	cut := sort.Search(len(b.samples), func(i int) bool { return b.samples[i].t >= start })
	if cut > 0 {
		b.samples = b.samples[cut:]
	}
	// snapshot the slice header; entries are immutable once appended, so we can
	// release the lock and iterate without blocking the capture path.
	snap := b.samples
	b.mu.Unlock()

	for _, s := range snap {
		idx := int((nowNano - s.t) / binNs) // 0 = now
		if idx < 0 {
			idx = 0
		}
		if idx >= bins {
			continue
		}
		if s.src == mac {
			up[idx] += int64(s.size)
		}
		if s.dst == mac {
			down[idx] += int64(s.size)
		}
	}
	return up, down
}

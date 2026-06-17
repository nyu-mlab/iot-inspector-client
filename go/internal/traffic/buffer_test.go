package traffic

import (
	"testing"
	"time"
)

func TestSeriesBinning(t *testing.T) {
	b := New(60*time.Second, 100000)
	const A, G = "aa:bb", "gw"
	now := int64(1_700_000_000_000_000_000) // arbitrary fixed ns

	ms := int64(1_000_000)
	b.Add(now-25*ms, A, G, 100)  // upload, 25ms ago  -> bin 0 (100ms bins)
	b.Add(now-150*ms, A, G, 200) // upload, 150ms ago -> bin 1
	b.Add(now-50*ms, G, A, 500)  // download, 50ms ago -> bin 0
	b.Add(now-90_000*ms, A, G, 9) // 90s ago -> outside window, dropped

	up, down := b.Series(A, now, 600) // 60s / 600 = 100ms bins

	if up[0] != 100 {
		t.Errorf("up[0] = %d, want 100", up[0])
	}
	if up[1] != 200 {
		t.Errorf("up[1] = %d, want 200", up[1])
	}
	if down[0] != 500 {
		t.Errorf("down[0] = %d, want 500", down[0])
	}
	// the 90s-old sample must not appear anywhere
	var total int64
	for _, v := range up {
		total += v
	}
	if total != 300 {
		t.Errorf("total upload = %d, want 300 (old sample should be excluded)", total)
	}
}

func TestMaxLenCap(t *testing.T) {
	b := New(60*time.Second, 10)
	now := int64(1_700_000_000_000_000_000)
	for i := 0; i < 100; i++ {
		b.Add(now-int64(i), "x", "y", 1)
	}
	b.mu.Lock()
	n := len(b.samples)
	b.mu.Unlock()
	if n > 10 {
		t.Errorf("buffer kept %d samples, want <= 10", n)
	}
}

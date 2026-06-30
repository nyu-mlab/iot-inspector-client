package metrics

import (
	"testing"
	"time"
)

func TestSnapshotMath(t *testing.T) {
	m := New()
	for i := 0; i < 5; i++ {
		m.Captured()
	}
	// two processed packets: 100µs total handle time, 60µs of it in the db.
	m.Processed(70 * time.Microsecond)
	m.Processed(30 * time.Microsecond)
	m.DB(40 * time.Microsecond)
	m.DB(20 * time.Microsecond)
	// channel occupancy samples: avg 20, max 30.
	m.SampleChan(10)
	m.SampleChan(20)
	m.SampleChan(30)

	s := m.SnapshotAndReset()
	if s.Captured != 5 || s.Processed != 2 || s.DBCalls != 2 {
		t.Fatalf("counts: cap=%d proc=%d db=%d", s.Captured, s.Processed, s.DBCalls)
	}
	if s.ChanAvg != 20 || s.ChanMax != 30 {
		t.Errorf("chan avg=%.1f max=%.1f, want 20 and 30", s.ChanAvg, s.ChanMax)
	}
	// parse = (100µs - 60µs) / 2 = 20µs; db = 60µs / 2 = 30µs.
	if got := s.ParsePerPacket(); got != 20*time.Microsecond {
		t.Errorf("parse/pkt = %v, want 20µs", got)
	}
	if got := s.DBPerCall(); got != 30*time.Microsecond {
		t.Errorf("db/call = %v, want 30µs", got)
	}

	// reset is real: a fresh snapshot is empty and divides-by-zero stay 0.
	z := m.SnapshotAndReset()
	if z.Captured != 0 || z.ParsePerPacket() != 0 || z.DBPerCall() != 0 {
		t.Errorf("after reset: %+v", z)
	}
}

func TestNilIsNoOp(t *testing.T) {
	var m *Metrics // metrics off: every call must be a safe no-op
	m.Captured()
	m.Processed(time.Second)
	m.DB(time.Second)
	m.SampleChan(99)
	if s := m.SnapshotAndReset(); s != (Snapshot{}) {
		t.Errorf("nil snapshot = %+v, want zero", s)
	}
}

// Package metrics is an optional capture-pipeline profiler (-metrics). It answers
// one question: when packets get dropped under load, is the parser slow, is
// SQLite slow, or is the kernel buffer overflowing? All counters are atomic and
// nil-safe, so the hot path pays nothing when metrics are off (m == nil).
package metrics

import (
	"sync/atomic"
	"time"
)

type Metrics struct {
	captured  atomic.Int64 // packets read off the wire
	processed atomic.Int64 // packets run through the processor
	processNS atomic.Int64 // cumulative time in handle()
	dbNS      atomic.Int64 // cumulative time in the per-packet flow upsert
	dbCalls   atomic.Int64
	chanSum   atomic.Int64 // channel-occupancy samples, for the average
	chanCnt   atomic.Int64
	chanMax   atomic.Int64
}

func New() *Metrics { return &Metrics{} }

func (m *Metrics) Captured() {
	if m != nil {
		m.captured.Add(1)
	}
}

// Processed records one packet through handle() and how long it took (parse +
// dispatch, including any DB time, which DB() tracks separately).
func (m *Metrics) Processed(d time.Duration) {
	if m == nil {
		return
	}
	m.processed.Add(1)
	m.processNS.Add(int64(d))
}

// DB records one flow upsert and its duration.
func (m *Metrics) DB(d time.Duration) {
	if m == nil {
		return
	}
	m.dbCalls.Add(1)
	m.dbNS.Add(int64(d))
}

// SampleChan records the current capture->processor channel occupancy.
func (m *Metrics) SampleChan(n int) {
	if m == nil {
		return
	}
	m.chanSum.Add(int64(n))
	m.chanCnt.Add(1)
	for {
		cur := m.chanMax.Load()
		if int64(n) <= cur || m.chanMax.CompareAndSwap(cur, int64(n)) {
			break
		}
	}
}

// Snapshot is one interval's totals. Rates are per the interval the reporter uses.
type Snapshot struct {
	Captured, Processed, DBCalls int64
	ProcessNS, DBNS              int64
	ChanAvg, ChanMax             float64
}

// ParsePerPacket is handle() time minus DB time, averaged per processed packet.
func (s Snapshot) ParsePerPacket() time.Duration {
	if s.Processed == 0 {
		return 0
	}
	return time.Duration((s.ProcessNS - s.DBNS) / s.Processed)
}

// DBPerCall is the average flow-upsert duration.
func (s Snapshot) DBPerCall() time.Duration {
	if s.DBCalls == 0 {
		return 0
	}
	return time.Duration(s.DBNS / s.DBCalls)
}

// SnapshotAndReset reads and zeroes every counter atomically-enough for a gauge.
func (m *Metrics) SnapshotAndReset() Snapshot {
	if m == nil {
		return Snapshot{}
	}
	cnt := m.chanCnt.Swap(0)
	sum := m.chanSum.Swap(0)
	avg := 0.0
	if cnt > 0 {
		avg = float64(sum) / float64(cnt)
	}
	return Snapshot{
		Captured:  m.captured.Swap(0),
		Processed: m.processed.Swap(0),
		DBCalls:   m.dbCalls.Swap(0),
		ProcessNS: m.processNS.Swap(0),
		DBNS:      m.dbNS.Swap(0),
		ChanAvg:   avg,
		ChanMax:   float64(m.chanMax.Swap(0)),
	}
}

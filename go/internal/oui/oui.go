// Package oui maps a MAC prefix to a hardware vendor using the embedded IEEE OUI
// registry (oui.csv). Mirrors oui_parser.py. The CSV is parsed lazily on first
// lookup so programs that never call Vendor() pay nothing.
package oui

import (
	"bytes"
	_ "embed"
	"encoding/csv"
	"io"
	"strings"
	"sync"
)

//go:embed oui.csv
var ouiCSV []byte

var (
	once      sync.Once
	prefixMap map[string]string
)

// load parses the IEEE CSV (columns: Registry, Assignment, Organization Name, …)
// into prefixMap, keyed by the uppercase 6-hex-digit assignment.
func load() {
	prefixMap = make(map[string]string, 40000)
	r := csv.NewReader(bytes.NewReader(ouiCSV))
	r.FieldsPerRecord = -1
	_, _ = r.Read() // header
	for {
		rec, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil || len(rec) < 3 {
			continue
		}
		prefixMap[strings.ToUpper(rec[1])] = rec[2]
	}
}

// Vendor returns the vendor for a MAC ("aa:bb:cc:dd:ee:ff" or with dashes), or "".
func Vendor(mac string) string {
	once.Do(load)
	clean := strings.ToUpper(strings.NewReplacer(":", "", "-", "").Replace(mac))
	if len(clean) < 6 {
		return ""
	}
	return prefixMap[clean[:6]]
}

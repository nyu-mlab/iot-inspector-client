// Package summary builds a short, plain-language blurb describing a device from
// the facts already collected (issue #308). Deterministic and local: no model,
// no network, no install — it works for every user and can't hallucinate.
package summary

import (
	"strconv"
	"strings"
)

// Describe composes a plain-language summary from whatever facts are known.
// Empty facts are skipped. name is expected to be non-empty (a label always
// exists); the rest are best-effort.
func Describe(name, vendor, typ string, hostnames, ports []string) string {
	var sentences []string

	switch {
	case typ != "" && vendor != "":
		sentences = append(sentences, name+" looks like a "+typ+", likely made by "+vendor+".")
	case typ != "":
		sentences = append(sentences, name+" looks like a "+typ+".")
	case vendor != "":
		sentences = append(sentences, name+" appears to be a device made by "+vendor+".")
	default:
		sentences = append(sentences, name+" is an unidentified device.")
	}

	if top := firstN(hostnames, 3); len(top) > 0 {
		sentences = append(sentences, "It mainly communicates with "+strings.Join(top, ", ")+".")
	}

	if len(ports) > 0 {
		noun := "ports"
		if len(ports) == 1 {
			noun = "port"
		}
		sentences = append(sentences, "It has "+strconv.Itoa(len(ports))+" open "+noun+" ("+strings.Join(firstN(ports, 5), ", ")+").")
	}

	return strings.Join(sentences, " ")
}

func firstN(s []string, n int) []string {
	if len(s) > n {
		return s[:n]
	}
	return s
}

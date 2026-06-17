package processor

import (
	"crypto/md5"
	"encoding/binary"
	"encoding/hex"
	"strconv"
	"strings"
)

// extractJA3 computes the JA3 TLS fingerprint (md5 hex) from a ClientHello TCP
// payload, or "" if the payload isn't a ClientHello. JA3 =
// md5(SSLVersion,Ciphers,Extensions,EllipticCurves,ECPointFormats), with GREASE
// values removed. It's a stable per-client fingerprint useful for identifying
// the device/TLS stack independent of the destination.
func extractJA3(b []byte) string {
	if len(b) < 5 || b[0] != 0x16 { // TLS handshake record
		return ""
	}
	rec := b[5:]
	if l := int(binary.BigEndian.Uint16(b[3:5])); l < len(rec) {
		rec = rec[:l]
	}
	if len(rec) < 4 || rec[0] != 0x01 { // ClientHello
		return ""
	}
	hs := rec[4:]
	if len(hs) < 34 {
		return ""
	}

	version := binary.BigEndian.Uint16(hs[0:2])
	p := 34                          // skip client_version(2) + random(32)
	p += 1 + int(hs[p])              // session_id
	if len(hs) < p+2 {
		return ""
	}

	clen := int(binary.BigEndian.Uint16(hs[p : p+2]))
	p += 2
	if len(hs) < p+clen {
		return ""
	}
	var ciphers []uint16
	for i := 0; i+1 < clen; i += 2 {
		ciphers = append(ciphers, binary.BigEndian.Uint16(hs[p+i:p+i+2]))
	}
	p += clen

	if len(hs) < p+1 {
		return ""
	}
	p += 1 + int(hs[p]) // compression_methods
	if len(hs) < p+2 {
		return ""
	}
	p += 2 // extensions_length

	var exts, curves, formats []uint16
	for p+4 <= len(hs) {
		extType := binary.BigEndian.Uint16(hs[p : p+2])
		extLen := int(binary.BigEndian.Uint16(hs[p+2 : p+4]))
		p += 4
		if p+extLen > len(hs) {
			break
		}
		exts = append(exts, extType)
		switch extType {
		case 0x000a: // supported_groups (elliptic curves)
			if extLen >= 2 {
				n := int(binary.BigEndian.Uint16(hs[p : p+2]))
				for i := 0; i+1 < n && 2+i+1 < extLen; i += 2 {
					curves = append(curves, binary.BigEndian.Uint16(hs[p+2+i:p+2+i+2]))
				}
			}
		case 0x000b: // ec_point_formats
			if extLen >= 1 {
				n := int(hs[p])
				for i := 0; i < n && 1+i < extLen; i++ {
					formats = append(formats, uint16(hs[p+1+i]))
				}
			}
		}
		p += extLen
	}

	ja3 := strings.Join([]string{
		strconv.Itoa(int(version)),
		joinU16(dropGREASE(ciphers)),
		joinU16(dropGREASE(exts)),
		joinU16(dropGREASE(curves)),
		joinU16(formats), // point formats have no GREASE
	}, ",")

	sum := md5.Sum([]byte(ja3))
	return hex.EncodeToString(sum[:])
}

// isGREASE reports whether v is a GREASE placeholder (RFC 8701), which must be
// excluded from JA3 so the fingerprint is stable.
func isGREASE(v uint16) bool { return v&0x0f0f == 0x0a0a }

func dropGREASE(in []uint16) []uint16 {
	out := in[:0:0]
	for _, v := range in {
		if !isGREASE(v) {
			out = append(out, v)
		}
	}
	return out
}

func joinU16(vs []uint16) string {
	parts := make([]string, len(vs))
	for i, v := range vs {
		parts[i] = strconv.Itoa(int(v))
	}
	return strings.Join(parts, "-")
}

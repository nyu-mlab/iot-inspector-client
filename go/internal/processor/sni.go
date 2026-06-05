package processor

import "encoding/binary"

// extractSNI parses the server_name from a TLS ClientHello carried in a TCP
// payload, or returns "" if the payload isn't a ClientHello or has no SNI.
// This replaces tls_processor.extract_sni(). It walks the record → handshake →
// ClientHello → extensions by length prefixes; every step is bounds-checked so
// malformed/partial records just yield "".
func extractSNI(b []byte) string {
	// TLS record header: type(1)=22 handshake, version(2), length(2)
	if len(b) < 5 || b[0] != 0x16 {
		return ""
	}
	rec := b[5:]
	if l := int(binary.BigEndian.Uint16(b[3:5])); l < len(rec) {
		rec = rec[:l]
	}

	// Handshake header: type(1)=1 ClientHello, length(3)
	if len(rec) < 4 || rec[0] != 0x01 {
		return ""
	}
	hs := rec[4:]

	// Skip: client_version(2) + random(32)
	p := 34
	if len(hs) < p+1 {
		return ""
	}
	// session_id
	p += 1 + int(hs[p])
	// cipher_suites
	if len(hs) < p+2 {
		return ""
	}
	p += 2 + int(binary.BigEndian.Uint16(hs[p:p+2]))
	// compression_methods
	if len(hs) < p+1 {
		return ""
	}
	p += 1 + int(hs[p])
	// extensions length(2)
	if len(hs) < p+2 {
		return ""
	}
	p += 2

	for p+4 <= len(hs) {
		extType := binary.BigEndian.Uint16(hs[p : p+2])
		extLen := int(binary.BigEndian.Uint16(hs[p+2 : p+4]))
		p += 4
		if p+extLen > len(hs) {
			return ""
		}
		if extType != 0x0000 { // server_name
			p += extLen
			continue
		}
		// server_name_list(2) | name_type(1)=0 host_name | name_len(2) | name
		ext := hs[p : p+extLen]
		if len(ext) < 5 || ext[2] != 0x00 {
			return ""
		}
		nameLen := int(binary.BigEndian.Uint16(ext[3:5]))
		if 5+nameLen > len(ext) {
			return ""
		}
		return string(ext[5 : 5+nameLen])
	}
	return ""
}

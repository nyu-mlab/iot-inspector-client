//go:build !windows

package main

import "os"

// hasCapturePrivilege reports whether we can open raw sockets and toggle IP
// forwarding. On Unix that means running as root.
func hasCapturePrivilege() bool {
	return os.Geteuid() == 0
}

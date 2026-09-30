//go:build windows

package main

import "golang.org/x/sys/windows"

// hasCapturePrivilege reports whether the process is running elevated. On
// Windows os.Geteuid() always returns -1, so check the process token for an
// enabled Administrators-group membership instead (a non-elevated admin has the
// group present but deny-only, which IsMember correctly reports as false).
func hasCapturePrivilege() bool {
	var sid *windows.SID
	err := windows.AllocateAndInitializeSid(
		&windows.SECURITY_NT_AUTHORITY, 2,
		windows.SECURITY_BUILTIN_DOMAIN_RID,
		windows.DOMAIN_ALIAS_RID_ADMINS,
		0, 0, 0, 0, 0, 0, &sid)
	if err != nil {
		return false
	}
	defer windows.FreeSid(sid)

	member, err := windows.Token(0).IsMember(sid)
	return err == nil && member
}

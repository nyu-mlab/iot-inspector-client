package devid

import (
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// tokenFile is the per-install token's filename, kept next to the database so
// it survives restarts the same way the capture state does.
const tokenFile = "device_id_token"

const (
	installPrefix = "ins_"
	tokenBytes    = 24
)

// InstallToken returns this install's device-id token, generating and
// persisting one on first call. The token is an identifier, not a secret: the
// client is open source, so it exists to let the server rate-limit or revoke a
// single install rather than to prove who is calling. DEVICE_ID_API_KEY
// overrides it, which is how an issued research key is supplied.
func InstallToken(stateDir string) (string, error) {
	if k := strings.TrimSpace(os.Getenv("DEVICE_ID_API_KEY")); k != "" {
		return k, nil
	}
	path := filepath.Join(stateDir, tokenFile)
	if b, err := os.ReadFile(path); err == nil {
		if tok := strings.TrimSpace(string(b)); tok != "" {
			return tok, nil
		}
	}
	buf := make([]byte, tokenBytes)
	if _, err := rand.Read(buf); err != nil {
		return "", fmt.Errorf("generate device-id token: %w", err)
	}
	tok := installPrefix + base64.RawURLEncoding.EncodeToString(buf)
	if err := os.MkdirAll(stateDir, 0o755); err != nil {
		return "", err
	}
	if err := os.WriteFile(path, []byte(tok), 0o600); err != nil {
		return "", fmt.Errorf("persist device-id token: %w", err)
	}
	return tok, nil
}

// NewForInstall builds a Client using this install's persisted token.
func NewForInstall(stateDir string) (*Client, error) {
	tok, err := InstallToken(stateDir)
	if err != nil {
		return nil, err
	}
	return New(tok), nil
}

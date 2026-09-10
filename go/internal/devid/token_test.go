package devid

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestInstallTokenGeneratesPersistsReuses(t *testing.T) {
	dir := t.TempDir()
	tok, err := InstallToken(dir)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.HasPrefix(tok, installPrefix) || len(tok) < 12 {
		t.Fatalf("token %q does not match what the server accepts", tok)
	}
	again, err := InstallToken(dir)
	if err != nil {
		t.Fatal(err)
	}
	if again != tok {
		t.Fatalf("token regenerated: %q then %q", tok, again)
	}
	b, err := os.ReadFile(filepath.Join(dir, tokenFile))
	if err != nil || string(b) != tok {
		t.Fatalf("token not persisted: %v %q", err, b)
	}
}

func TestInstallTokenDistinctPerInstall(t *testing.T) {
	a, _ := InstallToken(t.TempDir())
	b, _ := InstallToken(t.TempDir())
	if a == b {
		t.Fatal("two installs got the same token")
	}
}

func TestInstallTokenEnvOverride(t *testing.T) {
	t.Setenv("DEVICE_ID_API_KEY", "res_issued_key_123456")
	tok, err := InstallToken(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	if tok != "res_issued_key_123456" {
		t.Fatalf("env override ignored, got %q", tok)
	}
}

func TestNewForInstallUsesToken(t *testing.T) {
	dir := t.TempDir()
	c, err := NewForInstall(dir)
	if err != nil {
		t.Fatal(err)
	}
	tok, _ := InstallToken(dir)
	if c.APIKey != tok {
		t.Fatalf("client key %q != install token %q", c.APIKey, tok)
	}
}

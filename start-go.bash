#!/usr/bin/env bash
# start-go.bash - download the prebuilt Go IoT Inspector for this machine and run it.
# No Go, Python, or uv needed. Re-running reuses the cached download.
#
# Optional env overrides:
#   INSPECTOR_VERSION  release tag to use (e.g. go-v1.0.0); default = newest go-v* release
#   INSPECTOR_PORT     dashboard port (default 8080)
#   INSPECTOR_HOME     where the binary + database live (default ~/.iot-inspector-go)
set -euo pipefail

REPO="${INSPECTOR_REPO:-nyu-mlab/iot-inspector-client}"
VERSION="${INSPECTOR_VERSION:-}"
PORT="${INSPECTOR_PORT:-8080}"
APP_HOME="${INSPECTOR_HOME:-$HOME/.iot-inspector-go}"
URL="http://127.0.0.1:$PORT"

die() { echo "Error: $*" >&2; exit 1; }

tmp=""
opener=""
cleanup() {
  [ -n "$opener" ] && kill "$opener" 2>/dev/null
  [ -n "$tmp" ] && rm -rf "$tmp"
  return 0
}
trap cleanup EXIT

if [ "$(id -u)" -eq 0 ]; then
  die "run this as your normal user; it asks for your password (sudo) when needed."
fi
command -v curl >/dev/null 2>&1 || die "curl is required."

# --- 1. Pick the binary for this OS/CPU ---
case "$(uname -s)" in
  Darwin) ASSET="inspector-darwin-universal" ;;
  Linux)
    case "$(uname -m)" in
      x86_64 | amd64) ASSET="inspector-linux-amd64" ;;
      aarch64 | arm64) ASSET="inspector-linux-arm64" ;;
      *) die "unsupported CPU: $(uname -m)" ;;
    esac ;;
  *) die "unsupported OS: $(uname -s) (on Windows, run start-go.bat)" ;;
esac

if command -v sha256sum >/dev/null 2>&1; then
  sha256() { sha256sum "$1" | cut -d' ' -f1; }
else
  sha256() { shasum -a 256 "$1" | cut -d' ' -f1; }
fi

# --- 2. Find the release: newest go-v* tag, else the newest one already downloaded ---
if [ -z "$VERSION" ]; then
  VERSION=$(curl -fsSL --connect-timeout 10 "https://api.github.com/repos/$REPO/releases?per_page=50" 2>/dev/null \
    | grep -o '"tag_name": *"go-v[^"]*"' | head -n1 | sed 's/.*"\(go-v[^"]*\)"$/\1/' || true)
  if [ -z "$VERSION" ] && [ -d "$APP_HOME/bin" ]; then
    VERSION=$(ls -t "$APP_HOME/bin" 2>/dev/null | head -n1 || true)
    [ -n "$VERSION" ] && echo "Could not reach GitHub; using cached $VERSION."
  fi
  [ -n "$VERSION" ] || die "could not find a release (no internet?). Set INSPECTOR_VERSION to retry."
fi

BIN_DIR="$APP_HOME/bin/$VERSION"
BIN="$BIN_DIR/inspector"

# --- 3. Download + verify (skipped when already cached) ---
if [ ! -x "$BIN" ]; then
  echo "Downloading IoT Inspector $VERSION ($ASSET)..."
  tmp=$(mktemp -d)
  base="https://github.com/$REPO/releases/download/$VERSION"
  curl -fL --progress-bar -o "$tmp/$ASSET" "$base/$ASSET" || die "download failed: $base/$ASSET"
  curl -fsSL -o "$tmp/SHA256SUMS" "$base/SHA256SUMS" || die "download failed: $base/SHA256SUMS"
  want=$(awk -v f="$ASSET" '$2 == f {print $1}' "$tmp/SHA256SUMS")
  got=$(sha256 "$tmp/$ASSET")
  [ -n "$want" ] && [ "$want" = "$got" ] || die "checksum mismatch for $ASSET; not running it."
  mkdir -p "$BIN_DIR"
  chmod +x "$tmp/$ASSET"
  mv "$tmp/$ASSET" "$BIN"
  echo "Verified and saved to $BIN"
fi

# --- 4. Make sure the dashboard port is free ---
if curl -s -o /dev/null --connect-timeout 2 "$URL"; then
  die "something is already running at $URL. Close it, or set INSPECTOR_PORT to another port."
fi

# --- 5. Open the browser once the dashboard is up (in the background) ---
open_browser() {
  for _ in $(seq 1 60); do
    if curl -fs -o /dev/null --connect-timeout 2 "$URL/api/state"; then
      if [ "$(uname -s)" = "Darwin" ]; then
        open "$URL" >/dev/null 2>&1 || true
      elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$URL" >/dev/null 2>&1 || true
      fi
      echo "Dashboard: $URL"
      return
    fi
    sleep 1
  done
  echo "Dashboard did not come up; check the output above. It would be at $URL"
}

# --- 6. Run (needs root for packet capture); Ctrl-C stops it and restores the network ---
mkdir -p "$APP_HOME"
echo "IoT Inspector needs administrator access to capture network traffic."
echo "You may be asked for your password."
sudo -v || die "administrator access is required."
open_browser &
opener=$!
echo "Starting IoT Inspector. Press Ctrl-C to stop."
status=0
sudo "$BIN" -serve "127.0.0.1:$PORT" -db "$APP_HOME/inspector.db" \
  -report "$APP_HOME/report.html" -open=false || status=$?

# --- 7. Show the report as the normal user (not root) ---
if [ "$status" -eq 0 ] && [ -f "$APP_HOME/report.html" ]; then
  echo "Report: $APP_HOME/report.html"
  if [ "$(uname -s)" = "Darwin" ]; then
    open "$APP_HOME/report.html" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$APP_HOME/report.html" >/dev/null 2>&1 || true
  fi
fi
exit "$status"

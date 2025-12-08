#!/bin/bash
# install-deps.sh - Handles installation of UV and libpcap (Linux/macOS equivalent of Npcap).
# This script is designed to run on Linux (Debian/Ubuntu, Fedora/RHEL) and macOS (Homebrew).
# It will use 'sudo' to install system dependencies.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 0. Utility Functions ---

# Function to check if a command exists
command_exists () {
  command -v "$1" >/dev/null 2>&1
}

# Function to detect the package manager
detect_package_manager() {
    if command_exists apt-get; then
        echo "apt"
    elif command_exists yum; then
        echo "yum"
    elif command_exists dnf; then
        echo "dnf"
    elif command_exists brew; then
        echo "brew"
    else
        echo "unknown"
    fi
}

# --- 1. Libpcap (Packet Capture Dependency) Check and Installation ---
echo "Checking and installing packet capture dependencies (libpcap equivalent)..."

MANAGER=$(detect_package_manager)
LIBCAP_DEPS=()

case "$MANAGER" in
    "apt")
        echo "Detected Debian/Ubuntu."
        LIBCAP_DEPS=("libpcap-dev" "tcpdump")
        sudo apt-get update
        sudo apt-get install -y "${LIBCAP_DEPS[@]}"
        ;;
    "yum" | "dnf")
        echo "Detected Fedora/RHEL/CentOS."
        LIBCAP_DEPS=("libpcap" "libpcap-devel" "tcpdump")
        # On RHEL/Fedora, access is often granted by default or via /dev/bpf/
        sudo $MANAGER install -y "${LIBCAP_DEPS[@]}"
        ;;
    "brew")
        echo "Detected macOS (Homebrew)."
        # macOS uses BPF devices for network capture, but libpcap is still needed for headers
        LIBCAP_DEPS=("libpcap" "tcpdump")
        if command_exists brew; then
            brew install "${LIBCAP_DEPS[@]}" || true # Allow it to fail if already installed
        else
            echo "Error: Homebrew is not installed. Please install Homebrew before running this script on macOS."
            exit 1
        fi
        ;;
    "unknown")
        echo "Error: Could not detect a supported package manager (apt, yum, dnf, or brew)."
        echo "Please manually install 'libpcap' development headers and 'tcpdump'."
        exit 1
        ;;
esac

echo "Packet capture dependencies installed."

# --- 3. UV Installation ---
echo "Checking for 'uv' and installing if necessary..."
if ! command_exists uv; then
    echo "'uv' not found. Installing now (this may take a moment)..."
    # Download and execute the uv install script
    curl -Ls https://astral.sh/uv/install.sh | bash
    # Note: UV is typically installed into $HOME/.cargo/bin,
    # which needs to be in PATH for the next step.
    echo "UV installation complete."
else
    echo "'uv' found. Skipping UV installation."
fi

echo "=========================================================="
echo "Setup is complete. Returning control to the launch script."
echo "=========================================================="
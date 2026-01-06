#!/bin/bash
# run-app.sh - Handles virtual environment setup, readiness polling, and application launch.
# This script assumes 'uv' is installed and is run from the project root.

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to check if a command exists
command_exists () {
  command -v "$1" >/dev/null 2>&1
}

# --- Configuration ---
VENV_DIR=".venv"
# Relative path to the Streamlit app file
APP_PATH="src/iot_inspector/dashboard.py"
# Assuming the dependency script from the previous step is in the same directory
INSTALL_SCRIPT="./install.sh"
APP_URL="http://localhost:33721/"
polling_delay_seconds=3
max_attempts=20

# --- 1. Dependency Check (Check for 'uv') ---
echo "Checking for 'uv' command..."
if ! command -v uv &> /dev/null; then
    echo "=========================================================="
    echo "ERROR: 'uv' package manager not found."
    echo "Please run the dependency setup script first (requires sudo): $INSTALL_SCRIPT"
    echo "Example: sudo bash $INSTALL_SCRIPT"
    echo "=========================================================="
    exit 1
fi

# --- 2. Virtual Environment Setup ---
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment and installing packages..."
    # uv handles venv creation and package sync
    uv venv
    uv sync --locked
    echo "Virtual environment ready."
fi

# --- 3. Find and Launch Application ---
echo "Starting IoT Inspector..."

# Find the Python executable path within the environment using 'uv run which python'.
# We assume 'uv' itself has permissions to run this lookup.
PYTHON_EXECUTABLE=$VENV_DIR/bin/python

echo "Using Python interpreter: $PYTHON_EXECUTABLE"
echo "Launching Streamlit with 'sudo' to circumvent file permission issues and ensure network access."
echo "You may be prompted for your password."

# Launch the Streamlit app using the found python executable with sudo in the background (&)
sudo "$PYTHON_EXECUTABLE" -m streamlit run "$APP_PATH" --server.headless true &
STREAMLIT_PID=$!
echo "Streamlit process started with PID: $STREAMLIT_PID"

# --- 4. Readiness Polling (using curl) ---
echo "Polling for Streamlit server readiness..."
is_ready=0
attempt=0

while [ $is_ready -eq 0 ] && [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))

    # Use curl to check the HTTP status code.
    # -s: Silent mode, -o /dev/null: discard output, -w "%{http_code}": write the status code
    # We poll for the expected 200 status code.
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$APP_URL" | grep -q "200"; then
        is_ready=1
        echo "✅ Server is ready after $attempt attempts. Launching browser."
    else
        echo "Still waiting for Streamlit server (Attempt $attempt/$max_attempts)..."
        sleep "$polling_delay_seconds"
    fi
done

if [ $is_ready -eq 0 ]; then
    echo "❌ Server failed to start within the time limit ($max_attempts attempts). Check the console output for errors."
    # Kill the background process before exiting
    kill $STREAMLIT_PID || true
    exit 1
fi

# --- 5. Open Browser (Robust Check) ---
# We check for common browsers directly if xdg-open fails or is incomplete
echo "Attempting to launch browser..."

BROWSER_LAUNCHED=0

# Try common browsers directly
if command_exists google-chrome; then
    google-chrome "$APP_URL" &
    BROWSER_LAUNCHED=1
elif command_exists chromium-browser; then
    chromium-browser "$APP_URL" &
    BROWSER_LAUNCHED=1
elif command_exists firefox; then
    firefox "$APP_URL" &
    BROWSER_LAUNCHED=1
# Fallback to the system default utility (which caused the error, but we try anyway)
elif command_exists xdg-open; then
    xdg-open "$APP_URL" &
    BROWSER_LAUNCHED=1
# Final fallback for macOS
elif command_exists open && [[ "$(uname)" == "Darwin" ]]; then
    open "$APP_URL" &
    BROWSER_LAUNCHED=1
fi

if [ $BROWSER_LAUNCHED -eq 1 ]; then
    echo "Browser launched successfully in the background."
else
    echo "----------------------------------------------------------------------------------"
    echo "⚠️ WARNING: Could not automatically launch a web browser."
    echo "Please open the following URL manually in your preferred browser:"
    echo ">>> $APP_URL <<<"
    echo "----------------------------------------------------------------------------------"
fi

# --- 6. Wait for Application Exit ---
echo "IoT Inspector is running. Close the web browser tab or the main Streamlit application window to terminate."
# Wait for the background process (Streamlit) to exit naturally
wait $STREAMLIT_PID
EXIT_CODE=$?

echo "Application exited with code $EXIT_CODE. Returning control to the terminal."

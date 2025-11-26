# Packet Collector API
This API collects labeled network packets for IoT device activity analysis and stores them in a MongoDB database, and also 
stores a copy in PCAP format.

## Requirements

- Python 3.10+
- Install Gunicorn
- Install Python dependencies, add the --break-system-packages flag if needed
```bash
sudo apt-get install gunicorn -y
python3 -m pip install flask pymongo scapy[all] dotenv --break-system-packages
```

- MongoDB server (local or remote)

## MongoDB Setup

1. **Install MongoDB:**  

For example, on Ubuntu 22.04/24.04, use:
```bash
#!/bin/bash
# Install MongoDB 6.0+ on Ubuntu 24.04 (Noble Numbat)

# --- Line 1: Import the GPG key ---
# Downloads the key and securely installs it to the system's keyring directory.
curl -fsSL https://pgp.mongodb.com/server-6.0.asc | sudo gpg --dearmor -o /etc/apt/keyrings/mongodb-server-6.0.gpg

# --- Line 2: Configure Repo, Update, and Install ---
# Sets up the repository source list for 'noble', updates the package index, and installs the full suite.
echo "deb [ arch=amd64,arm64 signed-by=/etc/apt/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org

# --- Final Steps (Start and Verify) ---
# Start the database server and check its status.
sudo systemctl enable --now mongod
sudo systemctl status mongod --no-pager

echo ""
echo "Installation Complete: MongoDB server (mongod) is now running."
echo "Use 'mongosh' to connect to the database."
```

## Environment Variables and Create User

Set these before running the script:

- `MONGO_USER` — MongoDB username
- `MONGO_PASS` — MongoDB password
- `MONGO_HOST` — MongoDB host (default: localhost)
- `MONGO_PORT` — MongoDB port (default: 27017)

Populate a .env file as follows:
```bash
MONGO_USER="youruser"
MONGO_PASS="yourpass"
MONGO_HOST="localhost"
MONGO_PORT=27017
```

Example (Windows Command Prompt):
```bash
set MONGO_USER=youruser 
set MONGO_PASS=yourpass
set MONGO_HOST=localhost
set MONGO_PORT=27017
```

2. **Create a user** (optional, for authentication):  
   In the MongoDB shell:

```bash
#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status.
set -e

# --- 1. Variable Validation ---

# Check if MONGO_USER is set
if [ -z "${MONGO_USER}" ]; then
    echo "ERROR: The MONGO_USER environment variable is not set."
    echo "Please set it before running this script."
    exit 1
fi

# Check if MONGO_PASS is set
if [ -z "${MONGO_PASS}" ]; then
    echo "ERROR: The MONGO_PASS environment variable is not set."
    echo "Please set it before running this script."
    exit 1
fi

# --- 2. User Creation ---
echo "--- Attempting to create MongoDB user '$MONGO_USER' ---"

# Use mongosh to connect to the admin database and create the user.
# The user will have readWrite roles on the 'iot_inspector' database.
# Note: This assumes you are running this on the host where MongoDB is running
# and are already authenticated as an administrator or root user.

mongosh --quiet --eval "
  db.getSiblingDB('admin').createUser({
    user: '$MONGO_USER',
    pwd: '$MONGO_PASS',
    roles: [
      { role: 'readWrite', db: 'iot_inspector' }
    ]
  })
"

echo "✅ Success: MongoDB user '$MONGO_USER' created with readWrite access to 'iot_inspector'."
```

## Run as a Service (Optional)
To setup the service, from the root of the repository, run the following command:
```bash
sudo python3 generate_systemctl_config.py
```

**Enable and Start:** Enable the service to start on boot and start it immediately:
```bash
sudo systemctl enable iot-inspector-packet-collector.service
sudo systemctl start iot-inspector-packet-collector.service
```

**Check Status:** Verify the service is running:
```bash
sudo systemctl status iot-inspector-packet-collector.service
sudo journalctl -u iot-inspector-packet-collector.service -f
```

**Stop the Service:**
```bash
sudo systemctl start iot-inspector-packet-collector.service
```
## Run the API

The API will be available at `http://localhost:5000/label_packets`.
```bash
python3 src/libinspector/server/packet_collector.py
```

The API will be available at `http://localhost:5000/label_packets`.

## Usage

Send a POST request to `/label_packets` with JSON containing:

- `packets` (list of base64 strings)
- `mac_address`
- `device_name`
- `activity_label`
- `start_time`
- `end_time`

Example payload:
```json
{
  "packets": ["base64string1", "base64string2"],
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "device_name": "Device1",
  "activity_label": "activity",
  "start_time": "1717243200",
  "end_time": "1717243500"
}

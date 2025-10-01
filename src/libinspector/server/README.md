# Packet Collector API

## Requirements

- Python 3.8+
- Install dependencies:
```bash
pip install flask pymongo
```

- MongoDB server (local or remote)

## MongoDB Setup

1. **Install MongoDB:**  
   Download and install from [mongodb.com](https://www.mongodb.com/try/download/community).

2. **Create a user** (optional, for authentication):  
   In the MongoDB shell:

```mongosh
use admin 
db.createUser({ user: "youruser", pwd: "yourpass", roles: [ { role: "readWrite", db: "iot_inspector" } ] })
```

## Environment Variables

Set these before running the script:

- `MONGO_USER` — MongoDB username
- `MONGO_PASS` — MongoDB password
- `MONGO_HOST` — MongoDB host (default: localhost)
- `MONGO_PORT` — MongoDB port (default: 27017)

Example (Windows Command Prompt):
```bash
set MONGO_USER=youruser 
set MONGO_PASS=yourpass
set MONGO_HOST=localhost
set MONGO_PORT=27017
```

## Run the API

The API will be available at `http://localhost:5000/label_packets`.
```bash
python src\libinspector\server\packet_collector.py
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

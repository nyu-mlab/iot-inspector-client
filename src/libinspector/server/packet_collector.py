import json
import os
import base64
import time
import sys
import datetime
import re
from flask import Flask, request, jsonify
from pymongo import MongoClient
from scapy.all import wrpcap, Ether, IP
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)

packet_root_dir = "packets"
mongo_user = os.environ.get("MONGO_USER")
mongo_pass = os.environ.get("MONGO_PASS")
mongo_host = os.environ.get("MONGO_HOST", "localhost")
mongo_port = os.environ.get("MONGO_PORT", "27017")
if mongo_user and mongo_pass:
    mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/"
else:
    mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/"

mongo_client = MongoClient(mongo_uri, maxPoolSize=100)
db = mongo_client["iot_inspector"]

# --- CRITICAL: Database Connectivity Test on Startup ---
# We try to list collection names. If the connection or auth is bad, this will raise an exception
# and prevent the Flask server from starting with a bad configuration.
try:
    # Attempt a simple database operation (list collection names) to force connection/auth check
    app.logger.info("Attempting connection and write test to MongoDB...")
    # 1. Attempt to insert a test document
    db.test_connection.insert_one({"status": "startup_check", "timestamp": int(time.time())})
    # 2. Attempt to delete the test document
    db.test_connection.delete_one({"status": "startup_check"})
    # 3. Final check to ensure we can list collections
    db.list_collection_names()
    app.logger.info("Successfully connected and confirmed write access to MongoDB.")
except Exception as e:
    app.logger.info("=" * 50)
    app.logger.info("FATAL ERROR: Could not connect to MongoDB or authentication failed.")
    app.logger.info(f"Connection URI: {mongo_uri}")
    app.logger.info(f"Exception: {e}")
    app.logger.info("=" * 50)
    sys.exit(1)
    # If using gunicorn/uwsgi, this exit won't stop the workers, but will prevent the app from running correctly.
    # If running with 'python app.py', this will stop the application.


def is_prolific_id_valid(prolific_id: str) -> bool:
    """
    Performs sanity checks on the Prolific ID:
    1. Not empty.
    2. Length between 1 and 50 characters (inclusive).
    3. Contains only alphanumeric characters (A-Z, a-z, 0-9).
    Args:
        prolific_id (str): The Prolific ID to validate.

    Returns:
        bool: True if the ID is non-empty, 1-50 characters long, and alphanumeric; False otherwise.
    """
    if not prolific_id or not isinstance(prolific_id, str):
        return False

    # 2. Length check
    if not 1 <= len(prolific_id) <= 50:
        return False

    # 3. Alphanumeric check using regex (ensures no special characters)
    if not re.fullmatch(r'^[a-zA-Z0-9]+$', prolific_id):
        return False

    return True

@app.route('/label_packets', methods=['GET'])
def check_status():
    """
    Handles GET requests to check if the API is reachable and running.

    Returns:
        200: Success with a status message.
    """
    # A simple GET endpoint to confirm Caddy routing and Flask server health
    return jsonify({"status": "API is running", "message": "Ready to receive POST data for /label_packets"}), 200


@app.route('/label_packets', methods=['POST'])
def label_packets():
    """
    Handles POST requests to label network packets.

    Receives JSON with required fields: packets (base64-encoded), mac_address, device_name, activity_label, start_time, end_time.
    Decodes packets, validates input, and inserts a document into the MongoDB 'packets' collection.

    Returns:
        200: Success with status message.
        400: Error if required fields are missing or packet decoding fails.
        500: Error if database insertion fails.
    """
    raw_packets = []
    capture_times = []
    capture_lengths = []

    data = request.get_json()
    app.logger.info("Received POST data:", json.dumps(data, indent=4))
    required_keys = ["packets", "prolific_id", "mac_address", "device_name", "activity_label", "start_time", "end_time"]
    if not data or not all(key in data for key in required_keys):
        app.logger.warning("Missing required fields in POST data")
        return jsonify({"error": "Missing required fields"}), 400

    if not is_prolific_id_valid(data["prolific_id"]):
        app.logger.warning("Invalid Prolific ID received")
        return jsonify({"error": "Prolific ID is invalid"}), 500

    try:
        for pkt_metadata in data["packets"]:
            # Validate essential keys are present
            if not isinstance(pkt_metadata, dict) or 'time' not in pkt_metadata or 'raw_data' not in pkt_metadata:
                app.logger.error("Packet object missing 'time' or 'raw_data' key.")
                return jsonify({"error": "Packet metadata structure is invalid"}), 400

            raw_data_bytes = base64.b64decode(pkt_metadata["raw_data"])
            raw_packets.append(raw_data_bytes)
            capture_times.append(float(pkt_metadata["time"]))
            capture_lengths.append(len(raw_data_bytes))
    except Exception as e:
        app.logger.warning(f"Packet decoding occurred for collection '{data['prolific_id']}': {e}")
        return jsonify({"error": "Packet decoding failed"}), 400

    folder_path: str = os.path.join(str(data["prolific_id"]), str(data["device_name"]), str(data["activity_label"]))
    fullpath = os.path.normpath(os.path.join(packet_root_dir, folder_path))
    if not fullpath.startswith(packet_root_dir):
        app.logger.warning("Invalid characters detected in path components")
        return jsonify({"error": "Seems like invalid characters used in prolific ID, device name or activity label"}), 500

    prolific_user_packets_collected = db[data["prolific_id"]]

    doc = {
        "mac_address": data["mac_address"],
        "device_name": data["device_name"],
        "activity_label": data["activity_label"],
        "start_time": int(data["start_time"]),
        "end_time": int(data["end_time"]),
        "raw_packets": raw_packets,
        "capture_times": capture_times,
        "capture_lengths": capture_lengths
    }
    try:
        prolific_user_packets_collected.insert_one(doc)
    except Exception as e:
        app.logger.warning(f"MongoDB Insert FAILED for collection '{data['prolific_id']}': {e}")
        return jsonify({"error": "Database insert failed"}), 500

    try:
        os.makedirs(fullpath, exist_ok=True)
        pcap_file_name: str = make_pcap_filename(int(data["start_time"]), int(data["end_time"]))
        pcap_name: str = os.path.join(fullpath, pcap_file_name)
        save_packets_to_pcap(raw_packets, capture_times, pcap_name)
    except Exception as e:
        # If file saving fails, return a 500 but note that the DB save succeeded
        app.logger.warning(f"PCAP File Save FAILED for ID: {e}")
        return jsonify({
            "status": "partial_success",
            "inserted": 1,
            "warning": "PCAP file creation failed. Data successfully saved to MongoDB.",
        }), 200
    return jsonify({"status": "success", "inserted": 1}), 200


def make_pcap_filename(start_time: int, end_time: int) -> str:
    """
    Generates a pcap filename that is both human-readable and informative.
    The format is: 'Mon-DD-YYYY_HHMMSSAM/PM_DurationSeconds.pcap'

    Example: 'Oct-31-2025_11:31:00AM_6s.pcap'

    Args:
        start_time (int): Start time in seconds since the epoch.
        end_time (int): End time in seconds since the epoch.

    Returns:
        str: Human-readable filename.
    """
    start_dt = datetime.datetime.fromtimestamp(start_time)
    duration_seconds = end_time - start_time

    # Format the start time: e.g., 'Oct-31-2025_113100AM'
    safe_start = start_dt.strftime("%b-%d-%Y_%I:%M:%S%p")

    # Generate the filename with duration
    filename = f"{safe_start}_{duration_seconds}s.pcap"
    return filename


def save_packets_to_pcap(raw_packets: list, capture_times: list, filename="output.pcap"):
    """
    Saves a list of raw packet bytes to a pcap file.

    Args:
        raw_packets (list): List of bytes objects representing raw packets.
        capture_times (list): The epoch time of each packet when it was captured by IoT Inspector.
        filename (str): Output pcap file name.
    """
    scapy_packets = []
    for i, pkt_bytes in enumerate(raw_packets):
        try:
            pkt = Ether(pkt_bytes)
            if pkt.__class__.__name__ == "Raw":
                pkt = IP(pkt_bytes)
        except Exception:
            pkt = IP(pkt_bytes)

        # CRITICAL STEP: Assign the supplied original capture time
        # This is guaranteed to be correct for ALL packets.
        pkt.time = capture_times[i]
        scapy_packets.append(pkt)
    wrpcap(filename, scapy_packets)


if __name__ == '__main__':
    """
    For high load production use, consider using a WSGI server like Gunicorn or uWSGI.
    
    gunicorn -w 4 -b 0.0.0.0:5000 src.libinspector.server.packet_collector:app
    """
    app.run(host='0.0.0.0', port=5000)

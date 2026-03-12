import json
import os
import base64
import sys
import re
import logging
from .directory_explore import run_ls_command, get_label_summary
from .pcap_check import convert_bytes_to_packet, check_for_application_data, make_pcap_filename
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from scapy.all import wrpcap

load_dotenv()
app = Flask(__name__)
packet_root_dir = "packets"


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


def get_db(current_app: Flask):
    """Helper to get the database instance from the current app context."""
    return current_app.config['MONGO_CLIENT']["iot_inspector"]


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
    db = get_db(app)

    data = request.get_json()
    app.logger.info("Received POST data:", json.dumps(data, indent=4))
    required_keys = ["packets", "prolific_id", "mac_address", "device_category", "device_name", "activity_label",
                     "start_time", "end_time"]
    if not data or not all(key in data for key in required_keys):
        app.logger.warning("Missing required fields in POST data")
        return jsonify({"message": "Missing required fields"}), 400

    if not is_prolific_id_valid(data["prolific_id"]):
        app.logger.warning("Invalid Prolific ID received")
        return jsonify({"message": "Prolific ID is invalid"}), 400

    try:
        for pkt_metadata in data["packets"]:
            # Validate essential keys are present
            if not isinstance(pkt_metadata, dict) or 'time' not in pkt_metadata or 'raw_data' not in pkt_metadata:
                app.logger.error("Packet object missing 'time' or 'raw_data' key.")
                return jsonify({"message": "Packet metadata structure is invalid"}), 400

            raw_data_bytes = base64.b64decode(pkt_metadata["raw_data"])
            raw_packets.append(raw_data_bytes)
            capture_times.append(float(pkt_metadata["time"]))
            capture_lengths.append(len(raw_data_bytes))
    except Exception as e:
        app.logger.warning(f"Packet decoding occurred for collection '{data['prolific_id']}': {e}")
        return jsonify({"message": "Packet decoding failed"}), 400

    folder_path: str = os.path.join(str(data["prolific_id"]), str(data["device_name"]), str(data["activity_label"]))
    fullpath = os.path.normpath(os.path.join(packet_root_dir, folder_path))
    if not fullpath.startswith(packet_root_dir):
        app.logger.warning("Invalid characters detected in path components")
        return jsonify(
            {"message": "Seems like invalid characters used in prolific ID, device name or activity label"}), 500

    prolific_user_packets_collected = db[data["prolific_id"]]

    doc = {
        "mac_address": data["mac_address"],
        "device_name": data["device_name"],
        "device_category": data["device_category"],
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
        return jsonify({"message": "Database insert failed"}), 500

    try:
        os.makedirs(fullpath, exist_ok=True)
        pcap_file_name: str = make_pcap_filename(int(data["start_time"]), int(data["end_time"]))
        pcap_name: str = os.path.join(fullpath, pcap_file_name)
        packet_list = convert_bytes_to_packet(raw_packets, capture_times)

        if check_for_application_data(packet_list):
            wrpcap(pcap_name, packet_list)
            prolific_ls_dir_output = run_ls_command(os.path.join(packet_root_dir, str(data["prolific_id"])))
            current_labels = get_label_summary(prolific_ls_dir_output, data["prolific_id"])
            return jsonify({"status": "success",
                            "inserted": 1,
                            "message": current_labels}), 200
        else:
            return jsonify({"message": "The packet capture has an error, please re-do the labeling, "
                                       "try recording for a longer time, like an extra minute."}), 500
    except Exception as e:
        # If file saving fails, return a 500 but note that the DB save succeeded
        app.logger.warning(f"PCAP File Save FAILED for ID: {e}")
        return jsonify({
            "status": "partial_success",
            "inserted": 1,
            "message": "PCAP file creation failed. Data successfully saved to MongoDB.",
        }), 500


def init_db(app_instance: Flask):
    """Initializes Mongo and attaches it to the app config."""
    mongo_user = os.environ.get("MONGO_USER")
    mongo_pass = os.environ.get("MONGO_PASS")
    mongo_host = os.environ.get("MONGO_HOST", "localhost")
    mongo_port = os.environ.get("MONGO_PORT", "27017")

    if mongo_user and mongo_pass:
        uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/"
    else:
        uri = f"mongodb://{mongo_host}:{mongo_port}/"

    client = MongoClient(uri, maxPoolSize=100)

    try:
        db = client["iot_inspector"]
        db.test_connection.insert_one({"status": "startup_check"})
        db.test_connection.delete_one({"status": "startup_check"})
        app_instance.config['MONGO_CLIENT'] = client
        app_instance.logger.info("Successfully connected to MongoDB.")
        db.list_collection_names()
        app.logger.info("Successfully connected and confirmed write access to MongoDB.")
    except Exception as e:
        app_instance.logger.error(f"FATAL: MongoDB connection failed: {e}")
        sys.exit(1)


def main():
    """Entry point for project.scripts."""
    # Ensure logs show up in the console when run as a script
    logging.basicConfig(level=logging.INFO)

    print("--- IoT Inspector Packet Collector Starting ---")
    init_db(app)

    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    """
    For high load production use, consider using a WSGI server like Gunicorn or uWSGI.
    
    gunicorn -w 4 -b 0.0.0.0:5000 src.libinspector.server.packet_collector:app
    """
    main()

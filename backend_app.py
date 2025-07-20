# backend_app.py - This runs on your Ubuntu VM
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # Import CORS
import subprocess
import os
import json
import time # Import time for timestamp

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Define the directory where status.json will be stored on the VM
# This should be a path where your web server (e.g., Nginx, Apache) can serve static files if needed,
# but for Flask's built-in server, it's just a local path.
STATUS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE_PATH = os.path.join(STATUS_FILE_DIR, 'status.json')
SENTINEL_SCRIPT_PATH = os.path.join(STATUS_FILE_DIR, 'sentinel.py') # Path to your sentinel.py

@app.route('/trigger-sentinel', methods=['POST'])
def trigger_sentinel():
    try:
        data = request.get_json()
        token_id = data.get('tokenId')

        if token_id is None:
            return jsonify({"error": "tokenId is required"}), 400

        # Command to run your sentinel.py script on the VM
        # We explicitly use python3 as the executable
        command = ["python3", SENTINEL_SCRIPT_PATH, str(token_id)]

        # Execute sentinel.py
        # timeout ensures it doesn't hang indefinitely
        result = subprocess.run(command, capture_output=True, text=True, timeout=10) 

        if result.returncode != 0:
            print(f"Sentinel script error (stderr): {result.stderr}")
            print(f"Sentinel script output (stdout): {result.stdout}")
            return jsonify({"error": f"Sentinel script failed: {result.stderr}"}), 500

        print(f"Sentinel script output: {result.stdout}")
        return jsonify({"message": f"Sentinel script triggered for Token ID {token_id}", "output": result.stdout}), 200

    except subprocess.TimeoutExpired:
        print("Sentinel script timed out.")
        return jsonify({"error": "Sentinel script timed out"}), 500
    except Exception as e:
        print(f"Error in /trigger-sentinel: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/status.json')
def get_status_json():
    # Serve the status.json file directly
    if os.path.exists(STATUS_FILE_PATH):
        return send_from_directory(STATUS_FILE_DIR, 'status.json', mimetype='application/json')
    # Initial dummy content if file doesn't exist yet
    return jsonify({"tokenId": -1, "matchFound": False, "lastScanned": int(time.time())}), 200 

if __name__ == '__main__':
    # Create an initial dummy status.json if it doesn't exist, for initial frontend fetch
    if not os.path.exists(STATUS_FILE_PATH):
        with open(STATUS_FILE_PATH, 'w') as f:
            json.dump({"tokenId": -1, "matchFound": False, "lastScanned": int(time.time())}, f, indent=2)

    # Run on all interfaces, port 5000 (check for conflicts on your VM)
    # debug=True is good for testing, disable for production.
    app.run(host='0.0.0.0', port=5000, debug=True)
# sentinel.py - This is called by backend_app.py on your VM
import json
import time
import os
import sys # Import sys to read command line arguments

# Define the output path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE_PATH = os.path.join(SCRIPT_DIR, 'status.json')

def scan_for_ip(token_id):
    print(f"Scanning for derivatives of Token ID: {token_id}...")
    # Simulate finding a match for token ID 2 (your second minted token for demo)
    if token_id == 2: # <--- THIS IS STILL YOUR TARGET DEMO TOKEN ID
        print("Match found!")
        return True
    return False

def update_status_file(token_id, match_found):
    status = {"tokenId": token_id, "matchFound": match_found, "lastScanned": int(time.time())}
    with open(STATUS_FILE_PATH, 'w') as f: # Use the global STATUS_FILE_PATH
        json.dump(status, f, indent=2) 
    print(f"status.json updated at: {STATUS_FILE_PATH}")

if __name__ == "__main__":
    # Read token ID from command-line argument
    if len(sys.argv) > 1:
        try:
            token_to_scan = int(sys.argv[1])
        except ValueError:
            print("Invalid tokenId argument. Usage: python sentinel.py <tokenId>")
            sys.exit(1)
    else:
        # Default to -1 or some non-existent ID if no argument provided
        # This ensures status.json is created even if run directly without arg
        token_to_scan = -1 

    found = scan_for_ip(token_to_scan)
    update_status_file(token_to_scan, found)
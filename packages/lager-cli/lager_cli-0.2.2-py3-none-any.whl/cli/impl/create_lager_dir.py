#!/usr/bin/env python3
"""
Create /etc/lager directory in the Python container
"""
import os
import subprocess
import json

def main():
    try:
        # Create the directory as root first, then change ownership
        result = subprocess.run(['sudo', 'mkdir', '-p', '/etc/lager'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print(json.dumps({"error": f"Failed to create directory: {result.stderr}"}))
            return

        # Change ownership to www-data
        result = subprocess.run(['sudo', 'chown', '-R', 'www-data:www-data', '/etc/lager'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print(json.dumps({"error": f"Failed to change ownership: {result.stderr}"}))
            return

        # Verify the directory exists and is writable
        if os.path.exists('/etc/lager') and os.access('/etc/lager', os.W_OK):
            print(json.dumps({"success": True, "message": "/etc/lager directory created and writable"}))
        else:
            print(json.dumps({"error": "/etc/lager directory not accessible"}))

    except Exception as e:
        print(json.dumps({"error": f"Exception: {str(e)}"}))

if __name__ == "__main__":
    main()
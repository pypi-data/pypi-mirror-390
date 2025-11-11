#!/usr/bin/env python3
"""
Setup /etc/lager directory in the container
"""
import os
import json

def main():
    try:
        # Check if directory already exists
        if os.path.exists('/etc/lager'):
            if os.access('/etc/lager', os.W_OK):
                print(json.dumps({"success": True, "message": "/etc/lager already exists and is writable"}))
                return
            else:
                print(json.dumps({"error": "/etc/lager exists but is not writable"}))
                return

        # Try to create the directory
        try:
            os.makedirs('/etc/lager', exist_ok=True)
            print(json.dumps({"success": True, "message": "Created /etc/lager directory"}))
        except PermissionError:
            # If we can't create in /etc, we need to ask the container admin to do it
            print(json.dumps({
                "error": "Permission denied to create /etc/lager",
                "solution": "Container needs to be rebuilt with RUN mkdir -p /etc/lager && chown www-data:www-data /etc/lager"
            }))

    except Exception as e:
        print(json.dumps({"error": f"Exception: {str(e)}"}))

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Fix the nets directory issue by updating the path in net.py to use a writable location
"""
import os
import sys

def main():
    try:
        net_py_path = "/opt/lager/lager/pcb/net.py"

        # Read the current file
        with open(net_py_path, 'r') as f:
            content = f.read()

        # Replace the LOCAL_NETS_PATH
        old_path = 'LOCAL_NETS_PATH = "/etc/lager/saved_nets.json"'
        new_path = 'LOCAL_NETS_PATH = "/tmp/saved_nets.json"'

        if old_path in content:
            content = content.replace(old_path, new_path)

            # Write the updated file
            with open(net_py_path, 'w') as f:
                f.write(content)

            print('{"success": true, "message": "Updated LOCAL_NETS_PATH to /tmp/saved_nets.json"}')
        else:
            print('{"success": false, "message": "LOCAL_NETS_PATH not found in file"}')

    except Exception as e:
        print(f'{{"error": "Failed to update net.py: {str(e)}"}}')

if __name__ == "__main__":
    main()
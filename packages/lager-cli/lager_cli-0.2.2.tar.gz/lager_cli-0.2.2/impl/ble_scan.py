#!/usr/bin/env python3
"""
BLE scan implementation for gateway execution using existing lager BLE module
This file should be copied to the python container
"""
import json
import sys
import asyncio
import os
import traceback

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Add the lager module to path
sys.path.insert(0, '/opt/lager')

try:
    from lager.ble import Central
except ImportError as e:
    print(json.dumps({"error": f"Could not import lager BLE module: {e}"}))
    sys.exit(1)

def format_device_table(devices, verbose=False):
    """Format devices in a table similar to the CLI output"""
    if not devices:
        return "No devices found!"

    # Sort devices (addresses first, then named devices)
    sorted_devices = sorted(devices, key=lambda d: (d.name is None, d.name or d.address))

    # Create table
    lines = []
    if verbose:
        lines.append(f"{'Name':<20} {'Address':<17} {'RSSI':<6} {'UUIDs'}")
        lines.append("-" * 80)
    else:
        lines.append(f"{'Name':<20} {'Address':<17} {'RSSI'}")
        lines.append("-" * 50)

    for device in sorted_devices:
        device_name = device.name or device.address
        rssi = getattr(device, 'rssi', -100)

        if verbose:
            # Get UUIDs from device metadata if available
            uuids = []
            if hasattr(device, 'metadata') and device.metadata:
                uuids = device.metadata.get('uuids', [])
            uuids_str = ', '.join([str(uuid)[:8] + '...' for uuid in uuids[:3]])
            if len(uuids) > 3:
                uuids_str += f" (+{len(uuids)-3} more)"

            lines.append(f"{device_name:<20} {device.address:<17} {rssi:<6} {uuids_str}")
        else:
            lines.append(f"{device_name:<20} {device.address:<17} {rssi}")

    return '\n'.join(lines)

def main():
    """Main BLE scan function"""
    try:
        # Parse arguments
        scan_args = {}
        if len(sys.argv) >= 2:
            try:
                scan_args = json.loads(sys.argv[1])
            except:
                pass

        timeout = scan_args.get('timeout', 5.0)
        name_contains = scan_args.get('name_contains')
        name_exact = scan_args.get('name_exact')
        verbose = scan_args.get('verbose', False)

        print(f"{GREEN}Scanning for BLE devices for {timeout} seconds...{RESET}")

        # Create BLE central and scan
        central = Central()
        devices = central.scan(scan_time=timeout)

        print(f"{GREEN}Found {len(devices)} device(s){RESET}")

        if not devices:
            print(f"{RED}No BLE devices found!{RESET}")
            return

        # Apply filters
        if name_exact:
            devices = [d for d in devices if (d.name and d.name == name_exact)]

        if name_contains:
            devices = [d for d in devices if (d.name and name_contains.lower() in d.name.lower())]

        if not devices and (name_exact or name_contains):
            print(f"{RED}No devices found matching filter criteria!{RESET}")
            return

        # Display results
        print(f"\n{GREEN}" + format_device_table(devices, verbose) + f"{RESET}")

        # Also output structured data for programmatic use
        device_data = []
        for device in devices:
            device_info = {
                'name': device.name or device.address,
                'address': device.address,
                'rssi': getattr(device, 'rssi', -100)
            }

            if verbose and hasattr(device, 'metadata'):
                device_info['uuids'] = device.metadata.get('uuids', [])

            device_data.append(device_info)

        print(f"\nJSON Output:")
        print(json.dumps(device_data, indent=2))

    except Exception as e:
        traceback.print_exc()
        print(f"{RED}" + json.dumps({"error": f"BLE scan failed: {str(e)}"}) + f"{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
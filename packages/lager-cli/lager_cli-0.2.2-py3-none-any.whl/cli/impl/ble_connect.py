#!/usr/bin/env python3
"""
BLE connect implementation for gateway execution
This file should be copied to the python container
"""
import json
import sys
import asyncio
import traceback

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Add the lager module to path
sys.path.insert(0, '/opt/lager')

try:
    from lager.ble import Central, Client
    from bleak import BleakClient
except ImportError as e:
    print(json.dumps({"error": f"Could not import BLE modules: {e}"}))
    sys.exit(1)

async def connect_to_device(address, timeout=10):
    """Connect to BLE device and get basic info"""
    try:
        print(f"{GREEN}Connecting to BLE device: {address}{RESET}")

        async with BleakClient(address) as client:
            if await client.is_connected():
                print(f"{GREEN}✓ Connected to {address}{RESET}")

                # Get device info
                device_info = {
                    "address": address,
                    "connected": True,
                    "services": []
                }

                # Get services
                try:
                    services = await client.get_services()
                    for service in services:
                        service_info = {
                            "uuid": str(service.uuid),
                            "description": service.description,
                            "characteristics": []
                        }

                        for char in service.characteristics:
                            char_info = {
                                "uuid": str(char.uuid),
                                "description": char.description,
                                "properties": char.properties
                            }
                            service_info["characteristics"].append(char_info)

                        device_info["services"].append(service_info)

                    print(f"{GREEN}Found {len(services)} services{RESET}")

                except Exception as e:
                    print(f"Warning: Could not enumerate services: {e}")

                return device_info

            else:
                return {
                    "address": address,
                    "connected": False,
                    "error": "Failed to establish connection"
                }

    except Exception as e:
        return {
            "address": address,
            "connected": False,
            "error": f"Connection failed: {str(e)}"
        }

def main():
    """Main BLE connect function"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing BLE device address"}))
        sys.exit(1)

    try:
        address = sys.argv[1]

        # Validate address format
        if len(address) != 17 or address.count(':') != 5:
            print(json.dumps({"error": "Invalid BLE address format. Use XX:XX:XX:XX:XX:XX"}))
            sys.exit(1)

        # Run connection
        result = asyncio.run(connect_to_device(address))

        if result.get('connected'):
            print(f"\n{GREEN}Connection successful!{RESET}")
            print(f"{GREEN}Device: {result['address']}{RESET}")
            print(f"{GREEN}Services: {len(result.get('services', []))}{RESET}")

            # Show first few services
            services = result.get('services', [])
            if services:
                print(f"\n{GREEN}Services found:{RESET}")
                for i, service in enumerate(services[:3]):  # Show first 3
                    print(f"{GREEN}  {i+1}. {service['uuid'][:8]}... ({len(service['characteristics'])} characteristics){RESET}")
                if len(services) > 3:
                    print(f"{GREEN}  ... and {len(services)-3} more services{RESET}")

        else:
            print(f"{RED}✗ Connection failed: {result.get('error', 'Unknown error')}{RESET}")

        print(f"\nJSON Output:")
        print(json.dumps(result, indent=2))

        if not result.get('connected'):
            sys.exit(1)

    except Exception as e:
        traceback.print_exc()
        error_result = {"error": f"BLE connection failed: {str(e)}"}
        print(f"{RED}" + json.dumps(error_result) + f"{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
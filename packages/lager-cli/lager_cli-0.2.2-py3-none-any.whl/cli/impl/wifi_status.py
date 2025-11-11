#!/usr/bin/env python3
"""
WiFi status implementation for direct SSH execution
"""
import json
import subprocess
import re

def get_wifi_interfaces():
    """Get list of wireless interfaces"""
    try:
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        interfaces = []
        for line in result.stdout.split('\n'):
            if 'IEEE 802.11' in line:
                interface = line.split()[0]
                interfaces.append(interface)
        return interfaces
    except:
        return ['wlan0']  # Default fallback

def get_interface_status(interface):
    """Get status for a specific wireless interface"""
    try:
        # Get connection status
        result = subprocess.run(['iwconfig', interface], capture_output=True, text=True)
        output = result.stdout

        # Parse ESSID
        essid_match = re.search(r'ESSID:"([^"]*)"', output)
        essid = essid_match.group(1) if essid_match else "Not Connected"

        # Parse connection state
        if "Not-Associated" in output or essid == "":
            state = "Disconnected"
            essid = "Not Connected"
        elif "Access Point: Not-Associated" in output:
            state = "Disconnected"
        else:
            state = "Connected"

        # Get additional info if connected
        signal_info = ""
        if state == "Connected":
            signal_match = re.search(r'Signal level=([^\s]+)', output)
            if signal_match:
                signal_info = f" (Signal: {signal_match.group(1)})"

        return {
            "interface": interface,
            "ssid": essid,
            "state": state + signal_info
        }

    except Exception as e:
        return {
            "interface": interface,
            "ssid": "Error",
            "state": f"Failed to get status: {str(e)}"
        }

def main():
    try:
        interfaces = get_wifi_interfaces()

        print("WiFi Status:")
        print("=" * 40)

        for interface in interfaces:
            status = get_interface_status(interface)
            print(f"Interface: {status['interface']}")
            print(f"    SSID:  {status['ssid']}")
            print(f"    State: {status['state']}")
            print()

    except Exception as e:
        print(f"Error getting WiFi status: {e}")

if __name__ == "__main__":
    main()
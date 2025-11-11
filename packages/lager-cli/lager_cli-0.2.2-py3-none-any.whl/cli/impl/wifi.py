#!/usr/bin/env python3
"""
WiFi implementation for gateway execution - combines scan and status functionality
"""
import json
import subprocess
import re
import sys

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'


# ===== Status functionality =====

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


def wifi_status():
    """Get WiFi status for all interfaces"""
    try:
        interfaces = get_wifi_interfaces()

        print(f"{GREEN}WiFi Status:{RESET}")
        print("=" * 40)

        for interface in interfaces:
            status = get_interface_status(interface)

            # Color code based on connection state
            if "Connected" in status['state']:
                state_color = GREEN
            elif "Disconnected" in status['state']:
                state_color = RED
            else:
                state_color = RED

            print(f"{GREEN}Interface: {status['interface']}{RESET}")
            print(f"    SSID:  {GREEN if status['ssid'] != 'Not Connected' else RED}{status['ssid']}{RESET}")
            print(f"    State: {state_color}{status['state']}{RESET}")
            print()

    except Exception as e:
        print(f"{RED}Error getting WiFi status: {e}{RESET}")
        sys.exit(1)


# ===== Scan functionality =====

def scan_wifi_networks(interface='wlan0'):
    """Scan for available WiFi networks"""
    try:
        # Try iwlist scan first
        result = subprocess.run(['iwlist', interface, 'scan'], capture_output=True, text=True)

        if result.returncode != 0:
            # Try nmcli as fallback
            result = subprocess.run(['nmcli', 'dev', 'wifi'], capture_output=True, text=True)
            if result.returncode == 0:
                return parse_nmcli_output(result.stdout)
            else:
                return {"error": "Could not scan for networks"}

        return parse_iwlist_output(result.stdout)

    except Exception as e:
        return {"error": f"WiFi scan failed: {str(e)}"}


def parse_iwlist_output(output):
    """Parse iwlist scan output"""
    networks = []
    current_network = {}

    for line in output.split('\n'):
        line = line.strip()

        if 'Cell' in line and 'Address:' in line:
            # Start of new network entry
            if current_network:
                networks.append(current_network)
            current_network = {'address': line.split('Address: ')[1]}

        elif 'ESSID:' in line:
            essid_match = re.search(r'ESSID:"([^"]*)"', line)
            if essid_match:
                current_network['ssid'] = essid_match.group(1)

        elif 'Signal level=' in line:
            signal_match = re.search(r'Signal level=([^\s]+)', line)
            if signal_match:
                signal_str = signal_match.group(1)
                try:
                    # Convert to approximate percentage
                    if 'dBm' in signal_str:
                        dbm = int(signal_str.replace('dBm', ''))
                        strength = min(100, max(0, (dbm + 100) * 2))
                    else:
                        strength = 50  # Default
                    current_network['strength'] = strength
                except:
                    current_network['strength'] = 50

        elif 'Encryption key:' in line:
            if 'off' in line:
                current_network['security'] = 'Open'
            else:
                current_network['security'] = 'Secured'

    # Add the last network
    if current_network:
        networks.append(current_network)

    return {"access_points": networks}


def parse_nmcli_output(output):
    """Parse nmcli dev wifi output"""
    networks = []
    lines = output.strip().split('\n')[1:]  # Skip header

    for line in lines:
        parts = line.split()
        if len(parts) >= 6:
            try:
                network = {
                    'ssid': parts[1] if parts[1] != '--' else 'Hidden',
                    'address': parts[0],
                    'strength': int(parts[5]) if parts[5].isdigit() else 50,
                    'security': 'Secured' if parts[7] != '--' else 'Open'
                }
                networks.append(network)
            except:
                continue

    return {"access_points": networks}


def format_networks_table(networks):
    """Format networks in a table"""
    if not networks:
        return "No networks found!"

    lines = []
    lines.append(f"{'SSID':<25} {'Security':<10} {'Strength'}")
    lines.append("-" * 50)

    # Sort by signal strength (descending)
    sorted_networks = sorted(networks, key=lambda x: x.get('strength', 0), reverse=True)

    for net in sorted_networks:
        ssid = net.get('ssid', 'Unknown')[:24]
        security = net.get('security', 'Unknown')
        strength = net.get('strength', 0)
        lines.append(f"{ssid:<25} {security:<10} {strength}%")

    return '\n'.join(lines)


def wifi_scan(scan_args):
    """Scan for WiFi networks"""
    try:
        interface = scan_args.get('interface', 'wlan0')

        print(f"{GREEN}Scanning for WiFi networks on {interface}...{RESET}")

        result = scan_wifi_networks(interface)

        if 'error' in result:
            print(f"{RED}Error: {result['error']}{RESET}")
            print(json.dumps(result))
            sys.exit(1)
            return

        networks = result.get('access_points', [])

        print(f"\n{GREEN}Found {len(networks)} network(s):{RESET}")
        print(f"{GREEN}" + format_networks_table(networks) + f"{RESET}")

        print(f"\n{GREEN}JSON Output:{RESET}")
        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {"error": f"WiFi scan failed: {str(e)}"}
        print(f"{RED}" + json.dumps(error_result) + f"{RESET}")
        sys.exit(1)


# ===== Main dispatcher =====

def main():
    """Main WiFi function - dispatches to scan or status based on arguments"""
    try:
        # Parse arguments
        if len(sys.argv) < 2:
            # Default to status if no arguments
            wifi_status()
            return

        args = json.loads(sys.argv[1])
        action = args.get('action', 'status')

        if action == 'status':
            wifi_status()
        elif action == 'scan':
            wifi_scan(args)
        else:
            print(f"{RED}Error: Unknown action '{action}'. Use 'status' or 'scan'{RESET}")
            sys.exit(1)

    except json.JSONDecodeError as e:
        # If not valid JSON, assume it's the old interface argument for status
        wifi_status()
    except Exception as e:
        print(f"{RED}Error: {str(e)}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Unified debug implementation for all debug commands
"""
import sys
import os
import signal

# Force unbuffered output by reconfiguring existing streams
# Use write_through=True for real-time output when piping (e.g., to defmt-print)
sys.stdout.reconfigure(line_buffering=True, write_through=True)
sys.stderr.reconfigure(line_buffering=True, write_through=True)

import json
import logging
import tempfile
import time

# Suppress debug logging output - must be done before importing lager modules
logging.basicConfig(level=logging.ERROR, force=True)
# Also suppress any existing loggers
logging.getLogger('lager').setLevel(logging.ERROR)

# Global flag to track if SIGINT was received during RTT streaming
# This allows us to handle Ctrl+C gracefully and still execute post-RTT actions
_rtt_interrupted = False

def _sigint_handler_rtt(signum, frame):
    """Custom SIGINT handler for RTT streaming that doesn't terminate the script"""
    global _rtt_interrupted
    _rtt_interrupted = True
    # Don't raise KeyboardInterrupt - just set flag and let RTT loop check it

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

# Add gateway python path
sys.path.insert(0, '/opt/lager/gateway/python')

from lager.debug import (
    connect_jlink,
    disconnect,
    reset_device,
    flash_device,
    chip_erase,
    get_jlink_status
)
from lager.debug.gdb import get_controller, get_arch, reap_gdb_zombies


def info(args):
    """Show debug net information"""
    net = args['net']
    device_type = net.get('channel') or net.get('pin', 'unknown')
    instrument = net.get('instrument', '')

    # Try to get architecture
    try:
        arch = get_arch(device_type)
    except Exception:
        arch = "Unknown"

    # Get current debugger status
    jlink_status = get_jlink_status()

    print(f"Debug Net: {net.get('name', 'unknown')}")
    print(f"  Device:      {device_type}")
    print(f"  Arch:        {arch}")
    print(f"  Probe:       {instrument}")
    print(f"  Status:      {'Connected' if jlink_status['running'] else 'Disconnected'}")


def status(args):
    """Check debugger status"""
    json_output = args.get('json', False)

    # Check J-Link status only
    jlink_status = get_jlink_status()

    if json_output:
        result = {
            "connected": jlink_status['running'],
            "pid": jlink_status.get('pid') if jlink_status['running'] else None
        }
        print(json.dumps(result))
    else:
        if jlink_status['running']:
            pid = jlink_status.get('pid', 'unknown')
            print(f"Debugger: {GREEN}Connected{RESET} (PID {pid})")
        else:
            print(f"Debugger: {RED}Not connected{RESET}")


def connect(args):
    """Connect to debug target"""
    net = args['net']
    device_type = net.get('channel') or args.get('device_type') or net.get('pin', 'unknown')
    force = args.get('force', True)
    halt = args.get('halt', True)
    speed = args.get('speed')
    quiet = args.get('quiet', False)
    json_output = args.get('json', False)

    # Get instrument information from net
    instrument = net.get('instrument', '')

    # Only J-Link is supported
    instrument_lower = instrument.lower().replace('-', '').replace('_', '')
    if 'jlink' not in instrument_lower:
        if json_output:
            result = {"error": f"Only J-Link debuggers are supported. Got: {instrument}"}
            print(json.dumps(result))
        else:
            print(f"{RED}ERROR: Only J-Link debuggers are supported. Got: {instrument}{RESET}")
        sys.exit(1)

    # Map halt to attach mode
    if halt:
        attach = 'reset-halt'
    else:
        attach = 'attach'  # Attach without resetting (device should be running from flash)

    # Connect to J-Link
    status = connect_jlink(
        speed=speed,
        device=device_type,
        transport='SWD',
        force=force,
        ignore_if_connected=(not force),
        vardefs=[],
        attach=attach
    )

    # Determine the actual speed from status
    actual_speed = status.get('speed', 'unknown')
    requested_speed = status.get('requested_speed', speed)
    fallback_used = status.get('fallback_used', False)

    # Check if this was a reused connection
    reused = status.get('already_running') == 'ok'

    # If halt is False (default connect behavior for RTT), ensure device is running
    # This matches legacy behavior where connect gets the device ready for RTT
    if not halt and not reused:
        try:
            gdbmi = get_controller(device=device_type)
            # Use monitor go to start device execution
            responses = gdbmi.write('monitor go', timeout_sec=2.0, raise_error_on_timeout=False)
            # Consume responses but don't print them (silent start)
            for resp in responses:
                pass
        except Exception:
            # If starting fails, it's not critical for connect command
            pass

    # Handle post-connect actions (--rtt, --reset, --rtt-reset flags)
    post_connect_rtt = args.get('post_connect_rtt', False)
    post_connect_reset = args.get('post_connect_reset', False)
    post_connect_rtt_reset = args.get('post_connect_rtt_reset', False)

    if json_output:
        result = {
            "device": device_type,
            "speed_khz": actual_speed if actual_speed != 'unknown' else None,
            "requested_speed_khz": requested_speed if requested_speed and requested_speed != 'unknown' else None,
            "fallback_used": fallback_used,
            "reused_connection": reused,
            "halt_mode": halt
        }
        print(json.dumps(result))
    else:
        # Print success message matching legacy format
        if reused:
            print(f"{GREEN}Connected!{RESET} (reusing existing connection)")
        else:
            print(f"{GREEN}Connected!{RESET}")

    # Execute post-connect actions based on flags
    # Priority: --rtt-reset (highest) > --rtt > --reset
    if post_connect_rtt_reset:
        # --rtt-reset: Reset device FIRST, then immediately start RTT streaming
        # This captures the boot sequence logs as the device reboots

        # Step 1: Reset the device
        reset_args = {
            'net': net,
            'device_type': device_type,
            'halt': False
        }
        reset(reset_args)

        # Step 2: Brief delay to let device start booting
        time.sleep(0.5)

        # Step 3: Start RTT streaming to capture boot logs
        rtt_args = {
            'net': net,
            'timeout': None,  # Stream indefinitely until Ctrl+C
            'channel': 0
        }
        rtt_logs(rtt_args)

    elif post_connect_rtt:
        # Run RTT only
        # RTT handles SIGINT gracefully and returns normally
        rtt_args = {
            'net': net,
            'timeout': None,
            'channel': 0
        }
        rtt_logs(rtt_args)

    elif post_connect_reset:
        # Run reset only
        reset_args = {
            'net': net,
            'device_type': device_type,
            'halt': False
        }
        reset(reset_args)


def disconnect_cmd(args):
    """Disconnect from debug target"""
    # Check if debugger is running first
    jlink_status = get_jlink_status()
    if not jlink_status['running']:
        print(f"{RED}No active debugger session{RESET}")
        return

    # Disconnect from debugger
    disconnect(mcu=None)
    print(f"{GREEN}Disconnected!{RESET}")


def memrd(args):
    """Read memory from target"""
    net = args['net']
    device_type = net.get('channel') or args.get('device_type') or net.get('pin', 'unknown')
    start_addr = args.get('start_addr')
    length = args.get('length')
    json_output = args.get('json', False)

    # Validate length
    if length <= 0:
        if json_output:
            result = {"error": "Length must be greater than 0"}
            print(json.dumps(result))
        else:
            print(f"{RED}ERROR: Length must be greater than 0{RESET}")
        sys.exit(1)

    # Check if debugger is connected
    jlink_status = get_jlink_status()
    if not jlink_status['running']:
        if json_output:
            result = {"error": "No debugger connection found"}
            print(json.dumps(result))
        else:
            print(f"{RED}ERROR: No debugger connection found{RESET}")
            print("Connect first: lager debug <net> connect")
        sys.exit(1)

    # Read memory via GDB
    gdbmi = None
    try:
        # Memory reads require the device to be halted
        # Get GDB controller
        gdbmi = get_controller(device=device_type)

        # Halt the device using monitor reset + monitor halt
        # This is more reliable than just 'monitor halt' when device is running
        gdbmi.write('monitor reset', timeout_sec=2.0)
        gdbmi.write('monitor halt', timeout_sec=2.0)

        # Read memory using GDB command
        cmd = f'x/{length}xb 0x{start_addr:X}'
        responses = gdbmi.write(cmd, timeout_sec=5.0)

        # Collect output first, then print all at once to avoid interleaving
        output_lines = []
        error_detected = False
        error_payload = None

        for resp in responses:
            if resp.get('type') == 'console':
                output = resp.get('payload', '')
                if isinstance(output, str):
                    output_lines.append(output)
            elif resp.get('type') == 'result':
                if resp.get('message') == 'error':
                    error_detected = True
                    error_payload = resp.get('payload', '')
                    if isinstance(error_payload, str):
                        output_lines.append(error_payload)

        # Check if we got valid output or an error
        full_output = ''.join(output_lines)

        if error_detected or not full_output.strip():
            if json_output:
                result = {
                    "error": f"Failed to read memory at address 0x{start_addr:X}",
                    "details": "Address may be invalid or inaccessible"
                }
                print(json.dumps(result))
            else:
                print(f"{RED}ERROR: Failed to read memory at address 0x{start_addr:X}{RESET}")
                print("Address may be invalid or inaccessible")
            sys.exit(1)

        # Output all at once to prevent corruption
        if json_output:
            # Parse memory output into structured format
            memory_data = []
            for line in full_output.strip().split('\n'):
                if line.strip():
                    memory_data.append(line.strip())
            result = {
                "start_addr": f"0x{start_addr:X}",
                "length": length,
                "data": memory_data
            }
            print(json.dumps(result, indent=2))
        else:
            print(full_output, end='')
            sys.stdout.flush()

        # Always resume the device after reading (restore running state)
        # This ensures firmware continues executing after memory inspection
        gdbmi.write('monitor go', timeout_sec=2.0)

    except Exception as e:
        if json_output:
            result = {
                "error": f"Memory read failed: {str(e)}",
                "start_addr": f"0x{start_addr:X}",
                "length": length
            }
            print(json.dumps(result))
        else:
            print(f"{RED}ERROR: Memory read failed at address 0x{start_addr:X}{RESET}")
            print(f"Details: {str(e)}")
        sys.exit(1)
    finally:
        # Always cleanup GDB controller to prevent "active connection" errors
        if gdbmi:
            try:
                # Best effort to restore device to running state if we had an error
                # (successful path already did 'monitor go' above)
                try:
                    gdbmi.write('monitor go', timeout_sec=1.0, raise_error_on_timeout=False)
                except:
                    pass  # Best effort to restore state
                gdbmi.exit()
                # Reap zombie gdb-multiarch processes
                reap_gdb_zombies()
            except:
                pass  # Ignore cleanup errors


def reset(args):
    """Reset the target"""
    net = args['net']
    device_type = net.get('channel') or args.get('device_type') or net.get('pin', 'unknown')
    halt = args.get('halt', False)

    # Check if debugger is connected
    jlink_status = get_jlink_status()
    if not jlink_status['running']:
        print(f"{RED}ERROR: No debugger connection found{RESET}")
        print("Connect first: lager debug <net> connect")
        sys.exit(1)

    # Use GDB monitor commands (maintains J-Link GDB server connection for RTT)
    # This is what the legacy system does based on the screenshots
    try:
        gdbmi = get_controller(device=device_type)

        # Reset using monitor reset
        responses = gdbmi.write('monitor reset', timeout_sec=10.0)
        for resp in responses:
            pass  # Consume but don't print

        if not halt:
            # Start execution using monitor go (like legacy screenshot)
            responses = gdbmi.write('monitor go', timeout_sec=2.0, raise_error_on_timeout=False)
            for resp in responses:
                pass  # Consume but don't print

        # Print success message
        if halt:
            print(f"{GREEN}Reset complete (halted){RESET}")
        else:
            print(f"{GREEN}Reset complete{RESET}")

    except Exception as e:
        print(f"{RED}ERROR: Reset failed: {str(e)}{RESET}")
        sys.exit(1)


def erase(args):
    """Erase chip flash memory"""
    net = args['net']
    device_type = net.get('channel') or args.get('device_type') or net.get('pin', 'unknown')
    speed = args.get('speed', '4000')
    transport = args.get('transport', 'SWD')
    quiet = args.get('quiet', False)
    json_output = args.get('json', False)

    if not quiet and not json_output:
        print(f"WARNING: Erasing ALL flash memory on {device_type}")
        print("This operation cannot be undone!")

    has_error = False
    error_messages = []

    try:
        for output in chip_erase(device_type, speed=speed, transport=transport):
            if isinstance(output, bytes):
                line = output.decode('utf-8', errors='ignore')
            else:
                line = str(output)

            # Check for CRITICAL error indicators in output
            # Be more selective to avoid false positives
            line_lower = line.lower()
            if any(error_pattern in line_lower for error_pattern in [
                '****** error', 'cannot connect to j-link',
                'communication timed out', 'erase failed',
                'unknown / supported device', 'could not find supported device'
            ]):
                has_error = True
                error_messages.append(line.strip())

    except Exception as e:
        has_error = True
        error_messages.append(str(e))

    if has_error:
        if json_output:
            result = {
                "error": f"Chip erase failed for {device_type}",
                "details": error_messages[:3] if error_messages else []
            }
            print(json.dumps(result))
        else:
            print(f"{RED}ERROR: Chip erase failed for {device_type}{RESET}")
            if error_messages:
                print("Error details:")
                for msg in error_messages[:3]:
                    print(f"  {msg}")
        sys.exit(1)

    if json_output:
        result = {"success": True, "device": device_type}
        print(json.dumps(result))
    else:
        print(f"{GREEN}Erased!{RESET}")


def flash(args):
    """Flash firmware to target"""
    net = args['net']
    device_type = net.get('channel') or args.get('device_type') or net.get('pin', 'unknown')
    hexfile = args.get('hexfile')
    elffile = args.get('elffile')
    binfiles = args.get('binfiles', [])

    if not hexfile and not elffile and not binfiles:
        print(f"{RED}ERROR: No files provided for flashing{RESET}")
        sys.exit(1)

    # Check if debugger is connected (flash requires active connection)
    jlink_status = get_jlink_status()
    if not jlink_status['running']:
        print(f"{RED}ERROR: No debugger connection found{RESET}")
        print("Connect first: lager debug <net> connect --box <box>")
        sys.exit(1)

    # Files are already transferred to the gateway, read them from disk
    hexfiles_list = []
    elffiles_list = []
    binfiles_list = []

    if hexfile:
        if not os.path.exists(hexfile):
            print(f"{RED}ERROR: Hex file not found: {hexfile}{RESET}")
            sys.exit(1)

        # Validate Intel HEX file format
        try:
            with open(hexfile, 'r') as f:
                first_line = f.readline().strip()
                if not first_line.startswith(':'):
                    print(f"{RED}ERROR: Invalid HEX file format: {hexfile}{RESET}")
                    print(f"Intel HEX files must start with ':' (colon)")
                    sys.exit(1)
        except Exception as e:
            print(f"{RED}ERROR: Failed to validate HEX file: {hexfile}{RESET}")
            print(f"Details: {str(e)}")
            sys.exit(1)

        hexfiles_list.append(hexfile)

    elif elffile:
        if not os.path.exists(elffile):
            print(f"{RED}ERROR: ELF file not found: {elffile}{RESET}")
            sys.exit(1)

        # Validate ELF file format
        try:
            with open(elffile, 'rb') as f:
                magic = f.read(4)
                if magic != b'\x7fELF':
                    print(f"{RED}ERROR: Invalid ELF file format: {elffile}{RESET}")
                    print(f"File does not have ELF magic number (expected: 0x7F 'ELF')")
                    sys.exit(1)
        except Exception as e:
            print(f"{RED}ERROR: Failed to validate ELF file: {elffile}{RESET}")
            print(f"Details: {str(e)}")
            sys.exit(1)

        elffiles_list.append(elffile)

    elif binfiles:
        for binfile in binfiles:
            filename = binfile['filename']
            address = binfile['address']

            if not os.path.exists(filename):
                print(f"{RED}ERROR: Binary file not found: {filename}{RESET}")
                sys.exit(1)

            # Validate binary file is not empty
            try:
                file_size = os.path.getsize(filename)
                if file_size == 0:
                    print(f"{RED}ERROR: Binary file is empty: {filename}{RESET}")
                    sys.exit(1)
            except Exception as e:
                print(f"{RED}ERROR: Failed to check binary file: {filename}{RESET}")
                print(f"Details: {str(e)}")
                sys.exit(1)

            binfiles_list.append((filename, address))

    # Flash using lager.debug backend
    files = (hexfiles_list, binfiles_list, elffiles_list)

    has_error = False
    error_messages = []
    full_output = []  # Collect all output for pattern matching

    # Success indicators (matching legacy pattern detection)
    found_downloading = False
    found_ok = False

    try:
        for output in flash_device(files, preverify=False, verify=True, run_after=True, mcu=None):
            if isinstance(output, bytes):
                line = output.decode('utf-8', errors='ignore')
            else:
                line = str(output)

            # Print all output to show progress (like the old system)
            print(line, end='')
            sys.stdout.flush()

            # Store for pattern matching
            full_output.append(line)

            # Check for success patterns (like legacy)
            if 'Downloading file [' in line and ('.hex]' in line or '.bin]' in line or '.elf]' in line):
                found_downloading = True
            if 'O.K.' in line:
                found_ok = True

            # Check for CRITICAL error indicators in output
            # Be more selective to avoid false positives
            line_lower = line.lower()
            if any(error_pattern in line_lower for error_pattern in [
                '****** error', 'writing target memory failed',
                'cannot connect to j-link', 'communication timed out',
                'failed to open file', 'unknown / supported device',
                'could not find supported device'
            ]):
                has_error = True
                error_messages.append(line.strip())
            # Note: Don't flag "error:" or "failed:" alone as they may appear in informational messages

    except Exception as e:
        has_error = True
        error_messages.append(str(e))

    # Check success using pattern matching (like legacy)
    if has_error or not (found_downloading and found_ok):
        print(f"\n{RED}Flashing failed!{RESET}")
        if error_messages:
            print("Error details:")
            for msg in error_messages[:5]:  # Show first 5 error messages
                print(f"  {msg}")
        sys.exit(1)

    print(f"\n{GREEN}Flashed!{RESET}")

    # CRITICAL: Flash operation stops J-Link GDB server, so we must reconnect
    # Even if --logs is not set, we should reconnect to restore the debugger connection
    print(f"\n{GREEN}[FLASH] Reconnecting debugger after flash...{RESET}")
    sys.stdout.flush()

    # Create connect args
    connect_args = {
        'action': 'connect',
        'net': net,
        'force': True,
        'halt': False,  # Don't halt, let firmware run
        'device_type': device_type,
        'speed': '4000',
        'quiet': True,  # Suppress normal connect output
        'json': False
    }

    # Call connect directly to reconnect the debugger
    try:
        connect(connect_args)
    except Exception as e:
        print(f"{RED}WARNING: Failed to reconnect debugger: {str(e)}{RESET}")
        print("You may need to manually connect: lager debug <net> connect --box <box>")
        sys.exit(1)

    # CRITICAL: After reconnecting J-Link GDB Server, we MUST reset the device
    # The flash operation used J-Link Commander which disconnected, so the device
    # may be in an undefined state. We need to explicitly reset via GDB to ensure
    # the firmware starts fresh from reset vector.
    try:
        from lager.debug.gdb import get_controller
        gdbmi = get_controller(device=device_type)

        # Reset device using monitor reset - MUST consume responses!
        responses = gdbmi.write('monitor reset', timeout_sec=10.0)  # Increased timeout, raise on error
        for resp in responses:
            pass  # Consume but don't print

        # Small delay to let reset complete
        time.sleep(0.5)

        # Start execution using monitor go - MUST consume responses!
        responses = gdbmi.write('monitor go', timeout_sec=5.0)  # Increased timeout, raise on error
        for resp in responses:
            pass  # Consume but don't print

    except Exception as e:
        print(f"{RED}WARNING: Failed to reset device: {str(e)}{RESET}")
        print("Try manually resetting: lager debug <net> reset --box <box>")

    # If --logs flag is set, stream RTT logs
    stream_logs = args.get('stream_logs', False)
    if stream_logs:
        # Device was already reset above, so we just need to wait for RTT initialization
        # Give firmware time to boot and initialize RTT
        time.sleep(2.0)

        # Create RTT logs args
        logs_args = {
            'net': net,
            'timeout': None,  # Stream indefinitely until Ctrl+C
            'channel': 0,
        }

        # Call the rtt_logs function directly
        # This will block until user presses Ctrl+C
        # The J-Link GDB server will keep running because we're staying in this process
        try:
            rtt_logs(logs_args)
        except KeyboardInterrupt:
            pass  # Silent exit on Ctrl+C


def rtt_logs(args):
    """Stream RTT logs from the target

    Note: This function handles SIGINT (Ctrl+C) gracefully and returns normally.
    It does NOT propagate KeyboardInterrupt to allow post-RTT actions to execute.

    For --rtt-reset functionality, we install a custom SIGINT handler that sets
    a flag instead of raising KeyboardInterrupt, allowing the script to continue
    to the reset step after RTT streaming is interrupted.
    """
    import time
    import socket
    global _rtt_interrupted

    timeout = args.get('timeout')
    channel = args.get('channel', 0)
    net = args['net']
    device_type = net.get('channel') or net.get('pin', 'unknown')
    net_name = net.get('name', 'unknown')

    # Reset global interrupt flag for this RTT session
    _rtt_interrupted = False

    # Install custom SIGINT handler to handle Ctrl+C gracefully
    # Save original handler to restore later
    original_sigint_handler = signal.signal(signal.SIGINT, _sigint_handler_rtt)

    # Get instrument information
    instrument = net.get('instrument', 'Unknown')
    address = net.get('address', '') or net.get('pin', 'unknown')

    # Extract serial number from VISA address if it's a VISA format
    # Format: USB0::0x1366::0x0101::000504402175::INSTR
    # We want just the serial number (4th field)
    if '::' in address:
        parts = address.split('::')
        if len(parts) >= 4:
            serial_number = parts[3]  # Get the serial number field
        else:
            serial_number = address
    else:
        serial_number = address

    # Check if debugger is connected
    jlink_status = get_jlink_status()
    if not jlink_status['running']:
        print(f"{RED}ERROR: No debugger connection found{RESET}", file=sys.stderr)
        print("Connect first: lager debug <net> connect --box <box>", file=sys.stderr)
        sys.exit(1)

    # Determine RTT port based on channel (9090 for channel 0, 9091 for channel 1)
    rtt_port = 9090 + channel

    # Print connection header
    msg = f"Connecting to {net_name}: {instrument} (serial {serial_number}) - Press Ctrl+C to exit\n"
    sys.stderr.buffer.write(msg.encode())
    sys.stderr.buffer.flush()

    # Give firmware time to initialize RTT
    time.sleep(1.5)

    try:
        # Connect to J-Link RTT telnet server on localhost
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(5)  # 5 second timeout for initial connection

        try:
            sock.connect(('localhost', rtt_port))
        except (ConnectionRefusedError, socket.timeout, OSError) as conn_err:
            print(f"{RED}ERROR: Cannot connect to RTT telnet port (localhost:{rtt_port}){RESET}", file=sys.stderr)
            print(f"Connection error: {conn_err}", file=sys.stderr)
            print("\nPossible causes:", file=sys.stderr)
            print("  1. Debugger not connected (run: lager debug <net> connect --box <box>)", file=sys.stderr)
            print("  2. Firmware does not have RTT support compiled in", file=sys.stderr)
            print("  3. RTT control block not found in device memory", file=sys.stderr)
            print("  4. J-Link GDB server RTT port not listening", file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)

        sock.setblocking(False)  # Non-blocking for continuous read

        # Set timeout for reading (default: no timeout, stream until Ctrl+C)
        if timeout is None:
            timeout = 86400  # 24 hours - effectively infinite

        start_time = time.time()
        first_data_received = False
        bytes_received = 0

        try:
            while time.time() - start_time < timeout:
                # Check if SIGINT was received (Ctrl+C)
                if _rtt_interrupted:
                    break

                try:
                    data = sock.recv(4096)
                    if data:
                        if not first_data_received:
                            first_data_received = True

                        bytes_received += len(data)

                        # Output raw binary data to stdout
                        # This allows piping to defmt-print or other tools
                        sys.stdout.buffer.write(data)
                        sys.stdout.buffer.flush()
                    else:
                        # Connection closed
                        break
                except socket.error:
                    # No data available yet, continue waiting
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    # Fallback: in case SIGINT handler didn't catch it
                    break

            # If we exited the loop and no data was ever received, warn the user
            if not first_data_received:
                elapsed = time.time() - start_time
                print(f"\nWARNING: No RTT data received after {elapsed:.1f}s", file=sys.stderr)
                print("\nThis usually means:", file=sys.stderr)
                print("  1. Firmware is not running (crashed or halted)", file=sys.stderr)
                print("  2. Firmware does not have RTT support compiled in", file=sys.stderr)
                print("  3. Firmware has not initialized RTT yet", file=sys.stderr)
                print("  4. RTT control block not found in device memory", file=sys.stderr)
                sys.stderr.flush()

        finally:
            sock.close()

    except Exception as e:
        print(f"{RED}ERROR: RTT connection failed - {str(e)}{RESET}", file=sys.stderr)
        sys.stderr.flush()
        # Restore original SIGINT handler before exiting
        signal.signal(signal.SIGINT, original_sigint_handler)
        sys.exit(1)

    # Restore original SIGINT handler
    signal.signal(signal.SIGINT, original_sigint_handler)

    # Return normally - this allows post-RTT actions to execute
    # The caller can check _rtt_interrupted if needed


def main():
    if len(sys.argv) < 2:
        print(f"{RED}ERROR: Missing arguments{RESET}")
        sys.exit(1)

    try:
        args = json.loads(sys.argv[1])
        action = args.get('action')

        if not action:
            print(f"{RED}ERROR: No action specified{RESET}")
            sys.exit(1)

        # Route to appropriate handler
        handlers = {
            'info': info,
            'status': status,
            'connect': connect,
            'disconnect': disconnect_cmd,
            'memrd': memrd,
            'reset': reset,
            'erase': erase,
            'flash': flash,
            'rtt': rtt_logs,
        }

        handler = handlers.get(action)
        if not handler:
            print(f"{RED}ERROR: Unknown action: {action}{RESET}")
            sys.exit(1)

        handler(args)

    except json.JSONDecodeError as e:
        print(f"{RED}ERROR: Invalid JSON in arguments - {str(e)}{RESET}")
        sys.exit(1)
    except ValueError as e:
        # User input validation errors (speed, length, etc.)
        error_msg = str(e)
        # Check if this is a speed validation error and provide helpful message
        if 'speed' in error_msg.lower():
            print(f"{RED}ERROR: {error_msg}{RESET}")
        elif 'length' in error_msg.lower():
            print(f"{RED}ERROR: {error_msg}{RESET}")
        elif 'address' in error_msg.lower():
            print(f"{RED}ERROR: {error_msg}{RESET}")
        else:
            print(f"{RED}ERROR: Invalid input - {error_msg}{RESET}")
        sys.exit(1)
    except TimeoutError as e:
        print(f"{RED}ERROR: Operation timed out - {str(e)}{RESET}")
        print("This may indicate:")
        print("  - Target device is not responding")
        print("  - Debug probe connection issues")
        print("  - Very large operation taking too long")
        sys.exit(1)
    except FileNotFoundError as e:
        error_msg = str(e)
        print(f"{RED}ERROR: File not found - {error_msg}{RESET}")
        print("Please check that the file path is correct and the file exists")
        sys.exit(1)
    except PermissionError as e:
        error_msg = str(e)
        print(f"{RED}ERROR: Permission denied - {error_msg}{RESET}")
        print("Please check file permissions or try running with appropriate privileges")
        sys.exit(1)
    except ConnectionError as e:
        error_msg = str(e)
        print(f"{RED}ERROR: Connection failed - {error_msg}{RESET}")
        print("Please check:")
        print("  - Debug probe is connected to the host")
        print("  - Target device has power")
        print("  - Debug interface connections (SWDIO, SWCLK, GND)")
        sys.exit(1)
    except Exception as e:
        # Catch-all for unexpected errors
        error_msg = str(e)
        error_type = type(e).__name__

        # Special handling for JLinkStartError - the error message already contains detailed troubleshooting
        if error_type == 'JLinkStartError':
            # The error message already contains all the troubleshooting info, just print it
            print(f"{RED}ERROR: {error_msg}{RESET}", file=sys.stderr)
            sys.exit(1)

        # Try to provide more context for common error patterns
        if 'JLink' in error_msg or 'jlink' in error_msg.lower():
            print(f"{RED}ERROR: J-Link error - {error_msg}{RESET}")
            print("Check that:")
            print("  - J-Link probe is connected via USB")
            print("  - J-Link drivers are installed")
            print("  - No other application is using the J-Link")
        elif 'GDB' in error_msg or 'gdb' in error_msg.lower():
            print(f"{RED}ERROR: GDB communication error - {error_msg}{RESET}")
            print("This may indicate a problem with the debug server")
        else:
            print(f"{RED}ERROR: Operation failed - {error_msg}{RESET}")

        # Only show traceback in debug mode (set via environment variable)
        if os.environ.get('LAGER_DEBUG'):
            import traceback
            print(f"\nDebug information ({error_type}):")
            traceback.print_exc()
        else:
            print(f"\nFor detailed error information, set LAGER_DEBUG=1")
        sys.exit(1)


if __name__ == "__main__":
    main()

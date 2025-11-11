"""
    lager.debug.commands

    Debug an elf file - Updated for direct SSH execution
"""
import itertools
import click
import json
import io
import requests
from contextlib import redirect_stdout
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal
from ..paramtypes import MemoryAddressType, HexArrayType, BinfileType
from ..dut_storage import get_dut_ip, get_dut_name_by_ip, get_dut_user
from .service_helper import is_service_available, ensure_service_tunnel
from .service_client import DebugServiceClient
from .net_cache import get_net_cache


def _resolve_dut_with_username(ctx, dut):
    """
    Resolve DUT parameter to (IP, username) tuple.
    Handles both DUT names and direct IPs, looking up username from storage.

    Args:
        ctx: Click context
        dut: DUT name or IP address

    Returns:
        Tuple of (ip_address, username)
    """
    dut_name = None
    dut_ip = dut

    if dut:
        # Try to resolve as DUT name first
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut_ip = saved_ip
            dut_name = dut  # Original parameter was a DUT name
        else:
            # Parameter was an IP, try reverse lookup
            dut_name = get_dut_name_by_ip(dut)
    else:
        # Use default gateway
        dut_ip = get_default_gateway(ctx)
        if dut_ip:
            dut_name = get_dut_name_by_ip(dut_ip)

    # Get username (defaults to 'lagerdata' if not found)
    username = get_dut_user(dut_name) if dut_name else 'lagerdata'
    if not username:
        username = 'lagerdata'

    return (dut_ip, username)


def validate_speed_param(ctx, param, value):
    """
    Validate speed parameter at CLI level for immediate user feedback.

    Args:
        ctx: Click context
        param: Click parameter
        value: Speed value from user

    Returns:
        Validated speed value

    Raises:
        click.BadParameter: If speed is invalid
    """
    if value is None or value == 'adaptive':
        return value

    try:
        speed_int = int(value)
    except (ValueError, TypeError):
        raise click.BadParameter(
            f"Invalid speed value: '{value}'. "
            f"Speed must be a positive integer (in kHz) or 'adaptive'"
        )

    if speed_int <= 0:
        raise click.BadParameter(
            f"Invalid speed: {speed_int} kHz. "
            f"Speed must be a positive integer greater than 0"
        )

    if speed_int > 50000:  # 50 MHz is unrealistically high for SWD/JTAG
        raise click.BadParameter(
            f"Invalid speed: {speed_int} kHz. "
            f"Maximum supported speed is 50000 kHz (50 MHz). "
            f"Typical speeds: 100-4000 kHz"
        )

    return value

def _get_debug_net(ctx, dut, net_name=None):
    """
    Get debug net information for the DUT with caching.
    If net_name is provided, use that specific net.
    Otherwise, find the first available debug net.
    """
    # Check cache first
    cache = get_net_cache()
    cached_net = cache.get(dut, net_name)
    if cached_net:
        return cached_net

    # Cache miss - fetch from gateway
    # Run net.py list to get available nets
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run_python_internal(
                ctx, get_impl_path("net.py"), dut,
                image="", env={}, passenv=(), kill=False, download=(),
                allow_overwrite=False, signum="SIGTERM", timeout=0,
                detach=False, port=(), org=None, args=("list",)
            )
    except SystemExit:
        pass

    try:
        nets = json.loads(buf.getvalue() or "[]")
        debug_nets = [n for n in nets if n.get("role") == "debug"]

        if net_name:
            # Find specific debug net
            target_net = next((n for n in debug_nets if n.get("name") == net_name), None)
            if not target_net:
                click.secho(f"Debug net '{net_name}' not found.", fg='red', err=True)
                ctx.exit(1)
        else:
            # Find first available debug net
            if not debug_nets:
                click.secho("No debug nets found. Create one with: lager nets create <name> debug <device_type> <address>", fg='red', err=True)
                ctx.exit(1)
            target_net = debug_nets[0]

        # Cache the result before returning
        cache.set(dut, net_name, target_net)
        return target_net

    except json.JSONDecodeError:
        click.secho("Failed to parse nets information.", fg='red', err=True)
        ctx.exit(1)

def _get_service_client(dut):
    """
    Create and return a debug service client for the given DUT.

    Args:
        dut: DUT name or IP address

    Returns:
        DebugServiceClient instance or None on failure
    """
    try:
        client = DebugServiceClient(dut)
        return client
    except Exception as e:
        click.secho(f"Failed to create service client: {e}", fg='red', err=True)
        return None

def _is_connected(client):
    """
    Check if debugger is currently connected.

    Args:
        client: DebugServiceClient instance

    Returns:
        True if connected, False otherwise
    """
    try:
        status = client.get_debug_status()
        return status.get('connected', False)
    except Exception:
        return False

def _auto_connect_if_needed(client, debug_net, ctx, quiet=False):
    """
    Auto-connect to debugger if not already connected.
    Does NOT reconnect if already connected.

    Args:
        client: DebugServiceClient instance
        debug_net: Debug net configuration
        ctx: Click context
        quiet: Suppress informational messages

    Returns:
        True if connected (either already or newly), False on failure
    """
    # Check if already connected
    if _is_connected(client):
        return True

    # Not connected, auto-connect
    if not quiet:
        click.secho("Auto-connecting to debugger...", fg='cyan', dim=True)

    try:
        client.connect(debug_net, speed=None, force=False, halt=False)
        if not quiet:
            click.secho("Auto-connected!", fg='cyan', dim=True)
        return True
    except Exception as e:
        click.secho(f"Error: Failed to auto-connect to debugger", fg='red', err=True)
        click.secho(f"Details: {e}", fg='red', err=True)
        click.secho("\nTroubleshooting steps:", fg='cyan', err=True)
        click.secho("  1. Check physical debug cable connection", fg='cyan', err=True)
        click.secho("  2. Verify target device is powered on", fg='cyan', err=True)
        click.secho("  3. Check debug probe LED status", fg='cyan', err=True)
        return False

def _auto_disconnect(client, debug_net, no_disconnect=False, quiet=False):
    """
    Auto-disconnect from debugger to free resources.
    Respects --no-disconnect flag.

    Args:
        client: DebugServiceClient instance
        debug_net: Debug net configuration
        no_disconnect: If True, skip disconnect
        quiet: Suppress informational messages
    """
    if no_disconnect:
        return

    try:
        client.disconnect(debug_net)
        if not quiet:
            click.secho("Auto-disconnected debugger", fg='cyan', dim=True)
    except Exception:
        pass  # Ignore disconnect errors

class NetDebugGroup(click.MultiCommand):
    """Custom multi-command that treats first argument as net name"""

    def list_commands(self, ctx):
        """List all available debug subcommands"""
        return ['connect', 'disconnect', 'flash', 'reset', 'erase', 'memrd', 'status', 'rtt', 'health']

    def get_command(self, ctx, name):
        """Get the command for a given subcommand name"""
        commands = {
            'connect': connect,
            'disconnect': disconnect,
            'flash': flash,
            'reset': reset,
            'erase': erase,
            'memrd': memrd,
            'status': status,
            'rtt': rtt,
            'health': health,
        }
        return commands.get(name)

    def resolve_command(self, ctx, args):
        """Override to handle net_name extraction before command resolution"""
        # List of known subcommands
        subcommands = self.list_commands(ctx)

        # Check if first argument is a subcommand
        if args and args[0] in subcommands:
            # First arg is a subcommand, no net_name provided
            # Check if we have a default net_name
            if not hasattr(ctx.obj, 'net_name') or ctx.obj.net_name is None:
                default_net = get_default_net(ctx, 'debug')
                if default_net:
                    ctx.obj.net_name = default_net
                # If still no net_name, subcommands will handle the error

            # Return the command and remaining args
            cmd_name = args[0]
            return cmd_name, self.get_command(ctx, cmd_name), args[1:]

        # First arg might be net_name, second arg should be command
        if len(args) >= 2 and args[1] in subcommands:
            # Set the net_name from first arg
            ctx.obj.net_name = args[0]
            cmd_name = args[1]
            return cmd_name, self.get_command(ctx, cmd_name), args[2:]

        # Fall back to default behavior
        return super().resolve_command(ctx, args)

@click.command(name='debug', cls=NetDebugGroup)
@click.pass_context
def _debug(ctx):
    """
    Debug firmware and manage debug sessions

    Usage:
        lager debug <NET_NAME> <command>  # Explicit net name
        lager debug <command>              # Use default net name
    """
    # Net name extraction is handled by NetDebugGroup.resolve_command()
    pass


@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--force/--no-force', is_flag=True, default=False,
              help='Force new connection (default: reuse existing)', show_default=True)
@click.option('--halt/--no-halt', is_flag=True, default=False,
              help='Halt the device when connecting', show_default=True)
@click.option('--speed', type=str, default=None, callback=validate_speed_param,
              help='SWD/JTAG speed in kHz (e.g., 100, 4000) or "adaptive"')
@click.option('--quiet', is_flag=True, default=False,
              help='Suppress informational messages')
@click.option('--json', 'json_output', is_flag=True, default=False,
              help='Output results in JSON format')
@click.option('--rtt', is_flag=True, default=False,
              help='Automatically stream RTT logs after connecting')
@click.option('--rtt-reset', is_flag=True, default=False,
              help='Connect, reset device, then stream RTT logs (captures boot sequence)')
@click.option('--reset', is_flag=True, default=False,
              help='Reset the device after connecting')
def connect(ctx, box,
 dut, force, halt, speed, quiet, json_output, rtt, rtt_reset, reset):
    """Connect to debugger"""

    # Use box or dut (box takes precedence)
    dut = box or dut

    # Get net_name from parent context
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    debug_net = _get_debug_net(ctx, dut, net_name)

    # Use service client (required)
    if not is_service_available(dut, username):
        click.secho("Error: Debug service not available on gateway", fg='red', err=True)
        ctx.exit(1)

    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Failed to establish SSH tunnel to debug service", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    # Check if already connected and reconnect if so
    try:
        debug_status = client.get_debug_status()
        if debug_status.get('connected', False):
            if not quiet and not json_output:
                click.echo("Debugger already connected. Reconnecting...")
            # Disconnect first
            client.disconnect(debug_net)
    except Exception:
        # If status check fails, just proceed with connect
        pass

    # Connect to debugger
    try:
        result = client.connect(debug_net, speed=speed, force=force, halt=halt)
    except requests.exceptions.HTTPError as e:
        # Parse error response for more details
        error_detail = "Unknown error"
        try:
            error_json = e.response.json()
            error_detail = error_json.get('error', str(e))
        except:
            error_detail = str(e)

        click.secho("Error: Failed to connect to debugger", fg='red', err=True)

        # Check for common connection issues
        if "500" in str(e) or "Internal Server Error" in str(e):
            click.secho("\nPossible causes:", fg='yellow', err=True)
            click.secho("  • Debug probe not connected to target device", fg='yellow', err=True)
            click.secho("  • Target device not powered", fg='yellow', err=True)
            click.secho("  • Incorrect device type in net configuration", fg='yellow', err=True)
            click.secho("  • Debug interface disabled on target", fg='yellow', err=True)
            click.secho("\nTroubleshooting steps:", fg='cyan', err=True)
            click.secho("  1. Check physical debug cable connection", fg='cyan', err=True)
            click.secho("  2. Verify target device is powered on", fg='cyan', err=True)
            click.secho("  3. Check debug probe LED status", fg='cyan', err=True)
            click.secho(f"  4. Review net configuration: lager nets --box {dut}", fg='cyan', err=True)

        client.close()
        ctx.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        client.close()
        ctx.exit(1)

    if not quiet:
        if json_output:
            click.echo(json.dumps(result, indent=2))
        else:
            click.secho("Connected!", fg='green', err=True)

    # Handle post-connect actions
    if rtt or rtt_reset:
        # If --rtt-reset, reset the device first to capture boot sequence
        if rtt_reset:
            if not quiet:
                click.echo("Resetting device to capture boot sequence...", err=True)
            client.reset(debug_net, halt=False)

            # Wait for device to reset and firmware to boot
            # This delay ensures:
            # 1. Device completes reset cycle (~500ms)
            # 2. Firmware boots and initializes RTT control block (~1-2s)
            # 3. J-Link detects RTT control block in RAM (~500ms)
            # 4. J-Link RTT telnet server becomes available (~500ms)
            import time
            if not quiet:
                click.echo("Waiting for RTT initialization...", err=True)
            time.sleep(3.5)  # Increased from 2.0s to 3.5s for better reliability

        # Stream RTT logs using the service endpoint (fast!)
        if not quiet:
            click.echo("Starting RTT stream...", err=True)

        try:
            # Stream RTT data to stdout
            for chunk in client.rtt(channel=0, timeout=None):
                # Write directly to stdout in binary mode for maximum performance
                import sys
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
        except KeyboardInterrupt:
            # User pressed Ctrl+C - graceful exit
            if not quiet:
                click.echo("\nRTT stream stopped", err=True)
        except Exception as e:
            click.secho(f"\nRTT stream error: {e}", fg='red', err=True)
        finally:
            client.close()
    elif reset:
        client.reset(debug_net, halt=False)
        if not quiet:
            click.secho("Reset complete", fg='green')
        client.close()
    else:
        client.close()

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--keep-server', is_flag=True, default=False,
              help="Keep JLinkGDBServer running for external GDB client connections")
def disconnect(ctx, box, dut, keep_server):
    """Disconnect from debugger"""
    # Use box or dut (box takes precedence)
    dut = box or dut

    # Get net_name from parent context
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    debug_net = _get_debug_net(ctx, dut, net_name)

    # Use service client (required)
    if not is_service_available(dut, username):
        click.secho("Error: Debug service not available on gateway", fg='red', err=True)
        ctx.exit(1)

    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Failed to establish SSH tunnel to debug service", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    # Disconnect from debugger
    client.disconnect(debug_net, keep_jlink_running=keep_server)

    if keep_server:
        click.secho(f"Disconnected (JLinkGDBServer still running on {dut}:2331)", fg='green')
        click.secho(f"You can now connect with: arm-none-eabi-gdb firmware.elf -ex 'target extended-remote {dut}:2331'", fg='cyan')
    else:
        click.secho("Disconnected", fg='green')

    client.close()

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--hex', type=click.Path(exists=True))
@click.option('--elf', type=click.Path(exists=True))
@click.option('--bin', multiple=True, type=BinfileType(exists=True))
@click.option('--verbose', is_flag=True, default=False,
              help='Show detailed J-Link connection and flash output (slower)')
@click.option('--force-reconnect', is_flag=True, default=False,
              help='Force disconnect and reconnect before flash for clean state')
@click.option('--erase', is_flag=True, default=False,
              help='Erase all flash before flashing (ensures clean boot state for RTT)')
@click.option('--no-disconnect', is_flag=True, default=False,
              help='Keep debugger connected after flash (default: auto-disconnect)')
def flash(ctx, box,
 dut, hex, elf, bin, verbose, force_reconnect, erase, no_disconnect):
    """Flash firmware to target"""

    # Use box or dut (box takes precedence)
    dut = box or dut

    # Get net_name from parent context
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    debug_net = _get_debug_net(ctx, dut, net_name)

    # Use service client (required)
    if not is_service_available(dut, username):
        click.secho("Error: Debug service not available on gateway", fg='red', err=True)
        ctx.exit(1)

    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Failed to establish SSH tunnel to debug service", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    # Auto-connect if not already connected
    if not _auto_connect_if_needed(client, debug_net, ctx):
        client.close()
        ctx.exit(1)

    # Erase flash if requested (ensures clean state for RTT and firmware initialization)
    if erase:
        try:
            click.echo("Erasing flash memory...", err=True)
            client.erase(debug_net, speed='4000', transport='SWD')
            click.secho("Erase complete!", fg='green', err=True)

            # Reconnect after erase (erase auto-disconnects)
            # Always reconnect here to continue with flash operation
            import time
            time.sleep(0.3)
            client.connect(debug_net, force=False, halt=False)
        except Exception as e:
            click.secho(f"Flash erase failed: {e}", fg='red', err=True)
            # Don't disconnect if --no-disconnect was specified
            if not no_disconnect:
                client.disconnect(debug_net)
            client.close()
            ctx.exit(1)

    # Force reconnect if requested for clean state
    if force_reconnect:
        try:
            click.echo("Forcing clean reconnect...", err=True)
            # Disconnect
            client.disconnect(debug_net)
            import time
            time.sleep(0.5)
            # Reconnect with force
            client.connect(debug_net, force=True, halt=False)
            click.echo("Reconnect complete", err=True)
        except Exception as e:
            click.secho(f"Warning: Force reconnect failed: {e}", fg='yellow', err=True)
            # Continue anyway - user explicitly requested this

    # Flash firmware
    from pathlib import Path

    try:
        # Validate that only one file type is specified
        file_types_specified = sum([bool(hex), bool(elf), bool(bin)])
        if file_types_specified > 1:
            click.secho('Error: Cannot specify multiple file types (--hex, --elf, --bin)', fg='red', err=True)
            click.secho('Please specify only one file type option.', fg='red', err=True)
            ctx.exit(1)
        elif file_types_specified == 0:
            click.secho('Provide --hex, --elf, or --bin.', fg='red')
            ctx.exit(1)

        # Flash the appropriate file type
        if hex:
            result = client.flash(Path(hex), file_type='hex', verbose=verbose, net=debug_net)
        elif elf:
            result = client.flash(Path(elf), file_type='elf', verbose=verbose, net=debug_net)
        elif bin:
            if len(bin) > 1:
                click.secho("Multiple binary files not supported yet", fg='red', err=True)
                ctx.exit(1)
            bf = bin[0]
            result = client.flash(Path(bf.path), file_type='bin', address=bf.address, verbose=verbose, net=debug_net)

        # Display verbose flash output if available
        output = result.get('output', [])
        for line in output:
            click.echo(line)

        click.secho("\nFlashed!", fg='green')
    except requests.exceptions.HTTPError as e:
        # Extract error message from response if available
        try:
            error_detail = e.response.json().get('error', str(e))
        except Exception:
            error_detail = str(e)

        click.secho(f"Flash failed: {error_detail}", fg='red', err=True)
        _auto_disconnect(client, debug_net, no_disconnect=no_disconnect)
        client.close()
        ctx.exit(1)
    except Exception as e:
        click.secho(f"Flash failed: {e}", fg='red', err=True)
        _auto_disconnect(client, debug_net, no_disconnect=no_disconnect)
        client.close()
        ctx.exit(1)

    # Auto-disconnect to free hardware resources for other operations (e.g., UART)
    _auto_disconnect(client, debug_net, no_disconnect=no_disconnect)
    client.close()

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--speed', type=str, default='4000', callback=validate_speed_param,
              help='SWD/JTAG speed in kHz (default: 4000)')
@click.option('--yes', is_flag=True, default=False,
              help='Skip confirmation prompt')
@click.option('--quiet', is_flag=True, default=False,
              help='Suppress warning messages')
@click.option('--json', 'json_output', is_flag=True, default=False,
              help='Output results in JSON format')
@click.option('--no-disconnect', is_flag=True, default=False,
              help='Keep debugger connected after erase (default: auto-disconnect)')
def erase(ctx, box,
 dut, speed, yes, quiet, json_output, no_disconnect):
    """Erase all flash memory on target"""

    # Use box or dut (box takes precedence)
    dut = box or dut

    # Get net_name from parent context
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    debug_net = _get_debug_net(ctx, dut, net_name)
    device_type = debug_net.get('pin', 'unknown')

    # Confirm the erase operation (skip if quiet or json mode)
    if not yes and not quiet and not json_output:
        click.echo(f"WARNING: This will erase ALL flash memory on {device_type}")
        click.echo("This operation cannot be undone!")
        if not click.confirm("Do you want to continue?"):
            click.echo("Chip erase cancelled.")
            ctx.exit(0)

    # Use service client (required)
    if not is_service_available(dut, username):
        click.secho("Error: Debug service not available on gateway", fg='red', err=True)
        ctx.exit(1)

    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Failed to establish SSH tunnel to debug service", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    # Auto-connect if not already connected
    if not _auto_connect_if_needed(client, debug_net, ctx, quiet=quiet):
        client.close()
        ctx.exit(1)

    # Execute erase
    if not quiet:
        click.echo("Erasing flash memory...")

    try:
        result = client.erase(debug_net, speed=speed, transport='SWD')
    except requests.exceptions.HTTPError as e:
        # Extract error message from response if available
        try:
            error_detail = e.response.json().get('error', str(e))
        except Exception:
            error_detail = str(e)

        click.secho(f"Erase failed: {error_detail}", fg='red', err=True)
        _auto_disconnect(client, debug_net, no_disconnect=no_disconnect, quiet=quiet)
        client.close()
        ctx.exit(1)
    except Exception as e:
        click.secho(f"Erase failed: {e}", fg='red', err=True)
        _auto_disconnect(client, debug_net, no_disconnect=no_disconnect, quiet=quiet)
        client.close()
        ctx.exit(1)

    # Output results
    if json_output:
        click.echo(json.dumps(result, indent=2))
    elif not quiet:
        click.secho("Erase complete!", fg='green')

    # Erase internally disconnects (requires exclusive hardware access via JLinkExe)
    # If --no-disconnect was specified, reconnect to honor user's intent
    if no_disconnect:
        import time
        time.sleep(0.5)  # Give hardware time to be released
        if not quiet:
            click.secho("Reconnecting (erase requires disconnect)...", fg='cyan', dim=True)
        try:
            client.connect(debug_net, speed=None, force=False, halt=False)
            if not quiet:
                click.secho("Reconnected!", fg='cyan', dim=True)
        except Exception as e:
            click.secho(f"Warning: Failed to reconnect after erase: {e}", fg='yellow', err=True)

    client.close()

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--halt/--no-halt', is_flag=True, default=False,
              help='Halt the DUT after reset', show_default=True)
@click.option('--force-reconnect', is_flag=True, default=False,
              help='Force disconnect and reconnect before reset for clean state')
@click.option('--no-disconnect', is_flag=True, default=False,
              help='Keep debugger connected after reset (useful for RTT streaming)')
def reset(ctx, box,
 dut, halt, force_reconnect, no_disconnect):
    """Reset target"""

    # Use box or dut (box takes precedence)
    dut = box or dut

    # Get net_name from parent context
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    debug_net = _get_debug_net(ctx, dut, net_name)

    # Use service client (required)
    if not is_service_available(dut, username):
        click.secho("Error: Debug service not available on gateway", fg='red', err=True)
        ctx.exit(1)

    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Failed to establish SSH tunnel to debug service", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    # Auto-connect if not already connected (unless force-reconnect, which handles its own connection)
    if not force_reconnect:
        if not _auto_connect_if_needed(client, debug_net, ctx):
            client.close()
            ctx.exit(1)

    # Force reconnect if requested for clean state
    if force_reconnect:
        try:
            click.echo("Forcing clean reconnect...", err=True)
            client.disconnect(debug_net)
            import time
            time.sleep(0.5)
            client.connect(debug_net, force=True, halt=False)
            click.echo("Reconnect complete", err=True)
        except Exception as e:
            click.secho(f"Warning: Force reconnect failed: {e}", fg='yellow', err=True)

    # Reset device
    try:
        result = client.reset(debug_net, halt=halt)
        click.secho("Reset complete", fg='green')
    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg or "No debugger connection" in error_msg:
            click.secho("Error: No debugger connection found. Connect first with: lager debug <net> connect --box <box>", fg='red', err=True)
        else:
            click.secho(f"Error: {e}", fg='red', err=True)
        _auto_disconnect(client, debug_net, no_disconnect=no_disconnect or halt)
        client.close()
        ctx.exit(1)

    # Auto-disconnect to free hardware resources for other operations (e.g., UART)
    # Skip auto-disconnect if:
    #   - --halt was used (user wants to keep target halted)
    #   - --no-disconnect was used (user wants to keep connection for RTT streaming)
    _auto_disconnect(client, debug_net, no_disconnect=no_disconnect or halt)
    client.close()

@click.command()
@click.pass_context
@click.argument('start_addr', type=MemoryAddressType())
@click.argument('length', type=MemoryAddressType())
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--json', 'json_output', is_flag=True, default=False,
              help='Output results in JSON format')
@click.option('--no-disconnect', is_flag=True, default=False,
              help='Keep debugger connected after reading (default: auto-disconnect)')
def memrd(ctx, start_addr, length, box,
 dut, json_output, no_disconnect):
    """Read memory from target"""

    # Use box or dut (box takes precedence)
    dut = box or dut

    # Get net_name from parent context
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    debug_net = _get_debug_net(ctx, dut, net_name)

    # Use service client (required)
    if not is_service_available(dut, username):
        click.secho("Error: Debug service not available on gateway", fg='red', err=True)
        ctx.exit(1)

    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Failed to establish SSH tunnel to debug service", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    # Auto-connect if not already connected
    # Memory reads require device to be halted, so check if we need to halt
    if not _is_connected(client):
        # Not connected - auto-connect with halt for memory reads
        click.secho("Auto-connecting to debugger (with halt for memory read)...", fg='cyan', dim=True)
        try:
            client.connect(debug_net, speed=None, force=False, halt=True)
            click.secho("Auto-connected and halted!", fg='cyan', dim=True)
        except Exception as e:
            click.secho(f"Error: Failed to auto-connect to debugger", fg='red', err=True)
            click.secho(f"Details: {e}", fg='red', err=True)
            client.close()
            ctx.exit(1)

    # Validate memory address range (32-bit systems)
    max_address = 0xFFFFFFFF
    if start_addr > max_address or (start_addr + length) > max_address + 1:
        click.secho(f"Warning: Memory address 0x{start_addr:x} may be invalid for 32-bit system", fg='yellow', err=True)
        click.secho(f"Maximum valid address is 0x{max_address:x}", fg='yellow', err=True)
        if not click.confirm("Continue anyway?", default=False):
            _auto_disconnect(client, debug_net, no_disconnect=no_disconnect)
            client.close()
            ctx.exit(0)

    try:
        memory_data = client.read_memory(debug_net, start_addr, length)
    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg or "No debugger connection" in error_msg:
            click.secho("Error: No debugger connection found. Connect first with: lager debug <net> connect --box <box> --halt", fg='red', err=True)
            click.secho("Note: Device must be halted for memory reads to work reliably", fg='yellow', err=True)
        else:
            click.secho(f"Error reading memory: {e}", fg='red', err=True)
        _auto_disconnect(client, debug_net, no_disconnect=no_disconnect)
        client.close()
        ctx.exit(1)

    # Check if memory read returned empty data (silent failure)
    if not memory_data or len(memory_data) == 0:
        click.secho(f"Error: Memory read returned no data from address 0x{start_addr:08x}", fg='red', err=True)
        click.secho("Possible causes:", fg='yellow', err=True)
        click.secho("  • Device is not halted (use: lager debug <net> connect --box <box> --halt)", fg='yellow', err=True)
        click.secho("  • Invalid memory address for this device", fg='yellow', err=True)
        click.secho("  • Memory region is not accessible or not mapped", fg='yellow', err=True)
        _auto_disconnect(client, debug_net, no_disconnect=no_disconnect)
        client.close()
        ctx.exit(1)

    # Format output
    if json_output:
        result = {
            "start_addr": hex(start_addr),
            "length": length,
            "data": []
        }
        for i in range(0, len(memory_data), 8):
            chunk = memory_data[i:i+8]
            hex_values = '\t'.join([f'0x{b:02x}' for b in chunk])
            result["data"].append(f'{hex(start_addr + i)}:\t{hex_values}')
        click.echo(json.dumps(result, indent=2))
    else:
        for i in range(0, len(memory_data), 8):
            chunk = memory_data[i:i+8]
            hex_values = '\t'.join([f'0x{b:02x}' for b in chunk])
            click.echo(f'{hex(start_addr + i)}:\t{hex_values}')

    # Auto-disconnect to free hardware resources for other operations (e.g., UART)
    _auto_disconnect(client, debug_net, no_disconnect=no_disconnect)
    client.close()

# Note: gdbserver command removed as it relies on WebSocket tunneling
# For direct debugging, users should use gdb directly with the J-Link GDB server
# running on the gateway, which can be accessed via SSH port forwarding if needed

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def status(ctx, box, dut):
    """Show debug net status and information"""
    # Use box or dut (box takes precedence)
    dut = box or dut


    # Get net_name from parent context
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    debug_net = _get_debug_net(ctx, dut, net_name)

    # Use service client (required)
    if not is_service_available(dut, username):
        click.secho("Error: Debug service not available on gateway", fg='red', err=True)
        ctx.exit(1)

    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Failed to establish SSH tunnel to debug service", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    # Get info from service
    info_data = client.get_info(debug_net)

    click.echo(f"Debug Net Information:")
    click.echo(f"  Name: {info_data.get('net_name')}")
    click.echo(f"  Device Type: {info_data.get('device')}")
    click.echo(f"  Architecture: {info_data.get('arch')}")
    click.echo(f"  Probe: {info_data.get('probe')}")
    click.echo(f"  Connected: {info_data.get('connected')}")
    click.echo()

    client.close()

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--timeout', type=int, default=None, help='Read timeout in seconds (default: continuous until Ctrl+C)')
@click.option('--channel', type=int, default=0, help='RTT channel (0 or 1)', show_default=True)
@click.option('-e', '--elf', type=click.Path(exists=True), help='ELF file for defmt-print decoding')
def rtt(ctx, box,
 dut, timeout, channel, elf):
    """Stream RTT logs from target

    Uses the fast debug service API endpoint with HTTP chunked transfer encoding
    for real-time streaming. Supports piping to defmt-print for decoding.

    Examples:
        # Stream raw RTT output
        lager debug debug1 rtt --box TEST-4

        # Stream with defmt decoding (built-in)
        lager debug debug1 rtt --box TEST-4 -e firmware.elf

        # Stream with defmt decoding (piped)
        lager debug debug1 rtt --box TEST-4 | defmt-print -e firmware.elf

        # Stream with timeout
        lager debug debug1 rtt --box TEST-4 --timeout 10
    """
    import sys
    import subprocess
    import shutil
    from pathlib import Path

    # Use box or dut (box takes precedence)
    dut = box or dut

    # Get net_name from parent context
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    debug_net = _get_debug_net(ctx, dut, net_name)

    # Validate ELF file path if provided
    if elf:
        elf_path = Path(elf)
        if not elf_path.exists():
            click.secho(f"Error: ELF file not found: {elf}", fg='red', err=True)
            click.secho("\nTip: Make sure the path is correct. Common locations:", fg='yellow', err=True)
            click.secho("  • test/firmware.elf", fg='yellow', err=True)
            click.secho("  • ./target/thumbv7em-none-eabi/debug/firmware", fg='yellow', err=True)
            ctx.exit(1)

        if not elf_path.is_file():
            click.secho(f"Error: ELF path is not a file: {elf}", fg='red', err=True)
            ctx.exit(1)

    # Ensure SSH tunnel and get client
    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Failed to establish SSH tunnel to debug service", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    # Auto-connect if not already connected
    if not _auto_connect_if_needed(client, debug_net, ctx):
        client.close()
        ctx.exit(1)

    # If -e flag is provided, pipe to defmt-print
    defmt_process = None
    output_target = sys.stdout.buffer  # Default: write to stdout
    if elf:
        # Check if defmt-print is available
        if not shutil.which('defmt-print'):
            click.secho('Error: defmt-print not found. Install it with: cargo install defmt-print', fg='red', err=True)
            ctx.exit(1)

        # Start defmt-print as a subprocess
        defmt_cmd = ['defmt-print', '-e', elf]
        defmt_process = subprocess.Popen(
            defmt_cmd,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr
        )

        # Redirect output to defmt-print's stdin
        output_target = defmt_process.stdin

    try:
        # Stream RTT data using the fast API endpoint
        bytes_received = 0
        for chunk in client.rtt(channel=channel, timeout=timeout):
            # Write to output (either stdout or defmt-print stdin)
            output_target.write(chunk)
            output_target.flush()
            bytes_received += len(chunk)

        # If stream ended with no data (or very little data), provide guidance
        if bytes_received < 10:  # Less than 10 bytes suggests immediate EOF
            click.secho("\nRTT stream ended with no data received", fg='yellow', err=True)
            click.secho("\nPossible causes:", fg='yellow', err=True)
            click.secho("  1. Device firmware has not initialized RTT yet", fg='yellow', err=True)
            click.secho("  2. Device is halted (not running)", fg='yellow', err=True)
            click.secho("  3. Firmware doesn't have RTT enabled", fg='yellow', err=True)
            click.secho("\nRecommended solutions:", fg='yellow', err=True)
            click.secho("  • Use --rtt-reset to capture boot sequence:", fg='green', err=True)
            click.secho(f"    lager debug {net_name} connect --rtt-reset --box {dut} | defmt-print -e firmware.elf", fg='green', err=True)
            click.secho("  • Or ensure device is running before starting RTT:", fg='green', err=True)
            click.secho(f"    lager debug {net_name} reset --box {dut}", fg='green', err=True)
            click.secho(f"    sleep 2", fg='green', err=True)
            click.secho(f"    lager debug {net_name} rtt --box {dut} | defmt-print -e firmware.elf", fg='green', err=True)
    except KeyboardInterrupt:
        # User pressed Ctrl+C - graceful exit
        pass
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors with helpful messages
        if e.response.status_code == 500:
            error_text = e.response.text if hasattr(e.response, 'text') else str(e)
            # Check if the error message indicates an invalid channel
            if 'channel' in error_text.lower() and 'not available' in error_text.lower():
                click.secho(f"\nRTT stream error: Channel {channel} is not available", fg='red', err=True)
                click.secho(f"Try channel 0 instead: lager debug {net_name} rtt --box {dut} --channel 0", fg='yellow', err=True)
            else:
                click.secho(f"\nRTT stream error: {e}", fg='red', err=True)
                click.secho("Device may not have RTT enabled or RTT control block not found", fg='yellow', err=True)
        elif "Connection refused" in str(e) or "already is an active connection" in str(e):
            click.secho("\nRTT stream error: An RTT connection is already active", fg='red', err=True)
            click.secho("To fix this:", fg='yellow', err=True)
            click.secho("  1. Wait 1-2 seconds for the previous connection to close", fg='yellow', err=True)
            click.secho("  2. Or disconnect and reconnect: lager debug <net> disconnect --box <box>", fg='yellow', err=True)
            click.secho("  3. Then try again", fg='yellow', err=True)
        else:
            click.secho(f"\nRTT stream error: {e}", fg='red', err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"\nRTT stream error: {e}", fg='red', err=True)
        ctx.exit(1)
    finally:
        # Clean up defmt-print process if we started it
        if defmt_process:
            try:
                defmt_process.stdin.close()
                defmt_process.wait(timeout=2)
            except:
                defmt_process.kill()
                defmt_process.wait()

        # Auto-disconnect after RTT streaming completes
        _auto_disconnect(client, debug_net, no_disconnect=False)

        # Ensure client session is properly closed to release RTT connection
        try:
            client.close()
        except:
            pass  # Ignore errors during cleanup

        # Longer delay to ensure RTT telnet connection is fully closed on gateway
        # The gateway service now waits 1.0s on its side for proper cleanup
        import time
        time.sleep(1.5)

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--verbose', is_flag=True, default=False,
              help='Show detailed health information')
def health(ctx, box,
 dut, verbose):
    """Check debug service health

    Shows service status, uptime, and resource usage to help diagnose issues.
    Use --verbose for GDB controller cache statistics and warnings.
    """

    # Use box or dut (box takes precedence)
    dut = box or dut

    # Get net_name from parent context (though health doesn't need it)
    net_name = getattr(ctx.obj, 'net_name', None)

    # Resolve DUT name to IP if needed
    dut, username = _resolve_dut_with_username(ctx, dut)

    # Ensure SSH tunnel
    tunnel = ensure_service_tunnel(dut, username)
    if not tunnel:
        click.secho("Error: Debug service not available on gateway", fg='red', err=True)
        ctx.exit(1)

    client = _get_service_client(dut)
    if not client:
        click.secho("Error: Failed to create debug service client", fg='red', err=True)
        ctx.exit(1)

    try:
        # Get health information
        health_data = client.get_service_health(detailed=verbose)

        # Display health information
        click.echo(f"Debug Service Health:")
        click.echo(f"  Status: ", nl=False)
        if health_data.get('status') == 'healthy':
            click.secho(f"{health_data['status']}", fg='green')
        else:
            click.secho(f"{health_data['status']}", fg='red')

        click.echo(f"  Version: {health_data.get('version', 'unknown')}")

        if verbose:
            # Detailed information
            uptime_days = health_data.get('service_uptime_days', 0)
            click.echo(f"  Uptime: {uptime_days:.2f} days ({health_data.get('service_uptime_seconds', 0):.0f}s)")
            click.echo(f"  J-Link Running: {health_data.get('jlink_running', False)}")
            if health_data.get('jlink_pid'):
                click.echo(f"  J-Link PID: {health_data['jlink_pid']}")
            click.echo(f"  GDB Controllers Cached: {health_data.get('gdb_controllers_cached', 0)}")
            click.echo(f"  GDB Max Use Count: {health_data.get('gdb_max_use_count', 0)}")
            click.echo(f"  Active Connections: {health_data.get('active_connections', 0)}")

            # Display warnings if any
            warnings = health_data.get('warnings', [])
            if warnings:
                click.echo()
                click.secho("Warnings:", fg='yellow')
                for warning in warnings:
                    click.secho(f"  ⚠ {warning}", fg='yellow')
        else:
            # Basic information
            uptime_seconds = health_data.get('uptime', 0)
            uptime_hours = uptime_seconds / 3600
            if uptime_hours < 1:
                click.echo(f"  Uptime: {uptime_seconds / 60:.1f} minutes")
            elif uptime_hours < 48:
                click.echo(f"  Uptime: {uptime_hours:.1f} hours")
            else:
                click.echo(f"  Uptime: {uptime_hours / 24:.1f} days")

    except Exception as e:
        click.secho(f"Error getting health: {e}", fg='red', err=True)
        ctx.exit(1)
    finally:
        client.close()

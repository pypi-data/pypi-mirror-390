"""
lager.uart.commands

Commands for DUT UART interaction
"""
from __future__ import annotations

import sys
import io
import json
from contextlib import redirect_stdout

import click
from texttable import Texttable

from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

UART_ROLE = "uart"


# ---------- helpers ----------

def _resolve_gateway(ctx, box, dut):
    """
    Resolve gateway/dut parameter to IP address.
    Returns tuple of (ip_address, dut_name) where dut_name is used for username lookup.
    """
    from ..dut_storage import get_dut_ip, get_dut_name_by_ip

    # Check if box is a local DUT name first
    if box:
        local_ip = get_dut_ip(box)
        if local_ip:
            return (local_ip, gateway)  # Return IP and DUT name for username lookup
        # If gateway is an IP, try to find its DUT name
        dut_name = get_dut_name_by_ip(gateway)
        return (gateway, dut_name)

    # Check if dut is a local DUT name
    if dut:
        local_ip = get_dut_ip(dut)
        if local_ip:
            return (local_ip, dut)  # Return IP and DUT name for username lookup
        # If dut is an IP, try to find its DUT name
        dut_name = get_dut_name_by_ip(dut)
        return (dut, dut_name)

    # Fallback to default gateway
    default_gw = get_default_gateway(ctx)
    dut_name = get_dut_name_by_ip(default_gw) if default_gw else None
    return (default_gw, dut_name)


def _run_net_py(ctx: click.Context, dut: str, *args: str) -> list[dict]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run_python_internal(
                ctx,
                get_impl_path("net.py"),
                dut,
                image="",
                env={},
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum="SIGTERM",
                timeout=0,
                detach=False,
                port=(),
                org=None,
                args=args or ("list",),
            )
    except SystemExit:
        pass
    raw = buf.getvalue() or "[]"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def _list_uart_nets(ctx, box):
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == UART_ROLE]


def _get_uart_net(ctx, box, netname):
    """Get a specific UART net by name"""
    nets = _list_uart_nets(ctx, gateway)
    for net in nets:
        if net.get("name") == netname:
            return net
    return None


def _run_query_instruments(ctx: click.Context, dut: str) -> list[dict]:
    """Query instruments on the gateway to get device information."""
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run_python_internal(
                ctx,
                get_impl_path("query_instruments.py"),
                dut,
                image="",
                env={},
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum="SIGTERM",
                timeout=0,
                detach=False,
                port=(),
                org=None,
                args=(),
            )
    except SystemExit:
        pass
    raw = buf.getvalue() or "[]"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def _find_device_path(usb_serial: str, inst_list: list[dict]) -> str | None:
    """Find the /dev/tty* path for a given USB serial number."""
    for inst in inst_list:
        # Check if this is a UART device
        channels = inst.get("channels", {})
        uart_channels = channels.get("uart", [])

        # If this device's UART channels include our serial number
        if usb_serial in uart_channels:
            # Return the tty_path if available
            return inst.get("tty_path")

    return None


def display_nets(ctx, box, netname: str | None):
    """Display UART nets with their configuration parameters."""
    uart_nets = _list_uart_nets(ctx, gateway)

    # Check if there are any UART nets to display
    if not uart_nets:
        click.secho("No UART nets configured.", fg="yellow", err=True)
        return

    # Query instruments to get current device paths
    inst_list = _run_query_instruments(ctx, gateway)

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(["t", "t", "t", "t", "t", "t", "t"])
    table.set_cols_align(["l", "l", "l", "l", "l", "l", "l"])
    table.add_row(["Name", "Bridge Type", "Device Path", "Port", "Baudrate", "Format", "Flow Control"])

    for rec in uart_nets:
        if netname is None or netname == rec.get("name"):
            name = rec.get("name", "")
            bridge_type = rec.get("instrument", "Unknown")
            usb_serial = rec.get("pin", "")
            port = rec.get("channel", "0")
            params = rec.get("params", {})

            # Look up current device path from instruments
            device_path = _find_device_path(usb_serial, inst_list)
            display_path = device_path if device_path else f"{usb_serial} (disconnected)"

            # Extract parameters with defaults
            baudrate = params.get("baudrate", "115200")
            bytesize = params.get("bytesize", "8")
            parity = params.get("parity", "none")
            stopbits = params.get("stopbits", "1")

            # Build format string (e.g., "8N1")
            parity_char = {"none": "N", "even": "E", "odd": "O", "mark": "M", "space": "S"}.get(parity, "N")
            format_str = f"{bytesize}{parity_char}{stopbits}"

            # Build flow control string
            flow_parts = []
            if params.get("xonxoff"):
                flow_parts.append("XON/XOFF")
            if params.get("rtscts"):
                flow_parts.append("RTS/CTS")
            if params.get("dsrdtr"):
                flow_parts.append("DSR/DTR")
            flow_control = ", ".join(flow_parts) if flow_parts else "None"

            table.add_row([name, bridge_type, display_path, port, str(baudrate), format_str, flow_control])

    result = table.draw()
    click.echo(result)


def _run_backend(ctx, dut, action: str, **params):
    """Run backend command and handle errors gracefully"""
    data = {
        "action": action,
        "params": params,
    }
    try:
        run_python_internal(
            ctx,
            get_impl_path("uart.py"),
            dut,
            image="",
            env=(f"LAGER_COMMAND_DATA={json.dumps(data)}",),
            passenv=(),
            kill=False,
            download=(),
            allow_overwrite=False,
            signum="SIGTERM",
            timeout=0,
            detach=False,
            port=(),
            org=None,
            args=(),
        )
    except SystemExit as e:
        # Backend errors are already printed by the backend
        # Just re-raise to preserve exit code
        if e.code != 0:
            raise


def _connect_uart_streaming(ctx, gateway_ip, dut_name, netname, overrides, interactive):
    """
    Connect to UART via direct SSH for streaming output (no buffering).
    Uses the UART dispatcher on the gateway for net-based configuration.

    Args:
        ctx: Click context
        gateway_ip: IP address of the gateway
        dut_name: DUT name for username lookup (can be None)
        netname: Name of the UART net to connect to
        overrides: Dictionary of serial port parameter overrides
        interactive: Whether to use interactive mode
    """
    import subprocess
    import shlex
    import sys
    from ..dut_storage import get_dut_user

    # Get username for this DUT (defaults to 'lagerdata' if not found)
    username = get_dut_user(dut_name) if dut_name else 'lagerdata'
    if not username:
        username = 'lagerdata'

    # Build Python script that uses the UART dispatcher
    action = "monitor_interactive" if interactive else "monitor"

    # Convert overrides dict to Python dict literal
    overrides_str = repr(overrides)

    uart_script = f'''
import sys
sys.path.insert(0, '/app/gateway_python')

from lager.uart.dispatcher import {action}

try:
    {action}({repr(netname)}, overrides={overrides_str})
except KeyboardInterrupt:
    print("\\n\\033[31mDisconnected\\033[0m", file=sys.stderr)
    sys.exit(0)
except Exception as e:
    print(f"\\033[31mError: {{e}}\\033[0m", file=sys.stderr)
    sys.exit(1)
'''

    # Build SSH command to run the script on the gateway with correct username
    ssh_host = f'{username}@{gateway_ip}'

    # Use docker exec with proper flags for interactive/non-interactive modes
    docker_flags = '-it' if interactive else '-i'
    docker_cmd = f'docker exec {docker_flags} python python3 -u -c {shlex.quote(uart_script)}'

    ssh_cmd = ['ssh', '-t', '-o', 'LogLevel=ERROR', ssh_host, docker_cmd]

    # Track the SSH process and terminal settings
    ssh_process = None
    old_tty_settings = None

    try:
        import termios
        import tty

        # For interactive sessions, use cbreak mode (less restrictive than raw)
        # This allows smoother typing while still sending chars immediately
        if interactive:
            try:
                old_tty_settings = termios.tcgetattr(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
            except Exception:
                old_tty_settings = None

        ssh_process = subprocess.Popen(ssh_cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        exit_code = ssh_process.wait()
    except KeyboardInterrupt:
        if ssh_process:
            try:
                ssh_process.terminate()
                ssh_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                ssh_process.kill()
        exit_code = 0
    except Exception as e:
        click.secho(f"Error connecting to UART: {e}", fg='red', err=True)
        if ssh_process:
            try:
                ssh_process.terminate()
            except Exception:
                pass
        exit_code = 1
    finally:
        if old_tty_settings:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_tty_settings)
            except Exception:
                pass

    ctx.exit(exit_code)


# ---------- CLI ----------

@click.command()
@click.argument("NETNAME", required=False)
@click.pass_context
# Target options
@click.option('--dut', required=False, help="Lagerbox name or IP")
# Serial parameter overrides
@click.option('--baudrate', type=int, help='Baudrate in baud (e.g., 9600, 115200)')
@click.option('--bytesize', type=click.Choice(['5', '6', '7', '8']), help='Number of data bits')
@click.option('--parity', type=click.Choice(['none', 'even', 'odd', 'mark', 'space']), help='Parity checking mode')
@click.option('--stopbits', type=click.Choice(['1', '1.5', '2']), help='Number of stop bits')
# Flow control options
@click.option('--xonxoff/--no-xonxoff', default=None, help='Software flow control (XON/XOFF)')
@click.option('--rtscts/--no-rtscts', default=None, help='Hardware flow control (RTS/CTS)')
@click.option('--dsrdtr/--no-dsrdtr', default=None, help='Hardware flow control (DSR/DTR)')
# Session options
@click.option('-i', '--interactive', is_flag=True, help='Enable input mode for typing to serial port', show_default=True)
@click.option('--opost/--no-opost', default=False, help=r'Convert \n to \r\n on output', show_default=True)
@click.option('--line-ending', type=click.Choice(['lf', 'crlf', 'cr']), default='lf', help='Line ending format (lf=\\n, crlf=\\r\\n, cr=\\r)', show_default=True)
@click.option("--box", required=False, help="Lagerbox name or IP")
def uart(ctx, netname, dut, baudrate, bytesize, parity, stopbits, xonxoff, rtscts, dsrdtr,
         interactive, opost, line_ending, box):
    """
    Connect to UART serial port
    """
    # Resolve box/dut to gateway IP
    target_gateway, dut_name = _resolve_gateway(ctx, box, dut)

    # If no netname provided, try to use default
    if not netname:
        netname = get_default_net(ctx, 'uart')

    # If still no netname, list all UART nets
    if not netname:
        display_nets(ctx, target_gateway, None)
        return

    # Validate flow control options
    if xonxoff and rtscts:
        raise click.UsageError('Cannot use --xonxoff and --rtscts simultaneously')

    # Load net configuration
    net_config = _get_uart_net(ctx, target_gateway, netname)
    if not net_config:
        click.secho(f"Error: UART net '{netname}' not found", fg='red', err=True)
        click.echo(f"\nRun 'lager uart' to see available UART nets on {target_gateway}", err=True)
        click.echo(f"\nTo create a new UART net:", err=True)
        click.echo(f"  1. Find available UART devices: lager instruments --box {target_gateway}", err=True)
        click.echo(f"  2. Create net: lager nets create {netname} uart <port> <bridge-serial>", err=True)
        ctx.exit(1)

    # Validate TTY for interactive mode
    if interactive:
        if not sys.stdin.isatty():
            click.secho('Error: stdin is not a TTY (cannot use --interactive)', fg='red', err=True)
            ctx.exit(1)
        if not sys.stdout.isatty():
            click.secho('Error: stdout is not a TTY (cannot use --interactive)', fg='red', err=True)
            ctx.exit(1)

    # Build parameter overrides
    overrides = {}
    if baudrate is not None:
        overrides['baudrate'] = baudrate
    if bytesize is not None:
        overrides['bytesize'] = int(bytesize)
    if parity is not None:
        overrides['parity'] = parity
    if stopbits is not None:
        overrides['stopbits'] = stopbits
    if xonxoff is not None:
        overrides['xonxoff'] = xonxoff
    if rtscts is not None:
        overrides['rtscts'] = rtscts
    if dsrdtr is not None:
        overrides['dsrdtr'] = dsrdtr

    # Always include opost setting
    overrides['opost'] = opost

    # Always include line_ending setting
    overrides['line_ending'] = line_ending

    # Show connection info
    net_params = net_config.get("params", {})
    final_baudrate = overrides.get('baudrate', net_params.get("baudrate", 115200))
    bridge_type = net_config.get("instrument", "unknown")
    usb_serial = net_config.get("pin", "unknown")
    usb_serial_short = usb_serial[:10] if len(usb_serial) > 10 else usb_serial
    port = net_config.get("channel", "0")
    mode_str = "interactive" if interactive else "read-only"

    click.echo(
        f"Connecting to {netname}: {bridge_type} (serial {usb_serial_short})",
        err=True,
    )

    # Check if this is a DirectIPSession (local gateway connection via Tailscale)
    from ..context import DirectIPSession
    session = ctx.obj.get_session_for_gateway(target_gateway)
    is_direct_ip = isinstance(session, DirectIPSession)

    # For DirectIPSession (local gateways), use direct SSH for streaming output
    if is_direct_ip:
        _connect_uart_streaming(
            ctx, target_gateway, dut_name, netname, overrides, interactive
        )
        return

    # For cloud-connected gateways, use websocket API (not yet implemented)
    click.secho('Error: UART nets currently only work with local IP gateways (DirectIPSession)', fg='red', err=True)
    click.secho('Use a local IP address or gateway ID with Tailscale connection', fg='yellow', err=True)
    ctx.exit(1)

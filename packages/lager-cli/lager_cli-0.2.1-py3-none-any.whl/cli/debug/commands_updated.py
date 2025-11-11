"""
    lager.debug.commands

    Debug an elf file - Updated for direct SSH execution
"""
import itertools
import click
import json
import io
from contextlib import redirect_stdout
from ..context import get_default_gateway, get_impl_path
from ..python.commands import run_python_internal
from ..paramtypes import MemoryAddressType, HexArrayType, BinfileType
from ..dut_storage import get_dut_ip

def _get_debug_net(ctx, dut, net_name=None):
    """
    Get debug net information for the DUT.
    If net_name is provided, use that specific net.
    Otherwise, find the first available debug net.
    """
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
            return target_net
        else:
            # Find first available debug net
            if not debug_nets:
                click.secho("No debug nets found. Create one with: lager nets create <name> debug <device_type> <address>", fg='red', err=True)
                ctx.exit(1)
            return debug_nets[0]

    except json.JSONDecodeError:
        click.secho("Failed to parse nets information.", fg='red', err=True)
        ctx.exit(1)

@click.group(name='debug')
def _debug():
    """
        Debug firmware and manage debug sessions
    """
    pass

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--net', required=False, help='Name of debug net to use')
def status(ctx, dut, net):
    """Get debug status for a specific debug net."""
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    debug_net = _get_debug_net(ctx, dut, net)
    device_type = debug_net.get('pin', 'unknown')

    run_python_internal(
        ctx, get_impl_path('debug_status.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(debug_net),)
    )

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--net', required=False, help='Name of debug net to use')
@click.option('--force/--no-force', is_flag=True, default=True,
              help='Disconnect debugger before reconnecting', show_default=True)
@click.option('--halt/--no-halt', is_flag=True, default=True,
              help='Halt the device when connecting', show_default=True)
def connect(ctx, dut, net, force, halt):
    """Connect to debugger using debug net configuration."""
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    debug_net = _get_debug_net(ctx, dut, net)
    device_type = debug_net.get('pin', 'unknown')

    connect_args = {
        'net': debug_net,
        'force': force,
        'halt': halt,
        'device_type': device_type
    }

    run_python_internal(
        ctx, get_impl_path('debug_connect.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(connect_args),)
    )

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--net', required=False, help='Name of debug net to use')
def disconnect(ctx, dut, net):
    """Disconnect from debugger."""
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    debug_net = _get_debug_net(ctx, dut, net)

    run_python_internal(
        ctx, get_impl_path('debug_disconnect.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(debug_net),)
    )

@_debug.command()
@click.pass_context
@click.argument('net')
@click.option('--dut', required=False, help='Gateway / DUT id')
@click.option('--hexfile', type=click.Path(exists=True))
@click.option('--binfile', multiple=True, type=BinfileType(exists=True))
def flash(ctx, net, dut, hexfile, binfile):
    """Flash firmware to a board using debug net."""
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    debug_net = _get_debug_net(ctx, dut, net)
    device_type = debug_net.get('pin', 'unknown')

    # Build flash arguments
    flash_args = {
        'net': debug_net,
        'device_type': device_type,
        'hexfile': None,
        'binfiles': []
    }

    # Read file contents
    if hexfile:
        with open(hexfile, 'rb') as f:
            flash_args['hexfile'] = {
                'filename': hexfile,
                'content': f.read().decode('latin-1')  # Preserve binary data
            }
    elif binfile:
        for bf in binfile:
            with open(bf.path, 'rb') as f:
                flash_args['binfiles'].append({
                    'filename': bf.path,
                    'address': bf.address,
                    'content': f.read().decode('latin-1')  # Preserve binary data
                })
    else:
        click.secho('Provide --hexfile or --binfile.', fg='red')
        ctx.exit(1)

    run_python_internal(
        ctx, get_impl_path('debug_flash.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(flash_args),)
    )

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--net', required=False, help='Name of debug net to use')
@click.option('--halt/--no-halt', is_flag=True, default=False,
              help='Halt the DUT after reset', show_default=True)
def reset(ctx, dut, net, halt):
    """Reset the target using debug net."""
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    debug_net = _get_debug_net(ctx, dut, net)
    device_type = debug_net.get('pin', 'unknown')

    reset_args = {
        'net': debug_net,
        'device_type': device_type,
        'halt': halt
    }

    run_python_internal(
        ctx, get_impl_path('debug_reset.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(reset_args),)
    )

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--net', required=False, help='Name of debug net to use')
@click.argument('start_addr', type=MemoryAddressType())
@click.argument('length', type=MemoryAddressType())
def memrd(ctx, dut, net, start_addr, length):
    """Read memory from target using debug net."""
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    debug_net = _get_debug_net(ctx, dut, net)
    device_type = debug_net.get('pin', 'unknown')

    memrd_args = {
        'net': debug_net,
        'device_type': device_type,
        'start_addr': start_addr,
        'length': length
    }

    run_python_internal(
        ctx, get_impl_path('debug_memrd.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(memrd_args),)
    )

# Note: gdbserver command removed as it relies on WebSocket tunneling
# For direct debugging, users should use gdb directly with the J-Link GDB server
# running on the gateway, which can be accessed via SSH port forwarding if needed

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--net', required=False, help='Name of debug net to use')
def info(ctx, dut, net):
    """Show debug net information and device details."""
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    debug_net = _get_debug_net(ctx, dut, net)

    click.echo(f"Debug Net Information:")
    click.echo(f"  Name: {debug_net.get('name')}")
    click.echo(f"  Device Type: {debug_net.get('pin', 'unknown')}")
    click.echo(f"  Instrument: {debug_net.get('instrument')}")
    click.echo(f"  Address: {debug_net.get('address')}")
    click.echo()

    # Get additional device info
    run_python_internal(
        ctx, get_impl_path('debug_info.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(debug_net),)
    )
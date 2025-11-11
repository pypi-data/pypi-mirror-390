"""
    Battery commands
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

BATTERY_ROLE = "battery"


# ---------- helpers ----------

def _require_netname(ctx) -> str:
    netname = getattr(ctx.obj, "netname", None)
    if not netname:
        raise click.UsageError(
            "NETNAME required.\n\n"
            "Usage: lager battery <NETNAME> <COMMAND>\n"
            "Example: lager battery battery1 soc 50"
        )
    return netname


def _resolve_gateway(ctx, box, dut):
    from ..dut_storage import get_dut_ip

    # Check if box is a local DUT name first
    if box:
        local_ip = get_dut_ip(box)
        if local_ip:
            return local_ip

    # Check if dut is a local DUT name
    if dut:
        local_ip = get_dut_ip(dut)
        if local_ip:
            return local_ip

    return box or dut or get_default_gateway(ctx)


def _run_net_py(ctx: click.Context, gateway: str, *args: str) -> list[dict]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run_python_internal(
                ctx,
                get_impl_path('net.py'),
                gateway,
                image='',
                env=(),
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum='SIGTERM',
                timeout=0,
                detach=False,
                port=(),
                org=None,
                args=args,
            )
        raw = buf.getvalue().strip()
        return [json.loads(line) for line in raw.split('\n') if line.strip()]
    except Exception:
        return []


def _list_battery_nets(ctx, box: str) -> None:
    nets = _run_net_py(ctx, box, 'list', '--role', BATTERY_ROLE, '--format', 'json')
    if not nets:
        click.echo("No battery nets found on this gateway.")
        return

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 't', 't'])
    table.set_cols_align(['l', 'l', 'r'])
    table.add_row(['NAME', 'ROLE', 'CHANNEL'])
    
    for net in nets:
        name = net.get('name', 'unknown')
        role = net.get('role', 'unknown')
        channel = net.get('channel', 'unknown')
        table.add_row([name, role, channel])
    
    click.echo(table.draw())


def _run_backend(ctx, box, action: str, **params):
    data = {
        'action': action,
        'params': params,
    }
    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
        gateway,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum='SIGTERM',
        timeout=0,
        detach=False,
        port=(),
        org=None,
        args=(),
    ) 

@click.group(invoke_without_command=True)
@click.argument('NETNAME', required=False)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def battery(ctx, box, dut, netname):
    """
        Control battery simulator settings and output
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'battery')

    if netname is not None:
        ctx.obj.netname = netname

    # Only resolve gateway if no subcommand (listing nets)
    # When there's a subcommand, let it handle gateway resolution with its own --dut option
    if ctx.invoked_subcommand is None:
        gateway = _resolve_gateway(ctx, box, dut)
        _list_battery_nets(ctx, box)   

@battery.command()
@click.argument('MODE_TYPE', required=False, type=click.Choice(('static', 'dynamic')))
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def mode(ctx, box, dut, mode_type):
    """
        Set (or read) battery simulation mode type
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_mode', netname=netname, mode_type=mode_type)

@battery.command(name='set')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def set_mode(ctx, box, dut):
    """
        Initialize battery simulator mode
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_to_battery_mode', netname=netname)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def soc(ctx, box, dut, value):
    """
        Set (or read) battery state of charge in percent (%)
    """   
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_soc', netname=netname, value=value)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def voc(ctx, box, dut, value):
    """
        Set (or read) battery open circuit voltage in volts (V)
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_voc', netname=netname, value=value)

@battery.command(name='batt-full')
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def batt_full(ctx, box, dut, value):
    """
        Set (or read) battery fully charged voltage in volts (V)
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_volt_full', netname=netname, value=value)

@battery.command(name='batt-empty')
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def batt_empty(ctx, box, dut, value):
    """
        Set (or read) battery fully discharged voltage in volts (V)
    """      
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_volt_empty', netname=netname, value=value)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def capacity(ctx, box, dut, value):
    """
        Set (or read) battery capacity limit in amp-hours (Ah)
    """      
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_capacity', netname=netname, value=value)

@battery.command(name='current-limit')
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def current_limit(ctx, box, dut, value):
    """
        Set (or read) maximum charge/discharge current in amps (A)
    """       
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_current_limit', netname=netname, value=value)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def ovp(ctx, box, dut, value):
    """
        Set (or read) over voltage protection limit in volts (V)
    """   
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_ovp', netname=netname, value=value)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def ocp(ctx, box, dut, value):
    """
        Set (or read) over current protection limit in amps (A)
    """     
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_ocp', netname=netname, value=value)

@battery.command()
@click.argument('PARTNUMBER', required=False)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def model(ctx, box, dut, partnumber):
    """
        Set (or read) battery model (18650, nimh, lead-acid, etc.)
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_model', netname=netname, partnumber=partnumber)

@battery.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def state(ctx, box, dut):
    """
        Get battery state (comprehensive status)
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'state', netname=netname) 

@battery.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def enable(ctx, box, dut, yes):
    """
        Enable battery simulator output
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if yes or click.confirm(f"Enable Net?", default=False):
        pass
    else:
        click.echo("Aborting")
        return

    _run_backend(ctx, gateway, 'enable_battery', netname=netname) 

@battery.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def disable(ctx, box, dut, yes):
    """
        Disable battery simulator output
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if yes or click.confirm(f"Disable Net?", default=True):
        pass
    else:
        click.echo("Aborting")
        return

    _run_backend(ctx, gateway, 'disable_battery', netname=netname)

# --------- CLEAR COMMANDS ---------

@battery.command(name='clear')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def clear_both(ctx, box, dut):
    """
        Clear protection trip conditions (OVP/OCP)
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'clear', netname=netname)

# NEW: clear-ovp (targets OVP only if backend supports it; otherwise acts like clear)
@battery.command(name='clear-ovp')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def clear_ovp(ctx, box, dut):
    """
        Clear OVP trip condition
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'clear_ovp', netname=netname)

# NEW: clear-ocp (targets OCP only if backend supports it; otherwise acts like clear)
@battery.command(name='clear-ocp')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def clear_ocp(ctx, box, dut):
    """
        Clear OCP trip condition
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'clear_ocp', netname=netname)

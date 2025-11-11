"""
    Scope commands (analog nets using local nets)
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

SCOPE_ROLE = "scope"


# ---------- helpers ----------

def _require_netname(ctx) -> str:
    netname = getattr(ctx.obj, "netname", None)
    if not netname:
        raise click.UsageError(
            "NETNAME required.\n\n"
            "Usage: lager scope <NETNAME> <COMMAND>\n"
            "Example: lager scope scope1 disable"
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


def _list_scope_nets(ctx, box):
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == SCOPE_ROLE]


def validate_net(ctx, box, netname, net_role):
    """Validate that a net exists and has the specified role using locally saved nets"""
    nets = _run_net_py(ctx, box, "list")
    for net in nets:
        if net.get("name") == netname and net.get("role") == net_role:
            return True
    return False


def display_nets(ctx, box, netname: str | None):
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(["t", "t", "t"])
    table.set_cols_align(["l", "l", "r"])
    table.add_row(["name", "type", "channel"])

    for rec in _list_scope_nets(ctx, gateway):
        if netname is None or netname == rec.get("name"):
            # Local schema exposes top-level "pin"; that's the channel string.
            table.add_row([rec.get("name"), rec.get("role"), rec.get("pin")])

    click.secho(table.draw(), fg="green")


def _run_backend(ctx, dut, action: str, **params):
    """Run backend command for scope operations"""
    data = {
        "action": action,
        "mcu": params.pop("mcu", None),
        "params": params,
    }
    run_python_internal(
        ctx,
        get_impl_path("enable_disable.py"),
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


# ---------- CLI ----------

@click.group(invoke_without_command=True)
@click.argument("NETNAME", required=False)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def scope(ctx, box, dut, netname):
    """Control oscilloscope settings"""
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'scope')

    if netname is not None:
        ctx.obj.netname = netname

    if ctx.invoked_subcommand is None:
        gw = _resolve_gateway(ctx, box, dut)
        display_nets(ctx, gw, None)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def disable(ctx, box, dut, mcu):
    """Disable scope channel"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "disable_net", netname=netname, mcu=mcu)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def enable(ctx, box, dut, mcu):
    """Enable scope channel"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "enable_net", netname=netname, mcu=mcu)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def start(ctx, box, dut, mcu):
    """Start waveform capture"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "start_capture", netname=netname, mcu=mcu)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def start_single(ctx, box, dut, mcu):
    """Start single waveform capture"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "start_single", netname=netname, mcu=mcu)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def stop(ctx, box, dut, mcu):
    """Stop waveform capture"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "stop_capture", netname=netname, mcu=mcu)


@scope.group()
def measure():
    """Measure waveform characteristics"""
    pass


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", default=False, type=click.BOOL, help="Display measurement on screen")
@click.option("--cursor", default=False, type=click.BOOL, help="Enable measurement cursor")
def period(ctx, mcu, box, dut, display, cursor):
    """Measure waveform period"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_period",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("measurement.py"),
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


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", default=False, type=click.BOOL, help="Display measurement on screen")
@click.option("--cursor", default=False, type=click.BOOL, help="Enable measurement cursor")
def freq(ctx, mcu, box, dut, display, cursor):
    """Measure waveform frequency"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_freq",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("measurement.py"),
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


@scope.group()
def trigger():
    """Configure trigger settings"""
    pass


MODE_CHOICES = click.Choice(("normal", "auto", "single"))
COUPLING_CHOICES = click.Choice(("dc", "ac", "low_freq_rej", "high_freq_rej"))


@trigger.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mode", default="normal", type=MODE_CHOICES, help="Trigger mode", show_default=True)
@click.option("--coupling", default="dc", type=COUPLING_CHOICES, help="Coupling mode", show_default=True)
@click.option("--source", required=False, help="Trigger source", metavar="NET")
@click.option("--slope", type=click.Choice(("rising", "falling", "both")), help="Trigger slope")
@click.option("--level", type=click.FLOAT, help="Trigger level")
def edge(ctx, mcu, box, dut, mode, coupling, source, slope, level):
    """Set edge trigger"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "trigger_edge",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "mode": mode,
            "coupling": coupling,
            "source": source,
            "slope": slope,
            "level": level,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("trigger.py"),
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


@scope.group()
def cursor():
    """Control scope cursor"""
    pass


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--x", required=False, type=click.FLOAT, help="Cursor A x coordinate")
@click.option("--y", required=False, type=click.FLOAT, help="Cursor A y coordinate")
def set_a(ctx, box, dut, mcu, x, y):
    """Set cursor A position"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "set_a",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "x": x,
            "y": y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("cursor.py"),
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


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--x", required=False, type=click.FLOAT, help="Cursor B x coordinate")
@click.option("--y", required=False, type=click.FLOAT, help="Cursor B y coordinate")
def set_b(ctx, box, dut, mcu, x, y):
    """Set cursor B position"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "set_b",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "x": x,
            "y": y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("cursor.py"),
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


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--del-x", required=False, type=click.FLOAT, help="Shift A x coordinate")
@click.option("--del-y", required=False, type=click.FLOAT, help="Shift A y coordinate")
def move_a(ctx, box, dut, mcu, del_x, del_y):
    """Shift cursor A position"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "move_a",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "del_x": del_x,
            "del_y": del_y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("cursor.py"),
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


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--del-x", required=False, type=click.FLOAT, help="Shift B x coordinate")
@click.option("--del-y", required=False, type=click.FLOAT, help="Shift B y coordinate")
def move_b(ctx, box, dut, mcu, del_x, del_y):
    """Shift cursor B position"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "move_b",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "del_x": del_x,
            "del_y": del_y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("cursor.py"),
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


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def hide(ctx, box, dut, mcu):
    """Hide cursor"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "hide_cursor",
        "mcu": mcu,
        "params": {
            "netname": netname,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("cursor.py"),
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
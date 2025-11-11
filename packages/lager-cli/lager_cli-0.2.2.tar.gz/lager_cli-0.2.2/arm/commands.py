import os
import json
from pathlib import Path
import click
from ..context import get_default_gateway, get_default_net
from ..python.commands import run_python_internal

def _impl_arm_path() -> str:
    return str(Path(__file__).resolve().parent.parent / "impl" / "arm.py")

def _gateway_image() -> str:
    return os.environ.get("LAGER_GATEWAY_IMAGE", "python")

def _run(ctx, payload: dict, box: str):
    run_python_internal(
        ctx=ctx,
        runnable=_impl_arm_path(),
        gateway=gateway,
        image=_gateway_image(),
        env=(),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum="SIGTERM",
        timeout=30,  # 30 second timeout to prevent hanging
        detach=False,
        port=(),
        org=None,
        args=[json.dumps(payload)],
    )

def _require_netname(ctx) -> str:
    net = getattr(ctx.obj, "arm_netname", None) if ctx.obj is not None else None
    if not net:
        raise click.UsageError("NETNAME is required for this command.")
    return net

def _resolve_gateway_for_command(ctx, dut):
    """Resolve gateway from command-level --dut option or group-level stored gateway"""
    if dut:
        from ..dut_storage import get_dut_ip
        local_ip = get_dut_ip(dut)
        return local_ip if local_ip else dut
    # Fall back to gateway stored by the group command
    return getattr(ctx.obj, "gateway", None) or get_default_gateway(ctx)

@click.group(
    name="arm",
    context_settings={"max_content_width": 100},
    help="Control robot arm position and movement (units: mm)",
)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.argument("netname", required=False)
def arm(ctx, box,
 dut, netname):
    """
    Usage: lager arm [OPTIONS] [NETNAME] COMMAND [ARGS]
    """
    # Preserve whatever the top-level CLI stored in ctx.obj (don't replace with dict)
    if ctx.obj is None:
        # create a simple attribute container without nuking future expectations
        class _Obj: pass
        ctx.obj = _Obj()

    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'arm')

    # Store arm-specific fields as attributes so get_default_gateway(ctx) still works
    setattr(ctx.obj, "arm_netname", netname)

    # Only resolve gateway if dut is provided at group level
    # Otherwise, let subcommands resolve it
    if dut:
        from ..dut_storage import get_dut_ip
        local_ip = get_dut_ip(dut)
        gw = local_ip if local_ip else dut
        setattr(ctx.obj, "gateway", gw)
    else:
        # Don't set gateway - let subcommands handle it
        setattr(ctx.obj, "gateway", None)

@arm.command(name="position", help="Print current arm position (mm)")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def position(ctx, box, dut):

    # Use box or dut (box takes precedence)
    dut = box or dut
    net = _require_netname(ctx)
    gw = _resolve_gateway_for_command(ctx, dut)
    _run(ctx, {"netname": net, "command": "position"}, gw)

@arm.command(name="move", help="Move arm to absolute XYZ position (mm)")
@click.option("--timeout", type=click.FloatRange(min=0.0), default=5.0, show_default=True, help="Move timeout (s)")
@click.argument("x", type=float, required=True)
@click.argument("y", type=float, required=True)
@click.argument("z", type=float, required=True)
@click.option("--yes", is_flag=True, help="Confirm the action without prompting")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def move(ctx, timeout, x, y, z, yes,  box, dut):
    if not yes and not click.confirm(f"Move arm to specified coordinates?", default=False):
        click.echo("Aborting")
        return
    net = _require_netname(ctx)
    gw = _resolve_gateway_for_command(ctx, dut)
    _run(ctx, {"netname": net, "command": "move", "x": x, "y": y, "z": z, "timeout": timeout}, gw)

@arm.command(name="move-by", help="Move arm by dX dY dZ (mm)")
@click.option("--timeout", type=click.FloatRange(min=0.0), default=5.0, show_default=True, help="Move timeout (s)")
@click.argument("dx", type=float, required=False, default=0.0)
@click.argument("dy", type=float, required=False, default=0.0)
@click.argument("dz", type=float, required=False, default=0.0)
@click.option("--yes", is_flag=True, help="Confirm the action without prompting")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def delta(ctx, timeout, dx, dy, dz, yes,  box, dut):
    if not yes and not click.confirm("Move arm by specified amount?", default=False):
        click.echo("Aborting")
        return
    net = _require_netname(ctx)
    gw = _resolve_gateway_for_command(ctx, dut)
    _run(ctx, {"netname": net, "command": "move_by", "dx": dx, "dy": dy, "dz": dz, "timeout": timeout}, gw)

@arm.command(name="go-home", help="Move arm to the home position (X0 Y300 Z0)")
@click.option("--yes", is_flag=True, help="Confirm the action without prompting")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def go_home(ctx, yes,  box, dut):
    if not yes and not click.confirm("Move arm to home position (X0 Y300 Z0)?", default=False):
        click.echo("Aborting")
        return
    net = _require_netname(ctx)
    gw = _resolve_gateway_for_command(ctx, dut)
    _run(ctx, {"netname": net, "command": "go_home"}, gw)

@arm.command(name="enable-motor", help="Enable arm motors")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def enable_motor(ctx, box, dut):

    # Use box or dut (box takes precedence)
    dut = box or dut
    net = _require_netname(ctx)
    gw = _resolve_gateway_for_command(ctx, dut)
    _run(ctx, {"netname": net, "command": "enable_motor"}, gw)

@arm.command(name="disable-motor", help="Disable arm motors")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def disable_motor(ctx, box, dut):
    net = _require_netname(ctx)
    gw = _resolve_gateway_for_command(ctx, dut)
    _run(ctx, {"netname": net, "command": "disable_motor"}, gw)

@arm.command(name="read-and-save-position", help="Save current position as calibration reference")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def read_and_save_position(ctx, box, dut):
    net = _require_netname(ctx)
    gw = _resolve_gateway_for_command(ctx, dut)
    _run(ctx, {"netname": net, "command": "read_and_save_position"}, gw)

@arm.command(name="set-acceleration", help="Set arm acceleration: acceleration, travel, retract")
@click.argument("acceleration", type=click.IntRange(min=0), required=True)
@click.argument("travel", type=click.IntRange(min=0), required=True)
@click.argument("retract", type=click.IntRange(min=0), required=False, default=60)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def set_acceleration(ctx, acceleration, travel, retract,  box, dut):
    net = _require_netname(ctx)
    gw = _resolve_gateway_for_command(ctx, dut)
    _run(
        ctx,
        {
            "netname": net,
            "command": "set_acceleration",
            "acceleration": int(acceleration),
            "travel_acceleration": int(travel),
            "retract_acceleration": int(retract),
        },
        gw,
    )

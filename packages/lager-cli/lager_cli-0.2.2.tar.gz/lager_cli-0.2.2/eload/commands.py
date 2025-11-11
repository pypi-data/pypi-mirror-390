"""Electronic Load CLI commands."""

import click
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal


def _resolve_gateway(ctx, dut):
    """Resolve DUT name to IP address if it's a local DUT."""
    from ..dut_storage import get_dut_ip

    # Get the gateway/dut identifier (either from parameter or default)
    gateway_id = dut or get_default_gateway(ctx)

    # Try to resolve it as a local DUT name
    if gateway_id:
        local_ip = get_dut_ip(gateway_id)
        if local_ip:
            return local_ip

    return gateway_id


def _run_eload_script(ctx, box: str, args: list):
    """Run eload implementation script with proper arguments."""
    run_python_internal(
        ctx,
        get_impl_path('eload.py'),
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
        args=tuple(args),
    )


@click.group(invoke_without_command=True)
@click.argument('netname', required=False)
@click.pass_context
def eload(ctx, netname):
    """Control electronic load settings and modes"""
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'eload')

    ctx.obj.netname = netname


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def cc(ctx, value,  box, dut):
    """Set (or read) constant current mode in amps (A)"""
    resolved_dut = _resolve_gateway(ctx, dut)
    netname = ctx.obj.netname
    args = ["cc", netname]
    if value is not None:
        args.append(str(value))
    _run_eload_script(ctx, resolved_dut, args)


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def cv(ctx, value,  box, dut):
    """Set (or read) constant voltage mode in volts (V)"""
    resolved_dut = _resolve_gateway(ctx, dut)
    netname = ctx.obj.netname
    args = ["cv", netname]
    if value is not None:
        args.append(str(value))
    _run_eload_script(ctx, resolved_dut, args)


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def cr(ctx, value,  box, dut):
    """Set (or read) constant resistance mode in ohms (Ω)"""
    resolved_dut = _resolve_gateway(ctx, dut)
    netname = ctx.obj.netname
    args = ["cr", netname]
    if value is not None:
        args.append(str(value))
    _run_eload_script(ctx, resolved_dut, args)


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def cp(ctx, value,  box, dut):
    """Set (or read) constant power mode in watts (W)"""
    resolved_dut = _resolve_gateway(ctx, dut)
    netname = ctx.obj.netname
    args = ["cp", netname]
    if value is not None:
        args.append(str(value))
    _run_eload_script(ctx, resolved_dut, args)


@eload.command()
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def state(ctx, box, dut):
    """Display electronic load state"""
    # Use box or dut (box takes precedence)
    dut = box or dut

    resolved_dut = _resolve_gateway(ctx, dut)
    netname = ctx.obj.netname
    args = ["state", netname]
    _run_eload_script(ctx, resolved_dut, args)

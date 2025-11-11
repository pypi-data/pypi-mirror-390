import os
import json
from pathlib import Path
import click
from ..context import get_default_gateway, get_default_net
from ..python.commands import run_python_internal

def _impl_watt_path() -> str:
    """Construct path to the implementation script for watt meter."""
    return str(Path(__file__).resolve().parent.parent / "impl" / "watt.py")

@click.command(name="watt", help="Read power from watt meter net (returns watts)")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.argument("netname", required=False)
def watt(ctx, box, dut, netname):
    """
    Read power consumption from a watt meter net.
    Returns power measurement in watts (W).

    Example:
        lager watt my_power_net
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'watt')
        if netname is None:
            raise click.UsageError(
                "NETNAME required. Either provide it as an argument or set a default with: "
                "lager defaults add --watt-net <name>"
            )

    from ..dut_storage import get_dut_ip

    # Strip whitespace from netname for better UX
    netname = netname.strip()

    # Check if box is a local DUT name first
    if box:
        local_ip = get_dut_ip(box)
        if local_ip:
            gateway = local_ip
    elif dut:
        local_ip = get_dut_ip(dut)
        if local_ip:
            gateway = local_ip
        else:
            gateway = dut
    else:
        gateway = get_default_gateway(ctx)

    gateway_image = os.environ.get("LAGER_GATEWAY_IMAGE", "python")

    payload = json.dumps({"netname": netname})

    run_python_internal(
        ctx=ctx,
        runnable=_impl_watt_path(),
        gateway=gateway,
        image=gateway_image,
        env=(),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum="SIGTERM",
        timeout=None,
        detach=False,
        port=(),
        org=None,
        args=[payload],
    )

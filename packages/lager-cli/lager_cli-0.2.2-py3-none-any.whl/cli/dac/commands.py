import os
import json
from pathlib import Path
import click
from ..context import get_default_gateway, get_default_net
from ..python.commands import run_python_internal

def _impl_dac_path() -> str:
    """Construct path to the implementation script for DAC."""
    return str(Path(__file__).resolve().parent.parent / "impl" / "dac.py")

@click.command(name="dac", help="Set or read DAC output voltage")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.argument("netname", required=False)
@click.argument("voltage", required=False)
def dac(ctx, box, dut, netname, voltage):
    """
    Set the digital-to-analog converter for a net on the DUT (value in volts).
    If no voltage is provided, this command reads the current DAC value.
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'dac')
        if netname is None:
            raise click.UsageError("NETNAME required. Either provide it as an argument or set a default with: lager defaults add --dac-net <name>")
    from ..dut_storage import get_dut_ip

    # Validate voltage if provided
    if voltage is not None and voltage.strip() == "":
        click.secho("Error: Voltage argument cannot be empty", fg='red', err=True)
        click.secho("Usage: lager dac <netname> [voltage]", fg='yellow', err=True)
        ctx.exit(1)

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
    payload = {"netname": netname}
    if voltage is not None:
        payload["voltage"] = voltage
    payload_json = json.dumps(payload)
    run_python_internal(
        ctx=ctx,
        runnable=_impl_dac_path(),
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
        args=[payload_json],
    )
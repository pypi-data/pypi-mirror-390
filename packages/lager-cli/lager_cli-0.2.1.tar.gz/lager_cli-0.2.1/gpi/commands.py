import os
from pathlib import Path
import json
import click
from ..context import get_default_gateway, get_default_net
from ..python.commands import run_python_internal

def _impl_gpio_path() -> str:
    return str(Path(__file__).resolve().parent.parent / "impl" / "gpio.py")

@click.command(name="gpi", help="Read GPIO input state (0 or 1)")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.argument("netname", required=False)
def gpi(ctx, box, dut, netname):
    from ..dut_storage import get_dut_ip

    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'gpio')
        if netname is None:
            raise click.UsageError("NETNAME required. Either provide it as an argument or set a default with: lager defaults add --gpio-net <name>")

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

    payload = json.dumps({"netname": netname, "action": "input"})

    run_python_internal(
        ctx=ctx,
        runnable=_impl_gpio_path(),
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

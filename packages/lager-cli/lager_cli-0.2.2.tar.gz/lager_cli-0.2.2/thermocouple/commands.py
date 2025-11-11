import os
import json
from pathlib import Path
import click
from ..context import get_default_gateway, get_default_net
from ..python.commands import run_python_internal

def _impl_thermocouple_path() -> str:
    return str(Path(__file__).resolve().parent.parent / "impl" / "thermocouple.py")

@click.command(name="thermocouple", help="Read thermocouple temperature in degrees Celsius (°C)")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.argument("netname", required=False)
def thermocouple(ctx, box, dut, netname):
    from ..dut_storage import get_dut_ip

    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'thermocouple')
        if netname is None:
            raise click.UsageError("NETNAME required. Either provide it as an argument or set a default with: lager defaults add --thermocouple-net <name>")

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
        runnable=_impl_thermocouple_path(),
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




# """
#     lager.thermocouple.commands

#     Thermocouple commands
# """

# import click
# from ..context import get_default_gateway
# from ..context import get_impl_path
# from ..python.commands import run_python_internal

# @click.command()
# @click.pass_context
# @click.option("--box", required=False, help="Lagerbox name or IP")
# @click.option('--dut', required=False, hidden=True, help='ID of DUT')
# @click.argument('NET', required=True)
# def thermocouple(ctx, box, dut, net):
#     """
#         Read the thermocouple for a net the gateway. Result is in degrees C
#     """
#     gateway = gateway or dut
#     if gateway is None:
#         gateway = get_default_gateway(ctx)

#     run_python_internal(
#         ctx,
#         get_impl_path('thermocouple.py'),
#         dut,
#         image='',
#         env=(),
#         passenv=(),
#         kill=False,
#         download=(),
#         allow_overwrite=False,
#         signum='SIGTERM',
#         timeout=0,
#         detach=False,
#         port=(),
#         org=None,
#         args=(net,),
#     )


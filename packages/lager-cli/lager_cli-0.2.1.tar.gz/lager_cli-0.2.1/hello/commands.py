"""
    lager.hello.commands

    Say hello to gateway
"""
import click
from ..context import get_impl_path
from ..python.commands import run_python_internal
from ..dut_storage import resolve_and_validate_dut_with_name

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def hello(ctx, box, dut):
    """Test gateway connectivity"""
    # Use box or dut (box takes precedence)
    dut = box or dut

    # Resolve and validate the DUT, keeping track of the original name
    original_dut_name = dut  # Save for username lookup
    resolved_dut, dut_name = resolve_and_validate_dut_with_name(ctx, dut)

    run_python_internal(
        ctx,
        get_impl_path('hello.py'),
        resolved_dut,
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
        args=(resolved_dut,),  # Pass the resolved IP as an argument
        dut_name=dut_name,  # Pass DUT name for username lookup
    )

# """
#     lager.hello.commands

#     Say hello to gateway or DUT
# """
# import click
# from ..context import get_impl_path, get_default_gateway
# from ..python.commands import run_python_internal
# from ..dut_storage import get_dut_ip

# @click.command()
# @click.pass_context
# @click.option("--box", required=False, help="Lagerbox name or IP")
# @click.option('--dut', required=False, hidden=True, help='ID of DUT or saved DUT name')
# def hello(ctx, dut):
#     """
#         Say hello to gateway or DUT
#     """
#     dut_name = dut  # Save the original DUT name
#     dut_ip = None
#
#     # If dut is provided, check if it's a saved DUT name
#     if dut:
#         saved_ip = get_dut_ip(dut)
#         if saved_ip:
#             # Use the saved IP address for direct connection
#             dut_ip = saved_ip
#             dut = saved_ip
#     else:
#         # Get default gateway
#         dut = get_default_gateway(ctx)
#         # Check if the default gateway is a saved DUT name
#         if dut:
#             saved_ip = get_dut_ip(dut)
#             if saved_ip:
#                 dut_name = dut
#                 dut_ip = saved_ip
#                 dut = saved_ip
#
#     # For direct IP connections, try ping to verify connectivity
#     if dut_ip:
#         try:
#             import subprocess
#             # Try to ping the device to verify connectivity
#             result = subprocess.run([
#                 'ping', '-c', '3', '-W', '2000', dut_ip
#             ], capture_output=True, text=True, timeout=10)
#
#             if result.returncode == 0:
#                 if dut_name:
#                     click.echo(f'Hello from DUT {dut_name} ({dut_ip})! Your gateway is reachable via Tailscale.')
#                 else:
#                     click.echo(f'Hello from DUT {dut_ip}! Your gateway is reachable via Tailscale.')
#             else:
#                 click.secho(f'Failed to reach DUT {dut_ip}', fg='red', err=True)
#                 if result.stderr:
#                     click.echo(result.stderr.strip())
#         except subprocess.TimeoutExpired:
#             click.secho(f'Ping t o DUT {dut_ip} timed out', fg='red', err=True)
#         except Exception as e:
#             click.secho(f'Error connecting to DUT {dut_ip}: {str(e)}', fg='red', err=True)
#     else:
#         # Use the original Python script for regular gateway connection
#         # Pass DUT name and IP as arguments
#         args = []
#         if dut_name:
#             args.append(dut_name)
#         if dut:
#             args.append(dut)
#
#         run_python_internal(
#             ctx,
#             get_impl_path('hello.py'),
#             dut,
#             image='',
#             env=(),
#             passenv=(),
#             kill=False,
#             download=(),
#             allow_overwrite=False,
#             signum='SIGTERM',
#             timeout=0,
#             detach=False,
#             port=(),
#             org=None,
#             args=tuple(args),
#         )

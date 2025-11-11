"""
    lager.wifi.commands

    Commands for controlling WiFi - Updated for direct SSH execution
"""

import click
import json
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path
from ..python.commands import run_python_internal
from ..dut_storage import get_dut_ip

@click.group(name='wifi', hidden=True)
def _wifi():
    """
        Lager wifi commands
    """
    pass

@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
def status(ctx, box, dut):
    """
        Get the current WiFi Status of the gateway
    """
    # Use box or dut (box takes precedence)
    dut = box or dut

    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    status_args = {
        'action': 'status'
    }

    run_python_internal(
        ctx, get_impl_path('wifi.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(status_args),)
    )

@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--interface', required=False, help='Wireless interface to use', default='wlan0')
def access_points(ctx, box,
 dut, interface='wlan0'):
    """
        Get WiFi access points visible to the gateway
    """
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    scan_args = {
        'action': 'scan',
        'interface': interface
    }

    run_python_internal(
        ctx, get_impl_path('wifi.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(scan_args),)
    )

@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--ssid', required=True, help='SSID of the network to connect to')
@click.option('--interface', help='Wireless interface to use', default='wlan0', show_default=True)
@click.option('--password', required=False, help='Password of the network to connect to', default='')
def connect(ctx, box,
 dut, ssid, interface, password=''):
    """
        Connect the gateway to a new network
    """
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    wifi_config = {
        'ssid': ssid,
        'password': password,
        'interface': interface
    }

    run_python_internal(
        ctx, get_impl_path('wifi_connect.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(wifi_config),)
    )

@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting')
@click.argument('SSID', required=True)
def delete_connection(ctx, box,
 dut, yes, ssid):
    """
        Delete the specified network from the gateway
    """
    if not yes and not click.confirm('An ethernet connection will be required to bring the gateway back online. Proceed?', default=False):
        click.echo("Aborting")
        return

    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    run_python_internal(
        ctx, get_impl_path('wifi_disconnect.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(ssid,)
    )
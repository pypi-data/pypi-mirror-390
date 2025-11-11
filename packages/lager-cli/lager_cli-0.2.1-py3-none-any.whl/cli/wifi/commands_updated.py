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
@click.option('--dut', required=False, help='ID of DUT')
def status(ctx, dut):
    """
        Get the current WiFi Status of the gateway
    """
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    run_python_internal(
        ctx, get_impl_path('wifi_status.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None, args=()
    )

@_wifi.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--interface', required=False, help='Wireless interface to use')
def access_points(ctx, dut, interface=None):
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

    args = []
    if interface:
        args.append(interface)

    run_python_internal(
        ctx, get_impl_path('wifi_scan.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None, args=tuple(args)
    )

@_wifi.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--ssid', required=True, help='SSID of the network to connect to')
@click.option('--interface', help='Wireless interface to use', default='wlan0', show_default=True)
@click.option('--password', required=False, help='Password of the network to connect to', default='')
def connect(ctx, dut, ssid, interface, password=''):
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
@click.option('--dut', required=False, help='ID of DUT')
@click.confirmation_option(prompt='An ethernet connection will be required to bring the gateway back online. Proceed?')
@click.argument('SSID', required=True)
def delete_connection(ctx, dut, ssid):
    """
        Delete the specified network from the gateway
    """
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
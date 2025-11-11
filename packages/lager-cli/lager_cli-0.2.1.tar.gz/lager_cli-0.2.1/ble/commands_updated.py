"""
    lager.ble.commands

    Commands for BLE - Updated for direct SSH execution
"""
import re
import click
import json
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path
from ..python.commands import run_python_internal
from ..dut_storage import get_dut_ip

@click.group(name='ble')
def ble():
    """
        Lager BLE commands
    """
    pass

ADDRESS_NAME_RE = re.compile(r'\A([0-9A-F]{2}-){5}[0-9A-F]{2}\Z')

def check_name(device):
    return 0 if ADDRESS_NAME_RE.search(device['name']) else 1

def normalize_device(device):
    (address, data) = device
    item = {'address': address}
    manufacturer_data = data.get('manufacturer_data', {})
    for (k, v) in manufacturer_data.items():
        manufacturer_data[k] = bytes(v) if isinstance(v, list) else v
    item.update(data)
    return item

@ble.command('scan')
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--timeout', required=False, help='Total time gateway will spend scanning for devices', default=5.0, type=click.FLOAT, show_default=True)
@click.option('--name-contains', required=False, help='Filter devices to those whose name contains this string')
@click.option('--name-exact', required=False, help='Filter devices to those whose name matches this string')
@click.option('--verbose', required=False, is_flag=True, default=False, help='Verbose output (includes UUIDs)')
def scan(ctx, dut, timeout, name_contains, name_exact, verbose):
    """
        Scan for BLE devices via SSH execution
    """
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    scan_args = {
        'timeout': timeout,
        'name_contains': name_contains,
        'name_exact': name_exact,
        'verbose': verbose
    }

    run_python_internal(
        ctx, get_impl_path('ble_scan.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(scan_args),)
    )

@ble.command('info')
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('address', required=True)
def info(ctx, dut, address):
    """
        Get detailed information about a specific BLE device
    """
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    run_python_internal(
        ctx, get_impl_path('ble_info.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(address,)
    )

@ble.command('connect')
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('address', required=True)
def connect(ctx, dut, address):
    """
        Connect to a BLE device
    """
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    run_python_internal(
        ctx, get_impl_path('ble_connect.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(address,)
    )

@ble.command('disconnect')
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('address', required=True)
def disconnect(ctx, dut, address):
    """
        Disconnect from a BLE device
    """
    # Resolve DUT name to IP if needed
    if dut:
        saved_ip = get_dut_ip(dut)
        if saved_ip:
            dut = saved_ip
    else:
        dut = get_default_gateway(ctx)

    run_python_internal(
        ctx, get_impl_path('ble_disconnect.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(address,)
    )
"""
    lager.gateway.commands

    Gateway commands
"""
import collections
import os
import click
from ..context import get_default_gateway, get_impl_path
from ..python.commands import run_python_internal

@click.group(name='gateway', hidden=True)
def _gateway():
    """
        Lager gateway commands
    """
    pass

@_gateway.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='Lagerbox name or IP')
def hello(ctx, box, dut):
    """
        Say hello to gateway
    """
    gateway = box or dut
    run_python_internal(
        ctx,
        get_impl_path('hello.py'),
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
        args=(),
    )

@_gateway.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='Lagerbox name or IP')
@click.option('--model', required=False)
def serial_numbers(ctx, box, dut, model):
    """
        Get serial numbers of devices attached to gateway
    """
    gateway = box or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.serial_numbers(gateway, model)
    for device in resp.json()['devices']:
        device['serial'] = device['serial'].lstrip('0')
        click.echo('{vendor} {model}: {serial}'.format(**device))

@_gateway.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='Lagerbox name or IP')
def serial_ports(ctx, box, dut):
    """
        Get serial ports attached to gateway
    """
    gateway = box or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.serial_ports(gateway)
    style = ctx.obj.style
    for port in resp.json()['serial_ports']:
        click.echo('{} - {}'.format(style(port['device'], fg='green'), port['description']))

class HexParamType(click.ParamType):
    """
        Hexadecimal integer parameter
    """
    name = 'hex'

    def convert(self, value, param, ctx):
        """
            Parse string reprsentation of a hex integer
        """
        try:
            return int(value, 16)
        except ValueError:
            self.fail(f"{value} is not a valid hex integer", param, ctx)

    def __repr__(self):
        return 'HEX'

Binfile = collections.namedtuple('Binfile', ['path', 'address'])
class BinfileType(click.ParamType):
    """
        Type to represent a command line argument for a binfile (<path>,<address>)
    """
    envvar_list_splitter = os.path.pathsep
    name = 'binfile'

    def __init__(self, *args, exists=False, **kwargs):
        self.exists = exists
        super().__init__(*args, **kwargs)

    def convert(self, value, param, ctx):
        """
            Convert binfile param string into useable components
        """
        parts = value.rsplit(',', 1)
        if len(parts) != 2:
            self.fail(f'{value}. Syntax: --binfile <filename>,<address>', param, ctx)
        filename, address = parts
        path = click.Path(exists=self.exists).convert(filename, param, ctx)
        address = HexParamType().convert(address, param, ctx)

        return Binfile(path=path, address=address)

    def __repr__(self):
        return 'BINFILE'

def _status(ctx, box, mcu):
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    response = session.gateway_status(gateway, mcu).json()
    running = response['running']
    cmdline = response['cmdline']
    logfile = response['logfile']
    click.echo(f'Debugger running: {running}')
    if cmdline:
        click.echo('---- Debugger config ----')
        config = cmdline[3:-1]
        for i in range(0, len(config), 2):
            chunk = config[i:i+2]
            if chunk[0] == '-f':
                parts = chunk[1].split('/')
                click.echo(f'{parts[0]}: {parts[-1].rstrip(".cfg")}')
            elif chunk[0] == '-c':
                click.echo(chunk[1])

    if logfile:
        click.echo('---- Logs ----')
        click.echo(logfile)

@_gateway.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='Lagerbox name or IP')
@click.option('--mcu', required=False, default=None, help='MCU to query', type=click.INT)
def status(ctx, box, dut, mcu):
    """
        Get gateway debugger status
    """
    gateway = box or dut
    _status(ctx, gateway, mcu)


@_gateway.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='Lagerbox name or IP')
@click.option('--to', required=True, help='New name for gateway')
def rename(ctx, box, dut, to):
    """
        Rename a gateway
    """
    gateway = box or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    session.rename_gateway(gateway, to)

@_gateway.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='Lagerbox name or IP')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def reboot(ctx, box, dut, yes):
    """
        Reboot a gateway
    """
    gateway = box or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    if not yes:
        yes = click.confirm(f'This will reboot gateway {gateway}, are you sure?')

    if not yes:
        ctx.abort()

    session = ctx.obj.session
    session.reboot_gateway(gateway)


@_gateway.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='Lagerbox name or IP')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def shutdown(ctx, box, dut, yes):
    """
        Shut down a gateway
    """
    gateway = box or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    if not yes:
        yes = click.confirm(f'This will shut down gateway {gateway}, are you sure?')

    if not yes:
        ctx.abort()

    session = ctx.obj.session
    session.shutdown_gateway(gateway)

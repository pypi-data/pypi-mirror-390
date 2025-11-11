from __future__ import annotations

import itertools
import click

from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

# --------------------------------------------------------------------------- #
# helper: run the impl script on the remote gateway
# --------------------------------------------------------------------------- #
def _resolve_gateway(ctx: click.Context, dut: str | None) -> str:
    """
    Resolve DUT name to IP address if it's a local DUT, otherwise return as-is.
    """
    from ..dut_storage import get_dut_ip

    if dut:
        # Check if this is a local DUT name
        local_ip = get_dut_ip(dut)
        if local_ip:
            return local_ip
        return dut

    return get_default_gateway(ctx)


def _invoke_remote(
    ctx: click.Context,
    net_name: str,
    dut: str | None,
    command: str,
) -> None:
    """
    Copy `impl/usb.py` to the requested gateway and run:

        python usb.py <command> <net_name>

    The impl in turn invokes the backend dispatcher inside the gateway
    container.
    """
    resolved_dut = _resolve_gateway(ctx, dut)

    run_python_internal(
        ctx,
        get_impl_path("usb.py"),
        gateway=resolved_dut,
        image="",
        env={},
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum="SIGTERM",
        timeout=0,
        detach=False,
        port=(),
        org=None,
        args=(command, net_name),
    )


# --------------------------------------------------------------------------- #
# single command (verb comes **after** the net name)
# --------------------------------------------------------------------------- #
@click.command(
    "usb",
    help="Control programmable USB hub ports",
)
@click.argument("net_name", metavar="NET_NAME", required=False)
@click.argument(
    "command",
    metavar="COMMAND",
    type=click.Choice(["enable", "disable", "toggle"], case_sensitive=False),
)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def usb(
    ctx: click.Context,
    net_name: str,
    command: str,
    box: str | None,
    dut: str | None,
) -> None:  # pragma: no cover
    """
    Examples
    --------
    >>> lager usb usb1 enable  --box DUT
    >>> lager usb usb1 toggle  --box DUT
    >>> lager usb usb1 disable --box DUT
    """
    # Use provided net_name, or fall back to default if not provided
    if net_name is None:
        net_name = get_default_net(ctx, 'usb')
        if net_name is None:
            raise click.UsageError("NET_NAME required. Either provide it as an argument or set a default with: lager defaults add --usb-net <name>")

    # Use box or dut (box takes precedence)
    resolved_dut = box or dut
    _invoke_remote(ctx, net_name, resolved_dut, command.lower())
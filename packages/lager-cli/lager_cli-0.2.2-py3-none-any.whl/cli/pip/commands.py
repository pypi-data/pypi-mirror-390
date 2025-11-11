"""
    lager.pip.commands

    Commands for managing pip packages in lager python container
"""
import sys
import os
import re
import subprocess
import tempfile
import click
from ..context import get_default_gateway
from ..dut_storage import get_dut_ip

def _normalize_package_name(pkg):
    """Normalize package name for comparison (remove version specifiers)"""
    # Extract package name before version specifier
    match = re.match(r'^([a-zA-Z0-9\-_\.]+)', pkg)
    if match:
        return match.group(1).lower().replace('_', '-')
    return pkg.lower()

def _get_gateway_ip(ctx, dut, box):
    """Get the gateway IP from --dut, --box, or default"""
    target = dut or box
    if not target:
        target = get_default_gateway(ctx)
    if not target:
        click.secho('Error: No Lagerbox specified. Use --box <ip> or set a default.', fg='red', err=True)
        sys.exit(1)

    # Try to resolve DUT name to IP address
    ip = get_dut_ip(target)
    if ip:
        return ip

    # If not a DUT name, assume it's already an IP
    return target

def _read_remote_requirements(gateway_ip):
    """Read user requirements from remote gateway via SSH"""
    try:
        result = subprocess.run(
            ['ssh', '-o', 'ProxyCommand=none', '-o', 'ControlMaster=no', f'lagerdata@{gateway_ip}', 'cat ~/gateway/python/docker/user_requirements.txt 2>/dev/null || echo ""'],
            capture_output=True,
            text=True,
            timeout=10
        )

        packages = []
        for line in result.stdout.splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                packages.append(line)

        return packages
    except subprocess.TimeoutExpired:
        click.secho('Error: SSH connection timed out', fg='red', err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f'Error: Failed to read requirements from gateway: {e}', fg='red', err=True)
        sys.exit(1)

def _write_remote_requirements(gateway_ip, packages):
    """Write packages to remote gateway user requirements file via SSH"""
    try:
        # Create the file content
        content = '# User-installed packages via lager pip\n'
        content += '# This file is managed by lager pip install/uninstall commands\n'
        content += '# Add your custom packages below (one per line with optional version specifier)\n'
        content += '#\n'
        content += '# Examples:\n'
        content += '#   pandas==2.0.0\n'
        content += '#   numpy\n'
        content += '#   scipy>=1.10.0\n'
        content += '\n'
        for pkg in sorted(packages):
            content += f'{pkg}\n'

        # Write to temporary local file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name

        try:
            # Ensure directory exists on gateway
            subprocess.run(
                ['ssh', '-o', 'ProxyCommand=none', '-o', 'ControlMaster=no', f'lagerdata@{gateway_ip}', 'mkdir -p ~/gateway/python/docker'],
                check=True,
                capture_output=True,
                timeout=10
            )

            # Copy file to gateway
            subprocess.run(
                ['scp', '-o', 'ProxyCommand=none', '-o', 'ControlMaster=no', temp_path, f'lagerdata@{gateway_ip}:~/gateway/python/docker/user_requirements.txt'],
                check=True,
                capture_output=True,
                timeout=10
            )
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    except subprocess.TimeoutExpired:
        click.secho('Error: SSH/SCP operation timed out', fg='red', err=True)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        click.secho(f'Error: Failed to write requirements to gateway', fg='red', err=True)
        click.secho(f'Command failed with exit code {e.returncode}', fg='red', err=True)
        if e.stderr:
            click.secho(f'Error output: {e.stderr.decode()}', fg='red', err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f'Error: {e}', fg='red', err=True)
        sys.exit(1)

def _validate_packages(packages):
    """Validate that packages exist on PyPI before attempting installation"""
    import urllib.request
    import json

    invalid_packages = []

    for pkg in packages:
        # Extract package name (remove version specifiers)
        pkg_name = _normalize_package_name(pkg)

        try:
            # Check if package exists on PyPI
            url = f'https://pypi.org/pypi/{pkg_name}/json'
            req = urllib.request.Request(url, headers={'User-Agent': 'lager-cli'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status != 200:
                    invalid_packages.append(pkg)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                invalid_packages.append(pkg)
        except Exception:
            # Network error or timeout - skip validation for this package
            pass

    return invalid_packages

def _rebuild_python_container(gateway_ip):
    """Rebuild and restart the python container on the gateway"""
    click.secho('\nRebuilding python container...', fg='blue')

    try:
        click.secho('  Stopping existing containers...', fg='blue')
        subprocess.run(
            ['ssh', '-o', 'ProxyCommand=none', '-o', 'ControlMaster=no', f'lagerdata@{gateway_ip}', 'docker stop python controller 2>/dev/null || true && docker rm python controller 2>/dev/null || true'],
            capture_output=True,
            timeout=60
        )

        click.secho('  Rebuilding python container (no cache)...', fg='blue')
        click.secho('  This may take 3-5 minutes...', fg='yellow')
        # Build python container without cache to ensure user_requirements.txt changes are picked up
        subprocess.run(
            ['ssh', '-o', 'ProxyCommand=none', '-o', 'ControlMaster=no', f'lagerdata@{gateway_ip}', 'cd ~/gateway/python && docker build --no-cache -f docker/gatewaypy3.Dockerfile -t python .'],
            check=True,
            capture_output=False,
            timeout=600
        )

        click.secho('  Starting containers...', fg='blue')
        # Run the full start script - it will rebuild controller if needed and start both
        # Try both possible locations for start_all_containers.sh (sparse checkout structure)
        subprocess.run(
            ['ssh', '-o', 'ProxyCommand=none', '-o', 'ControlMaster=no', f'lagerdata@{gateway_ip}', 'cd ~/gateway && (./start_all_containers.sh 2>&1 || ./gateway/start_all_containers.sh 2>&1) | tail -20'],
            check=True,
            capture_output=False,
            timeout=300
        )
        click.secho('\n✓ Container rebuilt successfully!', fg='green')
        return True
    except subprocess.CalledProcessError as e:
        click.secho(f'\n✗ Failed to rebuild container', fg='red', err=True)
        return False
    except subprocess.TimeoutExpired:
        click.secho(f'\n✗ Container operation timed out', fg='red', err=True)
        return False

@click.group()
def pip():
    """Manage pip packages in the python container"""
    pass

@pip.command()
@click.pass_context
@click.option("--box", 'box', required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt and rebuild immediately')
@click.argument('packages', nargs=-1, required=True)
def install(ctx, box, dut, yes, packages):
    """Install packages permanently into the python container

    This command adds packages to the gateway's package list and rebuilds the container.
    Packages will persist across container restarts.

    Examples:
        lager pip install pandas
        lager pip install numpy==1.24.0
        lager pip install scipy matplotlib
    """
    # Get gateway IP
    gateway_ip = _get_gateway_ip(ctx, dut, box)

    # Read current requirements from gateway
    current_packages = _read_remote_requirements(gateway_ip)
    current_names = {_normalize_package_name(pkg) for pkg in current_packages}

    # Add new packages (avoid duplicates)
    new_packages = []
    for pkg in packages:
        pkg_name = _normalize_package_name(pkg)
        if pkg_name not in current_names:
            new_packages.append(pkg)
            current_packages.append(pkg)
            current_names.add(pkg_name)
            click.secho(f'Adding {pkg} to package list', fg='green')
        else:
            click.secho(f'Package {pkg} already in package list', fg='yellow')

    if not new_packages:
        click.secho('No new packages to install', fg='yellow')
        return

    # Validate packages exist on PyPI before modifying files
    click.secho('\nValidating packages on PyPI...', fg='blue')
    invalid_packages = _validate_packages(new_packages)

    if invalid_packages:
        click.secho('\n✗ Error: The following packages do not exist on PyPI:', fg='red', err=True)
        for pkg in invalid_packages:
            click.secho(f'  - {pkg}', fg='red', err=True)
        click.secho('\nNo changes were made. Please check package names and try again.', fg='yellow', err=True)
        sys.exit(1)

    click.secho('✓ All packages validated', fg='green')

    # Write updated requirements to gateway
    _write_remote_requirements(gateway_ip, current_packages)

    click.secho('\nPackages added successfully', fg='green')

    # Prompt user to rebuild container (skip prompt if --yes flag)
    if yes or click.confirm('\nRebuild and restart the python container now?', default=False):
        if _rebuild_python_container(gateway_ip):
            click.secho('Packages are now available.', fg='green')
        else:
            click.secho(f'To apply changes, run:', fg='yellow')
            click.secho(f'  lager pip apply --box {dut or box}', fg='yellow')
    else:
        click.secho('\nTo apply changes later, run:', fg='blue')
        click.secho(f'  lager pip apply --box {dut or box}', fg='blue')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def list(ctx, box, dut):
    """List user-installed packages

    Shows packages that have been installed via 'lager pip install'.
    These packages persist across container restarts.
    """
    # Get gateway IP
    gateway_ip = _get_gateway_ip(ctx, dut, box)

    # Read packages from gateway
    packages = _read_remote_requirements(gateway_ip)

    if not packages:
        click.secho('No user-installed packages found', fg='yellow')
        click.secho('\nTo install packages permanently:', fg='blue')
        click.secho('  lager pip install <package-name>', fg='blue')
        return

    click.secho('User-installed packages:', fg='green')
    for pkg in packages:
        click.echo(f'  {pkg}')

    click.secho(f'\nTotal: {len(packages)} package(s)', fg='blue')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt and rebuild immediately')
@click.argument('packages', nargs=-1, required=True)
def uninstall(ctx, box, dut, yes, packages):
    """Uninstall packages from the python container

    Removes packages that were installed via 'lager pip install'.
    Changes will take effect after container rebuild.

    Examples:
        lager pip uninstall pandas
        lager pip uninstall numpy scipy
    """
    # Get gateway IP
    gateway_ip = _get_gateway_ip(ctx, dut, box)

    # Read current requirements from gateway
    current_packages = _read_remote_requirements(gateway_ip)

    if not current_packages:
        click.secho('No user-installed packages found', fg='yellow')
        return

    # Normalize package names for removal
    packages_to_remove = {_normalize_package_name(pkg) for pkg in packages}

    # Filter out packages to remove
    removed = []
    remaining = []
    for pkg in current_packages:
        pkg_name = _normalize_package_name(pkg)
        if pkg_name in packages_to_remove:
            removed.append(pkg)
            click.secho(f'Removing {pkg} from package list', fg='green')
        else:
            remaining.append(pkg)

    if not removed:
        click.secho('No matching packages found in package list', fg='yellow')
        return

    # Write updated requirements to gateway
    _write_remote_requirements(gateway_ip, remaining)

    click.secho(f'\nRemoved {len(removed)} package(s) from package list', fg='green')

    # Prompt user to rebuild container (skip prompt if --yes flag)
    if yes or click.confirm('\nRebuild and restart the python container now?', default=False):
        if _rebuild_python_container(gateway_ip):
            click.secho('Packages have been removed.', fg='green')
        else:
            click.secho(f'To apply changes, run:', fg='yellow')
            click.secho(f'  lager pip apply --box {dut or box}', fg='yellow')
    else:
        click.secho('\nTo apply changes later, run:', fg='blue')
        click.secho(f'  lager pip apply --box {dut or box}', fg='blue')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
def apply(ctx, box, dut, yes):
    """Apply package changes by rebuilding the python container

    Use this command to rebuild the container after adding/removing packages
    with 'lager pip install' or 'lager pip uninstall' when you chose not to
    rebuild immediately.

    Examples:
        lager pip apply --box TEST-2
        lager pip apply --box TEST-2 --yes
    """
    # Get gateway IP
    gateway_ip = _get_gateway_ip(ctx, dut, box)

    # Read current packages to show what will be applied
    packages = _read_remote_requirements(gateway_ip)

    if packages:
        click.secho(f'Current package list ({len(packages)} package(s)):', fg='blue')
        for pkg in packages:
            click.echo(f'  {pkg}')
    else:
        click.secho('No packages in package list', fg='yellow')

    # Confirm rebuild unless --yes flag is used
    if not yes:
        if not click.confirm('\nRebuild and restart the python container now?', default=True):
            click.secho('Rebuild cancelled', fg='yellow')
            return

    # Rebuild container
    if _rebuild_python_container(gateway_ip):
        if packages:
            click.secho('Packages are now available.', fg='green')
        else:
            click.secho('Container rebuilt with no user packages.', fg='green')
    else:
        click.secho('Container rebuild failed', fg='red', err=True)
        sys.exit(1)


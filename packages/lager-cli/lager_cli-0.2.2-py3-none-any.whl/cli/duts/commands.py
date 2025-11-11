"""
    lager.duts.commands

    DUT commands for managing local configurations
"""
import click
import ipaddress
import json
from texttable import Texttable
from ..dut_storage import add_dut, delete_dut, delete_all_duts, list_duts, load_duts, save_duts, get_lager_file_path


@click.group(invoke_without_command=True)
@click.pass_context
def duts(ctx):
    """
        Manage DUT names and IP addresses
    """
    if ctx.invoked_subcommand is None:
        # Default behavior: list DUTs
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_dtype(['t', 't', 't'])
        table.set_cols_align(["l", "l", "l"])
        table.add_row(['name', 'ip', 'user'])

        # Show only saved local DUTs
        saved_duts = list_duts()
        for name, dut_info in sorted(saved_duts.items()):
            if isinstance(dut_info, dict):
                ip = dut_info.get('ip', 'unknown')
                user = dut_info.get('user', '-')
                table.add_row([name, ip, user])
            else:
                # Handle simple string format (IP only)
                table.add_row([name, dut_info, '-'])

        if not saved_duts:
            click.echo("No local DUTs found. Add one with: lager duts add --name <NAME> --ip <IP>")
        else:
            click.echo(table.draw())


@duts.command()
@click.option('--name', required=True, help='Name to assign to the DUT')
@click.option('--ip', required=True, help='IP address of the DUT')
@click.option('--user', required=False, help='Username for SSH connection (defaults to lagerdata)')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def add(name, ip, user, yes):
    """
        Add a DUT configuration
    """
    # Validate DUT name
    if not name or name.strip() == "":
        click.echo(click.style("Error: DUT name cannot be empty", fg='red'), err=True)
        raise click.Abort()

    # Validate IP address format
    if not ip or ip.strip() == "":
        click.echo(click.style("Error: IP address cannot be empty", fg='red'), err=True)
        raise click.Abort()

    try:
        # Try to parse as IPv4 or IPv6 address
        ipaddress.ip_address(ip)
    except ValueError:
        click.echo(click.style(f"Error: '{ip}' is not a valid IP address", fg='red'), err=True)
        click.echo(click.style("Please provide a valid IPv4 address (e.g., 192.168.1.100) or IPv6 address", fg='red'), err=True)
        raise click.Abort()

    # Check if DUT with same name or IP already exists
    existing_duts = list_duts()
    existing_name = None
    existing_ip = None

    # Check for duplicate name
    if name in existing_duts:
        existing_dut = existing_duts[name]
        if isinstance(existing_dut, dict):
            existing_name = (name, existing_dut.get('ip', 'unknown'))
        else:
            existing_name = (name, existing_dut)

    # Check for duplicate IP
    for dut_name, dut_info in existing_duts.items():
        dut_ip = dut_info.get('ip') if isinstance(dut_info, dict) else dut_info
        if dut_ip == ip and dut_name != name:
            existing_ip = (dut_name, dut_ip)
            break

    # Display warning if duplicates found
    if existing_name or existing_ip:
        click.echo(click.style(f"\n⚠ WARNING: Duplicate DUT detected!", fg='yellow', bold=True))
        click.echo()

        # Determine the specific conflict and appropriate prompt
        if existing_name and existing_ip:
            # Both name and IP are duplicates (unusual edge case)
            click.echo(f"  A DUT with the name '{existing_name[0]}' already exists:")
            click.echo(f"    Current: {existing_name[0]} → {existing_name[1]}")
            click.echo(f"    New:     {name} → {ip}")
            click.echo()
            if existing_ip[0] != name:
                click.echo(f"  A DUT with the IP '{existing_ip[1]}' also already exists:")
                click.echo(f"    Current: {existing_ip[0]} → {existing_ip[1]}")
                click.echo()
            confirm_prompt = "Add this DUT anyway?"
        elif existing_name:
            # Same name, check if IP is also the same
            if existing_name[1] == ip:
                click.echo(f"  A DUT with the name '{existing_name[0]}' and IP '{ip}' already exists.")
                click.echo()
                confirm_prompt = "Update existing DUT?"
            else:
                click.echo(f"  A DUT with the name '{existing_name[0]}' already exists:")
                click.echo(f"    Current: {existing_name[0]} → {existing_name[1]}")
                click.echo(f"    New:     {name} → {ip}")
                click.echo()
                confirm_prompt = "Overwrite DUT with new IP?"
        else:
            # Only IP is duplicate (different name)
            click.echo(f"  A DUT with the IP '{existing_ip[1]}' already exists:")
            click.echo(f"    Current: {existing_ip[0]} → {existing_ip[1]}")
            click.echo(f"    New:     {name} → {ip}")
            click.echo()
            click.echo(f"  Adding '{name}' will overwrite '{existing_ip[0]}' (duplicate IP not allowed).")
            click.echo()
            confirm_prompt = "Overwrite existing DUT?"

        # Ask for appropriate confirmation unless --yes flag is provided
        if not yes and not click.confirm(confirm_prompt, default=False):
            click.echo("Cancelled. DUT not added.")
            return

        # If confirmed (or --yes flag used) and there's a duplicate IP with a different name,
        # delete the old DUT to prevent having two DUTs with the same IP
        if existing_ip and existing_ip[0] != name:
            delete_dut(existing_ip[0])
    else:
        # No duplicates, ask for confirmation unless --yes flag is provided
        if not yes:
            click.echo(f"\nYou are about to add the following DUT:")
            click.echo(f"  Name: {name}")
            click.echo(f"  IP:   {ip}")
            if user:
                click.echo(f"  User: {user}")
            click.echo()

            if not click.confirm("Add this DUT?", default=False):
                click.echo("Cancelled. DUT not added.")
                return

    add_dut(name, ip, user)
    success_msg = f"Added DUT '{name}' with IP '{ip}'"
    if user:
        success_msg += f" (user: {user})"
    click.echo(click.style(success_msg, fg='green'))


@duts.command('delete')
@click.option('--name', required=True, help='Name of the DUT to delete')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def delete(name, yes):
    """
        Delete a DUT configuration
    """
    # Check if DUT exists first
    existing_duts = list_duts()
    if name not in existing_duts:
        click.echo(click.style(f"DUT '{name}' not found in .lager file", fg='red'), err=True)
        return

    # Get DUT info for display
    dut_info = existing_duts[name]
    if isinstance(dut_info, dict):
        ip = dut_info.get('ip', 'unknown')
    else:
        ip = dut_info

    # Display what will be deleted and ask for confirmation unless --yes flag is provided
    if not yes:
        click.echo(f"\nYou are about to delete the following DUT:")
        click.echo(f"  Name: {name}")
        click.echo(f"  IP:   {ip}")
        click.echo()

        if not click.confirm("Delete this DUT?", default=False):
            click.echo("Cancelled. DUT not deleted.")
            return

    if delete_dut(name):
        click.echo(click.style(f"Deleted DUT '{name}' from .lager file", fg='green'))
    else:
        click.echo(click.style(f"DUT '{name}' not found in .lager file", fg='red'), err=True)


@duts.command('edit')
@click.option('--name', required=True, help='Name of the DUT to edit')
@click.option('--ip', required=False, help='New IP address for the DUT')
@click.option('--user', required=False, help='New username for SSH connection')
@click.option('--new-name', required=False, help='New name for the DUT')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def edit(name, ip, user, new_name, yes):
    """
        Edit a DUT configuration
    """
    # Check if at least one change is specified
    if ip is None and new_name is None and user is None:
        click.echo(click.style("Error: You must specify at least one change (--ip, --user, or --new-name)", fg='red'), err=True)
        raise click.Abort()

    # Check if DUT exists
    existing_duts = list_duts()
    if name not in existing_duts:
        click.echo(click.style(f"DUT '{name}' not found in .lager file", fg='red'), err=True)
        return

    # Get current DUT info
    dut_info = existing_duts[name]
    if isinstance(dut_info, dict):
        current_ip = dut_info.get('ip')
        current_user = dut_info.get('user')
    else:
        current_ip = dut_info
        current_user = None

    # Determine new values (keep old if not specified)
    updated_ip = ip if ip else current_ip
    updated_user = user if user is not None else current_user
    updated_name = new_name if new_name else name

    # Validate new IP if specified
    if ip is not None:
        if not ip or ip.strip() == "":
            click.echo(click.style("Error: IP address cannot be empty", fg='red'), err=True)
            raise click.Abort()

        try:
            ipaddress.ip_address(ip)
        except ValueError:
            click.echo(click.style(f"Error: '{ip}' is not a valid IP address", fg='red'), err=True)
            click.echo(click.style("Please provide a valid IPv4 address (e.g., 192.168.1.100) or IPv6 address", fg='red'), err=True)
            raise click.Abort()

    # Validate new name if specified
    if new_name is not None:
        if not new_name or new_name.strip() == "":
            click.echo(click.style("Error: DUT name cannot be empty", fg='red'), err=True)
            raise click.Abort()

        # Check if new name conflicts with existing DUT (unless it's the same DUT)
        if new_name != name and new_name in existing_duts:
            existing_new_dut = existing_duts[new_name]
            existing_new_ip = existing_new_dut.get('ip') if isinstance(existing_new_dut, dict) else existing_new_dut
            click.echo(click.style(f"\n⚠ WARNING: A DUT with the name '{new_name}' already exists!", fg='yellow', bold=True))
            click.echo(f"  Existing: {new_name} → {existing_new_ip}")
            click.echo(f"  This operation will overwrite it.")
            click.echo()

    # Display what will change and ask for confirmation unless --yes flag is provided
    if not yes:
        click.echo(f"\nYou are about to edit the following DUT:")
        current_display = f"  Current: {name} → {current_ip}"
        if current_user:
            current_display += f" (user: {current_user})"
        click.echo(current_display)

        changes = []
        if new_name:
            changes.append(f"name: {name} → {updated_name}")
        if ip:
            changes.append(f"IP: {current_ip} → {updated_ip}")
        if user is not None:
            if current_user:
                changes.append(f"user: {current_user} → {updated_user}")
            else:
                changes.append(f"user: (none) → {updated_user}")

        for change in changes:
            click.echo(f"  Change:  {change}")
        click.echo()

        if not click.confirm("Apply these changes?", default=False):
            click.echo("Cancelled. DUT not modified.")
            return

    # Apply changes
    # If renaming, delete old entry
    if new_name and new_name != name:
        delete_dut(name)

    # Add/update with new values
    add_dut(updated_name, updated_ip, updated_user)

    # Build success message
    changes_made = []
    if new_name and new_name != name:
        changes_made.append(f"renamed '{name}' to '{updated_name}'")
    if ip:
        changes_made.append(f"changed IP to '{updated_ip}'")
    if user is not None:
        changes_made.append(f"changed user to '{updated_user}'")

    success_msg = f"Updated DUT"
    if changes_made:
        success_msg += ": " + ", ".join(changes_made)
    click.echo(click.style(success_msg, fg='green'))


@duts.command('delete-all')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def delete_all(yes):
    """
        Delete all DUT configurations
    """
    # Get current DUTs to display count
    saved_duts = list_duts()
    dut_count = len(saved_duts)

    if dut_count == 0:
        click.echo("No DUTs found in .lager file. Nothing to delete.")
        return

    # Display warning and DUT list
    click.echo(click.style(f"\n⚠ WARNING: You are about to delete ALL {dut_count} DUT(s) from .lager file:", fg='yellow', bold=True))
    click.echo()
    for name, dut_info in sorted(saved_duts.items()):
        if isinstance(dut_info, dict):
            ip = dut_info.get('ip', 'unknown')
        else:
            ip = dut_info
        click.echo(f"  - {name} ({ip})")
    click.echo()

    # Ask for confirmation unless --yes flag is provided (default is No)
    if not yes and not click.confirm("Are you sure you want to delete ALL DUTs?", default=False):
        click.echo("Cancelled. No DUTs were deleted.")
        return

    # Delete all DUTs
    count = delete_all_duts()
    click.echo(click.style(f"✓ Deleted all {count} DUT(s) from .lager file", fg='green'))


@duts.command('list')
@click.pass_context
def list_duts_cmd(ctx):
    """
        List DUTs
    """
    # Reuse the default behavior
    ctx.invoke(duts)


@duts.command('export')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def export(output):
    """
        Export DUT configuration
    """
    # Load the entire .lager file to preserve all data
    lager_file = get_lager_file_path()

    if not lager_file.exists():
        click.echo(click.style("No .lager file found. Nothing to export.", fg='yellow'))
        return

    try:
        with open(lager_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        click.echo(click.style("Error: .lager file is not valid JSON", fg='red'), err=True)
        raise click.Abort()

    # Format JSON with indentation
    json_output = json.dumps(data, indent=2)

    if output:
        # Write to file
        try:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            click.echo(click.style(f"Exported configuration to {output}", fg='green'))
        except IOError as e:
            click.echo(click.style(f"Error writing to file: {e}", fg='red'), err=True)
            raise click.Abort()
    else:
        # Print to stdout
        click.echo(json_output)


@duts.command('import')
@click.argument('file', type=click.Path(exists=True))
@click.option('--merge', is_flag=True, help='Merge with existing DUTs instead of replacing')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def import_duts(file, merge, yes):
    """
        Import DUT configuration
    """
    # Read the import file
    try:
        with open(file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
    except json.JSONDecodeError:
        click.echo(click.style(f"Error: '{file}' is not valid JSON", fg='red'), err=True)
        raise click.Abort()
    except IOError as e:
        click.echo(click.style(f"Error reading file: {e}", fg='red'), err=True)
        raise click.Abort()

    # Validate that the import data has DUTs
    import_duts = import_data.get('DUTS') or import_data.get('duts', {})
    if not import_duts:
        click.echo(click.style("Error: Import file does not contain any DUTs", fg='red'), err=True)
        raise click.Abort()

    # Get current DUTs for comparison
    current_duts = load_duts()

    # Show what will happen
    if merge:
        # Merge mode: show what will be added/updated
        new_duts = set(import_duts.keys()) - set(current_duts.keys())
        updated_duts = set(import_duts.keys()) & set(current_duts.keys())

        click.echo(click.style(f"\n{'Merge' if merge else 'Import'} Configuration", fg='cyan', bold=True))
        click.echo(f"Source: {file}")
        click.echo()

        if new_duts:
            click.echo(click.style(f"Will add {len(new_duts)} new DUT(s):", fg='green'))
            for name in sorted(new_duts):
                ip = import_duts[name].get('ip') if isinstance(import_duts[name], dict) else import_duts[name]
                click.echo(f"  + {name} → {ip}")
            click.echo()

        if updated_duts:
            click.echo(click.style(f"Will update {len(updated_duts)} existing DUT(s):", fg='yellow'))
            for name in sorted(updated_duts):
                current_ip = current_duts[name].get('ip') if isinstance(current_duts[name], dict) else current_duts[name]
                new_ip = import_duts[name].get('ip') if isinstance(import_duts[name], dict) else import_duts[name]
                if current_ip != new_ip:
                    click.echo(f"  ~ {name}: {current_ip} → {new_ip}")
                else:
                    click.echo(f"  = {name} → {new_ip} (no change)")
            click.echo()

        if current_duts and not new_duts and not updated_duts:
            click.echo(click.style("No changes (all DUTs already exist with same values)", fg='green'))
            click.echo()

        if current_duts:
            kept_duts = set(current_duts.keys()) - set(import_duts.keys())
            if kept_duts:
                click.echo(f"Will keep {len(kept_duts)} existing DUT(s) not in import file")
    else:
        # Replace mode: show before and after
        click.echo(click.style("\n⚠ WARNING: REPLACE MODE", fg='yellow', bold=True))
        click.echo(f"Source: {file}")
        click.echo()
        click.echo(click.style("This will COMPLETELY REPLACE your current DUT configuration!", fg='yellow'))
        click.echo()

        if current_duts:
            click.echo(click.style(f"Current DUTs ({len(current_duts)}) will be DELETED:", fg='red'))
            for name, dut_info in sorted(current_duts.items()):
                ip = dut_info.get('ip') if isinstance(dut_info, dict) else dut_info
                click.echo(f"  - {name} → {ip}")
            click.echo()

        click.echo(click.style(f"New DUTs ({len(import_duts)}) will be ADDED:", fg='green'))
        for name, dut_info in sorted(import_duts.items()):
            ip = dut_info.get('ip') if isinstance(dut_info, dict) else dut_info
            click.echo(f"  + {name} → {ip}")
        click.echo()

    # Confirmation prompt
    if not yes:
        action = "merge these DUTs" if merge else "replace your DUT configuration"
        if not click.confirm(f"Do you want to {action}?", default=False):
            click.echo("Cancelled. No changes made.")
            return

    # Perform the import
    if merge:
        # Merge: combine current and import DUTs
        merged_duts = current_duts.copy()
        merged_duts.update(import_duts)
        save_duts(merged_duts)
        click.echo(click.style(f"✓ Successfully merged {len(import_duts)} DUT(s) from {file}", fg='green'))
    else:
        # Replace: use only import DUTs
        save_duts(import_duts)
        click.echo(click.style(f"✓ Successfully imported {len(import_duts)} DUT(s) from {file}", fg='green'))
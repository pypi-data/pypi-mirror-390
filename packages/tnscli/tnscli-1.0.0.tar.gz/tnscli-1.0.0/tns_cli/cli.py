#!/usr/bin/env python3
"""
TNS CLI - Command-line interface for TAO Name Service

Usage:
    tns check <domain>          Check if a domain is available
    tns resolve <domain>        Resolve domain to addresses
    tns search <query>          Search for domains
    tns lookup <address>        Lookup domains by address
    tns stats                   Show platform statistics
    tns register <domain>       Register a new domain (requires wallet)
    tns link <domain> <hotkey>  Link a hotkey to your domain
    tns transfer <domain> <to>  Transfer domain ownership
    tns renew <domain>          Renew domain registration
"""

import click
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from .client import TNSClient
from substrateinterface import SubstrateInterface, Keypair
from dotenv import load_dotenv

load_dotenv()

console = Console()

# Configuration
API_URL = os.getenv("TNS_API_URL", "http://13.60.59.30:8000")
WS_URL = os.getenv("TNS_WS_URL", "ws://13.60.59.30:9944")

client = TNSClient(API_URL)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """TNS - TAO Name Service CLI"""
    pass


@cli.command()
@click.argument('domain')
def check(domain):
    """Check if a domain is available"""
    try:
        # Remove .tao suffix if present
        domain = domain.replace('.tao', '')

        result = client.check_availability(domain)

        if result['available']:
            console.print(f"[green]✓[/green] {result['name']} is [bold green]AVAILABLE[/bold green]")
            if result.get('price'):
                console.print(f"Registration fee: [yellow]{result['price']}[/yellow]")
        else:
            console.print(f"[red]✗[/red] {result['name']} is [bold red]NOT AVAILABLE[/bold red]")
            if result.get('reason'):
                console.print(f"Reason: {result['reason']}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument('domain')
def resolve(domain):
    """Resolve a domain to addresses"""
    try:
        domain = domain.replace('.tao', '')
        result = client.resolve(domain)

        table = Table(title=f"Domain: {result['name']}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Owner", result['owner'])
        table.add_row("Coldkey", result['coldkey'])
        table.add_row("Hotkey", result.get('hotkey') or '[dim]Not linked[/dim]')
        table.add_row("Expires at block", str(result['expiry']))
        table.add_row("Registered at block", str(result['registered_at']))
        table.add_row("Status", "[red]Expired[/red]" if result['is_expired'] else "[green]Active[/green]")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument('query')
@click.option('--limit', default=20, help='Maximum number of results')
def search(query, limit):
    """Search for domains"""
    try:
        result = client.search(query, limit=limit)

        if not result.get('domains'):
            console.print(f"[yellow]No domains found matching '{query}'[/yellow]")
            return

        table = Table(title=f"Search Results for '{query}' ({result['total']} total)")
        table.add_column("#", style="dim")
        table.add_column("Domain", style="cyan")
        table.add_column("Status", style="magenta")

        for idx, domain in enumerate(result['domains'], 1):
            status = "[red]Expired[/red]" if domain.get('is_expired') else "[green]Active[/green]"
            table.add_row(str(idx), domain['name'], status)

        console.print(table)

        if result['total'] > len(result['domains']):
            console.print(f"\n[dim]Showing {len(result['domains'])} of {result['total']} results[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument('address')
@click.option('--type', 'lookup_type', type=click.Choice(['owner', 'coldkey', 'hotkey']), default='owner',
              help='Type of address lookup')
def lookup(address, lookup_type):
    """Lookup domains by address"""
    try:
        if lookup_type == 'owner':
            result = client.lookup_by_owner(address)
        elif lookup_type == 'coldkey':
            result = client.lookup_by_coldkey(address)
        else:
            result = client.lookup_by_hotkey(address)

        domains = result.get('domains', []) if isinstance(result, dict) else result

        if not domains:
            console.print(f"[yellow]No domains found for {lookup_type} address {address}[/yellow]")
            return

        table = Table(title=f"Domains for {lookup_type}: {address[:12]}...{address[-12:]}")
        table.add_column("Domain", style="cyan")
        table.add_column("Owner", style="green")
        table.add_column("Status", style="magenta")

        for domain in domains:
            status = "[red]Expired[/red]" if domain.get('is_expired') else "[green]Active[/green]"
            owner_short = f"{domain['owner'][:8]}...{domain['owner'][-8:]}"
            table.add_row(domain['name'], owner_short, status)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@cli.command()
def stats():
    """Show platform statistics"""
    try:
        result = client.get_stats()

        stats_panel = Panel.fit(
            f"""[cyan]Total Domains:[/cyan] [bold]{result['total_domains']}[/bold]
[green]Active Domains:[/green] [bold]{result['active_domains']}[/bold]
[red]Expired Domains:[/red] [bold]{result['expired_domains']}[/bold]
[yellow]Total Events:[/yellow] [bold]{result['total_events']}[/bold]
[magenta]Recent Registrations (24h):[/magenta] [bold]{result['recent_registrations']}[/bold]""",
            title="[bold]TNS Platform Statistics[/bold]",
            border_style="blue"
        )

        console.print(stats_panel)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument('domain')
@click.argument('coldkey')
@click.option('--mnemonic', prompt=True, hide_input=True, help='Wallet mnemonic phrase')
def register(domain, coldkey, mnemonic):
    """Register a new domain (requires wallet)"""
    try:
        domain = domain.replace('.tao', '')

        # Check availability first
        avail = client.check_availability(domain)
        if not avail['available']:
            console.print(f"[red]✗[/red] Domain {domain}.tao is not available: {avail.get('reason')}")
            raise click.Abort()

        console.print(f"[green]✓[/green] Domain {domain}.tao is available")
        console.print(f"Registration fee: [yellow]{avail.get('price')}[/yellow]")

        if not click.confirm('Proceed with registration?'):
            console.print("[yellow]Registration cancelled[/yellow]")
            return

        # Connect to blockchain
        console.print("[dim]Connecting to blockchain...[/dim]")
        substrate = SubstrateInterface(url=WS_URL)

        # Create keypair from mnemonic
        keypair = Keypair.create_from_mnemonic(mnemonic)
        console.print(f"[dim]Using account: {keypair.ss58_address}[/dim]")

        # Create transaction
        call = substrate.compose_call(
            call_module='TNS',
            call_function='register',
            call_params={
                'name': domain.encode(),
                'coldkey': coldkey
            }
        )

        # Sign and submit
        console.print("[dim]Submitting transaction...[/dim]")
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
        receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)

        if receipt.is_success:
            console.print(f"[green]✓[/green] Domain {domain}.tao registered successfully!")
            console.print(f"[dim]Block hash: {receipt.block_hash}[/dim]")
        else:
            console.print(f"[red]✗[/red] Registration failed: {receipt.error_message}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument('domain')
@click.argument('hotkey')
@click.option('--mnemonic', prompt=True, hide_input=True, help='Wallet mnemonic phrase')
def link(domain, hotkey, mnemonic):
    """Link a hotkey to your domain"""
    try:
        domain = domain.replace('.tao', '')

        substrate = SubstrateInterface(url=WS_URL)
        keypair = Keypair.create_from_mnemonic(mnemonic)

        console.print(f"[dim]Linking {hotkey} to {domain}.tao...[/dim]")

        call = substrate.compose_call(
            call_module='TNS',
            call_function='link_hotkey',
            call_params={
                'name': domain.encode(),
                'hotkey': hotkey
            }
        )

        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
        receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)

        if receipt.is_success:
            console.print(f"[green]✓[/green] Hotkey linked successfully!")
        else:
            console.print(f"[red]✗[/red] Failed: {receipt.error_message}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument('domain')
@click.argument('new_owner')
@click.option('--mnemonic', prompt=True, hide_input=True, help='Wallet mnemonic phrase')
def transfer(domain, new_owner, mnemonic):
    """Transfer domain ownership"""
    try:
        domain = domain.replace('.tao', '')

        if not click.confirm(f'Transfer {domain}.tao to {new_owner}? This action is irreversible.'):
            console.print("[yellow]Transfer cancelled[/yellow]")
            return

        substrate = SubstrateInterface(url=WS_URL)
        keypair = Keypair.create_from_mnemonic(mnemonic)

        console.print(f"[dim]Transferring {domain}.tao...[/dim]")

        call = substrate.compose_call(
            call_module='TNS',
            call_function='transfer',
            call_params={
                'name': domain.encode(),
                'new_owner': new_owner
            }
        )

        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
        receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)

        if receipt.is_success:
            console.print(f"[green]✓[/green] Domain transferred successfully!")
        else:
            console.print(f"[red]✗[/red] Transfer failed: {receipt.error_message}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument('domain')
@click.option('--mnemonic', prompt=True, hide_input=True, help='Wallet mnemonic phrase')
def renew(domain, mnemonic):
    """Renew domain registration"""
    try:
        domain = domain.replace('.tao', '')

        substrate = SubstrateInterface(url=WS_URL)
        keypair = Keypair.create_from_mnemonic(mnemonic)

        console.print(f"[dim]Renewing {domain}.tao...[/dim]")

        call = substrate.compose_call(
            call_module='TNS',
            call_function='renew',
            call_params={
                'name': domain.encode()
            }
        )

        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
        receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)

        if receipt.is_success:
            console.print(f"[green]✓[/green] Domain renewed successfully!")
        else:
            console.print(f"[red]✗[/red] Renewal failed: {receipt.error_message}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise click.Abort()


if __name__ == '__main__':
    cli()

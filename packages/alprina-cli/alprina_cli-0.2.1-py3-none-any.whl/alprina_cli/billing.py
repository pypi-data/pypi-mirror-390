"""
Billing integration module for Alprina CLI.
Handles Stripe integration and usage metering.
"""

import os
from typing import Optional
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .auth import is_authenticated, get_auth_headers, load_token

console = Console()


def get_backend_url() -> str:
    """Get backend URL from environment or use default."""
    return os.getenv("ALPRINA_BACKEND", "https://api.alprina.ai")


def billing_status_command():
    """Display billing status and usage information."""
    if not is_authenticated():
        console.print("[red]Please login first: alprina auth login[/red]")
        return

    console.print(Panel("💳 Fetching billing information...", title="Billing Status"))

    try:
        backend_url = get_backend_url()
        headers = get_auth_headers()

        response = httpx.get(
            f"{backend_url}/billing/usage",
            headers=headers,
            timeout=10.0
        )

        if response.status_code == 200:
            data = response.json()
            _display_billing_info(data)
        else:
            console.print(f"[red]Failed to fetch billing info: {response.text}[/red]")

    except httpx.ConnectError:
        console.print("[yellow]Could not connect to backend. Displaying local info.[/yellow]")
        _display_local_billing_info()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def _display_billing_info(data: dict):
    """Display billing information from API response."""
    user = data.get("user", {})
    usage = data.get("usage", {})
    plan = data.get("plan", {})

    # Create info panel
    info = f"""[bold]Plan:[/bold] {plan.get('name', 'Free')}
[bold]Status:[/bold] {plan.get('status', 'Active')}
"""

    if plan.get('billing_cycle'):
        info += f"[bold]Billing Cycle:[/bold] {plan['billing_cycle']}\n"

    console.print(Panel(info, title="Subscription Info"))

    # Create usage table
    table = Table(title="Usage Statistics", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Used", justify="right")
    table.add_column("Limit", justify="right")
    table.add_column("Status", justify="center")

    scans_used = usage.get("scans_used", 0)
    scans_limit = plan.get("scans_limit", 10)
    scans_pct = (scans_used / scans_limit * 100) if scans_limit > 0 else 0

    status_color = "green" if scans_pct < 80 else "yellow" if scans_pct < 100 else "red"

    table.add_row(
        "Scans (today)",
        str(scans_used),
        str(scans_limit),
        f"[{status_color}]{scans_pct:.0f}%[/{status_color}]"
    )

    console.print(table)

    # Show upgrade message if on free plan
    if plan.get('name') == 'Free':
        console.print("\n[cyan]💡 Upgrade to Pro for unlimited scans and advanced features![/cyan]")
        console.print("[dim]Visit https://alprina.ai/pricing[/dim]")


def _display_local_billing_info():
    """Display billing info from local token when offline."""
    auth_data = load_token()

    if not auth_data:
        console.print("[red]Not authenticated[/red]")
        return

    user = auth_data.get("user", {})
    plan = user.get("plan", "free")

    console.print(Panel(
        f"[bold]Plan:[/bold] {plan.title()}\n"
        f"[yellow]Offline mode - showing cached information[/yellow]",
        title="Billing Status"
    ))


def check_scan_quota() -> bool:
    """
    Check if user has remaining scan quota.

    Returns:
        True if user can run a scan, False otherwise
    """
    if not is_authenticated():
        return False

    try:
        backend_url = get_backend_url()
        headers = get_auth_headers()

        response = httpx.get(
            f"{backend_url}/billing/usage",
            headers=headers,
            timeout=5.0
        )

        if response.status_code == 200:
            data = response.json()
            usage = data.get("usage", {})
            plan = data.get("plan", {})

            scans_used = usage.get("scans_used", 0)
            scans_limit = plan.get("scans_limit", 10)

            if scans_used >= scans_limit:
                console.print(f"[red]Scan quota exceeded ({scans_used}/{scans_limit})[/red]")
                console.print("[yellow]Upgrade your plan to continue scanning[/yellow]")
                return False

            return True

    except Exception:
        # Allow scans if backend is unreachable
        return True

    return True


def increment_usage(scan_type: str = "scan"):
    """
    Increment usage counter after a successful scan.

    Args:
        scan_type: Type of scan performed
    """
    try:
        backend_url = get_backend_url()
        headers = get_auth_headers()

        httpx.post(
            f"{backend_url}/billing/usage/increment",
            headers=headers,
            json={"type": scan_type},
            timeout=5.0
        )

    except Exception:
        # Silently fail if backend is unreachable
        pass

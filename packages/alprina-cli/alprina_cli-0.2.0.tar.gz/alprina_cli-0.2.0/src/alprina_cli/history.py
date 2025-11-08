"""
History module for Alprina CLI.
Displays scan history and detailed scan results.
"""

import httpx
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import json
from datetime import datetime

from .auth import is_authenticated, get_auth_headers, get_backend_url

console = Console()


def history_command(
    scan_id: Optional[str] = None,
    limit: int = 20,
    severity: Optional[str] = None,
    page: int = 1
):
    """
    Display scan history or specific scan details.

    Args:
        scan_id: Specific scan ID to view details
        limit: Number of scans to display per page
        severity: Filter by severity (critical, high, medium, low, info)
        page: Page number for pagination
    """
    if not is_authenticated():
        console.print("[red]✗ Please login first: alprina auth login[/red]")
        return

    try:
        if scan_id:
            _display_scan_details(scan_id)
        else:
            _display_scan_list(page=page, limit=limit, severity=severity)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


def _display_scan_list(page: int = 1, limit: int = 20, severity: Optional[str] = None):
    """Display list of scans in a table."""
    try:
        headers = get_auth_headers()
        backend_url = get_backend_url()

        # Build query params
        params = {
            "page": page,
            "limit": limit
        }
        if severity:
            params["severity"] = severity.upper()

        response = httpx.get(
            f"{backend_url}/scans",
            headers=headers,
            params=params,
            timeout=10.0
        )

        if response.status_code != 200:
            console.print(f"[red]✗ Failed to fetch scans: {response.status_code}[/red]")
            return

        data = response.json()
        scans = data.get("scans", [])
        total = data.get("total", 0)
        pages = data.get("pages", 0)

        if not scans:
            console.print("[yellow]No scans found[/yellow]")
            console.print("Run [bold]alprina scan <target>[/bold] to create your first scan")
            return

        # Create table
        table = Table(title=f"Scan History (Page {page}/{pages}, Total: {total})")

        table.add_column("ID", style="cyan", no_wrap=True, width=12)
        table.add_column("Date", style="dim", width=19)
        table.add_column("Target", style="bold")
        table.add_column("Type", justify="center", width=8)
        table.add_column("Findings", justify="right", width=10)
        table.add_column("Critical", justify="center", style="red", width=8)
        table.add_column("High", justify="center", style="yellow", width=8)
        table.add_column("Status", justify="center", width=10)

        for scan in scans:
            # Format ID (first 8 chars)
            scan_id = scan.get("id", "")[:8]

            # Format date
            created_at = scan.get("created_at", "")
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = created_at[:16]

            # Get data
            target = scan.get("target", "")
            scan_type = scan.get("scan_type", "")
            findings = scan.get("findings_count", 0)
            critical = scan.get("critical_count", 0)
            high = scan.get("high_count", 0)
            status = scan.get("status", "unknown")

            # Color code status
            status_style = {
                "completed": "[green]completed[/green]",
                "running": "[yellow]running[/yellow]",
                "failed": "[red]failed[/red]"
            }.get(status, status)

            # Color code critical/high counts
            critical_str = f"[red]{critical}[/red]" if critical > 0 else str(critical)
            high_str = f"[yellow]{high}[/yellow]" if high > 0 else str(high)

            table.add_row(
                scan_id,
                date_str,
                target,
                scan_type,
                str(findings),
                critical_str,
                high_str,
                status_style
            )

        console.print()
        console.print(table)
        console.print()

        # Show pagination info
        if pages > 1:
            console.print(f"[dim]Showing page {page} of {pages}[/dim]")
            if page < pages:
                console.print(f"[dim]Next page: alprina history --page {page + 1}[/dim]")

        console.print()
        console.print("[dim]View details: alprina history --scan-id <ID>[/dim]")
        if severity:
            console.print(f"[dim]Filtered by: {severity.upper()} severity[/dim]")

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to backend[/red]")
        console.print("[yellow]Make sure the API server is running[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


def _display_scan_details(scan_id: str):
    """Display detailed scan results."""
    try:
        headers = get_auth_headers()
        backend_url = get_backend_url()

        response = httpx.get(
            f"{backend_url}/scans/{scan_id}",
            headers=headers,
            timeout=10.0
        )

        if response.status_code == 404:
            console.print(f"[red]✗ Scan not found: {scan_id}[/red]")
            console.print("[yellow]Tip: Use 'alprina history' to see available scans[/yellow]")
            return
        elif response.status_code != 200:
            console.print(f"[red]✗ Failed to fetch scan: {response.status_code}[/red]")
            return

        scan = response.json()

        # Display scan overview
        console.print()
        console.print(Panel(
            f"[bold]Scan Details[/bold]\n\n"
            f"ID: [cyan]{scan.get('id')}[/cyan]\n"
            f"Target: [bold]{scan.get('target')}[/bold]\n"
            f"Type: {scan.get('scan_type')}\n"
            f"Profile: {scan.get('profile')}\n"
            f"Status: {scan.get('status')}\n"
            f"Started: {scan.get('started_at', 'N/A')}\n"
            f"Completed: {scan.get('completed_at', 'N/A')}",
            title="📊 Scan Overview"
        ))

        # Display findings summary
        findings_count = scan.get('findings_count', 0)
        critical = scan.get('critical_count', 0)
        high = scan.get('high_count', 0)
        medium = scan.get('medium_count', 0)
        low = scan.get('low_count', 0)
        info = scan.get('info_count', 0)

        summary_table = Table(title="Findings Summary")
        summary_table.add_column("Severity", style="bold")
        summary_table.add_column("Count", justify="right")

        summary_table.add_row("[red]CRITICAL[/red]", f"[red]{critical}[/red]" if critical > 0 else "0")
        summary_table.add_row("[yellow]HIGH[/yellow]", f"[yellow]{high}[/yellow]" if high > 0 else "0")
        summary_table.add_row("[blue]MEDIUM[/blue]", f"[blue]{medium}[/blue]" if medium > 0 else "0")
        summary_table.add_row("[green]LOW[/green]", str(low))
        summary_table.add_row("[dim]INFO[/dim]", str(info))
        summary_table.add_row("[bold]TOTAL[/bold]", f"[bold]{findings_count}[/bold]")

        console.print()
        console.print(summary_table)

        # Display detailed findings if available
        results = scan.get('results', {})
        findings = results.get('findings', [])

        if findings:
            console.print()
            console.print(Panel("[bold]Detailed Findings[/bold]", style="cyan"))

            for i, finding in enumerate(findings[:10], 1):  # Show first 10
                severity = finding.get('severity', 'UNKNOWN')
                title = finding.get('title', 'No title')
                description = finding.get('description', 'No description')

                severity_color = {
                    'CRITICAL': 'red',
                    'HIGH': 'yellow',
                    'MEDIUM': 'blue',
                    'LOW': 'green',
                    'INFO': 'dim'
                }.get(severity, 'white')

                console.print(f"\n[{severity_color}]━[/] [bold]{i}. [{severity_color}]{severity}[/{severity_color}] - {title}[/bold]")
                console.print(f"   {description}")

            if len(findings) > 10:
                console.print(f"\n[dim]... and {len(findings) - 10} more findings[/dim]")

        console.print()
        console.print("[dim]Tip: Export full report with 'alprina report --scan-id " + scan_id + "'[/dim]")

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to backend[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

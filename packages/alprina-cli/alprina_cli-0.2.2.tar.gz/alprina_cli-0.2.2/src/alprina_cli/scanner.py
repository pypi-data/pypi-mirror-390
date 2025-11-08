"""
Scanner module for Alprina CLI.
Handles remote and local security scanning using Alprina security agents.
"""

from pathlib import Path
from typing import Optional
import httpx
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from .auth import is_authenticated, get_auth_headers, get_backend_url
from .policy import validate_target
from .security_engine import run_remote_scan, run_local_scan
from .reporting import write_event
from .report_generator import generate_security_reports

console = Console()


def scan_command(
    target: str,
    profile: str = "default",
    safe_only: bool = True,
    output: Optional[Path] = None
):
    """
    Execute a security scan on a target (remote or local).
    """
    # Check if target is local or remote first
    target_path = Path(target)
    is_local = target_path.exists()

    # Only require auth for remote scans
    if not is_local and not is_authenticated():
        console.print(Panel(
            "[bold red]🔒 Authentication Required[/bold red]\n\n"
            "To use Alprina CLI, you need to authenticate first.\n\n"
            "[bold cyan]Quick Start:[/bold cyan]\n"
            "  1. Run: [bold]alprina auth login[/bold]\n"
            "  2. Browser opens → Sign in with GitHub\n"
            "  3. Authorize device → Done!\n\n"
            "[dim]Don't have an account? Visit:[/dim]\n"
            "[bold cyan]https://www.alprina.com[/bold cyan]\n\n"
            "[yellow]💡 Tip:[/yellow] Local scans work without authentication!",
            title="Welcome to Alprina CLI",
            border_style="red"
        ))
        return

    # Show warning if not authenticated for local scan
    if is_local and not is_authenticated():
        console.print("[yellow]⚠️  Running in offline mode (not authenticated)[/yellow]")

    console.print(Panel(
        f"🔍 Starting scan on: [bold]{target}[/bold]\n"
        f"Profile: [cyan]{profile}[/cyan]\n"
        f"Mode: {'[green]Safe only[/green]' if safe_only else '[yellow]Full scan[/yellow]'}",
        title="Alprina Security Scan"
    ))

    scan_id = None
    try:
        # Create scan entry in database (if authenticated)
        if is_authenticated():
            scan_id = _create_scan_entry(target, "local" if is_local else "remote", profile)
            if scan_id:
                console.print(f"[dim]Scan ID: {scan_id}[/dim]")

        # Execute scan
        if is_local:
            console.print(f"[cyan]→[/cyan] Detected local target: {target}")
            results = _scan_local(target, profile, safe_only)
        else:
            console.print(f"[cyan]→[/cyan] Detected remote target: {target}")
            validate_target(target)  # Check against policy
            results = _scan_remote(target, profile, safe_only)

        # Save results to database (if authenticated and scan was created)
        if is_authenticated() and scan_id:
            _save_scan_results(scan_id, results)
            console.print(f"[dim]✓ Scan saved to your account[/dim]")

        # Log the scan event locally
        write_event({
            "type": "scan",
            "target": target,
            "profile": profile,
            "mode": "local" if is_local else "remote",
            "safe_only": safe_only,
            "findings_count": len(results.get("findings", []))
        })

        # Display results
        _display_results(results)

        # Generate markdown security reports in .alprina/ folder
        if is_local and results.get("findings", []):
            try:
                report_dir = generate_security_reports(results, target)
                console.print(f"\n[green]✓[/green] Security reports generated in: [cyan]{report_dir}[/cyan]")
                console.print("[dim]Files created:[/dim]")
                console.print("[dim]  • SECURITY-REPORT.md - Full vulnerability analysis[/dim]")
                console.print("[dim]  • FINDINGS.md - Detailed findings with code context[/dim]")
                console.print("[dim]  • REMEDIATION.md - Step-by-step fix instructions[/dim]")
                console.print("[dim]  • EXECUTIVE-SUMMARY.md - Non-technical overview[/dim]")
            except Exception as report_error:
                console.print(f"[yellow]⚠️  Could not generate reports: {report_error}[/yellow]")

        if output:
            _save_results(results, output)

    except Exception as e:
        console.print(f"[red]Scan failed: {e}[/red]")


def _scan_local(target: str, profile: str, safe_only: bool) -> dict:
    """Execute local file/directory scan."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning local files...", total=None)

        results = run_local_scan(target, profile, safe_only)

        progress.update(task, completed=True)

    return results


def _scan_remote(target: str, profile: str, safe_only: bool) -> dict:
    """Execute remote target scan."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning remote target...", total=None)

        results = run_remote_scan(target, profile, safe_only)

        progress.update(task, completed=True)

    return results


def _display_results(results: dict):
    """Display scan results in a formatted table."""
    findings = results.get("findings", [])

    if not findings:
        console.print("\n[green]✓ No security issues found![/green]")
        return

    console.print(f"\n[yellow]⚠ Found {len(findings)} issues[/yellow]\n")

    table = Table(title="Security Findings", show_header=True, header_style="bold cyan")
    table.add_column("Severity", style="bold", width=10)
    table.add_column("Type", width=20)
    table.add_column("Description", width=50)
    table.add_column("Location", width=30)

    severity_colors = {
        "CRITICAL": "bold red",
        "HIGH": "red",
        "MEDIUM": "yellow",
        "LOW": "blue",
        "INFO": "dim"
    }

    for finding in findings:
        severity = finding.get("severity", "INFO")
        color = severity_colors.get(severity, "white")

        table.add_row(
            f"[{color}]{severity}[/{color}]",
            finding.get("type", "Unknown"),
            finding.get("description", "N/A"),
            finding.get("location", "N/A")
        )

    console.print(table)


def _save_results(results: dict, output: Path):
    """Save scan results to file."""
    import json

    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(results, f, indent=2)

    console.print(f"\n[green]✓[/green] Results saved to: {output}")


def recon_command(target: str, passive: bool = True):
    """
    Perform reconnaissance on a target.
    """
    if not is_authenticated():
        console.print("[red]Please login first: alprina auth login[/red]")
        return

    console.print(Panel(
        f"🕵️  Reconnaissance: [bold]{target}[/bold]\n"
        f"Mode: {'[green]Passive[/green]' if passive else '[yellow]Active[/yellow]'}",
        title="Alprina Recon"
    ))

    try:
        validate_target(target)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Gathering intelligence...", total=None)

            # Use Alprina security agent for reconnaissance
            from .security_engine import run_agent

            results = run_agent(
                task="web-recon",
                input_data=target,
                metadata={"passive": passive}
            )

            progress.update(task, completed=True)

        # Log event
        write_event({
            "type": "recon",
            "target": target,
            "passive": passive,
            "findings_count": len(results.get("findings", []))
        })

        console.print("\n[green]✓ Reconnaissance complete[/green]")
        _display_results(results)

    except Exception as e:
        console.print(f"[red]Recon failed: {e}[/red]")


def _create_scan_entry(target: str, scan_type: str, profile: str) -> Optional[str]:
    """Create a scan entry in the database before execution."""
    try:
        headers = get_auth_headers()
        backend_url = get_backend_url()

        response = httpx.post(
            f"{backend_url}/scans",
            headers=headers,
            json={
                "target": target,
                "scan_type": scan_type,
                "profile": profile
            },
            timeout=10.0
        )

        if response.status_code == 201:
            data = response.json()
            return data.get("scan_id")
        else:
            console.print(f"[yellow]⚠️  Could not create scan entry: {response.status_code}[/yellow]")
            return None

    except Exception as e:
        console.print(f"[yellow]⚠️  Could not create scan entry: {e}[/yellow]")
        return None


def _save_scan_results(scan_id: str, results: dict):
    """Save scan results to the database after completion."""
    try:
        headers = get_auth_headers()
        backend_url = get_backend_url()

        response = httpx.patch(
            f"{backend_url}/scans/{scan_id}",
            headers=headers,
            json={"results": results},
            timeout=30.0
        )

        if response.status_code != 200:
            console.print(f"[yellow]⚠️  Could not save scan results: {response.status_code}[/yellow]")

    except Exception as e:
        console.print(f"[yellow]⚠️  Could not save scan results: {e}[/yellow]")

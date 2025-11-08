"""
Reporting engine for Alprina CLI.
Generates structured reports in multiple formats (JSONL, HTML, PDF).
"""

import json
import os
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel

console = Console()

ALPRINA_DIR = Path.home() / ".alprina"
OUTPUT_DIR = ALPRINA_DIR / "out"
EVENTS_FILE = OUTPUT_DIR / "events.jsonl"


def ensure_output_dir():
    """Ensure output directory exists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_event(event: Dict[str, Any]):
    """
    Write an event to the JSONL log file.

    Args:
        event: Event dictionary to log
    """
    ensure_output_dir()

    # Add timestamp
    event["_timestamp"] = datetime.datetime.utcnow().isoformat()

    # Append to JSONL file
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


def load_events() -> list:
    """Load all events from the JSONL log file."""
    if not EVENTS_FILE.exists():
        return []

    events = []
    with open(EVENTS_FILE, "r") as f:
        for line in f:
            try:
                events.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    return events


def report_command(format: str = "html", output: Optional[Path] = None):
    """
    Generate a security report from scan results.

    Args:
        format: Report format (html, pdf, json)
        output: Output file path
    """
    console.print(Panel(
        f"📊 Generating report in [bold]{format.upper()}[/bold] format",
        title="Report Generation"
    ))

    # Load events
    events = load_events()

    if not events:
        console.print("[yellow]No scan events found. Run some scans first![/yellow]")
        return

    # Filter scan events
    scan_events = [e for e in events if e.get("type") in ["scan", "recon"]]

    if not scan_events:
        console.print("[yellow]No scan results found.[/yellow]")
        return

    console.print(f"Found {len(scan_events)} scan events")

    # Generate report based on format
    if format == "json":
        output_path = _generate_json_report(scan_events, output)
    elif format == "html":
        output_path = _generate_html_report(scan_events, output)
    elif format == "pdf":
        output_path = _generate_pdf_report(scan_events, output)
    else:
        console.print(f"[red]Unsupported format: {format}[/red]")
        return

    console.print(f"[green]✓ Report generated:[/green] {output_path}")


def _generate_json_report(events: list, output: Optional[Path] = None) -> Path:
    """Generate JSON report."""
    if output is None:
        output = OUTPUT_DIR / f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    ensure_output_dir()

    report = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "tool": "Alprina CLI",
        "version": "0.1.0",
        "total_scans": len(events),
        "events": events
    }

    with open(output, "w") as f:
        json.dump(report, f, indent=2)

    return output


def _generate_html_report(events: list, output: Optional[Path] = None) -> Path:
    """Generate HTML report."""
    if output is None:
        output = OUTPUT_DIR / f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    ensure_output_dir()

    # Extract all findings
    all_findings = []
    for event in events:
        findings = event.get("findings", [])
        if isinstance(findings, list):
            all_findings.extend(findings)

    # Count by severity
    severity_counts = {}
    for finding in all_findings:
        severity = finding.get("severity", "UNKNOWN")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    html_content = _create_html_template(events, all_findings, severity_counts)

    with open(output, "w") as f:
        f.write(html_content)

    return output


def _generate_pdf_report(events: list, output: Optional[Path] = None) -> Path:
    """Generate PDF report."""
    # First generate HTML
    html_path = _generate_html_report(events, None)

    if output is None:
        output = OUTPUT_DIR / f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    # Convert HTML to PDF using weasyprint
    try:
        from weasyprint import HTML
        HTML(filename=str(html_path)).write_pdf(output)
    except ImportError:
        console.print("[yellow]weasyprint not installed. Install with: pip install weasyprint[/yellow]")
        console.print(f"[yellow]HTML report available at: {html_path}[/yellow]")
        return html_path

    return output


def _create_html_template(events: list, findings: list, severity_counts: dict) -> str:
    """Create HTML report template."""
    severity_colors = {
        "CRITICAL": "#dc3545",
        "HIGH": "#fd7e14",
        "MEDIUM": "#ffc107",
        "LOW": "#0dcaf0",
        "INFO": "#6c757d"
    }

    findings_html = ""
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        color = severity_colors.get(severity, "#6c757d")

        findings_html += f"""
        <tr>
            <td style="color: {color}; font-weight: bold;">{severity}</td>
            <td>{finding.get('type', 'Unknown')}</td>
            <td>{finding.get('description', 'N/A')}</td>
            <td><code>{finding.get('location', 'N/A')}</code></td>
        </tr>
        """

    severity_summary_html = ""
    for severity, count in sorted(severity_counts.items()):
        color = severity_colors.get(severity, "#6c757d")
        severity_summary_html += f"""
        <div style="margin: 10px 0;">
            <span style="color: {color}; font-weight: bold;">{severity}:</span> {count}
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Alprina Security Report</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 40px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 3px solid #007bff;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #555;
                margin-top: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                text-align: left;
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background: #f8f9fa;
                font-weight: 600;
            }}
            .summary {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #6c757d;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Alprina Security Report</h1>

            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Generated:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Total Scans:</strong> {len(events)}</p>
                <p><strong>Total Findings:</strong> {len(findings)}</p>

                <h3>Findings by Severity</h3>
                {severity_summary_html}
            </div>

            <h2>Detailed Findings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Location</th>
                    </tr>
                </thead>
                <tbody>
                    {findings_html}
                </tbody>
            </table>

            <div class="footer">
                <p>Generated by Alprina CLI v0.1.0</p>
                <p>© 2025 Alprina. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

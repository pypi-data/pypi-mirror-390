"""
Mitigation suggestion module for Alprina CLI.
Provides AI-powered remediation guidance for security findings.
"""

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from .reporting import load_events
from .security_engine import run_agent

console = Console()


def mitigate_command(finding_id: Optional[str] = None, report_file: Optional[Path] = None):
    """
    Provide AI-powered mitigation suggestions for security findings.

    Args:
        finding_id: Specific finding ID to get mitigation for
        report_file: Path to report file to analyze
    """
    console.print(Panel("🛠️  Generating mitigation suggestions...", title="Alprina Mitigation"))

    # Load findings
    if report_file:
        findings = _load_findings_from_report(report_file)
    else:
        findings = _load_findings_from_events()

    if not findings:
        console.print("[yellow]No findings to mitigate[/yellow]")
        return

    # Filter to specific finding if requested
    if finding_id:
        findings = [f for f in findings if f.get("id") == finding_id]
        if not findings:
            console.print(f"[red]Finding {finding_id} not found[/red]")
            return

    # Generate mitigations for each finding
    for i, finding in enumerate(findings, 1):
        console.print(f"\n[bold cyan]Finding {i}/{len(findings)}[/bold cyan]")
        _generate_mitigation(finding)


def _load_findings_from_events() -> list:
    """Load findings from event log."""
    events = load_events()
    findings = []

    for event in events:
        if event.get("type") in ["scan", "recon"]:
            event_findings = event.get("findings", [])
            if isinstance(event_findings, list):
                findings.extend(event_findings)

    return findings


def _load_findings_from_report(report_path: Path) -> list:
    """Load findings from a report file."""
    import json

    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        return report.get("findings", [])
    except Exception as e:
        console.print(f"[red]Error loading report: {e}[/red]")
        return []


def _generate_mitigation(finding: dict):
    """
    Generate AI-powered mitigation suggestion for a single finding.

    Args:
        finding: Finding dictionary with severity, type, description, location
    """
    # Display finding info
    console.print(Panel(
        f"[bold]Severity:[/bold] {finding.get('severity', 'UNKNOWN')}\n"
        f"[bold]Type:[/bold] {finding.get('type', 'Unknown')}\n"
        f"[bold]Description:[/bold] {finding.get('description', 'N/A')}\n"
        f"[bold]Location:[/bold] {finding.get('location', 'N/A')}",
        title="Finding Details"
    ))

    # Use Alprina security agent to generate mitigation
    mitigation_prompt = f"""
    Security Finding:
    - Severity: {finding.get('severity')}
    - Type: {finding.get('type')}
    - Description: {finding.get('description')}
    - Location: {finding.get('location')}

    Provide:
    1. Risk explanation
    2. Step-by-step mitigation instructions
    3. Code examples if applicable
    4. Prevention best practices
    """

    try:
        result = run_agent(
            task="mitigation",
            input_data=mitigation_prompt,
            metadata=finding
        )

        mitigation_text = result.get("mitigation", "No specific mitigation available")

        # Display mitigation as markdown
        console.print("\n[bold green]Mitigation Guidance:[/bold green]")
        console.print(Markdown(mitigation_text))

    except Exception as e:
        console.print(f"[red]Error generating mitigation: {e}[/red]")

        # Provide fallback generic guidance
        _provide_generic_mitigation(finding)


def _provide_generic_mitigation(finding: dict):
    """Provide generic mitigation guidance based on finding type."""
    finding_type = finding.get("type", "").lower()

    generic_mitigations = {
        "hardcoded secret": """
        ### Mitigation Steps:
        1. **Remove** the hardcoded secret from the code immediately
        2. **Rotate** the exposed credentials/keys
        3. **Use environment variables** or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault)
        4. **Add** sensitive files to `.gitignore`
        5. **Audit** git history to ensure secret is not in past commits

        ### Prevention:
        - Use pre-commit hooks to scan for secrets
        - Implement automated secret scanning in CI/CD
        - Use tools like `git-secrets` or `trufflehog`
        """,

        "debug mode": """
        ### Mitigation Steps:
        1. **Disable** debug mode in production environments
        2. **Use** environment-based configuration (e.g., `DEBUG=False` in production)
        3. **Review** all debug-related settings

        ### Prevention:
        - Use separate config files for dev/staging/production
        - Implement configuration validation in deployment pipeline
        """,

        "environment file": """
        ### Mitigation Steps:
        1. **Ensure** `.env` files are in `.gitignore`
        2. **Remove** `.env` from git history if committed
        3. **Use** `.env.example` template without actual secrets

        ### Prevention:
        - Never commit `.env` files
        - Use environment-specific files (`.env.production`, `.env.development`)
        - Document required environment variables
        """,
    }

    mitigation = generic_mitigations.get(finding_type, """
    ### General Security Best Practices:
    1. Follow the principle of least privilege
    2. Keep dependencies up to date
    3. Implement proper input validation
    4. Use security linters and scanners
    5. Conduct regular security audits
    """)

    console.print(Markdown(mitigation))

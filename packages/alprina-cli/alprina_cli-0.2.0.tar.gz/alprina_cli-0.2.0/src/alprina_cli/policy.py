"""
Policy and guardrails engine for Alprina CLI.
Enforces scope, safety rules, and compliance checks.
"""

import yaml
from pathlib import Path
from typing import List, Optional
from ipaddress import ip_network, ip_address, AddressValueError
from urllib.parse import urlparse
from rich.console import Console
from rich.panel import Panel

console = Console()

ALPRINA_DIR = Path.home() / ".alprina"
POLICY_FILE = ALPRINA_DIR / "policy.yml"

DEFAULT_POLICY = {
    "project": "Alprina Security Audit",
    "scope": {
        "allow_domains": [],
        "allow_cidrs": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
        "forbid_ports": [22, 3389],  # SSH, RDP
    },
    "policies": {
        "allow_intrusive": False,
        "require_terms_ack": True,
        "max_concurrent_scans": 5,
    },
    "billing": {
        "plan": "free",
        "max_scans_per_day": 10,
    }
}


def load_policy() -> dict:
    """Load policy configuration from file."""
    if not POLICY_FILE.exists():
        return DEFAULT_POLICY.copy()

    try:
        with open(POLICY_FILE, "r") as f:
            policy = yaml.safe_load(f)
        return policy or DEFAULT_POLICY.copy()
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load policy file: {e}[/yellow]")
        return DEFAULT_POLICY.copy()


def save_policy(policy: dict):
    """Save policy configuration to file."""
    ALPRINA_DIR.mkdir(exist_ok=True)

    with open(POLICY_FILE, "w") as f:
        yaml.dump(policy, f, default_flow_style=False, sort_keys=False)


def validate_target(target: str, policy: Optional[dict] = None) -> bool:
    """
    Validate a target against policy rules.

    Args:
        target: Target URL, domain, or IP
        policy: Policy dict (loads from file if not provided)

    Returns:
        True if target is allowed

    Raises:
        ValueError: If target violates policy
    """
    if policy is None:
        policy = load_policy()

    scope = policy.get("scope", {})

    # Try to parse as IP address
    try:
        ip = ip_address(target)
        return _validate_ip(ip, scope)
    except (AddressValueError, ValueError):
        pass

    # Try to parse as URL
    if "://" in target:
        parsed = urlparse(target)
        domain = parsed.hostname
        port = parsed.port

        if port and port in scope.get("forbid_ports", []):
            raise ValueError(f"Port {port} is forbidden by policy")

        return _validate_domain(domain, scope)

    # Treat as domain
    return _validate_domain(target, scope)


def _validate_ip(ip: ip_address, scope: dict) -> bool:
    """Validate IP address against allowed CIDR ranges."""
    allow_cidrs = scope.get("allow_cidrs", [])

    if not allow_cidrs:
        # If no CIDRs specified, allow all private IPs
        return ip.is_private

    for cidr in allow_cidrs:
        if ip in ip_network(cidr):
            return True

    raise ValueError(f"IP {ip} is not in allowed CIDR ranges: {allow_cidrs}")


def _validate_domain(domain: str, scope: dict) -> bool:
    """Validate domain against allowed domains."""
    allow_domains = scope.get("allow_domains", [])

    if not allow_domains:
        # If no domains specified, allow all
        console.print("[yellow]Warning: No domain restrictions in policy. All domains allowed.[/yellow]")
        return True

    # Check if domain matches or is subdomain of allowed domains
    for allowed in allow_domains:
        if domain == allowed or domain.endswith(f".{allowed}"):
            return True

    raise ValueError(f"Domain {domain} is not in allowed domains: {allow_domains}")


def validate_file(path: Path) -> bool:
    """Validate if file type is allowed for scanning."""
    allowed_extensions = (
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
        ".env", ".yaml", ".yml", ".json", ".xml", ".ini", ".conf",
        ".sh", ".bash", ".zsh", ".dockerfile", ".tf", ".hcl"
    )

    if not path.suffix.lower() in allowed_extensions:
        raise ValueError(f"File type {path.suffix} is not supported for scanning")

    return True


def policy_init_command():
    """Initialize a new policy configuration file."""
    if POLICY_FILE.exists():
        console.print("[yellow]Policy file already exists. Overwrite? (y/N)[/yellow]")
        from rich.prompt import Confirm
        if not Confirm.ask("Overwrite existing policy?", default=False):
            return

    save_policy(DEFAULT_POLICY)

    console.print(Panel(
        f"[green]✓ Policy file created[/green]\n\n"
        f"Location: {POLICY_FILE}\n\n"
        f"Edit this file to customize your security scanning policies.",
        title="Policy Initialized"
    ))


def policy_test_command(target: str):
    """Test if a target is allowed by current policy."""
    console.print(f"Testing policy for target: [bold]{target}[/bold]\n")

    try:
        policy = load_policy()
        validate_target(target, policy)
        console.print(f"[green]✓ Target is allowed by policy[/green]")
    except ValueError as e:
        console.print(f"[red]✗ Target blocked by policy:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def check_intrusive_allowed(policy: Optional[dict] = None) -> bool:
    """Check if intrusive scans are allowed by policy."""
    if policy is None:
        policy = load_policy()

    return policy.get("policies", {}).get("allow_intrusive", False)


def get_scan_limits(policy: Optional[dict] = None) -> dict:
    """Get scan limits from policy."""
    if policy is None:
        policy = load_policy()

    billing = policy.get("billing", {})

    return {
        "max_scans_per_day": billing.get("max_scans_per_day", 10),
        "max_concurrent_scans": policy.get("policies", {}).get("max_concurrent_scans", 5),
    }

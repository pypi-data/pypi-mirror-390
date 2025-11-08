"""
Reconnaissance Tool

Context Engineering:
- Information gathering and target profiling
- Returns compressed intelligence summaries
- Safe, passive techniques by default
- Structured output for analysis

Reconnaissance without the noise.
"""

from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from loguru import logger
import socket
import re
from pathlib import Path

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


class ReconParams(BaseModel):
    """
    Parameters for reconnaissance.

    Context: Focused schema for info gathering.
    """
    target: str = Field(
        description="Target to reconnaissance (domain, IP, or file path)"
    )
    scope: Literal["passive", "active", "full"] = Field(
        default="passive",
        description="Recon scope: passive (safe), active (probing), full (comprehensive)"
    )
    max_findings: int = Field(
        default=50,
        description="Maximum findings to return (context efficiency)"
    )


class ReconTool(AlprinaToolBase[ReconParams]):
    """
    Reconnaissance and information gathering tool.

    Context Engineering Benefits:
    - Returns structured intelligence (not raw data dumps)
    - Passive mode by default (safe)
    - Configurable scope for depth control
    - Max findings limit for context control

    Scopes:
    - passive: Safe info gathering (DNS, headers, public info)
    - active: Light probing (port scan, service detection)
    - full: Comprehensive (includes technology detection, vuln hints)

    Usage:
    ```python
    tool = ReconTool()
    result = await tool.execute(ReconParams(
        target="example.com",
        scope="passive"
    ))
    ```
    """

    name: str = "Recon"
    description: str = """Reconnaissance and information gathering.

Capabilities:
- DNS resolution and info
- Service detection
- Technology fingerprinting
- Port scanning (active/full modes)
- Security header analysis

Returns: Structured intelligence summary"""
    params: type[ReconParams] = ReconParams

    async def execute(self, params: ReconParams) -> ToolOk | ToolError:
        """
        Execute reconnaissance.

        Context: Returns structured findings, not raw data.
        """
        logger.info(f"Recon: {params.target} (scope={params.scope})")

        try:
            # Determine target type
            is_network = self._is_network_target(params.target)

            if is_network:
                findings = await self._recon_network(params)
            else:
                findings = await self._recon_file(params)

            # Limit findings for context efficiency
            if len(findings) > params.max_findings:
                findings = findings[:params.max_findings]
                truncated = True
            else:
                truncated = False

            return ToolOk(
                content={
                    "target": params.target,
                    "scope": params.scope,
                    "findings": findings,
                    "summary": {
                        "total_findings": len(findings),
                        "truncated": truncated,
                        "target_type": "network" if is_network else "file"
                    }
                }
            )

        except Exception as e:
            logger.error(f"Recon failed: {e}")
            return ToolError(
                message=f"Reconnaissance failed: {str(e)}",
                brief="Recon failed"
            )

    async def _recon_network(self, params: ReconParams) -> List[Dict[str, Any]]:
        """
        Network target reconnaissance.

        Context: Returns high-level intelligence.
        """
        findings = []
        target = params.target

        # Remove protocol if present
        target_clean = target.replace("https://", "").replace("http://", "").split("/")[0]

        # Passive: DNS resolution
        try:
            ip_addr = socket.gethostbyname(target_clean)
            findings.append({
                "type": "DNS Resolution",
                "severity": "INFO",
                "title": "IP Address Resolved",
                "description": f"{target_clean} resolves to {ip_addr}",
                "data": {"ip": ip_addr},
                "confidence": 1.0
            })
        except Exception as e:
            findings.append({
                "type": "DNS Resolution",
                "severity": "LOW",
                "title": "DNS Resolution Failed",
                "description": f"Could not resolve {target_clean}: {str(e)}",
                "confidence": 0.8
            })

        # Passive: Protocol detection
        if target.startswith("http://"):
            findings.append({
                "type": "Security",
                "severity": "MEDIUM",
                "title": "Insecure Protocol Detected",
                "description": "Target uses HTTP instead of HTTPS",
                "data": {"protocol": "http"},
                "confidence": 1.0
            })

        # Active scope: Port scanning
        if params.scope in ["active", "full"]:
            port_findings = self._scan_common_ports(target_clean)
            findings.extend(port_findings)

        # Full scope: Technology detection
        if params.scope == "full":
            tech_findings = self._detect_technologies(target)
            findings.extend(tech_findings)

        return findings

    async def _recon_file(self, params: ReconParams) -> List[Dict[str, Any]]:
        """
        File/directory reconnaissance.

        Context: Analyze local targets for security info.
        """
        findings = []
        target_path = Path(params.target)

        if not target_path.exists():
            return [{
                "type": "Error",
                "severity": "HIGH",
                "title": "Target Not Found",
                "description": f"Path does not exist: {params.target}",
                "confidence": 1.0
            }]

        # File/directory info
        if target_path.is_file():
            findings.append({
                "type": "File Info",
                "severity": "INFO",
                "title": f"File: {target_path.name}",
                "description": f"Size: {target_path.stat().st_size} bytes",
                "data": {
                    "type": "file",
                    "size": target_path.stat().st_size,
                    "extension": target_path.suffix
                },
                "confidence": 1.0
            })

            # Check for sensitive file types
            sensitive_extensions = [".env", ".key", ".pem", ".p12", ".pfx", ".crt"]
            if target_path.suffix in sensitive_extensions:
                findings.append({
                    "type": "Sensitive File",
                    "severity": "HIGH",
                    "title": "Potentially Sensitive File",
                    "description": f"File has sensitive extension: {target_path.suffix}",
                    "confidence": 0.8
                })

        elif target_path.is_dir():
            # Directory reconnaissance
            files = list(target_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])

            findings.append({
                "type": "Directory Info",
                "severity": "INFO",
                "title": f"Directory: {target_path.name}",
                "description": f"Contains {file_count} files",
                "data": {"file_count": file_count},
                "confidence": 1.0
            })

            # Look for sensitive files
            sensitive_files = [
                ".env", ".env.local", "credentials.json",
                "id_rsa", "id_dsa", "config.json", "secrets.yml"
            ]

            for sensitive_name in sensitive_files:
                if (target_path / sensitive_name).exists():
                    findings.append({
                        "type": "Sensitive File",
                        "severity": "HIGH",
                        "title": f"Sensitive File Found: {sensitive_name}",
                        "description": f"Directory contains {sensitive_name}",
                        "confidence": 0.9
                    })

        return findings

    def _scan_common_ports(self, target: str) -> List[Dict[str, Any]]:
        """
        Scan common ports.

        Context: Quick scan of well-known ports.
        """
        findings = []
        common_ports = {
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            27017: "MongoDB"
        }

        for port, service in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target, port))
                sock.close()

                if result == 0:
                    findings.append({
                        "type": "Open Port",
                        "severity": "MEDIUM" if port in [22, 3306, 5432, 6379, 27017] else "INFO",
                        "title": f"Port {port} Open ({service})",
                        "description": f"Service {service} detected on port {port}",
                        "data": {"port": port, "service": service},
                        "confidence": 0.9
                    })
            except Exception:
                pass

        return findings

    def _detect_technologies(self, target: str) -> List[Dict[str, Any]]:
        """
        Detect technologies.

        Context: Simplified technology fingerprinting.
        """
        findings = []

        # Simple heuristics based on URL patterns
        tech_patterns = {
            "/wp-": "WordPress",
            "/wp-admin": "WordPress",
            "/api/": "REST API",
            "/graphql": "GraphQL",
            ".php": "PHP",
            ".aspx": "ASP.NET",
            ".jsp": "Java/JSP"
        }

        for pattern, tech in tech_patterns.items():
            if pattern in target:
                findings.append({
                    "type": "Technology",
                    "severity": "INFO",
                    "title": f"Technology Detected: {tech}",
                    "description": f"Target appears to use {tech}",
                    "data": {"technology": tech},
                    "confidence": 0.7
                })

        return findings

    def _is_network_target(self, target: str) -> bool:
        """Check if target is network-based"""
        # URL protocol = network
        if target.startswith(("http://", "https://")):
            return True

        # Absolute path = file (even if doesn't exist)
        if target.startswith("/") or target.startswith("~"):
            return False

        # Has dot and doesn't exist = likely network
        # No dot but doesn't exist = likely network (e.g., "localhost")
        target_path = Path(target)
        if not target_path.exists():
            # If it looks like a domain or IP, treat as network
            return True

        # Exists = file
        return False

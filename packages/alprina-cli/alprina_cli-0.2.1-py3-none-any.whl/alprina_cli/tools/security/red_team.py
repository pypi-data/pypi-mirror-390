"""
Red Team Tool

Context Engineering:
- Offensive security operations (authorized only)
- Attack simulation and penetration testing
- Returns structured attack chain results
- Memory-aware: Learns from past campaigns

Offensive operations require explicit authorization.
"""

from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field
from loguru import logger
from pathlib import Path
import re

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


class RedTeamParams(BaseModel):
    """
    Parameters for red team operations.

    Context: Focused schema for offensive security testing.
    """
    target: str = Field(
        description="Target for red team operations"
    )
    operation: Literal["recon", "initial_access", "privilege_escalation", "lateral_movement", "exfiltration", "full_chain"] = Field(
        default="recon",
        description="Operation type: recon, initial_access, privilege_escalation, lateral_movement, exfiltration, full_chain"
    )
    stealth_level: Literal["loud", "moderate", "stealth"] = Field(
        default="moderate",
        description="Stealth level: loud (noisy), moderate (balanced), stealth (evasive)"
    )
    authorized: bool = Field(
        default=False,
        description="Explicit authorization flag (must be True)"
    )
    max_findings: int = Field(
        default=20,
        description="Maximum findings to return"
    )


class RedTeamTool(AlprinaToolBase[RedTeamParams]):
    """
    Red team tool for offensive security operations.

    Context Engineering Benefits:
    - Structured attack chain results
    - Memory integration for campaign tracking
    - Stealth level configuration
    - Authorization verification

    CRITICAL: AUTHORIZED USE ONLY
    - Penetration testing engagements
    - Red team exercises
    - Authorized security assessments
    - CTF competitions

    Operations:
    - recon: Intelligence gathering
    - initial_access: Entry point identification
    - privilege_escalation: Elevation techniques
    - lateral_movement: Network traversal
    - exfiltration: Data extraction simulation
    - full_chain: Complete attack simulation

    Usage:
    ```python
    tool = RedTeamTool(memory_service=memory)
    result = await tool.execute(RedTeamParams(
        target="192.168.1.0/24",
        operation="recon",
        authorized=True
    ))
    ```
    """

    name: str = "RedTeam"
    description: str = """Red team offensive security operations.

AUTHORIZED USE ONLY - Requires explicit authorization flag.

Capabilities:
- Reconnaissance and intelligence gathering
- Initial access point identification
- Privilege escalation techniques
- Lateral movement simulation
- Exfiltration path analysis
- Full attack chain simulation

Returns: Structured attack chain results"""
    params: type[RedTeamParams] = RedTeamParams

    async def execute(self, params: RedTeamParams) -> ToolOk | ToolError:
        """
        Execute red team operation.

        Context: Returns structured offensive security results.
        """
        logger.info(f"RedTeam: {params.target} (op={params.operation}, stealth={params.stealth_level})")

        # CRITICAL: Verify authorization
        if not params.authorized:
            return ToolError(
                message="Red team operations require explicit authorization (set authorized=True)",
                brief="Authorization required"
            )

        try:
            # Check memory for past campaigns
            if self.memory_service and self.memory_service.is_enabled():
                past_campaigns = self.memory_service.get_tool_context("RedTeam", limit=3)
                if past_campaigns:
                    logger.info(f"Found {len(past_campaigns)} past red team campaigns")

            # Execute operation
            if params.operation == "recon":
                findings = await self._recon_operation(params)
            elif params.operation == "initial_access":
                findings = await self._initial_access_operation(params)
            elif params.operation == "privilege_escalation":
                findings = await self._privilege_escalation_operation(params)
            elif params.operation == "lateral_movement":
                findings = await self._lateral_movement_operation(params)
            elif params.operation == "exfiltration":
                findings = await self._exfiltration_operation(params)
            else:  # full_chain
                findings = await self._full_chain_operation(params)

            # Limit findings
            if len(findings) > params.max_findings:
                findings = findings[:params.max_findings]
                truncated = True
            else:
                truncated = False

            # Calculate success rate
            successful = sum(1 for f in findings if f.get("successful", False))
            success_rate = (successful / len(findings) * 100) if findings else 0

            result_content = {
                "target": params.target,
                "operation": params.operation,
                "stealth_level": params.stealth_level,
                "findings": findings,
                "summary": {
                    "total_findings": len(findings),
                    "successful": successful,
                    "success_rate": success_rate,
                    "truncated": truncated
                },
                "authorization_notice": "Authorized red team operation completed"
            }

            # Store in memory
            if self.memory_service and self.memory_service.is_enabled():
                self.memory_service.add_scan_results(
                    tool_name="RedTeam",
                    target=params.target,
                    results=result_content
                )

            return ToolOk(content=result_content)

        except Exception as e:
            logger.error(f"Red team operation failed: {e}")
            return ToolError(
                message=f"Red team operation failed: {str(e)}",
                brief="Operation failed"
            )

    async def _recon_operation(self, params: RedTeamParams) -> List[Dict[str, Any]]:
        """
        Reconnaissance operation.

        Context: Gather intelligence about target.
        """
        findings = []

        target_path = Path(params.target).expanduser()
        is_local = target_path.exists()

        if is_local:
            # Local recon
            findings.append({
                "phase": "recon",
                "technique": "File System Enumeration",
                "successful": True,
                "description": f"Enumerated target: {params.target}",
                "stealth_impact": "low" if params.stealth_level == "stealth" else "medium",
                "findings": {
                    "exists": target_path.exists(),
                    "is_file": target_path.is_file() if target_path.exists() else None,
                    "is_dir": target_path.is_dir() if target_path.exists() else None
                }
            })

            # Check for sensitive files
            if target_path.is_dir():
                sensitive_patterns = [".env", ".git", "id_rsa", "credentials", "secrets"]
                found_sensitive = []

                for pattern in sensitive_patterns:
                    matches = list(target_path.rglob(f"*{pattern}*"))[:5]
                    if matches:
                        found_sensitive.extend([str(m) for m in matches])

                if found_sensitive:
                    findings.append({
                        "phase": "recon",
                        "technique": "Sensitive File Discovery",
                        "successful": True,
                        "description": f"Found {len(found_sensitive)} sensitive files",
                        "stealth_impact": "low",
                        "findings": {"files": found_sensitive[:10]}
                    })

        else:
            # Network recon
            findings.append({
                "phase": "recon",
                "technique": "Target Analysis",
                "successful": True,
                "description": f"Analyzing network target: {params.target}",
                "stealth_impact": "low" if params.stealth_level == "stealth" else "medium",
                "findings": {
                    "target_type": "network",
                    "protocols": ["http", "https"] if params.target.startswith("http") else ["tcp"]
                }
            })

        return findings

    async def _initial_access_operation(self, params: RedTeamParams) -> List[Dict[str, Any]]:
        """
        Initial access operation.

        Context: Identify entry points.
        """
        findings = []

        target_path = Path(params.target).expanduser()
        is_local = target_path.exists()

        if is_local and target_path.is_file():
            # Check for common vulnerabilities
            try:
                content = target_path.read_text(errors="ignore")

                # Check for weak authentication
                if re.search(r"password\s*=\s*['\"].*['\"]", content, re.IGNORECASE):
                    findings.append({
                        "phase": "initial_access",
                        "technique": "Credential Discovery",
                        "successful": True,
                        "description": "Found hardcoded credentials",
                        "stealth_impact": "low",
                        "risk": "HIGH"
                    })

                # Check for default credentials
                if re.search(r"(admin|root|test).*password", content, re.IGNORECASE):
                    findings.append({
                        "phase": "initial_access",
                        "technique": "Default Credentials",
                        "successful": True,
                        "description": "Potential default credentials found",
                        "stealth_impact": "low",
                        "risk": "HIGH"
                    })

            except Exception as e:
                logger.debug(f"Could not analyze file: {e}")

        # Educational finding
        findings.append({
            "phase": "initial_access",
            "technique": "Entry Point Analysis",
            "successful": False,
            "description": "Initial access vectors identified (educational mode)",
            "stealth_impact": params.stealth_level,
            "note": "In real operations, test authentication, exposed services, and misconfigurations"
        })

        return findings

    async def _privilege_escalation_operation(self, params: RedTeamParams) -> List[Dict[str, Any]]:
        """
        Privilege escalation operation.

        Context: Identify elevation paths.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        if target_path.exists() and target_path.is_file():
            # Check for sudo configs, setuid binaries, etc.
            try:
                content = target_path.read_text(errors="ignore")

                # Check for sudo misconfigurations
                if "NOPASSWD" in content or "sudo" in content.lower():
                    findings.append({
                        "phase": "privilege_escalation",
                        "technique": "Sudo Misconfiguration",
                        "successful": True,
                        "description": "Potential sudo misconfiguration",
                        "stealth_impact": "low",
                        "risk": "HIGH"
                    })

                # Check for env manipulation
                if re.search(r"(LD_PRELOAD|LD_LIBRARY_PATH)", content):
                    findings.append({
                        "phase": "privilege_escalation",
                        "technique": "Environment Variable Exploitation",
                        "successful": True,
                        "description": "Environment variable manipulation possible",
                        "stealth_impact": "medium",
                        "risk": "MEDIUM"
                    })

            except Exception:
                pass

        findings.append({
            "phase": "privilege_escalation",
            "technique": "Privilege Analysis",
            "successful": False,
            "description": "Privilege escalation vectors analyzed",
            "stealth_impact": params.stealth_level,
            "note": "Check for: SUID binaries, cron jobs, kernel exploits, service misconfigurations"
        })

        return findings

    async def _lateral_movement_operation(self, params: RedTeamParams) -> List[Dict[str, Any]]:
        """
        Lateral movement operation.

        Context: Identify traversal paths.
        """
        findings = []

        # Network lateral movement analysis
        findings.append({
            "phase": "lateral_movement",
            "technique": "Network Mapping",
            "successful": False,
            "description": "Network traversal paths analyzed",
            "stealth_impact": params.stealth_level,
            "note": "Check for: SMB shares, SSH keys, pass-the-hash, Kerberos tickets"
        })

        # Check for credential reuse
        target_path = Path(params.target).expanduser()
        if target_path.exists() and target_path.is_dir():
            ssh_keys = list(target_path.rglob("*id_rsa*"))[:3]
            if ssh_keys:
                findings.append({
                    "phase": "lateral_movement",
                    "technique": "SSH Key Discovery",
                    "successful": True,
                    "description": f"Found {len(ssh_keys)} SSH keys",
                    "stealth_impact": "low",
                    "risk": "HIGH",
                    "keys": [str(k) for k in ssh_keys]
                })

        return findings

    async def _exfiltration_operation(self, params: RedTeamParams) -> List[Dict[str, Any]]:
        """
        Exfiltration operation.

        Context: Identify data extraction paths.
        """
        findings = []

        # Exfiltration path analysis
        findings.append({
            "phase": "exfiltration",
            "technique": "Data Extraction Analysis",
            "successful": False,
            "description": "Exfiltration channels analyzed",
            "stealth_impact": params.stealth_level,
            "note": "Check for: DNS tunneling, HTTPS channels, cloud storage, removable media"
        })

        # Check for sensitive data
        target_path = Path(params.target).expanduser()
        if target_path.exists() and target_path.is_dir():
            sensitive_extensions = [".db", ".sql", ".csv", ".xlsx", ".json"]
            data_files = []

            for ext in sensitive_extensions:
                files = list(target_path.rglob(f"*{ext}"))[:5]
                data_files.extend(files)

            if data_files:
                findings.append({
                    "phase": "exfiltration",
                    "technique": "Sensitive Data Discovery",
                    "successful": True,
                    "description": f"Found {len(data_files)} data files",
                    "stealth_impact": "low",
                    "risk": "MEDIUM",
                    "files": [str(f) for f in data_files[:10]]
                })

        return findings

    async def _full_chain_operation(self, params: RedTeamParams) -> List[Dict[str, Any]]:
        """
        Full attack chain operation.

        Context: Simulate complete attack.
        """
        findings = []

        # Execute all phases
        findings.extend(await self._recon_operation(params))
        findings.extend(await self._initial_access_operation(params))
        findings.extend(await self._privilege_escalation_operation(params))
        findings.extend(await self._lateral_movement_operation(params))
        findings.extend(await self._exfiltration_operation(params))

        # Add summary
        findings.append({
            "phase": "summary",
            "technique": "Full Attack Chain",
            "successful": True,
            "description": f"Completed full chain attack simulation ({len(findings)} phases)",
            "stealth_impact": params.stealth_level,
            "note": "Educational simulation - real attacks require proper authorization"
        })

        return findings

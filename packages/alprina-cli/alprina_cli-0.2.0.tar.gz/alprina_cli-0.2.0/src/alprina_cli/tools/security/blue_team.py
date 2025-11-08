"""
Blue Team Tool

Context Engineering:
- Defensive security operations
- Threat detection and incident response
- Returns structured defensive findings
- Memory-aware: Tracks threats and patterns

Defend, detect, respond.
"""

from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field
from loguru import logger
from pathlib import Path
import re
from datetime import datetime

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


class BlueTeamParams(BaseModel):
    """
    Parameters for blue team operations.

    Context: Focused schema for defensive security.
    """
    target: str = Field(
        description="Target for blue team operations (logs, systems, network)"
    )
    operation: Literal["threat_hunt", "incident_response", "log_analysis", "ioc_search", "baseline", "full_defense"] = Field(
        default="threat_hunt",
        description="Operation: threat_hunt, incident_response, log_analysis, ioc_search, baseline, full_defense"
    )
    severity_threshold: Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        default="MEDIUM",
        description="Minimum severity to report"
    )
    max_findings: int = Field(
        default=50,
        description="Maximum findings to return"
    )


class BlueTeamTool(AlprinaToolBase[BlueTeamParams]):
    """
    Blue team tool for defensive security operations.

    Context Engineering Benefits:
    - Structured threat findings
    - Memory integration for pattern tracking
    - Severity-based filtering
    - IOC detection and correlation

    Operations:
    - threat_hunt: Proactive threat hunting
    - incident_response: Respond to incidents
    - log_analysis: Analyze logs for anomalies
    - ioc_search: Search for indicators of compromise
    - baseline: Establish security baseline
    - full_defense: Comprehensive defensive assessment

    Usage:
    ```python
    tool = BlueTeamTool(memory_service=memory)
    result = await tool.execute(BlueTeamParams(
        target="/var/log",
        operation="threat_hunt",
        severity_threshold="HIGH"
    ))
    ```
    """

    name: str = "BlueTeam"
    description: str = """Blue team defensive security operations.

Capabilities:
- Proactive threat hunting
- Incident response procedures
- Log analysis and anomaly detection
- IOC search and correlation
- Security baseline establishment
- Comprehensive defensive assessment

Returns: Structured defensive findings"""
    params: type[BlueTeamParams] = BlueTeamParams

    # Common IOCs to search for
    KNOWN_IOCS = {
        "malicious_ips": ["10.0.0.0/8", "192.168.0.0/16"],  # Example private ranges
        "suspicious_commands": ["nc -e", "bash -i", "/dev/tcp", "python -c", "perl -e"],
        "malware_signatures": ["mimikatz", "powersploit", "metasploit", "cobalt"],
        "suspicious_files": [".exe.txt", ".scr", ".vbs", ".ps1"],
    }

    async def execute(self, params: BlueTeamParams) -> ToolOk | ToolError:
        """
        Execute blue team operation.

        Context: Returns structured defensive findings.
        """
        logger.info(f"BlueTeam: {params.target} (op={params.operation}, severity={params.severity_threshold})")

        try:
            # Check memory for past threats
            if self.memory_service and self.memory_service.is_enabled():
                past_threats = self.memory_service.search(
                    f"Previous threats found in {params.target}",
                    limit=5
                )
                if past_threats:
                    logger.info(f"Found {len(past_threats)} past threat records")

            # Execute operation
            if params.operation == "threat_hunt":
                findings = await self._threat_hunt_operation(params)
            elif params.operation == "incident_response":
                findings = await self._incident_response_operation(params)
            elif params.operation == "log_analysis":
                findings = await self._log_analysis_operation(params)
            elif params.operation == "ioc_search":
                findings = await self._ioc_search_operation(params)
            elif params.operation == "baseline":
                findings = await self._baseline_operation(params)
            else:  # full_defense
                findings = await self._full_defense_operation(params)

            # Filter by severity
            findings = self._filter_by_severity(findings, params.severity_threshold)

            # Limit findings
            if len(findings) > params.max_findings:
                findings = findings[:params.max_findings]
                truncated = True
            else:
                truncated = False

            # Calculate threat stats
            severity_counts = {}
            threat_detected = False
            for finding in findings:
                sev = finding.get("severity", "INFO")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                if finding.get("threat_detected", False):
                    threat_detected = True

            result_content = {
                "target": params.target,
                "operation": params.operation,
                "findings": findings,
                "summary": {
                    "total_findings": len(findings),
                    "threat_detected": threat_detected,
                    "by_severity": severity_counts,
                    "truncated": truncated,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            # Store in memory
            if self.memory_service and self.memory_service.is_enabled():
                self.memory_service.add_scan_results(
                    tool_name="BlueTeam",
                    target=params.target,
                    results=result_content
                )

            return ToolOk(content=result_content)

        except Exception as e:
            logger.error(f"Blue team operation failed: {e}")
            return ToolError(
                message=f"Blue team operation failed: {str(e)}",
                brief="Operation failed"
            )

    async def _threat_hunt_operation(self, params: BlueTeamParams) -> List[Dict[str, Any]]:
        """
        Proactive threat hunting.

        Context: Hunt for hidden threats.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        if target_path.exists():
            if target_path.is_file():
                findings.extend(self._hunt_file(target_path))
            else:
                # Hunt directory
                files_checked = 0
                for file_path in target_path.rglob("*"):
                    if file_path.is_file() and files_checked < 50:
                        findings.extend(self._hunt_file(file_path))
                        files_checked += 1

        # Add hunt summary
        findings.append({
            "operation": "threat_hunt",
            "technique": "Proactive Hunting",
            "severity": "INFO",
            "description": f"Completed threat hunt on {params.target}",
            "files_checked": files_checked if target_path.is_dir() else 1,
            "threat_detected": any(f.get("threat_detected") for f in findings)
        })

        return findings

    def _hunt_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Hunt for threats in a file"""
        findings = []

        try:
            # Skip binary files
            if self._is_binary(file_path):
                return findings

            content = file_path.read_text(errors="ignore")

            # Check for suspicious commands
            for cmd in self.KNOWN_IOCS["suspicious_commands"]:
                if cmd in content:
                    findings.append({
                        "operation": "threat_hunt",
                        "technique": "Suspicious Command Detection",
                        "severity": "HIGH",
                        "threat_detected": True,
                        "description": f"Suspicious command found: {cmd}",
                        "file": str(file_path),
                        "ioc": cmd
                    })

            # Check for malware signatures
            for signature in self.KNOWN_IOCS["malware_signatures"]:
                if signature.lower() in content.lower():
                    findings.append({
                        "operation": "threat_hunt",
                        "technique": "Malware Signature Detection",
                        "severity": "CRITICAL",
                        "threat_detected": True,
                        "description": f"Malware signature detected: {signature}",
                        "file": str(file_path),
                        "ioc": signature
                    })

            # Check for encoded payloads
            if re.search(r"base64|fromCharCode|eval\(", content):
                findings.append({
                    "operation": "threat_hunt",
                    "technique": "Encoded Payload Detection",
                    "severity": "MEDIUM",
                    "threat_detected": True,
                    "description": "Potential encoded payload",
                    "file": str(file_path)
                })

        except Exception as e:
            logger.debug(f"Could not hunt file {file_path}: {e}")

        return findings

    async def _incident_response_operation(self, params: BlueTeamParams) -> List[Dict[str, Any]]:
        """
        Incident response procedures.

        Context: Respond to security incidents.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        # Check for incident artifacts
        if target_path.exists():
            # Look for recently modified files (potential compromise)
            if target_path.is_dir():
                recent_files = []
                for file_path in target_path.rglob("*"):
                    if file_path.is_file():
                        recent_files.append(file_path)
                        if len(recent_files) >= 10:
                            break

                if recent_files:
                    findings.append({
                        "operation": "incident_response",
                        "technique": "Timeline Analysis",
                        "severity": "INFO",
                        "description": f"Analyzed {len(recent_files)} recent files",
                        "files": [str(f) for f in recent_files[:5]]
                    })

            # Check for suspicious file names
            if target_path.is_dir():
                for ext in self.KNOWN_IOCS["suspicious_files"]:
                    suspicious = list(target_path.rglob(f"*{ext}"))[:5]
                    if suspicious:
                        findings.append({
                            "operation": "incident_response",
                            "technique": "Suspicious File Discovery",
                            "severity": "HIGH",
                            "threat_detected": True,
                            "description": f"Found suspicious files: {ext}",
                            "files": [str(f) for f in suspicious]
                        })

        findings.append({
            "operation": "incident_response",
            "technique": "IR Procedures",
            "severity": "INFO",
            "description": "Incident response analysis complete",
            "recommendation": "Check: modified files, persistence mechanisms, lateral movement indicators"
        })

        return findings

    async def _log_analysis_operation(self, params: BlueTeamParams) -> List[Dict[str, Any]]:
        """
        Log analysis for anomalies.

        Context: Analyze logs for threats.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        if target_path.exists():
            log_files = []

            if target_path.is_file():
                log_files = [target_path]
            else:
                # Find log files
                for pattern in ["*.log", "*.txt", "*access*", "*error*"]:
                    log_files.extend(list(target_path.rglob(pattern))[:10])

            for log_file in log_files[:5]:
                try:
                    content = log_file.read_text(errors="ignore")
                    lines = content.splitlines()

                    # Check for failed auth attempts
                    failed_auth = sum(1 for line in lines if re.search(r"(failed|denied|unauthorized|403|401)", line, re.IGNORECASE))
                    if failed_auth > 5:
                        findings.append({
                            "operation": "log_analysis",
                            "technique": "Failed Authentication Detection",
                            "severity": "HIGH",
                            "threat_detected": True,
                            "description": f"Multiple failed auth attempts: {failed_auth}",
                            "file": str(log_file)
                        })

                    # Check for errors
                    errors = sum(1 for line in lines if re.search(r"(error|exception|fatal)", line, re.IGNORECASE))
                    if errors > 10:
                        findings.append({
                            "operation": "log_analysis",
                            "technique": "Error Pattern Analysis",
                            "severity": "MEDIUM",
                            "description": f"High error rate detected: {errors} errors",
                            "file": str(log_file)
                        })

                except Exception as e:
                    logger.debug(f"Could not analyze log {log_file}: {e}")

        findings.append({
            "operation": "log_analysis",
            "technique": "Log Review",
            "severity": "INFO",
            "description": f"Analyzed {len(log_files)} log files"
        })

        return findings

    async def _ioc_search_operation(self, params: BlueTeamParams) -> List[Dict[str, Any]]:
        """
        Search for indicators of compromise.

        Context: Hunt for known IOCs.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        if target_path.exists():
            # Search for all IOC types
            for ioc_type, ioc_list in self.KNOWN_IOCS.items():
                for ioc in ioc_list:
                    # Search in files
                    if target_path.is_dir():
                        matches = []
                        for file_path in target_path.rglob("*"):
                            if file_path.is_file() and not self._is_binary(file_path):
                                try:
                                    content = file_path.read_text(errors="ignore")
                                    if ioc.lower() in content.lower():
                                        matches.append(str(file_path))
                                        if len(matches) >= 3:
                                            break
                                except Exception:
                                    pass

                        if matches:
                            findings.append({
                                "operation": "ioc_search",
                                "technique": "IOC Correlation",
                                "severity": "HIGH",
                                "threat_detected": True,
                                "description": f"IOC found: {ioc}",
                                "ioc_type": ioc_type,
                                "ioc": ioc,
                                "matches": matches
                            })

        findings.append({
            "operation": "ioc_search",
            "technique": "IOC Hunting",
            "severity": "INFO",
            "description": f"Searched for {sum(len(v) for v in self.KNOWN_IOCS.values())} known IOCs"
        })

        return findings

    async def _baseline_operation(self, params: BlueTeamParams) -> List[Dict[str, Any]]:
        """
        Establish security baseline.

        Context: Create baseline for monitoring.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        if target_path.exists():
            # Baseline statistics
            stats = {
                "total_files": 0,
                "total_size": 0,
                "file_types": {}
            }

            if target_path.is_dir():
                for file_path in target_path.rglob("*"):
                    if file_path.is_file():
                        stats["total_files"] += 1
                        stats["total_size"] += file_path.stat().st_size
                        ext = file_path.suffix or "no_extension"
                        stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1

            findings.append({
                "operation": "baseline",
                "technique": "Baseline Establishment",
                "severity": "INFO",
                "description": "Security baseline created",
                "baseline": stats,
                "recommendation": "Monitor for deviations from this baseline"
            })

        return findings

    async def _full_defense_operation(self, params: BlueTeamParams) -> List[Dict[str, Any]]:
        """
        Full defensive assessment.

        Context: Comprehensive defensive check.
        """
        findings = []

        # Execute all defensive operations
        findings.extend(await self._threat_hunt_operation(params))
        findings.extend(await self._log_analysis_operation(params))
        findings.extend(await self._ioc_search_operation(params))
        findings.extend(await self._baseline_operation(params))

        return findings

    def _filter_by_severity(self, findings: List[Dict[str, Any]], threshold: str) -> List[Dict[str, Any]]:
        """Filter findings by severity threshold"""
        severity_order = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        threshold_level = severity_order.get(threshold, 2)

        return [
            f for f in findings
            if severity_order.get(f.get("severity", "INFO"), 0) >= threshold_level
        ]

    def _is_binary(self, file_path: Path) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
            return b'\x00' in chunk
        except Exception:
            return False

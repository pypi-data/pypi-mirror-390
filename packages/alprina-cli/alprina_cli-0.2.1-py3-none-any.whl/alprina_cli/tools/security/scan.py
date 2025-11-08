"""
Security Scan Tool

Context Engineering:
- Unified scan tool for local and remote targets
- Returns compressed findings (not verbose logs)
- Configurable scan profiles
- Optional agent enhancement

Based on: scanner.py + security_engine.py (refactored to tool pattern)
"""

from pathlib import Path
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field, field_validator
from loguru import logger

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


# Try to import security agents (optional)
try:
    from alprina_cli.agents.red_teamer import run_red_team_scan
    from alprina_cli.agents.blue_teamer import run_blue_team_scan
    from alprina_cli.agents.network_analyzer import run_network_analyzer_scan
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logger.debug("Security agents not available - using built-in analysis")


class ScanParams(BaseModel):
    """
    Parameters for security scan.

    Context: Clear schema for type safety and validation.
    """
    target: str = Field(
        description="Target to scan (file path, directory, URL, or IP)"
    )
    profile: Literal[
        "code-audit",
        "web-recon",
        "vuln-scan",
        "secret-detection",
        "config-audit",
        "network-analysis",
        "default"
    ] = Field(
        default="default",
        description="Scan profile determines which checks to run"
    )
    safe_only: bool = Field(
        default=True,
        description="Only perform safe, non-intrusive scans"
    )
    max_findings: int = Field(
        default=20,
        description="Maximum findings to return (context efficiency)"
    )

    @field_validator('target')
    @classmethod
    def validate_target(cls, v: str) -> str:
        """Validate target is not empty"""
        if not v or v.strip() == "":
            raise ValueError("Target cannot be empty")
        return v.strip()


class ScanTool(AlprinaToolBase[ScanParams]):
    """
    Unified security scanning tool.

    Context Engineering Benefits:
    - Single tool for local + remote scans
    - Returns compressed findings (not full logs)
    - Configurable max_findings for context control
    - Profile-based scan selection
    - Optional agent enhancement

    Profiles:
    - code-audit: Static code analysis
    - web-recon: Web application reconnaissance
    - vuln-scan: Vulnerability detection
    - secret-detection: Find hardcoded secrets
    - config-audit: Configuration security
    - network-analysis: Network traffic analysis

    Usage:
    ```python
    tool = ScanTool()
    result = await tool.execute(ScanParams(
        target="./src",
        profile="code-audit",
        safe_only=True
    ))
    ```
    """

    name: str = "Scan"
    description: str = """Perform security scans on local or remote targets.

Capabilities:
- Code analysis (SAST)
- Web reconnaissance
- Vulnerability detection
- Secret/credential detection
- Configuration auditing
- Network analysis

Returns: High-level summary with key findings (not full scan logs)"""
    params: type[ScanParams] = ScanParams

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent_mapping = self._build_agent_mapping()

    def _build_agent_mapping(self) -> Dict[str, Any]:
        """
        Build profile to agent mapping.

        Context: Only if agents available (fallback to built-in).
        """
        if not AGENTS_AVAILABLE:
            return {}

        return {
            "code-audit": run_red_team_scan,
            "web-recon": run_network_analyzer_scan,
            "vuln-scan": run_red_team_scan,
            "secret-detection": run_red_team_scan,
            "config-audit": run_blue_team_scan,
            "network-analysis": run_network_analyzer_scan,
            "default": run_red_team_scan
        }

    async def execute(self, params: ScanParams) -> ToolOk | ToolError:
        """
        Execute security scan.

        Context: Returns compressed findings, not verbose logs.
        """
        logger.info(f"Scan: {params.target} (profile={params.profile}, safe={params.safe_only})")

        try:
            # Determine if target is local or remote
            is_local = self._is_local_target(params.target)

            # Execute scan
            if is_local:
                results = await self._scan_local(params)
            else:
                results = await self._scan_remote(params)

            # Limit findings for context efficiency
            if len(results["findings"]) > params.max_findings:
                results["findings"] = results["findings"][:params.max_findings]
                results["summary"]["truncated"] = True
                results["summary"]["total_found"] = len(results["findings"])

            return ToolOk(content=results)

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            return ToolError(
                message=f"Scan failed: {str(e)}",
                brief="Scan failed"
            )

    async def _scan_local(self, params: ScanParams) -> Dict[str, Any]:
        """
        Scan local file or directory.

        Context: For code, config, or file analysis.
        """
        target_path = Path(params.target)

        if not target_path.exists():
            raise FileNotFoundError(f"Target not found: {params.target}")

        # Try agent-enhanced scan first (skip for now due to event loop conflicts)
        # TODO: Refactor old agents to proper async tools
        # if AGENTS_AVAILABLE and params.profile in self._agent_mapping:
        #     agent_func = self._agent_mapping[params.profile]
        #     result = agent_func(str(target_path), params.safe_only)
        #     return {...}

        # Use built-in scan (clean, async, no event loop conflicts)
        return await self._scan_local_builtin(params, target_path)

    async def _scan_remote(self, params: ScanParams) -> Dict[str, Any]:
        """
        Scan remote target (URL, IP, domain).

        Context: For web apps, APIs, network targets.
        """
        # Validate remote target format
        if not self._is_valid_remote_target(params.target):
            raise ValueError(f"Invalid remote target format: {params.target}")

        # Try agent-enhanced scan first (skip for now due to event loop conflicts)
        # TODO: Refactor old agents to proper async tools
        # if AGENTS_AVAILABLE and params.profile in self._agent_mapping:
        #     agent_func = self._agent_mapping[params.profile]
        #     result = agent_func(params.target, params.safe_only)
        #     return {...}

        # Use built-in scan (clean, async, no event loop conflicts)
        return await self._scan_remote_builtin(params)

    async def _scan_local_builtin(
        self,
        params: ScanParams,
        target_path: Path
    ) -> Dict[str, Any]:
        """
        Built-in local scan (fallback).

        Context: Basic analysis when agents unavailable.
        """
        findings = []

        # Check file type and size
        if target_path.is_file():
            findings.extend(self._analyze_file(target_path, params.profile))
        elif target_path.is_dir():
            findings.extend(self._analyze_directory(target_path, params.profile))

        return {
            "target": params.target,
            "scan_type": "local",
            "profile": params.profile,
            "findings": findings,
            "summary": {
                "total_findings": len(findings),
                "powered_by": "built-in",
                "safe_mode": params.safe_only
            }
        }

    async def _scan_remote_builtin(self, params: ScanParams) -> Dict[str, Any]:
        """
        Built-in remote scan (fallback).

        Context: Basic checks when agents unavailable.
        """
        findings = []

        # Basic remote target analysis
        if params.target.startswith(("http://", "https://")):
            findings.append({
                "type": "Web Target",
                "severity": "INFO",
                "title": "HTTP(S) Target Detected",
                "description": f"Target is a web application: {params.target}",
                "location": params.target,
                "confidence": 1.0
            })

            # Check for HTTP (not HTTPS)
            if params.target.startswith("http://"):
                findings.append({
                    "type": "Security Issue",
                    "severity": "MEDIUM",
                    "title": "Unencrypted HTTP Connection",
                    "description": "Target uses HTTP instead of HTTPS. Data may be transmitted insecurely.",
                    "location": params.target,
                    "confidence": 0.9
                })

        return {
            "target": params.target,
            "scan_type": "remote",
            "profile": params.profile,
            "findings": findings,
            "summary": {
                "total_findings": len(findings),
                "powered_by": "built-in",
                "safe_mode": params.safe_only
            }
        }

    def _analyze_file(self, file_path: Path, profile: str) -> List[Dict[str, Any]]:
        """Analyze individual file"""
        findings = []

        # File size check
        file_size = file_path.stat().st_size
        if file_size > 10 * 1024 * 1024:  # 10MB
            findings.append({
                "type": "Large File",
                "severity": "LOW",
                "title": f"Large File Detected: {file_path.name}",
                "description": f"File size: {file_size / (1024*1024):.2f}MB",
                "location": str(file_path),
                "confidence": 1.0
            })

        # Secret detection in code-audit profile
        if profile in ["code-audit", "secret-detection"]:
            secret_patterns = ["password", "api_key", "secret", "token"]
            try:
                content = file_path.read_text(errors="ignore")
                for pattern in secret_patterns:
                    if pattern in content.lower():
                        findings.append({
                            "type": "Potential Secret",
                            "severity": "MEDIUM",
                            "title": f"Potential {pattern} found in {file_path.name}",
                            "description": f"File may contain hardcoded secrets",
                            "location": str(file_path),
                            "confidence": 0.6
                        })
                        break  # Only report once per file
            except Exception:
                pass  # Skip files that can't be read

        return findings

    def _analyze_directory(self, dir_path: Path, profile: str) -> List[Dict[str, Any]]:
        """Analyze directory"""
        findings = []

        # Count files
        files = list(dir_path.rglob("*"))
        file_count = len([f for f in files if f.is_file()])

        findings.append({
            "type": "Directory Scan",
            "severity": "INFO",
            "title": f"Analyzed directory: {dir_path.name}",
            "description": f"Found {file_count} files to analyze",
            "location": str(dir_path),
            "confidence": 1.0
        })

        # Analyze subset of files (limit for context)
        analyzed = 0
        for file_path in files:
            if file_path.is_file() and analyzed < 10:  # Limit to 10 files
                findings.extend(self._analyze_file(file_path, profile))
                analyzed += 1

        return findings

    def _is_local_target(self, target: str) -> bool:
        """Check if target is local path"""
        return Path(target).exists()

    def _is_valid_remote_target(self, target: str) -> bool:
        """Check if target is valid remote target"""
        # URL
        if target.startswith(("http://", "https://")):
            return True

        # IP address
        parts = target.split(".")
        if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            return True

        # Domain name (simple check)
        if "." in target and not target.startswith("/"):
            return True

        return False

"""
Vulnerability Scanning Tool

Context Engineering:
- Identify security vulnerabilities in targets
- Returns structured vulnerability findings
- Configurable depth (quick, standard, deep)
- Token-efficient output with severity ranking

Find vulnerabilities, not false positives.
"""

from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from loguru import logger
from pathlib import Path
import re

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


class VulnScanParams(BaseModel):
    """
    Parameters for vulnerability scanning.

    Context: Focused schema for vulnerability detection.
    """
    target: str = Field(
        description="Target to scan (file, directory, URL, or IP)"
    )
    depth: Literal["quick", "standard", "deep"] = Field(
        default="standard",
        description="Scan depth: quick (common vulns), standard (balanced), deep (comprehensive)"
    )
    categories: List[str] = Field(
        default_factory=lambda: ["all"],
        description="Vulnerability categories: all, injection, crypto, config, code, deps"
    )
    max_findings: int = Field(
        default=50,
        description="Maximum vulnerability findings to return"
    )


class VulnScanTool(AlprinaToolBase[VulnScanParams]):
    """
    Vulnerability scanning tool.

    Context Engineering Benefits:
    - Returns ranked findings (HIGH → LOW)
    - Configurable depth for token control
    - Category filtering for focused scans
    - Max findings limit for context efficiency

    Scan Depths:
    - quick: Common vulnerabilities (fast, ~10s)
    - standard: Balanced scan (medium, ~30s)
    - deep: Comprehensive scan (slow, 60s+)

    Categories:
    - injection: SQL, XSS, command injection
    - crypto: Weak crypto, exposed secrets
    - config: Misconfigurations, insecure defaults
    - code: Code quality issues, logic flaws
    - deps: Dependency vulnerabilities

    Usage:
    ```python
    tool = VulnScanTool()
    result = await tool.execute(VulnScanParams(
        target="./src",
        depth="standard",
        categories=["injection", "crypto"]
    ))
    ```
    """

    name: str = "VulnScan"
    description: str = """Vulnerability scanning for security issues.

Capabilities:
- Injection vulnerabilities (SQL, XSS, Command)
- Cryptographic weaknesses
- Configuration issues
- Code quality problems
- Dependency vulnerabilities

Returns: Ranked vulnerability findings (HIGH → LOW)"""
    params: type[VulnScanParams] = VulnScanParams

    async def execute(self, params: VulnScanParams) -> ToolOk | ToolError:
        """
        Execute vulnerability scan.

        Context: Returns limited, ranked findings.
        """
        logger.info(f"VulnScan: {params.target} (depth={params.depth})")

        try:
            # Determine target type
            target_path = Path(params.target).expanduser()
            is_local = target_path.exists()

            if is_local:
                findings = await self._scan_local(params, target_path)
            else:
                findings = await self._scan_remote(params)

            # Filter by categories
            if "all" not in params.categories:
                findings = [
                    f for f in findings
                    if f.get("category") in params.categories
                ]

            # Sort by severity (HIGH → CRITICAL → MEDIUM → LOW → INFO)
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
            findings.sort(key=lambda f: severity_order.get(f.get("severity", "INFO"), 4))

            # Limit findings
            if len(findings) > params.max_findings:
                findings = findings[:params.max_findings]
                truncated = True
            else:
                truncated = False

            # Calculate summary stats
            severity_counts = {}
            for finding in findings:
                sev = finding.get("severity", "INFO")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

            # Prepare result
            result_content = {
                "target": params.target,
                "depth": params.depth,
                "findings": findings,
                "summary": {
                    "total_findings": len(findings),
                    "truncated": truncated,
                    "by_severity": severity_counts,
                    "target_type": "local" if is_local else "remote"
                }
            }

            # Store in memory if available
            if self.memory_service and self.memory_service.is_enabled():
                self.memory_service.add_scan_results(
                    tool_name="VulnScan",
                    target=params.target,
                    results=result_content
                )

            return ToolOk(content=result_content)

        except Exception as e:
            logger.error(f"VulnScan failed: {e}")
            return ToolError(
                message=f"Vulnerability scan failed: {str(e)}",
                brief="VulnScan failed"
            )

    async def _scan_local(
        self,
        params: VulnScanParams,
        target_path: Path
    ) -> List[Dict[str, Any]]:
        """
        Scan local file or directory.

        Context: Returns structured vulnerability findings.
        """
        findings = []

        if target_path.is_file():
            findings.extend(self._scan_file(target_path, params.depth))
        else:
            # Scan directory
            files = list(target_path.rglob("*"))
            for file_path in files:
                if file_path.is_file():
                    findings.extend(self._scan_file(file_path, params.depth))

                    # For quick scan, limit files checked
                    if params.depth == "quick" and len(findings) >= 20:
                        break

        return findings

    def _scan_file(self, file_path: Path, depth: str) -> List[Dict[str, Any]]:
        """Scan individual file for vulnerabilities"""
        findings = []

        try:
            # Skip binary files
            if self._is_binary(file_path):
                return findings

            content = file_path.read_text(errors="ignore")
            lines = content.splitlines()

            # Check for secrets/credentials
            findings.extend(self._check_secrets(file_path, content, lines))

            # Check for injection vulnerabilities
            if depth in ["standard", "deep"]:
                findings.extend(self._check_injection(file_path, content, lines))

            # Check for crypto issues
            if depth in ["standard", "deep"]:
                findings.extend(self._check_crypto(file_path, content, lines))

            # Check for config issues
            findings.extend(self._check_config(file_path, content, lines))

            # Deep scan: additional checks
            if depth == "deep":
                findings.extend(self._check_code_quality(file_path, content, lines))

        except Exception as e:
            logger.warning(f"Could not scan {file_path}: {e}")

        return findings

    def _check_secrets(
        self,
        file_path: Path,
        content: str,
        lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for exposed secrets"""
        findings = []

        # Common secret patterns
        secret_patterns = {
            r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{3,}['\"]": ("Password in plaintext", "HIGH"),
            r"(?i)(api[_-]?key|apikey)\s*=\s*['\"][^'\"]{10,}['\"]": ("API key exposed", "CRITICAL"),
            r"(?i)(secret[_-]?key|secretkey)\s*=\s*['\"][^'\"]{10,}['\"]": ("Secret key exposed", "CRITICAL"),
            r"(?i)(private[_-]?key|privatekey)\s*=\s*['\"][^'\"]{20,}['\"]": ("Private key exposed", "CRITICAL"),
            r"(?i)(token)\s*=\s*['\"][^'\"]{10,}['\"]": ("Auth token exposed", "HIGH"),
            r"-----BEGIN (RSA |EC )?PRIVATE KEY-----": ("Private key in file", "CRITICAL"),
        }

        for pattern, (title, severity) in secret_patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                findings.append({
                    "category": "crypto",
                    "severity": severity,
                    "title": title,
                    "description": f"Found at line {line_num} in {file_path.name}",
                    "file": str(file_path),
                    "line_number": line_num,
                    "confidence": 0.9
                })

        return findings

    def _check_injection(
        self,
        file_path: Path,
        content: str,
        lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for injection vulnerabilities"""
        findings = []

        # SQL injection patterns
        sql_patterns = [
            r"execute\([^)]*\+[^)]*\)",  # String concatenation in SQL
            r'SELECT.*"\s*\+\s*',  # SQL with concatenation
            r"=\s*['\"]SELECT.*['\"].*\+",  # SQL query with concatenation
            r"\.format\(.*SELECT",  # format() with SQL
        ]

        # Command injection patterns
        cmd_patterns = [
            r"os\.system\([^)]*\+[^)]*\)",  # os.system with concatenation
            r"subprocess\.call\([^)]*\+[^)]*\)",  # subprocess with concatenation
            r"eval\(",  # eval() usage
            r"exec\(",  # exec() usage
        ]

        for line_num, line in enumerate(lines, 1):
            # Check SQL injection
            for pattern in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "category": "injection",
                        "severity": "HIGH",
                        "title": "Potential SQL injection",
                        "description": f"Line {line_num}: {line.strip()[:80]}",
                        "file": str(file_path),
                        "line_number": line_num,
                        "confidence": 0.7
                    })

            # Check command injection
            for pattern in cmd_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "category": "injection",
                        "severity": "HIGH",
                        "title": "Potential command injection",
                        "description": f"Line {line_num}: {line.strip()[:80]}",
                        "file": str(file_path),
                        "line_number": line_num,
                        "confidence": 0.8
                    })

        return findings

    def _check_crypto(
        self,
        file_path: Path,
        content: str,
        lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for cryptographic issues"""
        findings = []

        # Weak crypto patterns
        weak_patterns = {
            r"hashlib\.md5": ("MD5 usage (weak)", "MEDIUM"),
            r"hashlib\.sha1": ("SHA1 usage (weak)", "MEDIUM"),
            r"DES\.new": ("DES encryption (weak)", "HIGH"),
            r"random\.random": ("Insecure random (use secrets module)", "MEDIUM"),
        }

        for line_num, line in enumerate(lines, 1):
            for pattern, (title, severity) in weak_patterns.items():
                if re.search(pattern, line):
                    findings.append({
                        "category": "crypto",
                        "severity": severity,
                        "title": title,
                        "description": f"Line {line_num} in {file_path.name}",
                        "file": str(file_path),
                        "line_number": line_num,
                        "confidence": 0.9
                    })

        return findings

    def _check_config(
        self,
        file_path: Path,
        content: str,
        lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for configuration issues"""
        findings = []

        # Check for debug mode enabled
        if re.search(r"(?i)debug\s*=\s*(True|1|\"true\")", content):
            findings.append({
                "category": "config",
                "severity": "MEDIUM",
                "title": "Debug mode enabled",
                "description": f"Debug mode found in {file_path.name}",
                "file": str(file_path),
                "confidence": 0.8
            })

        # Check for insecure defaults
        if ".env" in file_path.name and file_path.stat().st_size > 0:
            findings.append({
                "category": "config",
                "severity": "HIGH",
                "title": "Environment file with contents",
                "description": ".env file may contain secrets",
                "file": str(file_path),
                "confidence": 0.7
            })

        return findings

    def _check_code_quality(
        self,
        file_path: Path,
        content: str,
        lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Check for code quality issues (deep scan only)"""
        findings = []

        # Check for TODO/FIXME/HACK comments
        for line_num, line in enumerate(lines, 1):
            if re.search(r"(?i)(TODO|FIXME|HACK|XXX)", line):
                findings.append({
                    "category": "code",
                    "severity": "INFO",
                    "title": "Code comment requires attention",
                    "description": f"Line {line_num}: {line.strip()[:80]}",
                    "file": str(file_path),
                    "line_number": line_num,
                    "confidence": 1.0
                })

        return findings

    async def _scan_remote(self, params: VulnScanParams) -> List[Dict[str, Any]]:
        """
        Scan remote target (URL or IP).

        Context: Basic remote vulnerability checks.
        """
        findings = []
        target = params.target

        # Check for HTTP
        if target.startswith("http://"):
            findings.append({
                "category": "config",
                "severity": "MEDIUM",
                "title": "Insecure HTTP protocol",
                "description": "Target uses HTTP instead of HTTPS",
                "confidence": 1.0
            })

        # Placeholder for future remote scanning
        # (would integrate with tools like nmap, nikto, etc.)
        findings.append({
            "category": "info",
            "severity": "INFO",
            "title": "Remote scanning not fully implemented",
            "description": "Use local file/directory scanning for comprehensive results",
            "confidence": 1.0
        })

        return findings

    def _is_binary(self, file_path: Path) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
            return b'\x00' in chunk
        except Exception:
            return False

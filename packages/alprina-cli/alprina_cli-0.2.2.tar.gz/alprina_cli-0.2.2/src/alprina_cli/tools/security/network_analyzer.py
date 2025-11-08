"""
Network Analyzer Tool

Context Engineering:
- Lightweight tool (not full agent)
- Returns high-signal summaries (not verbose logs)
- Async by default for composability
- CAI integration as optional enhancement

Based on: agents/network_analyzer.py (refactored to tool pattern)
"""

import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from loguru import logger

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


# Try to import CAI (optional enhancement)
try:
    from alprina.agents import get_agent_by_name
    CAI_AVAILABLE = True
except ImportError:
    CAI_AVAILABLE = False
    logger.debug("CAI not available - using built-in network analysis")


class NetworkAnalyzerParams(BaseModel):
    """
    Parameters for network analysis.

    Context: Clear, minimal schema for type safety.
    """
    target: str = Field(
        description="Target to analyze (IP, domain, or pcap file path)"
    )
    safe_only: bool = Field(
        default=True,
        description="Only perform safe, non-intrusive analysis"
    )
    max_findings: int = Field(
        default=10,
        description="Maximum number of findings to return (context efficiency)"
    )


class NetworkAnalyzerTool(AlprinaToolBase[NetworkAnalyzerParams]):
    """
    Network traffic and packet analysis tool.

    Context Engineering Benefits:
    - Returns compressed summaries (not full packet dumps)
    - Configurable max_findings for context control
    - Async for composability with other tools
    - Optional CAI enhancement (not required)

    Usage:
    ```python
    tool = NetworkAnalyzerTool()
    result = await tool.execute(NetworkAnalyzerParams(
        target="192.168.1.1",
        safe_only=True
    ))
    ```
    """

    name: str = "NetworkAnalyzer"
    description: str = """Analyze network traffic patterns, protocols, and connections.

Capabilities:
- Network traffic pattern analysis
- Protocol inspection (TCP/UDP/ICMP)
- Suspicious connection detection
- Port scan detection
- Network vulnerability identification

Returns: High-level summary with key findings (not raw packet data)"""
    params: type[NetworkAnalyzerParams] = NetworkAnalyzerParams

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._alprina_agent = None

    def _get_alprina_agent(self):
        """
        Get Alprina agent if available.

        Context: Optional enhancement - tool works without CAI.
        """
        if not CAI_AVAILABLE:
            return None

        if self._alprina_agent is None:
            try:
                self._alprina_agent = get_agent_by_name("network_traffic_analyzer")
                logger.debug("CAI network analyzer initialized")
            except Exception as e:
                logger.debug(f"Alprina agent unavailable: {e}")
                return None

        return self._alprina_agent

    async def execute(self, params: NetworkAnalyzerParams) -> ToolOk | ToolError:
        """
        Execute network analysis.

        Context: Returns compressed findings, not verbose logs.
        """
        logger.info(f"NetworkAnalyzer: {params.target} (safe_only={params.safe_only})")

        try:
            # Try CAI-enhanced analysis first
            alprina_agent = self._get_alprina_agent()
            if alprina_agent:
                result = await self._analyze_with_cai(params, alprina_agent)
            else:
                result = await self._analyze_builtin(params)

            # Limit findings for context efficiency
            if len(result["findings"]) > params.max_findings:
                result["findings"] = result["findings"][:params.max_findings]
                result["summary"]["truncated"] = True
                result["summary"]["total_found"] = len(result["findings"])

            return ToolOk(content=result)

        except Exception as e:
            logger.error(f"Network analysis failed: {e}")
            return ToolError(
                message=f"Network analysis failed: {str(e)}",
                brief="Analysis failed"
            )

    async def _analyze_with_cai(
        self,
        params: NetworkAnalyzerParams,
        alprina_agent
    ) -> Dict[str, Any]:
        """
        CAI-enhanced network analysis.

        Context: Leverages CAI expertise when available.
        """
        prompt = f"""Perform network traffic analysis on: {params.target}

Focus areas:
- Traffic patterns and anomalies
- Protocol analysis (TCP/UDP/ICMP)
- Suspicious connections or behaviors
- Network vulnerabilities
- Port scanning activity

Provide concise findings with severity levels."""

        messages = [{"role": "user", "content": prompt}]
        result = await alprina_agent.run(messages)

        findings = self._parse_cai_response(result.value, params.target)

        return {
            "target": params.target,
            "findings": findings,
            "summary": {
                "total_findings": len(findings),
                "powered_by": "CAI",
                "safe_mode": params.safe_only
            }
        }

    async def _analyze_builtin(
        self,
        params: NetworkAnalyzerParams
    ) -> Dict[str, Any]:
        """
        Built-in network analysis (fallback).

        Context: Basic analysis when CAI unavailable.
        Works for common cases without external dependencies.
        """
        findings = []

        # Built-in heuristics for network analysis
        target = params.target

        # Check if target looks like IP address
        if self._is_ip_address(target):
            findings.append({
                "type": "Network Configuration",
                "severity": "INFO",
                "title": "IP Address Target",
                "description": f"Analyzing IP address: {target}",
                "confidence": 1.0
            })

        # Check for common ports in target (if URL)
        if ":" in target:
            port = target.split(":")[-1]
            if port.isdigit():
                port_num = int(port)
                if port_num in [22, 23, 3389]:  # SSH, Telnet, RDP
                    findings.append({
                        "type": "Sensitive Port",
                        "severity": "MEDIUM",
                        "title": f"Management Port Open: {port_num}",
                        "description": f"Port {port_num} is typically used for remote management",
                        "confidence": 0.8
                    })

        # If no specific findings, return general assessment
        if not findings:
            findings.append({
                "type": "Analysis Complete",
                "severity": "INFO",
                "title": "Network Analysis Complete",
                "description": f"Basic analysis of {target} complete. Enable CAI for deep inspection.",
                "confidence": 0.7
            })

        return {
            "target": params.target,
            "findings": findings,
            "summary": {
                "total_findings": len(findings),
                "powered_by": "built-in",
                "safe_mode": params.safe_only
            }
        }

    def _parse_cai_response(
        self,
        response: str,
        target: str
    ) -> List[Dict[str, Any]]:
        """
        Parse CAI response into structured findings.

        Context: Extracts high-signal information, discards noise.
        """
        findings = []

        # Patterns for severity levels
        patterns = [
            ("CRITICAL", r"(?i)(critical|severe|urgent).*?(?=\n\n|\Z)"),
            ("HIGH", r"(?i)high.*?(?=\n\n|\Z)"),
            ("MEDIUM", r"(?i)(medium|moderate).*?(?=\n\n|\Z)"),
            ("LOW", r"(?i)(low|minor|info).*?(?=\n\n|\Z)")
        ]

        for severity, pattern in patterns:
            matches = re.finditer(pattern, response, re.DOTALL)
            for match in matches:
                finding_text = match.group(0).strip()
                lines = finding_text.split('\n')
                title = lines[0] if lines else "Network Finding"

                findings.append({
                    "type": "Network Issue",
                    "severity": severity,
                    "title": title[:100],  # Truncate for context
                    "description": finding_text[:300],  # Limit description
                    "confidence": 0.85
                })

        # If no structured findings, create summary
        if not findings and len(response) > 50:
            findings.append({
                "type": "Analysis Summary",
                "severity": "INFO",
                "title": "Network Analysis Complete",
                "description": response[:400],  # Compressed summary
                "confidence": 0.9
            })

        return findings

    def _is_ip_address(self, target: str) -> bool:
        """Check if target looks like IP address"""
        parts = target.split(".")
        if len(parts) == 4:
            return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
        return False

"""
Alprina Reverse Engineering Agent

Binary analysis and reverse engineering
Integrated from Alprina framework for use in Alprina platform.
"""

import asyncio
from typing import Dict, Any, List
from loguru import logger


# Import actual CAI Reverse Engineering Agent
try:
    from alprina.agents import get_agent_by_name
    CAI_AVAILABLE = True
    logger.info("CAI Reverse Engineering Agent available")
except ImportError as e:
    CAI_AVAILABLE = False
    logger.warning(f"Alprina agents not available: {e}")


class ReverseEngineerWrapper:
    """
    Wrapper for CAI Reverse Engineering Agent.

    Provides synchronous interface to the async Alprina agent.
    """

    def __init__(self):
        self.name = "Reverse Engineering Agent"
        self.agent_type = "binary-analysis"
        self.description = "Binary analysis and reverse engineering"
        self._alprina_agent = None

    def _get_alprina_agent(self):
        """Get or create Alprina agent instance."""
        if not CAI_AVAILABLE:
            return None

        if self._alprina_agent is None:
            try:
                # Get the real Alprina agent
                self._alprina_agent = get_agent_by_name("reverse_engineering_agent")
                logger.info("CAI Reverse Engineering Agent initialized")
            except Exception as e:
                logger.error(f"Failed to initialize CAI Reverse Engineering Agent: {e}")
                return None

        return self._alprina_agent

    async def _scan_async(self, target: str, safe_only: bool = True) -> Dict[str, Any]:
        """
        Async scan using real Alprina agent.

        Args:
            target: Target system, application, or path
            safe_only: If True, only perform safe, non-destructive tests

        Returns:
            Dictionary with scan results
        """
        alprina_agent = self._get_alprina_agent()

        if alprina_agent is None:
            # Fallback to mock implementation
            return self._mock_scan(target, safe_only)

        try:
            # Build prompt for Alprina agent
            prompt = f"""Perform binary-analysis analysis on: {target}

Focus on:
- Binary reverse engineering
- Malware analysis
- Code decompilation
- Security bypasses

Provide detailed findings with severity levels."""

            # Create message for Alprina agent
            messages = [
                {"role": "user", "content": prompt}
            ]

            # Run Alprina agent (async)
            result = await alprina_agent.run(messages)

            # Parse Alprina agent response into findings
            findings = self._parse_cai_response(result.value, target)

            return {
                "agent": self.name,
                "type": self.agent_type,
                "target": target,
                "findings": findings,
                "summary": {
                    "total_findings": len(findings),
                    "alprina_powered": True
                }
            }

        except Exception as e:
            logger.error(f"CAI Reverse Engineering Agent error: {e}")
            # Fallback to mock
            return self._mock_scan(target, safe_only)

    def _mock_scan(self, target: str, safe_only: bool = True) -> Dict[str, Any]:
        """Mock scan implementation (fallback when CAI not available)."""
        findings = []
        findings.append({
            "type": "Security Finding",
            "severity": "INFO",
            "title": "Mock scan result",
            "description": "This is a mock implementation. Enable CAI for real analysis.",
            "file": target,
            "line": 0,
            "confidence": 0.5
        })

        return {
            "agent": self.name,
            "type": self.agent_type,
            "target": target,
            "findings": findings,
            "summary": {
                "total_findings": len(findings),
                "alprina_powered": False
            }
        }

    def _parse_cai_response(self, response: str, target: str) -> List[Dict[str, Any]]:
        """
        Parse Alprina agent response into structured findings.

        Args:
            response: Alprina agent response text
            target: Target that was scanned

        Returns:
            List of finding dictionaries
        """
        findings = []
        import re

        # Parse response text for findings
        high_pattern = r"(?i)(critical|high|severe).*?(?=\n\n|\Z)"
        medium_pattern = r"(?i)(medium|moderate).*?(?=\n\n|\Z)"
        low_pattern = r"(?i)(low|minor|info).*?(?=\n\n|\Z)"

        for severity, pattern in [("HIGH", high_pattern), ("MEDIUM", medium_pattern), ("LOW", low_pattern)]:
            matches = re.finditer(pattern, response, re.DOTALL)
            for match in matches:
                finding_text = match.group(0)
                lines = finding_text.strip().split('\n')
                title = lines[0] if lines else "Security Finding"

                finding = {
                    "type": "Binary Analysis",
                    "severity": severity,
                    "title": title[:100],
                    "description": finding_text[:500],
                    "file": target,
                    "line": 0,
                    "confidence": 0.8
                }
                findings.append(finding)

        # If no findings parsed, create a summary finding
        if not findings and len(response) > 50:
            findings.append({
                "type": "Binary Analysis",
                "severity": "INFO",
                "title": "Reverse Engineering Agent Analysis Complete",
                "description": response[:500],
                "file": target,
                "line": 0,
                "confidence": 1.0
            })

        return findings

    def scan(self, target: str, safe_only: bool = True) -> Dict[str, Any]:
        """
        Perform security scan (synchronous wrapper).

        Args:
            target: Target system, application, or path
            safe_only: If True, only perform safe, non-destructive tests

        Returns:
            Dictionary with scan results
        """
        logger.info(f"Reverse Engineering Agent scanning: {target} (safe_only={safe_only}, CAI={CAI_AVAILABLE})")

        # Run async scan in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._scan_async(target, safe_only))


# Create singleton instance
reverse_engineer_agent = ReverseEngineerWrapper()


def run_reverse_engineer_scan(target: str, safe_only: bool = True) -> Dict[str, Any]:
    """
    Run security scan.

    Args:
        target: Target to scan
        safe_only: Only perform safe tests

    Returns:
        Scan results
    """
    return reverse_engineer_agent.scan(target, safe_only)

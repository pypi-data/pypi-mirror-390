"""
Alprina Replay Attack Agent

Replay attack detection and prevention
Integrated from Alprina framework for use in Alprina platform.
"""

import asyncio
from typing import Dict, Any, List
from loguru import logger


# Import actual CAI Replay Attack Agent
try:
    from alprina.agents import get_agent_by_name
    CAI_AVAILABLE = True
    logger.info("CAI Replay Attack Agent available")
except ImportError as e:
    CAI_AVAILABLE = False
    logger.warning(f"Alprina agents not available: {e}")


class ReplayAttackWrapper:
    """
    Wrapper for CAI Replay Attack Agent.

    Provides synchronous interface to the async Alprina agent.
    """

    def __init__(self):
        self.name = "Replay Attack Agent"
        self.agent_type = "replay-check"
        self.description = "Replay attack detection and prevention"
        self._alprina_agent = None

    def _get_alprina_agent(self):
        """Get or create Alprina agent instance."""
        if not CAI_AVAILABLE:
            return None

        if self._alprina_agent is None:
            try:
                # Get the real Alprina agent
                self._alprina_agent = get_agent_by_name("replay_attack_agent")
                logger.info("CAI Replay Attack Agent initialized")
            except Exception as e:
                logger.error(f"Failed to initialize CAI Replay Attack Agent: {e}")
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
            prompt = f"""Perform replay-check analysis on: {target}

Focus on:
- Replay attack vectors
- Session token reuse
- Authentication bypass
- Timing vulnerabilities

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
            logger.error(f"CAI Replay Attack Agent error: {e}")
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
                    "type": "Replay Vulnerability",
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
                "type": "Replay Vulnerability",
                "severity": "INFO",
                "title": "Replay Attack Agent Analysis Complete",
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
        logger.info(f"Replay Attack Agent scanning: {target} (safe_only={safe_only}, CAI={CAI_AVAILABLE})")

        # Run async scan in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._scan_async(target, safe_only))


# Create singleton instance
replay_attack_agent = ReplayAttackWrapper()


def run_replay_attack_scan(target: str, safe_only: bool = True) -> Dict[str, Any]:
    """
    Run security scan.

    Args:
        target: Target to scan
        safe_only: Only perform safe tests

    Returns:
        Scan results
    """
    return replay_attack_agent.scan(target, safe_only)

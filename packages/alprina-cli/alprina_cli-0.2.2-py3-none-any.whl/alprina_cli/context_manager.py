"""
Conversation context management for chat interface.
Maintains scan results, findings, and conversation history.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
from loguru import logger


class ConversationContext:
    """Manages conversation context and scan results."""

    def __init__(self, max_history: int = 50):
        """
        Initialize conversation context.

        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.messages: List[Dict[str, str]] = []
        self.scan_results: Dict[str, Any] = {}
        self.current_findings: List[Dict] = []
        self.max_history = max_history
        self.session_start = datetime.now()

    def add_user_message(self, content: str):
        """Add user message to context."""
        self.messages.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()
        logger.debug(f"Added user message: {content[:50]}...")

    def add_assistant_message(self, content: str):
        """Add assistant response to context."""
        self.messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()
        logger.debug(f"Added assistant message: {content[:50]}...")

    def add_system_message(self, content: str):
        """Add system message (scan results, etc.)."""
        self.messages.append({
            "role": "system",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()

    def _trim_history(self):
        """Trim message history to max_history."""
        if len(self.messages) > self.max_history:
            # Keep system messages and recent messages
            system_messages = [m for m in self.messages if m["role"] == "system"]
            recent_messages = [m for m in self.messages if m["role"] != "system"][-self.max_history:]
            self.messages = system_messages + recent_messages
            logger.debug(f"Trimmed history to {len(self.messages)} messages")

    def load_scan_results(self, file_path: Path):
        """
        Load scan results from file.

        Args:
            file_path: Path to scan results JSON file
        """
        try:
            with open(file_path) as f:
                self.scan_results = json.load(f)
                self.current_findings = self.scan_results.get("findings", [])

                # Add system message about loaded results
                summary = self.get_context_summary()
                self.add_system_message(f"Loaded scan results: {summary}")

                logger.info(f"Loaded {len(self.current_findings)} findings from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load scan results: {e}")
            raise

    def load_scan_results_dict(self, results: Dict[str, Any]):
        """
        Load scan results from dictionary.

        Args:
            results: Scan results dictionary
        """
        self.scan_results = results
        self.current_findings = results.get("findings", [])

        # Add system message about results
        summary = self.get_context_summary()
        self.add_system_message(f"Scan completed: {summary}")

        logger.info(f"Loaded {len(self.current_findings)} findings from scan")

    def get_finding(self, finding_id: str) -> Optional[Dict]:
        """
        Get specific finding by ID.

        Args:
            finding_id: Finding identifier

        Returns:
            Finding dictionary or None if not found
        """
        for finding in self.current_findings:
            if finding.get("id") == finding_id:
                return finding
        return None

    def get_findings_by_severity(self, severity: str) -> List[Dict]:
        """
        Get findings filtered by severity.

        Args:
            severity: Severity level (HIGH, MEDIUM, LOW)

        Returns:
            List of findings matching severity
        """
        return [f for f in self.current_findings if f.get("severity") == severity.upper()]

    def get_messages(self, include_system: bool = True) -> List[Dict]:
        """
        Get conversation messages.

        Args:
            include_system: Whether to include system messages

        Returns:
            List of message dictionaries
        """
        if include_system:
            return self.messages
        return [m for m in self.messages if m["role"] != "system"]

    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """
        Get messages formatted for LLM API (without timestamps).

        Returns:
            List of message dictionaries with role and content only
        """
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.messages
        ]

    def get_context_summary(self) -> str:
        """
        Get summary of current scan context.

        Returns:
            Human-readable summary string
        """
        if not self.scan_results:
            return "No active scan context"

        target = self.scan_results.get('target', 'Unknown')
        total = len(self.current_findings)
        high = sum(1 for f in self.current_findings if f.get('severity') == 'HIGH')
        medium = sum(1 for f in self.current_findings if f.get('severity') == 'MEDIUM')
        low = sum(1 for f in self.current_findings if f.get('severity') == 'LOW')

        summary = f"{total} findings (HIGH: {high}, MEDIUM: {medium}, LOW: {low}) in {target}"
        return summary

    def get_detailed_context(self) -> str:
        """
        Get detailed context for system prompt.

        Returns:
            Detailed context string with findings
        """
        if not self.scan_results:
            return "No scan context available."

        context = f"""
Current Scan Context:
=====================
Target: {self.scan_results.get('target', 'Unknown')}
Scan ID: {self.scan_results.get('scan_id', 'Unknown')}
Profile: {self.scan_results.get('profile', 'default')}
Timestamp: {self.scan_results.get('timestamp', 'Unknown')}

Findings Summary:
-----------------
Total Findings: {len(self.current_findings)}
"""

        # Add severity breakdown
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            findings = self.get_findings_by_severity(severity)
            if findings:
                context += f"\n{severity} Severity ({len(findings)}):\n"
                for f in findings[:3]:  # Show first 3 of each severity
                    context += f"  - {f.get('id')}: {f.get('title')} ({f.get('file', 'N/A')})\n"
                if len(findings) > 3:
                    context += f"  ... and {len(findings) - 3} more\n"

        return context

    def clear(self):
        """Clear conversation history (keeps scan results)."""
        self.messages = []
        logger.info("Cleared conversation history")

    def clear_all(self):
        """Clear everything including scan results."""
        self.messages = []
        self.scan_results = {}
        self.current_findings = []
        logger.info("Cleared all context")

    def save_conversation(self, file_path: Path):
        """
        Save conversation to file.

        Args:
            file_path: Path to save conversation
        """
        conversation_data = {
            "session_start": self.session_start.isoformat(),
            "messages": self.messages,
            "scan_summary": self.get_context_summary(),
            "total_messages": len(self.messages)
        }

        with open(file_path, 'w') as f:
            json.dump(conversation_data, f, indent=2)

        logger.info(f"Saved conversation to {file_path}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get conversation statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_messages": len(self.messages),
            "user_messages": sum(1 for m in self.messages if m["role"] == "user"),
            "assistant_messages": sum(1 for m in self.messages if m["role"] == "assistant"),
            "system_messages": sum(1 for m in self.messages if m["role"] == "system"),
            "total_findings": len(self.current_findings),
            "high_severity": len(self.get_findings_by_severity("HIGH")),
            "medium_severity": len(self.get_findings_by_severity("MEDIUM")),
            "low_severity": len(self.get_findings_by_severity("LOW")),
            "session_duration": (datetime.now() - self.session_start).total_seconds()
        }

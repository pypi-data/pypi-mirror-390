"""
Alprina Agent Coordinator - Intelligent agent chaining and vulnerability lifecycle management.

Coordinates multiple security agents to work together in sophisticated workflows:
- Red Team → Blue Team → DFIR chains
- Vulnerability discovery → Validation → Remediation tracking
- Automated follow-up scans
- Agent-to-agent communication

Reference: AI SDK Agent Coordination Patterns
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from loguru import logger
from datetime import datetime, timedelta
import asyncio


class ChainType(Enum):
    """Types of agent coordination chains."""
    ATTACK_DEFENSE = "attack_defense"          # Red Team → Blue Team
    INVESTIGATION = "investigation"            # Discovery → DFIR → Analysis
    FULL_LIFECYCLE = "full_lifecycle"          # Red Team → Blue Team → DFIR → Remediation
    VALIDATION = "validation"                  # Scan → Retest → Verify
    CONTINUOUS = "continuous"                  # Ongoing monitoring and response


class VulnerabilityState(Enum):
    """Vulnerability lifecycle states."""
    DISCOVERED = "discovered"                  # Initial discovery
    VALIDATED = "validated"                    # Confirmed by retesting
    TRIAGED = "triaged"                       # Prioritized and assigned
    IN_REMEDIATION = "in_remediation"         # Being fixed
    FIXED = "fixed"                           # Fix applied
    VERIFIED = "verified"                     # Fix verified by retest
    FALSE_POSITIVE = "false_positive"         # Marked as false positive
    ACCEPTED_RISK = "accepted_risk"           # Risk accepted by stakeholders


class AgentCoordinator:
    """
    Coordinates multiple security agents for sophisticated workflows.

    Capabilities:
    - Agent chaining (A → B → C)
    - Vulnerability lifecycle tracking
    - Automated follow-up scans
    - Agent-to-agent communication
    - Intelligent chain selection
    """

    def __init__(self):
        """Initialize agent coordinator."""
        self.vulnerability_registry: Dict[str, Dict[str, Any]] = {}
        self.chain_history: List[Dict[str, Any]] = []
        logger.info("Agent Coordinator initialized")

    async def execute_chain(
        self,
        chain_type: ChainType,
        target: str,
        initial_findings: Optional[Dict[str, Any]] = None,
        safe_only: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a coordinated agent chain.

        Args:
            chain_type: Type of coordination chain to execute
            target: Target to scan
            initial_findings: Optional initial findings to start with
            safe_only: Only run safe checks

        Returns:
            Aggregated results from all agents in chain
        """
        logger.info(f"Executing {chain_type.value} chain on {target}")

        chain_def = self._get_chain_definition(chain_type)

        if not chain_def:
            logger.error(f"Unknown chain type: {chain_type}")
            return {"error": f"Unknown chain type: {chain_type}"}

        # Execute chain
        results = {
            "chain_type": chain_type.value,
            "target": target,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "vulnerabilities": []
        }

        context = initial_findings or {}

        for step in chain_def["steps"]:
            try:
                logger.info(f"Chain step: {step['name']} using {step['agent']}")

                # Execute agent with context from previous steps
                step_result = await self._execute_agent_step(
                    agent=step["agent"],
                    task=step["task"],
                    target=target,
                    context=context,
                    safe_only=safe_only
                )

                # Record step
                results["steps"].append({
                    "name": step["name"],
                    "agent": step["agent"],
                    "timestamp": datetime.now().isoformat(),
                    "findings_count": len(step_result.get("findings", [])),
                    "output": step_result
                })

                # Update context for next step
                context = self._merge_context(context, step_result)

                # Track vulnerabilities
                if step_result.get("findings"):
                    for finding in step_result["findings"]:
                        self._track_vulnerability(finding, step["agent"], target)
                        results["vulnerabilities"].append(finding)

            except Exception as e:
                logger.error(f"Chain step {step['name']} failed: {e}")
                results["steps"].append({
                    "name": step["name"],
                    "agent": step["agent"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

        results["end_time"] = datetime.now().isoformat()
        results["total_vulnerabilities"] = len(results["vulnerabilities"])

        # Record chain execution
        self.chain_history.append({
            "chain_type": chain_type.value,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities_found": results["total_vulnerabilities"]
        })

        return results

    def _get_chain_definition(self, chain_type: ChainType) -> Optional[Dict[str, Any]]:
        """
        Get chain definition for a given chain type.

        Args:
            chain_type: Type of chain

        Returns:
            Chain definition with steps
        """
        chains = {
            ChainType.ATTACK_DEFENSE: {
                "name": "Attack & Defense Chain",
                "description": "Red team attacks, blue team defends",
                "steps": [
                    {
                        "name": "Red Team Assessment",
                        "agent": "red_teamer",
                        "task": "offensive-security",
                        "description": "Identify exploitable vulnerabilities"
                    },
                    {
                        "name": "Blue Team Response",
                        "agent": "blue_teamer",
                        "task": "defensive-security",
                        "description": "Evaluate defenses against discovered attacks"
                    }
                ]
            },

            ChainType.INVESTIGATION: {
                "name": "Security Investigation Chain",
                "description": "Comprehensive security investigation",
                "steps": [
                    {
                        "name": "Initial Scan",
                        "agent": "codeagent",
                        "task": "code-audit",
                        "description": "Static code analysis"
                    },
                    {
                        "name": "Deep Analysis",
                        "agent": "secret_detection",
                        "task": "secret-detection",
                        "description": "Credential and secret scanning"
                    },
                    {
                        "name": "Forensic Analysis",
                        "agent": "dfir",
                        "task": "forensics",
                        "description": "DFIR investigation of findings"
                    }
                ]
            },

            ChainType.FULL_LIFECYCLE: {
                "name": "Full Security Lifecycle",
                "description": "Complete security assessment lifecycle",
                "steps": [
                    {
                        "name": "Red Team Attack",
                        "agent": "red_teamer",
                        "task": "offensive-security",
                        "description": "Offensive security testing"
                    },
                    {
                        "name": "Blue Team Defense",
                        "agent": "blue_teamer",
                        "task": "defensive-security",
                        "description": "Defensive posture evaluation"
                    },
                    {
                        "name": "Forensic Investigation",
                        "agent": "dfir",
                        "task": "forensics",
                        "description": "Evidence collection and analysis"
                    },
                    {
                        "name": "Remediation Planning",
                        "agent": "codeagent",
                        "task": "code-audit",
                        "description": "Code-level remediation guidance"
                    }
                ]
            },

            ChainType.VALIDATION: {
                "name": "Vulnerability Validation Chain",
                "description": "Discover, validate, and verify fixes",
                "steps": [
                    {
                        "name": "Initial Discovery",
                        "agent": "codeagent",
                        "task": "code-audit",
                        "description": "Find vulnerabilities"
                    },
                    {
                        "name": "Validation",
                        "agent": "bug_bounty",
                        "task": "vuln-scan",
                        "description": "Validate findings"
                    },
                    {
                        "name": "Retest",
                        "agent": "retester",
                        "task": "retest",
                        "description": "Verify fixes"
                    }
                ]
            },

            ChainType.CONTINUOUS: {
                "name": "Continuous Monitoring Chain",
                "description": "Ongoing security monitoring",
                "steps": [
                    {
                        "name": "Baseline Scan",
                        "agent": "codeagent",
                        "task": "code-audit",
                        "description": "Establish security baseline"
                    },
                    {
                        "name": "Secret Monitoring",
                        "agent": "secret_detection",
                        "task": "secret-detection",
                        "description": "Monitor for credential leaks"
                    },
                    {
                        "name": "Configuration Audit",
                        "agent": "config_audit",
                        "task": "config-audit",
                        "description": "Check configuration drift"
                    }
                ]
            }
        }

        return chains.get(chain_type)

    async def _execute_agent_step(
        self,
        agent: str,
        task: str,
        target: str,
        context: Dict[str, Any],
        safe_only: bool
    ) -> Dict[str, Any]:
        """
        Execute a single agent in the chain.

        Args:
            agent: Agent to execute
            task: Task for agent
            target: Scan target
            context: Context from previous steps
            safe_only: Only safe checks

        Returns:
            Agent execution results
        """
        from .security_engine import run_local_scan, run_remote_scan
        from pathlib import Path

        # Determine if local or remote
        is_local = Path(target).exists() if target else False

        try:
            if is_local:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    run_local_scan,
                    target,
                    task,
                    safe_only
                )
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    run_remote_scan,
                    target,
                    task,
                    safe_only
                )

            # Enhance result with context
            if isinstance(result, dict):
                result["context_from_previous_steps"] = context
                result["chain_position"] = len(context.get("chain_history", [])) + 1

            return result

        except Exception as e:
            logger.error(f"Agent {agent} execution failed: {e}")
            return {
                "error": str(e),
                "agent": agent,
                "task": task,
                "findings": []
            }

    def _merge_context(
        self,
        existing_context: Dict[str, Any],
        new_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge context from previous steps with new results.

        Args:
            existing_context: Existing context
            new_results: New results to merge

        Returns:
            Merged context
        """
        merged = existing_context.copy()

        # Add findings to context
        if "all_findings" not in merged:
            merged["all_findings"] = []

        if new_results.get("findings"):
            merged["all_findings"].extend(new_results["findings"])

        # Track chain history
        if "chain_history" not in merged:
            merged["chain_history"] = []

        merged["chain_history"].append({
            "agent": new_results.get("agent"),
            "findings_count": len(new_results.get("findings", [])),
            "timestamp": datetime.now().isoformat()
        })

        # Aggregate severity counts
        if "total_severity_counts" not in merged:
            merged["total_severity_counts"] = {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "INFO": 0
            }

        for finding in new_results.get("findings", []):
            severity = finding.get("severity", "INFO")
            if severity in merged["total_severity_counts"]:
                merged["total_severity_counts"][severity] += 1

        return merged

    def _track_vulnerability(
        self,
        finding: Dict[str, Any],
        discovered_by: str,
        target: str
    ):
        """
        Track vulnerability in lifecycle registry.

        Args:
            finding: Vulnerability finding
            discovered_by: Agent that discovered it
            target: Scan target
        """
        vuln_id = self._generate_vuln_id(finding, target)

        if vuln_id not in self.vulnerability_registry:
            # New vulnerability
            self.vulnerability_registry[vuln_id] = {
                "id": vuln_id,
                "state": VulnerabilityState.DISCOVERED.value,
                "finding": finding,
                "target": target,
                "discovered_by": discovered_by,
                "discovered_at": datetime.now().isoformat(),
                "history": [{
                    "state": VulnerabilityState.DISCOVERED.value,
                    "timestamp": datetime.now().isoformat(),
                    "agent": discovered_by
                }]
            }
            logger.info(f"New vulnerability tracked: {vuln_id}")
        else:
            # Update existing vulnerability
            self.vulnerability_registry[vuln_id]["history"].append({
                "state": "rediscovered",
                "timestamp": datetime.now().isoformat(),
                "agent": discovered_by
            })
            logger.info(f"Vulnerability rediscovered: {vuln_id}")

    def _generate_vuln_id(self, finding: Dict[str, Any], target: str) -> str:
        """
        Generate unique ID for vulnerability.

        Args:
            finding: Vulnerability finding
            target: Scan target

        Returns:
            Unique vulnerability ID
        """
        import hashlib

        # Create ID from type, location, and target
        vuln_string = f"{finding.get('type')}:{finding.get('location')}:{target}"
        return f"vuln_{hashlib.md5(vuln_string.encode()).hexdigest()[:12]}"

    def update_vulnerability_state(
        self,
        vuln_id: str,
        new_state: VulnerabilityState,
        notes: str = ""
    ) -> bool:
        """
        Update vulnerability lifecycle state.

        Args:
            vuln_id: Vulnerability ID
            new_state: New state
            notes: Optional notes

        Returns:
            True if updated successfully
        """
        if vuln_id not in self.vulnerability_registry:
            logger.warning(f"Vulnerability {vuln_id} not found in registry")
            return False

        vuln = self.vulnerability_registry[vuln_id]
        old_state = vuln["state"]

        # Update state
        vuln["state"] = new_state.value
        vuln["history"].append({
            "state": new_state.value,
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "previous_state": old_state
        })

        logger.info(f"Vulnerability {vuln_id}: {old_state} → {new_state.value}")
        return True

    def get_vulnerabilities_by_state(
        self,
        state: VulnerabilityState
    ) -> List[Dict[str, Any]]:
        """
        Get all vulnerabilities in a specific state.

        Args:
            state: Vulnerability state to filter by

        Returns:
            List of vulnerabilities in that state
        """
        return [
            vuln for vuln in self.vulnerability_registry.values()
            if vuln["state"] == state.value
        ]

    def get_vulnerability_metrics(self) -> Dict[str, Any]:
        """
        Get vulnerability lifecycle metrics.

        Returns:
            Metrics dictionary
        """
        metrics = {
            "total_vulnerabilities": len(self.vulnerability_registry),
            "by_state": {},
            "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0},
            "average_time_to_fix": None,
            "chains_executed": len(self.chain_history)
        }

        # Count by state
        for state in VulnerabilityState:
            metrics["by_state"][state.value] = len(
                self.get_vulnerabilities_by_state(state)
            )

        # Count by severity
        for vuln in self.vulnerability_registry.values():
            severity = vuln["finding"].get("severity", "INFO")
            if severity in metrics["by_severity"]:
                metrics["by_severity"][severity] += 1

        # Calculate average time to fix
        fixed_vulns = self.get_vulnerabilities_by_state(VulnerabilityState.VERIFIED)
        if fixed_vulns:
            fix_times = []
            for vuln in fixed_vulns:
                discovered = datetime.fromisoformat(vuln["discovered_at"])
                verified = next(
                    (datetime.fromisoformat(h["timestamp"])
                     for h in vuln["history"]
                     if h["state"] == VulnerabilityState.VERIFIED.value),
                    None
                )
                if verified:
                    fix_times.append((verified - discovered).total_seconds() / 3600)  # hours

            if fix_times:
                metrics["average_time_to_fix"] = sum(fix_times) / len(fix_times)

        return metrics

    async def schedule_follow_up_scan(
        self,
        vuln_id: str,
        delay_hours: int = 24
    ) -> bool:
        """
        Schedule a follow-up scan to verify vulnerability fix.

        Args:
            vuln_id: Vulnerability to retest
            delay_hours: Hours to wait before rescanning

        Returns:
            True if scheduled successfully
        """
        if vuln_id not in self.vulnerability_registry:
            logger.warning(f"Cannot schedule follow-up: {vuln_id} not found")
            return False

        vuln = self.vulnerability_registry[vuln_id]

        # In production, this would integrate with a job scheduler
        # For now, we just log the intent
        rescan_time = datetime.now() + timedelta(hours=delay_hours)

        logger.info(
            f"Follow-up scan scheduled for {vuln_id} at {rescan_time.isoformat()}"
        )

        vuln["follow_up_scheduled"] = {
            "scheduled_at": datetime.now().isoformat(),
            "rescan_at": rescan_time.isoformat(),
            "delay_hours": delay_hours
        }

        return True

    def recommend_chain(
        self,
        findings: Dict[str, Any],
        target_type: str = "code"
    ) -> ChainType:
        """
        Recommend appropriate agent chain based on initial findings.

        Args:
            findings: Initial scan findings
            target_type: Type of target (code, network, etc.)

        Returns:
            Recommended chain type
        """
        findings_list = findings.get("findings", [])

        # Count critical/high findings
        critical_high = len([
            f for f in findings_list
            if f.get("severity") in ["CRITICAL", "HIGH"]
        ])

        # If critical/high findings, recommend full lifecycle
        if critical_high > 0:
            logger.info("Critical findings detected → Recommending FULL_LIFECYCLE chain")
            return ChainType.FULL_LIFECYCLE

        # If moderate findings, recommend attack/defense
        if len(findings_list) > 5:
            logger.info("Multiple findings detected → Recommending ATTACK_DEFENSE chain")
            return ChainType.ATTACK_DEFENSE

        # Otherwise, validation chain
        logger.info("Standard findings → Recommending VALIDATION chain")
        return ChainType.VALIDATION


# Global coordinator instance
_coordinator = None


def get_coordinator() -> AgentCoordinator:
    """Get global agent coordinator instance."""
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentCoordinator()
    return _coordinator

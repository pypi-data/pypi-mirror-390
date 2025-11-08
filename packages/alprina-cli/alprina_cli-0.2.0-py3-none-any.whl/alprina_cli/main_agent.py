"""
Main Alprina Agent - The orchestrator that users interact with.

The Main Agent is aware of all specialized security agents and routes tasks accordingly.
Users talk to the Main Agent via CLI, which then coordinates with specialized agents.

Architecture:
User → CLI → Main Alprina Agent → Security Agents (CodeAgent, Web Scanner, etc.)
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime

from .llm_provider import get_llm_client
from .security_engine import (
    run_agent,
    run_local_scan,
    run_remote_scan,
    AGENTS_AVAILABLE
)
from .report_generator import generate_security_reports
from .workflows import (
    AlprinaWorkflow,
    WorkflowType,
    evaluate_scan_quality,
    evaluate_comprehensive_scan
)
from .agent_coordinator import (
    AgentCoordinator,
    ChainType,
    VulnerabilityState,
    get_coordinator
)
import asyncio


class MainAlprinaAgent:
    """
    Main Alprina Agent - The orchestrator that coordinates all security operations.

    This is the primary agent users interact with. It has knowledge of all specialized
    security agents and routes tasks to the appropriate agent.
    """

    # Registry of all available security agents
    SECURITY_AGENTS = {
        "codeagent": {
            "name": "CodeAgent",
            "task_type": "code-audit",
            "description": "Static Application Security Testing (SAST)",
            "capabilities": [
                "SQL injection detection",
                "XSS (Cross-Site Scripting) detection",
                "CSRF vulnerability detection",
                "Authentication and authorization flaws",
                "Hardcoded secrets and credentials",
                "Insecure cryptography",
                "Input validation issues",
                "Dependency vulnerability scanning"
            ],
            "languages": ["Python", "JavaScript", "TypeScript", "Java", "Go", "PHP", "Ruby", "Rust", "C/C++", "C#"],
            "use_cases": [
                "Scan source code files",
                "Find hardcoded secrets",
                "Detect code vulnerabilities",
                "Audit dependencies"
            ]
        },
        "web_scanner": {
            "name": "Web Scanner Agent",
            "task_type": "web-recon",
            "description": "Web application and API security testing",
            "capabilities": [
                "API endpoint security testing",
                "Authentication bypass detection",
                "Rate limiting analysis",
                "CORS misconfiguration detection",
                "Session management vulnerabilities",
                "HTTP security headers validation",
                "SSL/TLS configuration testing"
            ],
            "use_cases": [
                "Scan web applications",
                "Test API endpoints",
                "Analyze authentication flows",
                "Check security headers"
            ]
        },
        "bug_bounty": {
            "name": "Bug Bounty Agent",
            "task_type": "vuln-scan",
            "description": "OWASP Top 10 and business logic vulnerability detection",
            "capabilities": [
                "OWASP Top 10 vulnerability detection",
                "Business logic flaws",
                "Authorization issues",
                "Information disclosure",
                "Server misconfigurations",
                "Insecure deserialization",
                "XXE (XML External Entities)",
                "Path traversal"
            ],
            "use_cases": [
                "Comprehensive vulnerability scanning",
                "Business logic testing",
                "Authorization testing",
                "OWASP compliance checks"
            ]
        },
        "secret_detection": {
            "name": "Secret Detection Agent",
            "task_type": "secret-detection",
            "description": "Credential and secret scanning",
            "capabilities": [
                "API keys detection",
                "Passwords and tokens",
                "AWS/Cloud credentials",
                "Database connection strings",
                "Private keys and certificates",
                "OAuth tokens",
                "GitHub/GitLab tokens",
                "Slack tokens",
                "Entropy-based analysis"
            ],
            "use_cases": [
                "Find hardcoded secrets",
                "Scan for exposed credentials",
                "Detect API keys in code",
                "Check for password leaks"
            ]
        },
        "config_audit": {
            "name": "Config Audit Agent",
            "task_type": "config-audit",
            "description": "Infrastructure and configuration security",
            "capabilities": [
                "Docker security configuration",
                "Kubernetes manifest auditing",
                "CI/CD pipeline security",
                "Environment variable exposure",
                "Cloud infrastructure misconfigurations",
                "Terraform/IaC security",
                "Container security"
            ],
            "use_cases": [
                "Audit Docker configurations",
                "Scan Kubernetes manifests",
                "Check CI/CD security",
                "Review infrastructure as code"
            ]
        },
        # Priority 1: High-Value Security Agents
        "red_teamer": {
            "name": "Red Team Agent",
            "task_type": "offensive-security",
            "description": "Offensive security testing and attack simulation",
            "capabilities": [
                "Attack simulation",
                "Exploitation techniques",
                "Penetration testing",
                "Security bypass detection",
                "Attack vector identification",
                "Offensive reconnaissance"
            ],
            "use_cases": [
                "Simulate attacks on applications",
                "Test defensive measures",
                "Identify attack vectors",
                "Validate security controls"
            ]
        },
        "blue_teamer": {
            "name": "Blue Team Agent",
            "task_type": "defensive-security",
            "description": "Defensive security posture assessment",
            "capabilities": [
                "Security monitoring",
                "Defense validation",
                "Threat detection",
                "Incident response",
                "Security control assessment",
                "Gap analysis"
            ],
            "use_cases": [
                "Assess defensive security posture",
                "Validate security controls",
                "Identify defense gaps",
                "Monitor for threats"
            ]
        },
        "network_analyzer": {
            "name": "Network Traffic Analyzer",
            "task_type": "network-analysis",
            "description": "Network packet and traffic pattern analysis",
            "capabilities": [
                "Packet inspection",
                "Traffic pattern analysis",
                "Protocol security analysis",
                "Network anomaly detection",
                "Unencrypted traffic detection",
                "Suspicious connection identification"
            ],
            "use_cases": [
                "Analyze network traffic",
                "Inspect API communications",
                "Detect suspicious connections",
                "Validate encryption usage"
            ]
        },
        "reverse_engineer": {
            "name": "Reverse Engineering Agent",
            "task_type": "binary-analysis",
            "description": "Binary analysis and reverse engineering",
            "capabilities": [
                "Binary decompilation",
                "Malware analysis",
                "Executable security analysis",
                "Code obfuscation detection",
                "Backdoor detection",
                "Suspicious function analysis"
            ],
            "use_cases": [
                "Analyze binary executables",
                "Reverse engineer compiled code",
                "Detect malware and backdoors",
                "Examine obfuscated code"
            ]
        },
        "dfir": {
            "name": "DFIR Agent",
            "task_type": "forensics",
            "description": "Digital forensics and incident response",
            "capabilities": [
                "Forensic analysis",
                "Incident investigation",
                "Evidence collection",
                "Timeline reconstruction",
                "Post-breach analysis",
                "Log analysis"
            ],
            "use_cases": [
                "Investigate security incidents",
                "Perform forensic analysis",
                "Collect incident evidence",
                "Reconstruct attack timelines"
            ]
        },
        # Priority 2: Specialized Security Agents
        "android_sast": {
            "name": "Android SAST Agent",
            "task_type": "android-scan",
            "description": "Android application security testing",
            "capabilities": [
                "Android permission analysis",
                "Mobile app vulnerability scanning",
                "Intent security analysis",
                "Data storage security",
                "Network security in mobile apps"
            ],
            "use_cases": [
                "Scan Android applications",
                "Audit mobile app security",
                "Check Android permissions",
                "Analyze mobile data storage"
            ]
        },
        "memory_analysis": {
            "name": "Memory Analysis Agent",
            "task_type": "memory-forensics",
            "description": "Memory forensics and analysis",
            "capabilities": [
                "Memory dump analysis",
                "Process memory inspection",
                "Memory anomaly detection",
                "Malware memory artifacts",
                "Credential extraction from memory"
            ],
            "use_cases": [
                "Analyze memory dumps",
                "Investigate memory-based attacks",
                "Extract forensic evidence",
                "Detect memory anomalies"
            ]
        },
        "wifi_security": {
            "name": "WiFi Security Tester",
            "task_type": "wifi-test",
            "description": "Wireless network security testing",
            "capabilities": [
                "WiFi encryption analysis",
                "Wireless network scanning",
                "Access point security assessment",
                "Rogue AP detection",
                "Weak encryption identification"
            ],
            "use_cases": [
                "Test WiFi security",
                "Audit wireless networks",
                "Detect weak encryption",
                "Identify rogue access points"
            ]
        },
        "replay_attack": {
            "name": "Replay Attack Agent",
            "task_type": "replay-check",
            "description": "Replay attack detection and prevention",
            "capabilities": [
                "Session token analysis",
                "Timestamp validation checking",
                "Nonce implementation review",
                "Replay vulnerability detection",
                "Authentication token security"
            ],
            "use_cases": [
                "Check for replay vulnerabilities",
                "Validate session security",
                "Audit token mechanisms",
                "Test authentication flows"
            ]
        },
        "subghz_sdr": {
            "name": "Sub-GHz SDR Agent",
            "task_type": "radio-security",
            "description": "Software Defined Radio security testing",
            "capabilities": [
                "RF signal analysis",
                "Radio frequency security",
                "Wireless protocol analysis",
                "Unencrypted transmission detection",
                "IoT radio security"
            ],
            "use_cases": [
                "Analyze radio frequency security",
                "Test IoT device communications",
                "Audit wireless protocols",
                "Detect unencrypted RF transmissions"
            ]
        },
        # Priority 3: Utility & Support Agents
        "retester": {
            "name": "Retester Agent",
            "task_type": "retest",
            "description": "Re-testing previously found vulnerabilities",
            "capabilities": [
                "Vulnerability retesting",
                "Fix validation",
                "Regression testing",
                "Historical vulnerability tracking",
                "Remediation verification"
            ],
            "use_cases": [
                "Retest fixed vulnerabilities",
                "Validate security patches",
                "Verify remediation efforts",
                "Track vulnerability lifecycle"
            ]
        },
        "mail": {
            "name": "Mail Agent",
            "task_type": "email-report",
            "description": "Email notifications for security findings",
            "capabilities": [
                "Email report generation",
                "Team notifications",
                "Alert distribution",
                "Scheduled report delivery",
                "Custom email templates"
            ],
            "use_cases": [
                "Email security reports",
                "Send alert notifications",
                "Distribute findings to team",
                "Schedule automated reports"
            ]
        },
        "guardrails": {
            "name": "Guardrails Agent",
            "task_type": "safety-check",
            "description": "Safety validation before executing scans",
            "capabilities": [
                "Pre-scan safety checks",
                "Destructive operation detection",
                "Resource usage validation",
                "Permission verification",
                "Risk assessment"
            ],
            "use_cases": [
                "Validate scan safety",
                "Prevent destructive operations",
                "Check resource limits",
                "Assess operation risks"
            ]
        }
    }

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the Main Alprina Agent.

        Args:
            model: LLM model to use for natural language understanding
        """
        self.model = model
        self.llm = get_llm_client(model=model)
        self.conversation_history = []

        logger.info("Main Alprina Agent initialized with FULL CAI agent coverage")
        logger.info(f"Available security agents: {len(self.SECURITY_AGENTS)} (5 core + 13 specialized)")

    def process_user_request(self, user_message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user request and route to appropriate security agents.

        This is the main entry point. The Main Agent:
        1. Understands user's natural language request
        2. Determines which security agent(s) to use
        3. Coordinates execution with specialized agents (using workflows)
        4. Aggregates and returns results

        Args:
            user_message: Natural language request from user
            context: Optional context (scan results, previous findings, etc.)

        Returns:
            Dictionary with response and any actions taken
        """
        logger.info(f"Main Agent processing: {user_message[:100]}...")

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # Analyze user intent
        intent = self._analyze_intent(user_message, context)

        # Route to appropriate handler
        if intent["type"] == "scan_request":
            # Use async workflow for scan requests
            response = asyncio.run(self._handle_scan_request_async(intent, user_message))
        elif intent["type"] == "explain_vulnerability":
            response = self._handle_explanation_request(intent, user_message)
        elif intent["type"] == "get_remediation":
            response = self._handle_remediation_request(intent, user_message)
        elif intent["type"] == "general_question":
            response = self._handle_general_question(intent, user_message)
        elif intent["type"] == "list_capabilities":
            response = self._handle_capabilities_request()
        else:
            response = self._handle_general_question(intent, user_message)

        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response.get("message", ""),
            "timestamp": datetime.now().isoformat()
        })

        return response

    def _analyze_intent(self, user_message: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Analyze user's intent using LLM to determine which agent(s) to call.

        Args:
            user_message: User's natural language request
            context: Optional context

        Returns:
            Intent analysis with agent routing information
        """
        # Build intent analysis prompt
        prompt = f"""Analyze this user request and determine the intent:

User: "{user_message}"

Available Alprina Security Agents:
{self._format_agents_for_llm()}

Classify the intent as one of:
1. "scan_request" - User wants to scan code/web/API
2. "explain_vulnerability" - User wants explanation of a vulnerability
3. "get_remediation" - User wants fix instructions
4. "list_capabilities" - User asks what you can do / help
5. "general_question" - Security question or advice

For scan_request, identify:
- Target (file path, directory, URL, or IP)
- Which agent(s) to use (codeagent, web_scanner, bug_bounty, secret_detection, config_audit)
- Scan type (code-audit, web-recon, vuln-scan, secret-detection, config-audit)

Return JSON format:
{{
    "type": "scan_request|explain_vulnerability|get_remediation|list_capabilities|general_question",
    "agent": "codeagent|web_scanner|bug_bounty|secret_detection|config_audit",
    "target": "path/url if applicable",
    "confidence": 0.0-1.0
}}"""

        try:
            # Use LLM to analyze intent
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are an intent classifier for Alprina security platform. Return only JSON.",
                max_tokens=500,
                temperature=0.3
            )

            # Parse LLM response
            import json
            intent = json.loads(response.strip().strip("```json").strip("```"))
            return intent

        except Exception as e:
            logger.warning(f"Intent analysis failed: {e}, using fallback")
            return self._fallback_intent_analysis(user_message)

    def _fallback_intent_analysis(self, user_message: str) -> Dict[str, Any]:
        """Fallback intent analysis using keyword matching."""
        message_lower = user_message.lower()

        # Scan request keywords
        if any(word in message_lower for word in ["scan", "check", "analyze", "audit", "test"]):
            # Determine target and agent
            if any(word in message_lower for word in ["code", "file", "python", "javascript", ".py", ".js"]):
                return {"type": "scan_request", "agent": "codeagent", "target": None, "confidence": 0.8}
            elif any(word in message_lower for word in ["web", "api", "http", "url", "domain"]):
                return {"type": "scan_request", "agent": "web_scanner", "target": None, "confidence": 0.8}
            elif any(word in message_lower for word in ["secret", "key", "password", "token", "credential"]):
                return {"type": "scan_request", "agent": "secret_detection", "target": None, "confidence": 0.8}
            elif any(word in message_lower for word in ["docker", "kubernetes", "config", "k8s", "container"]):
                return {"type": "scan_request", "agent": "config_audit", "target": None, "confidence": 0.8}
            else:
                return {"type": "scan_request", "agent": "codeagent", "target": None, "confidence": 0.6}

        # Help/capabilities request
        if any(word in message_lower for word in ["help", "what can you", "capabilities", "what do you"]):
            return {"type": "list_capabilities", "confidence": 0.9}

        # Explanation request
        if any(word in message_lower for word in ["explain", "what is", "tell me about"]):
            return {"type": "explain_vulnerability", "confidence": 0.7}

        # Remediation request
        if any(word in message_lower for word in ["fix", "remediate", "solve", "how to fix"]):
            return {"type": "get_remediation", "confidence": 0.7}

        # Default to general question
        return {"type": "general_question", "confidence": 0.5}

    async def _handle_scan_request_async(self, intent: Dict, user_message: str) -> Dict[str, Any]:
        """
        Handle scan requests using AI SDK workflow patterns.

        Uses orchestrator-worker pattern with parallel execution and quality control.

        Args:
            intent: Intent analysis
            user_message: Original user message

        Returns:
            Scan results and response
        """
        agent_id = intent.get("agent", "codeagent")
        target = intent.get("target")

        # Extract target from message if not in intent
        if not target:
            target = self._extract_target_from_message(user_message)

        if not target:
            return {
                "message": "I'd be happy to run a scan! Could you tell me what you'd like to scan? For example:\n\n- `scan ./src` - Scan a directory\n- `scan app.py` - Scan a file\n- `scan https://api.example.com` - Scan a web endpoint\n- `find secrets in ./` - Search for hardcoded credentials",
                "type": "clarification_needed"
            }

        # Get agent info
        agent_info = self._get_agent_info(agent_id)

        logger.info(f"Routing scan to {agent_info['name']} for target: {target} using WORKFLOW orchestration")

        # Determine if local or remote scan
        from pathlib import Path
        is_local = Path(target).exists()

        try:
            # Check if this is a comprehensive scan (use multiple agents)
            is_comprehensive = any(word in user_message.lower() for word in ["comprehensive", "full", "complete", "all agents"])

            # Check if this is a deep analysis (use sequential workflow)
            is_deep_analysis = any(word in user_message.lower() for word in ["deep", "thorough", "detailed", "in-depth", "sequential"])

            # Check if this is a coordinated agent chain
            is_chain = any(word in user_message.lower() for word in ["chain", "coordinate", "lifecycle", "attack defense", "investigation"])

            if is_chain:
                # Use agent coordinator for sophisticated multi-agent chains
                logger.info("Using AGENT COORDINATOR for chain execution")

                coordinator = get_coordinator()

                # Detect chain type from keywords
                if "attack" in user_message.lower() and "defense" in user_message.lower():
                    chain_type = ChainType.ATTACK_DEFENSE
                elif "lifecycle" in user_message.lower() or "full" in user_message.lower():
                    chain_type = ChainType.FULL_LIFECYCLE
                elif "investigation" in user_message.lower() or "forensic" in user_message.lower():
                    chain_type = ChainType.INVESTIGATION
                elif "validation" in user_message.lower() or "retest" in user_message.lower():
                    chain_type = ChainType.VALIDATION
                elif "continuous" in user_message.lower() or "monitor" in user_message.lower():
                    chain_type = ChainType.CONTINUOUS
                else:
                    # Default to attack/defense
                    chain_type = ChainType.ATTACK_DEFENSE

                # Execute coordinated chain
                chain_results = await coordinator.execute_chain(
                    chain_type=chain_type,
                    target=target,
                    safe_only=True
                )

                results = {
                    "findings": chain_results.get("vulnerabilities", []),
                    "chain_type": chain_results.get("chain_type"),
                    "steps": chain_results.get("steps", []),
                    "total_steps": len(chain_results.get("steps", []))
                }

                agents_used = [step["agent"] for step in chain_results.get("steps", [])]

            elif is_deep_analysis:
                # Use sequential workflow for deep analysis with context passing
                logger.info("Using SEQUENTIAL WORKFLOW for deep analysis")

                workflow = AlprinaWorkflow(WorkflowType.SEQUENTIAL)

                # Define sequential steps with context passing
                steps = [
                    {
                        "agent": "codeagent",
                        "task": "code-audit",
                        "params": {"target": target, "safe_only": True}
                    },
                    {
                        "agent": "secret_detection",
                        "task": "secret-detection",
                        "params": {"target": target, "safe_only": True}
                    },
                    {
                        "agent": "main_alprina_agent",
                        "task": "aggregate_results",
                        "params": {"target": target}
                    }
                ]

                # Add web scanner if target is URL, otherwise config audit
                if not is_local:
                    steps.insert(1, {
                        "agent": "web_scanner",
                        "task": "web-recon",
                        "params": {"target": target, "safe_only": True}
                    })
                else:
                    steps.insert(1, {
                        "agent": "config_audit",
                        "task": "config-audit",
                        "params": {"target": target, "safe_only": True}
                    })

                # Execute sequential workflow
                workflow_result = await workflow.execute_sequential(steps)

                # Extract results from sequential execution
                all_findings = []
                for step in workflow_result.steps:
                    step_findings = step.get("output", {}).get("findings", [])
                    all_findings.extend(step_findings)

                results = {
                    "findings": all_findings,
                    "workflow_type": "sequential",
                    "steps_completed": len(workflow_result.steps)
                }

                agents_used = [step["agent"] for step in steps]

            elif is_comprehensive:
                # Use parallel workflow for comprehensive scans (2-3x faster!)
                logger.info("Using PARALLEL WORKFLOW for comprehensive scan")

                workflow = AlprinaWorkflow(WorkflowType.PARALLEL)

                # Define tasks for all relevant agents
                tasks = [
                    {"agent": "codeagent", "task": "code-audit", "params": {"target": target, "safe_only": True}},
                    {"agent": "secret_detection", "task": "secret-detection", "params": {"target": target, "safe_only": True}},
                ]

                # Add web scanner if target is URL
                if not is_local:
                    tasks.append({"agent": "web_scanner", "task": "web-recon", "params": {"target": target, "safe_only": True}})
                else:
                    # Add config audit for local scans
                    tasks.append({"agent": "config_audit", "task": "config-audit", "params": {"target": target, "safe_only": True}})

                # Execute all agents in parallel
                workflow_result = await workflow.execute_parallel(tasks)

                # Add quality control with evaluator-optimizer
                logger.info("Applying QUALITY CONTROL with evaluator-optimizer")
                quality_workflow = AlprinaWorkflow(WorkflowType.EVALUATOR_OPTIMIZER)

                refined_result = await quality_workflow.execute_evaluator_optimizer(
                    agent="main_alprina_agent",
                    task="aggregate_results",
                    params={"workflow_result": workflow_result.final_output},
                    evaluator_fn=evaluate_comprehensive_scan,
                    max_iterations=2
                )

                # Aggregate results from all agents
                results = self._aggregate_parallel_results(workflow_result.final_output)
                agents_used = [task["agent"] for task in tasks]

            else:
                # Single agent scan with quality control
                logger.info(f"Using SINGLE AGENT WORKFLOW with quality control: {agent_info['name']}")

                # Use evaluator-optimizer workflow for quality
                workflow = AlprinaWorkflow(WorkflowType.EVALUATOR_OPTIMIZER)

                workflow_result = await workflow.execute_evaluator_optimizer(
                    agent=agent_id,
                    task=agent_info["task_type"],
                    params={"target": target, "safe_only": True},
                    evaluator_fn=evaluate_scan_quality,
                    max_iterations=3
                )

                results = workflow_result.final_output
                agents_used = [agent_info["name"]]

            # Generate markdown reports if local scan with findings
            report_path = None
            if is_local and results.get("findings"):
                try:
                    report_path = generate_security_reports(results, target)
                except Exception as e:
                    logger.warning(f"Report generation failed: {e}")

            # Format response
            findings_count = len(results.get("findings", []))

            if is_chain:
                chain_name = results.get("chain_type", "agent chain").replace("_", " ").title()
                message = f"✓ **{chain_name} complete** using {len(agents_used)} coordinated agents!\n\n"
                message += f"**Workflow:** Agent Coordination Chain\n"
                message += f"**Chain Steps:** {results.get('total_steps', 0)}\n"
            elif is_deep_analysis:
                message = f"✓ **Deep analysis complete** using {len(agents_used)} agents sequentially with context passing!\n\n"
                message += f"**Workflow:** Sequential (each agent builds on previous results)\n"
            elif is_comprehensive:
                message = f"✓ **Comprehensive scan complete** using {len(agents_used)} agents in parallel!\n\n"
            else:
                message = f"✓ Scan complete using **{agent_info['name']}** with quality control!\n\n"

            message += f"**Target:** `{target}`\n"
            message += f"**Findings:** {findings_count} security issues detected\n"

            if findings_count > 0:
                # Summarize by severity
                severity_counts = {}
                for finding in results["findings"]:
                    sev = finding.get("severity", "UNKNOWN")
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1

                message += "\n**Severity Breakdown:**\n"
                for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
                    count = severity_counts.get(severity, 0)
                    if count > 0:
                        icons = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "⚪"}
                        message += f"  {icons.get(severity, '•')} {severity}: {count}\n"

                if report_path:
                    message += f"\n📁 **Security reports generated:** `{report_path}/`\n"
                    message += "  • SECURITY-REPORT.md\n"
                    message += "  • FINDINGS.md\n"
                    message += "  • REMEDIATION.md\n"
                    message += "  • EXECUTIVE-SUMMARY.md\n"
            else:
                message += "\n✅ No security issues found! Your code looks good.\n"

            message += f"\nNeed help fixing issues? Just ask: *\"How do I fix finding #1?\"*"

            return {
                "message": message,
                "type": "scan_complete",
                "results": results,
                "agent_used": ", ".join(agents_used),
                "report_path": report_path,
                "workflow_enabled": True
            }

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            return {
                "message": f"❌ Scan failed: {str(e)}\n\nPlease check the target path/URL and try again.",
                "type": "error",
                "error": str(e)
            }

    def _handle_explanation_request(self, intent: Dict, user_message: str) -> Dict[str, Any]:
        """Handle vulnerability explanation requests."""
        # Use LLM to generate explanation
        prompt = f"""User is asking about security concepts or vulnerabilities: "{user_message}"

Provide a clear, concise explanation covering:
1. What it is (simple definition)
2. Why it matters (risk/impact)
3. Common examples
4. How to prevent it

Keep it educational but practical. Use analogies if helpful."""

        try:
            explanation = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=self._get_system_prompt(),
                max_tokens=1000,
                temperature=0.7
            )

            return {
                "message": explanation,
                "type": "explanation"
            }
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return {
                "message": "I can explain security vulnerabilities! Try asking: 'What is SQL injection?' or 'Explain XSS attacks'",
                "type": "error"
            }

    def _handle_remediation_request(self, intent: Dict, user_message: str) -> Dict[str, Any]:
        """Handle remediation/fix requests."""
        prompt = f"""User needs help fixing a security issue: "{user_message}"

Provide step-by-step remediation instructions with:
1. Code examples (vulnerable vs. secure)
2. Best practices
3. Testing/verification steps

Be specific and actionable."""

        try:
            remediation = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=self._get_system_prompt(),
                max_tokens=1500,
                temperature=0.7
            )

            return {
                "message": remediation,
                "type": "remediation"
            }
        except Exception as e:
            logger.error(f"Remediation generation failed: {e}")
            return {
                "message": "I can help you fix security issues! Check the REMEDIATION.md file in your .alprina/ folder for detailed fix instructions.",
                "type": "error"
            }

    def _handle_general_question(self, intent: Dict, user_message: str) -> Dict[str, Any]:
        """Handle general security questions."""
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=self._get_system_prompt(),
                max_tokens=1000,
                temperature=0.7
            )

            return {
                "message": response,
                "type": "general"
            }
        except Exception as e:
            logger.error(f"Question handling failed: {e}")
            return {
                "message": "I'm here to help with security! Ask me to scan code, explain vulnerabilities, or provide security advice.",
                "type": "error"
            }

    def _handle_capabilities_request(self) -> Dict[str, Any]:
        """Handle 'What can you do?' requests."""
        message = """# 👋 Hey! I'm Alprina, your AI security assistant.

I coordinate with **5 specialized security agents** to help you find and fix vulnerabilities:

## 🔍 What I Can Do:

### 1️⃣ **Scan Your Code**
- "Scan ./src for vulnerabilities"
- "Check app.py for security issues"
- "Find hardcoded secrets in my project"

**Agents:** CodeAgent, Secret Detection Agent

### 2️⃣ **Test Web Applications & APIs**
- "Scan https://api.myapp.com"
- "Check my website for vulnerabilities"
- "Test my API endpoints"

**Agent:** Web Scanner Agent

### 3️⃣ **Comprehensive Security Audits**
- "Run full security scan on ./project"
- "Find OWASP Top 10 vulnerabilities"
- "Check for business logic flaws"

**Agent:** Bug Bounty Agent

### 4️⃣ **Audit Infrastructure**
- "Check my Dockerfile security"
- "Audit Kubernetes manifests"
- "Review CI/CD pipeline security"

**Agent:** Config Audit Agent

### 5️⃣ **Explain & Fix**
- "What is SQL injection?"
- "How do I fix XSS vulnerabilities?"
- "Explain finding #3"

## 📁 Automatic Reports

Every scan generates professional markdown reports in `.alprina/`:
- SECURITY-REPORT.md
- FINDINGS.md
- REMEDIATION.md
- EXECUTIVE-SUMMARY.md

## 💬 Just Talk to Me!

You don't need to memorize commands. Just tell me what you need:
- "I want to check my code for vulnerabilities"
- "Help me secure my API"
- "Find any exposed credentials"

**Ready to get started?** Try: `scan ./src`
"""

        return {
            "message": message,
            "type": "capabilities"
        }

    def _aggregate_parallel_results(self, parallel_outputs: List[Any]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agents running in parallel.

        Args:
            parallel_outputs: List of outputs from parallel workflow execution

        Returns:
            Aggregated results dictionary
        """
        aggregated = {
            "findings": [],
            "stats": {
                "total_agents": len(parallel_outputs),
                "total_findings": 0,
                "by_severity": {}
            }
        }

        # Combine findings from all agents
        for output in parallel_outputs:
            if isinstance(output, dict) and "findings" in output:
                aggregated["findings"].extend(output["findings"])

        # Deduplicate findings based on file + line + type
        seen = set()
        unique_findings = []
        for finding in aggregated["findings"]:
            key = (
                finding.get("file", ""),
                finding.get("line", 0),
                finding.get("type", ""),
                finding.get("message", "")
            )
            if key not in seen:
                seen.add(key)
                unique_findings.append(finding)

        aggregated["findings"] = unique_findings
        aggregated["stats"]["total_findings"] = len(unique_findings)

        # Count by severity
        for finding in unique_findings:
            severity = finding.get("severity", "UNKNOWN")
            aggregated["stats"]["by_severity"][severity] = aggregated["stats"]["by_severity"].get(severity, 0) + 1

        return aggregated

    def _extract_target_from_message(self, message: str) -> Optional[str]:
        """Extract scan target from natural language message."""
        import re

        # Look for file paths
        path_pattern = r'[./~][\w/.-]+'
        paths = re.findall(path_pattern, message)
        if paths:
            return paths[0]

        # Look for URLs
        url_pattern = r'https?://[\w.-]+(?:/[\w.-]*)?'
        urls = re.findall(url_pattern, message)
        if urls:
            return urls[0]

        # Look for IP addresses
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        ips = re.findall(ip_pattern, message)
        if ips:
            return ips[0]

        return None

    def _get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get information about a security agent."""
        # Map agent IDs to registry keys
        agent_map = {
            "codeagent": "codeagent",
            "web_scanner": "web_scanner",
            "bug_bounty": "bug_bounty",
            "secret_detection": "secret_detection",
            "config_audit": "config_audit"
        }

        registry_key = agent_map.get(agent_id, "codeagent")
        return self.SECURITY_AGENTS[registry_key]

    def _format_agents_for_llm(self) -> str:
        """Format agent registry for LLM consumption."""
        output = ""
        for agent_id, agent in self.SECURITY_AGENTS.items():
            output += f"\n**{agent['name']}** ({agent_id}):\n"
            output += f"  Task: {agent['task_type']}\n"
            output += f"  Use for: {', '.join(agent['use_cases'][:2])}\n"
        return output

    def _get_system_prompt(self) -> str:
        """Get system prompt for the Main Alprina Agent."""
        return f"""You are the Main Alprina Agent - the primary AI security assistant that users interact with.

You coordinate with {len(self.SECURITY_AGENTS)} specialized security agents:

{self._format_agents_for_llm()}

## Your Role:
- Understand user requests in natural language
- Route tasks to appropriate security agents
- Provide security advice and education
- Generate clear, actionable responses

## Communication Style:
- Friendly and conversational
- Explain security concepts simply
- Provide code examples when helpful
- Always offer next steps

## Remember:
- Users talk to YOU (Main Agent)
- YOU decide which specialized agent to use
- YOU coordinate all security operations
- YOU present results in user-friendly format

Be helpful, educational, and proactive in making security accessible to all developers!"""

    def get_agent_registry(self) -> Dict[str, Any]:
        """
        Get the complete registry of all security agents.

        Returns:
            Dictionary of all available security agents
        """
        return self.SECURITY_AGENTS

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available security agents.

        Returns:
            List of agent information dictionaries
        """
        agents_list = []
        for agent_id, agent_info in self.SECURITY_AGENTS.items():
            agents_list.append({
                "id": agent_id,
                "name": agent_info["name"],
                "description": agent_info["description"],
                "capabilities": agent_info["capabilities"],
                "use_cases": agent_info["use_cases"]
            })
        return agents_list

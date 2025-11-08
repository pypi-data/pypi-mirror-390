"""
Agent endpoints - /v1/agents/*
"""

from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.agent import AgentInfo, AgentListResponse
from ...security_engine import AGENTS_AVAILABLE

router = APIRouter()

# Complete agent catalog - ALL 18 AGENTS
AGENT_CATALOG = [
    # === CORE SECURITY AGENTS (5) ===
    {
        "name": "codeagent",
        "display_name": "CodeAgent",
        "description": "Static Application Security Testing (SAST) - analyzes source code for vulnerabilities",
        "capabilities": ["code-audit", "secret-detection", "vulnerability-detection", "dependency-scanning"],
        "supported_languages": ["python", "javascript", "typescript", "go", "rust", "java", "c", "cpp"],
        "category": "core",
        "icon": "🔍"
    },
    {
        "name": "web_scanner",
        "display_name": "Web Scanner Agent",
        "description": "Web application and API security testing",
        "capabilities": ["web-recon", "api-security", "header-analysis", "ssl-testing"],
        "supported_languages": None,
        "category": "core",
        "icon": "🌐"
    },
    {
        "name": "bug_bounty",
        "display_name": "Bug Bounty Agent",
        "description": "OWASP Top 10 and business logic vulnerability detection",
        "capabilities": ["vuln-scan", "owasp-testing", "business-logic-testing"],
        "supported_languages": None,
        "category": "core",
        "icon": "🎯"
    },
    {
        "name": "secret_detection",
        "display_name": "Secret Detection Agent",
        "description": "Detects hardcoded secrets, API keys, passwords, and credentials",
        "capabilities": ["secret-detection", "credential-scanning", "entropy-analysis"],
        "supported_languages": ["python", "javascript", "typescript", "go", "ruby", "php"],
        "category": "core",
        "icon": "🔑"
    },
    {
        "name": "config_audit",
        "display_name": "Config Audit Agent",
        "description": "Infrastructure and configuration security auditing",
        "capabilities": ["config-audit", "compliance-check", "docker-security", "k8s-audit"],
        "supported_languages": None,
        "category": "core",
        "icon": "⚙️"
    },

    # === PRIORITY 1: HIGH-VALUE AGENTS (5) ===
    {
        "name": "red_teamer",
        "display_name": "Red Team Agent",
        "description": "Offensive security testing and attack simulation",
        "capabilities": ["offensive-security", "attack-simulation", "pen-testing", "exploit-testing"],
        "supported_languages": None,
        "category": "offensive",
        "icon": "⚔️"
    },
    {
        "name": "blue_teamer",
        "display_name": "Blue Team Agent",
        "description": "Defensive security posture assessment and threat detection",
        "capabilities": ["defensive-security", "threat-detection", "defense-validation", "monitoring"],
        "supported_languages": None,
        "category": "defensive",
        "icon": "🛡️"
    },
    {
        "name": "network_analyzer",
        "display_name": "Network Traffic Analyzer",
        "description": "Network packet inspection and traffic pattern analysis",
        "capabilities": ["network-analysis", "packet-inspection", "traffic-analysis", "protocol-security"],
        "supported_languages": None,
        "category": "specialized",
        "icon": "📡"
    },
    {
        "name": "reverse_engineer",
        "display_name": "Reverse Engineering Agent",
        "description": "Binary analysis, decompilation, and malware detection",
        "capabilities": ["binary-analysis", "decompilation", "malware-analysis", "obfuscation-detection"],
        "supported_languages": None,
        "category": "specialized",
        "icon": "🔬"
    },
    {
        "name": "dfir",
        "display_name": "DFIR Agent",
        "description": "Digital Forensics and Incident Response",
        "capabilities": ["forensics", "incident-response", "evidence-collection", "timeline-reconstruction"],
        "supported_languages": None,
        "category": "specialized",
        "icon": "🔍"
    },

    # === PRIORITY 2: SPECIALIZED AGENTS (5) ===
    {
        "name": "android_sast",
        "display_name": "Android SAST Agent",
        "description": "Android application security testing and mobile security",
        "capabilities": ["android-scan", "mobile-security", "permission-analysis", "apk-analysis"],
        "supported_languages": ["java", "kotlin"],
        "category": "specialized",
        "icon": "📱"
    },
    {
        "name": "memory_analysis",
        "display_name": "Memory Analysis Agent",
        "description": "Memory forensics and memory-based attack detection",
        "capabilities": ["memory-forensics", "memory-dump-analysis", "credential-extraction"],
        "supported_languages": None,
        "category": "specialized",
        "icon": "💾"
    },
    {
        "name": "wifi_security",
        "display_name": "WiFi Security Tester",
        "description": "Wireless network security testing and encryption analysis",
        "capabilities": ["wifi-test", "wireless-security", "encryption-analysis", "ap-security"],
        "supported_languages": None,
        "category": "specialized",
        "icon": "📶"
    },
    {
        "name": "replay_attack",
        "display_name": "Replay Attack Agent",
        "description": "Replay attack detection and session security testing",
        "capabilities": ["replay-check", "session-security", "token-analysis", "nonce-validation"],
        "supported_languages": None,
        "category": "specialized",
        "icon": "🔁"
    },
    {
        "name": "subghz_sdr",
        "display_name": "Sub-GHz SDR Agent",
        "description": "Software Defined Radio security and RF analysis",
        "capabilities": ["radio-security", "rf-analysis", "iot-security", "wireless-protocol-analysis"],
        "supported_languages": None,
        "category": "specialized",
        "icon": "📻"
    },

    # === PRIORITY 3: UTILITY AGENTS (3) ===
    {
        "name": "retester",
        "display_name": "Retester Agent",
        "description": "Re-testing and validation of previously found vulnerabilities",
        "capabilities": ["retest", "fix-validation", "regression-testing", "remediation-verification"],
        "supported_languages": None,
        "category": "utility",
        "icon": "🔄"
    },
    {
        "name": "mail",
        "display_name": "Mail Agent",
        "description": "Email notifications and automated security reporting",
        "capabilities": ["email-report", "notifications", "alert-distribution", "scheduled-reports"],
        "supported_languages": None,
        "category": "utility",
        "icon": "📧"
    },
    {
        "name": "guardrails",
        "display_name": "Guardrails Agent",
        "description": "Safety validation and pre-scan security checks",
        "capabilities": ["safety-check", "validation", "risk-assessment", "permission-check"],
        "supported_languages": None,
        "category": "utility",
        "icon": "🛡️"
    }
]


@router.get("/agents", response_model=AgentListResponse)
async def list_agents():
    """
    List all available security agents.

    Returns information about all Alprina security agents including
    their capabilities, supported languages, and descriptions.

    **Example:**
    ```python
    import requests

    response = requests.get("http://localhost:8000/v1/agents")
    agents = response.json()["agents"]

    for agent in agents:
        print(f"{agent['display_name']}: {agent['description']}")
    ```
    """
    agents_list = [
        AgentInfo(
            name=agent["name"],
            display_name=agent["display_name"],
            description=agent["description"],
            capabilities=agent["capabilities"],
            supported_languages=agent["supported_languages"],
            category=agent.get("category", "core"),
            icon=agent.get("icon")
        )
        for agent in AGENT_CATALOG
    ]

    return AgentListResponse(
        agents=agents_list,
        total=len(agents_list),
        security_engine="active" if AGENTS_AVAILABLE else "fallback"
    )


@router.get("/agents/{agent_name}", response_model=AgentInfo)
async def get_agent_info(agent_name: str):
    """
    Get detailed information about a specific agent.

    **Parameters:**
    - `agent_name`: Agent identifier (e.g., "codeagent", "web_scanner_agent")
    """
    agent_data = next((a for a in AGENT_CATALOG if a["name"] == agent_name), None)

    if not agent_data:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found"
        )

    return AgentInfo(
        name=agent_data["name"],
        display_name=agent_data["display_name"],
        description=agent_data["description"],
        capabilities=agent_data["capabilities"],
        supported_languages=agent_data["supported_languages"]
    )

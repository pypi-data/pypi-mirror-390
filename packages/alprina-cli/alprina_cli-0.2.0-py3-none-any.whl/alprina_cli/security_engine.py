"""
Alprina Security Engine.
AI-powered vulnerability detection and security analysis.
Built on Alprina's proprietary security agent framework.
"""

import os
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger

from .llm_provider import get_llm_client

# Import Alprina security agents
try:
    from .agents.red_teamer import run_red_team_scan
    from .agents.blue_teamer import run_blue_team_scan
    from .agents.network_analyzer import run_network_analyzer_scan
    from .agents.reverse_engineer import run_reverse_engineer_scan
    from .agents.dfir import run_dfir_scan
    from .agents.android_sast import run_android_sast_scan
    from .agents.memory_analysis import run_memory_analysis_scan
    from .agents.wifi_security import run_wifi_security_scan
    from .agents.replay_attack import run_replay_attack_scan
    from .agents.subghz_sdr import run_subghz_sdr_scan
    from .agents.retester import run_retester_scan
    from .agents.mail import run_mail_scan
    from .agents.guardrails import run_guardrails_scan
    AGENTS_AVAILABLE = True
    logger.info("Alprina security engine initialized successfully")
except ImportError as e:
    AGENTS_AVAILABLE = False
    logger.error(f"Alprina agents not available: {e}")
    logger.warning("Using fallback LLM analysis methods")

# Task to Alprina agent mapping
AGENT_MAPPING = {
    "offensive-security": run_red_team_scan,
    "defensive-security": run_blue_team_scan,
    "network-analysis": run_network_analyzer_scan,
    "binary-analysis": run_reverse_engineer_scan,
    "forensics": run_dfir_scan,
    "android-scan": run_android_sast_scan,
    "memory-forensics": run_memory_analysis_scan,
    "wifi-test": run_wifi_security_scan,
    "replay-check": run_replay_attack_scan,
    "radio-security": run_subghz_sdr_scan,
    "retest": run_retester_scan,
    "email-report": run_mail_scan,
    "safety-check": run_guardrails_scan,
    # Aliases for common tasks
    "code-audit": run_red_team_scan,
    "web-recon": run_network_analyzer_scan,
    "vuln-scan": run_red_team_scan,
    "secret-detection": run_red_team_scan,
    "config-audit": run_blue_team_scan
}


def run_agent(task: str, input_data: str, metadata: dict) -> dict:
    """
    Run an Alprina security agent for vulnerability analysis.

    Args:
        task: Task/agent type (e.g., 'code-audit', 'web-recon', 'vuln-scan')
        input_data: Input data for the agent
        metadata: Additional metadata for the scan

    Returns:
        Dict containing scan results
    """
    logger.info(f"Running Alprina agent: {task}")
    logger.debug(f"Input length: {len(input_data)} chars")
    logger.debug(f"Metadata: {metadata}")

    # Use Alprina agents if available
    if AGENTS_AVAILABLE and task in AGENT_MAPPING:
        logger.info(f"Using Alprina agent for task: {task}")
        agent_func = AGENT_MAPPING[task]
        result = agent_func(
            target=metadata.get("path", input_data),
            safe_only=metadata.get("safe_only", True)
        )
        return result

    # Fallback to LLM-based analysis if agents not available
    logger.warning(f"Agent '{task}' not found in mapping, falling back to LLM analysis")
    return _run_llm_analysis(task, input_data, metadata)


def _run_llm_analysis(task: str, input_data: str, metadata: dict) -> dict:
    """
    Build analysis prompt for Alprina agent.

    Args:
        task: Task type
        content: Code/content to analyze
        metadata: Additional context

    Returns:
        Formatted prompt string
    """
    file_info = metadata.get("file", "unknown file")
    safe_only = metadata.get("safe_only", True)

    prompts = {
        "code-audit": f"""Perform a comprehensive security audit of this code.

File: {file_info}
Safe Mode: {safe_only}

Code to analyze:
```
{content[:5000]}  # Limit to 5000 chars for efficiency
```

Please identify:
1. Security vulnerabilities (SQL injection, XSS, etc.)
2. Hardcoded secrets (API keys, passwords, tokens)
3. Insecure configurations
4. Authentication/authorization issues
5. Input validation problems
6. Cryptographic weaknesses

For each finding, provide:
- Severity (HIGH/MEDIUM/LOW)
- Type/Category
- Description
- Location (line number if possible)
- Remediation steps

Format your response as a structured analysis.""",

        "secret-detection": f"""Scan this code for hardcoded secrets and sensitive information.

File: {file_info}

Code:
```
{content[:5000]}
```

Look for:
- API keys
- Passwords
- Tokens
- Private keys
- Database credentials
- AWS/Cloud credentials

Report each finding with severity and location.""",

        "config-audit": f"""Audit this configuration file for security issues.

File: {file_info}

Configuration:
```
{content[:5000]}
```

Check for:
- Insecure settings
- Default credentials
- Exposed secrets
- Weak permissions
- Security misconfigurations

Provide remediation for each issue."""
    }

    return prompts.get(task, prompts["code-audit"])


def _parse_alprina_result(result: str, metadata: dict) -> List[Dict[str, Any]]:
    """
    Parse Alprina agent result into structured findings.

    Args:
        result: Agent response string
        metadata: Original metadata

    Returns:
        List of finding dictionaries
    """
    findings = []

    # Simple parsing - look for severity keywords and extract findings
    # This is a basic parser - can be enhanced based on actual Alprina agent output format

    lines = result.split('\n')
    current_finding = None

    for line in lines:
        line_lower = line.lower()

        # Check for severity markers
        if any(sev in line_lower for sev in ['high', 'critical', 'severe']):
            if current_finding:
                findings.append(current_finding)
            current_finding = {
                "severity": "HIGH",
                "type": "Security Issue",
                "description": line.strip(),
                "location": metadata.get("file", "unknown"),
                "line": None
            }
        elif any(sev in line_lower for sev in ['medium', 'moderate']):
            if current_finding:
                findings.append(current_finding)
            current_finding = {
                "severity": "MEDIUM",
                "type": "Security Issue",
                "description": line.strip(),
                "location": metadata.get("file", "unknown"),
                "line": None
            }
        elif any(sev in line_lower for sev in ['low', 'minor', 'info']):
            if current_finding:
                findings.append(current_finding)
            current_finding = {
                "severity": "LOW",
                "type": "Security Issue",
                "description": line.strip(),
                "location": metadata.get("file", "unknown"),
                "line": None
            }
        elif current_finding and line.strip():
            # Add to current finding description
            current_finding["description"] += " " + line.strip()

    if current_finding:
        findings.append(current_finding)

    # If no findings parsed, create a summary finding
    if not findings and len(result) > 50:
        findings.append({
            "severity": "INFO",
            "type": "Analysis Complete",
            "description": result[:500],  # First 500 chars
            "location": metadata.get("file", "unknown"),
            "line": None
        })

    return findings


def _run_llm_analysis(task: str, input_data: str, metadata: dict) -> dict:
    """
    Fallback LLM-based analysis when CAI not available.

    Args:
        task: Analysis task
        input_data: Content to analyze
        metadata: Additional context

    Returns:
        Dict with findings
    """
    logger.info("Using LLM fallback analysis")

    try:
        llm_client = get_llm_client()

        if task in ["code-audit", "secret-detection", "config-audit"]:
            filename = metadata.get("file", "unknown")
            result = llm_client.analyze_code(input_data, filename, task)
            return result
        else:
            # For other tasks, use basic pattern matching
            return _pattern_based_analysis(input_data, metadata)

    except Exception as e:
        logger.error(f"LLM analysis error: {e}")
        return _pattern_based_analysis(input_data, metadata)


def _pattern_based_analysis(content: str, metadata: dict) -> dict:
    """
    Basic pattern-based security analysis as last resort fallback.

    Args:
        content: Content to analyze
        metadata: Context metadata

    Returns:
        Dict with findings
    """
    findings = []

    # Pattern-based detection
    patterns = {
        "Hardcoded Secret": [
            (r"password\s*=\s*['\"][^'\"]+['\"]", "HIGH"),
            (r"api_key\s*=\s*['\"][^'\"]+['\"]", "HIGH"),
            (r"secret\s*=\s*['\"][^'\"]+['\"]", "HIGH"),
            (r"token\s*=\s*['\"][^'\"]+['\"]", "MEDIUM"),
        ],
        "Debug Mode": [
            (r"debug\s*=\s*true", "MEDIUM"),
            (r"DEBUG\s*=\s*True", "MEDIUM"),
        ],
        "SQL Injection Risk": [
            (r"execute\(['\"].*%s.*['\"]", "HIGH"),
            (r"execute\(['\"].*\+.*['\"]", "HIGH"),
        ],
        "Insecure Function": [
            (r"eval\(", "HIGH"),
            (r"exec\(", "HIGH"),
        ]
    }

    import re

    for vuln_type, pattern_list in patterns.items():
        for pattern, severity in pattern_list:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "severity": severity,
                    "type": vuln_type,
                    "description": f"Pattern detected: {match.group(0)[:100]}",
                    "location": metadata.get("file", "unknown"),
                    "line": content[:match.start()].count('\n') + 1
                })

    # Environment file check
    if ".env" in metadata.get("file", ""):
        findings.append({
            "severity": "LOW",
            "type": "Environment File",
            "description": "Environment file detected - ensure it's in .gitignore",
            "location": metadata.get("file", "unknown"),
            "line": None
        })

    return {
        "findings": findings,
        "metadata": metadata,
        "alprina_enabled": False,
        "analysis_method": "pattern_based"
    }


def run_local_scan(path: str, profile: str = "code-audit", safe_only: bool = True) -> dict:
    """
    Scan local files/directories for security issues using Alprina agents.

    Args:
        path: Path to file or directory
        profile: Scan profile to use
        safe_only: Only run safe, non-intrusive checks

    Returns:
        Dict containing scan results
    """
    logger.info(f"Starting local scan: {path} (Engine: {'active' if AGENTS_AVAILABLE else 'fallback'})")

    target_path = Path(path)

    if not target_path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    # Collect files to scan
    if target_path.is_file():
        files = [target_path]
    else:
        files = _collect_scannable_files(target_path)

    logger.info(f"Found {len(files)} files to scan")

    results = {
        "mode": "local",
        "target": str(path),
        "profile": profile,
        "files_scanned": len(files),
        "findings": [],
        "alprina_engine": "active" if AGENTS_AVAILABLE else "fallback"
    }

    # Scan each file
    for i, file_path in enumerate(files, 1):
        try:
            logger.info(f"Scanning file {i}/{len(files)}: {file_path.name}")
            file_results = _scan_file(file_path, profile, safe_only)
            results["findings"].extend(file_results)
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

    logger.info(f"Scan complete: {len(results['findings'])} findings")
    return results


def run_remote_scan(target: str, profile: str = "web-recon", safe_only: bool = True) -> dict:
    """
    Scan remote target (URL, domain, or IP) using Alprina security agents.

    Args:
        target: Target URL, domain, or IP
        profile: Scan profile to use
        safe_only: Only run safe, non-intrusive checks

    Returns:
        Dict containing scan results
    """
    logger.info(f"Starting remote scan: {target} (Engine: {'active' if AGENTS_AVAILABLE else 'fallback'})")

    # Use Alprina security agent for remote scanning
    results = run_agent(
        task=profile,
        input_data=target,
        metadata={
            "safe_only": safe_only,
            "mode": "remote"
        }
    )

    return {
        "mode": "remote",
        "target": target,
        "profile": profile,
        "alprina_engine": "active" if AGENTS_AVAILABLE else "fallback",
        **results
    }


def _collect_scannable_files(directory: Path) -> List[Path]:
    """
    Collect files that should be scanned for security issues.
    """
    scannable_extensions = (
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
        ".env", ".yaml", ".yml", ".json", ".xml", ".ini", ".conf",
        ".sh", ".bash", ".zsh", ".dockerfile", ".tf", ".hcl", ".php",
        ".rb", ".c", ".cpp", ".h", ".cs", ".swift", ".kt"
    )

    scannable_names = (
        "Dockerfile", "Makefile", "docker-compose.yml", "docker-compose.yaml",
        ".env", ".env.local", ".env.production", ".env.development",
        "config.json", "settings.json", "secrets.json"
    )

    files = []

    for item in directory.rglob("*"):
        if item.is_file():
            # Check by extension or name
            if item.suffix.lower() in scannable_extensions or item.name in scannable_names:
                # Skip common directories
                if not any(part.startswith(".") or part in ["node_modules", "venv", "__pycache__", "dist", "build", "target"]
                          for part in item.parts):
                    files.append(item)

    return files


def _scan_file(file_path: Path, profile: str, safe_only: bool) -> List[Dict[str, Any]]:
    """
    Scan a single file for security issues using Alprina agents.
    """
    findings = []

    try:
        content = file_path.read_text(errors="ignore")
        file_hash = hashlib.md5(content.encode()).hexdigest()

        # Run Alprina agent on file content
        result = run_agent(
            task=profile,
            input_data=content,
            metadata={
                "file": str(file_path),
                "hash": file_hash,
                "safe_only": safe_only,
                "file_type": file_path.suffix
            }
        )

        # Extract findings from result
        if "findings" in result:
            for finding in result["findings"]:
                finding["location"] = str(file_path)
                findings.append(finding)

    except Exception as e:
        logger.error(f"Error scanning file {file_path}: {e}")

    return findings

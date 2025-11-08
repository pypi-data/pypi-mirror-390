"""
Scan endpoints - /v1/scan/*
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
import hashlib

from ..schemas.scan import CodeScanRequest, TargetScanRequest, ScanResponse, Finding, ScanSummary
from ...security_engine import run_agent, AGENTS_AVAILABLE

router = APIRouter()


@router.post("/scan/code", response_model=ScanResponse)
async def scan_code(request: CodeScanRequest):
    """
    Scan source code for security vulnerabilities.

    Analyzes the provided code using Alprina's AI-powered security agents
    to detect vulnerabilities, hardcoded secrets, insecure configurations,
    and other security issues.

    **Example:**
    ```python
    import requests

    response = requests.post(
        "http://localhost:8000/v1/scan/code",
        json={
            "code": "API_KEY = 'sk-1234567890'",
            "language": "python",
            "profile": "code-audit"
        }
    )
    ```
    """
    start_time = time.time()

    try:
        # Generate scan ID
        scan_id = f"scan_{hashlib.md5(request.code.encode()).hexdigest()[:10]}"

        # Prepare metadata
        metadata = request.metadata or {}
        metadata.update({
            "language": request.language,
            "profile": request.profile,
            "safe_only": request.safe_only
        })

        # Run security agent
        results = run_agent(
            task=request.profile,
            input_data=request.code,
            metadata=metadata
        )

        # Convert findings to schema
        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Unknown"),
                    title=finding.get("title", finding.get("type", "Security Finding")),
                    description=finding.get("description", ""),
                    location=finding.get("location"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        # Calculate summary
        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Alprina Security Engine",
            alprina_engine=results.get("alprina_engine", "active" if AGENTS_AVAILABLE else "fallback"),
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(e)}"
        )


@router.post("/scan/red-team", response_model=ScanResponse)
async def red_team_scan(request: TargetScanRequest):
    """
    Run offensive security red team scan.

    Performs attack simulation and penetration testing to identify
    exploitable vulnerabilities and attack vectors.
    """
    start_time = time.time()

    try:
        from ...agents.red_teamer import run_red_team_scan

        scan_id = f"scan_redteam_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_red_team_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Attack Vector"),
                    title=finding.get("title", "Red Team Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Red Team Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Red team scan failed: {str(e)}")


@router.post("/scan/blue-team", response_model=ScanResponse)
async def blue_team_scan(request: TargetScanRequest):
    """
    Run defensive security blue team assessment.

    Evaluates security posture, validates defenses, and identifies
    gaps in monitoring and threat detection capabilities.
    """
    start_time = time.time()

    try:
        from ...agents.blue_teamer import run_blue_team_scan

        scan_id = f"scan_blueteam_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_blue_team_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Defense Gap"),
                    title=finding.get("title", "Blue Team Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Blue Team Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blue team scan failed: {str(e)}")


@router.post("/scan/network-analysis", response_model=ScanResponse)
async def network_analysis_scan(request: TargetScanRequest):
    """
    Run network traffic analysis and packet inspection.

    Analyzes network traffic patterns, protocol security, and
    identifies suspicious connections and data exfiltration risks.
    """
    start_time = time.time()

    try:
        from ...agents.network_analyzer import run_network_analyzer_scan

        scan_id = f"scan_network_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_network_analyzer_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Network Issue"),
                    title=finding.get("title", "Network Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Network Traffic Analyzer",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network analysis scan failed: {str(e)}")


@router.post("/scan/reverse-engineering", response_model=ScanResponse)
async def reverse_engineering_scan(request: TargetScanRequest):
    """
    Run binary analysis and reverse engineering scan.

    Performs decompilation, binary analysis, malware detection,
    and identifies backdoors and obfuscation techniques.
    """
    start_time = time.time()

    try:
        from ...agents.reverse_engineer import run_reverse_engineer_scan

        scan_id = f"scan_reverse_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_reverse_engineer_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Binary Issue"),
                    title=finding.get("title", "Reverse Engineering Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Reverse Engineering Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reverse engineering scan failed: {str(e)}")


@router.post("/scan/forensics", response_model=ScanResponse)
async def forensics_scan(request: TargetScanRequest):
    """
    Run digital forensics and incident response (DFIR) scan.

    Performs forensic analysis, evidence collection, timeline reconstruction,
    and identifies indicators of compromise.
    """
    start_time = time.time()

    try:
        from ...agents.dfir import run_dfir_scan

        scan_id = f"scan_dfir_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_dfir_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Forensic Evidence"),
                    title=finding.get("title", "DFIR Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="DFIR Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DFIR scan failed: {str(e)}")


@router.post("/scan/android", response_model=ScanResponse)
async def android_scan(request: TargetScanRequest):
    """
    Run Android application security testing.

    Analyzes Android APK files for security vulnerabilities, dangerous
    permissions, insecure data storage, and network security issues.
    """
    start_time = time.time()

    try:
        from ...agents.android_sast import run_android_sast_scan

        scan_id = f"scan_android_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_android_sast_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Mobile Security Issue"),
                    title=finding.get("title", "Android Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Android SAST Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Android scan failed: {str(e)}")


@router.post("/scan/memory-analysis", response_model=ScanResponse)
async def memory_analysis_scan(request: TargetScanRequest):
    """
    Run memory forensics and memory-based attack detection.

    Analyzes memory dumps for forensic evidence, credential extraction,
    and memory-resident malware.
    """
    start_time = time.time()

    try:
        from ...agents.memory_analysis import run_memory_analysis_scan

        scan_id = f"scan_memory_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_memory_analysis_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Memory Issue"),
                    title=finding.get("title", "Memory Analysis Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Memory Analysis Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory analysis scan failed: {str(e)}")


@router.post("/scan/wifi-security", response_model=ScanResponse)
async def wifi_security_scan(request: TargetScanRequest):
    """
    Run wireless network security testing.

    Tests WiFi network security, encryption analysis, access point
    security, and wireless protocol vulnerabilities.
    """
    start_time = time.time()

    try:
        from ...agents.wifi_security import run_wifi_security_scan

        scan_id = f"scan_wifi_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_wifi_security_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "WiFi Security Issue"),
                    title=finding.get("title", "WiFi Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="WiFi Security Tester",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WiFi security scan failed: {str(e)}")


@router.post("/scan/replay-attack", response_model=ScanResponse)
async def replay_attack_scan(request: TargetScanRequest):
    """
    Run replay attack detection and session security testing.

    Tests for replay attack vulnerabilities, session security issues,
    token validation, and nonce implementation.
    """
    start_time = time.time()

    try:
        from ...agents.replay_attack import run_replay_attack_scan

        scan_id = f"scan_replay_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_replay_attack_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Replay Vulnerability"),
                    title=finding.get("title", "Replay Attack Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Replay Attack Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Replay attack scan failed: {str(e)}")


@router.post("/scan/radio-security", response_model=ScanResponse)
async def radio_security_scan(request: TargetScanRequest):
    """
    Run Software Defined Radio (SDR) and RF security analysis.

    Analyzes radio frequency security, IoT wireless protocols,
    and Sub-GHz communication vulnerabilities.
    """
    start_time = time.time()

    try:
        from ...agents.subghz_sdr import run_subghz_sdr_scan

        scan_id = f"scan_radio_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_subghz_sdr_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "RF Security Issue"),
                    title=finding.get("title", "Radio Security Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Sub-GHz SDR Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Radio security scan failed: {str(e)}")


@router.post("/scan/retest", response_model=ScanResponse)
async def retest_scan(request: TargetScanRequest):
    """
    Run vulnerability retesting and fix validation.

    Re-tests previously identified vulnerabilities to verify fixes,
    performs regression testing, and validates remediation efforts.
    """
    start_time = time.time()

    try:
        from ...agents.retester import run_retester_scan

        scan_id = f"scan_retest_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_retester_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Retest Result"),
                    title=finding.get("title", "Retest Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Retester Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retest scan failed: {str(e)}")


@router.post("/scan/email-report", response_model=ScanResponse)
async def email_report_scan(request: TargetScanRequest):
    """
    Generate and send email security reports.

    Creates automated security reports with findings and sends them
    via email to specified recipients for notification and alerting.
    """
    start_time = time.time()

    try:
        from ...agents.mail import run_mail_scan

        scan_id = f"scan_email_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_mail_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Email Report"),
                    title=finding.get("title", "Email Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Mail Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email report generation failed: {str(e)}")


@router.post("/scan/safety-check", response_model=ScanResponse)
async def safety_check_scan(request: TargetScanRequest):
    """
    Run pre-scan safety validation and guardrails check.

    Validates scan safety, performs risk assessment, checks permissions,
    and ensures scans won't cause harm before execution.
    """
    start_time = time.time()

    try:
        from ...agents.guardrails import run_guardrails_scan

        scan_id = f"scan_safety_{hashlib.md5(request.target.encode()).hexdigest()[:10]}"
        results = run_guardrails_scan(request.target, safe_only=request.safe_only)

        findings_list = []
        for i, finding in enumerate(results.get("findings", []), 1):
            findings_list.append(
                Finding(
                    id=f"{scan_id}_finding_{i}",
                    severity=finding.get("severity", "INFO"),
                    type=finding.get("type", "Safety Check"),
                    title=finding.get("title", "Guardrails Finding"),
                    description=finding.get("description", ""),
                    location=finding.get("file"),
                    line=finding.get("line"),
                    confidence=finding.get("confidence")
                )
            )

        summary = ScanSummary(
            total_findings=len(findings_list),
            critical=sum(1 for f in findings_list if f.severity == "CRITICAL"),
            high=sum(1 for f in findings_list if f.severity == "HIGH"),
            medium=sum(1 for f in findings_list if f.severity == "MEDIUM"),
            low=sum(1 for f in findings_list if f.severity == "LOW"),
            info=sum(1 for f in findings_list if f.severity == "INFO")
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResponse(
            scan_id=scan_id,
            status="completed",
            scanned_by="Guardrails Agent",
            alprina_engine="active" if AGENTS_AVAILABLE else "fallback",
            findings=findings_list,
            summary=summary,
            duration_ms=duration_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety check failed: {str(e)}")


@router.get("/scan/{scan_id}")
async def get_scan_results(scan_id: str):
    """
    Get scan results by ID.

    **Note:** Currently returns a placeholder. Implement database
    storage to persist and retrieve scan results.
    """
    # TODO: Implement database storage and retrieval
    return {
        "scan_id": scan_id,
        "status": "not_implemented",
        "message": "Scan result storage not yet implemented"
    }

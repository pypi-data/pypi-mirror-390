"""
Alprina Security Agents

This module contains all specialized security agents for the Alprina platform.
Agents are organized by security domain:

**Offensive Security:**
- Red Team Agent - Offensive security testing and attack simulation

**Defensive Security:**
- Blue Team Agent - Defensive security posture assessment

**Network Security:**
- Network Traffic Analyzer - Packet inspection and traffic analysis

**Binary Analysis:**
- Reverse Engineering Agent - Binary decompilation and analysis

**Forensics:**
- DFIR Agent - Digital Forensics and Incident Response

**Specialized:**
- Android SAST Agent - Android application security
- Memory Analysis Agent - Memory forensics
- WiFi Security Tester - Wireless network security
- Replay Attack Agent - Replay attack detection
- Sub-GHz SDR Agent - Radio frequency security

**Utility:**
- Retester Agent - Vulnerability retesting
- Mail Agent - Email notifications
- Guardrails Agent - Safety validation
- Flag Discriminator - CTF flag detection

All agents integrate with the Main Alprina Agent orchestrator and support
AI SDK workflow patterns for parallel execution and quality control.
"""

__version__ = "1.0.0"
__all__ = [
    "red_teamer",
    "blue_teamer",
    "network_analyzer",
    "reverse_engineer",
    "dfir",
    "android_sast",
    "memory_analysis",
    "wifi_security",
    "replay_attack",
    "subghz_sdr",
    "retester",
    "mail",
    "guardrails",
    "flag_discriminator"
]

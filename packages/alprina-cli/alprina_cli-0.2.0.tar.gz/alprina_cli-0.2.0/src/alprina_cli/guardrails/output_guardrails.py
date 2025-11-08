"""
Output Guardrails

Sanitize sensitive information from tool outputs.
Prevent leaking: PII, credentials, internal IPs, file paths, etc.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel
from loguru import logger
import re


class SanitizationResult(BaseModel):
    """Result from output sanitization"""
    sanitized_value: Any
    redactions_made: int = 0
    redaction_types: List[str] = []


class OutputGuardrail(ABC):
    """
    Base class for output guardrails.

    Context Engineering:
    - Fast sanitization (< 10ms per check)
    - Preserve data utility while removing sensitive info
    - Track what was redacted for audit logs
    """

    name: str = "OutputGuardrail"

    @abstractmethod
    def sanitize(self, value: Any) -> SanitizationResult:
        """
        Sanitize output value.

        Args:
            value: Output value to sanitize

        Returns:
            SanitizationResult with sanitized value and redaction info
        """
        raise NotImplementedError


class PIIScrubber(OutputGuardrail):
    """
    Scrub Personally Identifiable Information from outputs.

    Patterns detected:
    - Email addresses
    - Phone numbers (US/International)
    - Social Security Numbers
    - Credit card numbers
    - IP addresses (when configured)
    """

    name: str = "PIIScrubber"

    # PII patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # Phone pattern to match various formats: 555-123-4567, (555) 123-4567, 5551234567, +1-555-123-4567
    PHONE_PATTERN = r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b'
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    CREDIT_CARD_PATTERN = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'

    def __init__(self, scrub_emails: bool = True, scrub_phones: bool = True,
                 scrub_ssn: bool = True, scrub_credit_cards: bool = True):
        self.scrub_emails = scrub_emails
        self.scrub_phones = scrub_phones
        self.scrub_ssn = scrub_ssn
        self.scrub_credit_cards = scrub_credit_cards

    def sanitize(self, value: Any) -> SanitizationResult:
        """Scrub PII from value"""
        if not isinstance(value, str):
            return SanitizationResult(sanitized_value=value, redactions_made=0)

        sanitized = value
        redactions = 0
        redaction_types = []

        # Scrub emails
        if self.scrub_emails:
            emails_found = re.findall(self.EMAIL_PATTERN, sanitized)
            if emails_found:
                sanitized = re.sub(self.EMAIL_PATTERN, '[EMAIL_REDACTED]', sanitized)
                redactions += len(emails_found)
                redaction_types.append("email")
                logger.debug(f"Redacted {len(emails_found)} email(s)")

        # Scrub phone numbers
        if self.scrub_phones:
            phones_found = re.findall(self.PHONE_PATTERN, sanitized)
            if phones_found:
                sanitized = re.sub(self.PHONE_PATTERN, '[PHONE_REDACTED]', sanitized)
                redactions += len(phones_found)
                redaction_types.append("phone")
                logger.debug(f"Redacted {len(phones_found)} phone number(s)")

        # Scrub SSNs
        if self.scrub_ssn:
            ssns_found = re.findall(self.SSN_PATTERN, sanitized)
            if ssns_found:
                sanitized = re.sub(self.SSN_PATTERN, '[SSN_REDACTED]', sanitized)
                redactions += len(ssns_found)
                redaction_types.append("ssn")
                logger.debug(f"Redacted {len(ssns_found)} SSN(s)")

        # Scrub credit cards
        if self.scrub_credit_cards:
            cards_found = re.findall(self.CREDIT_CARD_PATTERN, sanitized)
            if cards_found:
                sanitized = re.sub(self.CREDIT_CARD_PATTERN, '[CREDIT_CARD_REDACTED]', sanitized)
                redactions += len(cards_found)
                redaction_types.append("credit_card")
                logger.debug(f"Redacted {len(cards_found)} credit card(s)")

        return SanitizationResult(
            sanitized_value=sanitized,
            redactions_made=redactions,
            redaction_types=redaction_types
        )


class CredentialFilter(OutputGuardrail):
    """
    Filter credentials and secrets from outputs.

    Patterns detected:
    - API keys (common formats)
    - AWS credentials
    - JWT tokens
    - Password patterns
    - Private keys
    - OAuth tokens
    """

    name: str = "CredentialFilter"

    # Credential patterns
    PATTERNS = [
        (r'api[_-]?key[_-]?[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', 'api_key'),
        (r'AKIA[0-9A-Z]{16}', 'aws_access_key'),
        (r'aws[_-]?secret[_-]?[=:]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?', 'aws_secret'),
        (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', 'jwt_token'),
        (r'password[_-]?[=:]\s*["\']?([^\s"\']{8,})["\']?', 'password'),
        (r'passwd[_-]?[=:]\s*["\']?([^\s"\']{8,})["\']?', 'password'),
        (r'token[_-]?[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', 'token'),
        (r'-----BEGIN (RSA |DSA )?PRIVATE KEY-----', 'private_key'),
        (r'-----BEGIN OPENSSH PRIVATE KEY-----', 'ssh_key'),
        (r'oauth[_-]?token[_-]?[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', 'oauth_token'),
        (r'gh[pousr]_[A-Za-z0-9_]{36,}', 'github_token'),
        (r'sk_live_[a-zA-Z0-9]{24,}', 'stripe_key'),
        (r'AIza[0-9A-Za-z_\-]{35}', 'google_api_key'),
        (r'SK[a-zA-Z0-9]{32}', 'twilio_key'),
    ]

    def sanitize(self, value: Any) -> SanitizationResult:
        """Filter credentials from value"""
        if not isinstance(value, str):
            return SanitizationResult(sanitized_value=value, redactions_made=0)

        sanitized = value
        redactions = 0
        redaction_types = []

        # Check each credential pattern
        for pattern, cred_type in self.PATTERNS:
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                sanitized = re.sub(pattern, f'[{cred_type.upper()}_REDACTED]', sanitized, flags=re.IGNORECASE)
                redactions += len(matches) if isinstance(matches[0], str) else len(matches)
                if cred_type not in redaction_types:
                    redaction_types.append(cred_type)
                logger.warning(f"Redacted {cred_type} from output")

        return SanitizationResult(
            sanitized_value=sanitized,
            redactions_made=redactions,
            redaction_types=redaction_types
        )


class IPRedactor(OutputGuardrail):
    """
    Redact internal IP addresses and hostnames.

    Patterns redacted:
    - Private IP ranges (10.x, 172.16-31.x, 192.168.x)
    - IPv6 private addresses
    - Internal hostnames
    - MAC addresses (optional)
    """

    name: str = "IPRedactor"

    # IP patterns
    PRIVATE_IP_PATTERNS = [
        r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # 10.x.x.x
        r'\b172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}\b',  # 172.16-31.x.x
        r'\b192\.168\.\d{1,3}\.\d{1,3}\b',  # 192.168.x.x
        r'\b127\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # 127.x.x.x (loopback)
    ]

    IPV6_PRIVATE_PATTERN = r'\bfe80:[0-9a-fA-F:]+\b'  # IPv6 link-local
    MAC_ADDRESS_PATTERN = r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b'

    def __init__(self, redact_private_ips: bool = True, redact_ipv6: bool = True,
                 redact_mac: bool = False):
        self.redact_private_ips = redact_private_ips
        self.redact_ipv6 = redact_ipv6
        self.redact_mac = redact_mac

    def sanitize(self, value: Any) -> SanitizationResult:
        """Redact IPs from value"""
        if not isinstance(value, str):
            return SanitizationResult(sanitized_value=value, redactions_made=0)

        sanitized = value
        redactions = 0
        redaction_types = []

        # Redact private IPs
        if self.redact_private_ips:
            for pattern in self.PRIVATE_IP_PATTERNS:
                ips_found = re.findall(pattern, sanitized)
                if ips_found:
                    sanitized = re.sub(pattern, '[IP_REDACTED]', sanitized)
                    redactions += len(ips_found)
                    if "private_ip" not in redaction_types:
                        redaction_types.append("private_ip")

        # Redact IPv6
        if self.redact_ipv6:
            ipv6_found = re.findall(self.IPV6_PRIVATE_PATTERN, sanitized)
            if ipv6_found:
                sanitized = re.sub(self.IPV6_PRIVATE_PATTERN, '[IPV6_REDACTED]', sanitized)
                redactions += len(ipv6_found)
                redaction_types.append("ipv6")

        # Redact MAC addresses
        if self.redact_mac:
            mac_found = re.findall(self.MAC_ADDRESS_PATTERN, sanitized)
            if mac_found:
                sanitized = re.sub(self.MAC_ADDRESS_PATTERN, '[MAC_REDACTED]', sanitized)
                redactions += len(mac_found)
                redaction_types.append("mac_address")

        if redactions > 0:
            logger.debug(f"Redacted {redactions} IP/MAC address(es)")

        return SanitizationResult(
            sanitized_value=sanitized,
            redactions_made=redactions,
            redaction_types=redaction_types
        )


class PathSanitizer(OutputGuardrail):
    """
    Sanitize sensitive file paths from outputs.

    Patterns sanitized:
    - User home directories
    - System paths
    - Windows paths with usernames
    - Temporary file paths with usernames
    """

    name: str = "PathSanitizer"

    # Path patterns
    PATTERNS = [
        (r'/home/([^/\s]+)', '/home/[USER]'),
        (r'/Users/([^/\s]+)', '/Users/[USER]'),
        (r'C:\\Users\\([^\\]+)', r'C:\\Users\\[USER]'),
        (r'/tmp/([^/\s]+)', '/tmp/[USER]'),
        (r'/var/tmp/([^/\s]+)', '/var/tmp/[USER]'),
    ]

    def __init__(self, sanitize_user_paths: bool = True):
        self.sanitize_user_paths = sanitize_user_paths

    def sanitize(self, value: Any) -> SanitizationResult:
        """Sanitize paths from value"""
        if not isinstance(value, str):
            return SanitizationResult(sanitized_value=value, redactions_made=0)

        if not self.sanitize_user_paths:
            return SanitizationResult(sanitized_value=value, redactions_made=0)

        sanitized = value
        redactions = 0
        redaction_types = []

        # Sanitize each path pattern
        for pattern, replacement in self.PATTERNS:
            matches = re.findall(pattern, sanitized)
            if matches:
                sanitized = re.sub(pattern, replacement, sanitized)
                redactions += len(matches)
                if "user_path" not in redaction_types:
                    redaction_types.append("user_path")

        if redactions > 0:
            logger.debug(f"Sanitized {redactions} user path(s)")

        return SanitizationResult(
            sanitized_value=sanitized,
            redactions_made=redactions,
            redaction_types=redaction_types
        )


# Default output guardrails chain
DEFAULT_OUTPUT_GUARDRAILS = [
    PIIScrubber(),
    CredentialFilter(),
    IPRedactor(redact_private_ips=True, redact_ipv6=False, redact_mac=False),
    PathSanitizer()
]


def sanitize_output(
    value: Any,
    guardrails: Optional[List[OutputGuardrail]] = None
) -> SanitizationResult:
    """
    Sanitize output through guardrail chain.

    Args:
        value: Output value to sanitize
        guardrails: List of guardrails to apply (defaults to DEFAULT_OUTPUT_GUARDRAILS)

    Returns:
        SanitizationResult with sanitized value and redaction summary
    """
    if guardrails is None:
        guardrails = DEFAULT_OUTPUT_GUARDRAILS

    sanitized = value
    total_redactions = 0
    all_redaction_types = []

    # Apply each guardrail in sequence
    for guardrail in guardrails:
        result = guardrail.sanitize(sanitized)
        sanitized = result.sanitized_value
        total_redactions += result.redactions_made
        all_redaction_types.extend(result.redaction_types)

    # Remove duplicates from redaction types
    all_redaction_types = list(set(all_redaction_types))

    return SanitizationResult(
        sanitized_value=sanitized,
        redactions_made=total_redactions,
        redaction_types=all_redaction_types
    )


def sanitize_dict(
    data: Dict[str, Any],
    guardrails: Optional[List[OutputGuardrail]] = None
) -> tuple[Dict[str, Any], int]:
    """
    Recursively sanitize all string values in a dictionary.

    Args:
        data: Dictionary to sanitize
        guardrails: List of guardrails to apply

    Returns:
        Tuple of (sanitized_dict, total_redactions)
    """
    sanitized = {}
    total_redactions = 0

    for key, value in data.items():
        if isinstance(value, str):
            result = sanitize_output(value, guardrails)
            sanitized[key] = result.sanitized_value
            total_redactions += result.redactions_made
        elif isinstance(value, dict):
            sanitized[key], redactions = sanitize_dict(value, guardrails)
            total_redactions += redactions
        elif isinstance(value, list):
            sanitized[key], redactions = sanitize_list(value, guardrails)
            total_redactions += redactions
        else:
            sanitized[key] = value

    return sanitized, total_redactions


def sanitize_list(
    data: List[Any],
    guardrails: Optional[List[OutputGuardrail]] = None
) -> tuple[List[Any], int]:
    """
    Recursively sanitize all string values in a list.

    Args:
        data: List to sanitize
        guardrails: List of guardrails to apply

    Returns:
        Tuple of (sanitized_list, total_redactions)
    """
    sanitized = []
    total_redactions = 0

    for item in data:
        if isinstance(item, str):
            result = sanitize_output(item, guardrails)
            sanitized.append(result.sanitized_value)
            total_redactions += result.redactions_made
        elif isinstance(item, dict):
            sanitized_item, redactions = sanitize_dict(item, guardrails)
            sanitized.append(sanitized_item)
            total_redactions += redactions
        elif isinstance(item, list):
            sanitized_item, redactions = sanitize_list(item, guardrails)
            sanitized.append(sanitized_item)
            total_redactions += redactions
        else:
            sanitized.append(item)

    return sanitized, total_redactions

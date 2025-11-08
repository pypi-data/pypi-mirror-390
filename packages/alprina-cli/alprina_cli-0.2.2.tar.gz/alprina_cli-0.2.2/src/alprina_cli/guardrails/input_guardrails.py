"""
Input Guardrails

Prevent malicious inputs from reaching tools.
Detect and block: SQL injection, command injection, path traversal, XXE, etc.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel
from loguru import logger
import re


class GuardrailResult(BaseModel):
    """Result from guardrail check"""
    passed: bool
    tripwire_triggered: bool = False
    reason: Optional[str] = None
    severity: str = "INFO"  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    sanitized_value: Optional[Any] = None


class InputGuardrail(ABC):
    """
    Base class for input guardrails.

    Context Engineering:
    - Fast checks (< 10ms per validation)
    - Clear pass/fail results
    - Provides sanitized alternatives when possible
    """

    name: str = "InputGuardrail"

    @abstractmethod
    def check(self, value: Any, param_name: str = "") -> GuardrailResult:
        """
        Check if input is safe.

        Args:
            value: Input value to check
            param_name: Name of parameter being checked

        Returns:
            GuardrailResult with pass/fail and optional sanitized value
        """
        raise NotImplementedError


class SQLInjectionGuardrail(InputGuardrail):
    """
    Detect SQL injection attempts.

    Patterns detected:
    - SQL keywords in unexpected places
    - Comment syntax (-- /* */)
    - Union-based injection
    - Boolean-based injection
    - Time-based injection
    """

    name: str = "SQLInjection"

    # Common SQL injection patterns
    SQL_PATTERNS = [
        r"(\bOR\b|\bAND\b)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?",  # OR 1=1
        r";\s*DROP\s+TABLE",  # DROP TABLE
        r";\s*DELETE\s+FROM",  # DELETE FROM
        r";\s*UPDATE\s+\w+\s+SET",  # UPDATE SET
        r"UNION\s+SELECT",  # UNION SELECT
        r"--\s*$",  # SQL comment
        r"/\*.*?\*/",  # Block comment
        r"'\s*OR\s+'",  # ' OR '
        r"'\s*;\s*--",  # '; --
        r"EXEC\s*\(",  # EXEC(
        r"EXECUTE\s*\(",  # EXECUTE(
        r"xp_cmdshell",  # xp_cmdshell
        r"SLEEP\s*\(",  # SLEEP( (time-based)
        r"WAITFOR\s+DELAY",  # WAITFOR DELAY
    ]

    def check(self, value: Any, param_name: str = "") -> GuardrailResult:
        """Check for SQL injection patterns"""
        if not isinstance(value, str):
            return GuardrailResult(passed=True)

        # Empty input check
        if not value.strip():
            return GuardrailResult(passed=True)

        # Check each pattern
        for pattern in self.SQL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"SQL injection detected in {param_name}: {value[:100]}")
                return GuardrailResult(
                    passed=False,
                    tripwire_triggered=True,
                    reason=f"SQL injection pattern detected: {pattern}",
                    severity="CRITICAL"
                )

        return GuardrailResult(passed=True)


class CommandInjectionGuardrail(InputGuardrail):
    """
    Detect command injection attempts.

    Patterns detected:
    - Shell metacharacters (;, |, &, `, $)
    - Command chaining
    - Subshell execution
    - Environment variable injection
    """

    name: str = "CommandInjection"

    DANGEROUS_PATTERNS = [
        r";\s*\w+",  # Command chaining with ;
        r"\|\s*\w+",  # Pipe to command
        r"&&\s*\w+",  # AND command
        r"\|\|\s*\w+",  # OR command
        r"`[^`]+`",  # Backtick command substitution
        r"\$\([^)]+\)",  # $() command substitution
        r">\s*/",  # Redirect to file
        r"<\s*/",  # Read from file
        r"\beval\b",  # eval
        r"\bexec\b",  # exec
        r"\bsystem\b",  # system
        r"/dev/tcp/",  # TCP backdoor
        r"/dev/udp/",  # UDP backdoor
        r"\bwget\b.*http",  # wget download
        r"\bcurl\b.*http",  # curl download
        r"nc\s+-",  # netcat
        r"bash\s+-i",  # Interactive bash
        r"sh\s+-i",  # Interactive sh
        r"python\s+-c",  # Python one-liner
        r"perl\s+-e",  # Perl one-liner
        r"ruby\s+-e",  # Ruby one-liner
    ]

    def check(self, value: Any, param_name: str = "") -> GuardrailResult:
        """Check for command injection patterns"""
        if not isinstance(value, str):
            return GuardrailResult(passed=True)

        # Empty input check
        if not value.strip():
            return GuardrailResult(passed=True)

        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Command injection detected in {param_name}: {value[:100]}")
                return GuardrailResult(
                    passed=False,
                    tripwire_triggered=True,
                    reason=f"Command injection pattern detected: {pattern}",
                    severity="CRITICAL"
                )

        return GuardrailResult(passed=True)


class PathTraversalGuardrail(InputGuardrail):
    """
    Detect path traversal attempts.

    Patterns detected:
    - ../ sequences
    - Absolute paths to sensitive locations
    - URL encoding tricks
    - Windows/Unix path tricks
    """

    name: str = "PathTraversal"

    DANGEROUS_PATTERNS = [
        r"\.\./",  # ../
        r"\.\.",  # ..
        r"%2e%2e",  # URL encoded ..
        r"\.\.\\",  # ..\
        r"\\\.\\",  # \.\
        r"/etc/passwd",  # /etc/passwd
        r"/etc/shadow",  # /etc/shadow
        r"C:\\Windows",  # C:\Windows
        r"C:\\Program Files",  # C:\Program Files
        r"/proc/self",  # /proc/self
        r"/root/",  # /root/
    ]

    # Absolute path patterns for sensitive system locations
    ABSOLUTE_PATH_PATTERNS = [
        r"^/etc/",  # Unix system config
        r"^/root/",  # Root home directory
        r"^/var/",  # System var directory
        r"^/usr/",  # System usr directory (except common public paths)
        r"^/boot/",  # Boot directory
        r"^/sys/",  # System directory
        r"^/proc/",  # Process directory
        r"^C:\\Windows\\",  # Windows directory
        r"^C:\\Program Files\\",  # Program Files
        r"^C:\\Users\\[^\\]+\\AppData\\",  # User app data
        r"^\\\\\.\\",  # Windows device path
    ]

    def check(self, value: Any, param_name: str = "") -> GuardrailResult:
        """Check for path traversal patterns"""
        if not isinstance(value, str):
            return GuardrailResult(passed=True)

        # Empty input check
        if not value.strip():
            return GuardrailResult(passed=True)  # Allow empty, will be handled by validation

        # Normalize path for checking
        normalized = value.replace("\\", "/").lower()

        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                logger.warning(f"Path traversal detected in {param_name}: {value[:100]}")
                return GuardrailResult(
                    passed=False,
                    tripwire_triggered=True,
                    reason=f"Path traversal pattern detected: {pattern}",
                    severity="HIGH"
                )

        # Check absolute path patterns (Unix and Windows)
        original_value = value  # Preserve original case for Windows paths
        for pattern in self.ABSOLUTE_PATH_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE) or re.search(pattern, original_value):
                logger.warning(f"Unauthorized absolute path access in {param_name}: {value[:100]}")
                return GuardrailResult(
                    passed=False,
                    tripwire_triggered=True,
                    reason=f"Unauthorized absolute path access to sensitive location",
                    severity="HIGH"
                )

        return GuardrailResult(passed=True)


class XXEGuardrail(InputGuardrail):
    """
    Detect XML External Entity (XXE) injection.

    Patterns detected:
    - DOCTYPE declarations
    - ENTITY definitions
    - External file references
    - SYSTEM keyword
    """

    name: str = "XXE"

    XXE_PATTERNS = [
        r"<!DOCTYPE[^>]*\[",  # DOCTYPE declaration with [ (entity definition)
        r"<!ENTITY",  # ENTITY definition
        r"SYSTEM\s+['\"]",  # SYSTEM keyword with quote
        r"PUBLIC\s+['\"]",  # PUBLIC keyword with quote
        r"file://",  # File protocol
        r"php://",  # PHP protocol
        r"expect://",  # Expect protocol
        r"data://",  # Data protocol
        r"<!ENTITY[^>]*SYSTEM",  # ENTITY with SYSTEM
        r"<!ENTITY[^>]*%",  # Parameter entity
        r"&[a-zA-Z]+;.*SYSTEM",  # Entity reference with SYSTEM
    ]

    def check(self, value: Any, param_name: str = "") -> GuardrailResult:
        """Check for XXE patterns"""
        if not isinstance(value, str):
            return GuardrailResult(passed=True)

        # Empty input check
        if not value.strip():
            return GuardrailResult(passed=True)

        # Check XXE patterns
        for pattern in self.XXE_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"XXE injection detected in {param_name}: {value[:100]}")
                return GuardrailResult(
                    passed=False,
                    tripwire_triggered=True,
                    reason=f"XXE injection pattern detected: {pattern}",
                    severity="HIGH"
                )

        return GuardrailResult(passed=True)


class LengthGuardrail(InputGuardrail):
    """
    Validate input length to prevent DoS.

    Prevents:
    - Extremely long inputs
    - Resource exhaustion
    """

    name: str = "Length"

    def __init__(self, max_length: int = 10000):
        self.max_length = max_length

    def check(self, value: Any, param_name: str = "") -> GuardrailResult:
        """Check input length"""
        if isinstance(value, str):
            length = len(value)
        elif isinstance(value, (list, dict)):
            length = len(str(value))
        else:
            return GuardrailResult(passed=True)

        if length > self.max_length:
            logger.warning(f"Input too long in {param_name}: {length} > {self.max_length}")
            return GuardrailResult(
                passed=False,
                tripwire_triggered=False,  # Not malicious, just too large
                reason=f"Input exceeds maximum length: {length} > {self.max_length}",
                severity="MEDIUM"
            )

        return GuardrailResult(passed=True)


class TypeGuardrail(InputGuardrail):
    """
    Validate input type.

    Ensures inputs match expected types.
    """

    name: str = "Type"

    def __init__(self, expected_type: type):
        self.expected_type = expected_type

    def check(self, value: Any, param_name: str = "") -> GuardrailResult:
        """Check input type"""
        if not isinstance(value, self.expected_type):
            logger.warning(f"Type mismatch in {param_name}: expected {self.expected_type}, got {type(value)}")
            return GuardrailResult(
                passed=False,
                tripwire_triggered=False,
                reason=f"Type mismatch: expected {self.expected_type.__name__}, got {type(value).__name__}",
                severity="LOW"
            )

        return GuardrailResult(passed=True)


# Default guardrail chain
DEFAULT_INPUT_GUARDRAILS = [
    SQLInjectionGuardrail(),
    CommandInjectionGuardrail(),
    PathTraversalGuardrail(),
    XXEGuardrail(),
    LengthGuardrail(max_length=10000)
]


def validate_input(
    value: Any,
    param_name: str = "",
    guardrails: Optional[list[InputGuardrail]] = None
) -> GuardrailResult:
    """
    Validate input against guardrails.

    Args:
        value: Input value to validate
        param_name: Name of parameter
        guardrails: List of guardrails to check (defaults to DEFAULT_INPUT_GUARDRAILS)

    Returns:
        GuardrailResult - passes only if all guardrails pass
    """
    if guardrails is None:
        guardrails = DEFAULT_INPUT_GUARDRAILS

    for guardrail in guardrails:
        result = guardrail.check(value, param_name)
        if not result.passed:
            logger.error(f"Guardrail {guardrail.name} failed for {param_name}: {result.reason}")
            return result

    return GuardrailResult(passed=True)


def validate_params(params: Dict[str, Any]) -> Dict[str, GuardrailResult]:
    """
    Validate all parameters in a dictionary.

    Args:
        params: Dictionary of parameters to validate

    Returns:
        Dictionary mapping param names to GuardrailResults
    """
    results = {}

    for param_name, value in params.items():
        results[param_name] = validate_input(value, param_name)

    return results

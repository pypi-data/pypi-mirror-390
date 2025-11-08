"""
Alprina CLI Guardrails System

Context Engineering:
- Input validation to prevent injection attacks
- Output sanitization to prevent data leakage
- PII scrubbing for privacy compliance
- Rate limiting and resource protection

Security first, always.
"""

from alprina_cli.guardrails.input_guardrails import (
    GuardrailResult,
    InputGuardrail,
    SQLInjectionGuardrail,
    CommandInjectionGuardrail,
    PathTraversalGuardrail,
    XXEGuardrail,
    LengthGuardrail,
    TypeGuardrail,
    DEFAULT_INPUT_GUARDRAILS,
    validate_input,
    validate_params
)

from alprina_cli.guardrails.output_guardrails import (
    SanitizationResult,
    OutputGuardrail,
    PIIScrubber,
    CredentialFilter,
    IPRedactor,
    PathSanitizer,
    DEFAULT_OUTPUT_GUARDRAILS,
    sanitize_output,
    sanitize_dict,
    sanitize_list
)

__all__ = [
    # Results
    "GuardrailResult",
    "SanitizationResult",
    # Input guardrails
    "InputGuardrail",
    "SQLInjectionGuardrail",
    "CommandInjectionGuardrail",
    "PathTraversalGuardrail",
    "XXEGuardrail",
    "LengthGuardrail",
    "TypeGuardrail",
    "DEFAULT_INPUT_GUARDRAILS",
    "validate_input",
    "validate_params",
    # Output guardrails
    "OutputGuardrail",
    "PIIScrubber",
    "CredentialFilter",
    "IPRedactor",
    "PathSanitizer",
    "DEFAULT_OUTPUT_GUARDRAILS",
    "sanitize_output",
    "sanitize_dict",
    "sanitize_list",
]

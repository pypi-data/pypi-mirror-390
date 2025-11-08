"""
Tests for Output Guardrails

Context: Validates PII scrubbing, credential filtering, and output sanitization.
"""

import pytest
from alprina_cli.guardrails.output_guardrails import (
    PIIScrubber,
    CredentialFilter,
    IPRedactor,
    PathSanitizer,
    sanitize_output,
    sanitize_dict,
    sanitize_list,
    SanitizationResult
)


class TestPIIScrubber:
    """Tests for PII scrubbing"""

    def test_scrub_email(self):
        """Test email scrubbing"""
        scrubber = PIIScrubber()

        result = scrubber.sanitize("Contact me at john.doe@example.com for details")

        assert result.sanitized_value == "Contact me at [EMAIL_REDACTED] for details"
        assert result.redactions_made == 1
        assert "email" in result.redaction_types

    def test_scrub_multiple_emails(self):
        """Test multiple email scrubbing"""
        scrubber = PIIScrubber()

        result = scrubber.sanitize(
            "Emails: alice@example.com, bob@test.org, charlie@demo.net"
        )

        assert "[EMAIL_REDACTED]" in result.sanitized_value
        assert result.redactions_made == 3
        assert "email" in result.redaction_types

    def test_scrub_phone_number(self):
        """Test phone number scrubbing"""
        scrubber = PIIScrubber()

        result = scrubber.sanitize("Call me at 555-123-4567")

        assert result.sanitized_value == "Call me at [PHONE_REDACTED]"
        assert result.redactions_made == 1
        assert "phone" in result.redaction_types

    def test_scrub_phone_formats(self):
        """Test various phone number formats"""
        scrubber = PIIScrubber()

        test_cases = [
            "555-123-4567",
            "(555) 123-4567",
            "5551234567",
            "+1-555-123-4567",
        ]

        for phone in test_cases:
            result = scrubber.sanitize(f"Phone: {phone}")
            assert "[PHONE_REDACTED]" in result.sanitized_value

    def test_scrub_ssn(self):
        """Test SSN scrubbing"""
        scrubber = PIIScrubber()

        result = scrubber.sanitize("SSN: 123-45-6789")

        assert result.sanitized_value == "SSN: [SSN_REDACTED]"
        assert result.redactions_made == 1
        assert "ssn" in result.redaction_types

    def test_scrub_credit_card(self):
        """Test credit card scrubbing"""
        scrubber = PIIScrubber()

        result = scrubber.sanitize("Card: 1234-5678-9012-3456")

        assert result.sanitized_value == "Card: [CREDIT_CARD_REDACTED]"
        assert result.redactions_made == 1
        assert "credit_card" in result.redaction_types

    def test_scrub_credit_card_formats(self):
        """Test various credit card formats"""
        scrubber = PIIScrubber()

        test_cases = [
            "1234-5678-9012-3456",
            "1234 5678 9012 3456",
            "1234567890123456",
        ]

        for card in test_cases:
            result = scrubber.sanitize(f"Card: {card}")
            assert "[CREDIT_CARD_REDACTED]" in result.sanitized_value

    def test_no_pii(self):
        """Test text without PII"""
        scrubber = PIIScrubber()

        result = scrubber.sanitize("This is normal text without any PII")

        assert result.sanitized_value == "This is normal text without any PII"
        assert result.redactions_made == 0
        assert len(result.redaction_types) == 0

    def test_scrub_all_pii_types(self):
        """Test scrubbing all PII types at once"""
        scrubber = PIIScrubber()

        text = """
        Contact: john@example.com
        Phone: 555-123-4567
        SSN: 123-45-6789
        Card: 1234-5678-9012-3456
        """

        result = scrubber.sanitize(text)

        assert "[EMAIL_REDACTED]" in result.sanitized_value
        assert "[PHONE_REDACTED]" in result.sanitized_value
        assert "[SSN_REDACTED]" in result.sanitized_value
        assert "[CREDIT_CARD_REDACTED]" in result.sanitized_value
        assert result.redactions_made == 4

    def test_selective_scrubbing(self):
        """Test selective PII scrubbing"""
        # Only scrub emails, not phones
        scrubber = PIIScrubber(scrub_emails=True, scrub_phones=False)

        result = scrubber.sanitize("Email: test@example.com, Phone: 555-123-4567")

        assert "[EMAIL_REDACTED]" in result.sanitized_value
        assert "555-123-4567" in result.sanitized_value
        assert result.redactions_made == 1

    def test_non_string_input(self):
        """Test non-string input"""
        scrubber = PIIScrubber()

        result = scrubber.sanitize(12345)

        assert result.sanitized_value == 12345
        assert result.redactions_made == 0


class TestCredentialFilter:
    """Tests for credential filtering"""

    def test_filter_api_key(self):
        """Test API key filtering"""
        filter = CredentialFilter()

        result = filter.sanitize("api_key=sk_test_1234567890abcdefghij")

        assert "[API_KEY_REDACTED]" in result.sanitized_value
        assert result.redactions_made > 0
        assert "api_key" in result.redaction_types

    def test_filter_aws_access_key(self):
        """Test AWS access key filtering"""
        filter = CredentialFilter()

        result = filter.sanitize("AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE")

        assert "[AWS_ACCESS_KEY_REDACTED]" in result.sanitized_value
        assert result.redactions_made > 0

    def test_filter_aws_secret(self):
        """Test AWS secret filtering"""
        filter = CredentialFilter()

        result = filter.sanitize("aws_secret=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")

        assert "[AWS_SECRET_REDACTED]" in result.sanitized_value

    def test_filter_jwt_token(self):
        """Test JWT token filtering"""
        filter = CredentialFilter()

        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        result = filter.sanitize(f"Token: {jwt}")

        assert "[JWT_TOKEN_REDACTED]" in result.sanitized_value
        assert "jwt_token" in result.redaction_types

    def test_filter_password(self):
        """Test password filtering"""
        filter = CredentialFilter()

        result = filter.sanitize("password=SuperSecret123!")

        assert "[PASSWORD_REDACTED]" in result.sanitized_value
        assert "password" in result.redaction_types

    def test_filter_github_token(self):
        """Test GitHub token filtering"""
        filter = CredentialFilter()

        # GitHub tokens are typically 40+ characters
        result = filter.sanitize("ghp_1234567890abcdefghijklmnopqrstuvwxyzABCDEF")

        assert "[GITHUB_TOKEN_REDACTED]" in result.sanitized_value

    def test_filter_private_key(self):
        """Test private key filtering"""
        filter = CredentialFilter()

        result = filter.sanitize("-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...")

        assert "[PRIVATE_KEY_REDACTED]" in result.sanitized_value

    def test_filter_multiple_credentials(self):
        """Test filtering multiple credential types"""
        filter = CredentialFilter()

        text = """
        api_key=sk_test_123456789
        password=secret123
        token=ghp_abcdefghijklmnop
        """

        result = filter.sanitize(text)

        assert result.redactions_made > 0
        assert len(result.redaction_types) > 1

    def test_no_credentials(self):
        """Test text without credentials"""
        filter = CredentialFilter()

        result = filter.sanitize("This is normal text without credentials")

        assert result.sanitized_value == "This is normal text without credentials"
        assert result.redactions_made == 0


class TestIPRedactor:
    """Tests for IP address redaction"""

    def test_redact_private_ip_10(self):
        """Test 10.x.x.x redaction"""
        redactor = IPRedactor()

        result = redactor.sanitize("Server at 10.0.0.5 is running")

        assert result.sanitized_value == "Server at [IP_REDACTED] is running"
        assert result.redactions_made == 1
        assert "private_ip" in result.redaction_types

    def test_redact_private_ip_192(self):
        """Test 192.168.x.x redaction"""
        redactor = IPRedactor()

        result = redactor.sanitize("Connect to 192.168.1.100")

        assert result.sanitized_value == "Connect to [IP_REDACTED]"
        assert "private_ip" in result.redaction_types

    def test_redact_private_ip_172(self):
        """Test 172.16-31.x.x redaction"""
        redactor = IPRedactor()

        result = redactor.sanitize("Database at 172.16.0.10")

        assert result.sanitized_value == "Database at [IP_REDACTED]"

    def test_redact_loopback(self):
        """Test loopback address redaction"""
        redactor = IPRedactor()

        result = redactor.sanitize("Localhost 127.0.0.1")

        assert result.sanitized_value == "Localhost [IP_REDACTED]"

    def test_redact_multiple_ips(self):
        """Test multiple IP redaction"""
        redactor = IPRedactor()

        result = redactor.sanitize("Servers: 10.0.0.1, 192.168.1.1, 172.16.0.1")

        assert result.redactions_made == 3
        assert "private_ip" in result.redaction_types

    def test_redact_ipv6(self):
        """Test IPv6 link-local redaction"""
        redactor = IPRedactor(redact_ipv6=True)

        result = redactor.sanitize("IPv6: fe80::1")

        assert "[IPV6_REDACTED]" in result.sanitized_value
        assert "ipv6" in result.redaction_types

    def test_redact_mac_address(self):
        """Test MAC address redaction"""
        redactor = IPRedactor(redact_mac=True)

        result = redactor.sanitize("MAC: 00:1A:2B:3C:4D:5E")

        assert result.sanitized_value == "MAC: [MAC_REDACTED]"
        assert "mac_address" in result.redaction_types

    def test_no_ips(self):
        """Test text without IPs"""
        redactor = IPRedactor()

        result = redactor.sanitize("No IP addresses here")

        assert result.sanitized_value == "No IP addresses here"
        assert result.redactions_made == 0

    def test_selective_redaction(self):
        """Test selective IP redaction"""
        # Don't redact private IPs
        redactor = IPRedactor(redact_private_ips=False)

        result = redactor.sanitize("Server: 10.0.0.1")

        assert "10.0.0.1" in result.sanitized_value
        assert result.redactions_made == 0


class TestPathSanitizer:
    """Tests for path sanitization"""

    def test_sanitize_linux_home(self):
        """Test Linux home directory sanitization"""
        sanitizer = PathSanitizer()

        result = sanitizer.sanitize("Path: /home/alice/documents/file.txt")

        assert result.sanitized_value == "Path: /home/[USER]/documents/file.txt"
        assert result.redactions_made == 1
        assert "user_path" in result.redaction_types

    def test_sanitize_mac_users(self):
        """Test macOS Users directory sanitization"""
        sanitizer = PathSanitizer()

        result = sanitizer.sanitize("Path: /Users/bob/Desktop/secret.txt")

        assert result.sanitized_value == "Path: /Users/[USER]/Desktop/secret.txt"

    def test_sanitize_windows_users(self):
        """Test Windows Users directory sanitization"""
        sanitizer = PathSanitizer()

        result = sanitizer.sanitize(r"Path: C:\Users\charlie\Documents\file.txt")

        assert r"C:\Users\[USER]" in result.sanitized_value

    def test_sanitize_tmp(self):
        """Test /tmp directory sanitization"""
        sanitizer = PathSanitizer()

        result = sanitizer.sanitize("Temp: /tmp/user123/cache")

        assert result.sanitized_value == "Temp: /tmp/[USER]/cache"

    def test_sanitize_multiple_paths(self):
        """Test multiple path sanitization"""
        sanitizer = PathSanitizer()

        text = "/home/alice/file.txt and /Users/bob/file.txt"
        result = sanitizer.sanitize(text)

        assert result.redactions_made == 2
        assert "/home/[USER]" in result.sanitized_value
        assert "/Users/[USER]" in result.sanitized_value

    def test_no_paths(self):
        """Test text without user paths"""
        sanitizer = PathSanitizer()

        result = sanitizer.sanitize("No paths here")

        assert result.sanitized_value == "No paths here"
        assert result.redactions_made == 0

    def test_disabled_sanitization(self):
        """Test disabled path sanitization"""
        sanitizer = PathSanitizer(sanitize_user_paths=False)

        result = sanitizer.sanitize("/home/alice/file.txt")

        assert "/home/alice/file.txt" in result.sanitized_value
        assert result.redactions_made == 0


class TestSanitizeOutput:
    """Tests for sanitize_output function"""

    def test_sanitize_with_all_guardrails(self):
        """Test sanitization with all default guardrails"""
        text = """
        Email: john@example.com
        API Key: api_key=sk_test_1234567890abcdefghijklmnop
        IP: 10.0.0.5
        Path: /home/alice/secret.txt
        """

        result = sanitize_output(text)

        assert "[EMAIL_REDACTED]" in result.sanitized_value
        assert "[API_KEY_REDACTED]" in result.sanitized_value
        assert "[IP_REDACTED]" in result.sanitized_value
        assert "/home/[USER]" in result.sanitized_value
        assert result.redactions_made > 0

    def test_sanitize_clean_text(self):
        """Test sanitization of clean text"""
        text = "This is clean text without sensitive data"

        result = sanitize_output(text)

        assert result.sanitized_value == text
        assert result.redactions_made == 0

    def test_custom_guardrails(self):
        """Test sanitization with custom guardrails"""
        # Only use PII scrubber
        guardrails = [PIIScrubber()]

        text = "Email: test@example.com, API: sk_test_123"
        result = sanitize_output(text, guardrails=guardrails)

        # Email should be redacted
        assert "[EMAIL_REDACTED]" in result.sanitized_value
        # API key should NOT be redacted (not in guardrails)
        assert "sk_test_123" in result.sanitized_value


class TestSanitizeDict:
    """Tests for sanitize_dict function"""

    def test_sanitize_simple_dict(self):
        """Test sanitizing simple dictionary"""
        data = {
            "email": "john@example.com",
            "name": "John Doe"
        }

        sanitized, redactions = sanitize_dict(data)

        assert sanitized["email"] == "[EMAIL_REDACTED]"
        assert sanitized["name"] == "John Doe"
        assert redactions == 1

    def test_sanitize_nested_dict(self):
        """Test sanitizing nested dictionary"""
        data = {
            "user": {
                "email": "alice@example.com",
                "phone": "555-123-4567"
            },
            "server": {
                "ip": "10.0.0.5"
            }
        }

        sanitized, redactions = sanitize_dict(data)

        assert "[EMAIL_REDACTED]" in sanitized["user"]["email"]
        assert "[PHONE_REDACTED]" in sanitized["user"]["phone"]
        assert "[IP_REDACTED]" in sanitized["server"]["ip"]
        assert redactions > 0

    def test_sanitize_dict_with_list(self):
        """Test sanitizing dictionary with list values"""
        data = {
            "emails": ["alice@example.com", "bob@example.com"],
            "name": "Test"
        }

        sanitized, redactions = sanitize_dict(data)

        assert sanitized["emails"][0] == "[EMAIL_REDACTED]"
        assert sanitized["emails"][1] == "[EMAIL_REDACTED]"
        assert redactions == 2

    def test_sanitize_empty_dict(self):
        """Test sanitizing empty dictionary"""
        data = {}

        sanitized, redactions = sanitize_dict(data)

        assert sanitized == {}
        assert redactions == 0

    def test_sanitize_dict_preserves_types(self):
        """Test that sanitization preserves non-string types"""
        data = {
            "count": 42,
            "enabled": True,
            "value": 3.14,
            "email": "test@example.com"
        }

        sanitized, redactions = sanitize_dict(data)

        assert sanitized["count"] == 42
        assert sanitized["enabled"] is True
        assert sanitized["value"] == 3.14
        assert sanitized["email"] == "[EMAIL_REDACTED]"


class TestSanitizeList:
    """Tests for sanitize_list function"""

    def test_sanitize_simple_list(self):
        """Test sanitizing simple list"""
        data = ["alice@example.com", "bob@example.com", "charlie@example.com"]

        sanitized, redactions = sanitize_list(data)

        assert all(item == "[EMAIL_REDACTED]" for item in sanitized)
        assert redactions == 3

    def test_sanitize_mixed_list(self):
        """Test sanitizing list with mixed types"""
        data = ["test@example.com", 123, True, "10.0.0.5"]

        sanitized, redactions = sanitize_list(data)

        assert sanitized[0] == "[EMAIL_REDACTED]"
        assert sanitized[1] == 123
        assert sanitized[2] is True
        assert "[IP_REDACTED]" in sanitized[3]

    def test_sanitize_nested_list(self):
        """Test sanitizing nested list"""
        data = [
            ["alice@example.com", "bob@example.com"],
            ["10.0.0.1", "192.168.1.1"]
        ]

        sanitized, redactions = sanitize_list(data)

        assert sanitized[0][0] == "[EMAIL_REDACTED]"
        assert "[IP_REDACTED]" in sanitized[1][0]
        assert redactions > 0

    def test_sanitize_list_with_dicts(self):
        """Test sanitizing list with dictionary items"""
        data = [
            {"email": "alice@example.com"},
            {"email": "bob@example.com"}
        ]

        sanitized, redactions = sanitize_list(data)

        assert sanitized[0]["email"] == "[EMAIL_REDACTED]"
        assert sanitized[1]["email"] == "[EMAIL_REDACTED]"
        assert redactions == 2

    def test_sanitize_empty_list(self):
        """Test sanitizing empty list"""
        data = []

        sanitized, redactions = sanitize_list(data)

        assert sanitized == []
        assert redactions == 0

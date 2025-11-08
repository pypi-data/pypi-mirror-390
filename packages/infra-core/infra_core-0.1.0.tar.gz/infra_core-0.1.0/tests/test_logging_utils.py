"""Tests for logging utilities."""

from __future__ import annotations

from infra_core.logging_utils import redact_sas_tokens, sanitize_url


def test_sanitize_url_strips_credentials_and_redacts_query() -> None:
    raw = "https://user:pass@example.com:443/path?sig=abc123&foo=bar"
    sanitized = sanitize_url(raw)
    assert "user" not in sanitized and "pass" not in sanitized
    assert "sig=<redacted>" in sanitized
    assert "foo=bar" in sanitized


def test_redact_sas_tokens_in_text() -> None:
    raw = "SharedAccessSignature=abc123&sig=def456&token=xyz"
    redacted = redact_sas_tokens(raw)
    assert "<redacted>" in redacted
    assert "abc123" not in redacted

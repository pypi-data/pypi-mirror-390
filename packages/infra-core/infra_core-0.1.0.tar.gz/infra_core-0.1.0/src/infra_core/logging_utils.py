"""Logging helpers shared across infra_core modules."""

from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_SENSITIVE_QUERY_KEYS = {
    "sig",
    "signature",
    "se",
    "sp",
    "st",
    "sr",
    "spr",
    "sv",
    "skt",
    "ske",
    "sks",
    "skv",
    "token",
    "access_token",
}

_SENSITIVE_TOKEN_PATTERN = re.compile(
    r"(sig|signature|token|access_token)=([^&;\s]+)", re.IGNORECASE
)


def redact_sas_tokens(value: str) -> str:
    """Redact SAS/shared tokens embedded in arbitrary strings for safe logging."""

    def _replace(match: re.Match[str]) -> str:
        return f"{match.group(1)}=<redacted>"

    return _SENSITIVE_TOKEN_PATTERN.sub(_replace, value)


def sanitize_url(url: str) -> str:
    """Return a URL with credentials stripped and sensitive query params redacted."""
    parsed = urlparse(url)
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    query_pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in _SENSITIVE_QUERY_KEYS:
            query_pairs.append((key, "<redacted>"))
        else:
            query_pairs.append((key, value))
    sanitized = parsed._replace(
        netloc=netloc,
        path=parsed.path or "/",
        params="",
        fragment="",
        query=urlencode(query_pairs, doseq=True),
    )
    return redact_sas_tokens(urlunparse(sanitized))

"""Blocking HTTP client with connection pooling and intelligent retries.

Core value: Production-ready synchronous HTTP with automatic connection reuse,
smart retry logic (retries timeouts/5xx, skips DNS/SSL/4xx errors), and bounded
exponential backoff to prevent runaway delays.

Example::

    # Simple usage with automatic retries
    html = fetch("https://example.com")

    # With rate limiting and capped exponential backoff
    html = fetch(
        "https://api.example.com/data",
        delay=1.0,           # Wait before request (rate limiting)
        max_retries=3,       # Retry transient errors up to 3 times
        max_backoff=30.0,    # Cap retry delays at 30s (default: 60s)
    )

    # Custom client with connection pooling
    client = RequestsHttpClient()
    html = fetch("https://example.com", client=client)
    client.close()

The module-level shared client can be reset if needed::

    reset_shared_http_client()
"""

from __future__ import annotations

import logging
import time
from typing import Callable, Dict, Iterable, Set

import requests

from .retry import (
    AsyncRetryConfig,
    RetryCallState,
    retry_state_summary,
    run_with_retries_sync,
    should_retry_requests_exception,
)

logger = logging.getLogger(__name__)

DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

DEFAULT_RETRY_STATUSES: Set[int] = {429, 500, 502, 503, 504}


class RequestsHttpClient:
    """Manages a requests.Session with connection pooling and context management."""

    def __init__(
        self, *, session_factory: Callable[[], requests.Session] | None = None
    ) -> None:
        """Initialise the client with an optional session factory."""
        self._session_factory = session_factory or requests.Session
        self._session = self._session_factory()

    def __enter__(self) -> RequestsHttpClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying session."""
        self._session.close()

    def reconfigure(
        self, *, session_factory: Callable[[], requests.Session] | None = None
    ) -> None:
        """Recreate the session with new configuration."""
        self.close()
        if session_factory is not None:
            self._session_factory = session_factory
        self._session = self._session_factory()

    def get(
        self, url: str, *, headers: Dict[str, str], timeout: int
    ) -> requests.Response:
        """Execute a GET request using the managed session."""
        return self._session.get(url, headers=headers, timeout=timeout)


_SHARED_CLIENT = RequestsHttpClient()


def get_shared_http_client() -> RequestsHttpClient:
    """Return the module-level RequestsHttpClient singleton."""
    return _SHARED_CLIENT


def set_shared_http_client(client: RequestsHttpClient) -> None:
    """Replace the module-level RequestsHttpClient singleton."""
    global _SHARED_CLIENT
    if _SHARED_CLIENT is not client:
        _dispose_http_client(_SHARED_CLIENT)
    _SHARED_CLIENT = client


def reset_shared_http_client(
    *, session_factory: Callable[[], requests.Session] | None = None
) -> None:
    """Reset the shared RequestsHttpClient."""
    set_shared_http_client(RequestsHttpClient(session_factory=session_factory))


def _should_retry_requests_transport_error(exc: Exception) -> bool:
    non_retryable = (requests.URLRequired, requests.TooManyRedirects)
    return not isinstance(exc, non_retryable)


def _dispose_http_client(client: RequestsHttpClient) -> None:
    try:
        client.close()
    except Exception:  # pragma: no cover - defensive cleanup
        logger.debug("Failed to dispose RequestsHttpClient", exc_info=True)


def fetch(
    url: str,
    *,
    headers: Dict[str, str] | None = None,
    timeout: int = 30,
    delay: float = 0.0,
    max_retries: int = 2,
    backoff: float = 1.0,
    max_backoff: float = 60.0,
    retry_statuses: Iterable[int] | None = None,
    client: RequestsHttpClient | None = None,
) -> str:
    """Fetch the given URL synchronously and return the response body as text.

    Automatically retries on transient errors (timeouts, retryable HTTP status
    codes) while skipping permanent failures (4xx). Uses exponential backoff
    with a configurable cap to prevent runaway delays.
    """

    if delay > 0:
        logger.debug("Respecting rate limit", extra={"url": url, "delay": delay})
        time.sleep(delay)

    merged_headers = DEFAULT_HEADERS.copy()
    if headers:
        merged_headers.update(headers)

    session = client or get_shared_http_client()
    retryable_statuses = (
        set(retry_statuses) if retry_statuses is not None else DEFAULT_RETRY_STATUSES
    )
    attempt_counter = 0

    def _request() -> requests.Response:
        nonlocal attempt_counter
        attempt_counter += 1
        logger.debug(
            "Fetching URL",
            extra={"url": url, "attempt": attempt_counter, "timeout": timeout},
        )
        response = session.get(url, headers=merged_headers, timeout=timeout)
        response.raise_for_status()
        return response

    policy = AsyncRetryConfig.create(
        max_retries=max_retries, backoff=backoff, max_backoff=max_backoff
    )

    def _should_retry(exc: BaseException) -> bool:
        return should_retry_requests_exception(
            exc,
            retryable_statuses=retryable_statuses,
            transport_predicate=_should_retry_requests_transport_error,
        )

    def _before_sleep(state: RetryCallState) -> None:
        exc, wait_time, status_code = retry_state_summary(state)
        logger.warning(
            "Fetch retry scheduled",
            extra={
                "url": url,
                "attempt": state.attempt_number,
                "wait": wait_time,
                "status": status_code,
            },
            exc_info=True,
        )

    try:
        response = run_with_retries_sync(
            _request,
            config=policy,
            should_retry=_should_retry,
            before_sleep=_before_sleep,
        )
    except requests.RequestException as exc:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        logger.error(
            "Fetch failed",
            extra={"url": url, "attempts": attempt_counter, "status": status_code},
            exc_info=True,
        )
        raise

    body: str = response.text
    return body

"""Async HTTP client with connection pooling and intelligent retries.

Core value: Production-ready async HTTP with automatic connection reuse, smart
retry logic (retries timeouts/5xx, skips DNS/SSL/4xx errors), and bounded
exponential backoff to prevent runaway delays.

Example::

    # Simple usage with automatic retries
    html = await fetch_async("https://example.com")

    # With rate limiting and capped exponential backoff
    html = await fetch_async(
        "https://api.example.com/data",
        delay=1.0,           # Wait before request (rate limiting)
        max_retries=3,       # Retry transient errors up to 3 times
        max_backoff=30.0,    # Cap retry delays at 30s (default: 60s)
    )

    # Custom client configuration (HTTP/2, connection limits, etc.)
    client = AsyncHttpClient(http2=True, limits=httpx.Limits(max_connections=100))
    html = await fetch_async("https://example.com", client=client)
    await client.close()

The module-level shared client should be cleaned up during shutdown::

    await close_async_http_client()
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Awaitable, Callable, Dict, Iterable, Set, cast

import httpx
from tenacity import RetryCallState

from .retry import (
    AsyncRetryConfig,
    retry_state_summary,
    run_with_retries,
    should_retry_http_exception,
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


@dataclass(frozen=True)
class RetryPolicy:
    """Retry configuration with exponential backoff.

    Attributes:
        max_retries: Maximum number of retry attempts (0 = no retries).
        backoff: Initial delay in seconds, doubles each retry (exponential backoff).
        max_backoff: Maximum delay cap in seconds (prevents unbounded growth).
        retry_statuses: HTTP status codes to retry (defaults to 429, 500, 502, 503, 504).
                        Timeouts and connection errors are always retried.
    """

    max_retries: int = 2
    backoff: float = 1.0
    max_backoff: float = 60.0
    retry_statuses: Iterable[int] | None = None


class AsyncHttpClient:
    """Manages an httpx.AsyncClient with connection pooling and event-loop awareness.

    This class lazily creates a shared httpx client that reuses TCP connections and
    TLS sessions. The internal lock is recreated if the event loop changes, making
    it safe across different asyncio contexts.

    Can be used as a context manager to ensure cleanup::

        async with AsyncHttpClient(http2=True) as client:
            response = await client.get("https://example.com")
        # Client automatically closed on exit

    Args:
        **client_kwargs: Passed to httpx.AsyncClient (e.g., http2=True, limits=...).
    """

    def __init__(self, **client_kwargs: object) -> None:
        self._client_kwargs: dict[str, Any] = self._build_client_kwargs(**client_kwargs)
        self._client: httpx.AsyncClient | None = None
        self._lock: asyncio.Lock | None = None
        self._lock_loop: asyncio.AbstractEventLoop | None = None

    async def __aenter__(self) -> httpx.AsyncClient:
        return await self.get_client()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def get_client(self) -> httpx.AsyncClient:
        """Return (and lazily create) the underlying httpx.AsyncClient."""
        lock = self._get_lock()
        async with lock:
            if self._client is None:
                self._client = httpx.AsyncClient(**cast(Any, self._client_kwargs))
            return self._client

    async def close(self) -> None:
        """Close the underlying client and reset the pool."""
        lock = self._get_lock()
        async with lock:
            if self._client is not None:
                await self._client.aclose()
                self._client = None

    async def reconfigure(self, **client_kwargs: object) -> None:
        """Recreate the client with new configuration."""
        await self.close()
        self._client_kwargs = self._build_client_kwargs(**client_kwargs)

    def _get_lock(self) -> asyncio.Lock:
        loop = asyncio.get_running_loop()
        if self._lock is None or self._lock_loop is not loop:
            self._lock = asyncio.Lock()
            self._lock_loop = loop
        return self._lock

    @staticmethod
    def _build_client_kwargs(**client_kwargs: object) -> Dict[str, Any]:
        base_kwargs: Dict[str, Any] = {"follow_redirects": True}
        base_kwargs.update(client_kwargs)
        return base_kwargs


_ASYNC_HTTP_CLIENT = AsyncHttpClient()
_PENDING_HTTP_CLIENT_DISPOSALS: "set[asyncio.Task[None]]" = set()


def get_shared_http_client() -> AsyncHttpClient:
    """Return the module-level AsyncHttpClient singleton."""
    return _ASYNC_HTTP_CLIENT


def set_shared_http_client(client: AsyncHttpClient) -> None:
    """Replace the module-level AsyncHttpClient singleton."""
    global _ASYNC_HTTP_CLIENT
    if _ASYNC_HTTP_CLIENT is not client:
        _dispose_async_http_client(_ASYNC_HTTP_CLIENT)
    _ASYNC_HTTP_CLIENT = client


def reset_shared_http_client(**client_kwargs: object) -> None:
    """Reset the module-level client to a fresh instance with optional kwargs."""
    set_shared_http_client(AsyncHttpClient(**client_kwargs))


async def fetch_async(
    url: str,
    *,
    headers: Dict[str, str] | None = None,
    timeout: float | httpx.Timeout = 30.0,
    delay: float = 0.0,
    max_retries: int = 2,
    backoff: float = 1.0,
    max_backoff: float = 60.0,
    retry_statuses: Iterable[int] | None = None,
    client: AsyncHttpClient | None = None,
) -> str:
    """Fetch the given URL asynchronously and return the response body as text.

    Automatically retries on transient errors (timeouts, 5xx status codes) but not
    on permanent failures (4xx, DNS errors, SSL errors). Uses exponential backoff
    with configurable cap to prevent runaway delays.

    Args:
        url: URL to fetch.
        headers: Additional headers merged with DEFAULT_HEADERS.
        timeout: Timeout in seconds, or httpx.Timeout for granular control::

            timeout=httpx.Timeout(connect=5.0, read=30.0)

        delay: Seconds to wait **before** request (for rate limiting).
        max_retries: Number of retry attempts (default: 2).
        backoff: Initial retry delay in seconds, doubles each attempt (default: 1.0).
        max_backoff: Maximum retry delay cap in seconds (default: 60.0).
        retry_statuses: HTTP statuses to retry (default: 429, 500, 502, 503, 504).
        client: Custom AsyncHttpClient instead of shared singleton.

    Returns:
        Response body as text.

    Raises:
        httpx.HTTPStatusError: On non-retryable HTTP errors (4xx) or after max retries.
        httpx.InvalidURL: On malformed URLs (not retried).
        httpx.TimeoutException: After max retries exhausted.

    Example::

        # Simple fetch
        html = await fetch_async("https://example.com")

        # With custom retry policy
        html = await fetch_async(
            "https://api.example.com",
            max_retries=5,
            max_backoff=30.0,
            delay=2.0,  # Rate limit: 2s before each request
        )
    """
    merged_headers = DEFAULT_HEADERS.copy()
    if headers:
        merged_headers.update(headers)

    policy = RetryPolicy(
        max_retries=max_retries,
        backoff=backoff,
        max_backoff=max_backoff,
        retry_statuses=retry_statuses,
    )

    async def _request(client: httpx.AsyncClient) -> httpx.Response:
        logger.debug(
            "Fetching URL",
            extra={"url": url, "timeout": timeout},
        )
        timeout_config = (
            timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout)
        )
        response = await client.get(
            url,
            headers=merged_headers,
            timeout=timeout_config,
        )
        response.raise_for_status()
        return response

    manager = client or get_shared_http_client()
    if delay > 0:
        logger.debug("Respecting rate limit", extra={"url": url, "delay": delay})
        await asyncio.sleep(delay)

    http_client = await manager.get_client()
    response = await _perform_with_retries(http_client, _request, url, policy)
    body: str = response.text
    return body


async def close_async_http_client() -> None:
    """Dispose the shared http client (useful in tests or shutdown hooks)."""
    await _ASYNC_HTTP_CLIENT.close()


async def reconfigure_shared_http_client(**client_kwargs: object) -> None:
    """Recreate the shared http client with new configuration."""
    await _ASYNC_HTTP_CLIENT.reconfigure(**client_kwargs)


async def _perform_with_retries(
    client: httpx.AsyncClient,
    request_fn: Callable[[httpx.AsyncClient], Awaitable[httpx.Response]],
    url: str,
    policy: RetryPolicy,
) -> httpx.Response:
    """Execute request with exponential backoff retry logic."""
    retryable_statuses = (
        set(policy.retry_statuses)
        if policy.retry_statuses is not None
        else DEFAULT_RETRY_STATUSES
    )
    config = AsyncRetryConfig.create(
        max_retries=policy.max_retries,
        backoff=policy.backoff,
        max_backoff=policy.max_backoff,
    )
    attempt_counter = 0  # Separate counter for final error logging outside callbacks.

    async def _request_with_count() -> httpx.Response:
        nonlocal attempt_counter
        attempt_counter += 1
        return await request_fn(client)

    def _should_retry(exc: BaseException) -> bool:
        return should_retry_http_exception(
            exc,
            retryable_statuses=retryable_statuses,
            transport_predicate=_should_retry_exception,
        )

    async def _before_sleep(state: RetryCallState) -> None:
        # Share uniform logging with capped wait info before backing off.
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
        return await run_with_retries(
            _request_with_count,
            config=config,
            should_retry=_should_retry,
            before_sleep=_before_sleep,
        )
    except (httpx.HTTPError, httpx.TimeoutException) as exc:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        logger.error(
            "Fetch failed",
            extra={"url": url, "attempts": attempt_counter, "status": status_code},
            exc_info=True,
        )
        add_note = getattr(exc, "add_note", None)
        if callable(add_note):
            add_note(f"Fetch failed for {url} after {attempt_counter} attempts.")
        raise


def _should_retry_exception(exc: Exception) -> bool:
    """Determine if an exception represents a retryable transport error.

    Returns True for transient errors (timeouts, connection resets),
    False for permanent errors (DNS, SSL, invalid URL, decoding).

    Args:
        exc: Exception from httpx request.

    Returns:
        True if exception should trigger retry, False otherwise.
    """
    if isinstance(exc, httpx.TimeoutException):
        return True
    if isinstance(exc, httpx.TransportError):
        non_retryable = (
            httpx.UnsupportedProtocol,
            httpx.InvalidURL,
            httpx.DecodingError,
        )
        return not isinstance(exc, non_retryable)
    return False


def _dispose_async_http_client(client: AsyncHttpClient) -> None:
    async def _close() -> None:
        try:
            await client.close()
        except Exception:  # pragma: no cover - defensive cleanup
            logger.debug("Failed to dispose AsyncHttpClient", exc_info=True)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            asyncio.run(client.close())
        except RuntimeError:
            logger.debug("No running loop to dispose AsyncHttpClient", exc_info=True)
        except Exception:  # pragma: no cover
            logger.debug("Failed to dispose AsyncHttpClient", exc_info=True)
        return

    task = loop.create_task(_close())
    _PENDING_HTTP_CLIENT_DISPOSALS.add(task)

    def _cleanup(finished: asyncio.Task[None]) -> None:
        _PENDING_HTTP_CLIENT_DISPOSALS.discard(finished)

    task.add_done_callback(_cleanup)

"""Async retry utilities with exponential backoff and exception filtering.

Provides reusable retry logic built on tenacity for both async and sync
operations. Intelligently retries transient failures (timeouts, 5xx errors)
while skipping permanent errors (DNS failures, SSL errors, 4xx status codes).

Key features:
- Configurable retry budgets (max_retries, backoff, max_backoff)
- Exception predicates for httpx and requests libraries
- Before-sleep callbacks for logging/telemetry
- Separate async and sync execution paths

Example:
    Retry an async HTTP operation with custom backoff:

    >>> config = AsyncRetryConfig.create(max_retries=3, backoff=2.0)
    >>> result = await run_with_retries(
    ...     operation=lambda: fetch_url("https://api.example.com"),
    ...     config=config,
    ...     should_retry=lambda exc: should_retry_http_exception(
    ...         exc,
    ...         retryable_statuses=[429, 500, 502, 503],
    ...         transport_predicate=lambda e: True,
    ...     ),
    ... )

Used by http_async.py, asset_client.py, and other infra_core modules.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, Iterable, TypeVar

import httpx
import requests
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

__all__ = [
    "AsyncRetryConfig",
    "RetryCallState",
    "run_with_retries",
    "run_with_retries_sync",
    "should_retry_http_exception",
    "should_retry_requests_exception",
    "retry_state_summary",
]


def retry_state_summary(
    state: RetryCallState,
) -> tuple[BaseException | None, float | None, int | None]:
    """Return (exception, wait_time, status_code) for a tenacity retry state."""
    outcome = state.outcome
    exc = outcome.exception() if outcome is not None else None
    wait_time = state.next_action.sleep if state.next_action is not None else None
    status_code = (
        getattr(getattr(exc, "response", None), "status_code", None) if exc else None
    )
    return exc, wait_time, status_code


T = TypeVar("T")


@dataclass(frozen=True)
class AsyncRetryConfig:
    """Retry policy configuration with exponential backoff.

    Controls retry behavior with bounded exponential backoff. Immutable to
    prevent accidental modification during retry operations.

    Attributes:
        max_retries: Maximum number of retry attempts after initial try.
            0 means no retries (fail on first error). Defaults to 2.
        backoff: Initial delay in seconds before first retry. Doubles each
            subsequent retry. Must be positive. Defaults to 1.0.
        max_backoff: Maximum delay cap in seconds to prevent unbounded growth.
            Must be positive. Defaults to 60.0.
    """

    max_retries: int = 2
    backoff: float = 1.0
    max_backoff: float = 60.0

    @classmethod
    def create(
        cls,
        *,
        max_retries: int = 2,
        backoff: float = 1.0,
        max_backoff: float = 60.0,
    ) -> "AsyncRetryConfig":
        """Create validated retry configuration.

        Args:
            max_retries: Maximum retry attempts. Must be non-negative.
                Defaults to 2.
            backoff: Initial delay in seconds. Must be positive. Defaults to 1.0.
            max_backoff: Maximum delay cap in seconds. Must be positive.
                Defaults to 60.0.

        Returns:
            Validated AsyncRetryConfig instance.

        Raises:
            ValueError: When max_retries is negative or backoff/max_backoff
                are not positive.

        Example:
            >>> config = AsyncRetryConfig.create(max_retries=3, backoff=2.0)
            >>> print(config.max_attempts)
            4
        """
        if max_retries < 0:
            raise ValueError(f"max_retries must be non-negative, got {max_retries}")
        if backoff <= 0:
            raise ValueError(f"backoff must be positive, got {backoff}")
        if max_backoff <= 0:
            raise ValueError(f"max_backoff must be positive, got {max_backoff}")
        return cls(max_retries=max_retries, backoff=backoff, max_backoff=max_backoff)

    @property
    def max_attempts(self) -> int:
        """Total attempts including the initial try.

        Returns:
            max_retries + 1 (initial attempt plus retries).
        """
        return self.max_retries + 1


async def run_with_retries(
    operation: Callable[[], Awaitable[T]],
    *,
    config: AsyncRetryConfig,
    should_retry: Callable[[BaseException], bool],
    before_sleep: Callable[[RetryCallState], Awaitable[None]] | None = None,
) -> T:
    """Execute async operation with tenacity-powered retries and exponential backoff.

    Retries operation according to config policy, consulting should_retry predicate
    for each exception. Implements bounded exponential backoff to prevent retry storms.
    Operation must be idempotent since it may execute multiple times.

    Args:
        operation: Async callable to execute. Must be idempotent (safe to call
            multiple times) since retries will re-execute it.
        config: Retry policy describing attempt budget and exponential backoff
            parameters (max_retries, backoff, max_backoff).
        should_retry: Predicate deciding if raised exception is retryable.
            Returns True to retry (if budget allows), False to propagate exception
            immediately even if retries remain.
        before_sleep: Optional async callback invoked before each retry delay.
            Receives RetryCallState with attempt number, exception info, and
            next sleep duration. Useful for logging or cleanup hooks.

    Returns:
        The successful result of operation when it completes without raising.

    Raises:
        The exception raised by operation when should_retry returns False or
        when the retry budget is exhausted.

    Example:
        >>> async def fetch_data():
        ...     # Might timeout or return 503
        ...     return await httpx_client.get("https://api.example.com/data")
        >>> config = AsyncRetryConfig.create(max_retries=3)
        >>> result = await run_with_retries(
        ...     operation=fetch_data,
        ...     config=config,
        ...     should_retry=lambda e: isinstance(e, httpx.TimeoutException),
        ... )
    """
    retrying = AsyncRetrying(
        reraise=True,
        stop=stop_after_attempt(config.max_attempts),
        wait=wait_exponential(multiplier=config.backoff, max=config.max_backoff),
        retry=retry_if_exception(should_retry),
        before_sleep=before_sleep,
    )

    async for attempt in retrying:
        with attempt:
            return await operation()
    raise AssertionError("retry loop should always return or raise")


def run_with_retries_sync(
    operation: Callable[[], T],
    *,
    config: AsyncRetryConfig,
    should_retry: Callable[[BaseException], bool],
    before_sleep: Callable[[RetryCallState], None] | None = None,
) -> T:
    """Execute sync operation with tenacity-powered retries (sync variant).

    Synchronous version of run_with_retries with identical retry logic.
    Use for sync operations (requests library, file I/O) instead of async.

    Args:
        operation: Sync callable to execute. Must be idempotent since retries
            will re-execute it.
        config: Retry policy describing attempt budget and exponential backoff.
        should_retry: Predicate deciding if raised exception is retryable.
        before_sleep: Optional sync callback invoked before each retry delay.

    Returns:
        The successful result of operation when it completes without raising.

    Raises:
        The exception raised by operation when should_retry returns False or
        when the retry budget is exhausted.

    Example:
        >>> import requests
        >>> def fetch_data():
        ...     return requests.get("https://api.example.com/data", timeout=10)
        >>> config = AsyncRetryConfig.create(max_retries=3)
        >>> response = run_with_retries_sync(
        ...     operation=fetch_data,
        ...     config=config,
        ...     should_retry=lambda e: isinstance(e, requests.Timeout),
        ... )
    """
    retrying = Retrying(
        reraise=True,
        stop=stop_after_attempt(config.max_attempts),
        wait=wait_exponential(multiplier=config.backoff, max=config.max_backoff),
        retry=retry_if_exception(should_retry),
        before_sleep=before_sleep,
    )
    for attempt in retrying:
        with attempt:
            return operation()
    raise AssertionError("retry loop should always return or raise")


def should_retry_http_exception(
    exc: BaseException,
    *,
    retryable_statuses: Iterable[int],
    transport_predicate: Callable[[Exception], bool],
) -> bool:
    """Determine if httpx exception should trigger retry.

    Implements intelligent retry logic for httpx: always retry timeouts, check
    HTTP status codes against retryable list, and consult transport predicate
    for connection errors. Never retries asyncio.CancelledError.

    Args:
        exc: Exception raised by httpx operation.
        retryable_statuses: HTTP status codes to retry (e.g., [429, 500, 502, 503]).
        transport_predicate: Callable deciding if transport-level exception
            (connection errors, DNS failures) should be retried. Return True
            to retry, False to propagate immediately.

    Returns:
        True when exception should trigger retry (if budget allows),
        False to propagate immediately.

    Example:
        >>> predicate = lambda exc: should_retry_http_exception(
        ...     exc,
        ...     retryable_statuses=[429, 500, 502, 503],
        ...     transport_predicate=lambda e: not isinstance(e, httpx.ConnectError),
        ... )
    """
    status_set = set(retryable_statuses)
    if isinstance(exc, asyncio.CancelledError):
        return False
    if isinstance(exc, httpx.TimeoutException):
        return True
    if isinstance(exc, httpx.HTTPError):
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        if status_code is not None:
            return status_code in status_set
        return transport_predicate(exc)
    return False


def should_retry_requests_exception(
    exc: BaseException,
    *,
    retryable_statuses: Iterable[int],
    transport_predicate: Callable[[Exception], bool],
) -> bool:
    """Determine if requests library exception should trigger retry.

    Implements intelligent retry logic for requests: always retry timeouts,
    check HTTP status codes against retryable list, and consult transport
    predicate for connection errors.

    Args:
        exc: Exception raised by requests operation.
        retryable_statuses: HTTP status codes to retry (e.g., [429, 500, 502, 503]).
        transport_predicate: Callable deciding if transport-level exception
            (connection errors, DNS failures) should be retried.

    Returns:
        True when exception should trigger retry (if budget allows),
        False to propagate immediately.

    Example:
        >>> predicate = lambda exc: should_retry_requests_exception(
        ...     exc,
        ...     retryable_statuses=[429, 500, 502, 503],
        ...     transport_predicate=lambda e: True,
        ... )
    """
    if isinstance(exc, requests.Timeout):
        return True
    if isinstance(exc, requests.RequestException):
        response = getattr(exc, "response", None)
        if response is not None and getattr(response, "status_code", None) is not None:
            return response.status_code in set(retryable_statuses)
        return transport_predicate(exc)
    return False

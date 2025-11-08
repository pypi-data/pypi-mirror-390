"""Async asset download client with retries, connection pooling, and bounded backoff.

This module provides production-ready asset downloading with:

- Automatic retry logic for transient failures (timeouts, 5xx errors) while
  skipping permanent errors (DNS failures, SSL errors, 4xx status codes).
- Shared HTTP connection pooling via a lazily-created httpx.AsyncClient that
  reuses TCP connections and TLS sessions across downloads.
- Bounded exponential backoff to prevent runaway retry delays.
- SHA-256 checksumming and efficient file reuse when assets already exist.

Use the module-level helpers for convenience, or instantiate AssetDownloadClient
directly for custom configuration and connection reuse::

    # Simple download with automatic retries and checksum
    from pathlib import Path

    result = await download_asset_async(
        "https://example.com/logo.png",
        Path("downloads/logo.png"),
        skip_if_exists=True,     # Reuse existing files
        compute_checksum=True,   # SHA-256 checksum
    )
    print(f"Downloaded: {result.path}, checksum: {result.checksum}")

    # Custom retry policy with bounded backoff
    result = await download_asset_async(
        "https://cdn.example.com/asset.jpg",
        Path("asset.jpg"),
        max_retries=5,       # Retry transient errors up to 5 times
        backoff=2.0,         # Start with 2s delay, doubles each retry
        max_backoff=30.0,    # Cap retry delays at 30s
    )

    # Long-lived client for multiple downloads (better connection reuse)
    async with AssetDownloadClient(user_agent="MyCrawler/1.0") as client:
        for url, path in download_queue:
            result = await client.download(url, path)
            print(f"Downloaded {result.path}")
    # Client automatically closed on exit

The module-level shared client should be cleaned up during shutdown::

    await reset_shared_client()
"""

from __future__ import annotations

import asyncio
import logging
import mimetypes
import warnings
import errno
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Iterable

import httpx
from tenacity import RetryCallState

from .http import DEFAULT_RETRY_STATUSES
from .logging_utils import sanitize_url
from .retry import (
    AsyncRetryConfig,
    retry_state_summary,
    run_with_retries,
    should_retry_http_exception,
)
from .fs_utils import compute_checksum as _compute_checksum

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DownloadResult:
    """Metadata returned after downloading an asset to disk.

    Attributes:
        path: Filesystem path of the downloaded asset.
        checksum: Checksum in format "algorithm:hexdigest" (e.g., "sha256:abc123...").
                  None if compute_checksum=False.
        mime: Best-effort MIME type guessed from the filename extension.
        reused: True when skip_if_exists=True and the file already existed.
    """

    path: Path
    checksum: str | None = None
    mime: str | None = None
    reused: bool = False


@dataclass(slots=True)
class _RetryConfig:
    """Normalized retry configuration shared between client and overrides."""

    timeout: float
    max_retries: int
    backoff: float
    max_backoff: float
    retry_statuses: frozenset[int]

    @classmethod
    def from_values(
        cls,
        *,
        timeout: float,
        max_retries: int,
        backoff: float,
        max_backoff: float,
        retry_statuses: Iterable[int] | None,
    ) -> _RetryConfig:
        timeout = cls._require_positive(float(timeout), "timeout")
        retry_config = AsyncRetryConfig.create(
            max_retries=int(max_retries),
            backoff=float(backoff),
            max_backoff=float(max_backoff),
        )
        statuses = frozenset(retry_statuses or DEFAULT_RETRY_STATUSES)
        return cls(
            timeout=timeout,
            max_retries=retry_config.max_retries,
            backoff=retry_config.backoff,
            max_backoff=retry_config.max_backoff,
            retry_statuses=statuses,
        )

    def derive(
        self,
        *,
        timeout: float | None = None,
        max_retries: int | None = None,
        backoff: float | None = None,
        max_backoff: float | None = None,
        retry_statuses: Iterable[int] | None = None,
    ) -> _RetryConfig:
        return _RetryConfig.from_values(
            timeout=self.timeout if timeout is None else timeout,
            max_retries=self.max_retries if max_retries is None else max_retries,
            backoff=self.backoff if backoff is None else backoff,
            max_backoff=self.max_backoff if max_backoff is None else max_backoff,
            retry_statuses=self.retry_statuses
            if retry_statuses is None
            else retry_statuses,
        )

    def as_async_retry_config(self) -> AsyncRetryConfig:
        return AsyncRetryConfig.create(
            max_retries=self.max_retries,
            backoff=self.backoff,
            max_backoff=self.max_backoff,
        )

    @staticmethod
    def _require_positive(value: float, name: str) -> float:
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")
        return value

    @staticmethod
    def _require_non_negative(value: int, name: str) -> int:
        if value < 0:
            raise ValueError(f"{name} must be non-negative, got {value}")
        return value


class AssetDownloadClient:
    """Download assets with retries, connection pooling, and bounded backoff.

    The client lazily creates a single ``httpx.AsyncClient`` that is reused across
    downloads for connection pooling. The internal lock is recreated if the event
    loop changes, making it safe across different asyncio contexts.

    Can be used as a context manager to ensure cleanup::

        async with AssetDownloadClient(user_agent="Crawler/1.0") as client:
            result = await client.download(
                "https://example.com/logo.png",
                Path("logo.png"),
                compute_checksum=True
            )
            print(f"{result.path}: {result.checksum}")
        # Client automatically closed on exit

    Or managed explicitly for long-lived usage::

        client = AssetDownloadClient(timeout=30.0, max_retries=5)
        try:
            for url, dest in download_jobs:
                result = await client.download(url, dest)
        finally:
            await client.close()

    Args:
        timeout: Default request timeout in seconds (must be > 0).
        max_retries: Maximum retry attempts after first failure (must be >= 0).
        backoff: Exponential backoff multiplier in seconds (must be > 0).
        max_backoff: Upper bound on retry delays in seconds (must be > 0).
        retry_statuses: HTTP status codes to retry (defaults to 429, 500, 502, 503, 504).
        user_agent: Optional User-Agent header for all requests.
    """

    def __init__(
        self,
        *,
        timeout: float = 60.0,
        max_retries: int = 4,
        backoff: float = 1.5,
        max_backoff: float = 60.0,
        retry_statuses: Iterable[int] | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Initialise the client with retry/backoff policy and optional headers.

        Args:
            timeout: Default request timeout in seconds applied to each download.
            max_retries: Maximum number of retry attempts after the first failure.
            backoff: Exponential backoff multiplier (in seconds) between retries.
            max_backoff: Upper bound (seconds) applied to exponential backoff delays.
            retry_statuses: HTTP status codes that should trigger a retry; defaults
                to ``infra_core.http.DEFAULT_RETRY_STATUSES`` when omitted.
            user_agent: Optional User-Agent header to include with all requests.
        """
        self._base_config = _RetryConfig.from_values(
            timeout=timeout,
            max_retries=max_retries,
            backoff=backoff,
            max_backoff=max_backoff,
            retry_statuses=retry_statuses,
        )
        self._client: httpx.AsyncClient | None = None
        self._client_lock: asyncio.Lock | None = None
        self._client_lock_loop: asyncio.AbstractEventLoop | None = None
        self._user_agent = user_agent

    async def __aenter__(self) -> AssetDownloadClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def _get_client(self) -> httpx.AsyncClient:
        """Return the shared httpx client, creating it lazily if required.

        Thread-safe via async lock. Multiple concurrent calls will wait for
        the first to initialize the client, then all share the same instance.

        Returns:
            Shared httpx.AsyncClient with connection pooling enabled.
        """
        lock = self._get_lock()
        async with lock:
            if self._client is None:
                headers = {}
                if self._user_agent:
                    headers["User-Agent"] = self._user_agent
                self._client = httpx.AsyncClient(follow_redirects=True, headers=headers)
            return self._client

    async def close(self) -> None:
        """Close the cached httpx client, allowing resources to be reclaimed."""
        lock = self._get_lock()
        async with lock:
            if self._client is not None:
                await self._client.aclose()
                self._client = None

    def _get_lock(self) -> asyncio.Lock:
        loop = asyncio.get_running_loop()
        if self._client_lock is None or self._client_lock_loop is not loop:
            self._client_lock = asyncio.Lock()
            self._client_lock_loop = loop
        return self._client_lock

    async def download(
        self,
        url: str,
        dest_path: Path,
        *,
        headers: dict[str, str] | None = None,
        skip_if_exists: bool = True,
        compute_checksum: bool = True,
        timeout: float | None = None,
        max_retries: int | None = None,
        backoff: float | None = None,
        max_backoff: float | None = None,
        retry_statuses: Iterable[int] | None = None,
    ) -> DownloadResult:
        """Download ``url`` to ``dest_path`` with retries and checksum support.

        Args:
            url: Remote asset URL to fetch.
            dest_path: Local filesystem path where the asset should be written.
            headers: Optional request headers to merge with the client defaults.
            skip_if_exists: When True, reuse existing files instead of re-downloading.
            compute_checksum: Whether to compute a checksum for the resulting file.
            timeout: Per-request timeout override; falls back to the client default.
            max_retries: Retry budget override; falls back to the client default.
            backoff: Backoff multiplier override; falls back to the client default.
            max_backoff: Maximum retry delay override; falls back to the client default.
            retry_statuses: HTTP status codes that should trigger retry logic; defaults
                to the client configuration.

        Returns:
            DownloadResult describing the stored file.

        Raises:
            httpx.HTTPError: When the request fails without a retryable status code.
            httpx.TimeoutException: When the request times out without retry budget.
        """
        _ensure_parent(dest_path)
        reuse = await self._maybe_reuse_existing_file(
            dest_path, skip_if_exists, compute_checksum
        )
        if reuse:
            return reuse

        client = await self._get_client()
        temp_path = self._create_temp_path(dest_path)
        policy = self._base_config.derive(
            timeout=timeout,
            max_retries=max_retries,
            backoff=backoff,
            max_backoff=max_backoff,
            retry_statuses=retry_statuses,
        )

        retryable_statuses = set(policy.retry_statuses)
        async_config = policy.as_async_retry_config()
        attempt_counter = 0  # Track attempts for logging outside tenacity callbacks.

        safe_url = sanitize_url(url)

        async def _perform_request() -> None:
            nonlocal attempt_counter
            attempt_counter += 1
            logger.debug(
                "Async download started",
                extra={
                    "url": safe_url,
                    "destination": str(dest_path),
                    "attempt": attempt_counter,
                    "timeout": policy.timeout,
                },
            )
            http_timeout = httpx.Timeout(policy.timeout)
            async with client.stream(
                "GET", url, headers=headers, timeout=http_timeout
            ) as response:
                response.raise_for_status()
                await self._stream_response_to_file(response, temp_path)

        def _should_retry(exc: BaseException) -> bool:
            return should_retry_http_exception(
                exc,
                retryable_statuses=retryable_statuses,
                transport_predicate=_should_retry_exception,
            )

        async def _before_sleep(state: RetryCallState) -> None:
            # Remove any partial file before the next attempt so we always write from scratch.
            self._cleanup_partial_file(temp_path, reason="retry")
            exc, wait_time, status_code = retry_state_summary(state)
            logger.warning(
                "Async download retry scheduled",
                extra={
                    "url": safe_url,
                    "destination": str(dest_path),
                    "attempt": state.attempt_number,
                    "wait": wait_time,
                    "status": status_code,
                },
                exc_info=True,
            )

        try:
            await run_with_retries(
                _perform_request,
                config=async_config,
                should_retry=_should_retry,
                before_sleep=_before_sleep,
            )
            self._finalize_download(temp_path, dest_path)
        except asyncio.CancelledError:
            # Downloads cancelled mid-stream still drop disk state.
            self._cleanup_partial_file(temp_path, reason="cancelled")
            logger.debug(
                "Async download cancelled",
                extra={
                    "url": safe_url,
                    "destination": str(dest_path),
                    "attempt": attempt_counter,
                },
            )
            raise
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            # All retries exhausted—cleanup before surfacing the failure.
            self._cleanup_partial_file(temp_path, reason="failure")
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            logger.error(
                "Async download failed",
                extra={
                    "url": safe_url,
                    "destination": str(dest_path),
                    "attempts": attempt_counter,
                    "status": status_code,
                },
                exc_info=True,
            )
            raise
        except Exception:
            # Unexpected failure (disk full, etc.) should still remove the temp file.
            self._cleanup_partial_file(temp_path, reason="failure")
            raise

        checksum = (
            await asyncio.to_thread(_compute_checksum, dest_path)
            if compute_checksum
            else None
        )
        mime = mimetypes.guess_type(dest_path.name)[0]
        return DownloadResult(path=dest_path, checksum=checksum, mime=mime)

    async def _maybe_reuse_existing_file(
        self,
        dest_path: Path,
        skip_if_exists: bool,
        compute_checksum: bool,
    ) -> DownloadResult | None:
        if not skip_if_exists or not dest_path.exists():
            return None
        checksum = (
            await asyncio.to_thread(_compute_checksum, dest_path)
            if compute_checksum
            else None
        )
        mime = mimetypes.guess_type(dest_path.name)[0]
        return DownloadResult(path=dest_path, checksum=checksum, mime=mime, reused=True)

    async def _stream_response_to_file(
        self, response: httpx.Response, dest_path: Path
    ) -> None:
        loop = asyncio.get_running_loop()
        with dest_path.open("wb") as handle:
            async for chunk in response.aiter_bytes():
                if chunk:
                    await loop.run_in_executor(None, handle.write, chunk)
            await loop.run_in_executor(None, handle.flush)

    def _cleanup_partial_file(self, dest_path: Path, *, reason: str) -> None:
        if not dest_path.exists():
            return
        try:
            dest_path.unlink(missing_ok=True)
        except OSError:
            logger.warning(
                "Failed to clean up partial file",
                extra={"path": str(dest_path), "reason": reason},
                exc_info=True,
            )

    def _create_temp_path(self, dest_path: Path) -> Path:
        fd, tmp_name = tempfile.mkstemp(
            dir=str(dest_path.parent),
            prefix=f".infra_core.{dest_path.name}.",
            suffix=".tmp",
        )
        os.close(fd)
        return Path(tmp_name)

    def _finalize_download(self, temp_path: Path, dest_path: Path) -> None:
        try:
            temp_path.replace(dest_path)
        except OSError as exc:
            if exc.errno == errno.EXDEV:
                shutil.move(str(temp_path), str(dest_path))
                return
            raise


def _should_retry_exception(exc: Exception) -> bool:
    """Return True for transient transport errors that should be retried.

    Retries timeouts and most transport errors, but skips protocol/URL/decoding
    errors that indicate a permanent problem.

    Args:
        exc: Exception raised during HTTP request.

    Returns:
        True if the error is likely transient and worth retrying.
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


_CLIENT: AssetDownloadClient | None = None
_CLIENT_LOCK: asyncio.Lock | None = None
_CLIENT_LOCK_LOOP: asyncio.AbstractEventLoop | None = None
_PENDING_ASSET_CLIENT_DISPOSALS: "set[asyncio.Task[None]]" = set()


def _get_shared_client_lock() -> asyncio.Lock:
    loop = asyncio.get_running_loop()
    global _CLIENT_LOCK, _CLIENT_LOCK_LOOP
    if _CLIENT_LOCK is None or _CLIENT_LOCK_LOOP is not loop:
        _CLIENT_LOCK = asyncio.Lock()
        _CLIENT_LOCK_LOOP = loop
    return _CLIENT_LOCK


async def get_shared_client() -> AssetDownloadClient:
    """Return the module-level AssetDownloadClient, constructing if needed."""
    global _CLIENT
    lock = _get_shared_client_lock()
    async with lock:
        if _CLIENT is None:
            _CLIENT = AssetDownloadClient()
        return _CLIENT


async def get_async_client() -> AssetDownloadClient:
    """Backward-compatible alias for get_shared_client()."""
    warnings.warn(
        "get_async_client() is deprecated; use get_shared_client() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return await get_shared_client()


def set_shared_client(client: AssetDownloadClient | None) -> None:
    """Replace the module-level AssetDownloadClient singleton (primarily for tests)."""
    global _CLIENT
    previous = _CLIENT
    _CLIENT = client
    if previous is not None and previous is not client:
        _dispose_asset_client(previous)


async def download_asset_async(
    url: str,
    dest_path: Path,
    *,
    headers: dict[str, str] | None = None,
    skip_if_exists: bool = True,
    timeout: float | None = None,
    max_retries: int | None = None,
    backoff: float | None = None,
    max_backoff: float | None = None,
    retry_statuses: Iterable[int] | None = None,
    compute_checksum: bool = True,
) -> DownloadResult:
    """Async helper that proxies to the shared client for convenience.

    Args:
        url: Remote asset URL to fetch.
        dest_path: Local filesystem path where the asset should be written.
        headers: Optional request headers to merge with the client defaults.
        skip_if_exists: When True, reuse existing files instead of re-downloading.
        timeout: Per-request timeout override; falls back to the client default.
        max_retries: Retry budget override; falls back to the client default.
        backoff: Backoff multiplier override; falls back to the client default.
        max_backoff: Maximum retry delay override; falls back to the client default.
        retry_statuses: HTTP status codes that should trigger retry logic; defaults
            to the client configuration.
        compute_checksum: Whether to compute a checksum for the resulting file.

    Returns:
        DownloadResult describing the stored file.
    """
    client = await get_shared_client()
    return await client.download(
        url,
        dest_path,
        headers=headers,
        skip_if_exists=skip_if_exists,
        timeout=timeout,
        max_retries=max_retries,
        backoff=backoff,
        max_backoff=max_backoff,
        retry_statuses=retry_statuses,
        compute_checksum=compute_checksum,
    )


def download_asset(
    url: str,
    dest_path: Path,
    *,
    headers: dict[str, str] | None = None,
    skip_if_exists: bool = True,
    timeout: float | None = None,
    max_retries: int | None = None,
    backoff: float | None = None,
    max_backoff: float | None = None,
    retry_statuses: Iterable[int] | None = None,
    compute_checksum: bool = True,
) -> DownloadResult:
    """Blocking wrapper around ``download_asset_async`` for CLI usage.

    Args:
        url: Remote asset URL to fetch.
        dest_path: Local filesystem path where the asset should be written.
        headers: Optional request headers to merge with the client defaults.
        skip_if_exists: When True, reuse existing files instead of re-downloading.
        timeout: Per-request timeout override; forwarded to the async helper.
        max_retries: Retry budget override; forwarded to the async helper.
        backoff: Backoff multiplier override; forwarded to the async helper.
        max_backoff: Upper bound on retry delays; forwarded to the async helper.
        retry_statuses: HTTP status codes that should trigger retry logic; forwarded
            to the async helper.
        compute_checksum: Whether to compute a checksum for the resulting file.

    Returns:
        DownloadResult describing the stored file.

    Raises:
        RuntimeError: If invoked while an event loop is already running.
        httpx.HTTPError: Propagated from the async helper on non-retryable errors.
        httpx.TimeoutException: Propagated when retries are exhausted.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(
            download_asset_async(
                url,
                dest_path,
                headers=headers,
                skip_if_exists=skip_if_exists,
                timeout=timeout,
                max_retries=max_retries,
                backoff=backoff,
                max_backoff=max_backoff,
                retry_statuses=retry_statuses,
                compute_checksum=compute_checksum,
            )
        )
    # Blocking inside a running loop would hang the event loop, so fail fast.
    raise RuntimeError(
        "download_asset() cannot be used inside a running event loop; use download_asset_async instead",
    )


async def reset_shared_client() -> None:
    """Reset the cached singleton—used primarily in tests to isolate state."""
    global _CLIENT
    lock = _get_shared_client_lock()
    async with lock:
        if _CLIENT is not None:
            await _CLIENT.close()
            _CLIENT = None


async def reset_async_client() -> None:
    """Backward-compatible alias for reset_shared_client()."""
    warnings.warn(
        "reset_async_client() is deprecated; use reset_shared_client() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    await reset_shared_client()


def _ensure_parent(path: Path) -> None:
    """Ensure the parent directory of ``path`` exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def _dispose_asset_client(client: AssetDownloadClient) -> None:
    async def _close() -> None:
        try:
            await client.close()
        except Exception:  # pragma: no cover - defensive cleanup
            logger.debug("Failed to dispose AssetDownloadClient", exc_info=True)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            asyncio.run(client.close())
        except RuntimeError:
            logger.debug(
                "No running loop to dispose AssetDownloadClient", exc_info=True
            )
        except Exception:  # pragma: no cover
            logger.debug("Failed to dispose AssetDownloadClient", exc_info=True)
        return

    task = loop.create_task(_close())
    _PENDING_ASSET_CLIENT_DISPOSALS.add(task)

    def _cleanup(completed: asyncio.Task[None]) -> None:
        _PENDING_ASSET_CLIENT_DISPOSALS.discard(completed)

    task.add_done_callback(_cleanup)

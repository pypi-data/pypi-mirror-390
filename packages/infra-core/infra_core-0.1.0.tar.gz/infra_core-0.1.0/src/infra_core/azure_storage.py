"""Opinionated Azure Blob Storage helpers shared across infra_core.

This module layers on top of the official Azure SDK to provide:

- Configuration glue (`AzureStorageSettings.from_env`) so every package reads
  container/connection-string/prefix env vars the same way.
- Cached `AzureStorageClient` instances (sync + async) with proper disposal of
  service clients and credentials via `close()` / `aclose()`.
- Thin module-level helpers (`upload_text`, `download_tree_async`, etc.) that
  delegate to the shared client for legacy callers.
- Centralised logging/skip behaviour when storage is disabled, plus prefix
  resolution and screenshot defaults.

Use `get_client(settings=...)` when you need long-lived control, or call the
module helpers for convenience; both paths share the same cached client.
"""

from __future__ import annotations

import asyncio
import errno
import inspect
import json
import logging
import os
import shutil
import tempfile
from collections.abc import AsyncIterable, Iterable
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from types import TracebackType
from typing import Any, Dict, List, Mapping, Protocol, Tuple, runtime_checkable

from azure.core.exceptions import AzureError, ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.storage.blob.aio import (
    BlobServiceClient as AsyncBlobServiceClient,
    ContainerClient as AsyncContainerClient,
)

from .logging_utils import sanitize_url


@runtime_checkable
class StorageBackend(Protocol):
    def ensure_parent(self, path: Path) -> None: ...

    def write_json(self, path: Path, data: Mapping[str, Any]) -> Path: ...

    def write_text(self, path: Path, text: str) -> Path: ...

    def upload_file(self, path: Path) -> None: ...


logger = logging.getLogger(__name__)

_CONNECTION_STRING_ENV = "AZURE_STORAGE_CONNECTION_STRING"
_CONTAINER_ENV = "AZURE_STORAGE_CONTAINER"
_PREFIX_ENV = "AZURE_STORAGE_BLOB_PREFIX"
_ACCOUNT_ENV = "AZURE_STORAGE_ACCOUNT"
_ENDPOINT_ENV = "AZURE_STORAGE_BLOB_ENDPOINT"


def _blob_name_for_path(path: Path, *, prefix: str | None = None) -> str:
    """Normalise a filesystem path into a blob-compatible name."""

    blob = path.as_posix().lstrip("/")
    if prefix:
        prefix = prefix.rstrip("/")
        return f"{prefix}/{blob}" if blob else prefix
    return blob


@dataclass(frozen=True)
class AzureStorageSettings:
    """Configuration for Azure Blob Storage from environment variables.

    Either connection_string OR (account_name + blob_endpoint) must be provided.

    Attributes:
        container: Azure storage container name (required).
        connection_string: Full connection string (recommended for local dev).
        account_name: Storage account name (for production with managed identity).
        blob_endpoint: Custom blob endpoint URL (optional, auto-generated from account_name).
        prefix: Blob name prefix for all operations (e.g., "screenshots/").
    """

    container: str | None
    connection_string: str | None = None
    account_name: str | None = None
    blob_endpoint: str | None = None
    prefix: str | None = None

    @classmethod
    def from_env(
        cls,
        *,
        container_var: str = _CONTAINER_ENV,
        connection_string_var: str = _CONNECTION_STRING_ENV,
        account_var: str = _ACCOUNT_ENV,
        endpoint_var: str = _ENDPOINT_ENV,
        prefix_var: str = _PREFIX_ENV,
        env: Mapping[str, str] = os.environ,
    ) -> "AzureStorageSettings":
        """Load settings from environment variables.

        Args:
            container_var: Env var name for container (default: AZURE_STORAGE_CONTAINER).
            connection_string_var: Env var name for connection string.
            account_var: Env var name for account name.
            endpoint_var: Env var name for blob endpoint.
            prefix_var: Env var name for blob prefix.
            env: Environment dict (default: os.environ).

        Returns:
            AzureStorageSettings with values from environment.
            All fields are None if corresponding env vars are empty/missing.
        """
        return cls(
            container=(env.get(container_var) or "").strip() or None,
            connection_string=(env.get(connection_string_var) or "").strip() or None,
            account_name=(env.get(account_var) or "").strip() or None,
            blob_endpoint=(env.get(endpoint_var) or "").strip() or None,
            prefix=(env.get(prefix_var) or "").strip() or None,
        )


@dataclass(frozen=True)
class _AzureStorageConfig:
    """Internal validated config with guaranteed non-None container.

    This is created from AzureStorageSettings only when container is present.
    Separates "settings from env" from "validated config ready to use".
    """

    container: str
    connection_string: str | None = None
    account_name: str | None = None
    blob_endpoint: str | None = None
    prefix: str | None = None

    @classmethod
    def from_settings(
        cls, settings: AzureStorageSettings
    ) -> "_AzureStorageConfig | None":
        if not settings.container:
            return None
        return cls(
            container=settings.container,
            connection_string=settings.connection_string,
            account_name=settings.account_name,
            blob_endpoint=settings.blob_endpoint,
            prefix=settings.prefix,
        )

    def create_service_client(
        self,
    ) -> Tuple[BlobServiceClient, DefaultAzureCredential | None]:
        if self.connection_string:
            logger.debug(
                "Creating BlobServiceClient from connection string",
                extra={"container": self.container},
            )
            client = BlobServiceClient.from_connection_string(self.connection_string)
            return client, None

        account_url = self.blob_endpoint
        if not account_url:
            if not self.account_name:
                raise RuntimeError(
                    "Azure storage credentials are not configured. "
                    "Provide connection string or account name/endpoint."
                )
            account_url = f"https://{self.account_name}.blob.core.windows.net"

        credential = DefaultAzureCredential()
        logger.debug(
            "Creating BlobServiceClient for account URL",
            extra={
                "container": self.container,
                "account_url": sanitize_url(account_url),
            },
        )
        client = BlobServiceClient(account_url=account_url, credential=credential)
        return client, credential

    def create_container_client(
        self,
    ) -> Tuple[ContainerClient, BlobServiceClient, DefaultAzureCredential | None]:
        service, credential = self.create_service_client()
        container = service.get_container_client(self.container)
        try:
            container.create_container()
        except ResourceExistsError:
            pass

        return container, service, credential

    def create_async_service_client(
        self,
    ) -> Tuple[AsyncBlobServiceClient, AsyncDefaultAzureCredential | None]:
        if self.connection_string:
            client = AsyncBlobServiceClient.from_connection_string(
                self.connection_string
            )
            logger.debug(
                "Creating AsyncBlobServiceClient from connection string",
                extra={"container": self.container},
            )
            return client, None

        account_url = self.blob_endpoint
        if not account_url:
            if not self.account_name:
                raise RuntimeError(
                    "Azure storage credentials are not configured. "
                    "Provide connection string or account name/endpoint."
                )
            account_url = f"https://{self.account_name}.blob.core.windows.net"

        credential = AsyncDefaultAzureCredential()
        logger.debug(
            "Creating AsyncBlobServiceClient for account URL",
            extra={
                "container": self.container,
                "account_url": sanitize_url(account_url),
            },
        )
        client = AsyncBlobServiceClient(account_url=account_url, credential=credential)
        return client, credential

    def blob_name_for_path(self, path: Path) -> str:
        return _blob_name_for_path(path, prefix=self.prefix)


class AzureStorageClient(StorageBackend):
    """Azure Blob Storage client with sync/async helpers and StorageBackend support.

    Manages lifecycle of Azure SDK clients (BlobServiceClient, ContainerClient)
    and credentials. Lazily creates clients on first use and caches them.

    Supports both sync and async operations. The async client is created
    independently from the sync client and must be closed with aclose().

    Usage::

        # Sync operations
        client = AzureStorageClient(config, settings=settings)
        client.upload_text(Path("test.txt"), "hello")
        client.close()

        # Async operations
        async with client:
            await client.upload_text_async(Path("test.txt"), "hello")
        # Auto-closes on exit

        # Or use context manager for sync
        with AzureStorageClient(config, settings=settings) as client:
            client.upload_text(Path("test.txt"), "hello")

    Args:
        config: Internal validated config (None if storage disabled).
        settings: Original settings from env (for logging/prefix fallback).
    """

    __slots__ = (
        "_config",
        "_settings",
        "_enabled",
        "_swallow_errors",
        "_logger",
        "_service",
        "_credential",
        "_container",
        "_async_service",
        "_async_container",
        "_async_credential",
        "_async_lock",
        "_async_lock_loop",
    )

    def __init__(
        self,
        config: _AzureStorageConfig | None,
        *,
        settings: AzureStorageSettings | None = None,
        enabled: bool | None = None,
        swallow_errors: bool = True,
        log: logging.Logger | None = None,
    ) -> None:
        self._config = config
        self._settings = settings
        self._enabled = enabled
        self._swallow_errors = swallow_errors
        self._logger = log or logger
        self._service: BlobServiceClient | None = None
        self._credential: DefaultAzureCredential | None = None
        self._container: ContainerClient | None = None
        self._async_service: AsyncBlobServiceClient | None = None
        self._async_container: AsyncContainerClient | None = None
        self._async_credential: AsyncDefaultAzureCredential | None = None
        self._async_lock: asyncio.Lock | None = None
        self._async_lock_loop: asyncio.AbstractEventLoop | None = None

    @classmethod
    @classmethod
    def from_settings(
        cls,
        settings: AzureStorageSettings | None = None,
        *,
        enabled: bool | None = None,
        swallow_errors: bool = True,
        log: logging.Logger | None = None,
    ) -> "AzureStorageClient":
        resolved = settings or AzureStorageSettings.from_env()
        config = _AzureStorageConfig.from_settings(resolved)
        return cls(
            config=config,
            settings=resolved,
            enabled=enabled,
            swallow_errors=swallow_errors,
            log=log,
        )

    @property
    def config(self) -> _AzureStorageConfig | None:
        return self._config

    @property
    def settings(self) -> AzureStorageSettings | None:
        return self._settings

    def is_configured(self) -> bool:
        return self._config is not None

    def _current_prefix(self) -> str | None:
        if self._config and self._config.prefix:
            return self._config.prefix
        if self._settings and self._settings.prefix:
            return self._settings.prefix
        return None

    def _log_unconfigured(self, action: str) -> None:
        container = self._settings.container if self._settings else None
        self._logger.debug(
            "Azure storage not configured; skipping action",
            extra={"container": container or "default", "action": action},
        )

    def blob_name_for_path(self, path: Path) -> str:
        prefix = self._current_prefix()
        return _blob_name_for_path(path, prefix=prefix)

    def _should_upload(self) -> bool:
        if self._enabled is not None:
            return self._enabled
        return self.is_configured()

    def _handle_upload_error(self, path: Path, exc: Exception) -> None:
        if self._swallow_errors:
            self._logger.warning(
                "Azure upload failed; retaining local copy",
                extra={
                    "path": str(path),
                    "blob_name": self.blob_name_for_path(path),
                    "error": type(exc).__name__,
                },
                exc_info=True,
            )
        else:
            raise

    def ensure_parent(self, path: Path) -> None:
        """Create parent directories for a path if needed."""
        path.parent.mkdir(parents=True, exist_ok=True)

    def write_text(self, path: Path, text: str) -> Path:
        """Write text locally and mirror to Azure when enabled."""
        self.ensure_parent(path)
        path.write_text(text, encoding="utf-8")
        self.upload_text(path, text)
        return path

    def write_json(self, path: Path, data: Mapping[str, Any]) -> Path:
        """Serialize data as JSON, write locally, and mirror to Azure."""
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        return self.write_text(path, text)

    async def write_text_async(self, path: Path, text: str) -> Path:
        """Async variant of write_text using thread offload for disk I/O."""
        self.ensure_parent(path)
        await asyncio.to_thread(path.write_text, text, encoding="utf-8")
        await self.upload_text_async(path, text)
        return path

    async def write_json_async(self, path: Path, data: Mapping[str, Any]) -> Path:
        """Async JSON writer that mirrors to Azure when enabled."""
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        return await self.write_text_async(path, text)

    def __enter__(self) -> "AzureStorageClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    async def __aenter__(self) -> "AzureStorageClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    def _get_async_lock(self) -> asyncio.Lock:
        """Get or create async lock bound to current event loop."""
        loop = asyncio.get_running_loop()
        if self._async_lock is None or self._async_lock_loop is not loop:
            self._async_lock = asyncio.Lock()
            self._async_lock_loop = loop
        return self._async_lock

    def container(self) -> ContainerClient | None:
        if not self._config:
            return None
        if self._container is None:
            container, service, credential = self._config.create_container_client()
            self._container = container
            self._service = service
            self._credential = credential
        return self._container

    async def container_async(self) -> AsyncContainerClient | None:
        if not self._config:
            return None
        lock = self._get_async_lock()
        async with lock:
            if self._async_service is None:
                service, credential = self._config.create_async_service_client()
                self._async_service = service
                self._async_credential = credential
            if self._async_container is None:
                container_async = self._async_service.get_container_client(
                    self._config.container
                )
                try:
                    await container_async.create_container()
                except ResourceExistsError:
                    pass
                self._async_container = container_async
        return self._async_container

    def upload_text(self, path: Path, text: str) -> None:
        """Upload text content to blob storage.

        Args:
            path: Filesystem path that determines blob name (with prefix applied).
            text: Text content to upload (will be UTF-8 encoded).

        Note:
            If storage is not configured, logs debug message and returns without error.
        """
        if not self._should_upload():
            return
        container = self.container()
        if not container:
            self._log_unconfigured("upload_text")
            return
        blob_name = self.blob_name_for_path(path)
        try:
            _upload_text_sync(container, blob_name, text.encode("utf-8"))
        except (OSError, AzureError) as exc:
            self._handle_upload_error(path, exc)
        except Exception as exc:  # pragma: no cover - defensive logging
            self._logger.error(
                "Unexpected failure uploading text to Azure",
                extra={"blob_name": blob_name, "path": str(path)},
                exc_info=True,
            )
            self._handle_upload_error(path, exc)

    async def upload_text_async(self, path: Path, text: str) -> None:
        if not self._should_upload():
            return
        container = await self.container_async()
        if not container:
            self._log_unconfigured("upload_text_async")
            return
        blob_name = self.blob_name_for_path(path)
        try:
            await container.upload_blob(
                name=blob_name, data=text.encode("utf-8"), overwrite=True
            )
        except (OSError, AzureError) as exc:
            self._handle_upload_error(path, exc)
        except Exception as exc:  # pragma: no cover - defensive logging
            self._logger.error(
                "Unexpected failure uploading text to Azure (async)",
                extra={"blob_name": blob_name, "path": str(path)},
                exc_info=True,
            )
            self._handle_upload_error(path, exc)

    def upload_file(self, path: Path, *, blob_path: str | None = None) -> None:
        if not self._should_upload():
            return
        container = self.container()
        if not container:
            self._log_unconfigured("upload_file")
            return
        blob_name = blob_path or self.blob_name_for_path(path)
        try:
            _upload_file_sync(container, blob_name, path)
        except (OSError, AzureError) as exc:
            self._handle_upload_error(path, exc)
        except Exception as exc:  # pragma: no cover - defensive logging
            self._logger.error(
                "Unexpected failure uploading file to Azure",
                extra={"blob_name": blob_name, "path": str(path)},
                exc_info=True,
            )
            self._handle_upload_error(path, exc)

    async def upload_file_async(
        self, path: Path, *, blob_path: str | None = None
    ) -> None:
        if not self._should_upload():
            return
        container = await self.container_async()
        if not container:
            self._log_unconfigured("upload_file_async")
            return
        blob_name = blob_path or self.blob_name_for_path(path)
        try:
            with path.open("rb") as handle:
                await container.upload_blob(name=blob_name, data=handle, overwrite=True)
        except (OSError, AzureError) as exc:
            self._handle_upload_error(path, exc)
        except Exception as exc:  # pragma: no cover - defensive logging
            self._logger.error(
                "Unexpected failure uploading file to Azure (async)",
                extra={"blob_name": blob_name, "path": str(path)},
                exc_info=True,
            )
            self._handle_upload_error(path, exc)

    def download_to_path(self, path: Path) -> bool:
        container = self.container()
        if not container:
            return False
        blob_name = self.blob_name_for_path(path)
        try:
            downloader = container.download_blob(blob_name)
        except ResourceNotFoundError:
            return False
        _stream_blob_to_path(downloader, path)
        return True

    def download_tree(self, path: Path) -> bool:
        """Download blob tree to local filesystem.

        Downloads the blob at the given path plus all blobs with that path as prefix.
        For example, if path is "screenshots/site1", downloads:
        - screenshots/site1 (if exists as blob)
        - screenshots/site1/* (all blobs with this prefix)

        Args:
            path: Local filesystem path (also used to determine blob prefix).

        Returns:
            True if any blobs were downloaded, False otherwise.

        Note:
            Creates parent directories as needed.
        """
        container = self.container()
        if not container:
            return False
        prefix = self.blob_name_for_path(path)
        downloaded_any = False
        if self.download_to_path(path):
            downloaded_any = True
        if not prefix.endswith("/"):
            prefix = f"{prefix}/"
        for blob in container.list_blobs(name_starts_with=prefix):
            name = getattr(blob, "name", "")
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix) :]
            if not relative:
                continue
            target = path / relative
            try:
                downloader = container.download_blob(name)
            except ResourceNotFoundError:
                continue
            _stream_blob_to_path(downloader, target)
            downloaded_any = True
        return downloaded_any

    def list_tree(self, path: Path) -> List[Tuple[str, int]]:
        container = self.container()
        if not container:
            return []
        prefix = self.blob_name_for_path(path)
        if not prefix.endswith("/"):
            prefix = f"{prefix}/"
        results: List[Tuple[str, int]] = []
        for blob in container.list_blobs(name_starts_with=prefix):
            name = getattr(blob, "name", "")
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix) :]
            if not relative or relative.endswith("/"):
                continue
            size = getattr(blob, "size", 0) or 0
            results.append((relative, int(size)))
        return results

    async def download_to_path_async(self, path: Path) -> bool:
        container = await self.container_async()
        if not container:
            return False
        blob_name = self.blob_name_for_path(path)
        try:
            downloader = await container.download_blob(blob_name)
        except ResourceNotFoundError:
            return False
        await _stream_blob_to_path_async(downloader, path)
        return True

    async def download_tree_async(self, path: Path) -> bool:
        container = await self.container_async()
        if not container:
            return False
        prefix = self.blob_name_for_path(path)
        downloaded_any = False
        if await self.download_to_path_async(path):
            downloaded_any = True
        if not prefix.endswith("/"):
            prefix = f"{prefix}/"
        async for blob in container.list_blobs(name_starts_with=prefix):
            name = getattr(blob, "name", "")
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix) :]
            if not relative:
                continue
            target = path / relative
            try:
                downloader = await container.download_blob(name)
            except ResourceNotFoundError:
                continue
            await _stream_blob_to_path_async(downloader, target)
            downloaded_any = True
        return downloaded_any

    async def list_tree_async(self, path: Path) -> List[Tuple[str, int]]:
        container = await self.container_async()
        if not container:
            return []
        prefix = self.blob_name_for_path(path)
        if not prefix.endswith("/"):
            prefix = f"{prefix}/"
        results: List[Tuple[str, int]] = []
        async for blob in container.list_blobs(name_starts_with=prefix):
            name = getattr(blob, "name", "")
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix) :]
            if not relative or relative.endswith("/"):
                continue
            size = getattr(blob, "size", 0) or 0
            results.append((relative, int(size)))
        return results

    def close(self) -> None:
        if self._container is not None:
            self._container.close()
            self._container = None
        if self._service is not None:
            self._service.close()
            self._service = None
        if self._credential is not None:
            self._credential.close()
            self._credential = None

    async def aclose(self) -> None:
        """Close async resources (sync resources are closed for completeness)."""
        self.close()
        lock = self._get_async_lock()
        async with lock:
            if self._async_container is not None:
                await self._async_container.close()
                self._async_container = None
            if self._async_service is not None:
                await self._async_service.close()
                self._async_service = None
            if self._async_credential is not None:
                await self._async_credential.close()
                self._async_credential = None


_CLIENT_LOCK = Lock()
SettingsKey = Tuple[str | None, str | None, str | None, str | None, str | None]
_DEFAULT_SETTINGS_KEY = object()
_CLIENT_CACHE: Dict[object | SettingsKey, AzureStorageClient] = {}
_PENDING_ASYNC_DISPOSALS: "set[asyncio.Task[None]]" = set()


def _settings_cache_key(settings: AzureStorageSettings) -> SettingsKey:
    return (
        settings.container,
        settings.connection_string,
        settings.account_name,
        settings.blob_endpoint,
        settings.prefix,
    )


def _resolve_settings(
    settings: AzureStorageSettings | None,
) -> Tuple[object | SettingsKey, AzureStorageSettings]:
    if settings is None:
        resolved = AzureStorageSettings.from_env()
        return _DEFAULT_SETTINGS_KEY, resolved
    return _settings_cache_key(settings), settings


def get_shared_client(
    settings: AzureStorageSettings | None = None,
) -> AzureStorageClient:
    """Get or create cached Azure storage client.

    Returns a cached client if settings match the cache. If settings changed,
    disposes the old client and creates a new one.

    Args:
        settings: Storage settings (default: load from environment).

    Returns:
        Cached AzureStorageClient instance (may be unconfigured if no container).
    """
    key, resolved = _resolve_settings(settings)
    with _CLIENT_LOCK:
        cached = _CLIENT_CACHE.get(key)
        config = _AzureStorageConfig.from_settings(resolved)
        if cached is None or cached.config != config:
            if cached is not None:
                _dispose_client(cached)
            cached = AzureStorageClient(config=config, settings=resolved)
            _CLIENT_CACHE[key] = cached
        return cached


def get_client(settings: AzureStorageSettings | None = None) -> AzureStorageClient:
    """Alias for get_shared_client for backward compatibility."""
    return get_shared_client(settings)


def set_shared_client(
    client: AzureStorageClient, *, settings: AzureStorageSettings | None = None
) -> None:
    """Replace the cached client with a custom instance.

    Args:
        client: Custom AzureStorageClient to use.
        settings: Settings key to associate with this client (default: default key).
    """
    key, _ = _resolve_settings(settings)
    with _CLIENT_LOCK:
        cached = _CLIENT_CACHE.get(key)
        if cached is not None:
            _dispose_client(cached)
        _CLIENT_CACHE[key] = client


def reset_shared_client(settings: AzureStorageSettings | None = None) -> None:
    """Clear cached client and create fresh instance on next access.

    Args:
        settings: Settings key to reset (default: reset default client).
    """
    key, _ = _resolve_settings(settings)
    with _CLIENT_LOCK:
        cached = _CLIENT_CACHE.pop(key, None)
        if cached is not None:
            _dispose_client(cached)


async def reset_shared_client_async(
    settings: AzureStorageSettings | None = None,
) -> None:
    """Async variant ensuring all resources (sync + async) are released."""
    key, _ = _resolve_settings(settings)
    with _CLIENT_LOCK:
        cached = _CLIENT_CACHE.pop(key, None)
    if cached is None:
        return
    await cached.aclose()


def is_enabled(settings: AzureStorageSettings | None = None) -> bool:
    _, resolved = _resolve_settings(settings)
    return _AzureStorageConfig.from_settings(resolved) is not None


def blob_path_for(path: Path, *, settings: AzureStorageSettings | None = None) -> str:
    return get_client(settings).blob_name_for_path(path)


def list_tree(
    path: Path, *, settings: AzureStorageSettings | None = None
) -> List[Tuple[str, int]]:
    return get_client(settings).list_tree(path)


def download_tree(path: Path, *, settings: AzureStorageSettings | None = None) -> bool:
    return get_client(settings).download_tree(path)


def download_to_path(
    path: Path, *, settings: AzureStorageSettings | None = None
) -> bool:
    return get_client(settings).download_to_path(path)


def upload_text(
    path: Path, text: str, *, settings: AzureStorageSettings | None = None
) -> None:
    get_client(settings).upload_text(path, text)


def upload_file(
    path: Path,
    *,
    blob_path: str | None = None,
    settings: AzureStorageSettings | None = None,
) -> None:
    get_client(settings).upload_file(path, blob_path=blob_path)


async def upload_text_async(
    path: Path, text: str, *, settings: AzureStorageSettings | None = None
) -> None:
    await get_client(settings).upload_text_async(path, text)


async def upload_file_async(
    path: Path,
    *,
    blob_path: str | None = None,
    settings: AzureStorageSettings | None = None,
) -> None:
    await get_client(settings).upload_file_async(path, blob_path=blob_path)


async def download_to_path_async(
    path: Path, *, settings: AzureStorageSettings | None = None
) -> bool:
    return await get_client(settings).download_to_path_async(path)


async def download_tree_async(
    path: Path, *, settings: AzureStorageSettings | None = None
) -> bool:
    return await get_client(settings).download_tree_async(path)


async def list_tree_async(
    path: Path, *, settings: AzureStorageSettings | None = None
) -> List[Tuple[str, int]]:
    return await get_client(settings).list_tree_async(path)


def _upload_text_sync(container: ContainerClient, blob_name: str, data: bytes) -> None:
    container.upload_blob(name=blob_name, data=data, overwrite=True)


def _upload_file_sync(container: ContainerClient, blob_name: str, path: Path) -> None:
    with path.open("rb") as handle:
        container.upload_blob(name=blob_name, data=handle, overwrite=True)


def _iter_downloader_chunks(downloader: Any) -> Iterable[bytes]:
    chunk_method = getattr(downloader, "chunks", None)
    if callable(chunk_method):
        chunks = chunk_method()
        if isinstance(chunks, Iterable):
            yield from chunks
            return
    readall = getattr(downloader, "readall", None)
    if callable(readall):
        data = readall()
        if data:
            yield data
        return
    raise RuntimeError("Downloader does not support chunk iteration or readall()")


async def _aiter_downloader_chunks(downloader: Any) -> AsyncIterable[bytes]:
    chunk_method = getattr(downloader, "chunks", None)
    if callable(chunk_method):
        chunks = chunk_method()
        if hasattr(chunks, "__aiter__"):
            async for chunk in chunks:
                yield chunk
            return
        if isinstance(chunks, Iterable):
            for chunk in chunks:
                yield chunk
            return
    readall = getattr(downloader, "readall", None)
    if callable(readall):
        result = readall()
        if inspect.isawaitable(result):
            data = await result
        else:
            data = result
        if data:
            yield data
        return
    raise RuntimeError("Downloader does not support async chunk iteration or readall()")


def _stream_blob_to_path(downloader: Any, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            for chunk in _iter_downloader_chunks(downloader):
                if not chunk:
                    continue
                handle.write(chunk)
            handle.flush()
            os.fsync(handle.fileno())
        _atomic_replace(tmp_path, destination)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


async def _stream_blob_to_path_async(downloader: Any, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    tmp_path = Path(tmp_name)
    loop = asyncio.get_running_loop()
    try:
        with os.fdopen(fd, "wb") as handle:
            async for chunk in _aiter_downloader_chunks(downloader):
                if not chunk:
                    continue
                await loop.run_in_executor(None, handle.write, chunk)
            await loop.run_in_executor(None, handle.flush)
            await loop.run_in_executor(None, os.fsync, handle.fileno())
        await loop.run_in_executor(None, _atomic_replace, tmp_path, destination)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _atomic_replace(source: Path, destination: Path) -> None:
    """Replace destination with source, falling back to shutil.move across devices."""
    try:
        source.replace(destination)
    except OSError as exc:
        if exc.errno == errno.EXDEV:
            shutil.move(str(source), str(destination))
            return
        raise


def _dispose_client(client: AzureStorageClient) -> None:
    """Dispose client resources, awaiting async cleanup when feasible."""
    try:
        client.close()
    except Exception:  # pragma: no cover - defensive disposal
        logger.debug("Failed to close AzureStorageClient synchronously", exc_info=True)
    _schedule_async_disposal(client)


def _schedule_async_disposal(client: AzureStorageClient) -> None:
    """Best-effort async cleanup for callers without an event loop."""

    async def _dispose_async() -> None:
        try:
            await client.aclose()
        except Exception:  # pragma: no cover - defensive disposal
            logger.debug(
                "Failed to close AzureStorageClient asynchronously", exc_info=True
            )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            asyncio.run(client.aclose())
        except RuntimeError:
            logger.debug(
                "No running loop available to dispose AzureStorageClient async resources",
                exc_info=True,
            )
        except Exception:  # pragma: no cover - defensive disposal
            logger.debug(
                "Failed to dispose AzureStorageClient async resources", exc_info=True
            )
        return

    task = loop.create_task(_dispose_async())
    _PENDING_ASYNC_DISPOSALS.add(task)

    def _clear(completed: asyncio.Task[None]) -> None:
        _PENDING_ASYNC_DISPOSALS.discard(completed)

    task.add_done_callback(_clear)

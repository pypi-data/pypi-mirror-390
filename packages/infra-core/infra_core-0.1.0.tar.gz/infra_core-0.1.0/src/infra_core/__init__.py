"""Expose runtime, storage, and HTTP helpers for automation pipelines.

This package centralizes the public surface of infra_core so downstream
projects can import stable symbols without relying on internal layout. It
re-exports runtime orchestration primitives, Azure Storage clients, filesystem
utilities, and both sync/async HTTP helpers.

Example:
    >>> from infra_core import (
    ...     TaskRuntime,
    ...     RuntimeConfig,
    ...     azure_is_enabled,
    ...     fetch_async,
    ... )
    >>> runtime = TaskRuntime(config=RuntimeConfig())
    >>> if azure_is_enabled():
    ...     print("Azure storage configured")
    >>> async def ping() -> int:
    ...     response = await fetch_async("https://example.com/status")
    ...     return response.status
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from .asset_client import (
    AssetDownloadClient,
    DownloadResult,
    download_asset,
    download_asset_async,
)
from .fs_utils import compute_checksum, ensure_parent, hashed_asset_path
from .http import DEFAULT_HEADERS as http_default_headers, fetch
from .http_async import DEFAULT_HEADERS as http_async_default_headers, fetch_async
from .task_runtime import RuntimeCancellationError, RuntimeConfig, TaskRuntime

logging.getLogger(__name__).addHandler(logging.NullHandler())

AzureStorageClient: Any
AzureStorageSettings: Any
blob_path_for: Any
download_to_path: Any
download_to_path_async: Any
download_tree: Any
download_tree_async: Any
get_azure_storage_client: Any
azure_is_enabled: Any
list_tree: Any
list_tree_async: Any
upload_file: Any
upload_file_async: Any
upload_text: Any
upload_text_async: Any

_AZURE_IMPORT_ERROR: ModuleNotFoundError | None = None


def _missing_azure_dependency(name: str) -> Callable[..., None]:
    """Return a callable that raises an informative error for optional Azure helpers."""

    def _missing(*_args: object, **_kwargs: object) -> None:
        if _AZURE_IMPORT_ERROR is not None:
            raise ModuleNotFoundError(
                f"{name} requires optional Azure dependencies. Install 'infra-core[azure]' to "
                "enable Azure helpers."
            ) from _AZURE_IMPORT_ERROR
        raise ModuleNotFoundError(
            f"{name} requires optional Azure dependencies that failed to import."
        )

    _missing.__name__ = name
    return _missing


try:
    from .azure_storage import (
        AzureStorageClient,
        AzureStorageSettings,
        blob_path_for,
        download_to_path,
        download_to_path_async,
        download_tree,
        download_tree_async,
        get_client as get_azure_storage_client,
        is_enabled as azure_is_enabled,
        list_tree,
        list_tree_async,
        upload_file,
        upload_file_async,
        upload_text,
        upload_text_async,
    )
except ModuleNotFoundError as exc:
    if exc.name and not exc.name.startswith("azure"):
        raise
    _AZURE_IMPORT_ERROR = exc
    AzureStorageClient = _missing_azure_dependency("AzureStorageClient")
    AzureStorageSettings = _missing_azure_dependency("AzureStorageSettings")
    blob_path_for = _missing_azure_dependency("blob_path_for")
    download_to_path = _missing_azure_dependency("download_to_path")
    download_to_path_async = _missing_azure_dependency("download_to_path_async")
    download_tree = _missing_azure_dependency("download_tree")
    download_tree_async = _missing_azure_dependency("download_tree_async")
    get_azure_storage_client = _missing_azure_dependency("get_azure_storage_client")
    azure_is_enabled = _missing_azure_dependency("azure_is_enabled")
    list_tree = _missing_azure_dependency("list_tree")
    list_tree_async = _missing_azure_dependency("list_tree_async")
    upload_file = _missing_azure_dependency("upload_file")
    upload_file_async = _missing_azure_dependency("upload_file_async")
    upload_text = _missing_azure_dependency("upload_text")
    upload_text_async = _missing_azure_dependency("upload_text_async")

__all__ = [
    "TaskRuntime",
    "RuntimeConfig",
    "RuntimeCancellationError",
    "AssetDownloadClient",
    "DownloadResult",
    "download_asset",
    "download_asset_async",
    "AzureStorageClient",
    "AzureStorageSettings",
    "blob_path_for",
    "download_to_path",
    "download_to_path_async",
    "download_tree",
    "download_tree_async",
    "get_azure_storage_client",
    "list_tree",
    "list_tree_async",
    "ensure_parent",
    "hashed_asset_path",
    "compute_checksum",
    "azure_is_enabled",
    "upload_file",
    "upload_file_async",
    "upload_text",
    "upload_text_async",
    "fetch",
    "fetch_async",
    "http_default_headers",
    "http_async_default_headers",
]

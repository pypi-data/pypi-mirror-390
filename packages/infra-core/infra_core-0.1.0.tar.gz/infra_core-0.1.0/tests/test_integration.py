"""Integration-style tests that exercise multiple infra_core modules together."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest
import respx

from infra_core import azure_storage
from infra_core.asset_client import (
    download_asset_async,
    get_shared_client,
    reset_shared_client,
    set_shared_client,
)
from infra_core.azure_storage import (
    AzureStorageClient,
    _AzureStorageConfig as AzureStorageConfig,
)
from infra_core.task_runtime import RuntimeConfig, TaskRuntime


@pytest.mark.asyncio
@respx.mock
async def test_download_and_mirror_to_azure(tmp_path: Path) -> None:
    respx.get("https://files.test/logo").mock(
        return_value=httpx.Response(200, content=b"logo-bytes")
    )
    dest = tmp_path / "logo.bin"

    result = await download_asset_async(
        "https://files.test/logo", dest, skip_if_exists=False, compute_checksum=True
    )
    assert result.path.exists()
    assert dest.read_bytes() == b"logo-bytes"

    class DummyContainer:
        def __init__(self) -> None:
            self.uploads: dict[str, bytes] = {}

        def upload_blob(self, *, name: str, data, overwrite: bool) -> None:  # type: ignore[no-untyped-def]
            payload = data.read() if hasattr(data, "read") else data
            self.uploads[name] = payload

        def list_blobs(self, *, name_starts_with: str):  # type: ignore[no-untyped-def]
            for name, payload in self.uploads.items():
                if name.startswith(name_starts_with):
                    yield type("Blob", (), {"name": name, "size": len(payload)})

        def close(self) -> None:  # pragma: no cover - noop
            pass

    config = AzureStorageConfig(container="demo", prefix="exports")
    client = AzureStorageClient(config=config)
    dummy = DummyContainer()
    client._container = dummy  # type: ignore[attr-defined]

    client.upload_file(result.path)

    blob_name = config.blob_name_for_path(result.path)
    assert dummy.uploads[blob_name] == b"logo-bytes"

    listing = client.list_tree(result.path.parent)
    assert listing == [(result.path.name, len(b"logo-bytes"))]


def test_asset_client_shared_lock_handles_multiple_event_loops() -> None:
    async def acquire_and_close() -> None:
        client = await get_shared_client()
        await client.close()
        set_shared_client(None)

    asyncio.run(acquire_and_close())
    asyncio.run(acquire_and_close())


@pytest.mark.asyncio
@respx.mock
async def test_end_to_end_runtime_download_and_upload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    respx.get("https://files.test/logo").mock(
        return_value=httpx.Response(200, content=b"logo-bytes")
    )
    respx.get("https://files.test/icon").mock(
        return_value=httpx.Response(200, content=b"icon-bytes")
    )

    uploaded: dict[str, bytes] = {}

    def fake_upload(path: Path, *, settings=None, blob_path=None) -> None:
        uploaded[path.name] = path.read_bytes()

    monkeypatch.setattr(azure_storage, "upload_file", fake_upload)

    await reset_shared_client()

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=2))
    dest_dir = tmp_path / "assets"

    async def pipeline(slug: str) -> None:
        dest = dest_dir / f"{slug}.bin"
        result = await download_asset_async(
            f"https://files.test/{slug}", dest, skip_if_exists=False
        )
        azure_storage.upload_file(result.path)

    tasks = [(slug, (lambda slug=slug: pipeline(slug))) for slug in ("logo", "icon")]
    await runtime.run(tasks)

    await reset_shared_client()

    assert uploaded == {
        "logo.bin": b"logo-bytes",
        "icon.bin": b"icon-bytes",
    }

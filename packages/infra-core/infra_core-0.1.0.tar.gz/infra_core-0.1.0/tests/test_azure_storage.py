"""Unit tests for azure_storage helpers."""

from __future__ import annotations

import logging
import errno
import types
from pathlib import Path

import pytest

from infra_core.azure_storage import (
    AzureStorageClient,
    StorageBackend,
    _AzureStorageConfig as AzureStorageConfig,
    ResourceNotFoundError,
    _blob_name_for_path as blob_name_for_path,
    _atomic_replace,
    AzureStorageSettings,
)
from infra_core import azure_storage


def test_client_matches_storage_backend_protocol() -> None:
    client = AzureStorageClient(config=None)
    assert isinstance(client, StorageBackend)


def test_config_from_settings_requires_container() -> None:
    empty = AzureStorageSettings(container=None)
    assert AzureStorageConfig.from_settings(empty) is None


def test_create_service_client_uses_connection_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = AzureStorageConfig(
        container="demo", connection_string="UseDevelopmentStorage=true"
    )
    dummy_client = object()
    captured: dict[str, object] = {}

    def fake_from_conn(cls, conn: str) -> object:
        captured["conn"] = conn
        return dummy_client

    monkeypatch.setattr(
        azure_storage.BlobServiceClient,
        "from_connection_string",
        classmethod(fake_from_conn),
    )

    client, credential = config.create_service_client()

    assert client is dummy_client
    assert credential is None
    assert captured["conn"] == "UseDevelopmentStorage=true"


def test_create_service_client_with_account_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = AzureStorageConfig(container="demo", account_name="acct")
    dummy_credential = object()
    captured: dict[str, object] = {}

    class DummyBlobServiceClient:
        def __init__(self, *, account_url: str, credential: object) -> None:
            captured["account_url"] = account_url
            captured["credential"] = credential

    monkeypatch.setattr(azure_storage, "BlobServiceClient", DummyBlobServiceClient)
    monkeypatch.setattr(
        azure_storage, "DefaultAzureCredential", lambda: dummy_credential
    )

    client, credential = config.create_service_client()

    assert isinstance(client, DummyBlobServiceClient)
    assert credential is dummy_credential
    assert captured["account_url"] == "https://acct.blob.core.windows.net"
    assert captured["credential"] is dummy_credential


def test_create_service_client_without_credentials_raises() -> None:
    config = AzureStorageConfig(container="demo")
    with pytest.raises(RuntimeError):
        config.create_service_client()


def test_create_async_service_client_uses_connection_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = AzureStorageConfig(
        container="demo", connection_string="UseDevelopmentStorage=true"
    )
    dummy_client = object()

    def fake_from_conn(cls, conn: str) -> object:
        return dummy_client

    monkeypatch.setattr(
        azure_storage.AsyncBlobServiceClient,
        "from_connection_string",
        classmethod(fake_from_conn),
    )

    client, credential = config.create_async_service_client()

    assert client is dummy_client
    assert credential is None


def test_write_text_mirrors_upload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = AzureStorageConfig(container="demo")
    client = AzureStorageClient(config=config)
    recorded: dict[str, object] = {}

    def _fake_upload(path: Path, text: str) -> None:
        recorded["path"] = path
        recorded["text"] = text

    monkeypatch.setattr(client, "upload_text", _fake_upload)
    target = tmp_path / "artifact.txt"

    client.write_text(target, "payload")

    assert target.read_text(encoding="utf-8") == "payload"
    assert recorded["path"] == target
    assert recorded["text"] == "payload"


def test_write_text_skips_upload_when_disabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = AzureStorageConfig(container="demo")
    client = AzureStorageClient(config=config, enabled=False)

    def _boom() -> None:  # pragma: no cover - triggered if upload happens
        raise AssertionError("container should not be fetched when disabled")

    monkeypatch.setattr(client, "container", _boom)
    target = tmp_path / "artifact.txt"

    client.write_text(target, "payload")

    assert target.read_text(encoding="utf-8") == "payload"


def test_write_json_serializes_dict(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = AzureStorageConfig(container="demo")
    client = AzureStorageClient(config=config)
    captured: dict[str, str] = {}

    def _fake_write(path: Path, text: str) -> Path:
        captured["text"] = text
        return path

    monkeypatch.setattr(client, "write_text", _fake_write)

    target = tmp_path / "manifest.json"
    client.write_json(target, {"slug": "demo"})

    assert captured["text"].startswith("{")
    assert captured["text"].endswith("\n")


@pytest.mark.asyncio
async def test_write_text_async_uses_async_upload(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = AzureStorageConfig(container="demo")
    client = AzureStorageClient(config=config)
    recorded: dict[str, object] = {}

    async def _fake_upload(path: Path, text: str) -> None:
        recorded["path"] = path
        recorded["text"] = text

    monkeypatch.setattr(client, "upload_text_async", _fake_upload)
    target = tmp_path / "artifact.txt"

    await client.write_text_async(target, "payload")

    assert target.read_text(encoding="utf-8") == "payload"
    assert recorded["path"] == target
    assert recorded["text"] == "payload"


def test_upload_text_swallows_errors_by_default(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    config = AzureStorageConfig(container="demo")
    client = AzureStorageClient(config=config)

    class DummyContainer:
        def upload_blob(self, *, name, data, overwrite):  # type: ignore[no-untyped-def]
            raise RuntimeError("boom")

    client._container = DummyContainer()  # type: ignore[attr-defined]
    caplog.set_level(logging.WARNING)

    client.upload_text(tmp_path / "artifact.txt", "payload")

    assert "Azure upload failed" in caplog.text


def test_upload_text_raises_when_swallow_errors_false(tmp_path: Path) -> None:
    config = AzureStorageConfig(container="demo")
    client = AzureStorageClient(config=config, swallow_errors=False)

    class DummyContainer:
        def upload_blob(self, *, name, data, overwrite):  # type: ignore[no-untyped-def]
            raise RuntimeError("boom")

    client._container = DummyContainer()  # type: ignore[attr-defined]

    with pytest.raises(RuntimeError):
        client.upload_text(tmp_path / "artifact.txt", "payload")


def test_list_tree_returns_empty_when_storage_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AzureStorageClient(config=None)
    monkeypatch.setattr(azure_storage, "get_client", lambda settings=None: client)

    result = azure_storage.list_tree(Path("/tmp/runs/batch/job/screens"))

    assert result == []


def test_list_tree_uses_default_container(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured = {}

    class DummyContainer:
        def list_blobs(self, *, name_starts_with: str):  # type: ignore[no-untyped-def]
            captured["prefix"] = name_starts_with
            return [
                type(
                    "Blob",
                    (),
                    {"name": f"{name_starts_with}slug/file.txt", "size": 128},
                )
            ]

    dummy_config = AzureStorageConfig(container="demo", prefix="exports")
    client = AzureStorageClient(config=dummy_config)
    client._container = DummyContainer()  # type: ignore[attr-defined]
    monkeypatch.setattr(azure_storage, "get_client", lambda settings=None: client)

    target = tmp_path / "runs" / "batch"
    result = azure_storage.list_tree(target)

    expected_prefix = dummy_config.blob_name_for_path(target)
    if not expected_prefix.endswith("/") and expected_prefix:
        expected_prefix = f"{expected_prefix}/"

    assert result == [("slug/file.txt", 128)]
    assert captured["prefix"] == expected_prefix


def test_blob_name_helper_handles_prefix() -> None:
    path = Path("/tmp/runs/e2e/job/screens")
    assert (
        blob_name_for_path(path, prefix="exports") == "exports/tmp/runs/e2e/job/screens"
    )


def test_blob_path_for_uses_config(monkeypatch: pytest.MonkeyPatch) -> None:
    config = AzureStorageConfig(container="demo", prefix="data")
    client = AzureStorageClient(config=config)
    monkeypatch.setattr(azure_storage, "get_client", lambda settings=None: client)
    path = Path("/tmp/runs/foo/bar")
    result = azure_storage.blob_path_for(path)
    assert result == config.blob_name_for_path(path)


def test_upload_text_uses_default_container(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = {}

    class DummyContainer:
        def upload_blob(self, *, name, data, overwrite):  # type: ignore[no-untyped-def]
            calls["upload_blob"] = (name, data, overwrite)

    dummy_config = AzureStorageConfig(container="demo", prefix=None)
    client = AzureStorageClient(config=dummy_config)
    client._container = DummyContainer()  # type: ignore[attr-defined]
    monkeypatch.setattr(azure_storage, "get_client", lambda settings=None: client)

    path = tmp_path / "runs" / "batch" / "job" / "screens.json"
    azure_storage.upload_text(path, "payload")

    assert calls["upload_blob"][0] == dummy_config.blob_name_for_path(path)
    assert calls["upload_blob"][1] == b"payload"
    assert calls["upload_blob"][2] is True


@pytest.mark.asyncio
async def test_upload_text_async_uses_async_container(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    uploads: list[tuple[str, bytes, bool]] = []

    class DummyAsyncContainer:
        def __init__(self) -> None:
            self.create_calls = 0

        async def create_container(self) -> None:
            self.create_calls += 1

        async def upload_blob(self, *, name: str, data: bytes, overwrite: bool) -> None:
            uploads.append((name, data, overwrite))

        async def close(self) -> None:
            pass

    class DummyAsyncService:
        def __init__(self, container: DummyAsyncContainer) -> None:
            self.container = container
            self.calls = 0

        def get_container_client(self, container_name: str) -> DummyAsyncContainer:
            self.calls += 1
            return self.container

        async def close(self) -> None:
            pass

    dummy_container = DummyAsyncContainer()
    dummy_service = DummyAsyncService(dummy_container)
    config = AzureStorageConfig(container="demo", prefix="exports")
    monkeypatch.setattr(
        AzureStorageConfig,
        "create_async_service_client",
        lambda self: (dummy_service, None),
    )

    client = AzureStorageClient(config=config)
    target = tmp_path / "runs" / "batch" / "job" / "log.txt"

    await client.upload_text_async(target, "payload")

    expected_blob = config.blob_name_for_path(target)
    assert uploads == [(expected_blob, b"payload", True)]
    assert dummy_container.create_calls == 1
    assert dummy_service.calls == 1

    await client.aclose()


def test_atomic_replace_falls_back_to_move(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = tmp_path / "blob.tmp"
    dest = tmp_path / "blob.bin"
    source.write_bytes(b"blob-bytes")
    dest.write_bytes(b"old")
    moves: list[tuple[str, str]] = []

    original_replace = Path.replace

    def fake_replace(self: Path, target: Path) -> Path:
        if self == source:
            raise OSError(errno.EXDEV, "cross-device")
        return original_replace(self, target)

    def fake_move(src: str, dst: str) -> None:
        moves.append((src, dst))
        Path(dst).write_bytes(Path(src).read_bytes())
        Path(src).unlink(missing_ok=True)

    monkeypatch.setattr(Path, "replace", fake_replace, raising=False)
    monkeypatch.setattr(azure_storage.shutil, "move", fake_move)

    _atomic_replace(source, dest)

    assert dest.read_bytes() == b"blob-bytes"
    assert not source.exists()
    assert moves == [(str(source), str(dest))]


def test_atomic_replace_propagates_other_os_errors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = tmp_path / "blob.tmp"
    dest = tmp_path / "blob.bin"
    source.write_bytes(b"blob-bytes")
    dest.write_bytes(b"old")
    original_replace = Path.replace

    def fake_replace(self: Path, target: Path) -> Path:
        if self == source:
            raise OSError(errno.EACCES, "denied")
        return original_replace(self, target)

    moved = False

    def fake_move(src: str, dst: str) -> None:
        nonlocal moved
        moved = True

    monkeypatch.setattr(Path, "replace", fake_replace, raising=False)
    monkeypatch.setattr(azure_storage.shutil, "move", fake_move)

    with pytest.raises(OSError):
        _atomic_replace(source, dest)

    assert moved is False
    assert source.exists()


def test_set_shared_client_disposes_previous(monkeypatch: pytest.MonkeyPatch) -> None:
    disposed: list[AzureStorageClient] = []
    monkeypatch.setattr(
        azure_storage, "_dispose_client", lambda client: disposed.append(client)
    )
    first = AzureStorageClient(config=None)
    second = AzureStorageClient(config=None)

    azure_storage.set_shared_client(first)
    azure_storage.set_shared_client(second)

    assert disposed == [first]
    azure_storage.reset_shared_client()


@pytest.mark.asyncio
async def test_reset_shared_client_async_closes_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    closed: list[bool] = []

    class DummyClient(AzureStorageClient):
        async def aclose(self) -> None:  # type: ignore[override]
            closed.append(True)

    client = DummyClient(config=None)
    azure_storage.set_shared_client(client)
    await azure_storage.reset_shared_client_async()

    assert closed == [True]


def test_download_tree_writes_all_blobs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = AzureStorageConfig(container="demo", prefix="exports")
    client = AzureStorageClient(config=config)
    target = tmp_path / "runs" / "batch"
    root_blob = config.blob_name_for_path(target)
    child_blob = f"{root_blob}/nested/info.txt"
    blobs = {
        child_blob: b"child",
    }

    class DummyDownloader:
        def __init__(self, data: bytes) -> None:
            self._data = data

        def chunks(self):
            yield self._data

    class DummyContainer:
        def download_blob(self, name: str) -> DummyDownloader:
            if name == root_blob:
                raise ResourceNotFoundError(message="missing")
            if name not in blobs:
                raise ResourceNotFoundError(message="missing")
            return DummyDownloader(blobs[name])

        def list_blobs(self, *, name_starts_with: str):
            for name, data in blobs.items():
                if name.startswith(name_starts_with) and name != name_starts_with:
                    yield type("Blob", (), {"name": name, "size": len(data)})

    dummy_container = DummyContainer()

    def _container(self: AzureStorageClient) -> DummyContainer:
        return dummy_container

    client.container = types.MethodType(_container, client)  # type: ignore[assignment]
    monkeypatch.setattr(azure_storage, "get_client", lambda settings=None: client)

    downloaded = azure_storage.download_tree(target)

    assert downloaded is True
    assert (target / "nested" / "info.txt").read_bytes() == b"child"


@pytest.mark.asyncio
async def test_download_tree_async_writes_all_blobs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = AzureStorageConfig(container="demo", prefix=None)
    client = AzureStorageClient(config=config)
    target = tmp_path / "jobs" / "task"
    root_blob = config.blob_name_for_path(target)
    child_blob = f"{root_blob}/child.bin"
    blobs = {
        child_blob: b"child-bytes",
    }

    class DummyAsyncDownloader:
        def __init__(self, data: bytes) -> None:
            self._data = data

        def chunks(self):
            async def _gen():
                yield self._data

            return _gen()

    class DummyAsyncContainer:
        async def download_blob(self, name: str) -> DummyAsyncDownloader:
            if name == root_blob:
                raise ResourceNotFoundError(message="missing")
            if name not in blobs:
                raise ResourceNotFoundError(message="missing")
            return DummyAsyncDownloader(blobs[name])

        def list_blobs(self, *, name_starts_with: str):
            async def _gen():
                for name, data in blobs.items():
                    if name.startswith(name_starts_with) and name != name_starts_with:
                        yield type("Blob", (), {"name": name, "size": len(data)})

            return _gen()

    dummy_async_container = DummyAsyncContainer()

    async def _container_async(self: AzureStorageClient) -> DummyAsyncContainer:
        return dummy_async_container

    client.container_async = types.MethodType(_container_async, client)  # type: ignore[assignment]
    monkeypatch.setattr(azure_storage, "get_client", lambda settings=None: client)

    downloaded = await azure_storage.download_tree_async(target)

    assert downloaded is True
    assert (target / "child.bin").read_bytes() == b"child-bytes"


@pytest.mark.asyncio
async def test_container_async_caches_service_and_container(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummyAsyncContainer:
        def __init__(self) -> None:
            self.create_calls = 0

        async def create_container(self) -> None:
            self.create_calls += 1

        async def close(self) -> None:
            pass

    class DummyAsyncService:
        def __init__(self, container: DummyAsyncContainer) -> None:
            self.container = container
            self.calls = 0

        def get_container_client(self, container_name: str) -> DummyAsyncContainer:
            self.calls += 1
            return self.container

        async def close(self) -> None:
            pass

    dummy_container = DummyAsyncContainer()
    dummy_service = DummyAsyncService(dummy_container)
    config = AzureStorageConfig(container="demo", prefix=None)
    monkeypatch.setattr(
        AzureStorageConfig,
        "create_async_service_client",
        lambda self: (dummy_service, None),
    )

    client = AzureStorageClient(config=config)

    first = await client.container_async()
    second = await client.container_async()

    assert first is second
    assert dummy_service.calls == 1
    assert dummy_container.create_calls == 1

    await client.aclose()


@pytest.mark.asyncio
async def test_upload_file_async_streams_bytes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}

    class DummyAsyncContainer:
        async def create_container(self) -> None:
            pass

        async def upload_blob(self, *, name: str, data, overwrite: bool) -> None:
            captured["name"] = name
            captured["data"] = data
            captured["overwrite"] = overwrite

        async def close(self) -> None:
            pass

    class DummyAsyncService:
        def __init__(self, container: DummyAsyncContainer) -> None:
            self.container = container

        def get_container_client(self, container_name: str) -> DummyAsyncContainer:
            return self.container

        async def close(self) -> None:
            pass

    container = DummyAsyncContainer()
    service = DummyAsyncService(container)
    config = AzureStorageConfig(container="demo", prefix="runs")

    client = AzureStorageClient(config=config)
    client._async_service = service  # type: ignore[attr-defined]
    client._async_container = container  # type: ignore[attr-defined]

    payload_path = tmp_path / "runs" / "note.bin"
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_bytes(b"payload-bytes")

    await client.upload_file_async(payload_path)

    assert captured["name"] == config.blob_name_for_path(payload_path)
    data = captured["data"]
    if isinstance(data, (bytes, bytearray)):
        assert data == b"payload-bytes"
    else:
        assert hasattr(data, "name")
        assert data.name == str(payload_path)
    assert captured["overwrite"] is True

    await client.aclose()


@pytest.mark.asyncio
async def test_download_to_path_async_writes_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data_map: dict[str, bytes] = {}

    class DummyDownloader:
        def __init__(self, name: str) -> None:
            self._name = name

        def chunks(self):
            async def _iterate():
                yield data_map[self._name]

            return _iterate()

        async def readall(self) -> bytes:
            return data_map[self._name]

    class DummyAsyncContainer:
        async def create_container(self) -> None:
            pass

        async def download_blob(self, name: str) -> DummyDownloader:
            if name not in data_map:
                raise ResourceNotFoundError("missing")
            return DummyDownloader(name)

        def list_blobs(self, *, name_starts_with: str):
            async def _iterator():
                if False:
                    yield  # pragma: no cover

            return _iterator()

        async def close(self) -> None:
            pass

    class DummyAsyncService:
        def __init__(self, container: DummyAsyncContainer) -> None:
            self.container = container

        def get_container_client(self, container_name: str) -> DummyAsyncContainer:
            return self.container

        async def close(self) -> None:
            pass

    container = DummyAsyncContainer()
    service = DummyAsyncService(container)
    config = AzureStorageConfig(container="demo", prefix="runs")

    blob_name = config.blob_name_for_path(tmp_path / "runs" / "item.txt")
    data_map[blob_name] = b"payload"

    client = AzureStorageClient(config=config)
    client._async_service = service  # type: ignore[attr-defined]
    client._async_container = container  # type: ignore[attr-defined]
    target = tmp_path / "runs" / "item.txt"

    result = await client.download_to_path_async(target)

    assert result is True
    assert target.read_bytes() == b"payload"

    await client.aclose()


@pytest.mark.asyncio
async def test_download_tree_async_materialises_blobs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class Blob:
        def __init__(self, name: str, size: int) -> None:
            self.name = name
            self.size = size

    class DummyDownloader:
        def __init__(self, name: str) -> None:
            self._name = name

        def chunks(self):
            async def _iterate():
                yield blob_data[self._name]

            return _iterate()

        async def readall(self) -> bytes:
            return blob_data[self._name]

    class DummyAsyncContainer:
        def __init__(self) -> None:
            self.list_prefixes: list[str] = []

        async def create_container(self) -> None:
            pass

        def list_blobs(self, *, name_starts_with: str):
            async def _iterator():
                for blob in blobs:
                    if blob.name.startswith(name_starts_with):
                        yield blob

            return _iterator()

        async def download_blob(self, name: str) -> DummyDownloader:
            if name not in blob_data:
                raise ResourceNotFoundError("missing")
            return DummyDownloader(name)

        async def close(self) -> None:
            pass

    class DummyAsyncService:
        def __init__(self, container: DummyAsyncContainer) -> None:
            self.container = container

        def get_container_client(self, container_name: str) -> DummyAsyncContainer:
            return self.container

        async def close(self) -> None:
            pass

    config = AzureStorageConfig(container="demo", prefix=None)
    container = DummyAsyncContainer()
    service = DummyAsyncService(container)
    root_path = tmp_path / "runs" / "batch"
    leaf_path = root_path / "slug" / "file.txt"
    leaf_blob = config.blob_name_for_path(leaf_path)
    blobs = [Blob(leaf_blob, 11)]
    blob_data = {
        leaf_blob: b"hello world",
    }

    client = AzureStorageClient(config=config)
    client._async_service = service  # type: ignore[attr-defined]
    client._async_container = container  # type: ignore[attr-defined]
    downloaded = await client.download_tree_async(root_path)

    assert downloaded is True
    assert (root_path / "slug" / "file.txt").read_bytes() == b"hello world"

    await client.aclose()


@pytest.mark.asyncio
async def test_list_tree_async_returns_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class Blob:
        def __init__(self, name: str, size: int) -> None:
            self.name = name
            self.size = size

    class DummyAsyncContainer:
        async def create_container(self) -> None:
            pass

        def list_blobs(self, *, name_starts_with: str):
            async def _iterator():
                for blob in blobs:
                    yield blob

            return _iterator()

        async def download_blob(self, name: str):
            raise AssertionError("should not download")

        async def close(self) -> None:
            pass

    class DummyAsyncService:
        def __init__(self, container: DummyAsyncContainer) -> None:
            self.container = container

        def get_container_client(self, container_name: str) -> DummyAsyncContainer:
            return self.container

        async def close(self) -> None:
            pass

    config = AzureStorageConfig(container="demo", prefix="runs")
    container = DummyAsyncContainer()
    service = DummyAsyncService(container)
    root_path = tmp_path / "runs" / "batch"
    leaf_a = config.blob_name_for_path(root_path / "slug" / "a.txt")
    leaf_b = config.blob_name_for_path(root_path / "slug" / "nested" / "b.txt")
    blobs = [
        Blob(leaf_a, 5),
        Blob(f"{config.blob_name_for_path(root_path / 'slug' / 'nested')}/", 0),
        Blob(leaf_b, 7),
    ]

    client = AzureStorageClient(config=config)
    client._async_service = service  # type: ignore[attr-defined]
    client._async_container = container  # type: ignore[attr-defined]
    entries = await client.list_tree_async(root_path)

    assert sorted(entries) == [("slug/a.txt", 5), ("slug/nested/b.txt", 7)]

    await client.aclose()


def test_download_to_path_short_circuits(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AzureStorageClient(config=None)
    monkeypatch.setattr(azure_storage, "get_client", lambda settings=None: client)
    assert azure_storage.download_to_path(Path("/tmp/file")) is False


def test_settings_from_env_allows_custom_var_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALT_CONTAINER", "custom-container")
    monkeypatch.setenv("ALT_CONN", "custom-conn")
    monkeypatch.setenv("ALT_PREFIX", "custom-prefix")
    settings = azure_storage.AzureStorageSettings.from_env(
        container_var="ALT_CONTAINER",
        connection_string_var="ALT_CONN",
        prefix_var="ALT_PREFIX",
    )
    config = AzureStorageConfig.from_settings(settings)
    assert config is not None
    assert config.container == "custom-container"
    assert config.connection_string == "custom-conn"
    assert config.prefix == "custom-prefix"


def test_get_client_disposes_stale_client(monkeypatch: pytest.MonkeyPatch) -> None:
    azure_storage.reset_shared_client()
    disposed: list[azure_storage.AzureStorageClient] = []
    monkeypatch.setattr(
        azure_storage, "_dispose_client", lambda client: disposed.append(client)
    )

    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "conn-a")
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "container-a")
    first = azure_storage.get_client()

    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "conn-b")
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "container-b")
    second = azure_storage.get_client()

    assert first is not second
    assert disposed == [first]
    azure_storage.reset_shared_client()


@pytest.mark.asyncio
async def test_aclose_closes_all_resources() -> None:
    class DummyCloseable:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    class DummyAsyncCloseable:
        def __init__(self) -> None:
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    client = AzureStorageClient(config=None)
    client._container = DummyCloseable()  # type: ignore[attr-defined]
    client._service = DummyCloseable()  # type: ignore[attr-defined]
    client._credential = DummyCloseable()  # type: ignore[attr-defined]
    client._async_container = DummyAsyncCloseable()  # type: ignore[attr-defined]
    client._async_service = DummyAsyncCloseable()  # type: ignore[attr-defined]
    client._async_credential = DummyAsyncCloseable()  # type: ignore[attr-defined]

    await client.aclose()

    assert client._container is None  # type: ignore[attr-defined]
    assert client._service is None  # type: ignore[attr-defined]
    assert client._credential is None  # type: ignore[attr-defined]
    assert client._async_container is None  # type: ignore[attr-defined]
    assert client._async_service is None  # type: ignore[attr-defined]
    assert client._async_credential is None  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_reset_shared_client_async_disposes_cached_client() -> None:
    azure_storage.reset_shared_client()

    class DummyCloseable(AzureStorageClient):
        def __init__(self) -> None:
            super().__init__(config=None)
            self.closed_sync = False
            self.closed_async = False

        def close(self) -> None:
            self.closed_sync = True
            super().close()

        async def aclose(self) -> None:
            self.closed_async = True
            await super().aclose()

    client = DummyCloseable()
    azure_storage.set_shared_client(client)

    await azure_storage.reset_shared_client_async()

    assert client.closed_sync is True
    assert client.closed_async is True

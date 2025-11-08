"""Tests for infra_core.asset_client."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest
import respx

from infra_core import asset_client


def test_asset_client_invalid_timeout_raises() -> None:
    with pytest.raises(ValueError):
        asset_client.AssetDownloadClient(timeout=0)


def test_asset_client_invalid_max_retries_raises() -> None:
    with pytest.raises(ValueError):
        asset_client.AssetDownloadClient(max_retries=-1)


@pytest.mark.asyncio
@respx.mock
async def test_async_download_writes_file(tmp_path: Path) -> None:
    content = b"hello world"
    respx.get("https://files.test/data").mock(
        return_value=httpx.Response(200, content=content)
    )

    client = asset_client.AssetDownloadClient()
    dest = tmp_path / "data.bin"

    result = await client.download("https://files.test/data", dest)

    assert dest.read_bytes() == content
    assert result.checksum is not None and result.checksum.startswith("sha256:")
    assert result.reused is False


@pytest.mark.asyncio
@respx.mock
async def test_async_download_skips_existing(tmp_path: Path) -> None:
    dest = tmp_path / "existing.bin"
    dest.write_bytes(b"cached")

    respx.get("https://files.test/data").mock(
        return_value=httpx.Response(200, content=b"new")
    )

    client = asset_client.AssetDownloadClient()
    result = await client.download("https://files.test/data", dest, skip_if_exists=True)

    assert result.path == dest
    assert result.checksum is not None
    assert result.reused is True
    assert respx.calls.call_count == 0


@pytest.mark.asyncio
async def test_download_asset_disallowed_in_running_loop(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        asset_client.download_asset("https://example.com", tmp_path / "file.bin")


@respx.mock
def test_download_asset_runs_event_loop(tmp_path: Path) -> None:
    respx.get("https://files.test/sync").mock(
        return_value=httpx.Response(200, content=b"sync")
    )

    dest = tmp_path / "sync.bin"
    result = asset_client.download_asset("https://files.test/sync", dest)

    assert result.path.exists()
    assert result.reused is False
    dest.unlink(missing_ok=True)
    asyncio.run(asset_client.reset_shared_client())


@pytest.mark.asyncio
async def test_reset_shared_client(tmp_path: Path) -> None:
    client1 = await asset_client.get_shared_client()
    await asset_client.reset_shared_client()
    client2 = await asset_client.get_shared_client()
    assert client1 is not client2


@pytest.mark.asyncio
async def test_deprecated_aliases_emit_warning() -> None:
    await asset_client.reset_shared_client()
    with pytest.deprecated_call():
        client = await asset_client.get_async_client()
    assert isinstance(client, asset_client.AssetDownloadClient)
    with pytest.deprecated_call():
        await asset_client.reset_async_client()


@pytest.mark.asyncio
@respx.mock
async def test_cancelled_download_cleans_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    respx.get("https://files.test/cancel").mock(
        return_value=httpx.Response(200, content=b"delayed")
    )

    client = asset_client.AssetDownloadClient()
    dest = tmp_path / "cancel.bin"

    async def fake_stream(
        self: asset_client.AssetDownloadClient, response: httpx.Response, path: Path
    ) -> None:  # type: ignore[override]
        path.write_bytes(b"partial")
        await asyncio.sleep(0.2)

    monkeypatch.setattr(
        asset_client.AssetDownloadClient,
        "_stream_response_to_file",
        fake_stream,
        raising=False,
    )

    task = asyncio.create_task(client.download("https://files.test/cancel", dest))
    await asyncio.sleep(0)  # Let the request start
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert not dest.exists()


@pytest.mark.asyncio
@respx.mock
async def test_failed_download_does_not_cache_partial_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter(
        [
            httpx.Response(200, content=b"data"),
            httpx.Response(200, content=b"fresh"),
        ]
    )
    route = respx.get("https://files.test/fail").mock(
        side_effect=lambda request: next(responses)
    )
    client = asset_client.AssetDownloadClient()
    dest = tmp_path / "asset.bin"
    original_stream = asset_client.AssetDownloadClient._stream_response_to_file

    async def boom(
        self: asset_client.AssetDownloadClient, response: httpx.Response, path: Path
    ) -> None:  # type: ignore[override]
        raise OSError("disk full")

    monkeypatch.setattr(
        asset_client.AssetDownloadClient,
        "_stream_response_to_file",
        boom,
        raising=False,
    )

    with pytest.raises(OSError):
        await client.download("https://files.test/fail", dest)

    assert not dest.exists()
    assert route.call_count == 1

    monkeypatch.setattr(
        asset_client.AssetDownloadClient,
        "_stream_response_to_file",
        original_stream,
        raising=False,
    )
    result = await client.download("https://files.test/fail", dest)

    assert route.call_count == 2
    assert result.path == dest
    assert dest.read_bytes() == b"fresh"


@pytest.mark.asyncio
async def test_asset_client_context_manager_calls_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[bool] = []

    async def fake_close(self: asset_client.AssetDownloadClient) -> None:
        called.append(True)

    monkeypatch.setattr(
        asset_client.AssetDownloadClient, "close", fake_close, raising=False
    )

    async with asset_client.AssetDownloadClient() as client:
        assert isinstance(client, asset_client.AssetDownloadClient)

    assert called == [True]


class _DummyResponse:
    def __init__(self, payload: bytes = b"payload") -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    async def aiter_bytes(self):
        yield self._payload


class _DummyAsyncClient:
    def __init__(self, sequence: list[object]) -> None:
        self.sequence = list(sequence)
        self.stream_calls = 0

    def stream(self, *_args, **_kwargs):
        client = self

        class _StreamCtx:
            async def __aenter__(self_inner):
                client.stream_calls += 1
                if not client.sequence:
                    raise AssertionError("sequence exhausted")
                item = client.sequence.pop(0)
                if isinstance(item, Exception):
                    raise item
                return item

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

        return _StreamCtx()

    async def aclose(self) -> None:
        return None


@pytest.mark.asyncio
async def test_download_retries_then_succeeds_without_checksum(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    request = httpx.Request("GET", "https://files.test/retry")
    failure = httpx.HTTPStatusError(
        "fail", request=request, response=httpx.Response(503, request=request)
    )
    success = _DummyResponse(b"fresh-bytes")
    dummy_client = _DummyAsyncClient([failure, success])
    monkeypatch.setattr(
        asset_client.httpx, "AsyncClient", lambda *args, **kwargs: dummy_client
    )

    warnings: list[dict[str, object] | None] = []
    monkeypatch.setattr(
        asset_client.logger,
        "warning",
        lambda *args, **kwargs: warnings.append(kwargs.get("extra")),
    )

    client = asset_client.AssetDownloadClient(max_retries=1)
    dest = tmp_path / "retry.bin"

    result = await client.download(
        "https://files.test/retry", dest, compute_checksum=False
    )

    assert result.checksum is None
    assert dest.read_bytes() == b"fresh-bytes"
    assert dummy_client.stream_calls == 2
    assert warnings


@pytest.mark.asyncio
async def test_download_raises_after_exhausting_retries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    request = httpx.Request("GET", "https://files.test/fail")
    failure = httpx.HTTPStatusError(
        "fail", request=request, response=httpx.Response(503, request=request)
    )
    dummy_client = _DummyAsyncClient([failure, failure])
    monkeypatch.setattr(
        asset_client.httpx, "AsyncClient", lambda *args, **kwargs: dummy_client
    )

    errors: list[dict[str, object] | None] = []
    monkeypatch.setattr(
        asset_client.logger,
        "error",
        lambda *args, **kwargs: errors.append(kwargs.get("extra")),
    )

    client = asset_client.AssetDownloadClient(max_retries=1)
    dest = tmp_path / "fail.bin"

    with pytest.raises(httpx.HTTPStatusError):
        await client.download("https://files.test/fail", dest, compute_checksum=False)

    assert not dest.exists()
    assert errors


def test_should_retry_exception_helper() -> None:
    timeout_exc = httpx.TimeoutException("boom")
    assert asset_client._should_retry_exception(timeout_exc) is True  # type: ignore[attr-defined]

    dns_exc = httpx.InvalidURL("bad")
    assert asset_client._should_retry_exception(dns_exc) is False

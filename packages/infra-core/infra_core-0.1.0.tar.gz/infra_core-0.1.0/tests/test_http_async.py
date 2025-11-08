"""Async tests for infra_core.http_async.fetch_async."""

from __future__ import annotations

import asyncio

import pytest
import respx
import httpx

from infra_core import http_async


@pytest.mark.asyncio
@respx.mock
async def test_fetch_async_success(monkeypatch: pytest.MonkeyPatch) -> None:
    route = respx.get("https://example.com/").mock(
        return_value=httpx.Response(200, text="ok")
    )

    async def fake_sleep(*_args, **_kwargs):
        return None

    monkeypatch.setattr(http_async.asyncio, "sleep", fake_sleep)

    body = await http_async.fetch_async("https://example.com/")

    assert body == "ok"
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_fetch_async_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def responder(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(503)
        return httpx.Response(200, text="done")

    respx.get("https://retry.me/").mock(side_effect=responder)

    async def fake_sleep(*_args, **_kwargs):
        return None

    monkeypatch.setattr(http_async.asyncio, "sleep", fake_sleep)

    result = await http_async.fetch_async("https://retry.me/", max_retries=2)

    assert result == "done"
    assert calls == 2


@pytest.mark.asyncio
@respx.mock
async def test_fetch_async_raises_after_non_retryable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    respx.get("https://fail.me/").mock(return_value=httpx.Response(404))

    async def fake_sleep(*_args, **_kwargs):
        return None

    monkeypatch.setattr(http_async.asyncio, "sleep", fake_sleep)

    with pytest.raises(httpx.HTTPStatusError):
        await http_async.fetch_async("https://fail.me/", max_retries=1)


@pytest.mark.asyncio
async def test_fetch_async_reuses_shared_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummyResponse:
        def __init__(self, text: str = "ok") -> None:
            self.text = text

        def raise_for_status(self) -> None:
            return None

    class DummyClient:
        instances = []

        def __init__(self, follow_redirects: bool = True) -> None:
            self.follow_redirects = follow_redirects
            self.closed = False
            DummyClient.instances.append(self)

        async def get(self, *args, **kwargs):
            return DummyResponse()

        async def aclose(self) -> None:
            self.closed = True

    # Use a fresh client manager so we don't interfere with other tests.
    http_async.reset_shared_http_client()
    monkeypatch.setattr(http_async.httpx, "AsyncClient", DummyClient)

    await http_async.fetch_async("https://dummy.local")
    await http_async.fetch_async("https://dummy.local/second")

    assert len(DummyClient.instances) == 1
    await http_async.close_async_http_client()
    http_async.reset_shared_http_client()


@pytest.mark.asyncio
async def test_close_async_http_client_disposes_underlying_client() -> None:
    class DummyClient:
        def __init__(self) -> None:
            self.closed = False

        async def aclose(self) -> None:
            self.closed = True

    http_async.reset_shared_http_client()
    dummy = DummyClient()
    client_manager = http_async.get_shared_http_client()
    client_manager._client = dummy  # type: ignore[attr-defined]

    await http_async.close_async_http_client()

    assert dummy.closed is True
    assert client_manager._client is None  # type: ignore[attr-defined]


@pytest.mark.asyncio
@respx.mock
async def test_reconfigure_shared_http_client_applies_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummyResponse:
        def __init__(self) -> None:
            self.text = "ok"

        def raise_for_status(self) -> None:
            return None

    class DummyClient:
        instances = []

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            DummyClient.instances.append(self)

        async def get(self, *args, **kwargs):
            return DummyResponse()

        async def aclose(self) -> None:
            return None

    respx.get("https://config.local/").mock(return_value=httpx.Response(200, text="ok"))

    http_async.reset_shared_http_client()
    monkeypatch.setattr(http_async.httpx, "AsyncClient", DummyClient)

    await http_async.reconfigure_shared_http_client(
        base_url="https://config.local", http2=True
    )
    await http_async.fetch_async("https://config.local/")

    assert DummyClient.instances[-1].kwargs["base_url"] == "https://config.local"
    assert DummyClient.instances[-1].kwargs["http2"] is True

    await http_async.close_async_http_client()
    http_async.reset_shared_http_client()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_async_handles_concurrent_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def responder(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        calls.append(str(request.url))
        return httpx.Response(200, text="ok")

    respx.get("https://concurrent.local/one").mock(side_effect=responder)
    respx.get("https://concurrent.local/two").mock(side_effect=responder)

    async def fake_sleep(*_args, **_kwargs):
        return None

    monkeypatch.setattr(http_async.asyncio, "sleep", fake_sleep)

    http_async.reset_shared_http_client()

    results = await asyncio.gather(
        http_async.fetch_async("https://concurrent.local/one"),
        http_async.fetch_async("https://concurrent.local/two"),
    )

    assert results == ["ok", "ok"]
    assert sorted(calls) == [
        "https://concurrent.local/one",
        "https://concurrent.local/two",
    ]
    await http_async.close_async_http_client()
    http_async.reset_shared_http_client()


@pytest.mark.asyncio
async def test_async_http_client_context_manager_closes_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummyClient:
        def __init__(self) -> None:
            self.closed = False

        async def aclose(self) -> None:
            self.closed = True

    created: list[DummyClient] = []

    def factory(**_kwargs):
        client = DummyClient()
        created.append(client)
        return client

    monkeypatch.setattr(http_async.httpx, "AsyncClient", factory)

    manager = http_async.AsyncHttpClient()
    async with manager as client:
        assert client is created[0]

    assert created[0].closed is True
    assert manager._client is None  # type: ignore[attr-defined]


@pytest.mark.asyncio
@respx.mock
async def test_fetch_async_delay_occurs_before_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timeline: list[tuple[str, float | str]] = []

    async def fake_sleep(duration: float):
        timeline.append(("sleep", duration))

    def responder(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        timeline.append(("request", str(request.url)))
        return httpx.Response(200, text="ok")

    respx.get("https://delay.local/").mock(side_effect=responder)
    monkeypatch.setattr(http_async.asyncio, "sleep", fake_sleep)

    body = await http_async.fetch_async("https://delay.local/", delay=1.5)

    assert body == "ok"
    assert timeline[0] == ("sleep", 1.5)
    assert timeline[1] == ("request", "https://delay.local/")


@pytest.mark.asyncio
async def test_fetch_async_retries_timeout_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummyResponse:
        def __init__(self) -> None:
            self.text = "success"

        def raise_for_status(self) -> None:
            return None

    class TimeoutThenSuccessClient:
        def __init__(self) -> None:
            self.calls = 0

        async def get(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise httpx.TimeoutException("boom")
            return DummyResponse()

        async def aclose(self) -> None:
            return None

    custom_manager = http_async.AsyncHttpClient()
    custom_manager._client = TimeoutThenSuccessClient()  # type: ignore[attr-defined]

    async def fake_sleep(*_args, **_kwargs):
        return None

    monkeypatch.setattr(http_async.asyncio, "sleep", fake_sleep)

    body = await http_async.fetch_async(
        "https://timeout.local/",
        client=custom_manager,
        max_retries=2,
    )

    assert body == "success"
    assert custom_manager._client.calls == 2  # type: ignore[attr-defined]
    await custom_manager.close()


@pytest.mark.asyncio
async def test_fetch_async_does_not_retry_invalid_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class InvalidURLClient:
        def __init__(self) -> None:
            self.calls = 0

        async def get(self, *args, **kwargs):
            self.calls += 1
            raise httpx.InvalidURL("bad url")

        async def aclose(self) -> None:
            return None

    custom_manager = http_async.AsyncHttpClient()
    custom_manager._client = InvalidURLClient()  # type: ignore[attr-defined]

    async def fake_sleep(*_args, **_kwargs):
        return None

    monkeypatch.setattr(http_async.asyncio, "sleep", fake_sleep)

    with pytest.raises(httpx.InvalidURL):
        await http_async.fetch_async(
            "https://invalid.local/",
            client=custom_manager,
            max_retries=3,
        )

    assert custom_manager._client.calls == 1  # type: ignore[attr-defined]
    await custom_manager.close()


@pytest.mark.asyncio
async def test_fetch_async_accepts_custom_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummyResponse:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            return None

    class DummyClient:
        def __init__(self) -> None:
            self.calls = 0

        async def get(self, *args, **kwargs):
            self.calls += 1
            return DummyResponse("custom")

        async def aclose(self) -> None:
            return None

    custom_manager = http_async.AsyncHttpClient()
    custom_manager._client = DummyClient()  # type: ignore[attr-defined]

    result = await http_async.fetch_async(
        "https://custom.local/", client=custom_manager
    )

    assert result == "custom"
    assert custom_manager._client.calls == 1  # type: ignore[attr-defined]
    await custom_manager.close()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_async_backoff_is_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def responder(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(503)
        return httpx.Response(200, text="done")

    respx.get("https://backoff.local/").mock(side_effect=responder)

    recorded: list[float] = []

    async def fake_sleep(duration: float):
        recorded.append(duration)

    monkeypatch.setattr(http_async.asyncio, "sleep", fake_sleep)

    result = await http_async.fetch_async(
        "https://backoff.local/",
        max_retries=3,
        backoff=10.0,
        max_backoff=0.25,
    )

    assert result == "done"
    assert recorded == [0.25]

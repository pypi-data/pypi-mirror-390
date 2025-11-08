"""Unit tests for infra_core.http.fetch."""

from __future__ import annotations

import pytest
import requests

from infra_core import http


@pytest.fixture(autouse=True)
def _disable_tenacity_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tenacity.nap.sleep", lambda *args, **kwargs: None)


class DummyResponse:
    def __init__(self, text: str = "OK", status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if 400 <= self.status_code:
            response = requests.Response()
            response.status_code = self.status_code
            raise requests.HTTPError(response=response)


class DummyClient:
    def __init__(self, responses: list[object]) -> None:
        self._responses = responses
        self.calls: list[str] = []
        self.closed = False

    def get(
        self, url: str, *, headers: dict[str, str], timeout: int
    ) -> requests.Response:
        self.calls.append(url)
        if not self._responses:
            raise AssertionError("No more responses queued")
        item = self._responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item  # type: ignore[return-value]

    def close(self) -> None:
        self.closed = True


def test_fetch_returns_body(monkeypatch: pytest.MonkeyPatch) -> None:
    client = DummyClient([DummyResponse("payload", 200)])
    body = http.fetch("https://example.com", client=client)
    assert body == "payload"
    assert client.calls == ["https://example.com"]


def test_fetch_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    response = requests.Response()
    response.status_code = 503
    client = DummyClient(
        [requests.HTTPError(response=response), DummyResponse("ok", 200)]
    )
    body = http.fetch("https://retry.me", max_retries=2, client=client)
    assert body == "ok"
    assert len(client.calls) == 2


def test_fetch_raises_after_non_retryable_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = requests.Response()
    response.status_code = 404
    client = DummyClient([requests.HTTPError(response=response)])
    with pytest.raises(requests.HTTPError):
        http.fetch("https://fail.me", max_retries=1, client=client)


def test_fetch_respects_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_calls: list[float] = []
    monkeypatch.setattr(
        http.time, "sleep", lambda duration: sleep_calls.append(duration)
    )
    client = DummyClient([DummyResponse("body", 200)])
    http.fetch("https://example.com", delay=0.5, client=client)
    assert sleep_calls and sleep_calls[0] == 0.5


def test_fetch_retries_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    client = DummyClient([requests.Timeout(), DummyResponse("ok", 200)])
    body = http.fetch("https://timeout.me", max_retries=1, client=client)
    assert body == "ok"
    assert len(client.calls) == 2


def test_fetch_does_not_retry_transport_error() -> None:
    client = DummyClient([requests.URLRequired("bad")])
    with pytest.raises(requests.URLRequired):
        http.fetch("https://bad", client=client)
    assert len(client.calls) == 1


def test_fetch_honors_custom_retry_statuses() -> None:
    response = requests.Response()
    response.status_code = 418
    client = DummyClient(
        [requests.HTTPError(response=response), DummyResponse("tea", 200)]
    )
    body = http.fetch("https://brew", retry_statuses={418}, client=client)
    assert body == "tea"


def test_fetch_backoff_is_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    response = requests.Response()
    response.status_code = 503
    client = DummyClient(
        [requests.HTTPError(response=response), DummyResponse("ok", 200)]
    )
    waits: list[float | None] = []

    def fake_warning(*args, **kwargs):
        waits.append(kwargs.get("extra", {}).get("wait"))

    monkeypatch.setattr(http.logger, "warning", fake_warning)
    http.fetch(
        "https://cap.me", max_retries=1, backoff=10.0, max_backoff=0.25, client=client
    )
    assert waits[0] == 0.25


def test_get_shared_http_client_reset() -> None:
    first = http.get_shared_http_client()
    http.reset_shared_http_client()
    second = http.get_shared_http_client()
    assert first is not second


def test_requests_http_client_context_manager_closes_session() -> None:
    class DummySession:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

        def get(self, *args, **kwargs):
            return DummyResponse()

    session = DummySession()

    def factory() -> requests.Session:  # type: ignore[return-value]
        return session  # type: ignore[return-value]

    with http.RequestsHttpClient(session_factory=factory) as client:
        client.get("https://example.com", headers={}, timeout=1)

    assert session.closed is True

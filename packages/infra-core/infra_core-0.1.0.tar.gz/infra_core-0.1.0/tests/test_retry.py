"""Unit tests for infra_core.retry helpers."""

from __future__ import annotations


import pytest

from infra_core.retry import (
    AsyncRetryConfig,
    run_with_retries,
    run_with_retries_sync,
    should_retry_http_exception,
    should_retry_requests_exception,
)


class DummyError(Exception):
    pass


@pytest.mark.asyncio  # type: ignore[misc]
async def test_run_with_retries_success_after_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise DummyError("boom")
        return "ok"

    config = AsyncRetryConfig.create(max_retries=2, backoff=0.01, max_backoff=0.01)

    def predicate(exc: BaseException) -> bool:
        return isinstance(exc, DummyError)

    result = await run_with_retries(operation, config=config, should_retry=predicate)

    assert result == "ok"
    assert attempts == 2


@pytest.mark.asyncio  # type: ignore[misc]
async def test_run_with_retries_raises_after_exhaustion() -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        raise DummyError("fail")

    config = AsyncRetryConfig.create(max_retries=1, backoff=0.01, max_backoff=0.01)

    with pytest.raises(DummyError):
        await run_with_retries(operation, config=config, should_retry=lambda exc: True)

    assert attempts == 2  # initial + one retry


def test_run_with_retries_sync_success() -> None:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise DummyError
        return "done"

    config = AsyncRetryConfig.create(max_retries=2, backoff=0.01, max_backoff=0.01)

    result = run_with_retries_sync(
        operation, config=config, should_retry=lambda exc: True
    )

    assert result == "done"
    assert attempts == 2


def test_should_retry_http_exception_filters_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import httpx

    retryable = should_retry_http_exception(
        httpx.HTTPStatusError("boom", request=None, response=httpx.Response(503)),
        retryable_statuses={503},
        transport_predicate=lambda exc: False,
    )
    non_retryable = should_retry_http_exception(
        httpx.HTTPStatusError("fail", request=None, response=httpx.Response(404)),
        retryable_statuses={503},
        transport_predicate=lambda exc: False,
    )

    assert retryable is True
    assert non_retryable is False


def test_should_retry_requests_exception_filters_status() -> None:
    import requests

    response = requests.Response()
    response.status_code = 503
    retry_exc = requests.HTTPError(response=response)

    response_404 = requests.Response()
    response_404.status_code = 404
    non_retry_exc = requests.HTTPError(response=response_404)

    assert should_retry_requests_exception(
        retry_exc,
        retryable_statuses={503},
        transport_predicate=lambda exc: False,
    )
    assert not should_retry_requests_exception(
        non_retry_exc,
        retryable_statuses={503},
        transport_predicate=lambda exc: False,
    )

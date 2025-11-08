"""Tests for infra_core.task_runtime.TaskRuntime."""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Iterable, List

import pytest

from infra_core.task_runtime import RuntimeCancellationError, RuntimeConfig, TaskRuntime


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_runs_all_tasks() -> None:
    processed: List[str] = []

    async def worker(identifier: str) -> None:
        await asyncio.sleep(0)
        processed.append(identifier)

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=2, task_timeout=1.0))
    tasks = [(str(i), lambda i=i: worker(str(i))) for i in range(5)]

    await runtime.run(tasks)

    assert sorted(processed) == ["0", "1", "2", "3", "4"]


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_invokes_timeout_callback() -> None:
    triggered: List[str] = []

    async def slow_task() -> None:
        await asyncio.sleep(0.05)

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=1, task_timeout=0.01))

    async def on_timeout(task_id: str) -> None:
        triggered.append(task_id)

    tasks = [("slow", slow_task)]

    await runtime.run(tasks, on_timeout=on_timeout)

    assert triggered == ["slow"]


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_propagates_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    triggered: List[str] = []

    async def err_task() -> None:
        raise RuntimeError("boom")

    async def on_error(task_id: str, exc: Exception) -> None:
        triggered.append(f"{task_id}:{exc}")

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=1, task_timeout=None))

    await runtime.run([("err", err_task)], on_error=on_error)

    assert triggered and triggered[0].startswith("err:boom")


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_raises_when_no_on_error_callback() -> None:
    async def err_task() -> None:
        raise RuntimeError("explode")

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=1))

    with pytest.raises(RuntimeError):
        await runtime.run([("err", err_task)])


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_raises_timeout_when_no_callback() -> None:
    async def slow_task() -> None:
        await asyncio.sleep(0.05)

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=1, task_timeout=0.01))

    with pytest.raises(asyncio.TimeoutError):
        await runtime.run([("slow", slow_task)])


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_cancel() -> None:
    async def task() -> None:
        await asyncio.sleep(0)

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=1))
    runtime.cancel()

    with pytest.raises(RuntimeCancellationError):
        await runtime.run([("t", task)])


def test_runtime_supports_multiple_event_loops() -> None:
    runtime = TaskRuntime(config=RuntimeConfig(concurrency=1))

    async def runner(name: str) -> None:
        await runtime.run([(name, lambda: asyncio.sleep(0))])

    asyncio.run(runner("first"))
    asyncio.run(runner("second"))


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_context_manager_runs_tasks() -> None:
    processed: list[str] = []

    async def worker() -> None:
        processed.append("ran")

    async with TaskRuntime(config=RuntimeConfig(concurrency=1)) as runtime:
        await runtime.run([("job", worker)])

    assert processed == ["ran"]


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_sync_callbacks_supported() -> None:
    timeouts: list[str] = []
    errors: list[str] = []

    async def slow() -> None:
        await asyncio.sleep(0.05)

    async def boom() -> None:
        raise RuntimeError("boom")

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=2, task_timeout=0.01))

    def on_timeout(task_id: str) -> None:
        timeouts.append(task_id)

    def on_error(task_id: str, exc: Exception) -> None:
        errors.append(f"{task_id}:{exc}")

    await runtime.run(
        [("slow", slow), ("err", boom)], on_timeout=on_timeout, on_error=on_error
    )

    assert timeouts == ["slow"]
    assert errors and errors[0].startswith("err:boom")


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_enforces_concurrency_limit() -> None:
    running = 0
    max_running = 0

    async def worker() -> None:
        nonlocal running, max_running
        running += 1
        max_running = max(max_running, running)
        await asyncio.sleep(0.01)
        running -= 1

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=2))
    tasks = [(str(i), worker) for i in range(5)]
    await runtime.run(tasks)

    assert max_running <= 2


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_cancel_during_run() -> None:
    async def canceller(runtime: TaskRuntime) -> None:
        runtime.cancel()

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=1))
    tasks = [
        ("first", lambda: canceller(runtime)),
        ("second", lambda: asyncio.sleep(0)),
    ]
    with pytest.raises(RuntimeCancellationError):
        await runtime.run(tasks)


def test_runtime_config_validation() -> None:
    with pytest.raises(ValueError):
        RuntimeConfig(concurrency=0)
    with pytest.raises(ValueError):
        RuntimeConfig(task_timeout=0)
    with pytest.raises(ValueError):
        RuntimeConfig(cancel_grace=0)


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_cancel_interrupts_running_tasks() -> None:
    runtime = TaskRuntime(config=RuntimeConfig(concurrency=2))
    started = asyncio.Event()
    running = 0

    async def worker() -> None:
        nonlocal running
        running += 1
        if running >= 2:
            started.set()
        await asyncio.Event().wait()

    run_task = asyncio.create_task(runtime.run([("a", worker), ("b", worker)]))
    await started.wait()
    runtime.cancel()
    with pytest.raises(RuntimeCancellationError):
        await asyncio.wait_for(run_task, timeout=1.0)


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_runtime_consumes_tasks_lazily() -> None:
    concurrency = 2
    runtime = TaskRuntime(config=RuntimeConfig(concurrency=concurrency))
    consumed = 0
    started = asyncio.Event()
    start_counter = 0
    release = asyncio.Event()

    async def worker() -> None:
        nonlocal start_counter
        start_counter += 1
        if start_counter == concurrency:
            started.set()
        await release.wait()

    def make_tasks() -> Iterable[tuple[str, Callable[[], Awaitable[None]]]]:
        nonlocal consumed
        for i in range(10):
            consumed += 1
            yield (f"job-{i}", worker)

    run_task = asyncio.create_task(runtime.run(make_tasks()))
    await asyncio.wait_for(started.wait(), timeout=1.0)
    assert consumed == concurrency
    release.set()
    await run_task

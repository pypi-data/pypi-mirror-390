"""Task-oriented asyncio runtime that enforces concurrency, timeouts, and cooperative cancellation.

Core value:
- Run many async jobs with a bounded semaphore so slow tasks cannot starve the loop.
- Enforce per-task time budgets and surface timeouts through structured callbacks.
- Provide a single cancellation signal that callers can trigger (graceful shutdowns, Ctrl+C, etc.).
- Power multiple production crawlers (Awwwards, Azure Functions) where predictable parallelism is critical.

Example – basic execution::

    runtime = TaskRuntime(config=RuntimeConfig(concurrency=5, task_timeout=30.0))
    tasks = [(slug, lambda slug=slug: fetch_site(slug)) for slug in slugs]
    await runtime.run(tasks)

Example – with callbacks::

    async def on_timeout(task_id: str) -> None:
        metrics.increment("site.timeout", tags={"task": task_id})

    await runtime.run(tasks, on_timeout=on_timeout, on_error=log_failure)

Example – context manager::

    async with TaskRuntime(config=RuntimeConfig(concurrency=workers)) as runtime:
        await runtime.run(tasks)

Example – cooperative cancellation::

    runtime.cancel()  # Signal all in-flight jobs to wind down

Key features:
- Bounded concurrency via ``asyncio.Semaphore``
- Optional per-task timeout using ``asyncio.timeout``
- Sync/async callbacks for timeout & error handling
- Lazy event/semaphore binding so the runtime can be reused across event loops
- Context manager for automatic cleanup

Real-world usage: orchestrating concurrent site crawls, screenshot capture pipelines, and Azure Functions that process batches of URLs.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass
from types import TracebackType
from typing import Awaitable, Callable, Iterable

logger = logging.getLogger(__name__)

OnTimeoutCallback = Callable[[str], Awaitable[None] | None] | None
OnErrorCallback = Callable[[str, Exception], Awaitable[None] | None] | None


class RuntimeCancellationError(RuntimeError):
    """Raised when the runtime receives an explicit cancellation request."""


@dataclass(slots=True)
class RuntimeConfig:
    """Configuration for :class:`TaskRuntime`.

    Attributes:
        concurrency: Maximum number of tasks to process concurrently.
        task_timeout: Optional per-task timeout (seconds). ``None`` disables the timeout.
        cancel_grace: Seconds to wait for in-flight tasks to finish cleanup after cancellation.
    """

    concurrency: int = 1
    task_timeout: float | None = None
    cancel_grace: float = 2.0

    def __post_init__(self) -> None:
        if self.concurrency <= 0:
            raise ValueError("concurrency must be positive")
        if self.task_timeout is not None and self.task_timeout <= 0:
            raise ValueError("task_timeout must be positive when provided")
        if self.cancel_grace <= 0:
            raise ValueError("cancel_grace must be positive")


class TaskRuntime:
    """Coordinates concurrent task execution with cooperative cancellation."""

    def __init__(
        self,
        *,
        config: RuntimeConfig,
        cancel_event: asyncio.Event | None = None,
    ) -> None:
        self._config = config
        self._external_cancel_event = cancel_event
        self._cancel_event: asyncio.Event | None = None
        self._cancel_event_loop: asyncio.AbstractEventLoop | None = None
        self._semaphore: asyncio.Semaphore | None = None
        self._semaphore_loop: asyncio.AbstractEventLoop | None = None
        self._active_tasks: set[asyncio.Task[None]] = set()
        self._active_tasks_loop: asyncio.AbstractEventLoop | None = None
        self._pending_cancel_wait: asyncio.Task[None] | None = None

    def cancel(self) -> None:
        """Signal cancellation. Active tasks should honour this asynchronously."""

        cancel_event = self._get_cancel_event()
        if cancel_event.is_set():
            return
        cancel_event.set()
        tasks = list(self._active_tasks)
        for task in tasks:
            task.cancel()
        loop = self._active_tasks_loop
        if loop is None or loop.is_closed():
            return
        if self._pending_cancel_wait is None or self._pending_cancel_wait.done():
            self._pending_cancel_wait = loop.create_task(self._await_active_tasks())

    async def __aenter__(self) -> "TaskRuntime":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Release resources and cancel outstanding tasks."""

        self.cancel()

    async def run(
        self,
        tasks: Iterable[tuple[str, Callable[[], Awaitable[None]]]],
        *,
        on_timeout: OnTimeoutCallback = None,
        on_error: OnErrorCallback = None,
    ) -> None:
        """Execute ``tasks`` concurrently with timeout/error callbacks.

        Args:
            tasks: Iterable of ``(task_id, task_fn)`` tuples. Each task_fn must
                be a callable returning an awaitable.
            on_timeout: Optional callback invoked when a task hits the timeout.
                Accepts ``task_id`` and may be sync or async.
            on_error: Optional callback invoked when a task raises an exception.
                Accepts ``(task_id, exc)`` and may be sync or async.

        Raises:
            RuntimeCancellationError: If the runtime is cancelled while tasks are running.
        """
        inflight: set[asyncio.Task[None]] = set()
        task_iter = iter(tasks)

        def _start_next() -> bool:
            try:
                task_id, fn = next(task_iter)
            except StopIteration:
                return False
            task = self._create_tracked_task(task_id, fn, on_timeout, on_error)
            inflight.add(task)
            return True

        for _ in range(self._config.concurrency):
            if not _start_next():
                break

        if not inflight:
            return

        try:
            while inflight:
                done, _ = await asyncio.wait(
                    inflight, return_when=asyncio.FIRST_COMPLETED
                )
                for finished in done:
                    inflight.discard(finished)
                    try:
                        finished.result()
                    except RuntimeCancellationError:
                        await self._await_active_tasks()
                        raise
                    except asyncio.CancelledError as exc:
                        await self._await_active_tasks()
                        raise RuntimeCancellationError("runtime cancelled") from exc
                while len(inflight) < self._config.concurrency and _start_next():
                    pass
        except RuntimeCancellationError:
            self.cancel()
            await self._await_active_tasks()
            raise

    async def _run_task(
        self,
        task_id: str,
        fn: Callable[[], Awaitable[None]],
        on_timeout: OnTimeoutCallback,
        on_error: OnErrorCallback,
    ) -> None:
        semaphore = self._get_semaphore()
        try:
            async with semaphore:
                if self._get_cancel_event().is_set():
                    raise RuntimeCancellationError("runtime cancelled")
                try:
                    if self._config.task_timeout:
                        async with asyncio.timeout(self._config.task_timeout):
                            await fn()
                    else:
                        await fn()
                except RuntimeCancellationError:
                    raise
                except asyncio.TimeoutError:
                    await self._invoke_callback(on_timeout, task_id)
                    if on_timeout is None:
                        raise
                except Exception as exc:  # pragma: no cover - defensive
                    logger.exception("Unexpected error processing %s", task_id)
                    await self._invoke_callback(on_error, task_id, exc)
                    if on_error is None:
                        raise
        except asyncio.CancelledError as exc:
            raise RuntimeCancellationError("runtime cancelled") from exc

    async def _invoke_callback(
        self,
        callback: Callable[..., Awaitable[None] | None] | None,
        *args: object,
    ) -> None:
        if callback is None:
            return
        try:
            result = callback(*args)
            if inspect.isawaitable(result):
                await result
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Callback %r raised an exception", callback)

    def _get_cancel_event(self) -> asyncio.Event:
        if self._external_cancel_event is not None:
            return self._external_cancel_event
        loop = asyncio.get_running_loop()
        if self._cancel_event is None or self._cancel_event_loop is not loop:
            self._cancel_event = asyncio.Event()
            self._cancel_event_loop = loop
        return self._cancel_event

    def _get_semaphore(self) -> asyncio.Semaphore:
        loop = asyncio.get_running_loop()
        if self._semaphore is None or self._semaphore_loop is not loop:
            self._semaphore = asyncio.Semaphore(self._config.concurrency)
            self._semaphore_loop = loop
        return self._semaphore

    def _track_active_task(self, task: asyncio.Task[None]) -> None:
        loop = asyncio.get_running_loop()
        if self._active_tasks_loop is not loop:
            self._active_tasks = set()
            self._active_tasks_loop = loop
        self._active_tasks.add(task)

        def _cleanup(completed: asyncio.Task[None]) -> None:
            self._active_tasks.discard(completed)

        task.add_done_callback(_cleanup)

    def _create_tracked_task(
        self,
        task_id: str,
        fn: Callable[[], Awaitable[None]],
        on_timeout: OnTimeoutCallback,
        on_error: OnErrorCallback,
    ) -> asyncio.Task[None]:
        task = asyncio.create_task(self._run_task(task_id, fn, on_timeout, on_error))
        self._track_active_task(task)
        return task

    async def _await_active_tasks(self) -> None:
        if not self._active_tasks:
            return
        pending = [task for task in self._active_tasks if not task.done()]
        if not pending:
            return
        try:
            _, still_pending = await asyncio.wait(
                pending, timeout=self._config.cancel_grace
            )
        except asyncio.CancelledError:
            return
        if still_pending:
            task_names = [
                task.get_name() if hasattr(task, "get_name") else repr(task)
                for task in still_pending
            ]
            sample = ", ".join(task_names[:5])
            logger.warning(
                "Cancellation grace period (%.1fs) expired with %d task(s) still running%s",
                self._config.cancel_grace,
                len(still_pending),
                f": {sample}" if sample else "",
            )

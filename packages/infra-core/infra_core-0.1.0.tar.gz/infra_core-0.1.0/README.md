# Infra Core

[![PyPI](https://img.shields.io/pypi/v/infra-core.svg)](https://pypi.org/project/infra-core/)
[![Python Versions](https://img.shields.io/pypi/pyversions/infra-core.svg)](https://pypi.org/project/infra-core/)
[![Build Status](https://github.com/pj-ms/infra-core/workflows/Build%20and%20Test/badge.svg)](https://github.com/pj-ms/infra-core/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`infra-core` contains the reusable HTTP, storage, Azure upload, and runtime helpers shared by multiple services.


## Modules

| Module                           | Purpose                                                                                                    |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `infra_core.http` / `http_async` | Request helpers with sensible defaults and retry/backoff logic.                                            |
| `infra_core.fs_utils`            | Local filesystem helpers (`ensure_parent`, `hashed_asset_path`, `compute_checksum`).                       |
| `infra_core.asset_client`        | Async asset downloader with retries, connection pooling, and checksum support.                             |
| `infra_core.azure_storage`       | Thin Azure Blob client with configurable retries and optional async wrappers.                              |
| `infra_core.task_runtime`        | Cooperative asyncio runtime (`TaskRuntime`) with per-task budgeting.                                       |

## Quick Start

### HTTP Fetching
```python
from infra_core import fetch, fetch_async

html = fetch("https://example.com", timeout=30)

async def load_async() -> str:
    return await fetch_async("https://example.com")
```

### Storage with Optional Azure Mirroring
```python
from pathlib import Path
from infra_core import AzureStorageClient, AzureStorageSettings, download_asset

settings = AzureStorageSettings.from_env()
storage = AzureStorageClient.from_settings(settings)
storage.write_json(Path("output/results.json"), {"status": "ok"})

asset_path = download_asset(
    "https://example.com/image.png",
    Path("assets/image.png"),
    skip_if_exists=True,
)
```

### Concurrent Task Runtime
```python
import asyncio
from infra_core import TaskRuntime, RuntimeConfig

async def process(item: str) -> None:
    ...

async def main() -> None:
    runtime = TaskRuntime(config=RuntimeConfig(concurrency=5, task_timeout=30.0))
    tasks = [(item, lambda item=item: process(item)) for item in ["a", "b", "c"]]
    await runtime.run(tasks)

asyncio.run(main())
```

#### Task Runtime Semantics

`TaskRuntime` enforces the configured concurrency per `run()` call by limiting the `inflight` set of tasks it schedules at once. A separate `_active_tasks` set tracks all tasks spawned across overlapping `run()` calls so that a single `cancel()` sweeps everything that is currently executing. As a result `_active_tasks` can temporarily exceed `config.concurrency`, which is expected and keeps cancellation comprehensive while each `run()` call still honours the configured bound.

By default, any task exception (including per-task timeouts) is propagated back to the caller so failure is obvious. Supplying `on_error` and/or `on_timeout` callbacks opts you into best-effort mode where the runtime reports failures via callbacks and continues processing the remaining tasks.

## Installation

Using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv pip install infra-core
```

Install with Azure helpers:

```bash
uv pip install "infra-core[azure]"
```

Or using pip:

```bash
pip install infra-core
pip install "infra-core[azure]"  # with Azure support
```

## Tests

```bash
pytest tests -v
```

Or with coverage:

```bash
pytest tests -v --cov=infra_core --cov-report=term-missing
```

## Configuration

### Azure Storage (Optional)

When Azure credentials are provided, `infra_core` mirrors files written via helpers such as `write_json`, `write_text`, and their async counterparts.

**Required**
- `AZURE_STORAGE_CONTAINER` – Target container name.

**Authentication (choose one)**
- `AZURE_STORAGE_CONNECTION_STRING` – Full connection string; or
- `AZURE_STORAGE_ACCOUNT` – Storage account name (uses DefaultAzureCredential)
  - `AZURE_STORAGE_BLOB_ENDPOINT` – Optional custom endpoint.

**Optional**
- `AZURE_STORAGE_BLOB_PREFIX` – Prefix applied to uploaded blobs.

#### Blob Download Safety

Blob download helpers stream data into unique temp files via `tempfile.mkstemp()` (see `azure_storage._stream_blob_to_path*`). The files are placed next to the destination, created with owner-only permissions, flushed and `fsync`'d, then atomically renamed into place. This preserves original extensions, avoids collisions when multiple processes download the same blob, and prevents partially-downloaded data from clobbering the real file.

No configuration is required to use the HTTP or runtime helpers; sensible defaults are provided.


## Logging

`infra_core` uses Python's standard `logging` module. To enable diagnostics in your application:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("infra_core.asset_client").setLevel(logging.DEBUG)
```

Logger namespaces:

| Logger | Purpose |
|--------|---------|
| `infra_core.asset_client` | Download/retry lifecycle |
| `infra_core.azure_storage` | Blob uploads/downloads |
| `infra_core.task_runtime` | Concurrency and cancellation events |

All log records include structured `extra={...}` fields (e.g., `url`, `blob_name`, `attempt`). Configure your formatter (JSON or text) to emit those keys for easier filtering, and sanitize environment-specific secrets before forwarding logs.

### OpenTelemetry/trace correlation

If your application uses OpenTelemetry, start spans around infra_core operations and add span IDs to log records so traces and logs stay aligned:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("download_batch") as span:
    logger = logging.getLogger("infra_core.asset_client")
    logger.info(
        "Starting download",
        extra={
            "url": url,
            "trace_id": span.get_span_context().trace_id,
            "span_id": span.get_span_context().span_id,
        },
    )
    await download_asset_async(url, dest)
```

## Troubleshooting

- **"Azure storage not configured" warning** – Ensure `AZURE_STORAGE_CONTAINER` is set along with either `AZURE_STORAGE_CONNECTION_STRING` or `AZURE_STORAGE_ACCOUNT`. Call `AzureStorageClient.from_settings()` after loading environment variables to confirm configuration.
- **`download_asset` raises inside async code** – Use `download_asset_async` when an event loop is running; the sync helper intentionally fails inside `asyncio` contexts to avoid deadlocks.
- **Type checker cannot find infra_core stubs** – Install dev extras (`pip install .[dev]` or `uv sync --extra dev`) so `py.typed` and dependency stubs are available to mypy/pyright.
- **HTTP retries still hitting rate limits** – Pass a `delay` to `fetch`/`fetch_async` or construct a custom `RequestsHttpClient`/`AsyncHttpClient` with tuned limits and headers.
- **Large Azure uploads timing out** – Use the async helpers (they stream files) and tweak `AzureStorageClient` settings (e.g., `swallow_errors=False`, custom retry logic) to observe detailed failures.

## Contributing

Using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
git clone https://github.com/pj-ms/infra-core.git
cd infra-core
uv sync --extra azure --extra dev
uv run pytest tests -v --cov=infra_core --cov-report=term-missing
uv run mypy src/infra_core
uv run ruff check src/ tests/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Releasing

This project uses [bump-my-version](https://github.com/callowayproject/bump-my-version) for versioning.

```bash
# Bump patch version (0.1.0 -> 0.1.1)
uv run bump-my-version bump patch

# Bump minor version (0.1.0 -> 0.2.0)
uv run bump-my-version bump minor

# Bump major version (0.1.0 -> 1.0.0)
uv run bump-my-version bump major
```

This will:
1. Update version in `pyproject.toml`
2. Create a git commit
3. Create a git tag (`v0.1.1`, etc.)
4. Push tag to trigger automatic PyPI publish

Then push:
```bash
git push && git push --tags
```

## License

MIT License - see [LICENSE](LICENSE) for details.

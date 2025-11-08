"""Argparse helpers shared by Azure Function service CLIs."""

from __future__ import annotations

import argparse
from pathlib import Path


def add_azure_service_arguments(
    parser: argparse.ArgumentParser,
    *,
    base_url_env_var: str,
    base_url_help: str | None = None,
    concurrency_default: int = 4,
    include_summary: bool = True,
    summary_help: str | None = None,
) -> None:
    """Add standard Azure Function trigger arguments to a parser."""

    parser.add_argument(
        "batch_id",
        help="Batch identifier for grouping related jobs",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        help=base_url_help
        or f"Azure Function base URL (defaults to {base_url_env_var})",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=concurrency_default,
        help="Number of concurrent jobs to process (default: %(default)s)",
    )
    parser.add_argument(
        "--poll",
        action="store_true",
        help="Poll run status until completion (default: true)",
    )
    parser.add_argument(
        "--no-poll",
        dest="poll",
        action="store_false",
        help="Return immediately after scheduling the batch (no polling)",
    )
    parser.set_defaults(poll=True)
    parser.add_argument(
        "--poll-timeout",
        type=float,
        default=600.0,
        help="Maximum seconds to poll before timeout (default: %(default)s)",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=5.0,
        help="Seconds between status checks (default: %(default)s)",
    )
    if include_summary:
        parser.add_argument(
            "--summary-file",
            type=Path,
            help=summary_help or "Optional path to write JSON summary of run results",
        )

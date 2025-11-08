"""Pure filesystem helpers shared across crawler packages.

This module provides reusable filesystem operations extracted from the
former storage.py module. All functions here are pure local filesystem
operations with no Azure or remote storage dependencies.

Key features:
- Parent directory creation with mkdir -p semantics
- Content-addressed path generation using SHA256 hashing
- Memory-efficient file checksumming with chunked reading

Example:
    Generate content-addressed storage path and save a file:

    >>> from pathlib import Path
    >>> from infra_core.fs_utils import hashed_asset_path, ensure_parent
    >>> base = Path("/var/assets")
    >>> url = "https://example.com/logo.png"
    >>> path = hashed_asset_path(base, url, "logo.png")
    >>> ensure_parent(path)
    >>> path.write_bytes(b"logo data")
"""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

CHUNK_SIZE = 8192


def ensure_parent(path: Path) -> None:
    """Create parent directories for path if they do not exist.

    Implements "mkdir -p" semantics: creates all intermediate directories
    as needed and does not raise an error if directories already exist.

    Args:
        path: Target file or directory path whose parent directories should
            be created. If path is /a/b/c/file.txt, this ensures /a/b/c/ exists.

    Example:
        >>> from pathlib import Path
        >>> from infra_core.fs_utils import ensure_parent
        >>> output = Path("/tmp/deep/nested/output.json")
        >>> ensure_parent(output)  # Creates /tmp/deep/nested/ if missing
        >>> output.write_text('{"result": 42}')
    """
    path.parent.mkdir(parents=True, exist_ok=True)


def hashed_asset_path(
    base_dir: Path, key: str, filename_hint: Optional[str] = None
) -> Path:
    """Return deterministic storage path for asset derived from key.

    Creates a two-level directory structure (XX/YY) based on the first four
    characters of the SHA256 hash of key. This content-addressed approach
    ensures consistent paths for the same key and distributes files across
    directories to avoid filesystem bottlenecks.

    Args:
        base_dir: Root directory for asset storage (e.g., Path("/var/assets")).
        key: Unique identifier for the asset, typically a URL. The SHA256 hash
            of this key determines the directory structure.
        filename_hint: Desired filename for the asset (e.g., "logo.png").
            If not provided, filename is extracted from key via URL parsing
            or defaults to "asset".

    Returns:
        Full path to the asset: base_dir/XX/YY/filename where XX/YY are the
        first four hex characters of SHA256(key).

    Example:
        >>> from pathlib import Path
        >>> from infra_core.fs_utils import hashed_asset_path
        >>> base = Path("/var/assets")
        >>> url = "https://example.com/logo.png"
        >>> path = hashed_asset_path(base, url, "logo.png")
        >>> print(path)
        /var/assets/3a/b2/logo.png  # 3ab2... from SHA256(url)
    """
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    subdir = base_dir / digest[:2] / digest[2:4]
    name = filename_hint or _filename_from_key(key)
    return subdir / name


def compute_checksum(path: Path, algorithm: str = "sha256") -> str:
    """Compute cryptographic hash of file in format "algorithm:hexdigest".

    Reads file in 8KB chunks to compute hash without loading the entire
    file into memory. Safe for large files (GB+) and concurrent access
    (read-only operation).

    Args:
        path: File to compute checksum for. Must be a readable file.
        algorithm: Hash algorithm name (e.g., "sha256", "md5", "sha512").
            Must be supported by Python's hashlib module. Defaults to "sha256".

    Returns:
        Checksum string like "sha256:abc123..." (algorithm prefix + hex digest).

    Raises:
        FileNotFoundError: When path does not exist.
        ValueError: When algorithm is not supported by hashlib.

    Example:
        >>> from pathlib import Path
        >>> from infra_core.fs_utils import compute_checksum
        >>> test_file = Path("/tmp/test.txt")
        >>> test_file.write_bytes(b"Hello, world!")
        >>> checksum = compute_checksum(test_file)
        >>> print(checksum)
        sha256:315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3
    """
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            hasher.update(chunk)
    return f"{algorithm}:{hasher.hexdigest()}"


def _filename_from_key(key: str) -> str:
    parsed = urlparse(key)
    name = Path(parsed.path).name
    if name:
        return name
    guessed = mimetypes.guess_extension(parsed.scheme or "")
    return f"asset{guessed or ''}"


__all__ = ["CHUNK_SIZE", "ensure_parent", "hashed_asset_path", "compute_checksum"]

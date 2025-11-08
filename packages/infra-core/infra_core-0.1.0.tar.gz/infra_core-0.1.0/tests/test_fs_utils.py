"""Test suite for infra_core.fs_utils module."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from infra_core import fs_utils


class TestEnsureParent:
    """Tests for ensure_parent() function."""

    def test_creates_single_level(self, tmp_path: Path) -> None:
        """Test creating a single directory level."""
        target = tmp_path / "subdir" / "file.txt"
        fs_utils.ensure_parent(target)
        assert (tmp_path / "subdir").exists()
        assert (tmp_path / "subdir").is_dir()

    def test_creates_multiple_levels(self, tmp_path: Path) -> None:
        """Test creating multiple nested directory levels."""
        target = tmp_path / "a" / "b" / "c" / "d" / "file.txt"
        fs_utils.ensure_parent(target)
        assert (tmp_path / "a" / "b" / "c" / "d").exists()
        assert (tmp_path / "a" / "b" / "c" / "d").is_dir()

    def test_does_not_fail_when_parent_exists(self, tmp_path: Path) -> None:
        """Test that no error occurs if parent already exists."""
        parent = tmp_path / "existing"
        parent.mkdir()
        target = parent / "file.txt"
        fs_utils.ensure_parent(target)  # Should not raise
        assert parent.exists()

    def test_does_not_create_target_file(self, tmp_path: Path) -> None:
        """Test that only parent directories are created, not the target file."""
        target = tmp_path / "subdir" / "file.txt"
        fs_utils.ensure_parent(target)
        assert (tmp_path / "subdir").exists()
        assert not target.exists()  # File itself should not be created

    def test_handles_current_directory(self, tmp_path: Path) -> None:
        """Test handling of a file in the current directory."""
        target = tmp_path / "file.txt"
        fs_utils.ensure_parent(target)  # Parent is tmp_path, which already exists
        assert tmp_path.exists()

    def test_concurrent_creation_safe(self, tmp_path: Path) -> None:
        """Test that concurrent calls to ensure_parent are safe (exist_ok=True)."""
        target = tmp_path / "subdir" / "file.txt"
        fs_utils.ensure_parent(target)
        fs_utils.ensure_parent(target)  # Second call should not fail
        assert (tmp_path / "subdir").exists()


class TestHashedAssetPath:
    """Tests for hashed_asset_path() function."""

    def test_deterministic_path_generation(self, tmp_path: Path) -> None:
        """Test that the same key always produces the same path."""
        key = "https://example.com/image.png"
        path1 = fs_utils.hashed_asset_path(tmp_path, key, "image.png")
        path2 = fs_utils.hashed_asset_path(tmp_path, key, "image.png")
        assert path1 == path2

    def test_two_level_directory_structure(self, tmp_path: Path) -> None:
        """Test that the path has a two-level directory structure (XX/YY)."""
        key = "https://example.com/asset.png"
        path = fs_utils.hashed_asset_path(tmp_path, key, "asset.png")
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        expected = tmp_path / digest[:2] / digest[2:4] / "asset.png"
        assert path == expected

    def test_uses_filename_hint(self, tmp_path: Path) -> None:
        """Test that filename_hint is used when provided."""
        key = "https://example.com/some-url"
        path = fs_utils.hashed_asset_path(tmp_path, key, "custom.png")
        assert path.name == "custom.png"

    def test_extracts_filename_from_key_when_no_hint(self, tmp_path: Path) -> None:
        """Test filename extraction from key when no hint provided."""
        key = "https://example.com/images/logo.png"
        path = fs_utils.hashed_asset_path(tmp_path, key)
        assert path.name == "logo.png"

    def test_fallback_filename_for_keyless_url(self, tmp_path: Path) -> None:
        """Test fallback to 'asset' when no filename can be extracted."""
        key = "https://example.com/"
        path = fs_utils.hashed_asset_path(tmp_path, key)
        assert path.name == "asset"

    def test_different_keys_produce_different_paths(self, tmp_path: Path) -> None:
        """Test that different keys produce different directory structures."""
        key1 = "https://example.com/image1.png"
        key2 = "https://example.com/image2.png"
        path1 = fs_utils.hashed_asset_path(tmp_path, key1, "image.png")
        path2 = fs_utils.hashed_asset_path(tmp_path, key2, "image.png")
        assert path1.parent != path2.parent

    def test_distributes_across_directories(self, tmp_path: Path) -> None:
        """Test that different keys are distributed across different directories."""
        paths = [
            fs_utils.hashed_asset_path(tmp_path, f"key_{i}", "file.txt")
            for i in range(100)
        ]
        # Collect unique first-level directories
        first_level_dirs = {path.parent.parent.name for path in paths}
        # With 100 keys, we should see distribution (not all in same dir)
        assert len(first_level_dirs) > 1

    def test_handles_special_characters_in_key(self, tmp_path: Path) -> None:
        """Test handling of keys with special characters."""
        key = "https://example.com/path?param=value&other=123"
        path = fs_utils.hashed_asset_path(tmp_path, key, "file.png")
        assert path.name == "file.png"
        assert path.is_relative_to(tmp_path)


class TestComputeChecksum:
    """Tests for compute_checksum() function."""

    def test_sha256_default_algorithm(self, tmp_path: Path) -> None:
        """Test that sha256 is the default algorithm."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"Hello, world!")
        checksum = fs_utils.compute_checksum(test_file)
        assert checksum.startswith("sha256:")
        expected_hash = hashlib.sha256(b"Hello, world!").hexdigest()
        assert checksum == f"sha256:{expected_hash}"

    def test_md5_algorithm(self, tmp_path: Path) -> None:
        """Test using md5 algorithm."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"Test data")
        checksum = fs_utils.compute_checksum(test_file, "md5")
        assert checksum.startswith("md5:")
        expected_hash = hashlib.md5(b"Test data").hexdigest()
        assert checksum == f"md5:{expected_hash}"

    def test_sha512_algorithm(self, tmp_path: Path) -> None:
        """Test using sha512 algorithm."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"Test data")
        checksum = fs_utils.compute_checksum(test_file, "sha512")
        assert checksum.startswith("sha512:")

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test checksum of an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_bytes(b"")
        checksum = fs_utils.compute_checksum(test_file)
        expected_hash = hashlib.sha256(b"").hexdigest()
        assert checksum == f"sha256:{expected_hash}"

    def test_large_file_chunked_reading(self, tmp_path: Path) -> None:
        """Test that large files are read in chunks."""
        test_file = tmp_path / "large.bin"
        # Create a file larger than CHUNK_SIZE (8192 bytes)
        data = b"x" * (fs_utils.CHUNK_SIZE * 3 + 100)
        test_file.write_bytes(data)
        checksum = fs_utils.compute_checksum(test_file)
        expected_hash = hashlib.sha256(data).hexdigest()
        assert checksum == f"sha256:{expected_hash}"

    def test_different_content_different_checksum(self, tmp_path: Path) -> None:
        """Test that different content produces different checksums."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_bytes(b"Content A")
        file2.write_bytes(b"Content B")
        checksum1 = fs_utils.compute_checksum(file1)
        checksum2 = fs_utils.compute_checksum(file2)
        assert checksum1 != checksum2

    def test_same_content_same_checksum(self, tmp_path: Path) -> None:
        """Test that identical content produces identical checksums."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = b"Same content"
        file1.write_bytes(content)
        file2.write_bytes(content)
        checksum1 = fs_utils.compute_checksum(file1)
        checksum2 = fs_utils.compute_checksum(file2)
        assert checksum1 == checksum2

    def test_invalid_algorithm_raises_error(self, tmp_path: Path) -> None:
        """Test that an invalid algorithm raises an error."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"Test")
        with pytest.raises(ValueError):
            fs_utils.compute_checksum(test_file, "invalid_algorithm")

    def test_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that attempting to checksum a nonexistent file raises an error."""
        nonexistent = tmp_path / "does_not_exist.txt"
        with pytest.raises(FileNotFoundError):
            fs_utils.compute_checksum(nonexistent)


class TestChunkSize:
    """Tests for CHUNK_SIZE constant."""

    def test_chunk_size_value(self) -> None:
        """Test that CHUNK_SIZE is set to 8192."""
        assert fs_utils.CHUNK_SIZE == 8192

    def test_chunk_size_is_power_of_two(self) -> None:
        """Test that CHUNK_SIZE is a power of 2 (optimal for I/O)."""
        chunk_size = fs_utils.CHUNK_SIZE
        assert chunk_size > 0
        assert (chunk_size & (chunk_size - 1)) == 0  # Power of 2 check

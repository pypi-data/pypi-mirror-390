"""Tests for BuildCache."""

from pathlib import Path

import pytest

from b8tex.core.cache import BuildCache
from b8tex.core.diagnostics import ModuleGraph
from b8tex.core.document import Document
from b8tex.core.options import BuildOptions, OutputFormat
from b8tex.core.results import CompileResult, OutputArtifact


@pytest.fixture
def temp_cache_db(tmp_path: Path) -> Path:
    """Create a temporary cache database."""
    return tmp_path / "test_cache.db"


@pytest.fixture
def cache(temp_cache_db: Path) -> BuildCache:
    """Create a BuildCache instance."""
    cache = BuildCache(db_path=temp_cache_db)
    yield cache
    cache.close()


def test_cache_initialization(temp_cache_db: Path):
    """Test cache initialization."""
    cache = BuildCache(db_path=temp_cache_db)
    try:
        assert cache.db_path == temp_cache_db
        assert temp_cache_db.exists()
    finally:
        cache.close()


def test_cache_default_path():
    """Test default cache path selection."""
    cache = BuildCache()
    try:
        # Should have created a cache in a platform-specific location
        assert cache.db_path.exists()
        assert cache.db_path.name == "build_cache.db"
    finally:
        cache.close()


def test_get_fingerprint_simple(cache: BuildCache):
    """Test fingerprint generation for simple document."""
    doc = Document.from_string("\\documentclass{article}\\begin{document}Hello\\end{document}")
    options = BuildOptions()

    fp = cache.get_fingerprint(doc, options)

    assert len(fp) == 64  # SHA256 hex digest
    assert isinstance(fp, str)


def test_get_fingerprint_deterministic(cache: BuildCache):
    """Test that identical documents produce identical fingerprints."""
    doc1 = Document.from_string("content")
    doc2 = Document.from_string("content")
    options = BuildOptions()

    fp1 = cache.get_fingerprint(doc1, options)
    fp2 = cache.get_fingerprint(doc2, options)

    assert fp1 == fp2


def test_get_fingerprint_changes_with_content(cache: BuildCache):
    """Test that fingerprint changes when content changes."""
    doc1 = Document.from_string("content1")
    doc2 = Document.from_string("content2")
    options = BuildOptions()

    fp1 = cache.get_fingerprint(doc1, options)
    fp2 = cache.get_fingerprint(doc2, options)

    assert fp1 != fp2


def test_get_fingerprint_changes_with_options(cache: BuildCache):
    """Test that fingerprint changes when options change."""
    doc = Document.from_string("content")
    options1 = BuildOptions(outfmt=OutputFormat.PDF)
    options2 = BuildOptions(outfmt=OutputFormat.HTML)

    fp1 = cache.get_fingerprint(doc, options1)
    fp2 = cache.get_fingerprint(doc, options2)

    assert fp1 != fp2


def test_get_fingerprint_with_module_graph(cache: BuildCache):
    """Test fingerprint with module graph."""
    doc = Document.from_string("content")
    options = BuildOptions()

    graph = ModuleGraph()
    graph.record_include("main.tex", "ch1.tex")

    fp_with_graph = cache.get_fingerprint(doc, options, module_graph=graph)
    fp_without_graph = cache.get_fingerprint(doc, options, module_graph=None)

    assert fp_with_graph != fp_without_graph


def test_write_and_read(cache: BuildCache, tmp_path: Path):
    """Test writing and reading cache entries."""
    doc = Document.from_string("content")
    options = BuildOptions()
    fp = cache.get_fingerprint(doc, options)

    # Create a real artifact file
    artifact_file = tmp_path / "output.pdf"
    artifact_file.write_bytes(b"fake pdf content")

    # Create a fake compile result
    result = CompileResult(
        success=True,
        artifacts=[
            OutputArtifact(
                kind=OutputFormat.PDF,
                path=artifact_file,
                size=artifact_file.stat().st_size,
            )
        ],
        warnings=["warning 1"],
        errors=[],
        returncode=0,
        elapsed=1.5,
    )

    # Write to cache
    cache.write(fp, result, tectonic_version="0.14.0")

    # Read back
    entry = cache.read(fp)

    assert entry is not None
    assert entry.fingerprint == fp
    assert entry.tectonic_version == "0.14.0"
    assert entry.result_data["success"] is True
    assert len(entry.result_data["artifacts"]) == 1


def test_read_nonexistent(cache: BuildCache):
    """Test reading a nonexistent cache entry."""
    entry = cache.read("nonexistent_fingerprint")

    assert entry is None


def test_is_fresh_existing(cache: BuildCache):
    """Test freshness check for existing entry."""
    doc = Document.from_string("content")
    options = BuildOptions()
    fp = cache.get_fingerprint(doc, options)

    result = CompileResult(success=True)
    cache.write(fp, result)

    assert cache.is_fresh(fp) is True


def test_is_fresh_nonexistent(cache: BuildCache):
    """Test freshness check for nonexistent entry."""
    assert cache.is_fresh("nonexistent") is False


def test_is_fresh_with_max_age(cache: BuildCache):
    """Test freshness check with max age."""
    doc = Document.from_string("content")
    options = BuildOptions()
    fp = cache.get_fingerprint(doc, options)

    result = CompileResult(success=True)
    cache.write(fp, result)

    # Should be fresh within a large time window
    assert cache.is_fresh(fp, max_age_seconds=3600) is True

    # Should not be fresh with a very small time window
    # (This is a bit fragile but should work in practice)
    import time

    time.sleep(0.01)
    assert cache.is_fresh(fp, max_age_seconds=0.001) is False


def test_invalidate(cache: BuildCache):
    """Test cache invalidation."""
    doc = Document.from_string("content")
    options = BuildOptions()
    fp = cache.get_fingerprint(doc, options)

    result = CompileResult(success=True)
    cache.write(fp, result)

    assert cache.read(fp) is not None

    cache.invalidate(fp)

    assert cache.read(fp) is None


def test_clear(cache: BuildCache):
    """Test clearing the entire cache."""
    doc1 = Document.from_string("content1")
    doc2 = Document.from_string("content2")
    options = BuildOptions()

    fp1 = cache.get_fingerprint(doc1, options)
    fp2 = cache.get_fingerprint(doc2, options)

    result = CompileResult(success=True)
    cache.write(fp1, result)
    cache.write(fp2, result)

    assert cache.stats()["total_entries"] == 2

    cache.clear()

    assert cache.stats()["total_entries"] == 0


def test_stats(cache: BuildCache):
    """Test cache statistics."""
    stats = cache.stats()

    assert "total_entries" in stats
    assert "total_size_bytes" in stats
    assert "db_size_bytes" in stats
    assert isinstance(stats["total_entries"], int)


def test_cache_persistence(temp_cache_db: Path):
    """Test that cache persists across instances."""
    doc = Document.from_string("content")
    options = BuildOptions()

    # Create first cache instance
    cache1 = BuildCache(db_path=temp_cache_db)
    try:
        fp = cache1.get_fingerprint(doc, options)
        result = CompileResult(success=True)
        cache1.write(fp, result)
    finally:
        cache1.close()

    # Create second cache instance with same database
    cache2 = BuildCache(db_path=temp_cache_db)
    try:
        entry = cache2.read(fp)

        assert entry is not None
        assert entry.result_data["success"] is True
    finally:
        cache2.close()

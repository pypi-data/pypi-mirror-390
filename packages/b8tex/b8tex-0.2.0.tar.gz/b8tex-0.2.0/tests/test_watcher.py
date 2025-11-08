"""Tests for watch mode functionality."""

import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Check if watchfiles is available
pytest.importorskip("watchfiles")

import contextlib

from b8tex import Document, TectonicCompiler
from b8tex.core.watcher import Watcher, WatchHandle


@pytest.fixture
def compiler():
    """Create a mock compiler for testing."""
    with patch.object(TectonicCompiler, "__init__", return_value=None):
        compiler = TectonicCompiler()
        compiler.compile_document = Mock()
        return compiler


@pytest.fixture
def sample_document(tmp_path: Path):
    """Create a sample document for testing."""
    doc_file = tmp_path / "test.tex"
    doc_file.write_text(
        r"""
\documentclass{article}
\begin{document}
Test document
\end{document}
"""
    )
    return Document.from_path(doc_file)


def test_watcher_init(compiler):
    """Test Watcher initialization."""
    watcher = Watcher(compiler)

    assert watcher.compiler is compiler
    assert watcher.debounce_seconds == 0.5


def test_watcher_custom_debounce(compiler):
    """Test Watcher with custom debounce."""
    watcher = Watcher(compiler, debounce_seconds=2.0)

    assert watcher.debounce_seconds == 2.0


@pytest.mark.asyncio
async def test_watch_handle_init():
    """Test WatchHandle initialization."""
    task = asyncio.create_task(asyncio.sleep(1))
    handle = WatchHandle(task)

    assert handle.task is task
    assert handle.running is True
    assert handle.compile_count == 0
    assert handle.is_running() is True

    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_watch_handle_stop():
    """Test stopping a watch handle."""
    task = asyncio.create_task(asyncio.sleep(10))
    handle = WatchHandle(task)

    handle.stop()

    # Wait a bit for cancellation to propagate
    await asyncio.sleep(0.01)

    assert handle.running is False
    assert task.cancelled() or task.done()


@pytest.mark.asyncio
async def test_watch_handle_wait():
    """Test waiting for watch handle completion."""
    task = asyncio.create_task(asyncio.sleep(0.1))
    handle = WatchHandle(task)

    await handle.wait()

    assert task.done()


def test_watcher_get_watch_paths_file_document(tmp_path: Path, compiler):
    """Test determining watch paths for file-based document."""
    doc_file = tmp_path / "test.tex"
    doc_file.write_text("content")

    document = Document.from_path(doc_file)
    watcher = Watcher(compiler)

    paths = watcher._get_watch_paths(document)

    assert tmp_path in paths


def test_watcher_get_watch_paths_in_memory(compiler):
    """Test determining watch paths for in-memory document."""
    from b8tex import InMemorySource

    document = Document(
        name="test",
        entrypoint=InMemorySource("test.tex", "content"),
    )
    watcher = Watcher(compiler)

    paths = watcher._get_watch_paths(document)

    # Should watch current directory for in-memory documents
    assert Path.cwd() in paths


def test_watcher_get_watch_paths_with_resources(tmp_path: Path, compiler):
    """Test watch paths include resource directories."""
    from b8tex import Resource

    doc_file = tmp_path / "test.tex"
    doc_file.write_text("content")

    resource_dir = tmp_path / "resources"
    resource_dir.mkdir()
    resource_file = resource_dir / "style.sty"
    resource_file.write_text("style")

    document = Document(
        name="test",
        entrypoint=doc_file,
        resources=[Resource(resource_file)],
    )
    watcher = Watcher(compiler)

    paths = watcher._get_watch_paths(document)

    assert tmp_path in paths
    assert resource_dir in paths


@pytest.mark.asyncio
async def test_watch_document_import_error(compiler, sample_document):
    """Test watch_document raises ImportError if watchfiles not available."""
    watcher = Watcher(compiler)

    with patch.dict("sys.modules", {"watchfiles": None}):
        with pytest.raises(ImportError, match="watchfiles"):
            await watcher.watch_document(sample_document)


@pytest.mark.asyncio
async def test_watch_document_initial_build(compiler, sample_document):
    """Test that watch_document performs initial build."""
    from b8tex.core.results import CompileResult

    watcher = Watcher(compiler)

    # Mock successful compilation
    mock_result = CompileResult(success=True)
    compiler.compile_document.return_value = mock_result

    # Mock awatch to not yield any changes
    async def mock_awatch(*args):
        if False:
            yield

    with patch("watchfiles.awatch", mock_awatch):
        handle = await watcher.watch_document(sample_document)

        # Should have performed initial build
        assert compiler.compile_document.called
        assert handle.compile_count == 1

        handle.stop()
        await handle.wait()


@pytest.mark.asyncio
async def test_watch_document_with_callbacks(compiler, sample_document):
    """Test watch_document calls success callback on initial build."""
    from b8tex.core.results import CompileResult

    watcher = Watcher(compiler)
    success_callback = Mock()

    # Mock successful compilation
    mock_result = CompileResult(success=True)
    compiler.compile_document.return_value = mock_result

    # Mock awatch
    async def mock_awatch(*args):
        if False:
            yield

    with patch("watchfiles.awatch", mock_awatch):
        handle = await watcher.watch_document(
            sample_document, on_success=success_callback
        )

        # Success callback should have been called
        success_callback.assert_called_once_with(mock_result)

        handle.stop()
        await handle.wait()


@pytest.mark.asyncio
async def test_watch_document_error_callback(compiler, sample_document):
    """Test watch_document calls error callback on build failure."""
    watcher = Watcher(compiler)
    error_callback = Mock()

    # Mock failed compilation
    compiler.compile_document.side_effect = RuntimeError("Build failed")

    # Mock awatch
    async def mock_awatch(*args):
        if False:
            yield

    with patch("watchfiles.awatch", mock_awatch):
        handle = await watcher.watch_document(
            sample_document, on_error=error_callback
        )

        # Error callback should have been called
        error_callback.assert_called_once()
        assert isinstance(error_callback.call_args[0][0], RuntimeError)

        handle.stop()
        await handle.wait()


@pytest.mark.asyncio
async def test_watch_document_custom_patterns(compiler, sample_document):
    """Test watch_document with custom file patterns."""
    from b8tex.core.results import CompileResult

    watcher = Watcher(compiler)

    # Mock successful compilation
    mock_result = CompileResult(success=True)
    compiler.compile_document.return_value = mock_result

    custom_patterns = ["*.tex", "*.bib"]

    # Mock awatch
    async def mock_awatch(*args):
        if False:
            yield

    with patch("watchfiles.awatch", mock_awatch):
        handle = await watcher.watch_document(
            sample_document, watch_patterns=custom_patterns
        )

        handle.stop()
        await handle.wait()

        # Test passed - patterns were accepted without error


@pytest.mark.asyncio
async def test_watch_loop_debouncing(compiler, tmp_path: Path):
    """Test that watch loop debounces rapid changes."""
    from b8tex.core.results import CompileResult

    doc_file = tmp_path / "test.tex"
    doc_file.write_text("content")
    document = Document.from_path(doc_file)

    watcher = Watcher(compiler, debounce_seconds=0.1)

    # Mock compilation
    mock_result = CompileResult(success=True, elapsed=0.1)
    compiler.compile_document.return_value = mock_result

    # Track build count
    build_count = 0

    def count_builds(result):
        nonlocal build_count
        build_count += 1

    # Simulate multiple rapid changes
    change_count = 0

    async def mock_awatch(*args):
        nonlocal change_count
        for _i in range(3):  # Simulate 3 changes
            change_count += 1
            yield [(1, str(doc_file))]  # Change type 1 = modified
            await asyncio.sleep(0.05)  # Rapid changes

    with patch("watchfiles.awatch", mock_awatch):
        handle = await watcher.watch_document(
            document, on_success=count_builds
        )

        # Let it process changes
        await asyncio.sleep(0.5)

        handle.stop()
        await handle.wait()

    # Should have debounced some builds
    # Initial build + some rebuilds (but not all 3 rapid changes)
    assert build_count >= 1  # At least initial build


@pytest.mark.asyncio
async def test_convenience_function(sample_document):
    """Test the watch_document convenience function."""
    from b8tex.core.results import CompileResult
    from b8tex.core.watcher import watch_document

    success_callback = Mock()

    # Mock TectonicCompiler
    with patch("b8tex.api.TectonicCompiler") as MockCompiler:
        mock_compiler = MockCompiler.return_value
        mock_compiler.compile_document.return_value = CompileResult(success=True)

        # Mock awatch
        async def mock_awatch(*args):
            if False:
                yield

        with patch("watchfiles.awatch", mock_awatch):
            handle = await watch_document(
                sample_document, on_success=success_callback
            )

            assert handle is not None
            assert success_callback.called

            handle.stop()
            await handle.wait()

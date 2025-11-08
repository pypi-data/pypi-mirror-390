"""File watching and auto-rebuild functionality for B8TeX."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from b8tex.api import TectonicCompiler
    from b8tex.core.document import Document
    from b8tex.core.options import BuildOptions
    from b8tex.core.results import CompileResult

# Set up logging
logger = logging.getLogger(__name__)


class WatchHandle:
    """Handle for a running file watcher.

    Allows control of a watch session (stop, check status, etc.).

    Attributes:
        task: Async task running the watcher
        running: Whether the watcher is currently running
        compile_count: Number of compilations triggered
    """

    def __init__(self, task: asyncio.Task[None]) -> None:
        """Initialize the watch handle.

        Args:
            task: Async task running the watcher
        """
        self.task = task
        self.running = True
        self.compile_count = 0
        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        """Stop the watcher."""
        self.running = False
        self._stop_event.set()
        if not self.task.done():
            self.task.cancel()

    async def wait(self) -> None:
        """Wait for the watcher to complete."""
        with contextlib.suppress(asyncio.CancelledError):
            await self.task

    def is_running(self) -> bool:
        """Check if watcher is still running.

        Returns:
            True if watcher is active
        """
        return self.running and not self.task.done()


class Watcher:
    """File system watcher for auto-rebuild on changes.

    Monitors source files and triggers recompilation when changes are detected.

    Example:
        ```python
        from b8tex import TectonicCompiler, Document, Watcher

        compiler = TectonicCompiler()
        document = Document.from_path(Path("document.tex"))

        watcher = Watcher(compiler)
        handle = await watcher.watch_document(
            document,
            on_success=lambda result: print(f"Built: {result.pdf_path}"),
            on_error=lambda e: print(f"Error: {e}")
        )

        # Later...
        handle.stop()
        ```
    """

    def __init__(
        self,
        compiler: TectonicCompiler,
        debounce_seconds: float = 0.5,
    ) -> None:
        """Initialize the watcher.

        Args:
            compiler: TectonicCompiler instance to use for builds
            debounce_seconds: Wait time after change before rebuilding
        """
        self.compiler = compiler
        self.debounce_seconds = debounce_seconds

    async def watch_document(
        self,
        document: Document,
        options: BuildOptions | None = None,
        *,
        on_success: Callable[[CompileResult], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        watch_patterns: list[str] | None = None,
    ) -> WatchHandle:
        """Watch a document and recompile on changes.

        Args:
            document: Document to watch and compile
            options: Build options for compilation
            on_success: Callback for successful compilations
            on_error: Callback for compilation errors
            watch_patterns: File patterns to watch (default: ["*.tex", "*.sty", "*.cls", "*.bib"])

        Returns:
            WatchHandle for controlling the watch session

        Raises:
            ImportError: If watchfiles is not installed
        """
        try:
            from watchfiles import awatch
        except ImportError as e:
            raise ImportError(
                "Watch mode requires the 'watchfiles' package. "
                "Install it with: pip install b8tex[watch]"
            ) from e

        # Determine paths to watch
        watch_paths = self._get_watch_paths(document)

        # Default patterns
        if watch_patterns is None:
            watch_patterns = ["*.tex", "*.sty", "*.cls", "*.bib", "*.png", "*.jpg", "*.pdf"]

        # Create and start watch task
        task = asyncio.create_task(
            self._watch_loop(
                document=document,
                options=options,
                watch_paths=watch_paths,
                watch_patterns=watch_patterns,
                on_success=on_success,
                on_error=on_error,
            )
        )

        handle = WatchHandle(task)

        # Initial build
        try:
            result = self.compiler.compile_document(document, options)
            handle.compile_count += 1
            if on_success:
                on_success(result)
        except Exception as e:
            if on_error:
                on_error(e)

        return handle

    async def _watch_loop(
        self,
        document: Document,
        options: BuildOptions | None,
        watch_paths: list[Path],
        watch_patterns: list[str],
        on_success: Callable[[CompileResult], None] | None,
        on_error: Callable[[Exception], None] | None,
    ) -> None:
        """Main watch loop (runs in background task).

        Args:
            document: Document being watched
            options: Build options
            watch_paths: Paths to monitor
            watch_patterns: File patterns to watch
            on_success: Success callback
            on_error: Error callback
        """
        from watchfiles import awatch

        last_build = time.time()

        # Convert paths to strings for watchfiles
        watch_path_strs = [str(p) for p in watch_paths]

        logger.info(f"Watching {len(watch_paths)} paths for changes...")
        logger.info(f"Patterns: {', '.join(watch_patterns)}")

        try:
            async for changes in awatch(*watch_path_strs):
                # Debounce: wait before rebuilding
                elapsed = time.time() - last_build
                if elapsed < self.debounce_seconds:
                    await asyncio.sleep(self.debounce_seconds - elapsed)

                # Check if any changed file matches our patterns
                relevant_changes = []
                for change_type, changed_path in changes:
                    path = Path(changed_path)
                    if any(path.match(pattern) for pattern in watch_patterns):
                        relevant_changes.append((change_type, path))

                if not relevant_changes:
                    continue

                logger.info(f"Detected {len(relevant_changes)} change(s), rebuilding...")
                last_build = time.time()

                # Rebuild
                try:
                    result = self.compiler.compile_document(document, options)
                    if on_success:
                        on_success(result)
                    logger.info(f"Build successful ({result.elapsed:.2f}s)")
                except Exception as e:
                    if on_error:
                        on_error(e)
                    logger.error(f"Build failed: {e}")

        except asyncio.CancelledError:
            logger.info("Watch stopped")
            raise

    def _get_watch_paths(self, document: Document) -> list[Path]:
        """Determine which paths to watch for the document.

        Args:
            document: Document to analyze

        Returns:
            List of paths to watch
        """
        from b8tex.core.document import InMemorySource

        watch_paths = []

        # Watch entrypoint if it's a file
        if not isinstance(document.entrypoint, InMemorySource):
            entrypoint_dir = document.entrypoint.parent
            if entrypoint_dir not in watch_paths:
                watch_paths.append(entrypoint_dir)

        # Watch resource directories
        for resource in document.resources:
            if not isinstance(resource.path_or_mem, InMemorySource):
                resource_dir = resource.path_or_mem.parent
                if resource_dir not in watch_paths:
                    watch_paths.append(resource_dir)

        # Watch search paths
        for search_path in document.search_paths:
            # InputPath has a .path attribute that is a Path object
            from b8tex.core.project import InputPath
            path = search_path.path if isinstance(search_path, InputPath) else search_path
            if path.exists() and path not in watch_paths:
                watch_paths.append(path)

        # If no paths found, watch current directory
        if not watch_paths:
            watch_paths.append(Path.cwd())

        return watch_paths


async def watch_document(
    document: Document,
    options: BuildOptions | None = None,
    *,
    compiler: TectonicCompiler | None = None,
    on_success: Callable[[CompileResult], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
) -> WatchHandle:
    """Watch a document and auto-rebuild on changes (convenience function).

    Args:
        document: Document to watch
        options: Build options
        compiler: Compiler to use (creates default if None)
        on_success: Callback for successful builds
        on_error: Callback for errors

    Returns:
        WatchHandle for controlling the watch session

    Example:
        ```python
        import asyncio
        from b8tex import Document, watch_document

        async def main():
            doc = Document.from_path(Path("document.tex"))
            handle = await watch_document(
                doc,
                on_success=lambda r: print(f"PDF: {r.pdf_path}")
            )

            # Let it run for a while
            await asyncio.sleep(60)
            handle.stop()

        asyncio.run(main())
        ```
    """
    if compiler is None:
        from b8tex.api import TectonicCompiler

        compiler = TectonicCompiler()

    watcher = Watcher(compiler)
    return await watcher.watch_document(
        document,
        options=options,
        on_success=on_success,
        on_error=on_error,
    )

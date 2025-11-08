"""Workspace management for build isolation."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from b8tex.core.document import Document, InMemorySource, Resource
from b8tex.core.options import BuildOptions
from b8tex.exceptions import WorkspaceError

if TYPE_CHECKING:
    from b8tex.core.project import InputPath

# Set up logging
logger = logging.getLogger(__name__)


class LayoutStrategy(Enum):
    """Strategy for organizing files in the workspace."""

    MIRROR = "mirror"  # Mirror source directory structure
    FLAT = "flat"  # Flatten all files into one directory
    TMP_ONLY = "tmp_only"  # Only materialize in-memory files


@dataclass
class Workspace:
    """Manages the build workspace for isolated compilation.

    Attributes:
        workdir: Working directory for builds
        layout: Layout strategy for organizing files
        cleanup_on_exit: Whether to clean up workdir when done
        search_paths: Additional search paths for LaTeX
        _staged_files: Mapping of original paths to staged paths
    """

    workdir: Path
    layout: LayoutStrategy = LayoutStrategy.MIRROR
    cleanup_on_exit: bool = True
    search_paths: list[InputPath] = field(default_factory=list)
    _staged_files: dict[str, Path] = field(default_factory=dict, init=False, repr=False)

    @classmethod
    def create_temp(
        cls,
        layout: LayoutStrategy = LayoutStrategy.MIRROR,
    ) -> Workspace:
        """Create a temporary workspace.

        Args:
            layout: Layout strategy

        Returns:
            Workspace instance
        """
        tempdir = Path(tempfile.mkdtemp(prefix="b8tex_"))
        logger.debug(f"Created temporary workspace: {tempdir}")
        return cls(workdir=tempdir, layout=layout, cleanup_on_exit=True)

    @classmethod
    def create_persistent(
        cls,
        path: Path,
        layout: LayoutStrategy = LayoutStrategy.MIRROR,
    ) -> Workspace:
        """Create a persistent workspace at a specific path.

        Args:
            path: Workspace directory
            layout: Layout strategy

        Returns:
            Workspace instance
        """
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created persistent workspace: {path}")
        return cls(workdir=path, layout=layout, cleanup_on_exit=False)

    def stage_document(self, document: Document) -> Path:
        """Stage a document's entrypoint in the workspace.

        Args:
            document: Document to stage

        Returns:
            Path to staged entrypoint

        Raises:
            WorkspaceError: If staging fails
        """
        try:
            if isinstance(document.entrypoint, InMemorySource):
                return self._materialize_in_memory(document.entrypoint)
            else:
                return self._stage_file(document.entrypoint)
        except Exception as e:
            raise WorkspaceError(f"Failed to stage document: {e}") from e

    def stage_resources(self, resources: list[Resource]) -> list[Path]:
        """Stage resource files in the workspace.

        Args:
            resources: Resources to stage

        Returns:
            List of staged file paths

        Raises:
            WorkspaceError: If staging fails
        """
        staged = []
        for resource in resources:
            try:
                if isinstance(resource.path_or_mem, InMemorySource):
                    path = self._materialize_in_memory(resource.path_or_mem)
                else:
                    path = self._stage_file(resource.path_or_mem)
                staged.append(path)
            except Exception as e:
                raise WorkspaceError(f"Failed to stage resource: {e}") from e
        return staged

    def _materialize_in_memory(self, source: InMemorySource) -> Path:
        """Write an in-memory source to the workspace.

        Args:
            source: In-memory source

        Returns:
            Path to materialized file
        """
        dest = self.workdir / source.filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(source.content, encoding=source.encoding)
        return dest

    def _stage_file(self, source: Path) -> Path:
        """Copy a file to the workspace.

        Args:
            source: Source file path

        Returns:
            Path to staged file
        """
        # Check if already staged
        source_key = str(source.resolve())
        if source_key in self._staged_files:
            return self._staged_files[source_key]

        # TMP_ONLY: Don't copy disk files, just return original path
        if self.layout == LayoutStrategy.TMP_ONLY:
            self._staged_files[source_key] = source
            return source

        # Determine destination based on layout
        if self.layout == LayoutStrategy.FLAT:
            # Flatten: just use filename
            dest = self.workdir / source.name
        else:  # MIRROR
            # Try to preserve relative structure if possible
            cwd = Path.cwd()
            # If source is relative to cwd, mirror that structure
            if source.is_relative_to(cwd):
                rel_path = source.relative_to(cwd)
                dest = self.workdir / rel_path
            else:
                # If not relative to cwd, just use filename
                dest = self.workdir / source.name

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        logger.debug(f"Staged file: {source.name} -> {dest}")
        self._staged_files[source_key] = dest
        return dest

    def resolve_outdir(self, options: BuildOptions) -> Path:
        """Resolve the output directory for artifacts.

        Args:
            options: Build options

        Returns:
            Output directory path
        """
        if options.outdir:
            return options.outdir

        # Default: output subdirectory in workspace
        outdir = self.workdir / "output"
        outdir.mkdir(parents=True, exist_ok=True)
        return outdir

    def setup_search_paths(
        self,
        document_paths: list[InputPath] | None = None,
        project_paths: list[InputPath] | None = None,
    ) -> dict[str, str]:
        """Set up TEXINPUTS environment variable for LaTeX search paths.

        Search order (highest to lowest priority):
        1. Workspace directory (staged files)
        2. Document-specific search paths
        3. Project-wide search paths
        4. Workspace search paths

        Args:
            document_paths: Document-specific search paths
            project_paths: Project-wide search paths

        Returns:
            Dictionary of environment variables to set (includes TEXINPUTS)
        """
        # Collect all search paths with their priorities
        all_paths: list[tuple[int, Path]] = []

        # Priority 0: Workspace directory (always searched first)
        all_paths.append((0, self.workdir))

        # Document paths
        if document_paths:
            for input_path in document_paths:
                all_paths.append((input_path.order, input_path.path))

        # Project paths
        if project_paths:
            for input_path in project_paths:
                all_paths.append((input_path.order + 1000, input_path.path))

        # Workspace configured paths
        for input_path in self.search_paths:
            all_paths.append((input_path.order + 2000, input_path.path))

        # Sort by priority (lower order = higher priority)
        all_paths.sort(key=lambda x: x[0])

        # Build TEXINPUTS string
        texinputs_paths = [str(path.resolve()) for _, path in all_paths]

        # Platform-specific path separator
        separator = ";" if platform.system() == "Windows" else ":"

        # TEXINPUTS format: path1:path2:path3::
        # The trailing :: tells TeX to also search default locations
        texinputs = separator.join(texinputs_paths) + separator + separator

        return {
            "TEXINPUTS": texinputs,
        }

    def isolate_environment(self, base_env: dict[str, str] | None = None) -> dict[str, str]:
        """Create an isolated environment for compilation.

        This removes ambient TEXINPUTS to prevent interference from
        the user's environment.

        Args:
            base_env: Base environment to start from (defaults to os.environ)

        Returns:
            Isolated environment dictionary
        """
        base_env = os.environ.copy() if base_env is None else base_env.copy()

        # Remove LaTeX-related environment variables that might interfere
        tex_vars_to_remove = [
            "TEXINPUTS",
            "TEXMFHOME",
            "TEXMFLOCAL",
            "TEXMFVAR",
            "TEXMFCONFIG",
        ]

        for var in tex_vars_to_remove:
            base_env.pop(var, None)

        return base_env

    def cleanup(self) -> None:
        """Clean up the workspace directory."""
        if self.cleanup_on_exit and self.workdir.exists():
            logger.debug(f"Cleaning up workspace: {self.workdir}")
            shutil.rmtree(self.workdir)

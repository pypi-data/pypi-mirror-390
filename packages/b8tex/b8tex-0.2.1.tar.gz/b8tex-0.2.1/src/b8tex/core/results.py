"""Compilation result classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from b8tex.core.options import OutputFormat

if TYPE_CHECKING:
    from b8tex.core.diagnostics import ModuleGraph


@dataclass
class OutputArtifact:
    """An output file produced by compilation.

    Attributes:
        kind: Type of output (PDF, HTML, etc.)
        path: Path to the output file
        size: File size in bytes
        created_at: Creation timestamp
    """

    kind: OutputFormat
    path: Path
    size: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CompileResult:
    """Result of a LaTeX compilation.

    Attributes:
        success: Whether compilation succeeded
        artifacts: Output files produced
        warnings: Warning messages from compilation
        errors: Error messages from compilation
        returncode: Process return code
        elapsed: Compilation time in seconds
        log_path: Path to log file (if kept)
        intermediates_dir: Directory with intermediate files (if kept)
        invocation: Command line used for compilation
        module_graph: Dependency graph of included files
    """

    success: bool
    artifacts: list[OutputArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    returncode: int = 0
    elapsed: float = 0.0
    log_path: Path | None = None
    intermediates_dir: Path | None = None
    invocation: list[str] = field(default_factory=list)
    module_graph: ModuleGraph | None = None

    @property
    def pdf_path(self) -> Path | None:
        """Path to PDF output, if produced."""
        for artifact in self.artifacts:
            if artifact.kind == OutputFormat.PDF:
                return artifact.path
        return None

    @property
    def html_path(self) -> Path | None:
        """Path to HTML output, if produced."""
        for artifact in self.artifacts:
            if artifact.kind == OutputFormat.HTML:
                return artifact.path
        return None

    @property
    def xdv_path(self) -> Path | None:
        """Path to XDV output, if produced."""
        for artifact in self.artifacts:
            if artifact.kind == OutputFormat.XDV:
                return artifact.path
        return None

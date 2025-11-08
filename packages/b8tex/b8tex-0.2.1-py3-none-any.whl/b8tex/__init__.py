"""
B8TeX - A high-level Python wrapper for Tectonic LaTeX compiler.

This package provides a modern, type-safe interface to the Tectonic LaTeX
compiler with support for project-aware compilation, custom packages,
and comprehensive build management.
"""

import logging

from b8tex.api import (
    TectonicCompiler,
    compile_document,
    compile_string,
)
from b8tex.core.binary import TectonicBinary
from b8tex.core.cache import BuildCache
from b8tex.core.document import Document, InMemorySource, Resource
from b8tex.core.options import (
    BuildOptions,
    BundleConfig,
    OutputFormat,
    SecurityPolicy,
)
from b8tex.core.project import InputPath, Project, Target
from b8tex.core.results import CompileResult, OutputArtifact
from b8tex.exceptions import (
    CompilationFailed,
    MissingBinaryError,
    SecurityPolicyError,
    TexError,
    UnsupportedOptionError,
    WorkspaceError,
)

# Optional watch mode (requires watchfiles)
try:
    from b8tex.core.watcher import Watcher, WatchHandle, watch_document

    _HAS_WATCH = True
except ImportError:
    _HAS_WATCH = False
    WatchHandle = None  # type: ignore
    Watcher = None  # type: ignore
    watch_document = None  # type: ignore

__version__ = "0.2.1"

# Optional templates (requires jinja2)
try:
    from b8tex.templates import (
        Author,
        ConditionalSection,
        DataTable,
        DocumentBuilder,
        PlotData,
        Raw,
        Section,
        TemplateConfig,
        TemplateDocument,
        TemplateMetadata,
        compile_template,
        compile_template_document,
        escape_latex,
        render_template_latex,
        validate_template_document,
    )

    _HAS_TEMPLATES = True
except ImportError:
    _HAS_TEMPLATES = False
    # Stub for type hints
    Author = None  # type: ignore
    ConditionalSection = None  # type: ignore
    DataTable = None  # type: ignore
    DocumentBuilder = None  # type: ignore
    PlotData = None  # type: ignore
    Raw = None  # type: ignore
    Section = None  # type: ignore
    TemplateConfig = None  # type: ignore
    TemplateDocument = None  # type: ignore
    TemplateMetadata = None  # type: ignore
    compile_template = None  # type: ignore
    compile_template_document = None  # type: ignore
    escape_latex = None  # type: ignore
    render_template_latex = None  # type: ignore
    validate_template_document = None  # type: ignore


def configure_logging(
    level: int = logging.WARNING,
    handler: logging.Handler | None = None,
    format_string: str | None = None,
) -> None:
    """Configure B8TeX logging output.

    By default, B8TeX uses Python's standard logging with WARNING level.
    Call this function to customize logging behavior for B8TeX operations.

    Args:
        level: Logging level (default: logging.WARNING).
            Use logging.DEBUG for detailed operational information,
            logging.INFO for high-level events, or logging.WARNING for issues only.
        handler: Custom logging handler. If None, uses StreamHandler to stderr
            with a standard format.
        format_string: Custom format string for log messages. If None, uses:
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    Example:
        >>> import logging
        >>> import b8tex
        >>> # Enable debug logging
        >>> b8tex.configure_logging(level=logging.DEBUG)
        >>> # Or with custom format
        >>> b8tex.configure_logging(
        ...     level=logging.INFO,
        ...     format_string='%(levelname)s: %(message)s'
        ... )
    """
    b8tex_logger = logging.getLogger("b8tex")

    # Remove existing handlers to avoid duplicates
    b8tex_logger.handlers.clear()

    # Create handler if not provided
    if handler is None:
        handler = logging.StreamHandler()
        if format_string is None:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

    b8tex_logger.addHandler(handler)
    b8tex_logger.setLevel(level)
    # Prevent propagation to avoid duplicate logs
    b8tex_logger.propagate = False


__all__ = [
    # Main API
    "TectonicCompiler",
    "compile_document",
    "compile_string",
    # Configuration
    "configure_logging",
    # Core types
    "TectonicBinary",
    "Document",
    "InMemorySource",
    "Resource",
    "BuildOptions",
    "BundleConfig",
    "OutputFormat",
    "SecurityPolicy",
    "InputPath",
    "Project",
    "Target",
    "CompileResult",
    "OutputArtifact",
    "BuildCache",
    # Watch mode (optional)
    "Watcher",
    "WatchHandle",
    "watch_document",
    # Templates (optional)
    "compile_template",
    "compile_template_document",
    "render_template_latex",
    "validate_template_document",
    "Author",
    "Section",
    "ConditionalSection",
    "TemplateDocument",
    "TemplateConfig",
    "TemplateMetadata",
    "DocumentBuilder",
    "DataTable",
    "PlotData",
    "Raw",
    "escape_latex",
    # Exceptions
    "TexError",
    "MissingBinaryError",
    "CompilationFailed",
    "UnsupportedOptionError",
    "WorkspaceError",
    "SecurityPolicyError",
]

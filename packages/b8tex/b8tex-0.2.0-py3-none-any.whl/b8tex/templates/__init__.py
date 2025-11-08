"""Template system for b8tex - programmatic LaTeX document generation.

This module provides a high-level, Pythonic API for creating LaTeX documents
using pre-built templates (NeurIPS, ICLR, ACL) with support for:

- Type-safe configuration
- Structured document building
- Data-driven content (DataFrames → tables, matplotlib → figures)
- Jinja2 template variables
- Multiple API styles (dataclass, builder, context managers)

Quick Start:
    >>> from b8tex.templates import compile_template
    >>> result = compile_template(
    ...     template="neurips",
    ...     title="My Research Paper",
    ...     authors="John Doe",
    ...     abstract="This paper presents...",
    ...     content=r"\\section{Introduction} Hello world!",
    ...     status="draft",
    ... )
    >>> print(f"PDF: {result.pdf_path}")
"""

from __future__ import annotations

# Public API - configuration
from b8tex.templates.config import (
    Author,
    StatusMode,
    TemplateConfig,
    TemplateMetadata,
    TemplateType,
)

# Public API - document models
from b8tex.templates.document import (
    ConditionalSection,
    Section,
    TemplateDocument,
)

# Public API - builder
from b8tex.templates.builder import DocumentBuilder

# Public API - data-driven features
from b8tex.templates.data import DataTable, PlotData

# Public API - validation
from b8tex.templates.validation import (
    TemplateValidator,
    ValidationIssue,
    ValidationSeverity,
)

# Public API - high-level functions
from b8tex.templates.api import (
    compile_template,
    compile_template_document,
    render_template_latex,
    validate_template_document,
)

# Public API - utilities
from b8tex.templates.escape import Raw, escape_latex

__all__ = [
    # Configuration
    "Author",
    "TemplateConfig",
    "TemplateMetadata",
    "TemplateType",
    "StatusMode",
    # Document models
    "Section",
    "ConditionalSection",
    "TemplateDocument",
    # Builder
    "DocumentBuilder",
    # Data features
    "DataTable",
    "PlotData",
    # Validation
    "TemplateValidator",
    "ValidationIssue",
    "ValidationSeverity",
    # High-level API
    "compile_template",
    "compile_template_document",
    "render_template_latex",
    "validate_template_document",
    # Utilities
    "Raw",
    "escape_latex",
]

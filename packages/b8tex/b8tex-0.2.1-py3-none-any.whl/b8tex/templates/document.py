"""Document model classes for template system."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from b8tex.core.document import InMemorySource, Resource
    from b8tex.templates.config import Author, TemplateConfig


@dataclass(frozen=True, slots=True)
class Section:
    """Document section with optional subsections.

    Attributes:
        title: Section title
        content: Section content (LaTeX or plain text)
        level: Section level (1=section, 2=subsection, 3=subsubsection, 4=paragraph)
        label: Optional label for cross-references
        numbered: Whether section should be numbered
        subsections: Nested subsections
    """

    title: str
    content: str = ""
    level: int = 1
    label: str | None = None
    numbered: bool = True
    subsections: tuple[Section, ...] = ()

    def __post_init__(self) -> None:
        """Validate section parameters."""
        if self.level < 1 or self.level > 4:
            raise ValueError(f"Section level must be 1-4, got {self.level}")


@dataclass(frozen=True, slots=True)
class ConditionalSection(Section):
    """Section that is conditionally included based on a condition.

    Attributes:
        condition: Boolean, string variable name, or callable that determines if section should be included
        default_visible: Default visibility when condition variable is not in context (for string conditions only)
    """

    condition: bool | str | Callable[[dict[str, Any]], bool] = True
    default_visible: bool = False

    def should_include(self, context: dict[str, Any] | None = None) -> bool:
        """Determine if section should be included.

        Args:
            context: Optional context dictionary for string/callable conditions

        Returns:
            True if section should be included
        """
        if isinstance(self.condition, bool):
            return self.condition

        if context is None:
            context = {}

        # String condition: lookup variable in context, use default_visible if not found
        if isinstance(self.condition, str):
            return bool(context.get(self.condition, self.default_visible))

        # Callable condition
        return self.condition(context)


@dataclass
class TemplateDocument:
    """Complete document specification for template-based generation.

    This is the main entry point for template-based document creation.
    Provides structured, type-safe document construction.

    Attributes:
        title: Document title
        config: Template configuration
        content: Raw LaTeX content (alternative to sections)
        sections: Structured sections (alternative to content)
        authors: List of authors or author string
        abstract: Document abstract
        keywords: Document keywords
        acknowledgments: Acknowledgments section
        bibliography: Path or in-memory bibliography file
        bibliography_style: BibTeX style (e.g., 'plain', 'acl_natbib')
        date: Document date (e.g., "January 2024", "\\today")
        resources: Additional resources (images, data files)
        variables: Template variables for Jinja2 substitution
    """

    title: str
    config: TemplateConfig
    content: str | None = None
    sections: list[Section] | None = None
    authors: list[Author] | str | None = None
    abstract: str | None = None
    keywords: list[str] | None = None
    acknowledgments: str | None = None
    bibliography: Path | InMemorySource | None = None
    bibliography_style: str | None = None
    date: str | None = None
    resources: list[Resource] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate document constraints."""
        # Disallow having BOTH content and sections (this is an error)
        if self.content is not None and self.sections is not None:
            raise ValueError("Cannot specify both content and sections")

        # Note: Missing content/sections is allowed (metadata-only documents)
        # The validator will warn about this

        # Validate configuration
        import warnings

        config_warnings = self.config.validate()
        for warning in config_warnings:
            warnings.warn(warning, UserWarning, stacklevel=2)

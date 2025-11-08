"""Document builder with fluent API and context manager support."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from b8tex.templates.config import TemplateConfig, TemplateMetadata, TemplateType, StatusMode, Author
from b8tex.templates.document import Section, TemplateDocument
from b8tex.templates.escape import Raw

if TYPE_CHECKING:
    from b8tex.core.document import InMemorySource, Resource


class DocumentBuilder:
    """Fluent builder for creating TemplateDocument with context managers.

    Supports three API styles:
    1. Fluent chaining: builder.add_section("Title").add_text("content")
    2. Context managers: with builder.section("Title"): builder.add_text(...)
    3. Dataclass: builder.build() returns TemplateDocument

    Example:
        with DocumentBuilder("My Paper", config) as builder:
            builder.add_abstract("This paper presents...")

            with builder.section("Introduction"):
                builder.add_text("Background information...")
                with builder.subsection("Motivation"):
                    builder.add_text("Why this work matters...")

            with builder.section("Methods"):
                builder.add_text("Our approach...")

            doc = builder.build()
    """

    def __init__(
        self,
        title: str | None = None,
        config: TemplateConfig | None = None,
        *,
        template: TemplateType | None = None,
        status: StatusMode = "final",
        organization: str | None = None,
        doc_type: str | None = None,
        doc_id: str | None = None,
    ):
        """Initialize document builder.

        Two initialization modes:

        1. Explicit config (backward compatible):
            DocumentBuilder(title="My Paper", config=TemplateConfig(...))

        2. Convenience parameters (new):
            DocumentBuilder(
                template="neurips",
                title="My Paper",
                status="draft",
                organization="Research Lab"
            )

        Args:
            title: Document title
            config: Template configuration (explicit mode)
            template: Template name (convenience mode)
            status: Document status mode (convenience mode)
            organization: Organization name for metadata (convenience mode)
            doc_type: Document type for metadata (convenience mode)
            doc_id: Document ID for metadata (convenience mode)

        Raises:
            ValueError: If neither config nor template is provided
        """
        # Determine which mode: explicit config or convenience parameters
        if config is not None:
            # Explicit mode: use provided config
            if template is not None:
                raise ValueError("Cannot specify both 'config' and 'template' parameters")
            if title is None:
                raise ValueError("'title' is required when using explicit config")
            self.config = config
            self.title = title
        elif template is not None:
            # Convenience mode: build config from parameters
            if title is None:
                raise ValueError("'title' is required")

            # Build metadata if any metadata parameters provided
            metadata = None
            if organization or doc_type or doc_id:
                metadata = TemplateMetadata(
                    organization=organization,
                    doc_type=doc_type,
                    doc_id=doc_id,
                )

            self.config = TemplateConfig(
                template=template,
                status=status,
                metadata=metadata,
            )
            self.title = title
        else:
            raise ValueError("Must provide either 'config' or 'template' parameter")

        # Document properties
        self._authors: list[Author] | str | None = None
        self._abstract: str | None = None
        self._keywords: list[str] | None = None
        self._acknowledgments: str | None = None
        self._bibliography: Path | InMemorySource | None = None
        self._bibliography_style: str | None = None
        self._resources: list[Resource] = []

        # Template variables for Jinja2
        self._variables: dict[str, Any] = {}

        # Section building state
        self._sections: list[Section] = []
        self._section_stack: list[_SectionBuilder] = []
        self._current_section: _SectionBuilder | None = None

    def __enter__(self) -> DocumentBuilder:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager, finalize any open sections."""
        # Close any remaining open sections
        while self._section_stack:
            self._end_section()

    def add_authors(self, authors: list[Author] | str) -> DocumentBuilder:
        """Set document authors.

        Args:
            authors: List of Author objects or author string

        Returns:
            Self for chaining
        """
        self._authors = authors
        return self

    def add_author(
        self,
        name: str,
        affiliation: str | None = None,
        email: str | None = None,
    ) -> DocumentBuilder:
        """Add a single author (convenience method).

        Args:
            name: Author name
            affiliation: Author affiliation
            email: Author email

        Returns:
            Self for chaining

        Raises:
            ValueError: If name is empty or whitespace
        """
        if not name or not name.strip():
            raise ValueError("Author name cannot be empty")

        author = Author(name=name, affiliation=affiliation, email=email)

        # Initialize authors list if needed
        if self._authors is None:
            self._authors = []
        elif isinstance(self._authors, str):
            # Convert string to list
            self._authors = [self._authors]

        # Ensure we have a list
        if not isinstance(self._authors, list):
            self._authors = [self._authors]

        self._authors.append(author)
        return self

    def add_abstract(self, text: str) -> DocumentBuilder:
        """Set document abstract.

        Args:
            text: Abstract text

        Returns:
            Self for chaining
        """
        self._abstract = text
        return self

    def set_abstract(self, text: str) -> DocumentBuilder:
        """Set document abstract (alias for add_abstract).

        Args:
            text: Abstract text

        Returns:
            Self for chaining
        """
        return self.add_abstract(text)

    def add_keywords(self, keywords: list[str]) -> DocumentBuilder:
        """Set document keywords.

        Args:
            keywords: List of keywords

        Returns:
            Self for chaining
        """
        self._keywords = keywords
        return self

    def add_keyword(self, keyword: str) -> DocumentBuilder:
        """Add a single keyword (convenience method).

        Args:
            keyword: Keyword to add

        Returns:
            Self for chaining
        """
        if self._keywords is None:
            self._keywords = []
        self._keywords.append(keyword)
        return self

    def add_acknowledgments(self, text: str) -> DocumentBuilder:
        """Set acknowledgments.

        Args:
            text: Acknowledgments text

        Returns:
            Self for chaining
        """
        self._acknowledgments = text
        return self

    def add_bibliography(
        self,
        bibliography: Path | InMemorySource,
        style: str | None = None,
    ) -> DocumentBuilder:
        """Set bibliography file and style.

        Args:
            bibliography: Path to .bib file or InMemorySource
            style: BibTeX style (e.g., 'plain', 'acl_natbib')

        Returns:
            Self for chaining
        """
        self._bibliography = bibliography
        if style:
            self._bibliography_style = style
        return self

    def add_resource(self, resource: Resource) -> DocumentBuilder:
        """Add a resource (image, data file, etc.).

        Args:
            resource: Resource to add

        Returns:
            Self for chaining
        """
        self._resources.append(resource)
        return self

    def section(self, title: str, numbered: bool = True, label: str | None = None):
        """Enter a section context.

        Args:
            title: Section title
            numbered: Whether section should be numbered
            label: Optional label for cross-references

        Returns:
            Context manager for section
        """
        return _SectionContext(self, title, level=1, numbered=numbered, label=label)

    def subsection(self, title: str, numbered: bool = True, label: str | None = None):
        """Enter a subsection context.

        Args:
            title: Subsection title
            numbered: Whether subsection should be numbered
            label: Optional label for cross-references

        Returns:
            Context manager for subsection
        """
        return _SectionContext(self, title, level=2, numbered=numbered, label=label)

    def subsubsection(self, title: str, numbered: bool = True, label: str | None = None):
        """Enter a subsubsection context.

        Args:
            title: Subsubsection title
            numbered: Whether subsubsection should be numbered
            label: Optional label for cross-references

        Returns:
            Context manager for subsubsection
        """
        return _SectionContext(self, title, level=3, numbered=numbered, label=label)

    def add_section(
        self,
        title: str,
        content: str = "",
        numbered: bool = True,
        label: str | None = None,
    ) -> DocumentBuilder:
        """Add a complete section (non-context manager style).

        Args:
            title: Section title
            content: Section content
            numbered: Whether section should be numbered
            label: Optional label for cross-references

        Returns:
            Self for chaining
        """
        section = Section(
            title=title,
            content=content,
            level=1,
            numbered=numbered,
            label=label,
        )
        self._sections.append(section)
        return self

    def add_text(self, text: str | Raw) -> DocumentBuilder:
        """Add text to current section.

        Args:
            text: Text content (escaped unless Raw)

        Returns:
            Self for chaining

        Raises:
            RuntimeError: If not in a section context
        """
        if self._current_section is None:
            raise RuntimeError("add_text() must be called within a section context")

        self._current_section.add_content(text)
        return self

    def add_raw_latex(self, latex: str) -> DocumentBuilder:
        """Add raw LaTeX to current section.

        Args:
            latex: Raw LaTeX code

        Returns:
            Self for chaining

        Raises:
            RuntimeError: If not in a section context
        """
        if self._current_section is None:
            raise RuntimeError("add_raw_latex() must be called within a section context")

        self._current_section.add_content(Raw(latex))
        return self

    def add_paragraph(self, text: str | Raw) -> DocumentBuilder:
        """Add paragraph to current section (alias for add_text).

        Args:
            text: Paragraph text (escaped unless Raw)

        Returns:
            Self for chaining

        Raises:
            RuntimeError: If not in a section context
        """
        return self.add_text(text)

    def set_variable(self, key: str, value: Any) -> DocumentBuilder:
        """Set a template variable for Jinja2 substitution.

        Template variables can be used in content with {{ variable_name }} syntax.

        Args:
            key: Variable name
            value: Variable value (will be converted to string)

        Returns:
            Self for chaining
        """
        self._variables[key] = value
        return self

    def add_table(
        self,
        data: Any,
        caption: str | None = None,
        label: str | None = None,
        **kwargs: Any,
    ) -> DocumentBuilder:
        """Add a table from data (DataFrame, dict, etc.).

        This is a convenience method that creates a DataTable and adds it as LaTeX.
        Requires pandas to be installed.

        Args:
            data: Data source (pandas DataFrame, dict, list of lists, etc.)
            caption: Table caption
            label: Table label for cross-references
            **kwargs: Additional arguments passed to DataTable constructor

        Returns:
            Self for chaining

        Raises:
            RuntimeError: If not in a section context
            ImportError: If pandas is not installed
        """
        if self._current_section is None:
            raise RuntimeError("add_table() must be called within a section context")

        try:
            from b8tex.templates.data import DataTable
        except ImportError as e:
            raise ImportError(
                "add_table() requires pandas. Install with: pip install 'b8tex[templates]'"
            ) from e

        # Create DataTable and get LaTeX
        table = DataTable(
            data=data,
            caption=caption,
            label=label,
            **kwargs,
        )
        latex = table.to_latex()

        # Add as raw LaTeX
        self._current_section.add_content(Raw(latex))
        return self

    def add_plot(
        self,
        source: Any,
        caption: str | None = None,
        label: str | None = None,
        **kwargs: Any,
    ) -> DocumentBuilder:
        """Add a plot/figure from matplotlib or file.

        This is a convenience method that creates a PlotData and adds it as LaTeX.
        Requires matplotlib to be installed if source is a Figure.

        Args:
            source: Plot source (matplotlib Figure, Path, or file-like)
            caption: Figure caption
            label: Figure label for cross-references
            **kwargs: Additional arguments passed to PlotData constructor

        Returns:
            Self for chaining

        Raises:
            RuntimeError: If not in a section context
            ImportError: If matplotlib is not installed (for Figure sources)
        """
        if self._current_section is None:
            raise RuntimeError("add_plot() must be called within a section context")

        try:
            from b8tex.templates.data import PlotData
        except ImportError as e:
            raise ImportError(
                "add_plot() requires matplotlib. Install with: pip install 'b8tex[templates]'"
            ) from e

        # Create PlotData and get LaTeX
        plot = PlotData(
            source=source,
            caption=caption,
            label=label,
            **kwargs,
        )
        latex = plot.to_latex()

        # Add as raw LaTeX
        self._current_section.add_content(Raw(latex))
        return self

    def build(self) -> TemplateDocument:
        """Build the final TemplateDocument.

        Returns:
            Constructed TemplateDocument

        Raises:
            RuntimeError: If sections are still open
        """
        if self._section_stack:
            raise RuntimeError(
                f"{len(self._section_stack)} section(s) still open. "
                "Close all section contexts before calling build()."
            )

        return TemplateDocument(
            title=self.title,
            config=self.config,
            sections=self._sections if self._sections else None,
            authors=self._authors,
            abstract=self._abstract,
            keywords=self._keywords,
            acknowledgments=self._acknowledgments,
            bibliography=self._bibliography,
            bibliography_style=self._bibliography_style,
            resources=self._resources,
            variables=self._variables,
        )

    def _begin_section(
        self,
        title: str,
        level: int,
        numbered: bool,
        label: str | None,
    ) -> None:
        """Begin a new section (internal).

        Args:
            title: Section title
            level: Section level (1-4)
            numbered: Whether numbered
            label: Optional label
        """
        section_builder = _SectionBuilder(title, level, numbered, label)

        # Push to stack
        self._section_stack.append(section_builder)
        self._current_section = section_builder

    def _end_section(self) -> None:
        """End current section (internal)."""
        if not self._section_stack:
            raise RuntimeError("No section to end")

        # Pop from stack
        finished_section = self._section_stack.pop()
        section = finished_section.build()

        # Add to parent or root
        if self._section_stack:
            # Add as subsection of parent
            parent = self._section_stack[-1]
            parent.add_subsection(section)
            self._current_section = parent
        else:
            # Add to root sections
            self._sections.append(section)
            self._current_section = None


class _SectionBuilder:
    """Internal builder for a single section."""

    def __init__(self, title: str, level: int, numbered: bool, label: str | None):
        self.title = title
        self.level = level
        self.numbered = numbered
        self.label = label
        self.content_parts: list[str] = []
        self.subsections: list[Section] = []

    def add_content(self, text: str | Raw) -> None:
        """Add content to this section."""
        self.content_parts.append(str(text))

    def add_subsection(self, section: Section) -> None:
        """Add a subsection."""
        self.subsections.append(section)

    def build(self) -> Section:
        """Build the Section object."""
        content = "\n\n".join(self.content_parts)
        return Section(
            title=self.title,
            content=content,
            level=self.level,
            numbered=self.numbered,
            label=self.label,
            subsections=tuple(self.subsections),
        )


class _SectionContext:
    """Context manager for section building."""

    def __init__(
        self,
        builder: DocumentBuilder,
        title: str,
        level: int,
        numbered: bool,
        label: str | None,
    ):
        self.builder = builder
        self.title = title
        self.level = level
        self.numbered = numbered
        self.label = label

    def __enter__(self) -> DocumentBuilder:
        """Enter section context."""
        self.builder._begin_section(self.title, self.level, self.numbered, self.label)
        return self.builder

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit section context."""
        self.builder._end_section()

"""Template renderer for generating LaTeX from TemplateDocument."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from b8tex.core.document import Document, InMemorySource, Resource
from b8tex.templates.escape import Raw, escape_latex

if TYPE_CHECKING:
    from b8tex.templates.config import Author
    from b8tex.templates.document import Section, TemplateDocument


class TemplateRenderer:
    """Renders TemplateDocument to LaTeX and b8tex Document.

    This class generates LaTeX source code from a structured TemplateDocument
    and converts it to a b8tex Document for compilation.
    """

    def __init__(self, template_doc: TemplateDocument):
        """Initialize renderer with a template document.

        Args:
            template_doc: Document to render
        """
        self.doc = template_doc
        self.config = template_doc.config
        self.template_name = self.config.template

    def render_latex(self) -> str:
        """Render document to complete LaTeX string.

        Returns:
            Complete LaTeX document source
        """
        parts = [
            self._render_document_class(),
            self._render_preamble(),
            r"\begin{document}",
            self._render_body(),
            r"\end{document}",
        ]

        return "\n\n".join(parts)

    def to_document(self, name: str = "document") -> Document:
        """Convert to b8tex Document for compilation.

        Args:
            name: Output name for the document

        Returns:
            b8tex Document object ready for compilation
        """
        latex_source = self.render_latex()
        entrypoint = InMemorySource(f"{name}.tex", latex_source)

        # Load template style file
        style_path = Path(__file__).parent / "styles" / f"{self.template_name}.sty"
        style_content = style_path.read_text(encoding="utf-8")
        style_resource = Resource(
            InMemorySource(f"{self.template_name}.sty", style_content),
            kind="sty",
        )

        # Combine with user resources
        resources = [style_resource] + self.doc.resources

        # Add bibliography if provided
        if self.doc.bibliography:
            if isinstance(self.doc.bibliography, Path):
                resources.append(Resource(self.doc.bibliography, kind="bib"))
            else:
                # InMemorySource
                resources.append(Resource(self.doc.bibliography, kind="bib"))

        return Document(
            name=name,
            entrypoint=entrypoint,
            resources=resources,
        )

    def _render_document_class(self) -> str:
        """Generate \\documentclass line.

        Returns:
            Document class declaration
        """
        options = self.config.get_document_class_options()

        if options:
            return f"\\documentclass[{','.join(options)}]{{article}}"
        return r"\documentclass{article}"

    def _render_preamble(self) -> str:
        """Generate preamble with style and metadata.

        Returns:
            Document preamble
        """
        lines = []

        # Load template style with options
        style_options = self.config.get_style_options()
        lines.append(f"\\usepackage[{','.join(style_options)}]{{{self.template_name}}}")

        # Set metadata commands
        if self.config.metadata:
            if self.config.metadata.organization:
                org = escape_latex(self.config.metadata.organization)
                lines.append(f"\\setorganization{{{org}}}")

            if self.config.metadata.doc_type:
                doc_type = escape_latex(self.config.metadata.doc_type)
                lines.append(f"\\setdoctype{{{doc_type}}}")

            if self.config.metadata.doc_id:
                doc_id = escape_latex(self.config.metadata.doc_id)
                lines.append(f"\\setdocid{{{doc_id}}}")

        # Standard packages (commonly needed)
        lines.extend([
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[T1]{fontenc}",
        ])

        # Hyperref (if enabled)
        if self.config.hyperref:
            lines.append(r"\usepackage{hyperref}")

        # More standard packages
        lines.extend([
            r"\usepackage{graphicx}",
            r"\usepackage{amsmath}",
            r"\usepackage{booktabs}",
        ])

        # Custom packages
        for pkg_name, pkg_options in self.config.custom_packages:
            if pkg_options:
                lines.append(f"\\usepackage[{pkg_options}]{{{pkg_name}}}")
            else:
                lines.append(f"\\usepackage{{{pkg_name}}}")

        # Custom commands
        for cmd_name, cmd_def in self.config.custom_commands.items():
            lines.append(f"\\newcommand{{\\{cmd_name}}}{{{cmd_def}}}")

        # Title
        title = escape_latex(self.doc.title)
        lines.append(f"\\title{{{title}}}")

        # Authors
        if self.doc.authors:
            authors_str = self._format_authors(self.doc.authors)
            lines.append(f"\\author{{{authors_str}}}")

        # Date (if specified)
        if self.doc.date:
            # Don't escape if it's \today or other LaTeX command
            if self.doc.date.startswith("\\"):
                lines.append(f"\\date{{{self.doc.date}}}")
            else:
                date = escape_latex(self.doc.date)
                lines.append(f"\\date{{{date}}}")

        return "\n".join(lines)

    def _render_body(self) -> str:
        """Generate document body.

        Returns:
            Document body content
        """
        lines = [r"\maketitle"]

        # Abstract
        if self.doc.abstract:
            abstract = self._process_content(self.doc.abstract)
            lines.append(f"\\begin{{abstract}}\n{abstract}\n\\end{{abstract}}")

        # Keywords (rendered as comment since templates don't provide \keywords command)
        if self.doc.keywords:
            keywords_str = ", ".join(escape_latex(kw) for kw in self.doc.keywords)
            lines.append(f"% Keywords: {keywords_str}")

        # Main content
        if self.doc.content:
            content = self._process_content(self.doc.content)
            lines.append(content)
        elif self.doc.sections:
            # Pass document variables as context for conditional sections
            lines.append(self._render_sections(self.doc.sections, context=self.doc.variables))

        # Acknowledgments
        if self.doc.acknowledgments:
            ack = self._process_content(self.doc.acknowledgments)
            lines.append(f"\\begin{{ack}}\n{ack}\n\\end{{ack}}")

        # Bibliography
        if self.doc.bibliography:
            style = self.doc.bibliography_style or "plain"
            lines.append(f"\\bibliographystyle{{{style}}}")

            if isinstance(self.doc.bibliography, Path):
                bib_name = self.doc.bibliography.stem
            else:
                # InMemorySource
                bib_name = self.doc.bibliography.filename.replace(".bib", "")

            lines.append(f"\\bibliography{{{bib_name}}}")

        return "\n\n".join(lines)

    def _render_sections(self, sections: list[Section], context: dict | None = None) -> str:
        """Render sections to LaTeX.

        Args:
            sections: List of sections to render
            context: Optional context for conditional sections

        Returns:
            Rendered sections as LaTeX
        """
        from b8tex.templates.document import ConditionalSection

        lines = []

        for section in sections:
            # Check if section should be included (for ConditionalSection)
            if isinstance(section, ConditionalSection):
                if not section.should_include(context):
                    continue

            # Map level to LaTeX command
            commands = ["section", "subsection", "subsubsection", "paragraph"]
            cmd_index = min(section.level - 1, len(commands) - 1)
            cmd = commands[cmd_index]

            # Add star for unnumbered sections
            if not section.numbered:
                cmd += "*"

            # Render section title
            title = escape_latex(section.title)
            lines.append(f"\\{cmd}{{{title}}}")

            # Add label if provided
            if section.label:
                from b8tex.templates.escape import sanitize_label
                safe_label = sanitize_label(section.label)
                lines.append(f"\\label{{{safe_label}}}")

            # Render content
            if section.content:
                content = self._process_content(section.content)
                lines.append(content)

            # Render subsections
            if section.subsections:
                subsections_latex = self._render_sections(list(section.subsections), context)
                lines.append(subsections_latex)

        return "\n\n".join(lines)

    def _format_authors(self, authors: list[Author] | str) -> str:
        """Format authors for LaTeX.

        Args:
            authors: List of Author objects or author string

        Returns:
            Formatted author string
        """
        if isinstance(authors, str):
            # Allow raw LaTeX author strings
            if isinstance(authors, Raw):
                return authors
            return escape_latex(authors)

        # Format structured authors
        author_lines = []
        for author in authors:
            parts = [escape_latex(author.name)]

            if author.affiliation:
                parts.append(escape_latex(author.affiliation))

            if author.email:
                # Email in texttt (monospace)
                parts.append(f"\\texttt{{{escape_latex(author.email)}}}")

            author_lines.append(" \\\\\n  ".join(parts))

        result = " \\and\n".join(author_lines)

        # Handle ACL-specific metadata placement
        if self.template_name == "acl":
            auto_placement = self.config.template_options.get("metadata_placement", "auto")
            if auto_placement == "auto" and author_lines:
                result += r"\aclmetadata"

        return result

    def _process_content(self, content: str) -> str:
        """Process content with Jinja2 template variables if enabled.

        Uses SandboxedEnvironment for security to prevent template injection attacks.

        Args:
            content: Content string (may contain {{variables}})

        Returns:
            Processed content with variables substituted
        """
        # If content is Raw, don't escape or process
        if isinstance(content, Raw):
            return content

        # Check if Jinja2 processing is needed
        if "{{" in content or "{%" in content:
            try:
                from jinja2.sandbox import SandboxedEnvironment
                from b8tex.templates.escape import escape_latex as jinja_escape

                # Use sandboxed environment for security
                env = SandboxedEnvironment()

                # Provide escape_latex as a filter
                env.globals["escape_latex"] = jinja_escape
                env.filters["escape_latex"] = jinja_escape

                # Create template from content
                template = env.from_string(content)

                # Use document variables for substitution
                variables = self.doc.variables.copy()

                # Also include config template_options for backward compatibility
                variables.update(self.config.template_options)

                return template.render(**variables)
            except ImportError:
                # Jinja2 not installed, return as-is
                import warnings
                warnings.warn(
                    "Jinja2 templates detected but jinja2 is not installed. "
                    "Install with: pip install jinja2",
                    UserWarning,
                    stacklevel=3,
                )
                return content

        # Content is assumed to be raw LaTeX by default
        # Users can use escape_latex() explicitly if needed
        return content

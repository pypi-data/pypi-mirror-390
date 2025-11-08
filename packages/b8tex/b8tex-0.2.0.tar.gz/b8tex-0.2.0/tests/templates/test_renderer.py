"""Tests for template renderer."""

from __future__ import annotations

from pathlib import Path

import pytest

from b8tex.core.document import Document, InMemorySource
from b8tex.templates.config import Author, TemplateConfig, TemplateMetadata
from b8tex.templates.document import ConditionalSection, Section, TemplateDocument
from b8tex.templates.escape import Raw
from b8tex.templates.renderer import TemplateRenderer


class TestRendererBasics:
    """Tests for basic renderer functionality."""

    def test_create_renderer(self):
        """Renderer should be created from TemplateDocument."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)

        assert renderer.doc == doc
        assert renderer.template_name == "neurips"

    def test_render_minimal_document(self):
        """Minimal document should render to valid LaTeX."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test Document", config=config, content="Content")
        renderer = TemplateRenderer(doc)

        latex = renderer.render_latex()

        assert isinstance(latex, str)
        assert r"\documentclass" in latex
        assert r"\begin{document}" in latex
        assert r"\end{document}" in latex
        assert "Test Document" in latex

    def test_render_with_abstract(self):
        """Document with abstract should render abstract."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            abstract="This is the abstract.",
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\begin{abstract}" in latex
        assert "This is the abstract." in latex
        assert r"\end{abstract}" in latex

    def test_render_string_authors(self):
        """String authors should be rendered."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            authors="John Doe, Jane Smith",
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert "John Doe, Jane Smith" in latex

    def test_render_author_list(self):
        """Author list should be rendered."""
        config = TemplateConfig(template="neurips")
        authors = [
            Author(name="Alice Brown", affiliation="MIT"),
            Author(name="Bob Johnson", affiliation="Stanford", email="bob@stanford.edu"),
        ]
        doc = TemplateDocument(title="Test", config=config, authors=authors)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert "Alice Brown" in latex
        assert "Bob Johnson" in latex
        assert "MIT" in latex
        assert "Stanford" in latex


class TestDocumentClass:
    """Tests for document class rendering."""

    def test_neurips_document_class(self):
        """NeurIPS template should use neurips package."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\documentclass{article}" in latex
        assert r"\usepackage{neurips}" in latex or r"\usepackage[final]{neurips}" in latex

    def test_iclr_document_class(self):
        """ICLR template should use iclr package."""
        config = TemplateConfig(template="iclr")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\documentclass{article}" in latex
        assert r"\usepackage{iclr}" in latex or r"\usepackage[final]{iclr}" in latex

    def test_acl_document_class(self):
        """ACL template should use acl package."""
        config = TemplateConfig(template="acl")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\documentclass" in latex
        assert r"\usepackage{acl}" in latex or r"\usepackage[final]{acl}" in latex

    def test_status_mode_final(self):
        """Final status should be passed to package."""
        config = TemplateConfig(template="neurips", status="final")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\usepackage[final]{neurips}" in latex

    def test_status_mode_draft(self):
        """Draft status should be passed to package."""
        config = TemplateConfig(template="neurips", status="draft")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\usepackage[draft]{neurips}" in latex

    def test_font_size_option(self):
        """Font size should be passed to document class."""
        config = TemplateConfig(template="neurips", font_size="12pt")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert "12pt" in latex


class TestMetadataCommands:
    """Tests for metadata command rendering."""

    def test_metadata_organization(self):
        """Organization metadata should render setorganization command."""
        metadata = TemplateMetadata(organization="OpenAI")
        config = TemplateConfig(template="neurips", metadata=metadata)
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\setorganization{OpenAI}" in latex

    def test_metadata_doc_type(self):
        """Doc type metadata should render setdoctype command."""
        metadata = TemplateMetadata(doc_type="Technical Report")
        config = TemplateConfig(template="neurips", metadata=metadata)
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\setdoctype{Technical Report}" in latex

    def test_metadata_doc_id(self):
        """Doc ID metadata should render setdocid command."""
        metadata = TemplateMetadata(doc_id="TR-2024-001")
        config = TemplateConfig(template="neurips", metadata=metadata)
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\setdocid{TR-2024-001}" in latex

    def test_all_metadata(self):
        """All metadata fields should render."""
        metadata = TemplateMetadata(
            organization="Research Lab",
            doc_type="Paper",
            doc_id="P-001",
        )
        config = TemplateConfig(template="neurips", metadata=metadata)
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\setorganization{Research Lab}" in latex
        assert r"\setdoctype{Paper}" in latex
        assert r"\setdocid{P-001}" in latex


class TestSectionRendering:
    """Tests for section rendering."""

    def test_render_single_section(self):
        """Single section should render correctly."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="Introduction", content="This is the intro.")]
        doc = TemplateDocument(title="Test", config=config, sections=sections)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\section{Introduction}" in latex
        assert "This is the intro." in latex

    def test_render_multiple_sections(self):
        """Multiple sections should render in order."""
        config = TemplateConfig(template="neurips")
        sections = [
            Section(title="Introduction", content="Intro content"),
            Section(title="Methods", content="Methods content"),
            Section(title="Results", content="Results content"),
        ]
        doc = TemplateDocument(title="Test", config=config, sections=sections)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\section{Introduction}" in latex
        assert r"\section{Methods}" in latex
        assert r"\section{Results}" in latex

        # Check order
        intro_pos = latex.index("Introduction")
        methods_pos = latex.index("Methods")
        results_pos = latex.index("Results")
        assert intro_pos < methods_pos < results_pos

    def test_render_subsection(self):
        """Subsection should render with subsection command."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="Subsection Title", content="Content", level=2)]
        doc = TemplateDocument(title="Test", config=config, sections=sections)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\subsection{Subsection Title}" in latex

    def test_render_subsubsection(self):
        """Subsubsection should render with subsubsection command."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="SubSubsection", content="Content", level=3)]
        doc = TemplateDocument(title="Test", config=config, sections=sections)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\subsubsection{SubSubsection}" in latex

    def test_render_nested_sections(self):
        """Nested sections should render hierarchically."""
        config = TemplateConfig(template="neurips")
        subsec = Section(title="Subsection", content="Sub content", level=2)
        main = Section(title="Main", content="Main content", level=1, subsections=(subsec,))
        doc = TemplateDocument(title="Test", config=config, sections=[main])
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\section{Main}" in latex
        assert r"\subsection{Subsection}" in latex
        assert "Main content" in latex
        assert "Sub content" in latex

    def test_unnumbered_section(self):
        """Unnumbered section should use starred command."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="Acknowledgments", numbered=False)]
        doc = TemplateDocument(title="Test", config=config, sections=sections)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\section*{Acknowledgments}" in latex

    def test_section_with_label(self):
        """Section with label should render label command."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="Introduction", label="sec:intro")]
        doc = TemplateDocument(title="Test", config=config, sections=sections)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\label{sec:intro}" in latex


class TestRawContent:
    """Tests for raw content rendering."""

    def test_render_raw_content(self):
        """Raw content should be rendered as-is."""
        config = TemplateConfig(template="neurips")
        content = r"\section{Intro} \textbf{Bold} \textit{Italic}"
        doc = TemplateDocument(title="Test", config=config, content=content)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\section{Intro}" in latex
        assert r"\textbf{Bold}" in latex
        assert r"\textit{Italic}" in latex

    def test_raw_content_not_escaped(self):
        """Raw content should not be escaped."""
        config = TemplateConfig(template="neurips")
        content = r"Special chars: $ % & # _ { } ~ ^"
        doc = TemplateDocument(title="Test", config=config, content=content)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        # Raw content should appear unescaped
        assert content in latex


class TestConditionalSections:
    """Tests for conditional section rendering."""

    def test_conditional_section_visible(self):
        """Conditional section should render when condition is true."""
        config = TemplateConfig(template="neurips")
        sections = [
            ConditionalSection(
                title="Appendix",
                content="Appendix content",
                condition="show_appendix",
            ),
        ]
        doc = TemplateDocument(
            title="Test",
            config=config,
            sections=sections,
            variables={"show_appendix": True},
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\section{Appendix}" in latex
        assert "Appendix content" in latex

    def test_conditional_section_hidden(self):
        """Conditional section should not render when condition is false."""
        config = TemplateConfig(template="neurips")
        sections = [
            ConditionalSection(
                title="Appendix",
                content="Appendix content",
                condition="show_appendix",
            ),
        ]
        doc = TemplateDocument(
            title="Test",
            config=config,
            sections=sections,
            variables={"show_appendix": False},
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\section{Appendix}" not in latex
        assert "Appendix content" not in latex

    def test_conditional_default_visible(self):
        """Conditional section with default_visible=True should show by default."""
        config = TemplateConfig(template="neurips")
        sections = [
            ConditionalSection(
                title="Methods",
                content="Methods content",
                condition="show_methods",
                default_visible=True,
            ),
        ]
        doc = TemplateDocument(
            title="Test",
            config=config,
            sections=sections,
            # No template_variables provided
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\section{Methods}" in latex


class TestBibliography:
    """Tests for bibliography rendering."""

    def test_bibliography_file(self):
        """Bibliography file should render bibliography command."""
        config = TemplateConfig(template="neurips")
        from b8tex.core.document import InMemorySource
        doc = TemplateDocument(
            title="Test",
            config=config,
            bibliography=InMemorySource("references.bib", "@article{test, title={Test}}"),
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\bibliography{references}" in latex  # .bib extension removed

    def test_bibliography_style(self):
        """Bibliography style should render bibliographystyle command."""
        config = TemplateConfig(template="neurips")
        from b8tex.core.document import InMemorySource
        doc = TemplateDocument(
            title="Test",
            config=config,
            bibliography=InMemorySource("refs.bib", "@article{test, title={Test}}"),
            bibliography_style="plain",
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\bibliographystyle{plain}" in latex

    def test_no_bibliography(self):
        """Document without bibliography should not have bib commands."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\bibliography" not in latex
        assert r"\bibliographystyle" not in latex


class TestCustomization:
    """Tests for custom packages and commands."""

    def test_custom_packages(self):
        """Custom packages should be included."""
        config = TemplateConfig(
            template="neurips",
            custom_packages=[("graphicx", None), ("amsmath", "fleqn")],
        )
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\usepackage{graphicx}" in latex
        assert r"\usepackage[fleqn]{amsmath}" in latex

    def test_custom_commands(self):
        """Custom commands should be defined."""
        config = TemplateConfig(
            template="neurips",
            custom_commands={
                "RR": r"\mathbb{R}",
                "NN": r"\mathbb{N}",
            },
        )
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\newcommand{\RR}{\mathbb{R}}" in latex
        assert r"\newcommand{\NN}{\mathbb{N}}" in latex


class TestToDocument:
    """Tests for converting to b8tex Document."""

    def test_to_document_basic(self):
        """Renderer should convert to b8tex Document."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)

        b8tex_doc = renderer.to_document()

        assert isinstance(b8tex_doc, Document)
        assert b8tex_doc.name == "document"
        assert isinstance(b8tex_doc.entrypoint, InMemorySource)

    def test_to_document_custom_name(self):
        """Document should support custom name."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)

        b8tex_doc = renderer.to_document(name="my_paper")

        assert b8tex_doc.name == "my_paper"

    def test_to_document_includes_style(self):
        """Document should include template style file."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")
        renderer = TemplateRenderer(doc)

        b8tex_doc = renderer.to_document()

        # Should have at least one resource (the style file)
        assert len(b8tex_doc.resources) >= 1

        # Check for neurips.sty resource
        style_resources = [
            r for r in b8tex_doc.resources
            if hasattr(r.path_or_mem, "filename") and r.path_or_mem.filename == "neurips.sty"
        ]
        assert len(style_resources) == 1

    def test_to_document_preserves_resources(self):
        """Document should preserve user-provided resources."""
        from b8tex.core.document import Resource

        config = TemplateConfig(template="neurips")
        user_resource = Resource(Path("image.png"))
        doc = TemplateDocument(title="Test", config=config, resources=[user_resource])
        renderer = TemplateRenderer(doc)

        b8tex_doc = renderer.to_document()

        # Should have style + user resource
        assert len(b8tex_doc.resources) >= 2


class TestTemplateVariables:
    """Tests for Jinja2 template variable rendering."""

    def test_simple_variable_substitution(self):
        """Simple variables should be substituted."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content="Value: {{ variable_name }}",
            variables={"variable_name": "test_value"},
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert "Value: test_value" in latex
        assert "{{ variable_name }}" not in latex

    def test_section_content_variable(self):
        """Variables in section content should be substituted."""
        config = TemplateConfig(template="neurips")
        sections = [
            Section(
                title="Results",
                content="Accuracy: {{ accuracy }}%",
            ),
        ]
        doc = TemplateDocument(
            title="Test",
            config=config,
            sections=sections,
            variables={"accuracy": 95.5},
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert "Accuracy: 95.5%" in latex

    def test_no_variables_no_error(self):
        """Content without variables should work."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content="No variables here",
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert "No variables here" in latex


class TestEscaping:
    """Tests for LaTeX escaping in renderer."""

    def test_title_escaping(self):
        """Title with special characters should be escaped."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test & Research: 50% Complete", config=config, content="Content")
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        # Title should be escaped
        assert r"\&" in latex
        assert r"\%" in latex

    def test_author_name_escaping(self):
        """Author names with special characters should be escaped."""
        config = TemplateConfig(template="neurips")
        authors = [Author(name="O'Brien & Smith")]
        doc = TemplateDocument(title="Test", config=config, authors=authors)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        assert r"\&" in latex

    def test_abstract_escaping(self):
        """Abstract with special characters should be escaped."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            abstract="We achieve 95% accuracy with $100 budget.",
        )
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        # Abstract should be escaped
        assert r"\%" in latex
        assert r"\$" in latex

    def test_raw_content_not_escaped(self):
        """Raw() content should not be escaped."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="Test", content=Raw(r"\textbf{Bold} & $math$"))]
        doc = TemplateDocument(title="Test", config=config, sections=sections)
        renderer = TemplateRenderer(doc)
        latex = renderer.render_latex()

        # Raw content should not be escaped
        assert r"\textbf{Bold} & $math$" in latex

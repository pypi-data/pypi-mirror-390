"""Tests for template document models."""

from __future__ import annotations

import pytest

from b8tex.templates.config import Author, TemplateConfig
from b8tex.templates.document import ConditionalSection, Section, TemplateDocument


class TestSection:
    """Tests for Section dataclass."""

    def test_create_minimal(self):
        """Section with just title should be valid."""
        section = Section(title="Introduction")
        assert section.title == "Introduction"
        assert section.content == ""
        assert section.level == 1
        assert section.label is None
        assert section.numbered is True
        assert len(section.subsections) == 0

    def test_create_with_content(self):
        """Section with content should be valid."""
        section = Section(title="Methods", content="This is the methods section.")
        assert section.title == "Methods"
        assert section.content == "This is the methods section."

    def test_section_levels(self):
        """Different section levels should be supported."""
        section1 = Section(title="Main", level=1)
        section2 = Section(title="Sub", level=2)
        section3 = Section(title="SubSub", level=3)

        assert section1.level == 1
        assert section2.level == 2
        assert section3.level == 3

    def test_section_with_label(self):
        """Section with label should be valid."""
        section = Section(title="Introduction", label="sec:intro")
        assert section.label == "sec:intro"

    def test_unnumbered_section(self):
        """Unnumbered section should be supported."""
        section = Section(title="Acknowledgments", numbered=False)
        assert section.numbered is False

    def test_section_with_subsections(self):
        """Section with subsections should be valid."""
        sub1 = Section(title="Subsection 1", level=2)
        sub2 = Section(title="Subsection 2", level=2)
        parent = Section(title="Parent", subsections=(sub1, sub2))

        assert len(parent.subsections) == 2
        assert parent.subsections[0].title == "Subsection 1"
        assert parent.subsections[1].title == "Subsection 2"

    def test_nested_subsections(self):
        """Nested subsections should be supported."""
        subsub = Section(title="SubSub", level=3)
        sub = Section(title="Sub", level=2, subsections=(subsub,))
        parent = Section(title="Parent", level=1, subsections=(sub,))

        assert len(parent.subsections) == 1
        assert parent.subsections[0].title == "Sub"
        assert len(parent.subsections[0].subsections) == 1
        assert parent.subsections[0].subsections[0].title == "SubSub"

    def test_section_immutability(self):
        """Section should be immutable."""
        section = Section(title="Test")
        with pytest.raises(AttributeError):
            section.title = "Changed"  # type: ignore

    def test_section_equality(self):
        """Sections should support equality."""
        section1 = Section(title="Test", content="Content")
        section2 = Section(title="Test", content="Content")
        section3 = Section(title="Test", content="Different")

        assert section1 == section2
        assert section1 != section3

    def test_section_with_all_fields(self):
        """Section with all fields should be valid."""
        subsection = Section(title="Sub", level=2)
        section = Section(
            title="Complete Section",
            content="Full content here.",
            level=1,
            label="sec:complete",
            numbered=True,
            subsections=(subsection,),
        )

        assert section.title == "Complete Section"
        assert section.content == "Full content here."
        assert section.level == 1
        assert section.label == "sec:complete"
        assert section.numbered is True
        assert len(section.subsections) == 1


class TestConditionalSection:
    """Tests for ConditionalSection dataclass."""

    def test_create_basic(self):
        """Basic conditional section should be valid."""
        section = ConditionalSection(
            title="Methods",
            content="Methods content",
            condition="show_methods",
        )
        assert section.title == "Methods"
        assert section.content == "Methods content"
        assert section.condition == "show_methods"

    def test_conditional_with_default(self):
        """Conditional section with default should be valid."""
        section = ConditionalSection(
            title="Appendix",
            content="Appendix content",
            condition="show_appendix",
            default_visible=False,
        )
        assert section.condition == "show_appendix"
        assert section.default_visible is False

    def test_conditional_inherits_section(self):
        """ConditionalSection should inherit from Section."""
        section = ConditionalSection(
            title="Test",
            content="Content",
            condition="test_condition",
        )
        assert isinstance(section, Section)
        assert section.level == 1
        assert section.numbered is True

    def test_conditional_with_level(self):
        """Conditional section with custom level should work."""
        section = ConditionalSection(
            title="Test",
            content="Content",
            condition="test",
            level=2,
        )
        assert section.level == 2

    def test_conditional_immutability(self):
        """ConditionalSection should be immutable."""
        section = ConditionalSection(
            title="Test",
            content="Content",
            condition="test",
        )
        with pytest.raises(AttributeError):
            section.condition = "changed"  # type: ignore


class TestTemplateDocument:
    """Tests for TemplateDocument dataclass."""

    def test_create_minimal(self):
        """Document with minimal fields should be valid."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test Paper", config=config, content="Content")

        assert doc.title == "Test Paper"
        assert doc.config == config
        assert doc.content == "Content"
        assert doc.sections is None
        assert doc.authors is None
        assert doc.abstract is None

    def test_create_with_content(self):
        """Document with raw content should be valid."""
        config = TemplateConfig(template="neurips")
        content = r"\section{Introduction} This is the introduction."
        doc = TemplateDocument(title="Test", config=config, content=content)

        assert doc.content == content
        assert doc.sections is None

    def test_create_with_sections(self):
        """Document with structured sections should be valid."""
        config = TemplateConfig(template="neurips")
        sections = [
            Section(title="Introduction", content="Intro content"),
            Section(title="Methods", content="Methods content"),
        ]
        doc = TemplateDocument(title="Test", config=config, sections=sections)

        assert doc.sections == sections
        assert doc.content is None
        assert len(doc.sections) == 2

    def test_cannot_have_both_content_and_sections(self):
        """Document cannot have both content and sections."""
        config = TemplateConfig(template="neurips")
        # Should raise ValueError
        with pytest.raises(ValueError, match="Cannot specify both"):
            TemplateDocument(
                title="Test",
                config=config,
                content="raw content",
                sections=[Section(title="Section")],
            )

    def test_with_string_authors(self):
        """Document with authors as string should be valid."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            authors="John Doe, Jane Smith",
        )
        assert doc.authors == "John Doe, Jane Smith"

    def test_with_author_list(self):
        """Document with author list should be valid."""
        config = TemplateConfig(template="neurips")
        authors = [
            Author(name="John Doe", affiliation="MIT"),
            Author(name="Jane Smith", affiliation="Stanford"),
        ]
        doc = TemplateDocument(title="Test", config=config, authors=authors)

        assert doc.authors == authors
        assert len(doc.authors) == 2
        assert doc.authors[0].name == "John Doe"

    def test_with_abstract(self):
        """Document with abstract should be valid."""
        config = TemplateConfig(template="neurips")
        abstract = "This paper presents a novel approach to..."
        doc = TemplateDocument(title="Test", config=config, abstract=abstract)

        assert doc.abstract == abstract

    def test_with_keywords(self):
        """Document with keywords should be valid."""
        config = TemplateConfig(template="neurips")
        keywords = ["machine learning", "neural networks", "optimization"]
        doc = TemplateDocument(title="Test", config=config, keywords=keywords)

        assert doc.keywords == keywords
        assert len(doc.keywords) == 3

    def test_with_acknowledgments(self):
        """Document with acknowledgments should be valid."""
        config = TemplateConfig(template="neurips")
        ack = "We thank the reviewers for their helpful feedback."
        doc = TemplateDocument(title="Test", config=config, acknowledgments=ack)

        assert doc.acknowledgments == ack

    def test_with_bibliography(self):
        """Document with bibliography should be valid."""
        from b8tex.core.document import InMemorySource
        config = TemplateConfig(template="neurips")
        bib = InMemorySource("references.bib", "@article{test, title={Test}}")
        doc = TemplateDocument(
            title="Test",
            config=config,
            bibliography=bib,
            bibliography_style="plain",
        )

        assert doc.bibliography == bib
        assert doc.bibliography_style == "plain"

    def test_with_date(self):
        """Document with date should be valid."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, date="January 2024")

        assert doc.date == "January 2024"

    def test_with_resources(self):
        """Document with resources should be valid."""
        from b8tex.core.document import Resource
        from pathlib import Path

        config = TemplateConfig(template="neurips")
        resources = [
            Resource(Path("image.png")),
            Resource(Path("references.bib")),
        ]
        doc = TemplateDocument(title="Test", config=config, resources=resources)

        assert doc.resources == resources
        assert len(doc.resources) == 2

    def test_with_template_variables(self):
        """Document with Jinja2 variables should be valid."""
        config = TemplateConfig(template="neurips")
        variables = {
            "author_count": 3,
            "institution": "MIT",
            "year": 2024,
        }
        doc = TemplateDocument(
            title="Test",
            config=config,
            variables=variables,
        )

        assert doc.variables == variables
        assert doc.variables["author_count"] == 3

    def test_complete_document(self):
        """Document with all fields should be valid."""
        from b8tex.templates.config import TemplateMetadata

        metadata = TemplateMetadata(organization="MIT", doc_type="Paper")
        config = TemplateConfig(template="neurips", metadata=metadata)

        authors = [
            Author(name="Alice", affiliation="MIT", email="alice@mit.edu"),
            Author(name="Bob", affiliation="Stanford"),
        ]

        sections = [
            Section(title="Introduction", content="Intro..."),
            Section(title="Methods", content="Methods..."),
            Section(title="Results", content="Results..."),
        ]

        from b8tex.core.document import InMemorySource
        bib = InMemorySource("refs.bib", "@article{test, title={Test}}")
        doc = TemplateDocument(
            title="Complete Test Document",
            config=config,
            sections=sections,
            authors=authors,
            abstract="This is the abstract.",
            keywords=["keyword1", "keyword2"],
            acknowledgments="Thanks to everyone.",
            bibliography=bib,
            bibliography_style="plain",
            date="January 2024",
            variables={"version": "1.0"},
        )

        assert doc.title == "Complete Test Document"
        assert len(doc.sections) == 3
        assert len(doc.authors) == 2
        assert doc.abstract == "This is the abstract."
        assert len(doc.keywords) == 2
        assert doc.acknowledgments == "Thanks to everyone."
        assert doc.variables["version"] == "1.0"

    def test_document_not_frozen(self):
        """TemplateDocument should be mutable (not frozen)."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config)

        # Should be able to modify fields
        doc.abstract = "New abstract"
        assert doc.abstract == "New abstract"

    def test_empty_sections_list(self):
        """Document with empty sections list should be valid."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, sections=[])

        assert doc.sections == []
        assert len(doc.sections) == 0

    def test_empty_authors_list(self):
        """Document with empty authors list should be valid."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, authors=[])

        assert doc.authors == []

    def test_none_bibliography(self):
        """Document without bibliography should be valid."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")

        assert doc.bibliography is None
        assert doc.bibliography_style is None

    def test_must_have_content_or_sections(self):
        """Document without content or sections is allowed (metadata-only)."""
        config = TemplateConfig(template="neurips")

        # Metadata-only documents are allowed (validator will warn)
        doc = TemplateDocument(title="Test", config=config)
        assert doc.content is None
        assert doc.sections is None


class TestDocumentIntegration:
    """Integration tests for document models."""

    def test_document_with_nested_sections(self):
        """Document with nested section hierarchy should work."""
        config = TemplateConfig(template="neurips")

        subsec1 = Section(title="Subsection 1", content="Content 1", level=2)
        subsec2 = Section(title="Subsection 2", content="Content 2", level=2)
        main_section = Section(
            title="Main Section",
            content="Main content",
            level=1,
            subsections=(subsec1, subsec2),
        )

        doc = TemplateDocument(
            title="Hierarchical Document",
            config=config,
            sections=[main_section],
        )

        assert len(doc.sections) == 1
        assert len(doc.sections[0].subsections) == 2
        assert doc.sections[0].subsections[0].title == "Subsection 1"

    def test_document_with_conditional_sections(self):
        """Document with conditional sections should work."""
        config = TemplateConfig(template="neurips")

        sections = [
            Section(title="Introduction", content="Always visible"),
            ConditionalSection(
                title="Appendix",
                content="Conditional content",
                condition="show_appendix",
                default_visible=False,
            ),
        ]

        doc = TemplateDocument(
            title="Test",
            config=config,
            sections=sections,
            variables={"show_appendix": True},
        )

        assert len(doc.sections) == 2
        assert isinstance(doc.sections[1], ConditionalSection)
        assert doc.variables["show_appendix"] is True

    def test_document_with_mixed_content(self):
        """Document with various content types should work."""
        from b8tex.templates.data import DataTable
        import pandas as pd

        config = TemplateConfig(template="neurips")
        authors = [Author(name="Test Author")]

        # Create a simple table
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        table = DataTable(data=df, caption="Test Table")

        sections = [
            Section(title="Introduction", content="Intro text"),
            Section(title="Results", content="See table below."),
        ]

        doc = TemplateDocument(
            title="Mixed Content Document",
            config=config,
            authors=authors,
            abstract="Abstract with data",
            sections=sections,
        )

        assert doc.title == "Mixed Content Document"
        assert len(doc.sections) == 2
        assert doc.abstract is not None

    def test_section_tree_traversal(self):
        """Traversing section tree should work correctly."""
        subsub = Section(title="SubSubSection", level=3, content="Deep content")
        subsec = Section(title="Subsection", level=2, subsections=(subsub,))
        main = Section(title="Main", level=1, subsections=(subsec,))

        # Navigate through the tree
        assert main.title == "Main"
        assert main.subsections[0].title == "Subsection"
        assert main.subsections[0].subsections[0].title == "SubSubSection"
        assert main.subsections[0].subsections[0].content == "Deep content"

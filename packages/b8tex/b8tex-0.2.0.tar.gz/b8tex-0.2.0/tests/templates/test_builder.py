"""Tests for document builder with fluent API."""

from __future__ import annotations

import pytest

from b8tex.templates.builder import DocumentBuilder
from b8tex.templates.config import Author, TemplateConfig
from b8tex.templates.document import Section
from b8tex.templates.escape import Raw


class TestBuilderBasics:
    """Tests for basic builder functionality."""

    def test_create_builder(self):
        """Builder should be created with minimal config."""
        builder = DocumentBuilder(template="neurips", title="Test Paper")
        assert builder.title == "Test Paper"
        assert builder.config.template == "neurips"

    def test_builder_with_all_config_params(self):
        """Builder should accept all configuration parameters."""
        builder = DocumentBuilder(
            template="neurips",
            title="Test",
            status="draft",
            organization="MIT",
            doc_type="Report",
            doc_id="R-001",
        )
        assert builder.config.template == "neurips"
        assert builder.config.status == "draft"
        assert builder.config.metadata.organization == "MIT"

    def test_add_author_string(self):
        """add_author with string should work."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.add_author("John Doe")

        assert len(builder._authors) == 1
        assert builder._authors[0].name == "John Doe"

    def test_add_author_with_affiliation(self):
        """add_author with affiliation should work."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.add_author("Jane Smith", affiliation="Stanford")

        assert builder._authors[0].name == "Jane Smith"
        assert builder._authors[0].affiliation == "Stanford"

    def test_add_author_with_email(self):
        """add_author with email should work."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.add_author("Bob", email="bob@example.com")

        assert builder._authors[0].email == "bob@example.com"

    def test_add_multiple_authors(self):
        """Multiple authors should be added in order."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.add_author("Alice")
        builder.add_author("Bob")
        builder.add_author("Charlie")

        assert len(builder._authors) == 3
        assert builder._authors[0].name == "Alice"
        assert builder._authors[1].name == "Bob"
        assert builder._authors[2].name == "Charlie"

    def test_set_abstract(self):
        """set_abstract should set abstract text."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.set_abstract("This is the abstract.")

        assert builder._abstract == "This is the abstract."

    def test_add_keywords(self):
        """add_keyword should add keywords."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.add_keyword("machine learning")
        builder.add_keyword("neural networks")

        assert len(builder._keywords) == 2
        assert "machine learning" in builder._keywords
        assert "neural networks" in builder._keywords


class TestBuilderSections:
    """Tests for section building."""

    def test_section_context(self):
        """Section context manager should work."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Introduction"):
            builder.add_text("This is the introduction.")

        doc = builder.build()
        assert len(doc.sections) == 1
        assert doc.sections[0].title == "Introduction"
        assert "This is the introduction." in doc.sections[0].content

    def test_multiple_sections(self):
        """Multiple sections should be added in order."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Introduction"):
            builder.add_text("Intro text")

        with builder.section("Methods"):
            builder.add_text("Methods text")

        doc = builder.build()
        assert len(doc.sections) == 2
        assert doc.sections[0].title == "Introduction"
        assert doc.sections[1].title == "Methods"

    def test_subsection(self):
        """Subsection should be nested."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Main"):
            builder.add_text("Main content")
            with builder.subsection("Sub"):
                builder.add_text("Sub content")

        doc = builder.build()
        assert len(doc.sections) == 1
        assert doc.sections[0].title == "Main"
        assert len(doc.sections[0].subsections) == 1
        assert doc.sections[0].subsections[0].title == "Sub"

    def test_subsubsection(self):
        """Subsubsection should be deeply nested."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("L1"):
            with builder.subsection("L2"):
                with builder.subsubsection("L3"):
                    builder.add_text("Deep content")

        doc = builder.build()
        assert doc.sections[0].subsections[0].subsections[0].title == "L3"

    def test_multiple_subsections(self):
        """Multiple subsections should be added to parent."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Main"):
            with builder.subsection("Sub1"):
                builder.add_text("Content 1")
            with builder.subsection("Sub2"):
                builder.add_text("Content 2")

        doc = builder.build()
        assert len(doc.sections[0].subsections) == 2

    def test_unnumbered_section(self):
        """Unnumbered section should work."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Acknowledgments", numbered=False):
            builder.add_text("Thanks!")

        doc = builder.build()
        assert doc.sections[0].numbered is False

    def test_section_with_label(self):
        """Section with label should work."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Introduction", label="sec:intro"):
            builder.add_text("Text")

        doc = builder.build()
        assert doc.sections[0].label == "sec:intro"


class TestBuilderContent:
    """Tests for content addition."""

    def test_add_text_multiple_times(self):
        """Multiple add_text calls should concatenate."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Test"):
            builder.add_text("First paragraph. ")
            builder.add_text("Second paragraph.")

        doc = builder.build()
        content = doc.sections[0].content
        assert "First paragraph." in content
        assert "Second paragraph." in content

    def test_add_paragraph(self):
        """add_paragraph should add paragraph break."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Test"):
            builder.add_paragraph("Para 1")
            builder.add_paragraph("Para 2")

        doc = builder.build()
        content = doc.sections[0].content
        assert "Para 1\n\n" in content  # Paragraph break
        assert "Para 2" in content

    def test_add_raw_latex(self):
        """add_raw_latex should add unescaped content."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Test"):
            builder.add_raw_latex(r"\textbf{Bold} & $math$")

        doc = builder.build()
        content = doc.sections[0].content
        # Content should be Raw and unescaped
        assert r"\textbf{Bold} & $math$" in str(content)

    def test_add_text_escapes_by_default(self):
        """add_text should escape special characters."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Test"):
            builder.add_text("Price: $100")

        doc = builder.build()
        # The text should be marked for escaping (not Raw)
        # Renderer will escape it
        content = doc.sections[0].content
        assert "Price: $100" in content

    def test_mixed_content(self):
        """Mixing text and raw LaTeX should work."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Test"):
            builder.add_text("Plain text ")
            builder.add_raw_latex(r"\textbf{bold} ")
            builder.add_text("more text")

        doc = builder.build()
        content = doc.sections[0].content
        assert "Plain text" in content
        assert r"\textbf{bold}" in content
        assert "more text" in content


class TestBuilderDataFeatures:
    """Tests for data-driven features."""

    def test_add_table_from_dataframe(self):
        """add_table with DataFrame should work."""
        import pandas as pd

        builder = DocumentBuilder(template="neurips", title="Test")
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

        with builder.section("Results"):
            builder.add_table(df, caption="Test Table")

        doc = builder.build()
        # Table should be in section content as LaTeX
        assert doc.sections[0].content is not None

    def test_add_plot_from_figure(self):
        """add_plot with matplotlib figure should work."""
        import matplotlib.pyplot as plt

        builder = DocumentBuilder(template="neurips", title="Test")
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        with builder.section("Results"):
            builder.add_plot(fig, caption="Test Plot")

        plt.close(fig)

        doc = builder.build()
        # Plot should be referenced in content
        assert doc.sections[0].content is not None

    def test_add_figure_from_path(self):
        """add_figure with path should work."""
        from pathlib import Path

        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Results"):
            builder.add_figure(Path("image.png"), caption="Test Figure")

        doc = builder.build()
        content = doc.sections[0].content
        assert "image.png" in content
        assert r"\includegraphics" in content


class TestBuilderContextManager:
    """Tests for builder as context manager."""

    def test_builder_context_manager(self):
        """Builder should work as context manager."""
        with DocumentBuilder(template="neurips", title="Test") as builder:
            builder.add_author("John Doe")
            with builder.section("Introduction"):
                builder.add_text("Text")

        # Should not raise any errors

    def test_context_manager_auto_closes_sections(self):
        """Context manager should auto-close sections on exit."""
        with DocumentBuilder(template="neurips", title="Test") as builder:
            with builder.section("Test"):
                builder.add_text("Content")
            # Section should be automatically closed

        doc = builder.build()
        assert len(doc.sections) == 1

    def test_exception_handling(self):
        """Builder should handle exceptions gracefully."""
        builder = DocumentBuilder(template="neurips", title="Test")

        try:
            with builder.section("Test"):
                builder.add_text("Content")
                raise ValueError("Test error")
        except ValueError:
            pass

        # Builder should still be usable after exception
        doc = builder.build()
        assert len(doc.sections) == 1


class TestBuilderBuild:
    """Tests for building final document."""

    def test_build_returns_template_document(self):
        """build() should return TemplateDocument."""
        from b8tex.templates.document import TemplateDocument

        builder = DocumentBuilder(template="neurips", title="Test")
        doc = builder.build()

        assert isinstance(doc, TemplateDocument)

    def test_build_includes_all_fields(self):
        """build() should include all configured fields."""
        builder = DocumentBuilder(template="neurips", title="Test Paper")
        builder.add_author("Alice")
        builder.set_abstract("Abstract text")
        builder.add_keyword("ml")

        with builder.section("Introduction"):
            builder.add_text("Intro")

        doc = builder.build()

        assert doc.title == "Test Paper"
        assert len(doc.authors) == 1
        assert doc.abstract == "Abstract text"
        assert len(doc.keywords) == 1
        assert len(doc.sections) == 1

    def test_build_creates_config(self):
        """build() should create TemplateConfig."""
        builder = DocumentBuilder(
            template="neurips",
            title="Test",
            status="draft",
            organization="MIT",
        )
        doc = builder.build()

        assert isinstance(doc.config, TemplateConfig)
        assert doc.config.template == "neurips"
        assert doc.config.status == "draft"
        assert doc.config.metadata.organization == "MIT"

    def test_build_multiple_times(self):
        """build() should be callable multiple times."""
        builder = DocumentBuilder(template="neurips", title="Test")

        doc1 = builder.build()
        doc2 = builder.build()

        # Should create new documents each time
        assert doc1 is not doc2
        assert doc1.title == doc2.title


class TestBuilderChaining:
    """Tests for method chaining."""

    def test_method_chaining(self):
        """Methods should return self for chaining."""
        builder = (
            DocumentBuilder(template="neurips", title="Test")
            .add_author("Alice")
            .add_author("Bob")
            .set_abstract("Abstract")
            .add_keyword("ml")
        )

        doc = builder.build()
        assert len(doc.authors) == 2
        assert doc.abstract == "Abstract"

    def test_chaining_with_sections(self):
        """Method chaining should work with sections."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Test"):
            builder.add_text("Text 1").add_text(" Text 2")

        doc = builder.build()
        assert "Text 1" in doc.sections[0].content
        assert "Text 2" in doc.sections[0].content


class TestBuilderEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_add_text_outside_section_raises(self):
        """add_text outside section should raise error."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with pytest.raises(RuntimeError, match="must be called within a section"):
            builder.add_text("Text")

    def test_nested_section_too_deep(self):
        """Deeply nested sections should work (no artificial limit)."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("L1"):
            with builder.subsection("L2"):
                with builder.subsubsection("L3"):
                    # Level 4 uses paragraph by default
                    builder.add_text("Deep")

        doc = builder.build()
        # Should not raise error

    def test_empty_section(self):
        """Empty section should be allowed."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with builder.section("Empty"):
            pass  # No content added

        doc = builder.build()
        assert len(doc.sections) == 1
        assert doc.sections[0].content == ""

    def test_build_without_sections(self):
        """Building without sections should be allowed."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.set_abstract("Abstract")

        doc = builder.build()
        assert doc.abstract == "Abstract"
        assert len(doc.sections) == 0

    def test_add_author_without_name_raises(self):
        """add_author with empty name should raise error."""
        builder = DocumentBuilder(template="neurips", title="Test")

        with pytest.raises(ValueError, match="Author name cannot be empty"):
            builder.add_author("")


class TestBuilderIntegration:
    """Integration tests for builder."""

    def test_complete_document_building(self):
        """Build a complete document with all features."""
        builder = DocumentBuilder(
            template="neurips",
            title="Complete Paper",
            status="draft",
            organization="Research Lab",
        )

        builder.add_author("Alice", affiliation="MIT", email="alice@mit.edu")
        builder.add_author("Bob", affiliation="Stanford")
        builder.set_abstract("This paper presents a novel approach...")
        builder.add_keyword("machine learning")
        builder.add_keyword("optimization")

        with builder.section("Introduction"):
            builder.add_paragraph("First paragraph.")
            builder.add_paragraph("Second paragraph.")

        with builder.section("Methods"):
            builder.add_text("We used the following approach:")
            with builder.subsection("Data Collection"):
                builder.add_text("Data was collected from...")
            with builder.subsection("Analysis"):
                builder.add_text("Analysis was performed using...")

        with builder.section("Results"):
            builder.add_text("The results show...")

        with builder.section("Conclusion"):
            builder.add_text("We conclude that...")

        doc = builder.build()

        assert doc.title == "Complete Paper"
        assert len(doc.authors) == 2
        assert doc.abstract is not None
        assert len(doc.keywords) == 2
        assert len(doc.sections) == 4
        assert len(doc.sections[1].subsections) == 2

    def test_builder_with_template_variables(self):
        """Builder should support template variables."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.set_variable("accuracy", 95.5)

        with builder.section("Results"):
            builder.add_text("Accuracy: {{ accuracy }}%")

        doc = builder.build()
        assert doc.variables["accuracy"] == 95.5

    def test_set_variable(self):
        """set_variable should add template variable."""
        builder = DocumentBuilder(template="neurips", title="Test")
        builder.set_variable("key", "value")

        doc = builder.build()
        assert doc.variables["key"] == "value"

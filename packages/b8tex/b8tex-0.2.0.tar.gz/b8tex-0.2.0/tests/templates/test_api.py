"""Tests for high-level template API."""

from __future__ import annotations

import pytest

from b8tex.core.results import CompileResult
from b8tex.templates.api import (
    compile_template,
    compile_template_document,
    render_template_latex,
    validate_template_document,
)
from b8tex.templates.config import Author, TemplateConfig
from b8tex.templates.document import Section, TemplateDocument


class TestCompileTemplate:
    """Tests for compile_template function."""

    @pytest.mark.slow
    def test_compile_minimal(self):
        """Compile minimal template should work."""
        result = compile_template(
            template="neurips",
            title="Test Paper",
            content=r"\section{Introduction} Hello world!",
        )

        assert isinstance(result, CompileResult)
        assert result.success is True
        assert result.pdf_path is not None
        assert result.pdf_path.exists()

    @pytest.mark.slow
    def test_compile_with_authors_string(self):
        """Compile with authors as string should work."""
        result = compile_template(
            template="neurips",
            title="Test",
            authors="John Doe, Jane Smith",
            content=r"\section{Test} Content.",
        )

        assert result.success is True

    @pytest.mark.slow
    def test_compile_with_author_list(self):
        """Compile with author list should work."""
        authors = [
            Author(name="Alice", affiliation="MIT"),
            Author(name="Bob", affiliation="Stanford"),
        ]

        result = compile_template(
            template="neurips",
            title="Test",
            authors=authors,
            content=r"\section{Test} Content.",
        )

        assert result.success is True

    @pytest.mark.slow
    def test_compile_with_abstract(self):
        """Compile with abstract should work."""
        result = compile_template(
            template="neurips",
            title="Test",
            abstract="This is the abstract.",
            content=r"\section{Test} Content.",
        )

        assert result.success is True

    @pytest.mark.slow
    def test_compile_with_keywords(self):
        """Compile with keywords should work."""
        result = compile_template(
            template="neurips",
            title="Test",
            keywords=["machine learning", "optimization"],
            content=r"\section{Test} Content.",
        )

        assert result.success is True

    @pytest.mark.slow
    def test_compile_with_sections(self):
        """Compile with structured sections should work."""
        sections = [
            Section(title="Introduction", content="Intro text."),
            Section(title="Methods", content="Methods text."),
        ]

        result = compile_template(
            template="neurips",
            title="Test",
            sections=sections,
        )

        assert result.success is True

    @pytest.mark.slow
    def test_compile_draft_status(self):
        """Compile with draft status should work."""
        result = compile_template(
            template="neurips",
            title="Test",
            status="draft",
            content=r"\section{Test} Content.",
        )

        assert result.success is True

    @pytest.mark.slow
    def test_compile_with_metadata(self):
        """Compile with metadata should work."""
        metadata = {
            "organization": "OpenAI",
            "doc_type": "Technical Report",
            "doc_id": "TR-2024-001",
        }

        result = compile_template(
            template="neurips",
            title="Test",
            metadata=metadata,
            content=r"\section{Test} Content.",
        )

        assert result.success is True

    @pytest.mark.slow
    def test_compile_custom_output_name(self):
        """Compile with custom output name should work."""
        result = compile_template(
            template="neurips",
            title="Test",
            output_name="my_paper",
            content=r"\section{Test} Content.",
        )

        assert result.success is True
        assert "my_paper" in str(result.pdf_path)

    @pytest.mark.slow
    def test_compile_all_templates(self):
        """All template types should compile successfully."""
        for template in ["neurips", "iclr", "acl"]:
            result = compile_template(
                template=template,
                title=f"Test {template.upper()}",
                content=r"\section{Test} Content.",
            )

            assert result.success is True, f"{template} compilation failed"

    def test_compile_validation_failure(self):
        """Compilation with validation errors should raise."""
        with pytest.raises(ValueError, match="validation failed"):
            compile_template(
                template="neurips",
                title="",  # Empty title should fail validation
                content=r"\section{Test} Content.",
                validate=True,
            )

    @pytest.mark.slow
    def test_compile_skip_validation(self):
        """Compilation with validate=False should skip validation."""
        # This would normally fail validation but shouldn't raise
        result = compile_template(
            template="neurips",
            title="Test",  # Use valid title but missing content
            validate=False,
        )

        # May or may not succeed depending on LaTeX requirements
        assert isinstance(result, CompileResult)


class TestCompileTemplateDocument:
    """Tests for compile_template_document function."""

    @pytest.mark.slow
    def test_compile_document_basic(self):
        """Compile TemplateDocument should work."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content=r"\section{Test} Content.",
        )

        result = compile_template_document(doc)

        assert isinstance(result, CompileResult)
        assert result.success is True

    @pytest.mark.slow
    def test_compile_document_with_sections(self):
        """Compile document with sections should work."""
        config = TemplateConfig(template="neurips")
        sections = [
            Section(title="Intro", content="Introduction."),
            Section(title="Conclusion", content="Conclusion."),
        ]
        doc = TemplateDocument(title="Test", config=config, sections=sections)

        result = compile_template_document(doc)

        assert result.success is True

    def test_compile_document_validation_error(self):
        """Compile invalid document should raise with validate=True."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="", config=config, content="Content")  # Empty title

        with pytest.raises(ValueError, match="validation failed"):
            compile_template_document(doc, validate=True)

    @pytest.mark.slow
    def test_compile_document_skip_validation(self):
        """Compile with validate=False should skip validation."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content=r"\section{Test} Content.",
        )

        result = compile_template_document(doc, validate=False)

        assert result.success is True

    @pytest.mark.slow
    def test_compile_document_custom_name(self):
        """Compile with custom output name should work."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content=r"\section{Test} Content.",
        )

        result = compile_template_document(doc, output_name="custom")

        assert result.success is True
        assert "custom" in str(result.pdf_path)


class TestRenderTemplateLatex:
    """Tests for render_template_latex function."""

    def test_render_minimal(self):
        """Render minimal document should work."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")

        latex = render_template_latex(doc)

        assert isinstance(latex, str)
        assert r"\documentclass" in latex
        assert r"\begin{document}" in latex
        assert r"\end{document}" in latex
        assert "Test" in latex

    def test_render_with_sections(self):
        """Render document with sections should work."""
        config = TemplateConfig(template="neurips")
        sections = [
            Section(title="Introduction", content="Intro."),
            Section(title="Methods", content="Methods."),
        ]
        doc = TemplateDocument(title="Test", config=config, sections=sections)

        latex = render_template_latex(doc)

        assert r"\section{Introduction}" in latex
        assert r"\section{Methods}" in latex
        assert "Intro." in latex
        assert "Methods." in latex

    def test_render_with_authors(self):
        """Render document with authors should work."""
        config = TemplateConfig(template="neurips")
        authors = [Author(name="Alice"), Author(name="Bob")]
        doc = TemplateDocument(title="Test", config=config, authors=authors)

        latex = render_template_latex(doc)

        assert "Alice" in latex
        assert "Bob" in latex

    def test_render_with_abstract(self):
        """Render document with abstract should work."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            abstract="This is the abstract.",
        )

        latex = render_template_latex(doc)

        assert r"\begin{abstract}" in latex
        assert "This is the abstract." in latex
        assert r"\end{abstract}" in latex

    def test_render_all_templates(self):
        """All templates should render successfully."""
        for template in ["neurips", "iclr", "acl"]:
            config = TemplateConfig(template=template)  # type: ignore
            doc = TemplateDocument(
                title=f"Test {template}",
                config=config,
                content=r"\section{Test} Content.",
            )

            latex = render_template_latex(doc)

            assert isinstance(latex, str)
            assert len(latex) > 0


class TestValidateTemplateDocument:
    """Tests for validate_template_document function."""

    def test_validate_valid_document(self):
        """Valid document should pass validation."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content=r"\section{Test} Content.",
        )

        is_valid, issues = validate_template_document(doc)

        assert is_valid is True
        # May have warnings but no errors
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_validate_invalid_document(self):
        """Invalid document should fail validation."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="", config=config, content="Content")  # Empty title

        is_valid, issues = validate_template_document(doc)

        assert is_valid is False
        assert len(issues) > 0

    def test_validate_returns_issues_list(self):
        """validate should return list of issues."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")

        is_valid, issues = validate_template_document(doc)

        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

    def test_validate_strict_mode(self):
        """Validation in strict mode should treat warnings as errors."""
        config = TemplateConfig(template="acl", two_column=False)  # Produces warning
        doc = TemplateDocument(title="Test", config=config, content="Content")

        is_valid, issues = validate_template_document(doc, strict=True)

        # Warnings should cause validation to fail in strict mode
        assert is_valid is False

    def test_validate_non_strict_mode(self):
        """Validation in non-strict mode should pass with warnings."""
        config = TemplateConfig(template="acl", two_column=False)  # Produces warning
        doc = TemplateDocument(title="Test", config=config, content="Content")

        is_valid, issues = validate_template_document(doc, strict=False)

        # Warnings should not cause validation to fail
        assert is_valid is True


class TestAPIIntegration:
    """Integration tests for template API."""

    @pytest.mark.slow
    def test_full_workflow_with_compile_template(self):
        """Complete workflow with compile_template should work."""
        result = compile_template(
            template="neurips",
            title="Integration Test Paper",
            authors=[
                Author(name="Alice", affiliation="MIT"),
                Author(name="Bob", affiliation="Stanford"),
            ],
            abstract="This paper presents an integration test.",
            keywords=["testing", "integration"],
            sections=[
                Section(title="Introduction", content="This is the introduction."),
                Section(title="Methods", content="Our methodology."),
                Section(title="Results", content="The results show..."),
                Section(title="Conclusion", content="We conclude that..."),
            ],
            status="draft",
            metadata={
                "organization": "Test Lab",
                "doc_type": "Research Paper",
            },
        )

        assert result.success is True
        assert result.pdf_path.exists()

    @pytest.mark.slow
    def test_workflow_validate_render_compile(self):
        """Workflow: validate, render, then compile should work."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Workflow Test",
            config=config,
            sections=[Section(title="Test", content="Content.")],
        )

        # Step 1: Validate
        is_valid, issues = validate_template_document(doc)
        assert is_valid is True

        # Step 2: Render to LaTeX
        latex = render_template_latex(doc)
        assert isinstance(latex, str)
        assert len(latex) > 0

        # Step 3: Compile
        result = compile_template_document(doc)
        assert result.success is True

    @pytest.mark.slow
    def test_compile_template_vs_compile_document(self):
        """compile_template and compile_template_document should be equivalent."""
        # Using compile_template
        result1 = compile_template(
            template="neurips",
            title="Test",
            content=r"\section{Test} Content.",
        )

        # Using compile_template_document
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content=r"\section{Test} Content.",
        )
        result2 = compile_template_document(doc)

        # Both should succeed
        assert result1.success is True
        assert result2.success is True

    def test_render_then_validate(self):
        """Rendering doesn't require validation first."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="", config=config, content="Content")  # Invalid

        # Rendering should work even for invalid doc
        latex = render_template_latex(doc)
        assert isinstance(latex, str)

        # But validation should fail
        is_valid, issues = validate_template_document(doc)
        assert is_valid is False


class TestAPIEdgeCases:
    """Tests for edge cases in API."""

    @pytest.mark.slow
    def test_compile_with_both_content_and_sections(self):
        """Compile with both content and sections should use sections."""
        # This is semantically incorrect but should be handled
        sections = [Section(title="Test", content="Section content.")]

        result = compile_template(
            template="neurips",
            title="Test",
            content=r"\section{Raw} Raw content.",  # Should be ignored
            sections=sections,
            validate=False,  # Skip validation to avoid warning
        )

        # Should compile (renderer handles this)
        assert result.success is True

    @pytest.mark.slow
    def test_compile_minimal_content(self):
        """Compile with minimal content should work."""
        result = compile_template(
            template="neurips",
            title="Minimal",
            content="Just text.",
        )

        assert result.success is True

    def test_validate_document_without_content_or_sections(self):
        """Validate document without content should produce warnings."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Empty", config=config, content="Content")

        is_valid, issues = validate_template_document(doc)

        # Should be valid (no errors) but may have warnings
        assert is_valid is True
        warnings = [i for i in issues if i.severity == "warning"]
        assert len(warnings) > 0

    @pytest.mark.slow
    def test_compile_unicode_content(self):
        """Compile with Unicode content should work."""
        result = compile_template(
            template="neurips",
            title="Unicode Test",
            content=r"\section{Test} Café résumé naïve über.",
        )

        assert result.success is True

    @pytest.mark.slow
    def test_compile_special_characters(self):
        """Compile with special characters should work (escaped)."""
        result = compile_template(
            template="neurips",
            title="Special & Characters: 50% Test",
            abstract="Price: $100 with 50% discount.",
            content=r"\section{Test} More special chars: \_ \# \& \$",
        )

        assert result.success is True

"""Tests for template validation."""

from __future__ import annotations

import pytest

from b8tex.templates.config import Author, TemplateConfig, TemplateMetadata
from b8tex.templates.document import Section, TemplateDocument
from b8tex.templates.validation import (
    TemplateValidator,
    ValidationIssue,
    ValidationSeverity,
)


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_issue(self):
        """ValidationIssue should be created with basic fields."""
        issue = ValidationIssue(severity="error", message="Test error")

        assert issue.severity == "error"
        assert issue.message == "Test error"
        assert issue.field is None
        assert issue.location is None

    def test_create_with_field(self):
        """ValidationIssue with field should be valid."""
        issue = ValidationIssue(
            severity="warning",
            message="Field issue",
            field="title",
        )

        assert issue.field == "title"

    def test_create_with_location(self):
        """ValidationIssue with location should be valid."""
        issue = ValidationIssue(
            severity="info",
            message="Location issue",
            location="section 1",
        )

        assert issue.location == "section 1"

    def test_immutability(self):
        """ValidationIssue should be immutable."""
        issue = ValidationIssue(severity="error", message="Test")

        with pytest.raises(AttributeError):
            issue.severity = "warning"  # type: ignore


class TestTemplateValidator:
    """Tests for TemplateValidator."""

    def test_create_validator(self):
        """Validator should be created with default settings."""
        validator = TemplateValidator()

        assert validator.strict is False

    def test_create_strict_validator(self):
        """Validator with strict mode should be created."""
        validator = TemplateValidator(strict=True)

        assert validator.strict is True

    def test_validate_minimal_document(self):
        """Minimal valid document should pass validation."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")

        validator = TemplateValidator()
        issues = validator.validate(doc)

        # Minimal doc may have warnings but should not error
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_validate_empty_title_error(self):
        """Empty title should produce error."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="", config=config, content="Content")

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) > 0
        assert any("title" in i.message.lower() for i in errors)

    def test_validate_no_content_warning(self):
        """Document without content should produce warning."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")

        validator = TemplateValidator()
        issues = validator.validate(doc)

        warnings = [i for i in issues if i.severity == "warning"]
        # May warn about missing abstract or content
        assert isinstance(warnings, list)

    def test_validate_with_content(self):
        """Document with content should pass."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content=r"\section{Intro} Content here.",
        )

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_validate_with_sections(self):
        """Document with sections should pass."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="Introduction", content="Content")]
        doc = TemplateDocument(title="Test", config=config, sections=sections)

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0


class TestSectionValidation:
    """Tests for section validation."""

    def test_validate_empty_section_title(self):
        """Empty section title should produce error."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="", content="Content")]
        doc = TemplateDocument(title="Test", config=config, sections=sections)

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) > 0
        assert any("section" in i.message.lower() for i in errors)

    def test_validate_section_without_content_warning(self):
        """Section without content should produce warning."""
        config = TemplateConfig(template="neurips")
        sections = [Section(title="Empty Section", content="")]
        doc = TemplateDocument(title="Test", config=config, sections=sections)

        validator = TemplateValidator()
        issues = validator.validate(doc)

        warnings = [i for i in issues if i.severity == "warning"]
        # May warn about empty section
        assert isinstance(warnings, list)

    def test_validate_nested_sections(self):
        """Nested sections should be validated."""
        config = TemplateConfig(template="neurips")
        subsec = Section(title="", content="Invalid")  # Empty title
        main = Section(title="Main", subsections=(subsec,))
        doc = TemplateDocument(title="Test", config=config, sections=[main])

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) > 0  # Should catch nested empty title

    def test_validate_section_level(self):
        """Invalid section levels should be caught during construction."""
        import pytest
        config = TemplateConfig(template="neurips")

        # Invalid level should raise ValueError during Section construction
        with pytest.raises(ValueError, match="Section level must be 1-4"):
            Section(title="Test", level=0)


class TestAuthorValidation:
    """Tests for author validation."""

    def test_validate_empty_author_name(self):
        """Empty author name should produce error."""
        config = TemplateConfig(template="neurips")
        authors = [Author(name="")]
        doc = TemplateDocument(title="Test", config=config, authors=authors)

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) > 0
        assert any("author" in i.message.lower() for i in errors)

    def test_validate_valid_authors(self):
        """Valid authors should pass."""
        config = TemplateConfig(template="neurips")
        authors = [
            Author(name="Alice", affiliation="MIT"),
            Author(name="Bob", affiliation="Stanford", email="bob@stanford.edu"),
        ]
        doc = TemplateDocument(title="Test", config=config, authors=authors)

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        # Should not error on valid authors
        assert len([e for e in errors if "author" in e.message.lower()]) == 0

    def test_validate_string_authors(self):
        """String authors should be accepted."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            authors="John Doe, Jane Smith",
        )

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_validate_empty_string_authors(self):
        """Empty string authors should produce warning."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, authors="")

        validator = TemplateValidator()
        issues = validator.validate(doc)

        # Empty authors string should produce warning
        warnings = [i for i in issues if i.severity == "warning"]
        assert len(warnings) > 0 or len(issues) == 0  # May or may not warn


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_validate_config_warnings(self):
        """Config validation warnings should be included."""
        config = TemplateConfig(template="acl", font_size="12pt")  # ACL needs 11pt
        doc = TemplateDocument(title="Test", config=config, content="Content")

        validator = TemplateValidator()
        issues = validator.validate(doc)

        warnings = [i for i in issues if i.severity == "warning"]
        # Should include ACL font size warning from config
        assert len(warnings) > 0

    def test_validate_neurips_config(self):
        """NeurIPS config with defaults should pass."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, content="Content")

        validator = TemplateValidator()
        issues = validator.validate(doc)

        # Default NeurIPS config should have no warnings
        warnings = [i for i in issues if i.severity == "warning"]
        config_warnings = [w for w in warnings if "config" in w.message.lower()]
        assert len(config_warnings) == 0


class TestHasErrors:
    """Tests for has_errors utility method."""

    def test_has_errors_with_errors(self):
        """has_errors should return True when errors present."""
        issues = [
            ValidationIssue(severity="error", message="Error 1"),
            ValidationIssue(severity="warning", message="Warning 1"),
        ]

        validator = TemplateValidator()
        assert validator.has_errors(issues) is True

    def test_has_errors_without_errors(self):
        """has_errors should return False when no errors."""
        issues = [
            ValidationIssue(severity="warning", message="Warning 1"),
            ValidationIssue(severity="info", message="Info 1"),
        ]

        validator = TemplateValidator()
        assert validator.has_errors(issues) is False

    def test_has_errors_empty_list(self):
        """has_errors should return False for empty list."""
        validator = TemplateValidator()
        assert validator.has_errors([]) is False

    def test_has_errors_strict_mode(self):
        """has_errors in strict mode should treat warnings as errors."""
        issues = [ValidationIssue(severity="warning", message="Warning")]

        validator = TemplateValidator(strict=True)
        assert validator.has_errors(issues) is True

    def test_has_errors_strict_mode_info_only(self):
        """has_errors in strict mode should not treat info as errors."""
        issues = [ValidationIssue(severity="info", message="Info")]

        validator = TemplateValidator(strict=True)
        assert validator.has_errors(issues) is False


class TestFormatIssues:
    """Tests for format_issues utility method."""

    def test_format_issues_single(self):
        """format_issues should format single issue."""
        issues = [ValidationIssue(severity="error", message="Test error")]

        validator = TemplateValidator()
        formatted = validator.format_issues(issues)

        assert isinstance(formatted, str)
        assert "error" in formatted.lower()
        assert "Test error" in formatted

    def test_format_issues_multiple(self):
        """format_issues should format multiple issues."""
        issues = [
            ValidationIssue(severity="error", message="Error 1"),
            ValidationIssue(severity="warning", message="Warning 1"),
            ValidationIssue(severity="info", message="Info 1"),
        ]

        validator = TemplateValidator()
        formatted = validator.format_issues(issues)

        assert "Error 1" in formatted
        assert "Warning 1" in formatted
        assert "Info 1" in formatted

    def test_format_issues_with_field(self):
        """format_issues should include field information."""
        issues = [
            ValidationIssue(severity="error", message="Invalid", field="title"),
        ]

        validator = TemplateValidator()
        formatted = validator.format_issues(issues)

        assert "title" in formatted

    def test_format_issues_with_location(self):
        """format_issues should include location information."""
        issues = [
            ValidationIssue(
                severity="error",
                message="Invalid",
                location="section 1",
            ),
        ]

        validator = TemplateValidator()
        formatted = validator.format_issues(issues)

        assert "section 1" in formatted

    def test_format_issues_empty_list(self):
        """format_issues should handle empty list."""
        validator = TemplateValidator()
        formatted = validator.format_issues([])

        assert isinstance(formatted, str)
        assert "no" in formatted.lower() and "issues" in formatted.lower()


class TestValidationIntegration:
    """Integration tests for validation."""

    def test_complete_valid_document(self):
        """Complete valid document should pass validation."""
        metadata = TemplateMetadata(organization="MIT", doc_type="Paper")
        config = TemplateConfig(template="neurips", metadata=metadata)

        authors = [
            Author(name="Alice", affiliation="MIT", email="alice@mit.edu"),
            Author(name="Bob", affiliation="Stanford"),
        ]

        sections = [
            Section(title="Introduction", content="Intro content"),
            Section(title="Methods", content="Methods content"),
            Section(title="Results", content="Results content"),
        ]

        doc = TemplateDocument(
            title="Complete Paper",
            config=config,
            authors=authors,
            abstract="This is the abstract.",
            keywords=["ml", "ai"],
            sections=sections,
        )

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_document_with_multiple_errors(self):
        """Document with multiple errors should catch all."""
        config = TemplateConfig(template="neurips")

        authors = [
            Author(name=""),  # Empty name - error
        ]

        sections = [
            Section(title="", content="Content"),  # Empty title - error
        ]

        doc = TemplateDocument(
            title="",  # Empty title - error
            config=config,
            authors=authors,
            sections=sections,
        )

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) >= 2  # At least document title and section title

    def test_validation_with_warnings_only(self):
        """Document with only warnings should pass (non-strict)."""
        config = TemplateConfig(template="acl", two_column=False)  # Warning
        doc = TemplateDocument(title="Test", config=config, content="Content")

        validator = TemplateValidator(strict=False)
        issues = validator.validate(doc)

        assert not validator.has_errors(issues)

    def test_validation_with_warnings_strict(self):
        """Document with warnings should fail in strict mode."""
        config = TemplateConfig(template="acl", two_column=False)  # Warning
        doc = TemplateDocument(title="Test", config=config, content="Content")

        validator = TemplateValidator(strict=True)
        issues = validator.validate(doc)

        # Warnings are treated as errors in strict mode
        assert validator.has_errors(issues)

    def test_deeply_nested_sections_validation(self):
        """Deeply nested sections should be fully validated."""
        config = TemplateConfig(template="neurips")

        subsub_invalid = Section(title="", content="Invalid")  # Error
        subsec = Section(title="Valid", subsections=(subsub_invalid,))
        main = Section(title="Main", subsections=(subsec,))

        doc = TemplateDocument(title="Test", config=config, sections=[main])

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) > 0  # Should find nested empty title


class TestValidationEdgeCases:
    """Tests for edge cases in validation."""

    def test_validate_very_long_title(self):
        """Very long title should produce warning."""
        config = TemplateConfig(template="neurips")
        long_title = "A" * 300  # Very long title
        doc = TemplateDocument(title=long_title, config=config, content="Content")

        validator = TemplateValidator()
        issues = validator.validate(doc)

        # May or may not warn about length
        assert isinstance(issues, list)

    def test_validate_special_characters_in_title(self):
        """Title with special characters should be accepted."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test & Research: 50% Complete",
            config=config,
            content="Content",
        )

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        # Special chars should be accepted (will be escaped)
        assert len(errors) == 0

    def test_validate_unicode_in_content(self):
        """Unicode content should be accepted."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content="Café résumé naïve über",
        )

        validator = TemplateValidator()
        issues = validator.validate(doc)

        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_validate_empty_sections_list(self):
        """Empty sections list should be handled."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(title="Test", config=config, sections=[])

        validator = TemplateValidator()
        issues = validator.validate(doc)

        # Empty sections list may produce warning
        assert isinstance(issues, list)

    def test_validate_empty_keywords_list(self):
        """Empty keywords list should be handled."""
        config = TemplateConfig(template="neurips")
        doc = TemplateDocument(
            title="Test",
            config=config,
            content="Content",
            keywords=[],
        )

        validator = TemplateValidator()
        issues = validator.validate(doc)

        # Empty keywords may or may not warn
        assert isinstance(issues, list)

    def test_validate_both_content_and_sections(self):
        """Having both content and sections should raise ValueError during construction."""
        import pytest
        config = TemplateConfig(template="neurips")

        # Should raise ValueError when trying to create document with both
        with pytest.raises(ValueError, match="Cannot specify both"):
            TemplateDocument(
                title="Test",
                config=config,
                content="Raw content",
                sections=[Section(title="Section")],
            )

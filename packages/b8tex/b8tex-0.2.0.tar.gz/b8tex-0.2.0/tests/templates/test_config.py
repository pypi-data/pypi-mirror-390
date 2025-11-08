"""Tests for template configuration system."""

from __future__ import annotations

import pytest

from b8tex.templates.config import (
    Author,
    StatusMode,
    TemplateConfig,
    TemplateMetadata,
    TemplateType,
)


class TestTemplateMetadata:
    """Tests for TemplateMetadata dataclass."""

    def test_create_empty(self):
        """Empty metadata should be valid."""
        metadata = TemplateMetadata()
        assert metadata.organization is None
        assert metadata.doc_type is None
        assert metadata.doc_id is None

    def test_create_with_all_fields(self):
        """Metadata with all fields should be valid."""
        metadata = TemplateMetadata(
            organization="OpenAI",
            doc_type="Technical Report",
            doc_id="TR-2024-001",
        )
        assert metadata.organization == "OpenAI"
        assert metadata.doc_type == "Technical Report"
        assert metadata.doc_id == "TR-2024-001"

    def test_create_with_partial_fields(self):
        """Metadata with some fields should be valid."""
        metadata = TemplateMetadata(organization="Anthropic")
        assert metadata.organization == "Anthropic"
        assert metadata.doc_type is None
        assert metadata.doc_id is None

    def test_immutability(self):
        """TemplateMetadata should be immutable."""
        metadata = TemplateMetadata(organization="Test")
        with pytest.raises(AttributeError):
            metadata.organization = "Changed"  # type: ignore

    def test_equality(self):
        """TemplateMetadata instances should support equality."""
        meta1 = TemplateMetadata(organization="Test", doc_type="Report")
        meta2 = TemplateMetadata(organization="Test", doc_type="Report")
        meta3 = TemplateMetadata(organization="Test", doc_type="Paper")

        assert meta1 == meta2
        assert meta1 != meta3


class TestAuthor:
    """Tests for Author dataclass."""

    def test_create_minimal(self):
        """Author with just name should be valid."""
        author = Author(name="John Doe")
        assert author.name == "John Doe"
        assert author.affiliation is None
        assert author.email is None

    def test_create_with_affiliation(self):
        """Author with affiliation should be valid."""
        author = Author(name="Jane Smith", affiliation="MIT")
        assert author.name == "Jane Smith"
        assert author.affiliation == "MIT"
        assert author.email is None

    def test_create_with_email(self):
        """Author with email should be valid."""
        author = Author(name="Bob Johnson", email="bob@example.com")
        assert author.name == "Bob Johnson"
        assert author.email == "bob@example.com"
        assert author.affiliation is None

    def test_create_full(self):
        """Author with all fields should be valid."""
        author = Author(
            name="Alice Brown",
            affiliation="Stanford University",
            email="alice@stanford.edu",
        )
        assert author.name == "Alice Brown"
        assert author.affiliation == "Stanford University"
        assert author.email == "alice@stanford.edu"

    def test_immutability(self):
        """Author should be immutable."""
        author = Author(name="Test")
        with pytest.raises(AttributeError):
            author.name = "Changed"  # type: ignore

    def test_equality(self):
        """Author instances should support equality."""
        author1 = Author(name="John", affiliation="MIT")
        author2 = Author(name="John", affiliation="MIT")
        author3 = Author(name="Jane", affiliation="MIT")

        assert author1 == author2
        assert author1 != author3


class TestTemplateConfig:
    """Tests for TemplateConfig dataclass."""

    def test_create_minimal(self):
        """Config with just template should use defaults."""
        config = TemplateConfig(template="neurips")
        assert config.template == "neurips"
        assert config.status == "final"
        assert config.review_mode is False
        assert config.metadata is None

    def test_create_with_status(self):
        """Config with status should be valid."""
        config = TemplateConfig(template="iclr", status="draft")
        assert config.template == "iclr"
        assert config.status == "draft"

    def test_all_template_types(self):
        """All template types should be valid."""
        for template in ["neurips", "iclr", "acl"]:
            config = TemplateConfig(template=template)  # type: ignore
            assert config.template == template

    def test_all_status_modes(self):
        """All status modes should be valid."""
        for status in ["final", "confidential", "internal", "draft"]:
            config = TemplateConfig(template="neurips", status=status)  # type: ignore
            assert config.status == status

    def test_with_metadata(self):
        """Config with metadata should be valid."""
        metadata = TemplateMetadata(organization="OpenAI")
        config = TemplateConfig(template="neurips", metadata=metadata)
        assert config.metadata == metadata
        assert config.metadata.organization == "OpenAI"

    def test_review_mode(self):
        """Review mode should be configurable."""
        config = TemplateConfig(template="neurips", review_mode=True)
        assert config.review_mode is True

    def test_font_size(self):
        """Font size should be configurable."""
        config = TemplateConfig(template="acl", font_size="11pt")
        assert config.font_size == "11pt"

    def test_line_numbers(self):
        """Line numbers should be configurable."""
        config = TemplateConfig(template="acl", line_numbers=True)
        assert config.line_numbers is True

    def test_two_column(self):
        """Two column mode should be configurable."""
        config = TemplateConfig(template="neurips", two_column=False)
        assert config.two_column is False

    def test_hyperref_enabled(self):
        """Hyperref should be configurable."""
        config = TemplateConfig(template="neurips", hyperref=False)
        assert config.hyperref is False

    def test_custom_document_class_options(self):
        """Custom document class options should be accepted."""
        config = TemplateConfig(
            template="neurips",
            custom_doc_class_options=["letterpaper", "onecolumn"],
        )
        assert "letterpaper" in config.custom_doc_class_options
        assert "onecolumn" in config.custom_doc_class_options

    def test_custom_packages(self):
        """Custom packages should be accepted."""
        config = TemplateConfig(
            template="neurips",
            custom_packages=[("graphicx", None), ("amsmath", "fleqn")],
        )
        assert len(config.custom_packages) == 2
        assert config.custom_packages[0] == ("graphicx", None)
        assert config.custom_packages[1] == ("amsmath", "fleqn")

    def test_custom_commands(self):
        """Custom commands should be accepted."""
        commands = {
            "RR": r"\mathbb{R}",
            "NN": r"\mathbb{N}",
        }
        config = TemplateConfig(template="neurips", custom_commands=commands)
        assert config.custom_commands == commands

    def test_immutability(self):
        """TemplateConfig should be immutable."""
        config = TemplateConfig(template="neurips")
        with pytest.raises(AttributeError):
            config.status = "draft"  # type: ignore

    def test_validate_empty_config(self):
        """Empty config should have no warnings."""
        config = TemplateConfig(template="neurips")
        warnings = config.validate()
        assert isinstance(warnings, list)
        assert len(warnings) == 0

    def test_validate_acl_font_size_warning(self):
        """ACL with non-11pt font should warn."""
        config = TemplateConfig(template="acl", font_size="12pt")
        warnings = config.validate()
        assert len(warnings) > 0
        assert any("ACL" in w and "11pt" in w for w in warnings)

    def test_validate_acl_two_column_warning(self):
        """ACL with single column should warn."""
        config = TemplateConfig(template="acl", two_column=False)
        warnings = config.validate()
        assert len(warnings) > 0
        assert any("ACL" in w and "two-column" in w for w in warnings)

    def test_validate_neurips_no_warnings(self):
        """NeurIPS with default settings should have no warnings."""
        config = TemplateConfig(template="neurips")
        warnings = config.validate()
        assert len(warnings) == 0

    def test_validate_iclr_no_warnings(self):
        """ICLR with default settings should have no warnings."""
        config = TemplateConfig(template="iclr")
        warnings = config.validate()
        assert len(warnings) == 0

    def test_validate_multiple_warnings(self):
        """Config with multiple issues should return multiple warnings."""
        config = TemplateConfig(
            template="acl",
            font_size="12pt",
            two_column=False,
        )
        warnings = config.validate()
        assert len(warnings) >= 2

    def test_equality(self):
        """TemplateConfig instances should support equality."""
        config1 = TemplateConfig(template="neurips", status="draft")
        config2 = TemplateConfig(template="neurips", status="draft")
        config3 = TemplateConfig(template="neurips", status="final")

        assert config1 == config2
        assert config1 != config3

    def test_repr(self):
        """Config should have useful repr."""
        config = TemplateConfig(template="neurips", status="draft")
        repr_str = repr(config)
        assert "TemplateConfig" in repr_str
        assert "neurips" in repr_str
        assert "draft" in repr_str


class TestConfigIntegration:
    """Integration tests for configuration system."""

    def test_full_configuration(self):
        """Complete configuration should work together."""
        metadata = TemplateMetadata(
            organization="Research Lab",
            doc_type="Technical Report",
            doc_id="TR-2024-001",
        )

        config = TemplateConfig(
            template="neurips",
            status="confidential",
            review_mode=False,
            metadata=metadata,
            font_size="10pt",
            line_numbers=False,
            two_column=True,
            hyperref=True,
            custom_doc_class_options=["letterpaper"],
            custom_packages=[("amsmath", None), ("algorithm2e", None)],
            custom_commands={"RR": r"\mathbb{R}"},
        )

        assert config.template == "neurips"
        assert config.status == "confidential"
        assert config.metadata.organization == "Research Lab"
        assert config.custom_commands["RR"] == r"\mathbb{R}"
        assert len(config.custom_packages) == 2

    def test_author_list(self):
        """List of authors should work correctly."""
        authors = [
            Author(name="Alice", affiliation="MIT"),
            Author(name="Bob", affiliation="Stanford", email="bob@stanford.edu"),
            Author(name="Charlie"),
        ]

        assert len(authors) == 3
        assert authors[0].name == "Alice"
        assert authors[1].email == "bob@stanford.edu"
        assert authors[2].affiliation is None

    def test_config_validation_comprehensive(self):
        """Comprehensive validation test."""
        # Valid configs should pass
        valid_configs = [
            TemplateConfig(template="neurips"),
            TemplateConfig(template="iclr", status="draft"),
            TemplateConfig(template="acl", font_size="11pt", two_column=True),
        ]

        for config in valid_configs:
            warnings = config.validate()
            assert isinstance(warnings, list)

    def test_template_type_literal(self):
        """Template type should be a Literal for type checking."""
        # This is primarily a type-checking test
        # Runtime behavior should accept valid template names
        config = TemplateConfig(template="neurips")
        assert config.template in ["neurips", "iclr", "acl"]

    def test_status_mode_literal(self):
        """Status mode should be a Literal for type checking."""
        config = TemplateConfig(template="neurips", status="draft")
        assert config.status in ["final", "confidential", "internal", "draft"]

"""Configuration dataclasses for template system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


TemplateType = Literal["neurips", "iclr", "acl"]
StatusMode = Literal["final", "confidential", "internal", "draft"]


@dataclass(frozen=True, slots=True)
class TemplateMetadata:
    """Template-specific metadata.

    Maps to LaTeX commands:
    - organization → \\setorganization{}
    - doc_type → \\setdoctype{}
    - doc_id → \\setdocid{}
    """

    organization: str | None = None
    doc_type: str | None = None
    doc_id: str | None = None


@dataclass(frozen=True, slots=True)
class Author:
    """Author information for a document.

    Attributes:
        name: Author's full name
        affiliation: Institution or organization
        email: Contact email address
    """

    name: str
    affiliation: str | None = None
    email: str | None = None


@dataclass(frozen=True)
class TemplateConfig:
    """Configuration for template-based document generation.

    This defines HOW the template should be applied. Combines style options,
    layout preferences, and metadata.

    Attributes:
        template: Which template to use (neurips, iclr, acl)
        status: Document status mode
        review_mode: Enable review mode (line numbers, etc.)
        metadata: Template metadata (organization, doc_type, doc_id)
        line_numbers: Override line number display (None = auto from status)
        columns: Override column count (None = template default)
        two_column: Alias for columns (True = 2 columns, False = 1 column)
        font_size: Override font size (None = template default)
        hyperref: Enable hyperref package (default: True)
        custom_doc_class_options: Additional documentclass options
        custom_packages: List of (package_name, options) tuples to include
        custom_commands: Dictionary of custom LaTeX commands
        template_options: Template-specific options dictionary
    """

    template: TemplateType
    status: StatusMode = "final"
    review_mode: bool = False
    metadata: TemplateMetadata | None = None
    line_numbers: bool | None = None
    columns: Literal[1, 2] | None = None
    two_column: bool | None = None
    font_size: Literal["10pt", "11pt", "12pt"] | None = None
    hyperref: bool = True
    custom_doc_class_options: list[str] = field(default_factory=list)
    custom_packages: list[tuple[str, str | None]] = field(default_factory=list)
    custom_commands: dict[str, str] = field(default_factory=dict)
    template_options: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        """Validate configuration and return list of warnings.

        Returns:
            List of warning messages (empty if valid)
        """
        warnings: list[str] = []

        # ACL requires 11pt
        if self.template == "acl":
            if self.font_size and self.font_size != "11pt":
                warnings.append(
                    f"ACL template requires 11pt font, got {self.font_size}. "
                    "Font size will be forced to 11pt."
                )

            # ACL is always 2-column
            if self.columns == 1 or self.two_column is False:
                warnings.append(
                    "ACL template is always 2-column. Column setting will be ignored."
                )

        # Validate template-specific options
        if self.template == "acl":
            if "metadata_placement" in self.template_options:
                placement = self.template_options["metadata_placement"]
                if placement not in ("auto", "manual"):
                    warnings.append(
                        f"Invalid ACL metadata_placement: {placement}. "
                        "Expected 'auto' or 'manual'."
                    )

        return warnings

    def get_document_class_options(self) -> list[str]:
        """Get document class options for this configuration.

        Returns:
            List of options for \\documentclass[]{}
        """
        options: list[str] = []

        # Font size
        if self.font_size:
            # ACL always gets 11pt
            if self.template == "acl":
                options.append("11pt")
            else:
                options.append(self.font_size)
        elif self.template == "acl":
            # ACL requires 11pt even if not specified
            options.append("11pt")

        # Column layout (handle both columns and two_column)
        column_count = self.columns
        if column_count is None and self.two_column is not None:
            column_count = 2 if self.two_column else 1

        if column_count == 1:
            options.append("onecolumn")
        elif column_count == 2:
            options.append("twocolumn")

        # Custom document class options
        options.extend(self.custom_doc_class_options)

        return options

    def get_style_options(self) -> list[str]:
        """Get style package options for this configuration.

        Returns:
            List of options for \\usepackage[]{}
        """
        options: list[str] = [self.status]

        if self.review_mode:
            options.append("review")

        return options

"""Validation for template documents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from b8tex.templates.document import Section, TemplateDocument


ValidationSeverity = Literal["error", "warning", "info"]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A validation issue found in a template document.

    Attributes:
        severity: Issue severity (error, warning, info)
        message: Description of the issue
        field: Field name where issue was found (if applicable)
        location: Additional location information
    """

    severity: ValidationSeverity
    message: str
    field: str | None = None
    location: str | None = None

    def __str__(self) -> str:
        """Format issue as string."""
        parts = [self.severity.upper()]

        if self.field:
            parts.append(f"[{self.field}]")

        parts.append(self.message)

        if self.location:
            parts.append(f"({self.location})")

        return " ".join(parts)


class TemplateValidator:
    """Validates template documents before rendering.

    Checks for common issues, missing required fields, and
    template-specific requirements.
    """

    def __init__(self, strict: bool = False):
        """Initialize validator.

        Args:
            strict: If True, treat warnings as errors
        """
        self.strict = strict

    def validate(self, doc: TemplateDocument) -> list[ValidationIssue]:
        """Validate a template document.

        Args:
            doc: Document to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues: list[ValidationIssue] = []

        # Validate required fields
        issues.extend(self._validate_required_fields(doc))

        # Validate configuration
        issues.extend(self._validate_config(doc))

        # Validate authors
        if doc.authors:
            issues.extend(self._validate_authors(doc.authors))

        # Validate content
        if doc.sections:
            issues.extend(self._validate_sections(doc.sections))

        # Validate content length
        issues.extend(self._validate_lengths(doc))

        # Template-specific validation
        issues.extend(self._validate_template_specific(doc))

        return issues

    def _validate_required_fields(self, doc: TemplateDocument) -> list[ValidationIssue]:
        """Check required fields are present."""
        issues: list[ValidationIssue] = []

        if not doc.title or not doc.title.strip():
            issues.append(
                ValidationIssue(
                    severity="error",
                    message="Document title is required",
                    field="title",
                )
            )

        if doc.content is None and doc.sections is None:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message="Document has no content or sections",
                    field="content/sections",
                )
            )

        # Warn if both content and sections are provided
        if doc.content is not None and doc.sections is not None:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message="Document has both content and sections. Sections will be ignored during rendering.",
                    field="content/sections",
                )
            )

        return issues

    def _validate_config(self, doc: TemplateDocument) -> list[ValidationIssue]:
        """Validate template configuration."""
        issues: list[ValidationIssue] = []

        # Get config warnings
        config_warnings = doc.config.validate()
        for warning in config_warnings:
            severity = "error" if self.strict else "warning"
            issues.append(
                ValidationIssue(
                    severity=severity,
                    message=warning,
                    field="config",
                )
            )

        return issues

    def _validate_authors(self, authors: list | str) -> list[ValidationIssue]:
        """Validate author information."""
        issues: list[ValidationIssue] = []

        # Handle string authors
        if isinstance(authors, str):
            if not authors.strip():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message="Authors string cannot be empty",
                        field="authors",
                    )
                )
            return issues

        # Handle list of Author objects
        from b8tex.templates.config import Author

        if isinstance(authors, list):
            for i, author in enumerate(authors):
                if isinstance(author, Author):
                    if not author.name or not author.name.strip():
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                message="Author name cannot be empty",
                                field=f"authors[{i}].name",
                            )
                        )

        return issues

    def _validate_sections(
        self,
        sections: list[Section],
        parent_level: int = 0,
    ) -> list[ValidationIssue]:
        """Validate section structure."""
        issues: list[ValidationIssue] = []

        for i, section in enumerate(sections):
            # Check for empty section title
            if not section.title or not section.title.strip():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message="Section title cannot be empty",
                        field=f"sections[{i}].title",
                    )
                )

            # Check section level
            if section.level < 1 or section.level > 4:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Invalid section level: {section.level}. Must be 1-4.",
                        field=f"sections[{i}].level",
                    )
                )

            # Check for deep nesting
            if section.level > 3:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Deep section nesting (level {section.level}) may affect formatting",
                        field=f"sections[{i}]",
                        location=section.title if section.title else "<empty>",
                    )
                )

            # Check for empty sections
            if not section.content and not section.subsections:
                issues.append(
                    ValidationIssue(
                        severity="info",
                        message=f"Section '{section.title}' is empty",
                        field=f"sections[{i}]",
                    )
                )

            # Check title length
            if len(section.title) > 200:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Section title is long ({len(section.title)} chars)",
                        field=f"sections[{i}].title",
                    )
                )

            # Validate subsections recursively
            if section.subsections:
                subsection_issues = self._validate_sections(
                    list(section.subsections),
                    parent_level=section.level,
                )
                issues.extend(subsection_issues)

        return issues

    def _validate_lengths(self, doc: TemplateDocument) -> list[ValidationIssue]:
        """Check content lengths."""
        issues: list[ValidationIssue] = []

        # Abstract length
        if doc.abstract:
            abstract_len = len(doc.abstract)
            if abstract_len > 3000:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Abstract is long ({abstract_len} chars). Consider shortening.",
                        field="abstract",
                    )
                )

            if abstract_len < 50:
                issues.append(
                    ValidationIssue(
                        severity="info",
                        message=f"Abstract is short ({abstract_len} chars)",
                        field="abstract",
                    )
                )

        # Title length
        if len(doc.title) > 150:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=f"Title is long ({len(doc.title)} chars)",
                    field="title",
                )
            )

        # Keywords count
        if doc.keywords:
            if len(doc.keywords) > 10:
                issues.append(
                    ValidationIssue(
                        severity="info",
                        message=f"Many keywords ({len(doc.keywords)}). Typical range is 3-6.",
                        field="keywords",
                    )
                )

        return issues

    def _validate_template_specific(self, doc: TemplateDocument) -> list[ValidationIssue]:
        """Validate template-specific requirements."""
        issues: list[ValidationIssue] = []

        template = doc.config.template

        # ACL-specific checks
        if template == "acl":
            # ACL works best with structured authors
            if doc.authors and isinstance(doc.authors, str):
                if r"\aclmetadata" not in doc.authors:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=(
                                "ACL template with string authors should include \\aclmetadata. "
                                "Consider using Author objects with metadata_placement='auto'."
                            ),
                            field="authors",
                        )
                    )

        # NeurIPS-specific checks
        if template == "neurips":
            # NeurIPS prefers single-column content
            if doc.config.columns == 2:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message="NeurIPS template is designed for single-column layout",
                        field="config.columns",
                    )
                )

        # ICLR-specific checks
        if template == "iclr":
            # ICLR prefers single-column content
            if doc.config.columns == 2:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message="ICLR template is designed for single-column layout",
                        field="config.columns",
                    )
                )

        return issues

    def has_errors(self, issues: list[ValidationIssue]) -> bool:
        """Check if issues list contains errors.

        Args:
            issues: List of validation issues

        Returns:
            True if any errors present (or warnings in strict mode)
        """
        if self.strict:
            return any(issue.severity in ("error", "warning") for issue in issues)
        return any(issue.severity == "error" for issue in issues)

    def format_issues(self, issues: list[ValidationIssue]) -> str:
        """Format issues as a readable string.

        Args:
            issues: List of validation issues

        Returns:
            Formatted string
        """
        if not issues:
            return "No validation issues found."

        lines = [f"Found {len(issues)} validation issue(s):", ""]

        # Group by severity
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        infos = [i for i in issues if i.severity == "info"]

        if errors:
            lines.append("ERRORS:")
            for issue in errors:
                lines.append(f"  - {issue}")
            lines.append("")

        if warnings:
            lines.append("WARNINGS:")
            for issue in warnings:
                lines.append(f"  - {issue}")
            lines.append("")

        if infos:
            lines.append("INFO:")
            for issue in infos:
                lines.append(f"  - {issue}")

        return "\n".join(lines)

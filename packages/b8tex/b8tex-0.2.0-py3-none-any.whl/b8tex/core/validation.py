"""LaTeX content validation and security checks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from b8tex.core.document import Document

ValidationMode = Literal["strict", "permissive", "disabled"]


@dataclass
class ValidationLimits:
    """Limits for LaTeX content validation.

    These limits help prevent resource exhaustion and security issues
    from malicious or overly complex LaTeX documents.

    Attributes:
        max_file_size: Maximum size in bytes for a single LaTeX file (default: 10MB)
        max_total_size: Maximum total size for all files in a document (default: 50MB)
        max_nesting_depth: Maximum include/input nesting depth (default: 20)
        max_files: Maximum number of files in a document (default: 100)
        allow_shell_escape: Whether to allow shell-escape packages (default: False)
        dangerous_packages: Set of package names to block
        allowed_packages_only: If set, only these packages are allowed

    Example:
        >>> limits = ValidationLimits(max_file_size=5 * 1024 * 1024)  # 5MB
        >>> limits = ValidationLimits(allow_shell_escape=True)  # Allow minted, etc.
    """

    max_file_size: int = 10 * 1024 * 1024
    max_total_size: int = 50 * 1024 * 1024
    max_nesting_depth: int = 20
    max_files: int = 100
    allow_shell_escape: bool = False
    dangerous_packages: set[str] = field(
        default_factory=lambda: {
            "shellesc",
            "minted",
            "pythontex",
            "sagetex",
            "write18",
        }
    )
    allowed_packages_only: set[str] | None = None


class ValidationError(Exception):
    """Raised when content validation fails.

    Attributes:
        message: Error message
        severity: Error severity ("error" or "warning")
        filename: File that caused the error (if applicable)
    """

    def __init__(
        self,
        message: str,
        severity: Literal["error", "warning"] = "error",
        filename: str | None = None,
    ):
        super().__init__(message)
        self.severity = severity
        self.filename = filename


class ContentValidator:
    """Validates LaTeX content for security and resource constraints.

    The validator checks for:
    - File size limits to prevent resource exhaustion
    - Dangerous LaTeX commands (shell-escape, write18, etc.)
    - Potentially unsafe packages
    - Document complexity limits

    Example:
        >>> validator = ContentValidator(mode="strict")
        >>> errors = validator.validate_content(latex_code, "main.tex")
        >>> if errors:
        ...     raise errors[0]  # In strict mode, this would have been raised already
    """

    # Patterns for dangerous commands
    SHELL_ESCAPE_PATTERN = re.compile(
        r"\\(write18|immediate\\write18|input\|)", re.IGNORECASE
    )
    PACKAGE_PATTERN = re.compile(r"\\usepackage(?:\[.*?\])?\{(.*?)\}")
    INPUT_PATTERN = re.compile(r"\\(?:input|include)\{(.*?)\}")

    def __init__(
        self,
        limits: ValidationLimits | None = None,
        mode: ValidationMode = "permissive",
    ):
        """Initialize the content validator.

        Args:
            limits: Validation limits (uses defaults if None)
            mode: Validation mode:
                - "strict": Raise errors immediately
                - "permissive": Collect warnings, only error on critical issues
                - "disabled": Skip validation entirely
        """
        self.limits = limits or ValidationLimits()
        self.mode = mode

    def validate_content(
        self, content: str, filename: str = "document.tex"
    ) -> list[ValidationError]:
        """Validate LaTeX source content.

        Args:
            content: LaTeX source code to validate
            filename: Filename for error reporting

        Returns:
            List of validation errors/warnings (empty if valid)

        Raises:
            ValidationError: In strict mode when validation fails

        Example:
            >>> validator = ContentValidator()
            >>> errors = validator.validate_content("\\documentclass{article}...", "main.tex")
            >>> for error in errors:
            ...     print(f"{error.severity}: {error}")
        """
        if self.mode == "disabled":
            return []

        errors: list[ValidationError] = []

        # Check file size
        size = len(content.encode("utf-8"))
        if size > self.limits.max_file_size:
            error = ValidationError(
                f"{filename}: File size {size} bytes exceeds limit "
                f"{self.limits.max_file_size} bytes",
                severity="error",
                filename=filename,
            )
            errors.append(error)
            if self.mode == "strict":
                raise error

        # Check for shell-escape commands
        if not self.limits.allow_shell_escape and self.SHELL_ESCAPE_PATTERN.search(content):
            error = ValidationError(
                f"{filename}: Shell-escape commands detected (\\write18 or similar) "
                f"but not allowed by security policy",
                severity="error",
                filename=filename,
            )
            errors.append(error)
            if self.mode == "strict":
                raise error

        # Check for dangerous or disallowed packages
        for match in self.PACKAGE_PATTERN.finditer(content):
            packages = match.group(1).split(",")
            for pkg in packages:
                pkg = pkg.strip()

                # Check dangerous packages
                if pkg in self.limits.dangerous_packages:
                    severity: Literal["error", "warning"] = "warning" if self.mode == "permissive" else "error"
                    error = ValidationError(
                        f"{filename}: Potentially dangerous package '{pkg}' detected. "
                        f"This package may execute arbitrary commands.",
                        severity=severity,
                        filename=filename,
                    )
                    errors.append(error)
                    if self.mode == "strict":
                        raise error

                # Check allowed packages whitelist
                if self.limits.allowed_packages_only and pkg not in self.limits.allowed_packages_only:
                    severity_check: Literal["error", "warning"] = "warning" if self.mode == "permissive" else "error"
                    error = ValidationError(
                        f"{filename}: Package '{pkg}' is not in the allowed package list",
                        severity=severity_check,
                        filename=filename,
                    )
                    errors.append(error)
                    if self.mode == "strict":
                        raise error

        return errors

    def validate_document(self, document: Document) -> list[ValidationError]:
        """Validate an entire document including all resources.

        This checks the entrypoint and all resources for compliance
        with the configured limits.

        Args:
            document: Document to validate

        Returns:
            List of validation errors/warnings

        Raises:
            ValidationError: In strict mode if validation fails

        Example:
            >>> from b8tex import Document
            >>> doc = Document.from_string("\\documentclass{article}...")
            >>> validator = ContentValidator()
            >>> errors = validator.validate_document(doc)
        """
        from b8tex.core.document import InMemorySource

        if self.mode == "disabled":
            return []

        errors: list[ValidationError] = []
        total_size = 0
        file_count = 0

        # Validate entrypoint
        if isinstance(document.entrypoint, InMemorySource):
            errors.extend(
                self.validate_content(document.entrypoint.content, document.entrypoint.filename)
            )
            total_size += len(document.entrypoint.content.encode("utf-8"))
            file_count += 1
        else:
            if document.entrypoint.exists():
                size = document.entrypoint.stat().st_size
                total_size += size
                file_count += 1

                if size > self.limits.max_file_size:
                    error = ValidationError(
                        f"{document.entrypoint}: File size {size} bytes exceeds limit "
                        f"{self.limits.max_file_size} bytes",
                        severity="error",
                        filename=str(document.entrypoint),
                    )
                    errors.append(error)
                    if self.mode == "strict":
                        raise error

        # Validate resources
        for resource in document.resources:
            if isinstance(resource.path_or_mem, InMemorySource):
                errors.extend(
                    self.validate_content(
                        resource.path_or_mem.content, resource.path_or_mem.filename
                    )
                )
                total_size += len(resource.path_or_mem.content.encode("utf-8"))
            else:
                if resource.path_or_mem.exists():
                    total_size += resource.path_or_mem.stat().st_size

            file_count += 1

        # Check total size
        if total_size > self.limits.max_total_size:
            error = ValidationError(
                f"Total document size {total_size} bytes exceeds limit "
                f"{self.limits.max_total_size} bytes",
                severity="error",
            )
            errors.append(error)
            if self.mode == "strict":
                raise error

        # Check file count
        if file_count > self.limits.max_files:
            error = ValidationError(
                f"Document contains {file_count} files, exceeds limit "
                f"{self.limits.max_files} files",
                severity="error",
            )
            errors.append(error)
            if self.mode == "strict":
                raise error

        return errors

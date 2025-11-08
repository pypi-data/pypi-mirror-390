"""Tests for LaTeX content validation and security policies."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from b8tex.core.document import Document, InMemorySource, Resource
from b8tex.core.validation import (
    ContentValidator,
    ValidationError,
    ValidationLimits,
)

# ValidationLimits Tests


def test_validation_limits_defaults():
    """Test default ValidationLimits values."""
    limits = ValidationLimits()
    assert limits.max_file_size == 10 * 1024 * 1024  # 10MB
    assert limits.max_total_size == 50 * 1024 * 1024  # 50MB
    assert limits.max_nesting_depth == 20
    assert limits.max_files == 100
    assert limits.allow_shell_escape is False
    assert len(limits.dangerous_packages) == 5
    assert "minted" in limits.dangerous_packages
    assert limits.allowed_packages_only is None


def test_validation_limits_custom():
    """Test custom ValidationLimits values override defaults."""
    limits = ValidationLimits(
        max_file_size=5 * 1024 * 1024,
        max_total_size=25 * 1024 * 1024,
        max_files=50,
        allow_shell_escape=True,
        dangerous_packages={"custom_pkg"},
        allowed_packages_only={"amsmath", "graphicx"},
    )
    assert limits.max_file_size == 5 * 1024 * 1024
    assert limits.max_total_size == 25 * 1024 * 1024
    assert limits.max_files == 50
    assert limits.allow_shell_escape is True
    assert limits.dangerous_packages == {"custom_pkg"}
    assert limits.allowed_packages_only == {"amsmath", "graphicx"}


def test_dangerous_packages_mutable():
    """Test each ValidationLimits instance gets its own dangerous_packages set."""
    limits1 = ValidationLimits()
    limits2 = ValidationLimits()

    limits1.dangerous_packages.add("custom")
    assert "custom" in limits1.dangerous_packages
    assert "custom" not in limits2.dangerous_packages


# ValidationError Tests


def test_validation_error_severity_error():
    """Test ValidationError with error severity."""
    error = ValidationError("Test error", severity="error", filename="test.tex")
    assert str(error) == "Test error"
    assert error.severity == "error"
    assert error.filename == "test.tex"


def test_validation_error_severity_warning():
    """Test ValidationError with warning severity."""
    warning = ValidationError("Test warning", severity="warning")
    assert str(warning) == "Test warning"
    assert warning.severity == "warning"
    assert warning.filename is None


def test_validation_error_with_filename():
    """Test ValidationError filename attribute."""
    error = ValidationError("Error message", filename="main.tex")
    assert error.filename == "main.tex"


# ContentValidator Mode Tests


def test_validator_disabled_mode_skips_validation():
    """Test mode='disabled' bypasses all checks."""
    validator = ContentValidator(mode="disabled")

    # Malicious content should pass
    content = r"""
    \documentclass{article}
    \usepackage{minted}
    \begin{document}
    \write18{rm -rf /}
    \end{document}
    """

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) == 0


def test_validator_permissive_mode_returns_warnings():
    """Test mode='permissive' collects warnings without raising."""
    limits = ValidationLimits(dangerous_packages={"minted"})
    validator = ContentValidator(limits=limits, mode="permissive")

    content = r"\documentclass{article}\usepackage{minted}\begin{document}\end{document}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    # In permissive mode, dangerous packages are warnings
    assert any("minted" in str(e) for e in errors)


def test_validator_strict_mode_raises_immediately():
    """Test mode='strict' raises ValidationError on first issue."""
    limits = ValidationLimits(dangerous_packages={"minted"})
    validator = ContentValidator(limits=limits, mode="strict")

    content = r"\documentclass{article}\usepackage{minted}\begin{document}\end{document}"

    with pytest.raises(ValidationError) as exc_info:
        validator.validate_content(content, "test.tex")

    assert "minted" in str(exc_info.value)


# File Size Tests


def test_validate_content_file_size_within_limit():
    """Test content within size limit passes validation."""
    validator = ContentValidator()

    # 1KB content
    content = "x" * 1024

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) == 0


def test_validate_content_file_size_exceeds_limit_strict():
    """Test content exceeding size limit raises in strict mode."""
    limits = ValidationLimits(max_file_size=1000)  # 1000 bytes
    validator = ContentValidator(limits=limits, mode="strict")

    # 2000 bytes
    content = "x" * 2000

    with pytest.raises(ValidationError) as exc_info:
        validator.validate_content(content, "test.tex")

    assert "exceeds limit" in str(exc_info.value)
    assert "2000 bytes" in str(exc_info.value)


def test_validate_content_file_size_exceeds_limit_permissive():
    """Test content exceeding size limit returns error in permissive mode."""
    limits = ValidationLimits(max_file_size=1000)
    validator = ContentValidator(limits=limits, mode="permissive")

    content = "x" * 2000

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) == 1
    assert errors[0].severity == "error"
    assert "exceeds limit" in str(errors[0])


def test_validate_content_unicode_size_calculation():
    """Test size is calculated from UTF-8 encoding."""
    validator = ContentValidator()

    # Emoji and unicode characters take multiple bytes
    content = "Hello 世界 🌍" * 100
    byte_size = len(content.encode("utf-8"))

    # Should pass if under limit
    errors = validator.validate_content(content, "test.tex")
    assert len(errors) == 0

    # Now test with tight limit
    limits = ValidationLimits(max_file_size=byte_size - 1)
    validator = ContentValidator(limits=limits, mode="permissive")
    errors = validator.validate_content(content, "test.tex")
    assert len(errors) == 1


# Shell Escape Tests


def test_validate_shell_escape_write18_detected():
    """Test \\write18 command is detected."""
    validator = ContentValidator(mode="permissive")

    content = r"\documentclass{article}\begin{document}\write18{ls}\end{document}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("shell-escape" in str(e).lower() for e in errors)


def test_validate_shell_escape_immediate_write18_detected():
    """Test \\immediate\\write18 is detected."""
    validator = ContentValidator(mode="permissive")

    content = r"\immediate\write18{rm -rf /}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("shell-escape" in str(e).lower() for e in errors)


def test_validate_shell_escape_input_pipe_detected():
    """Test \\input| is detected."""
    validator = ContentValidator(mode="permissive")

    content = r"\input|ls"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("shell-escape" in str(e).lower() for e in errors)


def test_validate_shell_escape_case_insensitive():
    """Test shell-escape pattern matching is case-insensitive."""
    validator = ContentValidator(mode="permissive")

    content1 = r"\Write18{command}"
    content2 = r"\WRITE18{command}"

    errors1 = validator.validate_content(content1, "test.tex")
    errors2 = validator.validate_content(content2, "test.tex")

    assert len(errors1) > 0
    assert len(errors2) > 0


def test_validate_shell_escape_allowed_when_enabled():
    """Test shell-escape allowed when allow_shell_escape=True."""
    limits = ValidationLimits(allow_shell_escape=True)
    validator = ContentValidator(limits=limits)

    content = r"\write18{ls}"

    errors = validator.validate_content(content, "test.tex")
    # Should not have shell-escape errors
    assert not any("shell-escape" in str(e).lower() for e in errors)


# Dangerous Package Tests


def test_validate_dangerous_package_shellesc():
    """Test 'shellesc' package is detected."""
    validator = ContentValidator(mode="permissive")

    content = r"\usepackage{shellesc}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("shellesc" in str(e) for e in errors)


def test_validate_dangerous_package_minted():
    """Test 'minted' package is detected."""
    validator = ContentValidator(mode="permissive")

    content = r"\usepackage{minted}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("minted" in str(e) for e in errors)


def test_validate_dangerous_package_pythontex():
    """Test 'pythontex' package is detected."""
    validator = ContentValidator(mode="permissive")

    content = r"\usepackage{pythontex}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("pythontex" in str(e) for e in errors)


def test_validate_dangerous_package_multiple():
    """Test multiple dangerous packages detected."""
    validator = ContentValidator(mode="permissive")

    content = r"\usepackage{minted}\usepackage{pythontex}\usepackage{shellesc}"

    errors = validator.validate_content(content, "test.tex")
    # Should have at least 3 errors (one for each dangerous package)
    assert len(errors) >= 3


def test_validate_dangerous_package_with_options():
    """Test dangerous package with options is still detected."""
    validator = ContentValidator(mode="permissive")

    content = r"\usepackage[cache=false,gobble]{minted}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("minted" in str(e) for e in errors)


def test_validate_dangerous_package_comma_separated():
    """Test comma-separated packages are checked individually."""
    validator = ContentValidator(mode="permissive")

    content = r"\usepackage{amsmath,minted,graphicx}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("minted" in str(e) for e in errors)


def test_validate_dangerous_package_with_whitespace():
    """Test whitespace around package names is handled."""
    validator = ContentValidator(mode="permissive")

    content = r"\usepackage{ minted }"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("minted" in str(e) for e in errors)


# Allowed Packages Tests


def test_validate_allowed_packages_only_mode_blocks_unlisted():
    """Test allowed_packages_only mode blocks unlisted packages."""
    limits = ValidationLimits(allowed_packages_only={"amsmath", "graphicx"})
    validator = ContentValidator(limits=limits, mode="permissive")

    content = r"\usepackage{hyperref}"

    errors = validator.validate_content(content, "test.tex")
    assert len(errors) > 0
    assert any("hyperref" in str(e) and "allowed package list" in str(e) for e in errors)


def test_validate_allowed_packages_only_mode_permits_listed():
    """Test whitelisted packages pass validation."""
    limits = ValidationLimits(allowed_packages_only={"amsmath", "graphicx"})
    validator = ContentValidator(limits=limits)

    content = r"\usepackage{amsmath}\usepackage{graphicx}"

    errors = validator.validate_content(content, "test.tex")
    # Should not have any "allowed package list" errors
    assert not any("allowed package list" in str(e) for e in errors)


def test_validate_allowed_packages_with_dangerous_overlap():
    """Test dangerous package check takes precedence over allowed list."""
    limits = ValidationLimits(
        allowed_packages_only={"amsmath", "minted"},
        dangerous_packages={"minted"}
    )
    validator = ContentValidator(limits=limits, mode="permissive")

    content = r"\usepackage{minted}"

    errors = validator.validate_content(content, "test.tex")
    # Should have dangerous package error
    assert any("dangerous" in str(e).lower() for e in errors)


# Document Validation Tests


def test_validate_document_inmemory_source():
    """Test validates InMemorySource entrypoint."""
    validator = ContentValidator(mode="permissive")

    content = r"\usepackage{minted}"
    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", content),
        resources=[]
    )

    errors = validator.validate_document(doc)
    assert len(errors) > 0
    assert any("minted" in str(e) for e in errors)


def test_validate_document_file_source():
    """Test validates Path entrypoint."""
    validator = ContentValidator(mode="permissive")

    # Create a document with an actual path (doesn't need to exist for validation)
    with patch.object(Path, 'exists', return_value=True):
        with patch.object(Path, 'stat', return_value=Mock(st_size=1000)):
            doc = Document(
                name="test",
                entrypoint=Path("test.tex"),
                resources=[]
            )

            errors = validator.validate_document(doc)
            # Should pass size check
            assert not any("exceeds limit" in str(e) for e in errors)


def test_validate_document_resources_inmemory():
    """Test validates resources with InMemorySource."""
    validator = ContentValidator(mode="permissive")

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\documentclass{article}"),
        resources=[
            Resource(InMemorySource("style.sty", r"\usepackage{minted}"))
        ]
    )

    errors = validator.validate_document(doc)
    assert len(errors) > 0
    assert any("minted" in str(e) for e in errors)


def test_validate_document_total_size_limit():
    """Test total size across all files enforced."""
    limits = ValidationLimits(max_total_size=2000)  # 2KB total
    validator = ContentValidator(limits=limits, mode="permissive")

    # Each file is 1KB, total 3KB
    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", "x" * 1024),
        resources=[
            Resource(InMemorySource("file1.tex", "y" * 1024)),
            Resource(InMemorySource("file2.tex", "z" * 1024)),
        ]
    )

    errors = validator.validate_document(doc)
    assert len(errors) > 0
    assert any("total" in str(e).lower() and "exceeds limit" in str(e) for e in errors)


def test_validate_document_file_count_limit():
    """Test maximum file count enforced."""
    limits = ValidationLimits(max_files=2)
    validator = ContentValidator(limits=limits, mode="permissive")

    # 1 entrypoint + 2 resources = 3 files (exceeds limit of 2)
    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", "content"),
        resources=[
            Resource(InMemorySource("file1.tex", "a")),
            Resource(InMemorySource("file2.tex", "b")),
        ]
    )

    errors = validator.validate_document(doc)
    assert len(errors) > 0
    assert any("file" in str(e).lower() and "exceeds limit" in str(e) for e in errors)


def test_validate_document_mixed_sources():
    """Test mix of InMemorySource and Path."""
    validator = ContentValidator()

    # Use actual paths (Resource will handle them properly)
    with patch.object(Path, 'exists', return_value=True):
        with patch.object(Path, 'stat', return_value=Mock(st_size=500)):
            doc = Document(
                name="test",
                entrypoint=InMemorySource("main.tex", "content"),
                resources=[
                    Resource(InMemorySource("mem.tex", "memory content")),
                    Resource(Path("file.tex"))
                ]
            )

            errors = validator.validate_document(doc)
            # Should pass without errors (no dangerous content, within limits)
            assert not any(e.severity == "error" for e in errors)


def test_validate_document_nonexistent_file():
    """Test handles nonexistent Path gracefully."""
    validator = ContentValidator()

    # Use actual path with exists=False
    with patch.object(Path, 'exists', return_value=False):
        doc = Document(
            name="test",
            entrypoint=InMemorySource("main.tex", "content"),
            resources=[Resource(Path("nonexistent.tex"))]
        )

        # Should not crash, just skip the nonexistent file
        errors = validator.validate_document(doc)
        # No errors expected for nonexistent file (size not counted)
        assert not any("exceeds limit" in str(e) for e in errors)


def test_validate_document_with_nested_dangerous_content():
    """Test dangerous content in resources detected."""
    validator = ContentValidator(mode="permissive")

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\documentclass{article}"),
        resources=[
            Resource(InMemorySource("dangerous.tex", r"\write18{rm -rf /}"))
        ]
    )

    errors = validator.validate_document(doc)
    assert len(errors) > 0
    assert any("shell-escape" in str(e).lower() for e in errors)

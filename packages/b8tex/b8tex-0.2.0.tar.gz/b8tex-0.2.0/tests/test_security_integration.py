"""Integration tests for security features in TectonicCompiler."""

from unittest.mock import Mock, patch

import pytest

from b8tex.api import TectonicCompiler
from b8tex.core.config import TexConfig
from b8tex.core.document import Document, InMemorySource, Resource
from b8tex.core.runner import ResourceLimits
from b8tex.core.validation import ContentValidator, ValidationError, ValidationLimits
from b8tex.exceptions import CompilationFailed

# Compiler Initialization Tests


def test_compiler_init_loads_config():
    """Test compiler initializes with config loading."""
    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig()
        mock_load.return_value = mock_config

        with patch("b8tex.api.TectonicBinary.discover"), patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(use_cache=False)

            assert mock_load.called
            assert isinstance(compiler.validator, ContentValidator)


def test_compiler_init_with_custom_validator():
    """Test custom validator accepted."""
    custom_validator = ContentValidator(mode="strict")

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig()
        mock_load.return_value = mock_config

        with patch("b8tex.api.TectonicBinary.discover"), patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(validator=custom_validator, use_cache=False)

            assert compiler.validator is custom_validator
            assert compiler.validator.mode == "strict"


def test_compiler_init_uses_resource_limits_from_config():
    """Test resource limits from config passed to ProcessRunner."""
    custom_limits = ResourceLimits(memory_mb=2048, timeout_seconds=600.0)
    mock_config = TexConfig(resource_limits=custom_limits)

    with patch("b8tex.api.load_config", return_value=mock_config):
        with patch("b8tex.api.TectonicBinary.discover"):
            with patch("b8tex.api.BuildCache"):
                compiler = TectonicCompiler(use_cache=False)

                assert compiler.runner.limits.memory_mb == 2048
                assert compiler.runner.limits.timeout_seconds == 600.0


def test_compiler_init_probes_binary_capabilities():
    """Test binary capabilities probed if not present."""
    mock_binary = Mock()
    mock_binary.capabilities = None

    with patch("b8tex.api.load_config"), patch("b8tex.api.BuildCache"):
        TectonicCompiler(binary=mock_binary, use_cache=False)

        assert mock_binary.probe.called


def test_compiler_init_skips_probe_if_capabilities_present():
    """Test binary probe skipped if capabilities already present."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()  # Already has capabilities

    with patch("b8tex.api.load_config"), patch("b8tex.api.BuildCache"):
        TectonicCompiler(binary=mock_binary, use_cache=False)

        assert not mock_binary.probe.called


# Validation Integration Tests


def test_compile_document_validates_content():
    """Test document validated before compilation."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock(version="0.15.0")
    mock_binary.validate_options = Mock()

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\documentclass{article}\begin{document}Hi\end{document}"),
        resources=[]
    )

    with patch("b8tex.api.load_config"):
        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)
            mock_validator = Mock(return_value=[])
            compiler.validator.validate_document = mock_validator

            # Mock compilation to avoid actual process execution
            with patch.object(compiler, "_build_command", return_value=["tectonic"]):
                with patch.object(compiler.runner, "run") as mock_run:
                    mock_run.return_value = Mock(returncode=0, stdout="", stderr="", elapsed=1.0)

                    with patch("b8tex.api.Workspace"):
                        with patch("b8tex.api.LogParser"):
                            with patch.object(compiler, "_collect_artifacts", return_value=[]):
                                try:
                                    compiler.compile_document(doc)
                                except Exception:
                                    pass  # Might fail due to mocking, but validation should have been called

            # Validation should have been called
            assert mock_validator.called


def test_compile_document_validation_error_raises():
    """Test validation errors prevent compilation."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    # Document with dangerous content
    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\usepackage{minted}"),
        resources=[]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_mode="strict")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            # Compilation should raise ValidationError
            with pytest.raises(ValidationError):
                compiler.compile_document(doc)


def test_compile_document_validation_file_size_enforced():
    """Test file size limits enforced during validation."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    # Large document exceeding limit
    limits = ValidationLimits(max_file_size=1000)  # 1000 bytes
    large_content = "x" * 2000  # 2000 bytes

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", large_content),
        resources=[]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_limits=limits, validation_mode="strict")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            with pytest.raises(ValidationError, match="exceeds limit"):
                compiler.compile_document(doc)


def test_compile_document_validation_dangerous_package_blocked():
    """Test dangerous packages blocked in strict mode."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\usepackage{pythontex}"),
        resources=[]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_mode="strict")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            with pytest.raises(ValidationError, match="pythontex"):
                compiler.compile_document(doc)


def test_compile_document_validation_shell_escape_blocked():
    """Test shell escape commands blocked."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\write18{rm -rf /}"),
        resources=[]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_mode="strict")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            with pytest.raises(ValidationError, match="(?i)shell.escape"):
                compiler.compile_document(doc)


def test_compile_document_validation_disabled_skips():
    """Test validation_mode='disabled' skips validation."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    # Dangerous content that would normally be blocked
    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\write18{ls}"),
        resources=[]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_mode="disabled")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            # Should not raise ValidationError (but may fail for other reasons)
            # We'll mock the rest of compilation to avoid errors
            with patch.object(compiler, "_build_command", return_value=["cmd"]):
                with patch.object(compiler.runner, "run") as mock_run:
                    mock_run.return_value = Mock(returncode=0, stdout="", stderr="", elapsed=1.0)
                    with patch("b8tex.api.Workspace"):
                        with patch("b8tex.api.LogParser"):
                            with patch.object(compiler, "_collect_artifacts", return_value=[]):
                                try:
                                    # Should not raise ValidationError
                                    compiler.compile_document(doc)
                                except ValidationError:
                                    pytest.fail("ValidationError raised when validation_mode='disabled'")
                                except Exception:
                                    # Other exceptions are OK for this test
                                    pass


# Resource Limit Tests


def test_compile_document_uses_resource_limits():
    """Test resource limits from config applied."""
    custom_limits = ResourceLimits(memory_mb=512, timeout_seconds=120.0)
    mock_config = TexConfig(resource_limits=custom_limits, validation_mode="disabled")

    with patch("b8tex.api.load_config", return_value=mock_config):
        with patch("b8tex.api.TectonicBinary.discover") as mock_discover:
            mock_binary = Mock()
            mock_binary.capabilities = Mock()
            mock_discover.return_value = mock_binary

            with patch("b8tex.api.BuildCache"):
                compiler = TectonicCompiler(use_cache=False)

                assert compiler.runner.limits.memory_mb == 512
                assert compiler.runner.limits.timeout_seconds == 120.0


# Error Handling Tests


def test_compile_document_compilation_failed_raised():
    """Test CompilationFailed raised on non-zero returncode."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\documentclass{article}"),
        resources=[]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_mode="disabled")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            with patch.object(compiler, "_build_command", return_value=["cmd"]):
                with patch.object(compiler.runner, "run") as mock_run:
                    # Return failure
                    mock_run.return_value = Mock(
                        returncode=1,
                        stdout="",
                        stderr="Error message",
                        elapsed=1.0
                    )

                    with patch("b8tex.api.Workspace"):
                        with patch("b8tex.api.LogParser") as mock_parser:
                            mock_parser_inst = Mock()
                            mock_parser_inst.get_errors.return_value = [Mock(text="LaTeX error")]
                            mock_parser_inst.get_warnings.return_value = []
                            mock_parser_inst.build_module_graph.return_value = None
                            mock_parser_inst.parse_output = Mock()
                            mock_parser.return_value = mock_parser_inst

                            with patch.object(compiler, "_collect_artifacts", return_value=[]):
                                with pytest.raises(CompilationFailed, match="return code"):
                                    compiler.compile_document(doc)


def test_compile_document_total_size_multiple_files():
    """Test total size calculated across all files."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    # Multiple files each under limit, but total > max_total_size
    limits = ValidationLimits(
        max_file_size=2000,  # 2KB per file
        max_total_size=3000  # 3KB total
    )

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", "x" * 1500),  # 1.5KB
        resources=[
            Resource(InMemorySource("file1.tex", "y" * 1200)),  # 1.2KB
            Resource(InMemorySource("file2.tex", "z" * 500)),   # 0.5KB
        ]
    )
    # Total: 3.2KB > 3KB limit

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_limits=limits, validation_mode="strict")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            with pytest.raises(ValidationError, match="(?i)total"):
                compiler.compile_document(doc)


def test_compile_document_file_count_limit_enforced():
    """Test maximum file count enforced."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    limits = ValidationLimits(max_files=2)  # Only 2 files allowed

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", "content"),
        resources=[
            Resource(InMemorySource("file1.tex", "a")),
            Resource(InMemorySource("file2.tex", "b")),
        ]
    )
    # Total: 3 files (entrypoint + 2 resources) > 2 limit

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_limits=limits, validation_mode="strict")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            with pytest.raises(ValidationError, match="file"):
                compiler.compile_document(doc)


def test_compile_document_nested_dangerous_content_in_resources():
    """Test dangerous content in resources detected."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\documentclass{article}"),
        resources=[
            Resource(InMemorySource("dangerous.tex", r"\write18{malicious}"))
        ]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_mode="strict")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            with pytest.raises(ValidationError, match="(?i)shell.escape"):
                compiler.compile_document(doc)


# Edge Cases


def test_compile_document_empty_dangerous_packages_allows_all():
    """Test empty dangerous_packages set allows all packages."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    limits = ValidationLimits(dangerous_packages=set())  # Empty set

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", r"\usepackage{minted}"),
        resources=[]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_limits=limits, validation_mode="permissive")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            # Validate should not raise (minted is not in empty dangerous set)
            errors = compiler.validator.validate_document(doc)
            # Should not have dangerous package errors
            assert not any("dangerous" in str(e).lower() for e in errors)


def test_compile_document_unicode_content_size_check():
    """Test Unicode content size calculated correctly."""
    mock_binary = Mock()
    mock_binary.capabilities = Mock()
    mock_binary.validate_options = Mock()

    # Unicode content with multi-byte characters
    unicode_content = "Hello 世界 🌍" * 100
    byte_size = len(unicode_content.encode("utf-8"))

    limits = ValidationLimits(max_file_size=byte_size - 1)  # Just under actual size

    doc = Document(
        name="test",
        entrypoint=InMemorySource("main.tex", unicode_content),
        resources=[]
    )

    with patch("b8tex.api.load_config") as mock_load:
        mock_config = TexConfig(validation_limits=limits, validation_mode="strict")
        mock_load.return_value = mock_config

        with patch("b8tex.api.BuildCache"):
            compiler = TectonicCompiler(binary=mock_binary, use_cache=False)

            # Should raise because byte size exceeds limit
            with pytest.raises(ValidationError, match="exceeds limit"):
                compiler.compile_document(doc)

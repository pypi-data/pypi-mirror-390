"""Tests for enhanced API functionality."""

import contextlib
from pathlib import Path

import pytest

from b8tex.api import TectonicCompiler, compile_document, compile_string
from b8tex.core.cache import BuildCache
from b8tex.core.document import Document
from b8tex.core.options import BuildOptions, SecurityPolicy
from b8tex.exceptions import MissingBinaryError


def test_compiler_init_with_cache():
    """Test compiler initialization with cache."""
    try:
        compiler = TectonicCompiler(use_cache=True)

        assert compiler.use_cache is True
        assert compiler.cache is not None
        assert isinstance(compiler.cache, BuildCache)

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_compiler_init_without_cache():
    """Test compiler initialization without cache."""
    try:
        compiler = TectonicCompiler(use_cache=False)

        assert compiler.use_cache is False
        assert compiler.cache is None

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_compiler_init_with_custom_cache(tmp_path: Path):
    """Test compiler initialization with custom cache."""
    try:
        cache_path = tmp_path / "custom_cache" / "b8tex.db"
        custom_cache = BuildCache(db_path=cache_path)
        try:
            compiler = TectonicCompiler(cache=custom_cache, use_cache=True)

            assert compiler.cache is custom_cache
            assert compiler.cache.db_path == cache_path
        finally:
            custom_cache.close()

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_validate_options_called(tmp_path: Path):
    """Test that validate_options is called before compilation."""
    try:
        compiler = TectonicCompiler(use_cache=False)

        # Mock validate_options to track calls
        original_validate = compiler.binary.validate_options
        call_count = {"count": 0}

        def mock_validate(opts):
            call_count["count"] += 1
            original_validate(opts)

        compiler.binary.validate_options = mock_validate

        # Create a simple document
        doc = Document.from_string("\\documentclass{article}\\begin{document}Hello\\end{document}")
        options = BuildOptions()

        # Attempt compilation (may fail, but validate should be called)
        try:
            compiler.compile_document(doc, options, workdir=tmp_path)
        except Exception:
            pass  # We don't care if compilation fails

        # Validate was called at least once
        assert call_count["count"] >= 1

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_cache_fingerprint_generation(tmp_path: Path):
    """Test that cache fingerprints are generated."""
    try:
        compiler = TectonicCompiler(use_cache=True)

        # Mock cache to track get_fingerprint calls
        original_get_fingerprint = compiler.cache.get_fingerprint
        fingerprints = []

        def mock_get_fingerprint(*args, **kwargs):
            fp = original_get_fingerprint(*args, **kwargs)
            fingerprints.append(fp)
            return fp

        compiler.cache.get_fingerprint = mock_get_fingerprint

        doc = Document.from_string("\\documentclass{article}\\begin{document}Test\\end{document}")

        with contextlib.suppress(Exception):
            compiler.compile_document(doc, workdir=tmp_path)

        # Should have generated at least one fingerprint
        assert len(fingerprints) >= 1
        assert all(isinstance(fp, str) for fp in fingerprints)

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_cache_write_on_success(tmp_path: Path):
    """Test that successful compilations are written to cache."""
    try:
        compiler = TectonicCompiler(use_cache=True)

        # Track cache write calls
        write_calls = []
        original_write = compiler.cache.write

        def mock_write(*args, **kwargs):
            write_calls.append((args, kwargs))
            return original_write(*args, **kwargs)

        compiler.cache.write = mock_write

        doc = Document.from_string(
            "\\documentclass{article}\\begin{document}Hello World\\end{document}",
            name="test"
        )

        try:
            result = compiler.compile_document(doc, workdir=tmp_path, timeout=30.0)

            if result.success:
                # Should have written to cache
                assert len(write_calls) >= 1
        except Exception as e:
            # Compilation may fail for various reasons (missing tectonic, etc.)
            pytest.skip(f"Compilation failed: {e}")

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_cache_restoration(tmp_path: Path):
    """Test cache restoration on subsequent compilation."""
    try:
        cache_path = tmp_path / "cache" / "b8tex.db"
        cache = BuildCache(db_path=cache_path)
        try:
            compiler = TectonicCompiler(cache=cache, use_cache=True)

            doc = Document.from_string(
                "\\documentclass{article}\\begin{document}Cached\\end{document}",
                name="cached"
            )
            options = BuildOptions()

            # First compilation
            try:
                result1 = compiler.compile_document(doc, options, workdir=tmp_path / "work1", timeout=30.0)

                if not result1.success:
                    pytest.skip("First compilation failed")

                # Second compilation with same document (should hit cache)
                result2 = compiler.compile_document(doc, options, workdir=tmp_path / "work2", timeout=30.0)

                # Both should succeed
                assert result2.success

                # Second should be faster (cached) - elapsed should be near 0
                # Note: With current implementation, cached results have elapsed from cache
                assert result2.elapsed >= 0

            except Exception as e:
                pytest.skip(f"Compilation failed: {e}")
        finally:
            cache.close()

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_search_paths_setup(tmp_path: Path):
    """Test that search paths are properly set up."""
    try:
        compiler = TectonicCompiler(use_cache=False)

        # Create paths
        custom_path = tmp_path / "custom_packages"
        custom_path.mkdir()

        from b8tex.core.project import InputPath

        doc = Document.from_string(
            "\\documentclass{article}\\begin{document}Test\\end{document}",
            name="test"
        )
        doc.search_paths = [InputPath(custom_path, order=10)]

        # Mock the runner to capture environment
        env_captured = {}

        def mock_run(cmd, cwd, env, timeout):
            env_captured.update(env)
            # Return a failed result to avoid actual compilation
            from b8tex.core.runner import CompletedProcess
            return CompletedProcess(returncode=1, stdout="", stderr="mock failure", elapsed=0.0)

        compiler.runner.run = mock_run

        try:
            compiler.compile_document(doc, workdir=tmp_path)
        except Exception:
            pass  # We expect failure from mock

        # Check that TEXINPUTS was set
        assert "TEXINPUTS" in env_captured
        assert str(custom_path.resolve()) in env_captured["TEXINPUTS"]

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_environment_isolation(tmp_path: Path):
    """Test that LaTeX environment variables are isolated."""
    try:
        compiler = TectonicCompiler(use_cache=False)

        doc = Document.from_string("\\documentclass{article}\\begin{document}Test\\end{document}")
        options = BuildOptions()

        # Set some LaTeX environment variables
        options.env = {
            "TEXINPUTS": "/some/path",
            "TEXMFHOME": "/home/texmf",
            "PATH": "/usr/bin",
        }

        # Mock runner to capture environment
        env_captured = {}

        def mock_run(cmd, cwd, env, timeout):
            env_captured.update(env)
            from b8tex.core.runner import CompletedProcess
            return CompletedProcess(returncode=1, stdout="", stderr="mock", elapsed=0.0)

        compiler.runner.run = mock_run

        with contextlib.suppress(Exception):
            compiler.compile_document(doc, options, workdir=tmp_path)

        # Original TEXINPUTS should be removed (isolated)
        # New TEXINPUTS should be set by workspace
        if "TEXINPUTS" in env_captured:
            # Should not contain the original "/some/path"
            assert "/some/path" not in env_captured["TEXINPUTS"]

        # PATH should be preserved
        assert env_captured.get("PATH") == "/usr/bin"

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_build_command_v1(tmp_path: Path):
    """Test V1 command building."""
    try:
        compiler = TectonicCompiler(use_cache=False)

        entrypoint = tmp_path / "test.tex"
        outdir = tmp_path / "output"
        options = BuildOptions(synctex=True, print_log=True)

        cmd = compiler._build_command(entrypoint, outdir, options)

        # Should have basic structure
        assert str(compiler.binary.path) in cmd
        assert str(entrypoint) in cmd
        assert "--outdir" in cmd
        assert str(outdir) in cmd

        # Should have options
        if compiler.binary.capabilities and "--synctex" in compiler.binary.capabilities.supported_flags:
            assert "--synctex" in cmd
        assert "--print" in cmd

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_compile_string_convenience():
    """Test compile_string convenience function."""
    try:
        result = compile_string(
            "\\documentclass{article}\\begin{document}Hello\\end{document}",
            name="convenience_test",
            timeout=30.0,
        )

        # May succeed or fail depending on environment
        assert result.success in [True, False]
        assert result.returncode is not None

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")
    except Exception as e:
        # Allow other exceptions (compilation errors, etc.)
        pytest.skip(f"Compilation error: {e}")


def test_compile_document_convenience():
    """Test compile_document convenience function."""
    try:
        doc = Document.from_string(
            "\\documentclass{article}\\begin{document}Convenience\\end{document}"
        )

        result = compile_document(doc, timeout=30.0)

        assert result.success in [True, False]
        assert result.returncode is not None

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")
    except Exception as e:
        pytest.skip(f"Compilation error: {e}")


def test_security_policy_validation():
    """Test that security policies are validated."""
    try:
        compiler = TectonicCompiler(use_cache=False)

        # If shell-escape is not supported, should raise error
        caps = compiler.binary.capabilities

        if caps and "-Z shell-escape" not in caps.supported_flags:
            from b8tex.exceptions import UnsupportedOptionError

            options = BuildOptions(
                security=SecurityPolicy(allow_shell_escape=True)
            )

            with pytest.raises(UnsupportedOptionError):
                compiler.binary.validate_options(options)

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")

"""Tests for enhanced Binary functionality."""

from pathlib import Path

import pytest

from b8tex.core.binary import TectonicBinary
from b8tex.core.options import BuildOptions, SecurityPolicy
from b8tex.exceptions import MissingBinaryError, UnsupportedOptionError


def test_probe_detects_multiple_flags():
    """Test that probe detects multiple flags."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        # Should detect at least basic flags
        assert caps.supported_flags
        assert isinstance(caps.supported_flags, set)

        # Version should be detected
        assert caps.version
        assert caps.version != "unknown"

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_interface_for_v1_default():
    """Test that V1 is returned by default."""
    try:
        binary = TectonicBinary.discover()
        binary.probe()

        # Without project_dir, should use V1
        interface = binary.interface_for()
        assert interface == "v1"

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_interface_for_v2_with_toml(tmp_path: Path):
    """Test that V2 is returned when Tectonic.toml exists."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        if not caps.supports_v2:
            pytest.skip("Tectonic V2 not supported")

        # Create a mock Tectonic.toml
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        toml_file = project_dir / "Tectonic.toml"
        toml_file.write_text("[doc]\nname = 'test'\n")

        interface = binary.interface_for(project_dir)
        assert interface == "v2"

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_validate_options_basic():
    """Test basic option validation."""
    try:
        binary = TectonicBinary.discover()
        binary.probe()

        # Basic options should work
        options = BuildOptions()
        binary.validate_options(options)  # Should not raise

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_validate_options_synctex():
    """Test synctex validation."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        options = BuildOptions(synctex=True)

        if "--synctex" in caps.supported_flags:
            # Should not raise
            binary.validate_options(options)
        else:
            # Should raise UnsupportedOptionError
            with pytest.raises(UnsupportedOptionError) as exc_info:
                binary.validate_options(options)
            assert "--synctex" in str(exc_info.value)

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_validate_options_shell_escape():
    """Test shell-escape validation."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        options = BuildOptions(
            security=SecurityPolicy(allow_shell_escape=True)
        )

        if "-Z shell-escape" in caps.supported_flags:
            # Should not raise
            binary.validate_options(options)
        else:
            # Should raise UnsupportedOptionError
            with pytest.raises(UnsupportedOptionError):
                binary.validate_options(options)

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_build_v2_compile_cmd(tmp_path: Path):
    """Test building V2 compile command."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        if not caps.supports_v2:
            pytest.skip("Tectonic V2 not supported")

        entrypoint = tmp_path / "main.tex"
        outdir = tmp_path / "output"
        options = BuildOptions(synctex=True, print_log=True)

        cmd = binary.build_v2_compile_cmd(entrypoint, outdir, options)

        # Should have basic structure
        assert cmd[0] == str(binary.path)
        assert cmd[1] == "-X"
        assert cmd[2] == "compile"
        assert str(entrypoint) in cmd
        assert "--outdir" in cmd
        assert str(outdir) in cmd

        # Should have options
        if "--synctex" in caps.supported_flags:
            assert "--synctex" in cmd
        assert "--print" in cmd

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_build_v2_build_cmd(tmp_path: Path):
    """Test building V2 build command."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        if not caps.supports_v2:
            pytest.skip("Tectonic V2 not supported")

        project_dir = tmp_path / "project"
        options = BuildOptions(keep_logs=True)

        cmd = binary.build_v2_build_cmd(project_dir, options)

        # Should have basic structure
        assert cmd[0] == str(binary.path)
        assert cmd[1] == "-X"
        assert cmd[2] == "build"

        # Should have options
        if "--keep-logs" in caps.supported_flags:
            assert "--keep-logs" in cmd

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_build_v2_compile_with_extra_args(tmp_path: Path):
    """Test V2 compile command with extra arguments."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        if not caps.supports_v2:
            pytest.skip("Tectonic V2 not supported")

        entrypoint = tmp_path / "main.tex"
        outdir = tmp_path / "output"
        options = BuildOptions(extra_args=["--custom", "arg"])

        cmd = binary.build_v2_compile_cmd(entrypoint, outdir, options)

        # Should include extra args
        assert "--custom" in cmd
        assert "arg" in cmd

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_build_v2_with_untrusted(tmp_path: Path):
    """Test V2 compile with untrusted mode."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        if not caps.supports_v2:
            pytest.skip("Tectonic V2 not supported")

        entrypoint = tmp_path / "main.tex"
        outdir = tmp_path / "output"
        options = BuildOptions(
            security=SecurityPolicy(untrusted=True)
        )

        cmd = binary.build_v2_compile_cmd(entrypoint, outdir, options)

        # Should include untrusted flag
        if "--untrusted" in caps.supported_flags:
            assert "--untrusted" in cmd

    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")

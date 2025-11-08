"""Tests for TectonicBinary."""

import pytest

from b8tex.core.binary import TectonicBinary
from b8tex.exceptions import MissingBinaryError


def test_discover_binary():
    """Test binary discovery."""
    # This will skip if tectonic is not installed
    try:
        binary = TectonicBinary.discover()
        assert binary.path.exists()
    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_probe_capabilities():
    """Test capability probing."""
    try:
        binary = TectonicBinary.discover()
        caps = binary.probe()

        assert caps.version
        assert isinstance(caps.supports_v2, bool)
        assert isinstance(caps.supported_flags, set)
    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")


def test_build_cmd():
    """Test command building."""
    try:
        binary = TectonicBinary.discover()
        cmd = binary.build_cmd(["--version"])

        assert len(cmd) == 2
        assert cmd[0] == str(binary.path)
        assert cmd[1] == "--version"
    except MissingBinaryError:
        pytest.skip("Tectonic binary not found")

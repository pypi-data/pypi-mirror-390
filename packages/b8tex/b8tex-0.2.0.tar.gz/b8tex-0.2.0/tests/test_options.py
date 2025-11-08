"""Tests for build options and configuration."""

import pytest

from b8tex.core.options import BuildOptions, OutputFormat, SecurityPolicy
from b8tex.exceptions import SecurityPolicyError


def test_output_format_enum():
    """Test OutputFormat enum."""
    assert OutputFormat.PDF.value == "pdf"
    assert OutputFormat.HTML.value == "html"
    assert OutputFormat.XDV.value == "xdv"


def test_security_policy_default():
    """Test default security policy."""
    policy = SecurityPolicy()

    assert policy.untrusted is False
    assert policy.allow_shell_escape is False
    assert policy.shell_escape_cwd is None


def test_security_policy_validation():
    """Test security policy validation."""
    # This should raise an error
    with pytest.raises(SecurityPolicyError):
        SecurityPolicy(untrusted=True, allow_shell_escape=True)


def test_build_options_defaults():
    """Test default build options."""
    opts = BuildOptions()

    assert opts.outdir is None
    assert opts.outfmt == OutputFormat.PDF
    assert opts.reruns is None
    assert opts.synctex is False
    assert opts.print_log is False
    assert opts.keep_logs is False
    assert opts.keep_intermediates is False
    assert opts.only_cached is False
    assert opts.extra_args == []
    assert isinstance(opts.security, SecurityPolicy)
    assert opts.env == {}

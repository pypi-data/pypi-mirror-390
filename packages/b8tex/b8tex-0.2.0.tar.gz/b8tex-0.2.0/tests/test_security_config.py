"""Tests for timeouts, retry policies, resource limits, and configuration."""

import os
import tomllib
from unittest.mock import Mock, call, patch

import pytest

from b8tex.core.config import TexConfig, create_default_config, load_config
from b8tex.core.retry import CleanupManager, RetryPolicy, retry_with_policy
from b8tex.core.runner import ResourceLimits
from b8tex.core.timeouts import TimeoutConfig
from b8tex.core.validation import ValidationLimits

# TimeoutConfig Tests


def test_timeout_config_defaults():
    """Test default TimeoutConfig values."""
    config = TimeoutConfig()
    assert config.compilation == 300.0
    assert config.download == 300.0
    assert config.probe == 5.0
    assert config.cache_read == 10.0
    assert config.cache_write == 30.0
    assert config.file_operation == 60.0
    assert config.global_multiplier == 1.0
    assert config.enable_size_scaling is True
    assert config.base_size_kb == 100
    assert config.size_scale_factor == 0.1


def test_timeout_config_custom_values():
    """Test custom TimeoutConfig values."""
    config = TimeoutConfig(
        compilation=600.0,
        download=120.0,
        probe=10.0,
        global_multiplier=2.0,
        enable_size_scaling=False
    )
    assert config.compilation == 600.0
    assert config.download == 120.0
    assert config.probe == 10.0
    assert config.global_multiplier == 2.0
    assert config.enable_size_scaling is False


def test_get_compilation_timeout_basic():
    """Test basic compilation timeout retrieval."""
    config = TimeoutConfig(compilation=450.0)
    timeout = config.get("compilation")
    assert timeout == 450.0


def test_get_download_timeout():
    """Test download timeout retrieval."""
    config = TimeoutConfig(download=180.0)
    timeout = config.get("download")
    assert timeout == 180.0


def test_get_probe_timeout():
    """Test probe timeout retrieval."""
    config = TimeoutConfig(probe=15.0)
    timeout = config.get("probe")
    assert timeout == 15.0


def test_get_cache_operation_timeout():
    """Test cache operation uses max of read/write."""
    config = TimeoutConfig(cache_read=10.0, cache_write=30.0)
    timeout = config.get("cache_operation")
    assert timeout == 30.0  # max(10, 30)


def test_get_file_io_timeout():
    """Test file I/O timeout retrieval."""
    config = TimeoutConfig(file_operation=90.0)
    timeout = config.get("file_io")
    assert timeout == 90.0


def test_get_compilation_size_scaling_enabled():
    """Test document size increases timeout."""
    config = TimeoutConfig(
        compilation=300.0,
        enable_size_scaling=True,
        base_size_kb=100,
        size_scale_factor=0.1
    )
    # 200KB document: base + (200-100)*0.1 = 300 + 10 = 310
    timeout = config.get("compilation", document_size_kb=200)
    assert timeout == 310.0


def test_get_compilation_size_scaling_below_base():
    """Test document smaller than base size doesn't reduce timeout."""
    config = TimeoutConfig(
        compilation=300.0,
        base_size_kb=100,
        size_scale_factor=0.1
    )
    # 50KB document (below base): timeout = base only
    timeout = config.get("compilation", document_size_kb=50)
    assert timeout == 300.0


def test_get_compilation_size_scaling_disabled():
    """Test size parameter ignored when size scaling disabled."""
    config = TimeoutConfig(
        compilation=300.0,
        enable_size_scaling=False,
        size_scale_factor=0.1
    )
    # Even with 1000KB, should return base timeout
    timeout = config.get("compilation", document_size_kb=1000)
    assert timeout == 300.0


def test_get_compilation_size_scaling_none_size():
    """Test document_size_kb=None returns base timeout."""
    config = TimeoutConfig(compilation=300.0)
    timeout = config.get("compilation", document_size_kb=None)
    assert timeout == 300.0


def test_get_non_compilation_ignores_size():
    """Test size parameter ignored for non-compilation operations."""
    config = TimeoutConfig(download=180.0, size_scale_factor=0.1)
    # Download should ignore document size
    timeout = config.get("download", document_size_kb=1000)
    assert timeout == 180.0


def test_get_global_multiplier_applied():
    """Test global multiplier scales all timeouts."""
    config = TimeoutConfig(
        compilation=300.0,
        download=180.0,
        probe=5.0,
        global_multiplier=2.0
    )
    assert config.get("compilation") == 600.0
    assert config.get("download") == 360.0
    assert config.get("probe") == 10.0


def test_get_global_multiplier_with_size_scaling():
    """Test multiplier applied after size scaling."""
    config = TimeoutConfig(
        compilation=300.0,
        global_multiplier=2.0,
        base_size_kb=100,
        size_scale_factor=0.1
    )
    # (300 + (200-100)*0.1) * 2 = 310 * 2 = 620
    timeout = config.get("compilation", document_size_kb=200)
    assert timeout == 620.0


def test_from_env_no_env_vars():
    """Test from_env() returns defaults when no env vars set."""
    with patch.dict(os.environ, {}, clear=True):
        config = TimeoutConfig.from_env()
        assert config.compilation == 300.0
        assert config.download == 300.0
        assert config.global_multiplier == 1.0


def test_from_env_compilation_override():
    """Test B8TEX_TIMEOUT_COMPILATION env var."""
    with patch.dict(os.environ, {"B8TEX_TIMEOUT_COMPILATION": "600"}):
        config = TimeoutConfig.from_env()
        assert config.compilation == 600.0


def test_from_env_download_override():
    """Test B8TEX_TIMEOUT_DOWNLOAD env var."""
    with patch.dict(os.environ, {"B8TEX_TIMEOUT_DOWNLOAD": "120"}):
        config = TimeoutConfig.from_env()
        assert config.download == 120.0


def test_from_env_probe_override():
    """Test B8TEX_TIMEOUT_PROBE env var."""
    with patch.dict(os.environ, {"B8TEX_TIMEOUT_PROBE": "10"}):
        config = TimeoutConfig.from_env()
        assert config.probe == 10.0


def test_from_env_multiplier_override():
    """Test B8TEX_TIMEOUT_MULTIPLIER env var."""
    with patch.dict(os.environ, {"B8TEX_TIMEOUT_MULTIPLIER": "2.5"}):
        config = TimeoutConfig.from_env()
        assert config.global_multiplier == 2.5


def test_from_env_size_scaling_override_true():
    """Test B8TEX_TIMEOUT_SIZE_SCALING='true' enables scaling."""
    with patch.dict(os.environ, {"B8TEX_TIMEOUT_SIZE_SCALING": "true"}):
        config = TimeoutConfig.from_env()
        assert config.enable_size_scaling is True


def test_from_env_size_scaling_override_false():
    """Test B8TEX_TIMEOUT_SIZE_SCALING='false' disables scaling."""
    with patch.dict(os.environ, {"B8TEX_TIMEOUT_SIZE_SCALING": "0"}):
        config = TimeoutConfig.from_env()
        assert config.enable_size_scaling is False


def test_from_env_size_scaling_truthy_values():
    """Test '1', 'yes', 'True' all enable scaling."""
    for value in ["1", "yes", "True"]:
        with patch.dict(os.environ, {"B8TEX_TIMEOUT_SIZE_SCALING": value}):
            config = TimeoutConfig.from_env()
            assert config.enable_size_scaling is True


def test_from_env_invalid_value_ignored():
    """Test invalid float values ignored (don't crash)."""
    with patch.dict(os.environ, {"B8TEX_TIMEOUT_COMPILATION": "invalid"}):
        config = TimeoutConfig.from_env()
        # Should fall back to default
        assert config.compilation == 300.0


def test_validate_valid_config():
    """Test valid config passes validation."""
    config = TimeoutConfig()
    # Should not raise
    config.validate()


def test_validate_negative_compilation():
    """Test negative compilation timeout rejected."""
    config = TimeoutConfig(compilation=-1)
    with pytest.raises(ValueError, match="compilation timeout must be positive"):
        config.validate()


def test_validate_zero_compilation():
    """Test zero compilation timeout rejected."""
    config = TimeoutConfig(compilation=0)
    with pytest.raises(ValueError, match="compilation timeout must be positive"):
        config.validate()


def test_validate_negative_download():
    """Test negative download timeout rejected."""
    config = TimeoutConfig(download=-5)
    with pytest.raises(ValueError, match="download timeout must be positive"):
        config.validate()


def test_validate_negative_probe():
    """Test negative probe timeout rejected."""
    config = TimeoutConfig(probe=-1)
    with pytest.raises(ValueError, match="probe timeout must be positive"):
        config.validate()


def test_validate_negative_multiplier():
    """Test negative global_multiplier rejected."""
    config = TimeoutConfig(global_multiplier=-1)
    with pytest.raises(ValueError, match="global_multiplier must be positive"):
        config.validate()


def test_validate_zero_multiplier():
    """Test zero global_multiplier rejected."""
    config = TimeoutConfig(global_multiplier=0)
    with pytest.raises(ValueError, match="global_multiplier must be positive"):
        config.validate()


def test_validate_negative_scale_factor():
    """Test negative size_scale_factor rejected."""
    config = TimeoutConfig(size_scale_factor=-0.5)
    with pytest.raises(ValueError, match="size_scale_factor must be non-negative"):
        config.validate()


def test_validate_zero_scale_factor_allowed():
    """Test zero size_scale_factor is valid (disables scaling effect)."""
    config = TimeoutConfig(size_scale_factor=0)
    # Should not raise
    config.validate()


# RetryPolicy Tests


def test_retry_policy_defaults():
    """Test default RetryPolicy values."""
    policy = RetryPolicy()
    assert policy.max_attempts == 3
    assert policy.initial_delay == 1.0
    assert policy.max_delay == 30.0
    assert policy.exponential_backoff is True
    assert policy.backoff_factor == 2.0
    assert OSError in policy.retryable_exceptions
    assert IOError in policy.retryable_exceptions
    assert TimeoutError in policy.retryable_exceptions


def test_retry_policy_custom_values():
    """Test custom RetryPolicy values."""
    policy = RetryPolicy(
        max_attempts=5,
        initial_delay=0.5,
        max_delay=10.0,
        backoff_factor=3.0,
        retryable_exceptions=(ValueError,)
    )
    assert policy.max_attempts == 5
    assert policy.initial_delay == 0.5
    assert policy.max_delay == 10.0
    assert policy.backoff_factor == 3.0
    assert policy.retryable_exceptions == (ValueError,)


def test_retry_success_on_first_attempt():
    """Test no retry when operation succeeds immediately."""
    policy = RetryPolicy()
    operation = Mock(return_value="success")

    result = retry_with_policy(policy, operation, "test_op")

    assert result == "success"
    assert operation.call_count == 1


def test_retry_success_on_second_attempt():
    """Test retry after first failure."""
    policy = RetryPolicy(initial_delay=0.01)  # Fast for testing
    operation = Mock(side_effect=[OSError("fail"), "success"])

    with patch("time.sleep"):  # Don't actually sleep
        result = retry_with_policy(policy, operation, "test_op")

    assert result == "success"
    assert operation.call_count == 2


def test_retry_success_on_last_attempt():
    """Test success on final retry."""
    policy = RetryPolicy(max_attempts=3, initial_delay=0.01)
    operation = Mock(side_effect=[OSError("fail1"), OSError("fail2"), "success"])

    with patch("time.sleep"):
        result = retry_with_policy(policy, operation, "test_op")

    assert result == "success"
    assert operation.call_count == 3


def test_retry_all_attempts_fail():
    """Test all retries exhausted, raises last exception."""
    policy = RetryPolicy(max_attempts=3, initial_delay=0.01)
    operation = Mock(side_effect=OSError("always fails"))

    with patch("time.sleep"), pytest.raises(OSError, match="always fails"):
        retry_with_policy(policy, operation, "test_op")

    assert operation.call_count == 3


def test_retry_non_retryable_exception_not_retried():
    """Test non-retryable exceptions raised immediately."""
    policy = RetryPolicy(retryable_exceptions=(OSError,))
    operation = Mock(side_effect=ValueError("not retryable"))

    with pytest.raises(ValueError, match="not retryable"):
        retry_with_policy(policy, operation, "test_op")

    assert operation.call_count == 1


def test_retry_max_attempts_one_no_retry():
    """Test max_attempts=1 means no retry."""
    policy = RetryPolicy(max_attempts=1)
    operation = Mock(side_effect=OSError("fail"))

    with pytest.raises(OSError):
        retry_with_policy(policy, operation, "test_op")

    assert operation.call_count == 1


def test_retry_exponential_backoff_delays():
    """Test delays follow exponential backoff pattern."""
    policy = RetryPolicy(
        max_attempts=4,
        initial_delay=1.0,
        backoff_factor=2.0
    )
    operation = Mock(side_effect=[OSError(), OSError(), OSError(), "success"])

    with patch("time.sleep") as mock_sleep:
        retry_with_policy(policy, operation, "test_op")

    # Should have 3 sleeps: 1.0, 2.0, 4.0
    assert mock_sleep.call_count == 3
    assert mock_sleep.call_args_list[0] == call(1.0)
    assert mock_sleep.call_args_list[1] == call(2.0)
    assert mock_sleep.call_args_list[2] == call(4.0)


def test_retry_exponential_backoff_respects_max_delay():
    """Test delay capped at max_delay."""
    policy = RetryPolicy(
        max_attempts=5,
        initial_delay=10.0,
        max_delay=15.0,
        backoff_factor=2.0
    )
    operation = Mock(side_effect=[OSError()] * 4 + ["success"])

    with patch("time.sleep") as mock_sleep:
        retry_with_policy(policy, operation, "test_op")

    # Delays: 10, 15 (capped), 15 (capped), 15 (capped)
    delays = [args[0] for args, _ in mock_sleep.call_args_list]
    assert all(d <= 15.0 for d in delays)


def test_retry_linear_backoff():
    """Test exponential_backoff=False keeps delay constant."""
    policy = RetryPolicy(
        max_attempts=4,
        initial_delay=2.0,
        exponential_backoff=False
    )
    operation = Mock(side_effect=[OSError()] * 3 + ["success"])

    with patch("time.sleep") as mock_sleep:
        retry_with_policy(policy, operation, "test_op")

    # All delays should be 2.0
    delays = [args[0] for args, _ in mock_sleep.call_args_list]
    assert all(d == 2.0 for d in delays)


# CleanupManager Tests


def test_cleanup_manager_register():
    """Test callbacks can be registered."""
    cleanup = CleanupManager()
    callback = Mock()

    cleanup.register(callback, "test_cleanup")

    assert len(cleanup._cleanup_callbacks) == 1


def test_cleanup_manager_cleanup_lifo_order():
    """Test callbacks executed in reverse order (LIFO)."""
    cleanup = CleanupManager()
    calls = []

    cleanup.register(lambda: calls.append(1), "first")
    cleanup.register(lambda: calls.append(2), "second")
    cleanup.register(lambda: calls.append(3), "third")

    cleanup.cleanup()

    # Should be called in reverse order
    assert calls == [3, 2, 1]


def test_cleanup_manager_cleanup_exception_handling():
    """Test exception in one callback doesn't stop others."""
    cleanup = CleanupManager()
    calls = []

    cleanup.register(lambda: calls.append(1), "first")
    cleanup.register(lambda: (_ for _ in ()).throw(Exception("fail")), "second")
    cleanup.register(lambda: calls.append(3), "third")

    # Should not raise, but all callbacks should run
    cleanup.cleanup()

    assert calls == [3, 1]  # 3 and 1 executed, 2 failed


def test_cleanup_manager_context_no_exception():
    """Test cleanup not run if no exception in context."""
    callback = Mock()

    with CleanupManager() as cleanup:
        cleanup.register(callback, "test")
        # No exception

    # Cleanup should NOT have been called (no exception)
    assert callback.call_count == 0


def test_cleanup_manager_context_with_exception():
    """Test cleanup run when exception occurs in context."""
    callback = Mock()

    try:
        with CleanupManager() as cleanup:
            cleanup.register(callback, "test")
            raise ValueError("test exception")
    except ValueError:
        pass

    # Cleanup should have been called
    assert callback.call_count == 1


def test_cleanup_manager_context_exception_propagated():
    """Test original exception propagated after cleanup."""
    with pytest.raises(ValueError, match="test exception"), CleanupManager() as cleanup:
        cleanup.register(lambda: None, "test")
        raise ValueError("test exception")


# ResourceLimits Tests


def test_resource_limits_defaults():
    """Test default ResourceLimits values."""
    limits = ResourceLimits()
    assert limits.memory_mb == 1024
    assert limits.timeout_seconds == 300.0
    assert limits.max_output_size_mb == 100
    assert limits.cpu_time_seconds is None


def test_resource_limits_custom_values():
    """Test custom ResourceLimits values."""
    limits = ResourceLimits(
        memory_mb=2048,
        timeout_seconds=60.0,
        max_output_size_mb=50,
        cpu_time_seconds=120
    )
    assert limits.memory_mb == 2048
    assert limits.timeout_seconds == 60.0
    assert limits.max_output_size_mb == 50
    assert limits.cpu_time_seconds == 120


def test_resource_limits_unlimited_memory():
    """Test memory_mb=None means unlimited."""
    limits = ResourceLimits(memory_mb=None)
    assert limits.memory_mb is None


# TexConfig Tests


def test_tex_config_defaults():
    """Test default TexConfig values."""
    config = TexConfig()
    assert config.auto_download is True
    assert config.tectonic_version is None
    assert config.binary_path is None
    assert isinstance(config.resource_limits, ResourceLimits)
    assert isinstance(config.timeouts, TimeoutConfig)
    assert config.validation_mode == "permissive"
    assert isinstance(config.validation_limits, ValidationLimits)
    assert config.max_cache_size_mb == 1000
    assert config.max_cache_age_days == 30


def test_tex_config_custom_values():
    """Test custom TexConfig values."""
    custom_limits = ResourceLimits(memory_mb=512)
    config = TexConfig(
        auto_download=False,
        tectonic_version="0.15.0",
        resource_limits=custom_limits,
        validation_mode="strict",
        max_cache_size_mb=500
    )
    assert config.auto_download is False
    assert config.tectonic_version == "0.15.0"
    assert config.resource_limits.memory_mb == 512
    assert config.validation_mode == "strict"
    assert config.max_cache_size_mb == 500


def test_load_config_no_file_uses_defaults():
    """Test missing config file returns defaults."""
    with patch("b8tex.core.config.get_config_path") as mock_get_path:
        mock_path = Mock()
        mock_path.exists.return_value = False
        mock_get_path.return_value = mock_path

        config = load_config()

        assert config.auto_download is True
        assert isinstance(config.resource_limits, ResourceLimits)


def test_create_default_config_creates_file(tmp_path):
    """Test default config file created."""
    config_path = tmp_path / "config.toml"

    create_default_config(config_path)

    assert config_path.exists()
    content = config_path.read_text()
    assert "B8TeX Configuration" in content
    assert "[validation]" in content
    assert "[timeouts]" in content


def test_create_default_config_content(tmp_path):
    """Test file content is valid TOML."""
    config_path = tmp_path / "config.toml"

    create_default_config(config_path)

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    # Should be parseable
    assert "auto_download" in data
    assert "validation" in data
    assert "timeouts" in data


def test_create_default_config_creates_directory(tmp_path):
    """Test parent directory created if doesn't exist."""
    config_path = tmp_path / "subdir" / "config.toml"

    create_default_config(config_path)

    assert config_path.parent.exists()
    assert config_path.exists()

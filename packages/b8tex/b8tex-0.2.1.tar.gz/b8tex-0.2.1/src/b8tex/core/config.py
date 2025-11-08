"""Configuration management for B8TeX."""

from __future__ import annotations

import contextlib
import logging
import tomllib
import warnings
from dataclasses import dataclass, field
from pathlib import Path

from b8tex.core.runner import ResourceLimits
from b8tex.core.timeouts import TimeoutConfig
from b8tex.core.validation import ValidationLimits, ValidationMode

logger = logging.getLogger(__name__)


@dataclass
class TexConfig:
    """B8TeX configuration.

    Attributes:
        auto_download: Whether to automatically download Tectonic if not found
        tectonic_version: Specific Tectonic version to download (None = latest)
        binary_path: Custom path to Tectonic binary (overrides discovery)
        resource_limits: Resource limits for process execution
        timeouts: Timeout configuration for operations
        validation_mode: LaTeX content validation mode (strict/permissive/disabled)
        validation_limits: Limits for LaTeX content validation
        max_cache_size_mb: Maximum cache size in megabytes (default: 1000MB)
        max_cache_age_days: Maximum cache entry age in days (default: 30)
    """

    auto_download: bool = True
    tectonic_version: str | None = None
    binary_path: Path | None = None
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    validation_mode: ValidationMode = "permissive"
    validation_limits: ValidationLimits = field(default_factory=ValidationLimits)
    max_cache_size_mb: int = 1000
    max_cache_age_days: int = 30


def get_config_path() -> Path:
    """Get the path to the B8TeX configuration file.

    Returns:
        Path to config file (~/.b8tex/config.toml)
    """
    import os

    import platformdirs

    # Allow override via environment variable
    env_path = os.environ.get("B8TEX_CONFIG_PATH")
    if env_path:
        return Path(env_path)

    # Use platformdirs for cross-platform config directory
    config_dir = Path(platformdirs.user_config_dir("b8tex", "b8tex"))
    return config_dir / "config.toml"


def load_config() -> TexConfig:
    """Load B8TeX configuration from file and environment.

    Environment variables override config file:
    - B8TEX_NO_AUTO_DOWNLOAD=1: Disable automatic downloads
    - B8TEX_TECTONIC_VERSION: Override Tectonic version
    - TECTONIC_PATH: Custom binary path

    Returns:
        TexConfig instance
    """
    import os

    # Start with defaults
    config = TexConfig()

    # Load from config file if exists
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)

            # Parse basic config
            if "auto_download" in data:
                config.auto_download = bool(data["auto_download"])

            if "tectonic_version" in data:
                config.tectonic_version = str(data["tectonic_version"])

            if "binary_path" in data:
                config.binary_path = Path(data["binary_path"]).expanduser()

            if "max_cache_size_mb" in data:
                config.max_cache_size_mb = int(data["max_cache_size_mb"])

            if "max_cache_age_days" in data:
                config.max_cache_age_days = int(data["max_cache_age_days"])

            # Parse validation config
            if "validation" in data:
                val_data = data["validation"]
                if "mode" in val_data:
                    mode_str = str(val_data["mode"])
                    if mode_str in ("strict", "permissive", "disabled"):
                        config.validation_mode = mode_str  # type: ignore[assignment]
                    else:
                        logger.warning(f"Invalid validation mode '{mode_str}', using default")

                if "limits" in val_data:
                    lim = val_data["limits"]
                    config.validation_limits = ValidationLimits(
                        max_file_size=lim.get("max_file_size", config.validation_limits.max_file_size),
                        max_total_size=lim.get("max_total_size", config.validation_limits.max_total_size),
                        max_nesting_depth=lim.get("max_nesting_depth", config.validation_limits.max_nesting_depth),
                        max_files=lim.get("max_files", config.validation_limits.max_files),
                        allow_shell_escape=lim.get("allow_shell_escape", config.validation_limits.allow_shell_escape),
                        dangerous_packages=set(lim.get("dangerous_packages", [])) if "dangerous_packages" in lim else config.validation_limits.dangerous_packages,
                        allowed_packages_only=set(lim.get("allowed_packages_only", [])) if "allowed_packages_only" in lim else None,
                    )

            # Parse resource limits
            if "resource_limits" in data:
                res_data = data["resource_limits"]
                config.resource_limits = ResourceLimits(
                    memory_mb=res_data.get("memory_mb", config.resource_limits.memory_mb),
                    timeout_seconds=res_data.get("timeout_seconds", config.resource_limits.timeout_seconds),
                    max_output_size_mb=res_data.get("max_output_size_mb", config.resource_limits.max_output_size_mb),
                    cpu_time_seconds=res_data.get("cpu_time_seconds", config.resource_limits.cpu_time_seconds),
                )

            # Parse timeouts
            if "timeouts" in data:
                time_data = data["timeouts"]
                config.timeouts = TimeoutConfig(
                    compilation=time_data.get("compilation", config.timeouts.compilation),
                    download=time_data.get("download", config.timeouts.download),
                    probe=time_data.get("probe", config.timeouts.probe),
                    cache_read=time_data.get("cache_read", config.timeouts.cache_read),
                    cache_write=time_data.get("cache_write", config.timeouts.cache_write),
                    file_operation=time_data.get("file_operation", config.timeouts.file_operation),
                    global_multiplier=time_data.get("global_multiplier", config.timeouts.global_multiplier),
                    enable_size_scaling=time_data.get("enable_size_scaling", config.timeouts.enable_size_scaling),
                    base_size_kb=time_data.get("base_size_kb", config.timeouts.base_size_kb),
                    size_scale_factor=time_data.get("size_scale_factor", config.timeouts.size_scale_factor),
                )

        except tomllib.TOMLDecodeError as e:
            # Warn about invalid TOML syntax
            logger.warning(f"Failed to parse config file {config_path}: {e}", exc_info=True)
            warnings.warn(
                f"B8TeX config file has invalid TOML syntax and will be ignored: {config_path}",
                UserWarning,
                stacklevel=2,
            )
        except (OSError, ValueError) as e:
            # Warn about file access or value errors
            logger.warning(f"Error reading config file {config_path}: {e}", exc_info=True)
            warnings.warn(
                f"B8TeX config file could not be read and will be ignored: {config_path}",
                UserWarning,
                stacklevel=2,
            )

    # Environment variables override config file
    if os.environ.get("B8TEX_NO_AUTO_DOWNLOAD"):
        config.auto_download = False

    if version := os.environ.get("B8TEX_TECTONIC_VERSION"):
        config.tectonic_version = version

    if path := os.environ.get("TECTONIC_PATH"):
        config.binary_path = Path(path)

    # Validation mode
    if val_mode := os.environ.get("B8TEX_VALIDATION_MODE"):
        if val_mode in ("strict", "permissive", "disabled"):
            config.validation_mode = val_mode  # type: ignore[assignment]
        else:
            logger.warning(f"Invalid validation mode '{val_mode}', ignoring")

    # Timeout overrides (TimeoutConfig.from_env() handles B8TEX_TIMEOUT_* variables)
    env_timeouts = TimeoutConfig.from_env()
    if env_timeouts.compilation != config.timeouts.compilation:
        config.timeouts.compilation = env_timeouts.compilation
    if env_timeouts.download != config.timeouts.download:
        config.timeouts.download = env_timeouts.download
    if env_timeouts.probe != config.timeouts.probe:
        config.timeouts.probe = env_timeouts.probe
    if env_timeouts.global_multiplier != 1.0:
        config.timeouts.global_multiplier = env_timeouts.global_multiplier
    if env_timeouts.enable_size_scaling != config.timeouts.enable_size_scaling:
        config.timeouts.enable_size_scaling = env_timeouts.enable_size_scaling

    # Resource limit overrides
    if memory := os.environ.get("B8TEX_MEMORY_LIMIT_MB"):
        with contextlib.suppress(ValueError):
            config.resource_limits.memory_mb = int(memory)

    if cpu_time := os.environ.get("B8TEX_CPU_TIME_LIMIT"):
        with contextlib.suppress(ValueError):
            config.resource_limits.cpu_time_seconds = int(cpu_time)

    # Cache limits
    if cache_size := os.environ.get("B8TEX_MAX_CACHE_SIZE_MB"):
        with contextlib.suppress(ValueError):
            config.max_cache_size_mb = int(cache_size)

    if cache_age := os.environ.get("B8TEX_MAX_CACHE_AGE_DAYS"):
        with contextlib.suppress(ValueError):
            config.max_cache_age_days = int(cache_age)

    return config


def create_default_config(path: Path | None = None) -> None:
    """Create a default configuration file with comments.

    Args:
        path: Path to config file (defaults to standard location)
    """
    if path is None:
        path = get_config_path()

    # Create directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    config_content = """# B8TeX Configuration
# See https://github.com/samehkamaleldin/pytex for documentation

# Automatically download Tectonic binary if not found
# Can be overridden with B8TEX_NO_AUTO_DOWNLOAD=1 environment variable
auto_download = true

# Specific Tectonic version to download (leave commented for latest stable)
# Can be overridden with B8TEX_TECTONIC_VERSION environment variable
# tectonic_version = "0.15.0"

# Custom path to Tectonic binary (overrides automatic discovery)
# Can be overridden with TECTONIC_PATH environment variable
# binary_path = "/usr/local/bin/tectonic"

# Cache configuration
max_cache_size_mb = 1000  # Maximum cache size in MB
max_cache_age_days = 30   # Maximum age of cache entries in days

# Security and validation settings
[validation]
mode = "permissive"  # Options: "strict", "permissive", "disabled"

[validation.limits]
max_file_size = 10485760      # 10MB in bytes
max_total_size = 52428800     # 50MB in bytes
max_nesting_depth = 20        # Maximum include/input nesting
max_files = 100               # Maximum number of files in a document
allow_shell_escape = false    # Allow packages like minted, pythontex

# Dangerous packages that require shell-escape (only checked when allow_shell_escape = false)
# dangerous_packages = ["shellesc", "minted", "pythontex", "sagetex", "write18"]

# Whitelist mode: only allow specific packages (leave commented to allow all)
# allowed_packages_only = ["amsmath", "graphicx", "hyperref"]

# Resource limits for process execution
[resource_limits]
memory_mb = 1024              # Maximum memory per process (1GB)
timeout_seconds = 300.0       # Maximum execution time (5 minutes)
max_output_size_mb = 100      # Maximum stdout/stderr size
# cpu_time_seconds = 300      # Maximum CPU time (Unix only)

# Timeout configuration for different operations
[timeouts]
compilation = 300.0           # LaTeX compilation timeout
download = 300.0              # Binary download timeout
probe = 5.0                   # Binary capability probe timeout
cache_read = 10.0             # Cache read timeout
cache_write = 30.0            # Cache write timeout
file_operation = 60.0         # File I/O timeout
global_multiplier = 1.0       # Multiply all timeouts by this factor
enable_size_scaling = true    # Scale compilation timeout by document size
base_size_kb = 100            # Base document size for timeout calculation
size_scale_factor = 0.1       # Additional seconds per KB above base size
"""

    path.write_text(config_content)

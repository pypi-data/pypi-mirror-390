"""Centralized timeout configuration for B8TeX operations."""

from __future__ import annotations

import contextlib
import os
from dataclasses import dataclass
from typing import Literal

OperationType = Literal[
    "compilation",
    "download",
    "probe",
    "cache_operation",
    "file_io",
]


@dataclass
class TimeoutConfig:
    """Centralized timeout configuration.

    All timeouts are in seconds. The configuration supports:
    - Per-operation timeouts for different types of operations
    - Document size-based scaling for compilation timeouts
    - Global multiplier for adjusting all timeouts (useful for slow systems)
    - Environment variable overrides

    Attributes:
        compilation: Timeout for LaTeX compilation (default: 5 minutes)
        download: Timeout for downloading binaries (default: 5 minutes)
        probe: Timeout for probing binary capabilities (default: 5 seconds)
        cache_read: Timeout for reading from cache (default: 10 seconds)
        cache_write: Timeout for writing to cache (default: 30 seconds)
        file_operation: Timeout for individual file operations (default: 1 minute)
        global_multiplier: Multiplier applied to all timeouts (default: 1.0)
        enable_size_scaling: Enable document size-based timeout scaling
        base_size_kb: Base document size for timeout calculations
        size_scale_factor: Additional seconds per KB above base size

    Example:
        >>> config = TimeoutConfig(compilation=600.0)  # 10 minutes
        >>> timeout = config.get("compilation")  # Returns 600.0
        >>> # For a 500KB document with size scaling:
        >>> timeout = config.get("compilation", document_size_kb=500)
    """

    compilation: float = 300.0
    download: float = 300.0
    probe: float = 5.0
    cache_read: float = 10.0
    cache_write: float = 30.0
    file_operation: float = 60.0
    global_multiplier: float = 1.0
    enable_size_scaling: bool = True
    base_size_kb: int = 100
    size_scale_factor: float = 0.1

    def get(
        self,
        operation: OperationType,
        *,
        document_size_kb: int | None = None,
    ) -> float:
        """Get effective timeout for an operation.

        Args:
            operation: Type of operation
            document_size_kb: Document size in KB for size-based scaling

        Returns:
            Effective timeout in seconds

        Example:
            >>> config = TimeoutConfig()
            >>> config.get("compilation")
            300.0
            >>> config.get("compilation", document_size_kb=200)
            310.0  # Base + 100KB extra * 0.1s/KB
        """
        # Get base timeout for operation
        base_timeout = {
            "compilation": self.compilation,
            "download": self.download,
            "probe": self.probe,
            "cache_operation": max(self.cache_read, self.cache_write),
            "file_io": self.file_operation,
        }[operation]

        # Apply size scaling for compilation if enabled
        if (
            operation == "compilation"
            and self.enable_size_scaling
            and document_size_kb is not None
        ):
            extra_kb = max(0, document_size_kb - self.base_size_kb)
            base_timeout += extra_kb * self.size_scale_factor

        # Apply global multiplier
        return base_timeout * self.global_multiplier

    @classmethod
    def from_env(cls) -> TimeoutConfig:
        """Load timeout configuration from environment variables.

        Supported environment variables:
            B8TEX_TIMEOUT_COMPILATION: Compilation timeout in seconds
            B8TEX_TIMEOUT_DOWNLOAD: Download timeout in seconds
            B8TEX_TIMEOUT_PROBE: Binary probe timeout in seconds
            B8TEX_TIMEOUT_MULTIPLIER: Global timeout multiplier

        Returns:
            TimeoutConfig instance with environment overrides

        Example:
            >>> os.environ["B8TEX_TIMEOUT_MULTIPLIER"] = "2.0"
            >>> config = TimeoutConfig.from_env()
            >>> config.global_multiplier
            2.0
        """
        config = cls()

        if val := os.getenv("B8TEX_TIMEOUT_COMPILATION"):
            with contextlib.suppress(ValueError):
                config.compilation = float(val)

        if val := os.getenv("B8TEX_TIMEOUT_DOWNLOAD"):
            with contextlib.suppress(ValueError):
                config.download = float(val)

        if val := os.getenv("B8TEX_TIMEOUT_PROBE"):
            with contextlib.suppress(ValueError):
                config.probe = float(val)

        if val := os.getenv("B8TEX_TIMEOUT_MULTIPLIER"):
            with contextlib.suppress(ValueError):
                config.global_multiplier = float(val)

        if val := os.getenv("B8TEX_TIMEOUT_SIZE_SCALING"):
            config.enable_size_scaling = val.lower() in ("true", "1", "yes")

        return config

    def validate(self) -> None:
        """Validate timeout configuration values.

        Raises:
            ValueError: If any timeout value is invalid
        """
        if self.compilation <= 0:
            raise ValueError("compilation timeout must be positive")
        if self.download <= 0:
            raise ValueError("download timeout must be positive")
        if self.probe <= 0:
            raise ValueError("probe timeout must be positive")
        if self.global_multiplier <= 0:
            raise ValueError("global_multiplier must be positive")
        if self.size_scale_factor < 0:
            raise ValueError("size_scale_factor must be non-negative")

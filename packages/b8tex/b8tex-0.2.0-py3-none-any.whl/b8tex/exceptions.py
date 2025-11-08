"""Exception classes for B8TeX."""

from typing import Any


class TexError(Exception):
    """Base exception for all B8TeX errors."""

    pass


class MissingBinaryError(TexError):
    """Raised when the Tectonic binary cannot be found."""

    def __init__(
        self, message: str | None = None, auto_download_attempted: bool = False
    ) -> None:
        if message is None:
            if auto_download_attempted:
                message = (
                    "Tectonic binary not found and automatic download failed.\n\n"
                    "Please install Tectonic manually:\n"
                    "  - macOS: brew install tectonic\n"
                    "  - Linux: See https://tectonic-typesetting.github.io/install.html\n"
                    "  - Windows: See https://tectonic-typesetting.github.io/install.html\n\n"
                    "Or try manual download with: b8tex install-binary\n\n"
                    "You can also set TECTONIC_PATH environment variable to point to "
                    "an existing Tectonic installation."
                )
            else:
                message = (
                    "Tectonic binary not found.\n\n"
                    "Automatic download is disabled. To enable it:\n"
                    "  1. Remove B8TEX_NO_AUTO_DOWNLOAD environment variable, or\n"
                    "  2. Edit ~/.b8tex/config.toml and set auto_download = true, or\n"
                    "  3. Manually download with: b8tex install-binary\n\n"
                    "Alternatively, install Tectonic manually:\n"
                    "  - macOS: brew install tectonic\n"
                    "  - Linux: See https://tectonic-typesetting.github.io/install.html\n"
                    "  - Windows: See https://tectonic-typesetting.github.io/install.html"
                )
        super().__init__(message)
        self.auto_download_attempted = auto_download_attempted


class CompilationFailed(TexError):
    """Raised when LaTeX compilation fails."""

    def __init__(
        self,
        message: str,
        errors: list[Any] | None = None,
        log_tail: str | None = None,
        returncode: int | None = None,
    ) -> None:
        super().__init__(message)
        self.errors = errors or []
        self.log_tail = log_tail
        self.returncode = returncode


class UnsupportedOptionError(TexError):
    """Raised when a build option is not supported by the installed Tectonic version."""

    def __init__(
        self,
        flag: str,
        required_version: str,
        detected_version: str,
    ) -> None:
        message = (
            f"Option '{flag}' requires Tectonic {required_version} "
            f"but detected version {detected_version}"
        )
        super().__init__(message)
        self.flag = flag
        self.required_version = required_version
        self.detected_version = detected_version


class WorkspaceError(TexError):
    """Raised when there's an error setting up or managing the build workspace."""

    pass


class SecurityPolicyError(TexError):
    """Raised when a security policy constraint is violated."""

    pass


class TimeoutExpired(TexError):
    """Raised when a compilation process exceeds the timeout."""

    def __init__(self, timeout: float) -> None:
        super().__init__(f"Compilation timed out after {timeout} seconds")
        self.timeout = timeout


class ResourceLimitExceeded(TexError):
    """Raised when a process exceeds resource limits."""

    def __init__(
        self,
        message: str,
        limit_type: str | None = None,
        limit_value: int | float | None = None,
        actual_value: int | float | None = None,
    ) -> None:
        super().__init__(message)
        self.limit_type = limit_type
        self.limit_value = limit_value
        self.actual_value = actual_value


class DownloadError(TexError):
    """Raised when downloading the Tectonic binary fails."""

    def __init__(self, message: str, url: str | None = None, cause: Exception | None = None) -> None:
        full_message = f"Failed to download Tectonic binary: {message}"
        if url:
            full_message += f"\nURL: {url}"
        if cause:
            full_message += f"\nCause: {cause}"
        full_message += "\n\nYou can try again with: b8tex install-binary --force"
        super().__init__(full_message)
        self.url = url
        self.cause = cause


class UnsupportedPlatformError(TexError):
    """Raised when the current platform is not supported for binary downloads."""

    def __init__(self, platform: str, arch: str) -> None:
        message = (
            f"Unsupported platform: {platform} ({arch})\n\n"
            "Automatic binary download is not available for your platform.\n"
            "Please install Tectonic manually:\n"
            "  - See https://tectonic-typesetting.github.io/install.html"
        )
        super().__init__(message)
        self.platform = platform
        self.arch = arch

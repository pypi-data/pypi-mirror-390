"""Tectonic binary discovery and management."""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from b8tex.exceptions import (
    DownloadError,
    MissingBinaryError,
    UnsupportedOptionError,
    UnsupportedPlatformError,
)

if TYPE_CHECKING:
    from b8tex.core.options import BuildOptions

# Module-level constants
DEFAULT_TECTONIC_VERSION = "0.15.0"
MAX_DOWNLOAD_SIZE_BYTES = 100 * 1024 * 1024  # 100MB
DOWNLOAD_TIMEOUT_SECONDS = 300  # 5 minutes
PROBE_TIMEOUT_SECONDS = 5.0
BINARY_EXECUTABLE_MODE = 0o755

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class Capabilities:
    """Capabilities of a Tectonic binary.

    Attributes:
        version: Semantic version string
        supports_v2: Whether V2 interface (-X compile/build) is available
        supported_flags: Set of supported command-line flags
    """

    version: str
    supports_v2: bool = False
    supported_flags: set[str] = field(default_factory=set)


@dataclass
class TectonicBinary:
    """Represents a Tectonic executable.

    Attributes:
        path: Path to the tectonic binary
        capabilities: Binary capabilities (version, features, etc.)
    """

    path: Path
    capabilities: Capabilities | None = None

    @classmethod
    def _get_cache_dir(cls) -> Path:
        """Get the cache directory for Tectonic binaries.

        Returns:
            Path to cache directory
        """
        import platformdirs

        cache = Path(platformdirs.user_cache_dir("b8tex", "b8tex"))
        cache.mkdir(parents=True, exist_ok=True)
        return cache

    @classmethod
    def _detect_platform(cls) -> tuple[str, str]:
        """Detect OS and architecture.

        Returns:
            Tuple of (system, arch) e.g. ('linux', 'x86_64')

        Raises:
            UnsupportedPlatformError: If platform is not supported
        """
        import platform

        system = platform.system().lower()
        machine = platform.machine().lower()

        # Normalize system name
        if system == "darwin":
            system = "macos"

        # Normalize architecture
        if machine in ("amd64", "x86_64"):
            arch = "x86_64"
        elif machine in ("arm64", "aarch64"):
            arch = "aarch64"
        else:
            raise UnsupportedPlatformError(system, machine)

        # Verify supported platform
        supported = {
            ("linux", "x86_64"),
            ("linux", "aarch64"),
            ("macos", "x86_64"),
            ("macos", "aarch64"),
            ("windows", "x86_64"),
        }

        if (system, arch) not in supported:
            raise UnsupportedPlatformError(system, arch)

        return system, arch

    @classmethod
    def _get_download_url(cls, version: str = DEFAULT_TECTONIC_VERSION) -> str:
        """Get download URL for Tectonic binary.

        Args:
            version: Tectonic version to download (must be semantic version format)

        Returns:
            Download URL for the platform

        Raises:
            ValueError: If version format is invalid
            UnsupportedPlatformError: If platform is not supported
        """
        # Validate version format (semantic versioning: X.Y.Z)
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            raise ValueError(
                f"Invalid version format: {version}. Must be semantic version (e.g., 0.15.0)"
            )

        system, arch = cls._detect_platform()
        base = "https://github.com/tectonic-typesetting/tectonic/releases/download"

        # Map to actual GitHub release asset names
        if system == "linux":
            platform_str = f"{arch}-unknown-linux-gnu"
            ext = "tar.gz"
        elif system == "macos":
            platform_str = f"{arch}-apple-darwin"
            ext = "tar.gz"
        elif system == "windows":
            platform_str = f"{arch}-pc-windows-msvc"
            ext = "zip"
        else:
            raise UnsupportedPlatformError(system, arch)

        filename = f"tectonic-{version}-{platform_str}.{ext}"
        return f"{base}/tectonic@{version}/{filename}"

    @classmethod
    def _is_windows(cls) -> bool:
        """Check if running on Windows platform.

        Returns:
            True if Windows, False otherwise
        """
        import platform

        return platform.system() == "Windows"

    @classmethod
    def _validate_extracted_path(cls, member_path: str, target_dir: Path) -> Path:
        """Validate that extracted path is safe and within target directory.

        Args:
            member_path: Path from archive member
            target_dir: Target extraction directory

        Returns:
            Validated absolute path

        Raises:
            DownloadError: If path is unsafe (path traversal attempt)
        """
        # Resolve absolute paths
        target_dir_abs = target_dir.resolve()
        member_path_abs = (target_dir / member_path).resolve()

        # Ensure the extracted path is within target directory using is_relative_to()
        try:
            member_path_abs.relative_to(target_dir_abs)
        except ValueError:
            raise DownloadError(
                f"Archive contains unsafe path: {member_path}",
                url=None,
                cause=None,
            ) from None

        return member_path_abs

    @classmethod
    def _download_with_validation(
        cls, url: str, target_path: Path, timeout: int = DOWNLOAD_TIMEOUT_SECONDS
    ) -> None:
        """Download file with size and timeout validation.

        Args:
            url: URL to download from
            target_path: Where to save the file
            timeout: Timeout in seconds

        Raises:
            DownloadError: If download fails or violates constraints
        """
        import urllib.error
        import urllib.request

        try:
            # Create request with timeout
            req = urllib.request.Request(url, headers={"User-Agent": "b8tex/0.1.0"})

            with urllib.request.urlopen(req, timeout=timeout) as response:
                # Validate content type
                content_type = response.headers.get("Content-Type", "")
                if not any(
                    ct in content_type
                    for ct in ["application/", "binary/", "octet-stream"]
                ):
                    logger.warning(f"Unexpected content type: {content_type}")

                # Check file size
                content_length = response.headers.get("Content-Length")
                if content_length:
                    size = int(content_length)
                    if size > MAX_DOWNLOAD_SIZE_BYTES:
                        raise DownloadError(
                            f"File too large: {size} bytes (max {MAX_DOWNLOAD_SIZE_BYTES})",
                            url=url,
                            cause=None,
                        )

                # Download in chunks with size tracking
                downloaded = 0
                with open(target_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break

                        downloaded += len(chunk)
                        if downloaded > MAX_DOWNLOAD_SIZE_BYTES:
                            raise DownloadError(
                                f"Download exceeded size limit: {MAX_DOWNLOAD_SIZE_BYTES} bytes",
                                url=url,
                                cause=None,
                            )

                        f.write(chunk)

                logger.debug(f"Downloaded {downloaded} bytes from {url}")

        except TimeoutError as e:
            raise DownloadError("Download timed out", url=url, cause=e) from e
        except urllib.error.HTTPError as e:
            raise DownloadError(f"HTTP error {e.code}: {e.reason}", url=url, cause=e) from e
        except urllib.error.URLError as e:
            raise DownloadError("Network error", url=url, cause=e) from e

    @classmethod
    def _download_binary(cls, version: str = DEFAULT_TECTONIC_VERSION, force: bool = False) -> Path:
        """Download Tectonic binary to cache with security validations.

        Args:
            version: Version to download
            force: Force re-download even if cached

        Returns:
            Path to downloaded binary

        Raises:
            DownloadError: If download fails
            UnsupportedPlatformError: If platform is not supported
            ValueError: If version format is invalid
        """
        import tarfile
        import tempfile
        import zipfile

        cache_dir = cls._get_cache_dir()
        binary_name = "tectonic.exe" if cls._is_windows() else "tectonic"
        target_path = cache_dir / binary_name
        lock_path = cache_dir / ".tectonic.lock"

        # Use lock file to prevent concurrent downloads
        try:
            # Create lock file (platform-independent approach)
            if not force and target_path.exists():
                logger.debug(f"Using cached binary at {target_path}")
                return target_path

            # Simple file-based locking (works cross-platform)
            try:
                # Try to create lock file exclusively
                lock_fd = os.open(
                    lock_path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                )
                os.close(lock_fd)
                logger.debug("Acquired download lock")
            except FileExistsError:
                # Another process is downloading, wait a bit and check again
                import time

                logger.info("Another process is downloading, waiting...")
                for _ in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    if target_path.exists():
                        logger.info("Binary downloaded by another process")
                        return target_path
                # If still not available, proceed anyway (lock might be stale)
                logger.warning("Download lock exists but binary not found, proceeding...")

            url = cls._get_download_url(version)
            logger.info(f"Downloading Tectonic {version}...")
            logger.info(f"From: {url}")

            # Download to temp file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".download", dir=cache_dir
            ) as tmp:
                tmp_path = Path(tmp.name)

            try:
                # Download with validation
                cls._download_with_validation(url, tmp_path)

                # Validate downloaded file size
                file_size = tmp_path.stat().st_size
                if file_size == 0:
                    raise DownloadError("Downloaded file is empty", url=url, cause=None)

                logger.debug(f"Downloaded file size: {file_size} bytes")

                # Extract binary from archive
                binary_found = False
                if url.endswith(".tar.gz"):
                    with tarfile.open(tmp_path, "r:gz") as archive:
                        # Extract tectonic binary
                        for member in archive.getmembers():
                            if member.name.endswith("tectonic") and not member.isdir():
                                # Validate path safety
                                cls._validate_extracted_path(member.name, cache_dir)

                                # Extract to temporary name first
                                temp_extract_path = cache_dir / f".{binary_name}.tmp"
                                src = archive.extractfile(member)
                                if src:
                                    with src, open(temp_extract_path, "wb") as dst:
                                        dst.write(src.read())

                                # Atomic rename
                                temp_extract_path.rename(target_path)
                                binary_found = True
                                break

                elif url.endswith(".zip"):
                    with zipfile.ZipFile(tmp_path) as archive:
                        # Extract tectonic.exe
                        for name in archive.namelist():
                            if name.endswith("tectonic.exe") or name.endswith("tectonic"):
                                # Validate path safety
                                cls._validate_extracted_path(name, cache_dir)

                                # Extract to temporary name first
                                temp_extract_path = cache_dir / f".{binary_name}.tmp"
                                with archive.open(name) as src:
                                    with open(temp_extract_path, "wb") as dst:
                                        dst.write(src.read())

                                # Atomic rename
                                temp_extract_path.rename(target_path)
                                binary_found = True
                                break

                if not binary_found:
                    raise DownloadError(
                        "Binary not found in archive",
                        url=url,
                        cause=None,
                    )

                # Make executable (Unix-like systems)
                if not cls._is_windows():
                    target_path.chmod(BINARY_EXECUTABLE_MODE)

                logger.info(f"Successfully downloaded to: {target_path}")
                return target_path

            except (tarfile.TarError, zipfile.BadZipFile) as e:
                raise DownloadError("Archive extraction failed", url=url, cause=e) from e
            finally:
                # Clean up temp files
                tmp_path.unlink(missing_ok=True)
                temp_extract = cache_dir / f".{binary_name}.tmp"
                temp_extract.unlink(missing_ok=True)

        finally:
            # Remove lock file
            lock_path.unlink(missing_ok=True)

    @classmethod
    def discover(cls, env_var: str = "TECTONIC_PATH") -> TectonicBinary:
        """Discover the Tectonic binary with auto-download support.

        Args:
            env_var: Environment variable to check first

        Returns:
            TectonicBinary instance

        Raises:
            MissingBinaryError: If binary cannot be found
        """
        from b8tex.core.config import load_config

        # Load configuration
        config = load_config()

        # 1. Check custom binary path from config
        if (
            config.binary_path
            and config.binary_path.is_file()
            and os.access(config.binary_path, os.X_OK)
        ):
            return cls(path=config.binary_path)

        # 2. Check environment variable
        env_path = os.environ.get(env_var)
        if env_path:
            binary_path = Path(env_path)
            if binary_path.is_file() and os.access(binary_path, os.X_OK):
                return cls(path=binary_path)

        # 3. Search in PATH
        binary_name = "tectonic"
        found = shutil.which(binary_name)
        if found:
            return cls(path=Path(found))

        # 4. Check cache directory
        cache_dir = cls._get_cache_dir()
        cached_binary = cache_dir / ("tectonic.exe" if cls._is_windows() else "tectonic")
        if cached_binary.exists() and os.access(cached_binary, os.X_OK):
            return cls(path=cached_binary)

        # 5. Auto-download if enabled
        if config.auto_download:
            try:
                version = config.tectonic_version or DEFAULT_TECTONIC_VERSION
                binary_path = cls._download_binary(version=version)
                return cls(path=binary_path)
            except (DownloadError, UnsupportedPlatformError, ValueError) as e:
                # Log the error and fall through
                logger.warning(f"Auto-download failed: {e}")

        # 6. Raise helpful error
        raise MissingBinaryError(auto_download_attempted=config.auto_download)

    def probe(self) -> Capabilities:
        """Probe the binary to determine its capabilities.

        Returns:
            Capabilities object

        Raises:
            MissingBinaryError: If binary cannot be executed
        """
        try:
            result = subprocess.run(
                [str(self.path), "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=PROBE_TIMEOUT_SECONDS,
            )

            if result.returncode != 0:
                raise MissingBinaryError(
                    f"Failed to execute {self.path}: {result.stderr}"
                )

            # Parse version from output like "Tectonic 0.14.1"
            version = "unknown"
            for line in result.stdout.splitlines():
                if "Tectonic" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        version = parts[1]
                    break

            # Check for V2 support by running help
            help_result = subprocess.run(
                [str(self.path), "--help"],
                capture_output=True,
                text=True,
                check=False,
                timeout=PROBE_TIMEOUT_SECONDS,
            )

            help_text = help_result.stdout

            supports_v2 = "-X" in help_text

            # Comprehensive flag detection
            supported_flags = set()

            # Common flags
            flags_to_check = [
                "--synctex",
                "--untrusted",
                "--keep-logs",
                "--keep-intermediates",
                "--reruns",
                "--print",
                "--outdir",
                "--outfmt",
                "--bundle",
                "--only-cached",
                "-Z shell-escape",
                "-Z shell-escape-cwd",
            ]

            for flag in flags_to_check:
                if flag in help_text:
                    supported_flags.add(flag)

            caps = Capabilities(
                version=version,
                supports_v2=supports_v2,
                supported_flags=supported_flags,
            )
            self.capabilities = caps
            return caps

        except subprocess.TimeoutExpired as e:
            raise MissingBinaryError(f"Tectonic binary timed out: {e}") from e
        except Exception as e:
            raise MissingBinaryError(f"Failed to probe Tectonic binary: {e}") from e

    def build_cmd(self, args: list[str]) -> list[str]:
        """Build a command line for execution.

        Args:
            args: Arguments to pass to tectonic

        Returns:
            Complete command as list of strings
        """
        return [str(self.path), *args]

    def interface_for(self, project_dir: Path | None = None) -> Literal["v1", "v2"]:
        """Determine which interface (V1/V2) to use.

        Args:
            project_dir: Project directory (to check for Tectonic.toml)

        Returns:
            'v1' or 'v2'
        """
        if not self.capabilities:
            self.probe()

        # Use V2 if available and Tectonic.toml exists
        if self.capabilities and self.capabilities.supports_v2 and project_dir:
            toml_path = project_dir / "Tectonic.toml"
            if toml_path.exists():
                return "v2"

        return "v1"

    def validate_options(self, options: BuildOptions) -> None:
        """Validate that build options are supported by this binary.

        Args:
            options: Build options to validate

        Raises:
            UnsupportedOptionError: If an option is not supported
        """
        if not self.capabilities:
            self.probe()

        # At this point capabilities should be set, but check defensively
        if self.capabilities is None:
            raise MissingBinaryError("Failed to probe binary capabilities")

        # Check synctex
        if options.synctex and "--synctex" not in self.capabilities.supported_flags:
            raise UnsupportedOptionError(
                flag="--synctex",
                required_version="0.1.11+",
                detected_version=self.capabilities.version,
            )

        # Check keep-logs
        if options.keep_logs and "--keep-logs" not in self.capabilities.supported_flags:
            raise UnsupportedOptionError(
                flag="--keep-logs",
                required_version="0.1.11+",
                detected_version=self.capabilities.version,
            )

        # Check keep-intermediates
        if (
            options.keep_intermediates
            and "--keep-intermediates" not in self.capabilities.supported_flags
        ):
            raise UnsupportedOptionError(
                flag="--keep-intermediates",
                required_version="0.1.11+",
                detected_version=self.capabilities.version,
            )

        # Check shell-escape
        if (
            options.security.allow_shell_escape
            and "-Z shell-escape" not in self.capabilities.supported_flags
        ):
            raise UnsupportedOptionError(
                flag="-Z shell-escape",
                required_version="0.1.12+",
                detected_version=self.capabilities.version,
            )

    def build_v2_compile_cmd(
        self,
        entrypoint: Path,
        outdir: Path,
        options: BuildOptions,
    ) -> list[str]:
        """Build a V2 compile command.

        Args:
            entrypoint: Path to .tex file
            outdir: Output directory
            options: Build options

        Returns:
            Command as list of strings
        """
        cmd = [str(self.path), "-X", "compile", str(entrypoint)]

        # Output options
        cmd.extend(["--outdir", str(outdir)])

        # Add other common options
        if options.synctex:
            cmd.append("--synctex")

        if options.print_log:
            cmd.append("--print")

        if options.keep_logs:
            cmd.append("--keep-logs")

        if options.security.untrusted:
            cmd.append("--untrusted")

        # Extra arguments
        cmd.extend(options.extra_args)

        return cmd

    def build_v2_build_cmd(
        self,
        project_dir: Path,  # noqa: ARG002
        options: BuildOptions,
    ) -> list[str]:
        """Build a V2 build command (uses Tectonic.toml).

        Args:
            project_dir: Project directory (not used, caller sets cwd)
            options: Build options

        Returns:
            Command as list of strings
        """
        cmd = [str(self.path), "-X", "build"]

        # Change to project directory (V2 build works from project root)
        # Note: Caller should set cwd=project_dir when running

        # Add common options
        if options.print_log:
            cmd.append("--print")

        if options.keep_logs:
            cmd.append("--keep-logs")

        # Extra arguments
        cmd.extend(options.extra_args)

        return cmd

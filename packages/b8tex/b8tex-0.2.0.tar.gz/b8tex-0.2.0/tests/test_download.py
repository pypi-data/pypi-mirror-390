"""Tests for Tectonic binary download functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from b8tex.core.binary import TectonicBinary
from b8tex.core.config import load_config
from b8tex.exceptions import DownloadError, MissingBinaryError, UnsupportedPlatformError


def test_detect_platform():
    """Test platform detection."""
    with patch("platform.system", return_value="Linux"):
        with patch("platform.machine", return_value="x86_64"):
            system, arch = TectonicBinary._detect_platform()
            assert system == "linux"
            assert arch == "x86_64"

    with patch("platform.system", return_value="Darwin"):
        with patch("platform.machine", return_value="arm64"):
            system, arch = TectonicBinary._detect_platform()
            assert system == "macos"
            assert arch == "aarch64"

    with patch("platform.system", return_value="Windows"):
        with patch("platform.machine", return_value="AMD64"):
            system, arch = TectonicBinary._detect_platform()
            assert system == "windows"
            assert arch == "x86_64"


def test_detect_platform_unsupported():
    """Test platform detection with unsupported platform."""
    with patch("platform.system", return_value="FreeBSD"):
        with patch("platform.machine", return_value="x86_64"):
            with pytest.raises(UnsupportedPlatformError):
                TectonicBinary._detect_platform()

    with patch("platform.system", return_value="Linux"):
        with patch("platform.machine", return_value="powerpc"):
            with pytest.raises(UnsupportedPlatformError):
                TectonicBinary._detect_platform()


def test_get_download_url():
    """Test download URL generation."""
    with patch("platform.system", return_value="Linux"):
        with patch("platform.machine", return_value="x86_64"):
            url = TectonicBinary._get_download_url("0.15.0")
            assert "tectonic@0.15.0" in url
            assert "x86_64-unknown-linux-gnu" in url
            assert url.endswith(".tar.gz")

    with patch("platform.system", return_value="Darwin"):
        with patch("platform.machine", return_value="arm64"):
            url = TectonicBinary._get_download_url("0.15.0")
            assert "tectonic@0.15.0" in url
            assert "aarch64-apple-darwin" in url
            assert url.endswith(".tar.gz")

    with patch("platform.system", return_value="Windows"):
        with patch("platform.machine", return_value="AMD64"):
            url = TectonicBinary._get_download_url("0.15.0")
            assert "tectonic@0.15.0" in url
            assert "x86_64-pc-windows-msvc" in url
            assert url.endswith(".zip")


def test_get_cache_dir(tmp_path: Path):
    """Test cache directory creation."""
    with patch("platformdirs.user_cache_dir", return_value=str(tmp_path / "cache")):
        cache_dir = TectonicBinary._get_cache_dir()
        assert cache_dir.exists()
        assert cache_dir.is_dir()


def test_download_binary_cached(tmp_path: Path):
    """Test that download skips if binary is already cached."""
    # Create a fake cached binary
    binary_path = tmp_path / "tectonic"
    binary_path.write_text("fake binary")

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=tmp_path):
        with patch("platform.system", return_value="Linux"):
            result = TectonicBinary._download_binary(version="0.15.0", force=False)
            assert result == binary_path
            assert result.exists()


def test_download_binary_force_redownload(tmp_path: Path):
    """Test that force flag triggers re-download."""
    # Create a fake cached binary
    binary_path = tmp_path / "tectonic"
    binary_path.write_text("old binary")

    def mock_download_validation(url, target_path, timeout=None):
        # Write some data to make it non-empty
        target_path.write_text("downloaded data")

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=tmp_path), patch.object(
        TectonicBinary, "_is_windows", return_value=False
    ), patch.object(
        TectonicBinary, "_download_with_validation", side_effect=mock_download_validation
    ) as mock_download, patch(
        "tarfile.open"
    ) as mock_tarfile:
        # Mock tarfile to not actually extract
        mock_archive = MagicMock()
        mock_member = MagicMock()
        mock_member.name = "tectonic"
        mock_member.isdir.return_value = False

        # Create a proper file-like object that returns bytes
        import io
        mock_file_obj = io.BytesIO(b"fake binary data")

        mock_archive.getmembers.return_value = [mock_member]
        mock_archive.extractfile.return_value = mock_file_obj
        mock_tarfile.return_value.__enter__.return_value = mock_archive

        TectonicBinary._download_binary(version="0.15.0", force=True)

        # Should have attempted download
        assert mock_download.called


def test_download_binary_network_error(tmp_path: Path):
    """Test download handling of network errors."""
    with patch.object(TectonicBinary, "_get_cache_dir", return_value=tmp_path), patch.object(
        TectonicBinary, "_is_windows", return_value=False
    ), patch.object(
        TectonicBinary,
        "_download_with_validation",
        side_effect=DownloadError("Network error", url="http://test", cause=None),
    ):
        with pytest.raises(DownloadError) as exc_info:
            TectonicBinary._download_binary(version="0.15.0")

        assert "Network error" in str(exc_info.value)


def test_download_binary_extraction_error(tmp_path: Path):
    """Test download handling of extraction errors."""
    import tarfile

    def mock_download_validation(url, target_path, timeout=None):
        # Write some data to make it non-empty
        target_path.write_text("downloaded data")

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=tmp_path), patch.object(
        TectonicBinary, "_is_windows", return_value=False
    ), patch.object(
        TectonicBinary, "_download_with_validation", side_effect=mock_download_validation
    ), patch(
        "tarfile.open", side_effect=tarfile.TarError("Bad archive")
    ):
        with pytest.raises(DownloadError) as exc_info:
            TectonicBinary._download_binary(version="0.15.0")

        assert "Archive extraction failed" in str(exc_info.value)


def test_discover_with_auto_download_disabled(tmp_path: Path, monkeypatch):
    """Test that discovery fails gracefully when auto-download is disabled."""
    # Set environment to disable auto-download
    monkeypatch.setenv("B8TEX_NO_AUTO_DOWNLOAD", "1")

    # Mock PATH search to fail
    with patch("shutil.which", return_value=None):
        with patch.object(TectonicBinary, "_get_cache_dir", return_value=tmp_path):
            with pytest.raises(MissingBinaryError) as exc_info:
                TectonicBinary.discover()

            assert not exc_info.value.auto_download_attempted
            assert "Automatic download is disabled" in str(exc_info.value)


def test_discover_with_auto_download_enabled(tmp_path: Path, monkeypatch):
    """Test that discovery attempts download when enabled."""
    # Ensure auto-download is enabled
    monkeypatch.delenv("B8TEX_NO_AUTO_DOWNLOAD", raising=False)

    binary_path = tmp_path / "tectonic"
    binary_path.write_text("fake binary")
    binary_path.chmod(0o755)

    # Mock all discovery methods to fail until download
    with patch("shutil.which", return_value=None):
        with patch.object(TectonicBinary, "_get_cache_dir", return_value=tmp_path):
            with patch.object(
                TectonicBinary, "_download_binary", return_value=binary_path
            ):
                with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
                    result = TectonicBinary.discover()
                    assert result.path == binary_path


def test_discover_respects_config_binary_path(tmp_path: Path, monkeypatch):
    """Test that custom binary path from config is respected."""
    binary_path = tmp_path / "custom_tectonic"
    binary_path.write_text("fake binary")
    binary_path.chmod(0o755)

    # Create config file with custom path
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_file.write_text(f'binary_path = "{binary_path}"\n')

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
        result = TectonicBinary.discover()
        assert result.path == binary_path


def test_discover_checks_cache_before_download(tmp_path: Path, monkeypatch):
    """Test that discovery checks cache directory before downloading."""
    monkeypatch.delenv("B8TEX_NO_AUTO_DOWNLOAD", raising=False)

    # Create a cached binary
    binary_path = tmp_path / "tectonic"
    binary_path.write_text("cached binary")
    binary_path.chmod(0o755)

    with patch("shutil.which", return_value=None):
        with patch.object(TectonicBinary, "_get_cache_dir", return_value=tmp_path):
            with patch.object(
                TectonicBinary, "_download_binary"
            ) as mock_download:
                with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
                    result = TectonicBinary.discover()

                    # Should find cached binary without downloading
                    assert not mock_download.called
                    assert result.path == binary_path


def test_discover_environment_variable_priority(tmp_path: Path, monkeypatch):
    """Test that environment variable takes priority."""
    env_binary = tmp_path / "env_tectonic"
    env_binary.write_text("env binary")
    env_binary.chmod(0o755)

    cached_binary = tmp_path / "tectonic"
    cached_binary.write_text("cached binary")
    cached_binary.chmod(0o755)

    monkeypatch.setenv("TECTONIC_PATH", str(env_binary))

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=tmp_path):
        result = TectonicBinary.discover()
        # Environment variable should win
        assert result.path == env_binary


def test_load_config_from_environment(tmp_path: Path, monkeypatch):
    """Test loading configuration from environment variables."""
    monkeypatch.setenv("B8TEX_NO_AUTO_DOWNLOAD", "1")
    monkeypatch.setenv("B8TEX_TECTONIC_VERSION", "0.14.0")
    monkeypatch.setenv("TECTONIC_PATH", "/custom/path/tectonic")

    with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
        config = load_config()

        assert config.auto_download is False
        assert config.tectonic_version == "0.14.0"
        assert config.binary_path == Path("/custom/path/tectonic")


def test_load_config_from_file(tmp_path: Path):
    """Test loading configuration from file."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_file.write_text(
        """
auto_download = false
tectonic_version = "0.13.0"
binary_path = "/file/path/tectonic"
"""
    )

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
        config = load_config()

        assert config.auto_download is False
        assert config.tectonic_version == "0.13.0"
        assert config.binary_path == Path("/file/path/tectonic")


def test_config_environment_overrides_file(tmp_path: Path, monkeypatch):
    """Test that environment variables override config file."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_file.write_text(
        """
auto_download = true
tectonic_version = "0.13.0"
"""
    )

    monkeypatch.setenv("B8TEX_NO_AUTO_DOWNLOAD", "1")
    monkeypatch.setenv("B8TEX_TECTONIC_VERSION", "0.15.0")

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
        config = load_config()

        # Environment should override file
        assert config.auto_download is False
        assert config.tectonic_version == "0.15.0"


def test_config_invalid_file_ignored(tmp_path: Path):
    """Test that invalid config files are ignored gracefully."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_file.write_text("invalid toml {{{")

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
        # Should not raise, just return defaults
        config = load_config()
        assert config.auto_download is True
        assert config.tectonic_version is None

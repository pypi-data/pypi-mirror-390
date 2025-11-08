"""Tests for B8TeX CLI commands."""

from pathlib import Path
from unittest.mock import patch

from b8tex import cli
from b8tex.core.binary import Capabilities, TectonicBinary
from b8tex.exceptions import DownloadError, UnsupportedPlatformError


def test_cli_help():
    """Test help command."""
    result = cli.show_help()
    assert result == 0


def test_cli_main_no_args():
    """Test main with no arguments shows help."""
    with patch("sys.argv", ["b8tex"]):
        result = cli.main()
        assert result == 0


def test_cli_main_help_flag():
    """Test main with help flags."""
    for flag in ["help", "--help", "-h"]:
        with patch("sys.argv", ["b8tex", flag]):
            result = cli.main()
            assert result == 0


def test_cli_main_unknown_command():
    """Test main with unknown command."""
    with patch("sys.argv", ["b8tex", "unknown-command"]):
        result = cli.main()
        assert result == 1


def test_install_binary_success(tmp_path: Path):
    """Test successful binary installation."""
    binary_path = tmp_path / "tectonic"
    binary_path.write_text("fake binary")
    binary_path.chmod(0o755)

    mock_caps = Capabilities(version="0.15.0", supports_v2=True)

    with patch.object(
        TectonicBinary, "_download_binary", return_value=binary_path
    ), patch.object(TectonicBinary, "probe", return_value=mock_caps):
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            result = cli.install_binary([])
            assert result == 0


def test_install_binary_with_version(tmp_path: Path):
    """Test binary installation with specific version."""
    binary_path = tmp_path / "tectonic"
    binary_path.write_text("fake binary")
    binary_path.chmod(0o755)

    mock_caps = Capabilities(version="0.14.0", supports_v2=False)

    with patch.object(
        TectonicBinary, "_download_binary", return_value=binary_path
    ) as mock_download, patch.object(TectonicBinary, "probe", return_value=mock_caps):
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            result = cli.install_binary(["--version=0.14.0"])
            assert result == 0
            # Verify correct version was requested
            mock_download.assert_called_once()
            assert mock_download.call_args[1]["version"] == "0.14.0"


def test_install_binary_with_force(tmp_path: Path):
    """Test binary installation with force flag."""
    binary_path = tmp_path / "tectonic"
    binary_path.write_text("fake binary")
    binary_path.chmod(0o755)

    mock_caps = Capabilities(version="0.15.0", supports_v2=True)

    with patch.object(
        TectonicBinary, "_download_binary", return_value=binary_path
    ) as mock_download, patch.object(TectonicBinary, "probe", return_value=mock_caps):
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            result = cli.install_binary(["--force"])
            assert result == 0
            # Verify force flag was passed
            mock_download.assert_called_once()
            assert mock_download.call_args[1]["force"] is True


def test_install_binary_unsupported_platform():
    """Test binary installation on unsupported platform."""
    with patch.object(
        TectonicBinary,
        "_download_binary",
        side_effect=UnsupportedPlatformError("freebsd", "x86_64"),
    ):
        result = cli.install_binary([])
        assert result == 1


def test_install_binary_download_error():
    """Test binary installation with download error."""
    with patch.object(
        TectonicBinary,
        "_download_binary",
        side_effect=DownloadError("Network error", url="http://example.com"),
    ):
        result = cli.install_binary([])
        assert result == 1


def test_install_binary_unexpected_error():
    """Test binary installation with unexpected error."""
    with patch.object(
        TectonicBinary, "_download_binary", side_effect=RuntimeError("Unexpected")
    ):
        result = cli.install_binary([])
        assert result == 1


def test_show_config_with_binary_found(tmp_path: Path):
    """Test show config when binary is found."""
    binary_path = tmp_path / "tectonic"
    binary_path.write_text("fake binary")
    binary_path.chmod(0o755)

    mock_caps = Capabilities(version="0.15.0", supports_v2=True)

    with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
        with patch.object(TectonicBinary, "discover") as mock_discover:
            mock_binary = TectonicBinary(path=binary_path, capabilities=mock_caps)
            mock_discover.return_value = mock_binary

            with patch.object(TectonicBinary, "probe", return_value=mock_caps):
                result = cli.show_config([])
                assert result == 0


def test_show_config_without_binary(tmp_path: Path):
    """Test show config when binary is not found."""
    with patch("platformdirs.user_config_dir", return_value=str(tmp_path)), patch.object(
        TectonicBinary, "discover", side_effect=Exception("Not found")
    ):
        result = cli.show_config([])
        assert result == 0  # Should still succeed


def test_init_config_new_file(tmp_path: Path):
    """Test creating new config file."""
    config_dir = tmp_path / "config"

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
        result = cli.init_config([])
        assert result == 0

        config_file = config_dir / "config.toml"
        assert config_file.exists()
        content = config_file.read_text()
        assert "auto_download" in content
        assert "tectonic_version" in content


def test_init_config_existing_file_abort(tmp_path: Path, monkeypatch):
    """Test aborting when config file already exists."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_file.write_text("existing content")

    # Mock user input to abort
    monkeypatch.setattr("builtins.input", lambda _: "n")

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
        result = cli.init_config([])
        assert result == 0
        # File should still have original content
        assert config_file.read_text() == "existing content"


def test_init_config_existing_file_overwrite(tmp_path: Path, monkeypatch):
    """Test overwriting existing config file."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_file.write_text("old content")

    # Mock user input to overwrite
    monkeypatch.setattr("builtins.input", lambda _: "y")

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
        result = cli.init_config([])
        assert result == 0
        # File should have new content
        content = config_file.read_text()
        assert "auto_download" in content
        assert "old content" not in content


def test_init_config_error(tmp_path: Path):
    """Test error handling in init_config."""
    # Use a path that will fail (e.g., permission denied)
    with patch("platformdirs.user_config_dir", return_value="/root/no-permission"), patch(
        "b8tex.core.config.create_default_config",
        side_effect=PermissionError("Permission denied"),
    ):
        result = cli.init_config([])
        assert result == 1


def test_cli_main_install_binary(tmp_path: Path):
    """Test main entry point with install-binary command."""
    binary_path = tmp_path / "tectonic"
    binary_path.write_text("fake binary")
    binary_path.chmod(0o755)

    mock_caps = Capabilities(version="0.15.0", supports_v2=True)

    with patch("sys.argv", ["b8tex", "install-binary"]), patch.object(
        TectonicBinary, "_download_binary", return_value=binary_path
    ), patch.object(TectonicBinary, "probe", return_value=mock_caps):
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            result = cli.main()
            assert result == 0


def test_cli_main_config(tmp_path: Path):
    """Test main entry point with config command."""
    with patch("sys.argv", ["b8tex", "config"]):
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            with patch.object(
                TectonicBinary, "discover", side_effect=Exception("Not found")
            ):
                result = cli.main()
                assert result == 0


def test_cli_main_init_config(tmp_path: Path):
    """Test main entry point with init-config command."""
    config_dir = tmp_path / "config"

    with patch("sys.argv", ["b8tex", "init-config"]):
        with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
            result = cli.main()
            assert result == 0


def test_install_binary_version_from_config(tmp_path: Path):
    """Test that install-binary uses version from config if not specified."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_file.write_text('tectonic_version = "0.13.0"\n')

    binary_path = tmp_path / "tectonic"
    binary_path.write_text("fake binary")
    binary_path.chmod(0o755)

    mock_caps = Capabilities(version="0.13.0", supports_v2=False)

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)), patch.object(
        TectonicBinary, "_download_binary", return_value=binary_path
    ) as mock_download, patch.object(TectonicBinary, "probe", return_value=mock_caps):
        result = cli.install_binary([])
        assert result == 0
        # Should use version from config
        mock_download.assert_called_once()
        assert mock_download.call_args[1]["version"] == "0.13.0"


def test_show_config_displays_correct_info(tmp_path: Path, capsys):
    """Test that show_config displays correct configuration information."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_file.write_text(
        """
auto_download = false
tectonic_version = "0.14.0"
"""
    )

    with patch("platformdirs.user_config_dir", return_value=str(config_dir)), patch.object(
        TectonicBinary, "discover", side_effect=Exception("Not found")
    ):
        result = cli.show_config([])
        assert result == 0

        captured = capsys.readouterr()
        assert "B8TeX Configuration" in captured.out
        assert "Auto-download enabled: False" in captured.out
        assert "0.14.0" in captured.out


def test_clean_cache_empty_cache(tmp_path: Path, capsys):
    """Test clean_cache with empty cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=cache_dir):
        result = cli.clean_cache([])
        assert result == 0

        captured = capsys.readouterr()
        assert "Cache is already empty" in captured.out


def test_clean_cache_nonexistent_cache(tmp_path: Path, capsys):
    """Test clean_cache when cache directory doesn't exist."""
    cache_dir = tmp_path / "cache"

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=cache_dir):
        result = cli.clean_cache([])
        assert result == 0

        captured = capsys.readouterr()
        assert "Cache directory does not exist" in captured.out


def test_clean_cache_with_files_abort(tmp_path: Path, monkeypatch, capsys):
    """Test clean_cache with files but user aborts."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    # Create some cached files
    (cache_dir / "tectonic-0.15.0").write_text("fake binary")
    (cache_dir / "other-file.txt").write_text("some data")

    # Mock user input to abort
    monkeypatch.setattr("builtins.input", lambda _: "n")

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=cache_dir):
        result = cli.clean_cache([])
        assert result == 0

        captured = capsys.readouterr()
        assert "Found 2 cached file(s)" in captured.out
        assert "Aborted" in captured.out

        # Files should still exist
        assert (cache_dir / "tectonic-0.15.0").exists()
        assert (cache_dir / "other-file.txt").exists()


def test_clean_cache_with_files_confirm(tmp_path: Path, monkeypatch, capsys):
    """Test clean_cache with files and user confirms deletion."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    # Create some cached files
    (cache_dir / "tectonic-0.15.0").write_text("fake binary")
    (cache_dir / "other-file.txt").write_text("some data")

    # Mock user input to confirm
    monkeypatch.setattr("builtins.input", lambda _: "y")

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=cache_dir):
        result = cli.clean_cache([])
        assert result == 0

        captured = capsys.readouterr()
        assert "Found 2 cached file(s)" in captured.out
        assert "Deleted 2 file(s)" in captured.out

        # Files should be deleted
        assert not (cache_dir / "tectonic-0.15.0").exists()
        assert not (cache_dir / "other-file.txt").exists()


def test_clean_cache_with_directory(tmp_path: Path, monkeypatch, capsys):
    """Test clean_cache with subdirectories."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    # Create a subdirectory
    subdir = cache_dir / "artifacts"
    subdir.mkdir()
    (subdir / "file.pdf").write_text("pdf content")

    # Mock user input to confirm
    monkeypatch.setattr("builtins.input", lambda _: "y")

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=cache_dir):
        result = cli.clean_cache([])
        assert result == 0

        captured = capsys.readouterr()
        assert "Found 1 cached file(s)" in captured.out
        assert "Deleted 1 file(s)" in captured.out

        # Directory should be deleted
        assert not subdir.exists()


def test_clean_cache_permission_error(tmp_path: Path, monkeypatch, capsys):
    """Test clean_cache handles permission errors gracefully."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    # Create a file
    test_file = cache_dir / "test-file.txt"
    test_file.write_text("data")

    # Mock user input to confirm
    monkeypatch.setattr("builtins.input", lambda _: "y")

    # Mock unlink to raise permission error
    original_unlink = Path.unlink

    def mock_unlink(self, *args, **kwargs):
        if self.name == "test-file.txt":
            raise PermissionError("Permission denied")
        return original_unlink(self, *args, **kwargs)

    with patch.object(TectonicBinary, "_get_cache_dir", return_value=cache_dir), patch.object(
        Path, "unlink", mock_unlink
    ):
        result = cli.clean_cache([])
        assert result == 0

        captured = capsys.readouterr()
        assert "Failed to delete test-file.txt" in captured.err


def test_clean_cache_unexpected_error(tmp_path: Path, capsys):
    """Test clean_cache handles unexpected errors."""
    with patch.object(
        TectonicBinary, "_get_cache_dir", side_effect=RuntimeError("Unexpected error")
    ):
        result = cli.clean_cache([])
        assert result == 1

        captured = capsys.readouterr()
        assert "Error cleaning cache" in captured.err


def test_cli_main_clean_cache(tmp_path: Path, monkeypatch):
    """Test main entry point with clean-cache command."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    # Mock user input to abort
    monkeypatch.setattr("builtins.input", lambda _: "n")

    with patch("sys.argv", ["b8tex", "clean-cache"]), patch.object(
        TectonicBinary, "_get_cache_dir", return_value=cache_dir
    ):
        result = cli.main()
        assert result == 0

"""Command-line interface for B8TeX."""

from __future__ import annotations

import sys

# Import constants from binary module
from b8tex.core.binary import DEFAULT_TECTONIC_VERSION


def install_binary(args: list[str]) -> int:
    """Install Tectonic binary to cache directory.

    Args:
        args: Command-line arguments (--force, --version=X.Y.Z)

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    from b8tex.core.binary import TectonicBinary
    from b8tex.core.config import load_config
    from b8tex.exceptions import DownloadError, UnsupportedPlatformError

    # Parse arguments
    force = "--force" in args
    version = None
    for arg in args:
        if arg.startswith("--version="):
            version = arg.split("=", 1)[1]

    # Load config for default version
    if version is None:
        config = load_config()
        version = config.tectonic_version or DEFAULT_TECTONIC_VERSION

    # Attempt download
    try:
        print(f"Installing Tectonic {version}...")
        binary_path = TectonicBinary._download_binary(version=version, force=force)
        print(f"✓ Successfully installed to: {binary_path}")

        # Verify it works
        binary = TectonicBinary(path=binary_path)
        caps = binary.probe()
        print(f"✓ Version: {caps.version}")
        print(f"✓ V2 interface support: {caps.supports_v2}")

        return 0

    except UnsupportedPlatformError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1

    except DownloadError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return 1


def show_config(args: list[str]) -> int:  # noqa: ARG001
    """Show current B8TeX configuration.

    Args:
        args: Command-line arguments (unused)

    Returns:
        Exit code (0 = success)
    """
    from b8tex.core.config import get_config_path, load_config

    config = load_config()
    config_path = get_config_path()

    print("B8TeX Configuration")
    print("=" * 50)
    print(f"Config file: {config_path}")
    print(f"Config exists: {config_path.exists()}")
    print()
    print(f"Auto-download enabled: {config.auto_download}")
    print(f"Tectonic version: {config.tectonic_version or 'latest (0.15.0)'}")
    print(f"Custom binary path: {config.binary_path or 'None'}")
    print()

    # Try to discover binary
    try:
        from b8tex.core.binary import TectonicBinary

        binary = TectonicBinary.discover()
        print(f"✓ Tectonic binary found: {binary.path}")

        caps = binary.probe()
        print(f"  Version: {caps.version}")
        print(f"  V2 support: {caps.supports_v2}")

    except Exception as e:
        print(f"✗ Tectonic binary not found: {e}")

    return 0


def init_config(args: list[str]) -> int:  # noqa: ARG001
    """Initialize B8TeX configuration file.

    Args:
        args: Command-line arguments (unused)

    Returns:
        Exit code (0 = success)
    """
    from b8tex.core.config import create_default_config, get_config_path

    config_path = get_config_path()

    if config_path.exists():
        print(f"Configuration file already exists: {config_path}")
        response = input("Overwrite? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            return 0

    try:
        create_default_config()
        print(f"✓ Created configuration file: {config_path}")
        print()
        print("Edit this file to customize B8TeX behavior:")
        print(f"  {config_path}")
        return 0

    except Exception as e:
        print(f"✗ Error creating config file: {e}", file=sys.stderr)
        return 1


def clean_cache(args: list[str]) -> int:  # noqa: ARG001
    """Clean the B8TeX cache directory.

    Args:
        args: Command-line arguments (unused)

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    from b8tex.core.binary import TectonicBinary

    try:
        cache_dir = TectonicBinary._get_cache_dir()

        if not cache_dir.exists():
            print(f"Cache directory does not exist: {cache_dir}")
            return 0

        print(f"Cache directory: {cache_dir}")

        # List cached files
        files = list(cache_dir.glob("*"))
        if not files:
            print("Cache is already empty")
            return 0

        print(f"Found {len(files)} cached file(s):")
        for file in files:
            size = file.stat().st_size if file.is_file() else 0
            print(f"  {file.name} ({size:,} bytes)")

        response = input("\nDelete all cached files? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            return 0

        # Delete files
        deleted = 0
        for file in files:
            try:
                if file.is_file():
                    file.unlink()
                    deleted += 1
                elif file.is_dir():
                    import shutil

                    shutil.rmtree(file)
                    deleted += 1
            except Exception as e:
                print(f"✗ Failed to delete {file.name}: {e}", file=sys.stderr)

        print(f"✓ Deleted {deleted} file(s)")
        return 0

    except Exception as e:
        print(f"✗ Error cleaning cache: {e}", file=sys.stderr)
        return 1


def show_help() -> int:
    """Show help message.

    Returns:
        Exit code (0)
    """
    help_text = """B8TeX - Python wrapper for Tectonic LaTeX compiler

Usage:
    b8tex <command> [options]

Commands:
    install-binary     Download and install Tectonic binary
        --version=X.Y.Z    Specify version to download (default: 0.15.0)
        --force            Force re-download even if cached

    config             Show current configuration
    init-config        Create default configuration file
    clean-cache        Remove downloaded binaries from cache
    help               Show this help message

Environment Variables:
    TECTONIC_PATH              Path to Tectonic binary
    B8TEX_NO_AUTO_DOWNLOAD     Disable automatic downloads (set to any value)
    B8TEX_TECTONIC_VERSION     Override Tectonic version
    B8TEX_CONFIG_PATH          Override config file location

Configuration File:
    Location: ~/.config/b8tex/config.toml (or platform equivalent)
    Use 'b8tex init-config' to create a default configuration file

Examples:
    # Download latest Tectonic
    b8tex install-binary

    # Download specific version
    b8tex install-binary --version=0.15.0

    # Force re-download
    b8tex install-binary --force

    # Show configuration
    b8tex config

    # Initialize config file
    b8tex init-config

    # Clean cache
    b8tex clean-cache

For more information, visit: https://github.com/sameh/pytex
"""
    print(help_text)
    return 0


def main() -> int:
    """Main entry point for B8TeX CLI.

    Returns:
        Exit code
    """
    args = sys.argv[1:]

    if not args or args[0] in ("help", "--help", "-h"):
        return show_help()

    command = args[0]
    command_args = args[1:]

    if command == "install-binary":
        return install_binary(command_args)
    elif command == "config":
        return show_config(command_args)
    elif command == "init-config":
        return init_config(command_args)
    elif command == "clean-cache":
        return clean_cache(command_args)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Run 'b8tex help' for usage information", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

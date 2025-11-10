#!/usr/bin/env python3
"""CLI entry point that executes the downloaded Erdo CLI binary."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_binary_path() -> Path:
    """Get the path to the CLI binary."""
    package_dir = Path(__file__).parent
    bin_dir = package_dir / "bin"

    # Determine binary name based on platform
    if platform.system().lower() == "windows":
        binary_name = "erdo.exe"
    else:
        binary_name = "erdo"

    return bin_dir / binary_name


def find_system_cli() -> Optional[str]:
    """Find erdo CLI in system PATH, excluding pyenv shims."""
    erdo_path = shutil.which("erdo")
    if erdo_path and "pyenv/shims" not in erdo_path:
        return erdo_path
    return None


def main() -> None:
    """Main CLI entry point."""
    # First, check if erdo is available in system PATH
    system_cli = find_system_cli()
    if system_cli:
        try:
            result = subprocess.run([system_cli] + sys.argv[1:])
            sys.exit(result.returncode)
        except Exception as e:
            print(f"Error executing system CLI: {e}")
            # Fall through to try local binary

    # Check for local binary
    binary_path = get_binary_path()
    if not binary_path.exists():
        try:
            from .install_cli import download_and_install_cli

            download_and_install_cli()
        except Exception as e:
            print(f"Failed to download CLI: {e}")
            print(
                "Please manually download from: https://github.com/erdoai/homebrew-tap/releases"
            )
            sys.exit(1)

    # Execute the local binary with all arguments
    try:
        result = subprocess.run([str(binary_path)] + sys.argv[1:])
        sys.exit(result.returncode)
    except FileNotFoundError:
        print(f"Error: CLI binary not found at {binary_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error executing CLI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

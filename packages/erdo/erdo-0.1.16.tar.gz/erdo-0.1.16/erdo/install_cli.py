#!/usr/bin/env python3
"""Post-install script to download Erdo CLI binary from GitHub releases."""

import os
import platform
import shutil
import urllib.request
from pathlib import Path


def get_platform_info():
    """Get platform and architecture information."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize architecture names
    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["aarch64", "arm64"]:
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    # Map platform names
    if system == "darwin":
        platform_name = "darwin"
    elif system == "linux":
        platform_name = "linux"
    elif system == "windows":
        platform_name = "windows"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

    return platform_name, arch


def get_download_url(version="latest"):
    """Get the download URL for the CLI binary."""
    platform_name, arch = get_platform_info()

    # Construct the binary name based on GoReleaser naming convention
    if platform_name == "windows":
        binary_name = f"erdo-cli_Windows_{arch}.zip"
    else:
        # For Unix-like systems, use tar.gz
        if arch == "amd64":
            arch_name = "x86_64"
        else:
            arch_name = arch

        platform_title = platform_name.title()
        binary_name = f"erdo-cli_{platform_title}_{arch_name}.tar.gz"

    base_url = "https://github.com/erdoai/homebrew-tap/releases"
    if version == "latest":
        return f"{base_url}/latest/download/{binary_name}"
    else:
        return f"{base_url}/download/{version}/{binary_name}"


def download_and_install_cli():
    """Download and install the CLI binary."""
    try:
        # Get the installation directory
        package_dir = Path(__file__).parent
        bin_dir = package_dir / "bin"
        bin_dir.mkdir(exist_ok=True)

        platform_name, arch = get_platform_info()

        # Determine the final binary name
        if platform_name == "windows":
            binary_name = "erdo.exe"
        else:
            binary_name = "erdo"

        binary_path = bin_dir / binary_name

        # Skip if binary already exists
        if binary_path.exists():
            print(f"Erdo CLI already installed at {binary_path}")
            return

        print("Downloading Erdo CLI...")
        download_url = get_download_url()

        # Download the archive
        archive_path = bin_dir / "erdo-cli-archive"
        urllib.request.urlretrieve(download_url, archive_path)

        # Extract the binary
        if platform_name == "windows":
            import zipfile

            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                # Extract erdo.exe from the zip
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith("erdo.exe"):
                        with (
                            zip_ref.open(file_info) as source,
                            open(binary_path, "wb") as target,
                        ):
                            shutil.copyfileobj(source, target)
                        break
        else:
            import tarfile

            with tarfile.open(archive_path, "r:gz") as tar_ref:
                # Extract erdo binary from the tar.gz
                for member in tar_ref.getmembers():
                    if member.name.endswith("/erdo") or member.name == "erdo":
                        with (
                            tar_ref.extractfile(member) as source,
                            open(binary_path, "wb") as target,
                        ):
                            shutil.copyfileobj(source, target)
                        break

        # Make executable on Unix-like systems
        if platform_name != "windows":
            os.chmod(binary_path, 0o755)

        # Clean up the archive
        archive_path.unlink()

        print(f"✓ Erdo CLI installed to {binary_path}")

        # Add to PATH instructions
        print("\nTo use the CLI globally, add the following to your PATH:")
        print(f'export PATH="{bin_dir}:$PATH"')

    except Exception as e:
        print(f"Warning: Failed to download Erdo CLI: {e}")
        print(
            "You can manually download it from: https://github.com/erdoai/homebrew-tap/releases"
        )


if __name__ == "__main__":
    download_and_install_cli()

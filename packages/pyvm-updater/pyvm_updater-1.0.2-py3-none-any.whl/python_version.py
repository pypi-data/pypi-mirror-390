"""
Python Version Manager - CLI Tool
Checks and updates Python to the latest version across Windows, Linux, and macOS

Requirements:
    pip install requests beautifulsoup4 packaging click

Note: Dependencies are automatically installed via setup.py during CLI installation.
"""

import platform
import sys
import os
import subprocess
import tempfile
import shutil
import hashlib
import re
import time
from pathlib import Path
from typing import Optional, Tuple

try:
    import requests
    from bs4 import BeautifulSoup
    from packaging import version as pkg_version
    import click
except ImportError as e:
    print("ERROR: Missing required packages.")
    print("Please install them using:")
    print("  pip install requests beautifulsoup4 packaging click")
    print("\nOr install this tool via:")
    print("  pip install -e .")
    print(f"\nDetails: {e}")
    sys.exit(1)

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
DOWNLOAD_TIMEOUT = 120  # seconds
REQUEST_TIMEOUT = 15  # seconds


def get_os_info():
    """Detect the operating system and architecture"""
    os_name = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize architecture names
    if machine in ['amd64', 'x86_64']:
        arch = 'amd64'
    elif machine in ['arm64', 'aarch64']:
        arch = 'arm64'
    else:
        arch = 'x86'
    
    return os_name, arch


def is_admin():
    """Check if script is running with admin/sudo privileges"""
    try:
        if platform.system().lower() == 'windows':
            import ctypes
            # Type hint fix: windll is only available on Windows
            return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[attr-defined]
        else:
            # os.geteuid() only exists on Unix-like systems
            return hasattr(os, 'geteuid') and os.geteuid() == 0
    except Exception:
        return False


def validate_version_string(version_str: str) -> bool:
    """Validate that version string matches expected format (e.g., 3.11.5)"""
    if not version_str:
        return False
    # Match format: digit.digit[.digit[...]]
    pattern = r'^\d+\.\d+(\.\d+)*$'
    return bool(re.match(pattern, version_str))


def get_latest_python_info_with_retry() -> Tuple[Optional[str], Optional[str]]:
    """Fetch the latest Python version with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            result = get_latest_python_info()
            if result[0]:  # If we got a version
                return result
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                print(f"All retry attempts failed: {e}")
    return None, None


def get_latest_python_info() -> Tuple[Optional[str], Optional[str]]:
    """Fetch the latest Python version and download URLs"""
    URL = "https://www.python.org/downloads/"
    
    try:
        response = requests.get(URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Specify parser explicitly for consistency
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get version from download button
        download_button = soup.find('a', class_='button')
        if not download_button:
            print("Error: Could not find download button on Python.org")
            return None, None
        
        latest_ver_string = download_button.get_text(strip=True)
        latest_ver = latest_ver_string.split()[-1]
        
        # Validate version string
        if not validate_version_string(latest_ver):
            print(f"Error: Invalid version format retrieved: {latest_ver}")
            return None, None
        
        # Get download URL for specific OS
        download_url_raw = download_button.get('href')
        download_url: Optional[str] = None
        if download_url_raw and isinstance(download_url_raw, str):
            if not download_url_raw.startswith('http'):
                download_url = f"https://www.python.org{download_url_raw}"
            else:
                download_url = download_url_raw
        
        return latest_ver, download_url
        
    except requests.Timeout:
        print("Error: Request to python.org timed out. Check your internet connection.")
        return None, None
    except requests.RequestException as e:
        print(f"Error: Network request failed: {e}")
        return None, None
    except Exception as e:
        print(f"Error: Unexpected error while fetching Python info: {e}")
        return None, None


def download_file(url: str, destination: str) -> bool:
    """Download a file with progress indication and integrity checking"""
    try:
        # Validate URL
        if not url.startswith(('https://', 'http://')):
            print(f"Error: Invalid URL scheme: {url}")
            return False
            
        response = requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
                    else:
                        # No content-length header
                        print(f"\rDownloading: {downloaded} bytes", end='', flush=True)
        
        print()  # New line after progress
        
        # Verify file was downloaded
        if not os.path.exists(destination):
            print("Error: Downloaded file not found")
            return False
            
        file_size = os.path.getsize(destination)
        if total_size and file_size != total_size:
            print(f"Warning: Downloaded file size ({file_size}) doesn't match expected size ({total_size})")
            
        return True
        
    except requests.Timeout:
        print("\nError: Download timed out. Please check your internet connection.")
        return False
    except requests.RequestException as e:
        print(f"\nError: Download failed: {e}")
        return False
    except IOError as e:
        print(f"\nError: Could not write to file {destination}: {e}")
        return False
    except Exception as e:
        print(f"\nError: Unexpected error during download: {e}")
        return False


def update_python_windows(version_str: str) -> bool:
    """Update Python on Windows"""
    print("\n🪟 Windows detected - Downloading Python installer...")
    
    # Validate version string
    if not validate_version_string(version_str):
        print(f"Error: Invalid version string: {version_str}")
        return False
    
    # Construct Windows installer URL - safely
    try:
        parts = version_str.split('.')
        if len(parts) < 3:
            print(f"Error: Version string must have major.minor.patch format: {version_str}")
            return False
        major, minor, patch = parts[0], parts[1], parts[2]
    except (ValueError, IndexError) as e:
        print(f"Error parsing version string '{version_str}': {e}")
        return False
    
    arch = 'amd64' if platform.machine().lower() in ['amd64', 'x86_64'] else 'win32'
    installer_url = f"https://www.python.org/ftp/python/{version_str}/python-{version_str}-{arch}.exe"
    
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, f"python-{version_str}-installer.exe")
    
    print(f"Downloading from: {installer_url}")
    if not download_file(installer_url, installer_path):
        return False
    
    print("\n⚠️  Starting installer...")
    print("Please follow the installer prompts.")
    print("Recommendation: Check 'Add Python to PATH'")
    
    try:
        # Run installer (interactive mode) - using list instead of shell
        result = subprocess.run([installer_path], check=False)
        
        if result.returncode != 0:
            print(f"Warning: Installer exited with code {result.returncode}")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: Installer not found at {installer_path}")
        return False
    except PermissionError:
        print("Error: Permission denied. Try running as Administrator.")
        return False
    except Exception as e:
        print(f"Error running installer: {e}")
        return False
    finally:
        # Cleanup - with better error handling
        try:
            if os.path.exists(installer_path):
                os.remove(installer_path)
                print(f"Cleaned up temporary installer file")
        except PermissionError:
            print(f"Warning: Could not delete temporary file {installer_path} (permission denied)")
        except OSError as e:
            print(f"Warning: Could not delete temporary file {installer_path}: {e}")


def update_python_linux(version_str: str) -> bool:
    """Update Python on Linux using package manager or pyenv"""
    print("\n🐧 Linux detected")
    
    # Validate version string
    if not validate_version_string(version_str):
        print(f"Error: Invalid version string: {version_str}")
        return False
    
    # Extract major.minor version (e.g., "3.11" from "3.11.5")
    try:
        parts = version_str.split('.')
        if len(parts) < 2:
            print(f"Error: Invalid version format: {version_str}")
            return False
        major_minor = f"{parts[0]}.{parts[1]}"
    except (ValueError, IndexError) as e:
        print(f"Error parsing version: {e}")
        return False
    
    # Detect package manager
    if shutil.which('apt'):
        print("Using apt package manager...")
        print("\n⚠️  This requires sudo privileges.")
        print("⚠️  This will add the deadsnakes PPA (third-party repository)")
        
        # Use safer subprocess approach - no shell=True
        commands = [
            ["sudo", "apt", "update"],
            ["sudo", "apt", "install", "-y", "software-properties-common"],
            ["sudo", "add-apt-repository", "-y", "ppa:deadsnakes/ppa"],
            ["sudo", "apt", "update"],
            ["sudo", "apt", "install", "-y", f"python{major_minor}"]
        ]
        
        for cmd in commands:
            print(f"Running: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, check=False, capture_output=False)
                if result.returncode != 0:
                    print(f"⚠️  Command failed with exit code {result.returncode}: {' '.join(cmd)}")
                    print("Continuing anyway...")
            except FileNotFoundError:
                print(f"Error: Command not found: {cmd[0]}")
                return False
            except Exception as e:
                print(f"Error running command: {e}")
                return False
        
        return True
    
    elif shutil.which('yum') or shutil.which('dnf'):
        pkg_mgr = 'dnf' if shutil.which('dnf') else 'yum'
        print(f"Using {pkg_mgr} package manager...")
        print("\n⚠️  This requires sudo privileges.")
        print(f"\nPlease run manually:")
        print(f"  sudo {pkg_mgr} install python3")
        print(f"\nNote: Specific version {version_str} may not be available via {pkg_mgr}")
        print("Consider using pyenv for version-specific installations.")
        return False
    
    else:
        print("No supported package manager found (apt, yum, or dnf).")
        print("\n📦 Recommended: Install pyenv for easy Python version management")
        print("Visit: https://github.com/pyenv/pyenv#installation")
        print("\nPyenv installation (quick):")
        print("  curl https://pyenv.run | bash")
        print(f"  pyenv install {version_str}")
        return False
    
    return True


def update_python_macos(version_str: str) -> bool:
    """Update Python on macOS using Homebrew or official installer"""
    print("\n🍎 macOS detected")
    
    # Validate version string
    if not validate_version_string(version_str):
        print(f"Error: Invalid version string: {version_str}")
        return False
    
    if shutil.which('brew'):
        print("Using Homebrew...")
        print("Attempting to update Python via Homebrew...")
        
        try:
            # Update Homebrew
            print("Updating Homebrew...")
            result = subprocess.run(["brew", "update"], check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: brew update failed: {result.stderr}")
            
            # Upgrade Python
            print("Upgrading Python...")
            result = subprocess.run(["brew", "upgrade", "python3"], check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Note: {result.stderr}")
                print("Python may already be up-to-date or not installed via Homebrew")
            
            return True
            
        except FileNotFoundError:
            print("Error: Homebrew command not found")
            return False
        except Exception as e:
            print(f"Error running Homebrew: {e}")
            return False
    else:
        print("Homebrew not found.")
        print("\n📥 Option 1: Install via official installer")
        
        # Fix URL construction - proper format is "3-11-5" not "3115"
        url_version = version_str.replace('.', '-')
        print(f"   https://www.python.org/downloads/release/python-{url_version}/")
        
        print("\n📦 Option 2: Install Homebrew first")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("   Then run: brew install python")
        
        return False


def check_python_version(silent: bool = False) -> Tuple[str, Optional[str], bool]:
    """
    Check local Python version against the latest stable version from python.org
    Returns: (local_version, latest_version, needs_update)
    """
    local_ver = platform.python_version()
    
    if not silent:
        print(f"Checking Python version... (Current: {local_ver})")

    # Use retry logic
    latest_ver, _ = get_latest_python_info_with_retry()
    
    if not latest_ver:
        if not silent:
            print("Error: Could not fetch latest version information.")
            print("Please check your internet connection and try again.")
        return local_ver, None, False

    try:
        # Validate latest version
        if not validate_version_string(latest_ver):
            if not silent:
                print(f"Error: Invalid version format from server: {latest_ver}")
            return local_ver, None, False
        
        # Use 'version.parse' to create comparable version objects
        local_version_obj = pkg_version.parse(local_ver)
        latest_version_obj = pkg_version.parse(latest_ver)
        needs_update = local_version_obj < latest_version_obj

        if not silent:
            # Display Results
            print("\n" + "=" * 40)
            print("     Python Version Check Report")
            print("=" * 40)
            print(f"Your version:   {local_ver}")
            print(f"Latest version: {latest_ver}")
            print("=" * 40)
            
            if not needs_update:
                print("✓ You are up-to-date!")
            else:
                print(f"⚠ A new version ({latest_ver}) is available!")
        
        return local_ver, latest_ver, needs_update
                
    except Exception as e:
        if not silent:
            print(f"Error comparing versions: {e}")
            print("This might be due to an unexpected version format.")
        return local_ver, latest_ver, False


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--version', is_flag=True, help='Show tool version')
def cli(ctx, version):
    """Python Version Manager - Check and update Python across platforms"""
    if version:
        click.echo("Python Version Manager v1.0.0")
        ctx.exit()
    
    if ctx.invoked_subcommand is None:
        # Default behavior: just check version
        ctx.invoke(check)


@cli.command()
def check():
    """Check current Python version against latest stable release"""
    try:
        local_ver, latest_ver, needs_update = check_python_version(silent=False)
        
        if needs_update:
            click.echo("\n💡 Tip: Run 'pyvm update' to upgrade Python")
            sys.exit(1)  # Exit code 1 indicates update available
        else:
            sys.exit(0)  # Exit code 0 indicates up-to-date
            
    except KeyboardInterrupt:
        click.echo("\n\nOperation cancelled by user.")
        sys.exit(130)


@cli.command()
@click.option('--auto', is_flag=True, help='Automatically proceed without confirmation')
def update(auto):
    """Download and install the latest Python version"""
    try:
        click.echo("🔍 Checking for updates...")
        local_ver, latest_ver, needs_update = check_python_version(silent=True)
        
        if not latest_ver:
            click.echo("❌ Could not fetch latest version information.")
            sys.exit(1)
        
        click.echo(f"\n📊 Current version: {local_ver}")
        click.echo(f"📊 Latest version:  {latest_ver}")
        
        if not needs_update:
            click.echo("\n✅ You already have the latest version!")
            sys.exit(0)
        
        click.echo(f"\n🚀 Update available: {local_ver} → {latest_ver}")
        
        # Confirm update
        if not auto:
            if not click.confirm("\nDo you want to proceed with the update?"):
                click.echo("Update cancelled.")
                sys.exit(0)
        
        # Check admin privileges for some operations
        os_name, arch = get_os_info()
        click.echo(f"\n🖥️  Detected: {os_name.title()} ({arch})")
        
        # Perform update based on OS
        success = False
        if os_name == 'windows':
            success = update_python_windows(latest_ver)
        elif os_name == 'linux':
            success = update_python_linux(latest_ver)
        elif os_name == 'darwin':
            success = update_python_macos(latest_ver)
        else:
            click.echo(f"❌ Unsupported operating system: {os_name}")
            sys.exit(1)
        
        if success:
            click.echo("\n✅ Update process completed!")
            click.echo("⚠️  Note: You may need to restart your terminal/IDE")
            click.echo("    to use the new Python version.")
        else:
            click.echo("\n⚠️  Update process encountered issues.")
            click.echo("    Please check the messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo("\n\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        sys.exit(1)


@cli.command()
def info():
    """Show detailed system and Python information"""
    try:
        click.echo("=" * 50)
        click.echo("           System Information")
        click.echo("=" * 50)
        
        os_name, arch = get_os_info()
        click.echo(f"Operating System: {os_name.title()}")
        click.echo(f"Architecture:     {arch}")
        click.echo(f"Python Version:   {platform.python_version()}")
        click.echo(f"Python Path:      {sys.executable}")
        click.echo(f"Platform:         {platform.platform()}")
        
        click.echo(f"\nAdmin/Sudo:       {'Yes' if is_admin() else 'No'}")
        
        click.echo("=" * 50)
        
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script"""
    try:
        cli()
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
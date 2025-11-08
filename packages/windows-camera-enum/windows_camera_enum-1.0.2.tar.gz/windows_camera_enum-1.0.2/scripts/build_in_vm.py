#!/usr/bin/env python3
"""
VM build utility for windows-camera-enum.

Workaround for Parallels/VM shared folder limitations that break pip builds.
Copies source to Windows-native temp directory, builds, then copies artifacts back.

Usage:
    python scripts/build_in_vm.py           # Standard build
    python scripts/build_in_vm.py --dev     # Development/editable install
    python scripts/build_in_vm.py --verbose # Show detailed build output
    python scripts/build_in_vm.py --keep-temp # Don't delete temp directory
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def detect_platform():
    """Detect if running on Windows."""
    return sys.platform == 'win32'


def run_command(cmd, description, cwd=None, verbose=False):
    """Run a command and display status."""
    print(f"→ {description}...", end=" ", flush=True)

    try:
        result = subprocess.run(
            cmd,
            capture_output=not verbose,
            text=True,
            check=True,
            cwd=cwd,
            shell=isinstance(cmd, str)
        )
        print("✓")
        if verbose and result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("✗")
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def sync_source_files(source_dir, dest_dir, verbose=False):
    """
    Sync source files from shared folder to native directory.
    Excludes build artifacts, .git, caches, etc.
    """
    print(f"→ Syncing source files...", end=" ", flush=True)

    # Files and directories to exclude
    exclude_patterns = {
        '__pycache__',
        '.git',
        '.idea',
        '.vscode',
        'build',
        '_skbuild',
        'dist',
        '*.egg-info',
        '.pytest_cache',
        '*.pyc',
        '*.pyo',
        '*.so',
        '*.pyd',
        '*.dll',
        'venv',
        'env',
        '.venv',
    }

    copied_count = 0

    def should_exclude(path):
        """Check if path should be excluded."""
        name = path.name
        # Check exact matches
        if name in exclude_patterns:
            return True
        # Check wildcards
        for pattern in exclude_patterns:
            if '*' in pattern:
                if pattern.startswith('*.') and name.endswith(pattern[1:]):
                    return True
        return False

    def copy_tree(src, dst):
        """Recursively copy directory tree, excluding patterns."""
        nonlocal copied_count

        dst.mkdir(parents=True, exist_ok=True)

        for item in src.iterdir():
            src_item = src / item.name
            dst_item = dst / item.name

            if should_exclude(src_item):
                if verbose:
                    print(f"\n  Skipping: {src_item.relative_to(source_dir)}", end="")
                continue

            if src_item.is_dir():
                copy_tree(src_item, dst_item)
            else:
                shutil.copy2(src_item, dst_item)
                copied_count += 1
                if verbose:
                    print(f"\n  Copied: {src_item.relative_to(source_dir)}", end="")

    try:
        copy_tree(source_dir, dest_dir)
        print(f"✓ ({copied_count} files)")
        if verbose:
            print()
        return True
    except Exception as e:
        print(f"✗")
        print(f"Error syncing files: {e}")
        return False


def copy_build_artifacts(temp_dir, project_dir, verbose=False):
    """Copy build artifacts back to project directory."""
    print("→ Copying build artifacts back...", end=" ", flush=True)

    artifacts_copied = False

    # Copy dist/ directory if it exists
    temp_dist = temp_dir / 'dist'
    project_dist = project_dir / 'dist'

    if temp_dist.exists():
        if project_dist.exists():
            shutil.rmtree(project_dist)
        shutil.copytree(temp_dist, project_dist)
        artifacts_copied = True

        if verbose:
            wheel_count = len(list(project_dist.glob('*.whl')))
            print(f"\n  Copied dist/ ({wheel_count} wheel files)", end="")

    if artifacts_copied:
        print(" ✓")
        if verbose:
            print()
        return True
    else:
        print(" (no artifacts)")
        return False


def get_package_name(project_root):
    """Get package name from pyproject.toml."""
    pyproject = project_root / "pyproject.toml"

    if pyproject.exists():
        content = pyproject.read_text()
        for line in content.splitlines():
            if line.startswith("name ="):
                return line.split("=")[1].strip().strip('"').strip("'")

    return "windows-camera-enum"


def main():
    parser = argparse.ArgumentParser(
        description="Build windows-camera-enum in VM with shared folder workaround"
    )
    parser.add_argument(
        "-d", "--dev",
        action="store_true",
        help="Install in development/editable mode"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed build output"
    )
    parser.add_argument(
        "--skip-uninstall",
        action="store_true",
        help="Skip uninstall step (useful for first build)"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Don't delete temporary build directory"
    )

    args = parser.parse_args()

    # Check platform
    if not detect_platform():
        print("⚠ Warning: This script is designed for Windows VMs with shared folders.")
        print("For native builds, use: python scripts/rebuild.py")
        proceed = input("Continue anyway? (y/N): ")
        if proceed.lower() != 'y':
            sys.exit(0)

    # Determine project root (script is in scripts/ subdirectory)
    project_root = Path(__file__).parent.parent.resolve()
    package_name = get_package_name(project_root)

    print("=" * 60)
    print("WINDOWS CAMERA ENUM - VM BUILD UTILITY")
    print("=" * 60)
    print(f"Package: {package_name}")
    print(f"Source: {project_root}")
    print(f"Mode: {'Development (editable)' if args.dev else 'Standard install'}")
    print("=" * 60)

    # Create temporary build directory
    if sys.platform == 'win32':
        # Use C:\Temp on Windows for better performance
        temp_base = Path("C:/Temp")
        temp_base.mkdir(exist_ok=True)
        temp_dir = temp_base / "windows-camera-enum-build"

        # Clean up old temp directory if exists
        if temp_dir.exists():
            print(f"→ Cleaning old temp directory...", end=" ", flush=True)
            shutil.rmtree(temp_dir)
            print("✓")
    else:
        # Use system temp on other platforms
        temp_dir = Path(tempfile.mkdtemp(prefix="windows-camera-enum-"))

    print(f"→ Temp directory: {temp_dir}")

    try:
        # Step 1: Sync source files to temp directory
        if not sync_source_files(project_root, temp_dir, args.verbose):
            print("✗ Failed to sync source files")
            sys.exit(1)

        # Step 2: Uninstall existing package
        if not args.skip_uninstall:
            run_command(
                f"pip uninstall -y {package_name}",
                f"Uninstalling {package_name}",
                cwd=temp_dir,
                verbose=args.verbose
            )
        else:
            print("→ Skipping uninstall step")

        # Step 3: Build and install in temp directory
        if args.dev:
            install_cmd = "pip install -e ."
            if args.verbose:
                install_cmd += " --verbose"
            success = run_command(
                install_cmd,
                "Building and installing (editable mode)",
                cwd=temp_dir,
                verbose=args.verbose
            )
        else:
            install_cmd = "pip install ."
            if args.verbose:
                install_cmd += " --verbose"
            success = run_command(
                install_cmd,
                "Building and installing",
                cwd=temp_dir,
                verbose=args.verbose
            )

        if not success:
            print("✗ Build failed")
            sys.exit(1)

        # Step 4: Build wheel for distribution
        print("→ Building wheel package...", end=" ", flush=True)
        wheel_result = subprocess.run(
            "pip wheel . --no-deps --wheel-dir dist",
            capture_output=True,
            text=True,
            shell=True,
            cwd=temp_dir
        )
        if wheel_result.returncode == 0:
            print("✓")
        else:
            print("✗")
            if args.verbose:
                print(wheel_result.stderr)

        # Step 5: Copy build artifacts back to project directory
        copy_build_artifacts(temp_dir, project_root, args.verbose)

        # Summary
        print("=" * 60)
        print("✓ Build completed successfully!")
        print()
        print("Next steps:")
        print(f"  • Test: python examples/basic_usage.py")
        print(f"  • Import: python -c 'import {package_name.replace('-', '_')}'")

        # Show artifact locations
        dist_dir = project_root / 'dist'
        if dist_dir.exists():
            wheels = list(dist_dir.glob('*.whl'))
            if wheels:
                print(f"\nBuild artifacts:")
                for wheel in wheels:
                    print(f"  • {wheel}")

        print("=" * 60)

    finally:
        # Cleanup temp directory
        if not args.keep_temp and temp_dir.exists():
            print(f"→ Cleaning up temp directory...", end=" ", flush=True)
            try:
                shutil.rmtree(temp_dir)
                print("✓")
            except Exception as e:
                print(f"✗ ({e})")
        elif args.keep_temp:
            print(f"→ Temp directory kept at: {temp_dir}")


if __name__ == "__main__":
    main()

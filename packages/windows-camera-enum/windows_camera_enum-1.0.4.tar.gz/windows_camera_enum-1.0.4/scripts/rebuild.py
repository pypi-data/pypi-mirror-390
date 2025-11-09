#!/usr/bin/env python3
"""
Quick rebuild utility for windows-camera-enum.

Automatically uninstalls, cleans, and rebuilds the package.
Useful for rapid development iteration.

Usage:
    python scripts/rebuild.py           # Standard build
    python scripts/rebuild.py --dev     # Development/editable install
    python scripts/rebuild.py --verbose # Show detailed build output
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, verbose=False):
    """Run a command and display status."""
    print(f"→ {description}...", end=" ", flush=True)

    try:
        result = subprocess.run(
            cmd,
            capture_output=not verbose,
            text=True,
            check=True,
            shell=True if isinstance(cmd, str) else False
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


def clean_build_artifacts(project_root, verbose=False):
    """Remove build artifacts."""
    print("→ Cleaning build artifacts...", end=" ", flush=True)

    artifacts = [
        "build",
        "_skbuild",
        "dist",
        "*.egg-info",
    ]

    removed_count = 0
    for pattern in artifacts:
        for path in project_root.glob(pattern):
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                removed_count += 1
                if verbose:
                    print(f"\n  Removed: {path.name}", end="")

    print("✓" if removed_count > 0 else "✓ (already clean)")
    if verbose and removed_count > 0:
        print()


def get_package_name():
    """Get package name from pyproject.toml."""
    project_root = Path(__file__).parent.parent
    pyproject = project_root / "pyproject.toml"

    if pyproject.exists():
        content = pyproject.read_text()
        for line in content.splitlines():
            if line.startswith("name ="):
                return line.split("=")[1].strip().strip('"').strip("'")

    return "windows-camera-enum"


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild windows-camera-enum package"
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

    args = parser.parse_args()

    # Determine project root (script is in scripts/ subdirectory)
    project_root = Path(__file__).parent.parent
    package_name = get_package_name()

    print("=" * 60)
    print("WINDOWS CAMERA ENUM - REBUILD UTILITY")
    print("=" * 60)
    print(f"Package: {package_name}")
    print(f"Mode: {'Development (editable)' if args.dev else 'Standard install'}")
    print("=" * 60)

    # Step 1: Uninstall existing package
    if not args.skip_uninstall:
        run_command(
            f"pip uninstall -y {package_name}",
            f"Uninstalling {package_name}",
            args.verbose
        )
    else:
        print("→ Skipping uninstall step")

    # Step 2: Clean build artifacts
    clean_build_artifacts(project_root, args.verbose)

    # Step 3: Rebuild and install
    if args.dev:
        install_cmd = "pip install -e ."
        if args.verbose:
            install_cmd += " --verbose"
        success = run_command(
            install_cmd,
            "Building and installing (editable mode)",
            args.verbose
        )
    else:
        install_cmd = "pip install ."
        if args.verbose:
            install_cmd += " --verbose"
        success = run_command(
            install_cmd,
            "Building and installing",
            args.verbose
        )

    # Summary
    print("=" * 60)
    if success:
        print("✓ Rebuild completed successfully!")
        print()
        print("Next steps:")
        print(f"  • Test: python examples/basic_usage.py")
        print(f"  • Import: python -c 'import {package_name.replace('-', '_')}'")
    else:
        print("✗ Rebuild failed - see errors above")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

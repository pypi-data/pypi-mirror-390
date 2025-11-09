# Development Utilities

This directory contains utility scripts for developing and maintaining the `windows-camera-enum` project.

## Scripts

### `bump_version.py`

Automated version management utility that updates version numbers across the project.

**Purpose:** Ensures consistent version numbering across `pyproject.toml` and `src/camera_enum/__init__.py`

**Usage:**
```bash
# Increment patch version (1.1.2 -> 1.1.3)
python scripts/bump_version.py patch

# Increment minor version (1.1.2 -> 1.2.0)
python scripts/bump_version.py minor

# Increment major version (1.1.2 -> 2.0.0)
python scripts/bump_version.py major

# Set specific version
python scripts/bump_version.py set 2.0.0
```

**When to use:**
- Before committing new features (minor bump)
- Before committing bug fixes (patch bump)
- Before committing breaking changes (major bump)
- Following [Semantic Versioning](https://semver.org/) principles

---

### `rebuild.py`

Quick rebuild utility for rapid development iteration. Automates the full rebuild cycle: uninstall → clean → build → install.

**Purpose:** Eliminates manual cleanup steps and ensures a fresh build state

**Usage:**
```bash
# Standard rebuild
python scripts/rebuild.py

# Development/editable install (recommended for active development)
python scripts/rebuild.py --dev

# Show detailed build output
python scripts/rebuild.py --verbose

# Skip uninstall (useful for first-time build)
python scripts/rebuild.py --skip-uninstall
```

**When to use:**
- After modifying C++ code (`camera_enum.cpp`)
- After changing build configuration (`CMakeLists.txt`, `pyproject.toml`)
- When troubleshooting build issues
- During active development for quick iteration

**What it does:**
1. Uninstalls existing package (`pip uninstall`)
2. Removes build artifacts (`build/`, `_skbuild/`, `dist/`, `*.egg-info`)
3. Rebuilds and installs package (`pip install .` or `pip install -e .`)

---

### `build_in_vm.py`

VM build utility for working with Parallels/VM shared folders that have file system limitations.

**Purpose:** Workaround for shared folder issues that break pip builds by copying source to native Windows temp directory, building there, then copying artifacts back.

**Usage:**
```bash
# Standard rebuild (from Windows VM)
python scripts/build_in_vm.py

# Development/editable install
python scripts/build_in_vm.py --dev

# Show detailed build output
python scripts/build_in_vm.py --verbose

# Keep temp directory for debugging
python scripts/build_in_vm.py --keep-temp
```

**When to use:**
- When developing on macOS but building in Windows VM with shared folders
- When `pip install .` fails with file system or symlink errors
- When CMake has issues with shared folder paths

**What it does:**
1. Creates temp directory in native Windows location (`C:\Temp\windows-camera-enum-build\`)
2. Syncs source files (excludes .git, build artifacts, caches)
3. Runs full build process in temp directory
4. Copies build artifacts (`dist/*.whl`) back to shared folder
5. Cleans up temp directory (unless `--keep-temp`)

**Development workflow:**
1. Edit code on macOS (using your preferred editor/IDE)
2. Run `python scripts/build_in_vm.py` from Windows VM
3. Test the built package in Windows
4. Commit and publish from macOS side (artifacts are synced back)

---

## Notes

- All scripts automatically detect the project root directory
- Scripts can be run from anywhere in the project
- Use `--help` with any script for more information

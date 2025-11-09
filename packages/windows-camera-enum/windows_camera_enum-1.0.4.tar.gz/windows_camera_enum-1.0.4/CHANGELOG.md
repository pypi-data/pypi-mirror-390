# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2025-11-08

### Fixed
- **Version string inconsistency** - Fixed `__version__` in `__init__.py` to match package version
  - Resolves issue where `camera_enum.__version__` reported incorrect version
  - Both `pyproject.toml` and `__init__.py` now properly synchronized at 1.0.4

## [1.0.3] - 2025-11-07

### Added
- **Automated PyPI publishing workflow** via GitHub Actions
  - Uses cibuildwheel for multi-Python version support
  - Trusted publishing for secure authentication
  - Automatic builds on version tag push

### Known Issues
- ⚠️ **Version string bug**: `__version__` in `__init__.py` incorrectly reports "1.0.2" instead of "1.0.3"
  - Package version in `pyproject.toml` is correct (1.0.3)
  - PyPI version is correct (1.0.3)
  - Only the runtime `__version__` string is affected
  - **Fixed in v1.0.4**

## [1.0.2] - 2025-01-08

### Added
- **PyPI badges** to README.md for better visibility
  - PyPI version badge
  - Python versions badge
  - MIT License badge
  - Downloads badge
- **Project URLs** in pyproject.toml for PyPI sidebar links
  - Homepage
  - Repository
  - Documentation
  - Changelog
  - Issues tracker
- **Installation section** prominently at top of README

### Changed
- Improved README.md layout with badges and quick installation instructions

## [1.0.1] - 2025-01-08

### Fixed
- Removed references to `scripts/bump_version.py` from user-facing documentation
  - This development-only tool is not included in source distributions
  - Updated README.md, CHANGELOG.md, and docs/ARCHITECTURE.md
- Removed "optimized for microscope cameras" language to clarify this library works with all USB UVC cameras
  - Updated README.md and CHANGELOG.md

### Documentation
- Clarified that this is a general-purpose Windows camera enumeration library
- Cleaned up developer tool references to match what's included in distributions

## [1.0.0] - 2025-01-08

### 🎉 First Public Release

Initial public release of `windows-camera-enum`, a Python library for enumerating Windows camera devices using DirectShow APIs.

### Features

**Core Functionality:**
- Comprehensive camera device enumeration with `list_cameras()` API
- Resolution detection with width and height information
- Frame rate enumeration for each supported resolution
- Pixel format detection (MJPEG, YUY2, RGB24, NV12, etc.)
- Camera controls enumeration (zoom, focus, brightness, exposure, etc.) with min/max/default values
- Device path and index information for camera identification

**Type Safety:**
- Complete type hints for all public APIs
- PEP 561 compliant with `py.typed` marker
- TypedDict definitions for structured return values
- Full IDE autocomplete support

**Error Handling:**
- Custom exception hierarchy:
  - `CameraException` - Base exception for all camera errors
  - `NoCameraFoundException` - Raised when no cameras detected
  - `COMInitializationException` - COM initialization failures
  - `CameraAccessDeniedException` - Permission/access denied
- Graceful handling of COM failures with detailed error messages
- HRESULT codes included in error messages for debugging

**Build System:**
- Modern scikit-build-core + CMake build system
- pybind11 for clean C++/Python integration
- pyproject.toml-only configuration (no setup.py)
- Python 3.8-3.13 support
- Proper wheel packaging (Python files + compiled extension only)

**Developer Tools:**
- `scripts/rebuild.py` - Quick rebuild utility for development
- `scripts/build_in_vm.py` - VM build script for Parallels/shared folder workarounds

**Documentation:**
- Comprehensive README with usage examples
- Architecture documentation in `docs/ARCHITECTURE.md`
- Development utilities documentation in `scripts/README.md`
- Example code in `examples/basic_usage.py`

### Technical Details

- **Platform:** Windows only (DirectShow APIs)
- **Python:** 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **License:** MIT
- **Build Requirements:** Windows SDK, CMake 3.18+, Visual Studio compiler

### Project Structure

```
windows-camera-enum/
├── src/
│   ├── camera_enum/        # Pure Python package
│   │   ├── __init__.py
│   │   └── py.typed
│   └── cpp/                # C++ extension source
│       └── camera_enum.cpp
├── examples/
│   └── basic_usage.py
├── scripts/
│   ├── rebuild.py
│   └── build_in_vm.py
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPROVEMENTS.md
└── README.md
```

### Credits

This project is a fork of [python-capture-device-list](https://github.com/yushulx/python-capture-device-list) by Xiao Ling (yushulx) with additional features and modern Python tooling.

---

## Release Notes

### What's Changed
- Complete rewrite with pybind11 for cleaner C++/Python integration
- Enhanced API with detailed camera information (resolutions, frame rates, formats, controls)
- Modern build system using scikit-build-core
- Comprehensive type hints and error handling
- Organized project structure with separate Python and C++ source directories
- Development utilities for rapid iteration

### Breaking Changes from Original
- Package renamed: `windows-capture-device-list` → `windows-camera-enum`
- Module renamed: `device` → `camera_enum`
- API changed: `getCameraList()` → `list_cameras()` with richer return structure
- Python 3.6-3.7 support dropped (EOL)

[1.0.4]: https://github.com/thecheapgeek/python-lite-camera/releases/tag/v1.0.4
[1.0.3]: https://github.com/thecheapgeek/python-lite-camera/releases/tag/v1.0.3
[1.0.2]: https://github.com/thecheapgeek/python-lite-camera/releases/tag/v1.0.2
[1.0.1]: https://github.com/thecheapgeek/python-lite-camera/releases/tag/v1.0.1
[1.0.0]: https://github.com/thecheapgeek/python-lite-camera/releases/tag/v1.0.0

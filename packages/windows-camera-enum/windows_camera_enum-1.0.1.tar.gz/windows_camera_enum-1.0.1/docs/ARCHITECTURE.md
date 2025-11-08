# Architecture Documentation

Technical reference for contributing to **windows-camera-enum**.

**Version:** 1.2.0
**Platform:** Windows (DirectShow APIs)
**Python Support:** 3.8+

## Project Overview

A Python C++ extension that uses Windows DirectShow COM APIs to enumerate camera devices and their supported resolutions, frame rates, formats, and controls.

**Original Project:** https://github.com/yushulx/python-capture-device-list by Xiao Ling (yushulx)

## Architecture

### Core Components

**1. C++ Extension Module (`src/camera_enum/camera_enum.cpp`)**

Uses Windows DirectShow COM APIs to enumerate video capture devices.

**Key DirectShow Interfaces:**
- `ICreateDevEnum` - System device enumerator
- `IEnumMoniker` - Iterates through device monikers
- `IPropertyBag` - Reads device properties (FriendlyName, Description)
- `IBaseFilter` - Device filter interface
- `IEnumPins` - Enumerates device pins
- `IEnumMediaTypes` - Enumerates supported media types for resolution detection
- `VIDEOINFOHEADER` - Contains resolution data (biWidth, biHeight)

**2. Python Wrapper (`src/camera_enum/__init__.py`)**

Provides type-hinted wrapper around C++ extension (pybind11).

**Main API:**
```python
def list_cameras() -> List[Dict[str, Any]]: ...
```

**Returns:** List of camera information dictionaries containing:
- `index` (int): Camera device index
- `name` (str): Camera friendly name
- `path` (str): Device path for identification
- `resolutions` (List[Dict]): Supported resolutions with width, height, frame_rates, and formats
- `controls` (Dict): Available camera controls (exposure, focus, brightness, etc.) with min/max/default values

**Exception Classes:**
- `CameraException` - Base exception
- `NoCameraFoundException` - No cameras detected
- `COMInitializationException` - COM initialization failed
- `CameraAccessDeniedException` - Permission/access denied

### Data Flow

1. `list_cameras()` called from Python
2. C++ function (`_list_cameras`) initializes COM (`CoInitializeEx`)
   - If fails: Throws `std::runtime_error` (converted to Python RuntimeError by pybind11)
3. Enumerates video input devices via DirectShow
   - If `VFW_E_NOT_FOUND`: Returns empty list (no cameras)
   - If other error: Throws `std::runtime_error`
4. For each device:
   - Reads friendly name and device path from IPropertyBag
   - Binds to IBaseFilter to query camera controls and enumerate pins
   - Queries media types for each pin to extract resolutions, frame rates, and pixel formats
   - Builds Python dict with all camera information
5. Returns Python list of camera info dicts
6. Python wrapper converts RuntimeError to custom exceptions based on error message
7. Raises `NoCameraFoundException` if result list is empty
8. COM cleanup (`CoUninitialize`)

### Error Handling

**C++ Layer (`camera_enum.cpp`):**
- Uses pybind11 exception handling with `std::runtime_error`
- Throws exceptions on critical errors (automatically converted to Python RuntimeError)
- Returns empty list for "no cameras found" (not an error)
- Includes HRESULT codes in error messages for debugging

**Python Layer (`src/camera_enum/__init__.py`):**
- Catches RuntimeError from C++ extension
- Converts to specific exception types based on error message
- Raises `NoCameraFoundException` for empty list
- Always includes helpful error messages for users

### Memory Management

The C++ code uses **manual COM reference counting**:
- All COM objects must call `Release()` when done
- `_FreeMediaType()` and `_DeleteMediaType()` handle media type cleanup
- `CoTaskMemFree()` used for COM-allocated memory

## Build System

The project uses **scikit-build-core** (modern CMake + pyproject.toml-only build).

**Key Files:**
- `pyproject.toml` - Project metadata and build configuration
- `CMakeLists.txt` - CMake build configuration

**Build Commands:**
```bash
pip install .               # Standard install
pip install -e .            # Development/editable mode
pip wheel . --verbose       # Build wheel
```

**CMakeLists.txt defines:**
- Extension module named `camera_enum`
- Source: `src/camera_enum/camera_enum.cpp`
- Installs to `src/camera_enum/` directory
- Uses `PythonExtensions` CMake module from scikit-build-core

**Dependencies:**

*Build-time:*
- scikit-build-core>=0.8.0
- pybind11>=2.11.0
- cmake>=3.18

*Runtime:*
- Windows SDK (for DirectShow headers)
- Python 3.8+

## Project Structure

```
windows-camera-enum/
├── src/
│   └── camera_enum/           # Source package (src layout)
│       ├── __init__.py         # Python API wrapper with type hints
│       ├── camera_enum.cpp     # C++ extension source
│       └── py.typed            # PEP 561 type marker
├── examples/
│   └── basic_usage.py          # Usage example with OpenCV
├── scripts/
│   ├── README.md               # Development utilities docs
│   ├── rebuild.py              # Quick rebuild utility
│   └── build_in_vm.py          # VM build script
├── tests/                      # Reserved for unit tests
├── docs/
│   ├── ARCHITECTURE.md         # This file
│   └── IMPROVEMENTS.md         # Planned enhancements
├── CMakeLists.txt              # CMake configuration
├── pyproject.toml              # Project configuration
└── README.md                   # User documentation
```

## Development

### Type Hints

All public APIs must have complete type annotations. The project includes `src/camera_enum/py.typed` for PEP 561 compliance.

### Quick Rebuild

For rapid development iteration:
```bash
python scripts/rebuild.py           # Standard install
python scripts/rebuild.py --dev     # Development/editable mode
python scripts/rebuild.py --verbose # Detailed output
```

This automates: uninstall → clean build artifacts → rebuild → install

### Testing

Run the example to verify functionality:
```bash
python examples/basic_usage.py
```

The `tests/` directory is reserved for future pytest-based unit tests.

## Technical Constraints

**Platform:** Windows only (uses DirectShow COM APIs)

**DirectShow Limitations:**
- Some cameras don't expose all capabilities through DirectShow
- Frame rate enumeration depends on driver quality
- Control availability varies by camera manufacturer

**Build System:**
- Requires Windows SDK for DirectShow headers
- CMake 3.18+ required for scikit-build-core
- Must use Visual Studio compiler on Windows

## Contributing

When contributing:
1. Follow PEP 8 style for Python code
2. Use descriptive variable and function names
3. Add type hints to all public APIs
4. Test with real camera hardware when possible

## Resources

- [DirectShow Documentation](https://learn.microsoft.com/en-us/windows/win32/directshow/directshow)
- [pybind11 Documentation](https://pybind11.readthedocs.io/)
- [scikit-build-core Documentation](https://scikit-build-core.readthedocs.io/)

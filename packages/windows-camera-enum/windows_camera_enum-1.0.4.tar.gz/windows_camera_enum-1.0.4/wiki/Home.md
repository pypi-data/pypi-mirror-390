# Windows Camera Enumeration - Documentation Wiki

[![PyPI version](https://badge.fury.io/py/windows-camera-enum.svg)](https://pypi.org/project/windows-camera-enum/)
[![Python Versions](https://img.shields.io/pypi/pyversions/windows-camera-enum.svg)](https://pypi.org/project/windows-camera-enum/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Welcome to the **windows-camera-enum** documentation wiki! This library provides comprehensive camera device enumeration for Windows using DirectShow APIs.

## Quick Start

```bash
pip install windows-camera-enum
```

```python
import camera_enum

cameras = camera_enum.list_cameras()
for camera in cameras:
    print(f"[{camera['index']}] {camera['name']}")
    for res in camera['resolutions']:
        print(f"  {res['width']}x{res['height']}")
```

## What is windows-camera-enum?

A Python library that fills the gap left by OpenCV - **native camera enumeration on Windows**. Get detailed information about:

- 📷 Connected camera devices
- 📐 Supported resolutions and frame rates
- 🎨 Pixel formats (MJPEG, YUY2, RGB24, etc.)
- 🎛️ Camera controls (zoom, focus, brightness, exposure)
- 🔍 Device paths and indices for identification

Perfect for computer vision applications, microscopy, surveillance systems, and any project requiring camera detection on Windows.

## Documentation Navigation

### 📚 User Documentation
- **[Getting Started](Getting-Started)** - Installation, setup, and your first program
- **[API Reference](API-Reference)** - Complete function and exception documentation
- **[Examples Gallery](Examples)** - Real-world code examples and use cases
- **[Troubleshooting & FAQ](Troubleshooting)** - Common issues and solutions

### 🔧 Developer Resources
- **[Camera Compatibility](Camera-Compatibility)** - Tested cameras and known issues
- **[Contributing Guide](Contributing)** - How to contribute to the project
- **[Architecture](https://github.com/thecheapgeek/python-lite-camera/blob/main/docs/ARCHITECTURE.md)** - Technical deep dive (in repo)

### 📦 Links
- **[PyPI Package](https://pypi.org/project/windows-camera-enum/)**
- **[GitHub Repository](https://github.com/thecheapgeek/python-lite-camera)**
- **[Changelog](https://github.com/thecheapgeek/python-lite-camera/blob/main/CHANGELOG.md)**
- **[Issue Tracker](https://github.com/thecheapgeek/python-lite-camera/issues)**

## Key Features

### Rich Camera Information
```python
{
    "index": 0,
    "name": "Logitech HD Webcam C920",
    "path": "\\\\?\\usb#vid_046d&pid_082d...",
    "resolutions": [
        {
            "width": 1920,
            "height": 1080,
            "frame_rates": [30.0, 24.0, 15.0],
            "formats": ["MJPEG", "YUY2"]
        }
    ],
    "controls": {
        "Zoom": {"min": 100, "max": 500, "default": 100},
        "Focus": {"min": 0, "max": 250, "default": 0, "auto": True}
    }
}
```

### Type-Safe API
- Full type hints for IDE autocomplete
- Custom exception classes for error handling
- PEP 561 compliant

### Modern Python
- Python 3.8 - 3.13 support
- Modern build system (scikit-build-core)
- Clean C++/Python integration via pybind11

## Platform Requirements

- **Operating System:** Windows 10/11
- **Python:** 3.8 or later
- **Dependencies:** Windows SDK (for DirectShow)

## Community

This is a fork of [python-capture-device-list](https://github.com/yushulx/python-capture-device-list) by Xiao Ling (yushulx), enhanced with modern Python features, comprehensive camera information, and better error handling.

### Contributing

We welcome contributions! See the [Contributing Guide](Contributing) for details on:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Adding to the camera compatibility list

## Support

- **Questions?** Check the [Troubleshooting & FAQ](Troubleshooting) page
- **Found a bug?** [Report it on GitHub](https://github.com/thecheapgeek/python-lite-camera/issues)
- **Need a feature?** [Request it on GitHub](https://github.com/thecheapgeek/python-lite-camera/issues)

---

**Latest Version:** 1.0.3 | **License:** MIT | **Author:** Jonathan

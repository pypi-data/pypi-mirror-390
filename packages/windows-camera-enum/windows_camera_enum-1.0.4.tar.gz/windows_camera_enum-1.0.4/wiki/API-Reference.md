# API Reference

Complete API documentation for **windows-camera-enum**.

## Module: `camera_enum`

```python
import camera_enum
```

## Functions

### `list_cameras()`

Enumerates all available camera devices on the system.

**Signature:**
```python
def list_cameras() -> List[Dict[str, Any]]: ...
```

**Returns:**
- `List[Dict[str, Any]]`: List of camera information dictionaries

**Raises:**
- `NoCameraFoundException`: No cameras detected on the system
- `COMInitializationException`: DirectShow COM initialization failed
- `CameraAccessDeniedException`: Camera access denied (check privacy settings)
- `CameraException`: General camera error

**Example:**
```python
import camera_enum

cameras = camera_enum.list_cameras()

for camera in cameras:
    print(f"{camera['index']}: {camera['name']}")
```

## Return Data Structure

Each camera dictionary contains the following keys:

### Camera Dictionary

```python
{
    "index": int,                    # Camera device index (0, 1, 2, ...)
    "name": str,                     # Human-readable camera name
    "path": str,                     # Unique Windows device path
    "resolutions": List[Dict],       # List of supported resolutions
    "controls": Dict[str, Dict]      # Available camera controls
}
```

### Resolution Dictionary

Each resolution in the `resolutions` list contains:

```python
{
    "width": int,                    # Frame width in pixels
    "height": int,                   # Frame height in pixels
    "frame_rates": List[float],      # Supported frame rates in FPS
    "formats": List[str]             # Pixel formats (e.g., "MJPEG", "YUY2")
}
```

**Common pixel formats:**
- `"MJPEG"` - Motion JPEG (compressed)
- `"YUY2"` - YUV 4:2:2 format
- `"RGB24"` - 24-bit RGB
- `"NV12"` - YUV 4:2:0 planar format
- `"I420"` - YUV 4:2:0 planar format

### Control Dictionary

Each control in the `controls` dictionary contains:

```python
{
    "min": int,                      # Minimum value
    "max": int,                      # Maximum value
    "step": int,                     # Step size for increments
    "default": int,                  # Factory default value
    "auto": bool                     # Whether automatic mode is available
}
```

**Common controls:**
- `"Zoom"` - Digital or optical zoom
- `"Focus"` - Manual or auto focus
- `"Exposure"` - Exposure time/value
- `"Brightness"` - Image brightness
- `"Contrast"` - Image contrast
- `"Saturation"` - Color saturation
- `"Sharpness"` - Image sharpness
- `"White Balance"` - Color temperature
- `"Backlight Compensation"` - Backlight adjustment
- `"Gain"` - Image gain/ISO

## Complete Example

```python
import camera_enum

cameras = camera_enum.list_cameras()

for camera in cameras:
    # Basic info
    print(f"\n{'=' * 60}")
    print(f"Camera Index: {camera['index']}")
    print(f"Name: {camera['name']}")
    print(f"Device Path: {camera['path']}")

    # Resolutions
    print(f"\nSupported Resolutions ({len(camera['resolutions'])} total):")
    for res in camera['resolutions']:
        fps_range = f"{min(res['frame_rates']):.0f}-{max(res['frame_rates']):.0f}"
        formats = ', '.join(res['formats'])
        print(f"  {res['width']}x{res['height']} @ {fps_range} FPS ({formats})")

    # Controls
    if camera['controls']:
        print(f"\nAvailable Controls ({len(camera['controls'])} total):")
        for control_name, control_info in camera['controls'].items():
            auto_str = " (Auto available)" if control_info.get('auto') else ""
            print(f"  {control_name}: {control_info['min']}-{control_info['max']}{auto_str}")
    else:
        print("\nNo controls available")
```

## Exception Classes

### Exception Hierarchy

```
BaseException
└── Exception
    └── CameraException                    # Base exception for all camera errors
        ├── NoCameraFoundException         # No cameras detected
        ├── COMInitializationException     # COM initialization failed
        └── CameraAccessDeniedException    # Camera access denied
```

### `CameraException`

Base exception for all camera-related errors.

**Usage:**
```python
try:
    cameras = camera_enum.list_cameras()
except camera_enum.CameraException as e:
    print(f"Camera error occurred: {e}")
```

### `NoCameraFoundException`

Raised when no cameras are detected on the system.

**When raised:**
- No physical cameras connected
- Cameras disabled in Device Manager
- Virtual cameras not running

**Handling:**
```python
try:
    cameras = camera_enum.list_cameras()
except camera_enum.NoCameraFoundException:
    print("Please connect a camera and try again")
```

### `COMInitializationException`

Raised when DirectShow COM initialization fails.

**When raised:**
- DirectShow not available (rare on Windows)
- COM subsystem error

**Handling:**
```python
try:
    cameras = camera_enum.list_cameras()
except camera_enum.COMInitializationException as e:
    print(f"DirectShow initialization failed: {e}")
    print("Try restarting your computer")
```

### `CameraAccessDeniedException`

Raised when camera access is denied.

**When raised:**
- Windows Privacy Settings block camera access
- Another application has exclusive camera access
- Insufficient permissions

**Handling:**
```python
try:
    cameras = camera_enum.list_cameras()
except camera_enum.CameraAccessDeniedException as e:
    print("Camera access denied")
    print("Check Windows Settings > Privacy > Camera")
```

## Type Hints

The module includes complete type hints for better IDE support and type checking.

**Type annotations:**
```python
from typing import List, Dict, Any

cameras: List[Dict[str, Any]] = camera_enum.list_cameras()

# Access with IDE autocomplete
camera_index: int = cameras[0]['index']
camera_name: str = cameras[0]['name']
```

**Type checking with mypy:**
```bash
pip install mypy
mypy your_script.py
```

## Module Attributes

### `__version__`

The version of the installed package.

```python
print(camera_enum.__version__)
# Output: '1.0.3'
```

## Platform Support

**Supported Platforms:**
- Windows 10 (64-bit)
- Windows 11 (64-bit)

**Python Versions:**
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

**Architecture:**
- x86_64 (64-bit) only

## Performance Considerations

### Caching Results

The `list_cameras()` function queries hardware each time. For frequent calls, cache the result:

```python
import camera_enum
from functools import lru_cache
import time

@lru_cache(maxsize=1)
def get_cameras_cached(cache_key):
    return camera_enum.list_cameras()

# Use with timestamp as cache key (cache for 5 seconds)
def get_cameras_with_ttl(ttl=5):
    cache_key = int(time.time() / ttl)
    return get_cameras_cached(cache_key)

# First call queries hardware
cameras = get_cameras_with_ttl()

# Subsequent calls within 5 seconds use cache
cameras = get_cameras_with_ttl()
```

### Lazy Loading

If you only need basic info, filter the results:

```python
# Get just camera names and indices
cameras = camera_enum.list_cameras()
camera_list = [
    {"index": c['index'], "name": c['name']}
    for c in cameras
]
```

## Thread Safety

The DirectShow API uses COM, which has threading requirements:

**Single-threaded usage (recommended):**
```python
# Call from main thread
cameras = camera_enum.list_cameras()
```

**Multi-threaded usage:**
```python
from threading import Thread

def enumerate_cameras():
    # Each thread must call independently
    cameras = camera_enum.list_cameras()
    print(f"Found {len(cameras)} cameras")

thread = Thread(target=enumerate_cameras)
thread.start()
thread.join()
```

## Related Documentation

- **[Getting Started](Getting-Started)** - Installation and basic usage
- **[Examples Gallery](Examples)** - Real-world code examples
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions
- **[Camera Compatibility](Camera-Compatibility)** - Tested cameras

## See Also

- [DirectShow Documentation](https://learn.microsoft.com/en-us/windows/win32/directshow/directshow)
- [OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)

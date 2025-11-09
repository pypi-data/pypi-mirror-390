# Getting Started with windows-camera-enum

This guide will help you install and start using **windows-camera-enum** in your Python projects.

## Prerequisites

### System Requirements

- **Operating System:** Windows 10 or Windows 11
- **Python:** Version 3.8 or later
- **Windows SDK:** Required for DirectShow (usually pre-installed)

### Check Your Python Version

```bash
python --version
```

You should see Python 3.8.0 or higher.

## Installation

### From PyPI (Recommended)

The easiest way to install:

```bash
pip install windows-camera-enum
```

### Verify Installation

```python
import camera_enum
print(camera_enum.__version__)
# Output: 1.0.3
```

### Upgrade to Latest Version

```bash
pip install --upgrade windows-camera-enum
```

## Your First Program

### List All Cameras

Create a file called `list_cameras.py`:

```python
import camera_enum

try:
    cameras = camera_enum.list_cameras()

    if not cameras:
        print("No cameras found!")
    else:
        print(f"Found {len(cameras)} camera(s):\n")

        for camera in cameras:
            print(f"[{camera['index']}] {camera['name']}")
            print(f"  Device Path: {camera['path']}")
            print(f"  Resolutions: {len(camera['resolutions'])} available")
            print()

except camera_enum.NoCameraFoundException:
    print("No cameras detected. Please connect a camera.")
except camera_enum.COMInitializationException as e:
    print(f"DirectShow initialization failed: {e}")
except camera_enum.CameraException as e:
    print(f"Camera error: {e}")
```

Run it:
```bash
python list_cameras.py
```

### Display Resolution Details

```python
import camera_enum

cameras = camera_enum.list_cameras()

for camera in cameras:
    print(f"\n{camera['name']} - Supported Resolutions:")
    print("-" * 60)

    for res in camera['resolutions']:
        # Format frame rates
        fps_str = ', '.join(f"{fps:.0f}" for fps in res['frame_rates'])

        # Format pixel formats
        formats_str = ', '.join(res['formats'])

        print(f"{res['width']:4d} x {res['height']:4d}  |  {fps_str:20s} FPS  |  {formats_str}")
```

### Display Camera Controls

```python
import camera_enum

cameras = camera_enum.list_cameras()

for camera in cameras:
    if camera['controls']:
        print(f"\n{camera['name']} - Available Controls:")
        print("-" * 60)

        for control_name, control_info in camera['controls'].items():
            print(f"{control_name}:")
            print(f"  Range: {control_info['min']} - {control_info['max']}")
            print(f"  Default: {control_info['default']}")
            print(f"  Step: {control_info['step']}")
            if control_info.get('auto'):
                print(f"  Auto Mode: Available")
    else:
        print(f"{camera['name']}: No controls available")
```

## Integration with OpenCV

### Basic Camera Preview

```python
import camera_enum
import cv2

# List cameras
cameras = camera_enum.list_cameras()

if not cameras:
    print("No cameras found!")
    exit(1)

# Display available cameras
print("Available cameras:")
for camera in cameras:
    print(f"  [{camera['index']}] {camera['name']}")

# Select first camera
camera_index = cameras[0]['index']
print(f"\nOpening camera {camera_index}...")

# Open with OpenCV
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print("Failed to open camera!")
    exit(1)

print("Camera opened! Press 'q' to quit.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Display frame
    cv2.imshow("Camera Preview", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Set Specific Resolution

```python
import camera_enum
import cv2

cameras = camera_enum.list_cameras()
camera = cameras[0]

# Find a specific resolution
target_width, target_height = 1920, 1080

# Check if resolution is supported
supported = any(
    res['width'] == target_width and res['height'] == target_height
    for res in camera['resolutions']
)

if not supported:
    print(f"{target_width}x{target_height} not supported!")
    print("Available resolutions:")
    for res in camera['resolutions']:
        print(f"  {res['width']}x{res['height']}")
    exit(1)

# Open camera
cap = cv2.VideoCapture(camera['index'])

# Set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_height)

# Verify resolution was set
actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Requested: {target_width}x{target_height}")
print(f"Actual: {actual_width}x{actual_height}")

# Continue with camera operations...
cap.release()
```

## Error Handling Best Practices

Always handle exceptions when working with cameras:

```python
import camera_enum

def safe_list_cameras():
    """Safely list cameras with comprehensive error handling."""
    try:
        cameras = camera_enum.list_cameras()
        return cameras

    except camera_enum.NoCameraFoundException:
        print("No cameras detected.")
        print("- Check if a camera is connected")
        print("- Check Windows Device Manager for camera status")
        return []

    except camera_enum.COMInitializationException as e:
        print(f"DirectShow initialization failed: {e}")
        print("- This may indicate DirectShow is not available")
        print("- Try restarting your computer")
        return []

    except camera_enum.CameraAccessDeniedException as e:
        print(f"Camera access denied: {e}")
        print("- Check Windows Privacy Settings")
        print("- Settings > Privacy > Camera")
        return []

    except camera_enum.CameraException as e:
        print(f"General camera error: {e}")
        return []

# Use it
cameras = safe_list_cameras()
```

## Common Patterns

### Find Camera by Name

```python
def find_camera_by_name(name_substring):
    """Find a camera whose name contains the given substring."""
    cameras = camera_enum.list_cameras()

    for camera in cameras:
        if name_substring.lower() in camera['name'].lower():
            return camera

    return None

# Example
logitech = find_camera_by_name("Logitech")
if logitech:
    print(f"Found: {logitech['name']}")
```

### Check Resolution Support

```python
def supports_resolution(camera, width, height):
    """Check if camera supports a specific resolution."""
    for res in camera['resolutions']:
        if res['width'] == width and res['height'] == height:
            return True
    return False

# Example
camera = camera_enum.list_cameras()[0]
if supports_resolution(camera, 1920, 1080):
    print("1080p supported!")
```

### Get Best Resolution

```python
def get_max_resolution(camera):
    """Get the highest resolution supported by camera."""
    if not camera['resolutions']:
        return None

    max_res = max(
        camera['resolutions'],
        key=lambda r: r['width'] * r['height']
    )

    return (max_res['width'], max_res['height'])

# Example
camera = camera_enum.list_cameras()[0]
width, height = get_max_resolution(camera)
print(f"Max resolution: {width}x{height}")
```

## Next Steps

- **[API Reference](API-Reference)** - Detailed API documentation
- **[Examples Gallery](Examples)** - More code examples
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions

## Need Help?

- Check the [Troubleshooting & FAQ](Troubleshooting) page
- [Report issues on GitHub](https://github.com/thecheapgeek/python-lite-camera/issues)

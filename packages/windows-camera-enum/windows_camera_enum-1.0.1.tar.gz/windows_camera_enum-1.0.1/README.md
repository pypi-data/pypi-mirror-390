# Windows Camera Enumeration

> **Note:** This is a fork of [python-capture-device-list](https://github.com/yushulx/python-capture-device-list) by [Xiao Ling (yushulx)](https://github.com/yushulx)
>
> This fork includes type hints, modern Python support (3.8+), comprehensive error handling, and a modernized build system.

A Python library for enumerating camera devices and their supported resolutions on Windows using DirectShow APIs. **OpenCV** does not provide a native API for camera enumeration - this library fills that gap.

## Environment
* [Microsoft Windows SDK](https://en.wikipedia.org/wiki/Microsoft_Windows_SDK)
* Python 3.8 or later

## How to Build the CPython Extension

The project uses modern **scikit-build-core** with everything configured in `pyproject.toml`.

**Build and install:**
```bash
pip install .
```

**Build wheel package:**
```bash
pip wheel . --verbose
```

**Build in development mode:**
```bash
pip install -e . --verbose
```

## Development Utilities

**Quick rebuild (uninstall + clean + build + install):**
```bash
python scripts/rebuild.py           # Standard install
python scripts/rebuild.py --dev     # Development/editable mode
python scripts/rebuild.py --verbose # Show detailed build output
```

## Usage

### Basic Example with Error Handling

```python
import camera_enum

try:
    cameras = camera_enum.list_cameras()
    for camera in cameras:
        print(f"[{camera['index']}] {camera['name']}")
        print(f"  Path: {camera['path']}")

        # Display resolutions with frame rates and formats
        for res in camera['resolutions']:
            fps_str = ', '.join(f"{fps:.1f}" for fps in res['frame_rates'])
            formats_str = ', '.join(res['formats'])
            print(f"  {res['width']}x{res['height']}: {fps_str} FPS ({formats_str})")
except camera_enum.NoCameraFoundException:
    print("No cameras found. Please connect a camera.")
except camera_enum.COMInitializationException as e:
    print(f"COM initialization failed: {e}")
except camera_enum.CameraException as e:
    print(f"Camera error: {e}")
```

### Exception Classes

The module provides the following exception classes:

- **`CameraException`** - Base exception for all camera-related errors
- **`NoCameraFoundException`** - Raised when no cameras are detected
- **`COMInitializationException`** - Raised when COM initialization fails
- **`CameraAccessDeniedException`** - Raised when camera access is denied

## Test
```py
import camera_enum
import cv2

def select_camera(last_index):
    number = 0
    hint = "Select a camera (0 to " + str(last_index) + "): "
    try:
        number = int(input(hint))
        # select = int(select)
    except Exception:
        print("It's not a number!")
        return select_camera(last_index)

    if number > last_index:
        print("Invalid number! Retry!")
        return select_camera(last_index)

    return number


def open_camera(index):
    cap = cv2.VideoCapture(index)
    return cap

def main():
    # print OpenCV version
    print("OpenCV version: " + cv2.__version__)

    # Get camera list with error handling
    try:
        cameras = camera_enum.list_cameras()
    except camera_enum.NoCameraFoundException:
        print("No camera devices found. Please connect a camera and try again.")
        return
    except camera_enum.COMInitializationException as e:
        print(f"COM initialization error: {e}")
        print("DirectShow may not be available on this system.")
        return
    except camera_enum.CameraException as e:
        print(f"Camera error: {e}")
        return

    # Display camera list
    for camera in cameras:
        print(f"{camera['index']}: {camera['name']}")
        for res in camera['resolutions']:
            print(f"  {res['width']}x{res['height']}")

    last_index = len(cameras) - 1

    if last_index < 0:
        print("No device is connected")
        return

    # Select a camera
    camera_number = select_camera(last_index)
    
    # Open camera
    cap = open_camera(camera_number)

    if cap.isOpened():
        width = cap.get(3) # Frame Width
        height = cap.get(4) # Frame Height
        print('Default width: ' + str(width) + ', height: ' + str(height))

        while True:
            
            ret, frame = cap.read()
            cv2.imshow("frame", frame)

            # key: 'ESC'
            key = cv2.waitKey(20)
            if key == 27:
                break

        cap.release() 
        cv2.destroyAllWindows() 

if __name__ == "__main__":
    main()

```

Run the example:
```bash
python examples/basic_usage.py
```

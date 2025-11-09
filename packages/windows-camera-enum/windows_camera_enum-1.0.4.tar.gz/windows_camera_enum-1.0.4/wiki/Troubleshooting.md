# Troubleshooting & FAQ

Common issues and solutions when using **windows-camera-enum**.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Camera Detection Issues](#camera-detection-issues)
- [Permission and Access Issues](#permission-and-access-issues)
- [Performance Issues](#performance-issues)
- [Integration Issues](#integration-issues)
- [Build from Source Issues](#build-from-source-issues)
- [Frequently Asked Questions](#frequently-asked-questions)

---

## Installation Issues

### Pip Install Fails

**Problem:**
```
ERROR: Could not find a version that satisfies the requirement windows-camera-enum
```

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   # Must be 3.8 or higher
   ```

2. **Check platform:**
   ```bash
   python -c "import platform; print(platform.system())"
   # Must output: Windows
   ```

3. **Upgrade pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

4. **Check architecture (64-bit only):**
   ```bash
   python -c "import platform; print(platform.architecture()[0])"
   # Must output: 64bit
   ```

### Import Error After Installation

**Problem:**
```python
import camera_enum
# ModuleNotFoundError: No module named 'camera_enum'
```

**Solutions:**

1. **Verify installation:**
   ```bash
   pip show windows-camera-enum
   ```

2. **Check you're using the right Python:**
   ```bash
   python -m pip show windows-camera-enum
   ```

3. **Reinstall:**
   ```bash
   pip uninstall windows-camera-enum
   pip install windows-camera-enum
   ```

---

## Camera Detection Issues

### NoCameraFoundException Raised

**Problem:**
```python
camera_enum.NoCameraFoundException: No cameras detected
```

**Diagnostic Steps:**

1. **Check Device Manager:**
   - Press `Win + X` → Device Manager
   - Look under "Cameras" or "Imaging devices"
   - Is your camera listed?
   - Does it have a yellow warning icon?

2. **Check if camera is enabled:**
   - Right-click camera in Device Manager
   - Is "Enable device" visible? If so, click it

3. **Check if another app is using the camera:**
   - Close Zoom, Teams, Skype, etc.
   - Try again

4. **Test with built-in Windows app:**
   - Open Windows Camera app
   - Can you see video? If not, it's a hardware/driver issue

5. **Check USB connection:**
   - Try a different USB port
   - Try unplugging and replugging
   - Use a direct port (not a USB hub)

6. **Update drivers:**
   - Right-click camera in Device Manager
   - "Update driver" → "Search automatically"

### Camera Detected But Missing Information

**Problem:**
```python
cameras = camera_enum.list_cameras()
# Camera found but resolutions list is empty
```

**Causes:**
- Poor DirectShow driver support
- Virtual camera with limited capabilities
- Camera in use by another application

**Solutions:**

1. **Check if camera is in use:**
   ```python
   import camera_enum
   import cv2

   cameras = camera_enum.list_cameras()
   cap = cv2.VideoCapture(cameras[0]['index'])

   if cap.isOpened():
       print("Camera is accessible")
       cap.release()
   else:
       print("Camera is in use or inaccessible")
   ```

2. **Try with a different camera** to rule out driver issues

3. **Check DirectShow support:**
   - Some virtual cameras (OBS Virtual Camera, etc.) have limited DirectShow support
   - Try with a physical camera

---

## Permission and Access Issues

### CameraAccessDeniedException

**Problem:**
```python
camera_enum.CameraAccessDeniedException: Camera access denied
```

**Solution - Check Windows Privacy Settings:**

1. **Open Settings:**
   - Press `Win + I`
   - Go to "Privacy & Security" → "Camera"

2. **Enable camera access:**
   - Turn ON "Camera access"
   - Turn ON "Let apps access your camera"
   - Turn ON "Let desktop apps access your camera"

3. **Restart your application**

**Solution - Check Antivirus/Security Software:**

Some security software blocks camera access:
- Temporarily disable antivirus
- Check if the issue persists
- Add exception for Python if needed

### Access Denied for Specific Camera

**Problem:**
Only one camera raises access denied, others work fine.

**Solutions:**

1. **Camera exclusive access:**
   - Another app has exclusive lock
   - Close all apps that might use camera
   - Check Task Manager for background processes

2. **Driver issue:**
   - Update camera driver
   - Uninstall and reinstall driver

---

## Performance Issues

### Slow Camera Enumeration

**Problem:**
`list_cameras()` takes several seconds to complete.

**Causes:**
- Many cameras connected
- Slow camera drivers
- Network cameras timing out

**Solutions:**

1. **Cache results:**
   ```python
   import camera_enum
   import time

   # Cache for 10 seconds
   cache = {"cameras": None, "timestamp": 0}

   def get_cameras_cached(ttl=10):
       now = time.time()
       if cache["cameras"] is None or (now - cache["timestamp"]) > ttl:
           cache["cameras"] = camera_enum.list_cameras()
           cache["timestamp"] = now
       return cache["cameras"]
   ```

2. **Disconnect unused cameras**

3. **Use async enumeration if calling frequently:**
   ```python
   import camera_enum
   from concurrent.futures import ThreadPoolExecutor

   executor = ThreadPoolExecutor(max_workers=1)

   def async_enumerate():
       future = executor.submit(camera_enum.list_cameras)
       return future

   # Start enumeration
   future = async_enumerate()

   # Do other work...

   # Get result when needed
   cameras = future.result()
   ```

---

## Integration Issues

### OpenCV Can't Open Camera

**Problem:**
Camera detected by `camera_enum` but OpenCV can't open it.

```python
cameras = camera_enum.list_cameras()  # Works
cap = cv2.VideoCapture(cameras[0]['index'])  # Fails
```

**Solutions:**

1. **Try different backend:**
   ```python
   import cv2

   # Try DirectShow explicitly
   cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

   # Or try MSMF
   cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)
   ```

2. **Check OpenCV version:**
   ```python
   import cv2
   print(cv2.__version__)
   # Upgrade if old: pip install --upgrade opencv-python
   ```

3. **Close other applications** using the camera

### Resolution Not Applied in OpenCV

**Problem:**
Set resolution but camera uses different one.

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# Still gets 640x480
```

**Solutions:**

1. **Set resolution BEFORE reading frames:**
   ```python
   cap = cv2.VideoCapture(index)

   # Set resolution immediately
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

   # Verify
   w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
   h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
   print(f"Resolution: {int(w)}x{int(h)}")

   # Now read frames
   ret, frame = cap.read()
   ```

2. **Check if resolution is supported:**
   ```python
   import camera_enum

   cameras = camera_enum.list_cameras()
   camera = cameras[0]

   supported = any(
       r['width'] == 1920 and r['height'] == 1080
       for r in camera['resolutions']
   )

   if not supported:
       print("1920x1080 not supported by this camera")
   ```

3. **Use DirectShow backend:**
   ```python
   cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
   ```

---

## Build from Source Issues

### CMake Not Found

**Problem:**
```
CMake must be installed to build
```

**Solution:**
```bash
pip install cmake
```

### Visual Studio Not Found

**Problem:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Solution:**

1. **Install Visual Studio Build Tools:**
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Select "Build Tools for Visual Studio"
   - Install "C++ build tools" workload

2. **Or install full Visual Studio Community** (free)

### Windows SDK Headers Not Found

**Problem:**
```
fatal error C1083: Cannot open include file: 'dshow.h'
```

**Solution:**

1. **Install Windows SDK:**
   - Usually comes with Visual Studio
   - Or download standalone: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/

2. **Verify installation:**
   - Check `C:\Program Files (x86)\Windows Kits\10\Include\`
   - Should have DirectShow headers

---

## Frequently Asked Questions

### Does this work on Linux or macOS?

**No.** This library uses Windows DirectShow APIs and only works on Windows.

For Linux, use Video4Linux (V4L2). For macOS, use AVFoundation.

### Can I use this with virtual cameras (OBS, Snap Camera)?

**Yes**, but with limitations:
- Virtual cameras may not report all resolutions correctly
- Some controls might not be available
- DirectShow support varies by virtual camera software

Test with a physical camera first to ensure your code works.

### Why is my USB microscope not detected?

USB microscopes should be detected if they:
- Have UVC (USB Video Class) drivers
- Appear in Windows Device Manager under "Cameras"

Some industrial cameras require proprietary SDKs and won't appear in DirectShow.

### Can I control camera settings (zoom, focus, etc.)?

**Currently no.** The library only **reads** camera capabilities.

Control functions are planned for a future release. See [IMPROVEMENTS.md](https://github.com/thecheapgeek/python-lite-camera/blob/main/docs/IMPROVEMENTS.md).

For now, use OpenCV to control some settings:
```python
import cv2

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_ZOOM, 100)
cap.set(cv2.CAP_PROP_FOCUS, 50)
```

### Does this work with IP/Network cameras?

**No.** This library only enumerates **local USB/built-in cameras** via DirectShow.

For network cameras, use RTSP/HTTP streaming libraries.

### How do I know which camera index to use?

Use `list_cameras()` to see all cameras with their indices:

```python
import camera_enum

cameras = camera_enum.list_cameras()
for camera in cameras:
    print(f"Index {camera['index']}: {camera['name']}")
```

Then use the index with OpenCV or other libraries.

### Why do some cameras show no frame rates?

Some cameras/drivers don't expose frame rate information through DirectShow. This is a driver limitation, not a library issue.

The camera will still work; you just won't know all supported frame rates in advance.

### Can this library open the camera for capture?

**No.** This library only **enumerates** cameras. Use OpenCV, Pillow, or another library to actually capture frames.

```python
import camera_enum
import cv2

# Enumerate with camera_enum
cameras = camera_enum.list_cameras()

# Capture with OpenCV
cap = cv2.VideoCapture(cameras[0]['index'])
ret, frame = cap.read()
```

---

## Still Having Issues?

1. **Search existing issues:** [GitHub Issues](https://github.com/thecheapgeek/python-lite-camera/issues)
2. **Report a bug:** [Create new issue](https://github.com/thecheapgeek/python-lite-camera/issues/new)

When reporting issues, include:
- Python version (`python --version`)
- Package version (`pip show windows-camera-enum`)
- Windows version
- Full error message with traceback
- Camera model/type
- Minimal code to reproduce the issue

## Related Pages

- **[Getting Started](Getting-Started)** - Installation and setup
- **[API Reference](API-Reference)** - Complete API documentation
- **[Examples](Examples)** - Code examples
- **[Camera Compatibility](Camera-Compatibility)** - Tested cameras

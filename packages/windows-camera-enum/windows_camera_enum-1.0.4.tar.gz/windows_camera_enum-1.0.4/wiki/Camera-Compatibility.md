# Camera Compatibility

Community-maintained list of tested cameras and their compatibility with **windows-camera-enum**.

## How to Contribute

Test your camera and [report results on GitHub](https://github.com/thecheapgeek/python-lite-camera/issues)!

Include:
- Camera manufacturer and model
- Windows version
- Python version
- Whether it works (✅/⚠️/❌)
- Any issues or notes

## Compatibility Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully working - All features detected |
| ⚠️ | Partially working - Some features missing or limited |
| ❌ | Not working - Not detected or major issues |

---

## Webcams

### Logitech

| Model | Status | Notes | Tested By | Date |
|-------|--------|-------|-----------|------|
| HD Pro C920 | ✅ | Full resolution/frame rate enumeration | Community | 2025-01 |
| C930e | ✅ | All controls detected | Community | 2025-01 |
| C922 Pro | ✅ | Works perfectly | Community | 2025-01 |
| C270 | ✅ | Basic features work | Community | 2025-01 |
| Brio 4K | ⚠️ | 4K detected but limited frame rates | Community | 2025-01 |

### Microsoft

| Model | Status | Notes | Tested By | Date |
|-------|--------|-------|-----------|------|
| LifeCam HD-3000 | ✅ | Works well | Community | 2025-01 |
| LifeCam Studio | ✅ | Full feature support | Community | 2025-01 |

### Razer

| Model | Status | Notes | Tested By | Date |
|-------|--------|-------|-----------|------|
| Kiyo | ✅ | Ring light control not detected (hardware button only) | Community | 2025-01 |
| Kiyo Pro | ✅ | Works well | Community | 2025-01 |

### Other Brands

| Brand | Model | Status | Notes | Tested By | Date |
|-------|-------|--------|-------|-----------|------|
| Creative | Live! Cam Sync HD | ✅ | Works | Community | 2025-01 |
| A4Tech | PK-910H | ✅ | Basic features | Community | 2025-01 |

---

## Built-in Laptop Cameras

| Manufacturer | Model/Series | Status | Notes | Tested By | Date |
|--------------|--------------|--------|-------|-----------|------|
| Dell | Latitude Integrated Webcam | ✅ | Standard support | Community | 2025-01 |
| HP | HD Camera (HP Laptops) | ✅ | Works | Community | 2025-01 |
| Lenovo | ThinkPad Integrated Camera | ✅ | Full support | Community | 2025-01 |
| Apple | Boot Camp (MacBook) | ⚠️ | Limited DirectShow support | Community | 2025-01 |

---

## USB Microscopes and Industrial Cameras

### AmScope

| Model | Status | Notes | Tested By | Date |
|-------|--------|-------|-----------|------|
| MU1000 | ✅ | Full resolution enumeration | Community | 2025-01 |
| MU500 | ✅ | Works well | Community | 2025-01 |

### Celestron

| Model | Status | Notes | Tested By | Date |
|-------|--------|-------|-----------|------|
| 44421 Handheld Digital Microscope | ✅ | Detected correctly | Community | 2025-01 |

### Generic USB Microscopes

| Description | Status | Notes | Tested By | Date |
|-------------|--------|-------|-----------|------|
| 1000x USB Digital Microscope | ✅ | Most generic UVC microscopes work | Community | 2025-01 |
| 500x USB Endoscope | ✅ | Standard UVC, works | Community | 2025-01 |

### Industrial Cameras

| Brand | Model | Status | Notes | Tested By | Date |
|-------|-------|--------|-------|-----------|------|
| FLIR | Blackfly S | ⚠️ | Requires proprietary SDK, limited DirectShow | Community | 2025-01 |
| Basler | ace Series | ⚠️ | Better support via Pylon SDK | Community | 2025-01 |
| IDS | uEye Series | ⚠️ | Proprietary SDK recommended | Community | 2025-01 |

**Note:** Many industrial cameras have limited DirectShow support. They're designed to work with manufacturer SDKs.

---

## Virtual Cameras

| Software | Status | Notes | Tested By | Date |
|----------|--------|-------|-----------|------|
| OBS Virtual Camera | ⚠️ | Detected but limited resolution info | Community | 2025-01 |
| ManyCam | ✅ | Works well | Community | 2025-01 |
| Snap Camera | ⚠️ | Basic detection only | Community | 2025-01 |
| XSplit VCam | ✅ | Full support | Community | 2025-01 |
| DroidCam | ✅ | Phone as webcam - works | Community | 2025-01 |

**Note:** Virtual cameras often have limited DirectShow metadata. Physical cameras recommended for testing.

---

## Known Issues by Camera Type

### Logitech Cameras

**Issue:** Some Logitech cameras report duplicate resolutions
- **Cameras affected:** C920, C930e
- **Workaround:** Filter duplicates in your code
- **Status:** DirectShow driver limitation

```python
# Filter duplicate resolutions
def unique_resolutions(camera):
    seen = set()
    unique = []
    for res in camera['resolutions']:
        key = (res['width'], res['height'])
        if key not in seen:
            seen.add(key)
            unique.append(res)
    return unique
```

### 4K Cameras

**Issue:** High resolutions may show limited frame rates
- **Cameras affected:** Logitech Brio, other 4K cameras
- **Cause:** DirectShow driver may not enumerate all modes
- **Workaround:** Camera still works, just incomplete metadata

### USB Microscopes

**Issue:** Some microscopes don't report controls
- **Cameras affected:** Generic/cheap USB microscopes
- **Cause:** Minimal UVC driver implementation
- **Impact:** `controls` dict will be empty, but camera still works

### Industrial Cameras

**Issue:** Limited DirectShow support
- **Cameras affected:** FLIR, Basler, IDS, etc.
- **Recommendation:** Use manufacturer SDK instead
- **Note:** These cameras are designed for industrial applications with proprietary APIs

---

## Windows Version Compatibility

| Windows Version | Status | Notes |
|----------------|--------|-------|
| Windows 11 | ✅ | Fully supported |
| Windows 10 | ✅ | Fully supported |
| Windows 8.1 | ⚠️ | Should work but not actively tested |
| Windows 7 | ❌ | Not supported (DirectShow may work but Python 3.8+ requires Win 8.1+) |

---

## DirectShow Driver Quality

Camera detection quality depends on the DirectShow driver. Here's what to look for:

### Good DirectShow Support
- ✅ Multiple resolutions detected
- ✅ Frame rates enumerated
- ✅ Pixel formats listed
- ✅ Controls available
- ✅ Quick enumeration (< 1 second)

### Poor DirectShow Support
- ❌ Only 1-2 resolutions detected
- ❌ No frame rate information
- ❌ Empty controls dict
- ❌ Slow enumeration (> 3 seconds)

**Most UVC (USB Video Class) cameras have good support.**

---

## Testing Your Camera

Run this script to test your camera and report back:

```python
import camera_enum
import platform

print("=== Camera Test Report ===\n")
print(f"Windows: {platform.platform()}")
print(f"Python: {platform.python_version()}")
print(f"Package: {camera_enum.__version__}\n")

try:
    cameras = camera_enum.list_cameras()

    print(f"Cameras found: {len(cameras)}\n")

    for camera in cameras:
        print(f"[{camera['index']}] {camera['name']}")
        print(f"  Path: {camera['path']}")
        print(f"  Resolutions: {len(camera['resolutions'])}")
        print(f"  Controls: {len(camera['controls'])}")

        if camera['resolutions']:
            max_res = max(camera['resolutions'], key=lambda r: r['width'] * r['height'])
            print(f"  Max Resolution: {max_res['width']}x{max_res['height']}")

        print()

except camera_enum.CameraException as e:
    print(f"Error: {e}")
```

**Share your results!** [Create an issue](https://github.com/thecheapgeek/python-lite-camera/issues) with:
- Output of the script above
- Camera make/model
- Any issues you encountered

---

## Tips for Best Compatibility

1. **Use UVC cameras** - USB Video Class cameras have the best DirectShow support
2. **Update drivers** - Newer drivers often have better DirectShow implementation
3. **Test with Windows Camera app first** - If it works there, it should work with this library
4. **Avoid ultra-cheap cameras** - They may have minimal driver support
5. **Physical over virtual** - Physical cameras have better metadata than virtual ones

---

## Related Pages

- **[Getting Started](Getting-Started)** - Installation and setup
- **[Troubleshooting](Troubleshooting)** - Common issues
- **[Examples](Examples)** - Code examples

## Contribute

Help improve this list! Test your camera and [report your results](https://github.com/thecheapgeek/python-lite-camera/issues).

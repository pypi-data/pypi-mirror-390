# Examples Gallery

Practical code examples for common use cases with **windows-camera-enum**.

## Table of Contents

- [Basic Examples](#basic-examples)
- [OpenCV Integration](#opencv-integration)
- [Multi-Camera Handling](#multi-camera-handling)
- [GUI Applications](#gui-applications)
- [Advanced Use Cases](#advanced-use-cases)
- [Utility Functions](#utility-functions)

---

## Basic Examples

### Simple Camera Listing

```python
import camera_enum

cameras = camera_enum.list_cameras()

print(f"Found {len(cameras)} camera(s):\n")

for camera in cameras:
    print(f"[{camera['index']}] {camera['name']}")
```

### Pretty Print Camera Information

```python
import camera_enum
import json

cameras = camera_enum.list_cameras()

# Pretty print as JSON
for camera in cameras:
    print(json.dumps(camera, indent=2))
    print()
```

### Check if Cameras Available

```python
import camera_enum

def has_camera():
    """Check if any cameras are available."""
    try:
        cameras = camera_enum.list_cameras()
        return len(cameras) > 0
    except camera_enum.CameraException:
        return False

if has_camera():
    print("Cameras available!")
else:
    print("No cameras found")
```

---

## OpenCV Integration

### Basic Camera Preview

```python
import camera_enum
import cv2

def show_camera_preview(camera_index=0):
    """Show live preview from specified camera."""
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"Failed to open camera {camera_index}")
        return

    print("Press 'q' to quit")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Camera Preview", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Show preview from first camera
cameras = camera_enum.list_cameras()
if cameras:
    show_camera_preview(cameras[0]['index'])
```

### Camera Selector Menu

```python
import camera_enum
import cv2

def select_and_preview():
    """Let user select a camera and show preview."""
    cameras = camera_enum.list_cameras()

    if not cameras:
        print("No cameras found!")
        return

    # Show available cameras
    print("Available cameras:")
    for camera in cameras:
        print(f"  {camera['index']}: {camera['name']}")

    # Get user selection
    while True:
        try:
            choice = int(input("\nSelect camera index: "))
            if any(c['index'] == choice for c in cameras):
                break
            print("Invalid index!")
        except ValueError:
            print("Please enter a number")

    # Open selected camera
    cap = cv2.VideoCapture(choice)

    if not cap.isOpened():
        print("Failed to open camera")
        return

    print(f"Opened camera {choice}. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow(f"Camera {choice}", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

select_and_preview()
```

### Set Best Resolution

```python
import camera_enum
import cv2

def open_camera_max_resolution(camera_index):
    """Open camera with its maximum resolution."""
    cameras = camera_enum.list_cameras()

    # Find camera info
    camera = next((c for c in cameras if c['index'] == camera_index), None)

    if not camera:
        print(f"Camera {camera_index} not found")
        return None

    # Get maximum resolution
    if not camera['resolutions']:
        print("No resolution info available")
        return None

    max_res = max(
        camera['resolutions'],
        key=lambda r: r['width'] * r['height']
    )

    # Open camera
    cap = cv2.VideoCapture(camera_index)

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, max_res['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, max_res['height'])

    # Verify
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Requested: {max_res['width']}x{max_res['height']}")
    print(f"Actual: {actual_w}x{actual_h}")

    return cap

# Use it
cameras = camera_enum.list_cameras()
if cameras:
    cap = open_camera_max_resolution(cameras[0]['index'])
    if cap:
        ret, frame = cap.read()
        if ret:
            print(f"Frame shape: {frame.shape}")
        cap.release()
```

### Save Snapshot with Timestamp

```python
import camera_enum
import cv2
from datetime import datetime

def capture_snapshot(camera_index, output_dir="snapshots"):
    """Capture a snapshot and save with timestamp."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Failed to open camera")
        return None

    # Grab frame
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture frame")
        return None

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/snapshot_{timestamp}.jpg"

    # Save
    cv2.imwrite(filename, frame)
    print(f"Saved: {filename}")

    return filename

# Capture from first camera
cameras = camera_enum.list_cameras()
if cameras:
    capture_snapshot(cameras[0]['index'])
```

---

## Multi-Camera Handling

### Record from Multiple Cameras

```python
import camera_enum
import cv2
import threading

def record_camera(camera_index, window_name):
    """Record from a single camera in a thread."""
    cap = cv2.VideoCapture(camera_index)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(window_name)

def record_all_cameras():
    """Show preview from all cameras simultaneously."""
    cameras = camera_enum.list_cameras()

    if not cameras:
        print("No cameras found")
        return

    print(f"Opening {len(cameras)} camera(s). Press 'q' in any window to quit.")

    threads = []
    for camera in cameras:
        window_name = f"Camera {camera['index']}: {camera['name']}"
        thread = threading.Thread(
            target=record_camera,
            args=(camera['index'], window_name)
        )
        thread.start()
        threads.append(thread)

    # Wait for threads
    for thread in threads:
        thread.join()

record_all_cameras()
```

### Compare Cameras Side-by-Side

```python
import camera_enum
import cv2
import numpy as np

def show_cameras_side_by_side():
    """Display all cameras in a single window."""
    cameras = camera_enum.list_cameras()

    if len(cameras) < 2:
        print("Need at least 2 cameras")
        return

    # Open all cameras
    caps = [cv2.VideoCapture(c['index']) for c in cameras]

    print("Press 'q' to quit")

    while True:
        frames = []

        # Grab frame from each camera
        for cap in caps:
            ret, frame = cap.read()
            if ret:
                # Resize to consistent size
                frame = cv2.resize(frame, (640, 480))
                frames.append(frame)

        if not frames:
            break

        # Stack horizontally
        combined = np.hstack(frames)

        cv2.imshow("All Cameras", combined)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

show_cameras_side_by_side()
```

---

## GUI Applications

### Tkinter Camera Selector

```python
import camera_enum
import tkinter as tk
from tkinter import ttk

def create_camera_selector():
    """Create a GUI camera selector."""
    root = tk.Tk()
    root.title("Camera Selector")

    cameras = camera_enum.list_cameras()

    if not cameras:
        label = tk.Label(root, text="No cameras found!", fg="red")
        label.pack(padx=20, pady=20)
        root.mainloop()
        return

    # Camera selection
    tk.Label(root, text="Select Camera:").pack(pady=10)

    camera_var = tk.StringVar()
    camera_names = [f"{c['index']}: {c['name']}" for c in cameras]
    camera_combo = ttk.Combobox(root, textvariable=camera_var, values=camera_names, width=40)
    camera_combo.pack(padx=20)
    camera_combo.current(0)

    # Resolution display
    res_text = tk.Text(root, height=10, width=50)
    res_text.pack(padx=20, pady=10)

    def show_resolutions():
        """Display resolutions for selected camera."""
        selected_index = camera_combo.current()
        camera = cameras[selected_index]

        res_text.delete(1.0, tk.END)
        res_text.insert(tk.END, f"Resolutions for {camera['name']}:\n\n")

        for res in camera['resolutions']:
            fps_str = f"{min(res['frame_rates']):.0f}-{max(res['frame_rates']):.0f} FPS"
            res_text.insert(tk.END, f"{res['width']}x{res['height']} @ {fps_str}\n")

    # Button to update
    btn = tk.Button(root, text="Show Resolutions", command=show_resolutions)
    btn.pack(pady=10)

    # Show initial selection
    show_resolutions()

    root.mainloop()

create_camera_selector()
```

---

## Advanced Use Cases

### Camera Hot-Plug Detection

```python
import camera_enum
import time

def monitor_cameras(interval=2):
    """Monitor for camera connections/disconnections."""
    previous_cameras = set()

    print("Monitoring cameras... (Ctrl+C to stop)\n")

    try:
        while True:
            try:
                cameras = camera_enum.list_cameras()
                current_cameras = {c['name'] for c in cameras}

                # Detect new cameras
                added = current_cameras - previous_cameras
                for name in added:
                    print(f"[CONNECTED] {name}")

                # Detect removed cameras
                removed = previous_cameras - current_cameras
                for name in removed:
                    print(f"[DISCONNECTED] {name}")

                previous_cameras = current_cameras

            except camera_enum.CameraException:
                pass

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped monitoring")

monitor_cameras()
```

### Export Camera Info to JSON

```python
import camera_enum
import json

def export_camera_info(filename="camera_info.json"):
    """Export all camera information to JSON file."""
    cameras = camera_enum.list_cameras()

    with open(filename, 'w') as f:
        json.dump(cameras, f, indent=2)

    print(f"Exported {len(cameras)} camera(s) to {filename}")

export_camera_info()
```

### Generate HTML Report

```python
import camera_enum

def generate_html_report(filename="camera_report.html"):
    """Generate HTML report of all cameras."""
    cameras = camera_enum.list_cameras()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .camera { border: 1px solid #ccc; padding: 15px; margin: 10px 0; }
            .camera h2 { margin-top: 0; }
            table { border-collapse: collapse; width: 100%; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
        </style>
    </head>
    <body>
        <h1>Camera Report</h1>
    """

    for camera in cameras:
        html += f"""
        <div class="camera">
            <h2>[{camera['index']}] {camera['name']}</h2>
            <p><strong>Device Path:</strong> {camera['path']}</p>

            <h3>Resolutions</h3>
            <table>
                <tr>
                    <th>Resolution</th>
                    <th>Frame Rates</th>
                    <th>Formats</th>
                </tr>
        """

        for res in camera['resolutions']:
            fps = ', '.join(f"{f:.0f}" for f in res['frame_rates'])
            formats = ', '.join(res['formats'])
            html += f"""
                <tr>
                    <td>{res['width']} x {res['height']}</td>
                    <td>{fps} FPS</td>
                    <td>{formats}</td>
                </tr>
            """

        html += """
            </table>
        </div>
        """

    html += """
    </body>
    </html>
    """

    with open(filename, 'w') as f:
        f.write(html)

    print(f"Generated {filename}")

generate_html_report()
```

---

## Utility Functions

### Camera Information Cache

```python
import camera_enum
import time
import pickle

class CameraCache:
    """Cache camera information with TTL."""

    def __init__(self, ttl=60):
        self.ttl = ttl
        self.cache = None
        self.timestamp = 0

    def get_cameras(self):
        """Get cameras (from cache if fresh)."""
        now = time.time()

        if self.cache is None or (now - self.timestamp) > self.ttl:
            self.cache = camera_enum.list_cameras()
            self.timestamp = now

        return self.cache

    def invalidate(self):
        """Force refresh on next call."""
        self.cache = None
        self.timestamp = 0

    def save_to_file(self, filename):
        """Save cache to file."""
        with open(filename, 'wb') as f:
            pickle.dump((self.cache, self.timestamp), f)

    def load_from_file(self, filename):
        """Load cache from file."""
        try:
            with open(filename, 'rb') as f:
                self.cache, self.timestamp = pickle.load(f)
        except FileNotFoundError:
            pass

# Use it
cache = CameraCache(ttl=30)
cameras = cache.get_cameras()  # Queries hardware
cameras = cache.get_cameras()  # Uses cache
```

### Resolution Validator

```python
import camera_enum

def validate_resolution(camera_index, width, height):
    """Check if camera supports a specific resolution."""
    cameras = camera_enum.list_cameras()

    camera = next((c for c in cameras if c['index'] == camera_index), None)

    if not camera:
        return False

    for res in camera['resolutions']:
        if res['width'] == width and res['height'] == height:
            return True

    return False

# Use it
if validate_resolution(0, 1920, 1080):
    print("1080p supported!")
else:
    print("1080p not supported")
```

---

## Related Pages

- **[Getting Started](Getting-Started)** - Installation and basic usage
- **[API Reference](API-Reference)** - Complete API documentation
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions

## Contributing Examples

Have a useful example? [Submit it on GitHub](https://github.com/thecheapgeek/python-lite-camera/issues)!

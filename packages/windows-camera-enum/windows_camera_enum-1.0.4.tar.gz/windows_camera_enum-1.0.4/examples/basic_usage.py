"""
Basic usage example for windows-camera-enum.

Demonstrates how to:
- List all available cameras with detailed information
- Display supported resolutions, frame rates, and formats
- Display available camera controls
- Open a camera preview with OpenCV

Requirements:
    pip install opencv-python
"""
import camera_enum
import cv2


def display_camera_info(cameras):
    """Display detailed camera information."""
    print("=" * 80)
    print("CAMERA ENUMERATION RESULTS")
    print("=" * 80)
    print(f"\nFound {len(cameras)} camera(s)\n")

    for camera in cameras:
        print(f"[{camera['index']}] {camera['name']}")
        print(f"  Device Path: {camera.get('path', 'N/A')}")

        # Display resolutions with frame rates and formats
        print("\n  Supported Resolutions:")
        resolutions = camera.get('resolutions', [])
        if resolutions:
            for res in resolutions:
                width = res['width']
                height = res['height']

                # Format frame rates
                frame_rates = res.get('frame_rates', [])
                if frame_rates:
                    fps_str = ', '.join(f"{fps:.1f}" for fps in frame_rates)
                else:
                    fps_str = "Unknown"

                # Format pixel formats
                formats = res.get('formats', [])
                if formats:
                    formats_str = ', '.join(formats)
                else:
                    formats_str = "Unknown"

                # Display on single line: resolution @ fps | formats
                print(f"    {width}x{height} @ {fps_str} FPS | {formats_str}")
        else:
            print("    No resolution information available")

        # Display camera controls
        controls = camera.get('controls', {})
        if controls:
            print("\n  Available Controls:")
            for ctrl_name, ctrl_info in controls.items():
                min_val = ctrl_info.get('min', 0)
                max_val = ctrl_info.get('max', 0)
                default_val = ctrl_info.get('default', 0)
                step = ctrl_info.get('step', 1)
                auto = ctrl_info.get('auto', False)

                auto_str = " (auto supported)" if auto else ""
                print(f"    {ctrl_name}: {min_val} to {max_val} (default: {default_val}, step: {step}){auto_str}")
        else:
            print("\n  No camera controls available")

        print()  # Blank line between cameras

    print("=" * 80)


def select_camera(last_index):
    """Prompt user to select a camera."""
    while True:
        hint = f"Select a camera (0 to {last_index}): "
        try:
            number = int(input(hint))
            if 0 <= number <= last_index:
                return number
            else:
                print(f"Invalid number! Please enter a number between 0 and {last_index}")
        except ValueError:
            print("Invalid input! Please enter a number")
        except KeyboardInterrupt:
            print("\nCancelled by user")
            return None


def open_camera_preview(camera_index):
    """Open camera preview with OpenCV."""
    print(f"\nOpening camera {camera_index}...")
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"Failed to open camera {camera_index}")
        return

    # Get actual resolution
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Active resolution: {int(width)}x{int(height)} @ {fps:.1f} FPS")
    print("Press ESC to close preview")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        cv2.imshow("Camera Preview (Press ESC to exit)", frame)

        # ESC key to exit
        key = cv2.waitKey(20)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def test_camera_enumeration():
    """Test the list_cameras() API."""
    print("\n" + "=" * 80)
    print("TESTING CAMERA ENUMERATION")
    print("=" * 80)

    try:
        cameras = camera_enum.list_cameras()
        display_camera_info(cameras)

        if cameras:
            last_index = len(cameras) - 1
            camera_index = select_camera(last_index)

            if camera_index is not None:
                open_camera_preview(camera_index)

    except camera_enum.NoCameraFoundException:
        print("No camera devices found. Please connect a camera and try again.")
    except camera_enum.COMInitializationException as e:
        print(f"COM initialization error: {e}")
        print("DirectShow may not be available on this system.")
    except camera_enum.CameraException as e:
        print(f"Camera error: {e}")


def main():
    """Main test function."""
    print("OpenCV version:", cv2.__version__)
    print("camera_enum version:", camera_enum.__version__)

    # Test camera enumeration API
    test_camera_enumeration()


if __name__ == "__main__":
    main()

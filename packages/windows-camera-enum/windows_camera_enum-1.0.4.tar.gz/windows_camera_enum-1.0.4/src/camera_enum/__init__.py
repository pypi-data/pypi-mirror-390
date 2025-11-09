"""
Windows DirectShow camera device enumeration.

This module provides utilities for enumerating camera devices and their
supported capabilities on Windows using DirectShow APIs.
"""

from typing import Any, Dict, List, TypedDict

from .camera_enum import list_cameras as _list_cameras

__version__ = "1.0.4"
__all__ = [
    "list_cameras",
    "CameraException",
    "NoCameraFoundException",
    "CameraAccessDeniedException",
    "COMInitializationException",
]


# Type definitions for better IDE support
class ResolutionInfo(TypedDict):
    """Camera resolution information."""
    width: int
    height: int
    frame_rates: List[float]
    formats: List[str]


class CameraControlInfo(TypedDict):
    """Camera control information."""
    min: int
    max: int
    step: int
    default: int
    auto: bool


class CameraInfo(TypedDict):
    """Complete camera device information."""
    index: int
    name: str
    path: str
    resolutions: List[ResolutionInfo]
    controls: Dict[str, CameraControlInfo]


# Custom Exception Classes
class CameraException(Exception):
    """Base exception for camera operations."""
    pass


class NoCameraFoundException(CameraException):
    """Raised when no cameras are available."""
    pass


class CameraAccessDeniedException(CameraException):
    """Raised when camera access is denied (permissions issue)."""
    pass


class COMInitializationException(CameraException):
    """Raised when COM initialization fails."""
    pass


def list_cameras() -> List[Dict[str, Any]]:
    """
    Enumerate all video capture devices with detailed information.

    Returns:
        List of camera information dictionaries. Each dictionary contains:
            - index (int): Camera device index
            - name (str): Camera friendly name
            - path (str): Device path for identification
            - resolutions (List[Dict]): Supported resolutions, each with:
                - width (int): Resolution width in pixels
                - height (int): Resolution height in pixels
                - frame_rates (List[float]): Supported frame rates in FPS
                - formats (List[str]): Supported pixel formats (e.g., 'MJPEG', 'YUY2')
            - controls (Dict[str, Dict]): Available camera controls, each with:
                - min (int): Minimum value
                - max (int): Maximum value
                - step (int): Step size
                - default (int): Default value
                - auto (bool): Whether auto mode is supported

    Raises:
        NoCameraFoundException: When no cameras are connected or available
        COMInitializationException: When COM initialization fails
        CameraAccessDeniedException: When camera access is denied (permissions)
        CameraException: For other camera-related errors

    Example:
        >>> import camera_enum
        >>> import json
        >>>
        >>> try:
        ...     cameras = camera_enum.list_cameras()
        ...     for camera in cameras:
        ...         print(f"[{camera['index']}] {camera['name']}")
        ...         print(f"  Path: {camera['path']}")
        ...
        ...         # Display resolutions
        ...         print(f"  Resolutions:")
        ...         for res in camera['resolutions']:
        ...             fps_str = ', '.join(f"{fps:.1f}" for fps in res['frame_rates'])
        ...             formats_str = ', '.join(res['formats'])
        ...             print(f"    {res['width']}x{res['height']}: {fps_str} FPS ({formats_str})")
        ...
        ...         # Display available controls
        ...         if camera['controls']:
        ...             print(f"  Controls:")
        ...             for ctrl_name, ctrl_info in camera['controls'].items():
        ...                 auto_str = " (auto)" if ctrl_info['auto'] else ""
        ...                 print(f"    {ctrl_name}: {ctrl_info['min']}-{ctrl_info['max']}{auto_str}")
        ...
        ... except camera_enum.NoCameraFoundException:
        ...     print("No cameras found")
        ... except camera_enum.CameraException as e:
        ...     print(f"Camera error: {e}")

    Note:
        This function is only available on Windows and requires DirectShow support.
    """
    try:
        result = _list_cameras()
    except RuntimeError as e:
        error_msg = str(e)

        # Convert C++ RuntimeErrors to our custom exceptions
        if "COM initialization failed" in error_msg:
            raise COMInitializationException(error_msg) from e
        elif "permissions" in error_msg.lower() or "access denied" in error_msg.lower():
            raise CameraAccessDeniedException(error_msg) from e
        else:
            # Generic camera exception for other errors
            raise CameraException(error_msg) from e

    # Handle empty list (no cameras found)
    if len(result) == 0:
        raise NoCameraFoundException(
            "No camera devices found. Please ensure a camera is connected "
            "and has proper drivers installed."
        )

    return result

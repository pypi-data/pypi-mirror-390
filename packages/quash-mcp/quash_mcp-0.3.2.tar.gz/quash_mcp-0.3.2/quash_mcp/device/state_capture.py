import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple, List
from adbutils import adb

logger = logging.getLogger("quash-device")


def get_current_package(serial: str) -> str:
    """
    Get the currently focused app package.

    Args:
        serial: Device serial number

    Returns:
        Package name of current app
    """
    try:
        device = adb.device(serial)
        output = device.shell("dumpsys window windows | grep -E 'mCurrentFocus'")
        # Parse output like: mCurrentFocus=Window{abc123 u0 com.android.settings/com.android.settings.MainActivity}
        if "/" in output:
            package = output.split("/")[0].split()[-1]
            return package
        return "unknown"
    except Exception as e:
        logger.warning(f"Failed to get current package: {e}")
        return "unknown"


def get_accessibility_tree(serial: str, tcp_port: int = 8080) -> List[Dict[str, Any]]:
    """
    Get accessibility tree from Portal app via TCP.

    Args:
        serial: Device serial number
        tcp_port: Local TCP port for Portal communication

    Returns:
        Accessibility tree as a list of dictionaries, or an empty list if failed
    """
    try:
        device = adb.device(serial)
        local_port = device.forward_port(tcp_port)

        response = requests.get(
            f"http://localhost:{local_port}/a11y_tree",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                # The 'data' field should contain the JSON string of the a11y_tree
                a11y_tree_json_str = data.get("data", "[]")
                try:
                    parsed_tree = json.loads(a11y_tree_json_str)
                    logger.debug(f"get_accessibility_tree returning tree of length: {len(parsed_tree)}")
                    return parsed_tree
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse a11y_tree JSON string: {a11y_tree_json_str}")
                    return []
            else:
                logger.warning(f"Portal error: {data.get('error', 'Unknown error')}")
                return []
        else:
            logger.warning(f"Failed to get accessibility tree: HTTP {response.status_code}")
            return []

    except Exception as e:
        logger.warning(f"Failed to get accessibility tree: {e}")
        return []


def capture_screenshot(serial: str) -> Optional[bytes]:
    """
    Capture screenshot from device.

    Args:
        serial: Device serial number

    Returns:
        Screenshot as PNG bytes, or None if failed
    """
    try:
        device = adb.device(serial)
        # device.shell("screencap -p", stream=True) returns an AdbConnection object (file-like)
        # We need to read the bytes from it.
        with device.shell("screencap -p", stream=True) as conn:
            screenshot_bytes = conn.read(1024 * 1024 * 10) # Read up to 10MB
        return screenshot_bytes
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        return None


def get_device_state(serial: str) -> Tuple[Dict[str, Any], Optional[bytes]]:
    """
    Get complete device state: UI state and screenshot.

    Args:
        serial: Device serial number

    Returns:
        Tuple of (ui_state_dict, screenshot_bytes)
    """
    # Get current package
    current_package = get_current_package(serial)

    logger.debug("Capturing device state...")

    # Get current package
    current_package = get_current_package(serial)

    # Get accessibility tree
    a11y_tree = get_accessibility_tree(serial)

    # Build UI state
    ui_state = {
        "a11y_tree": a11y_tree,
        "phone_state": {
            "package": current_package,
            "activity": "unknown",  # Can be added later
        }
    }

    # Capture screenshot
    screenshot = capture_screenshot(serial)

    return ui_state, screenshot
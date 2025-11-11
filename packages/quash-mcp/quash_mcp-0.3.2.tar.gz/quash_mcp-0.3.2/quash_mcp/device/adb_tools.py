"""
ADB Tools - Basic Android device communication wrapper.
Simplified version for device management without agent-specific functionality.
Includes lightweight tool functions for executing backend-generated code.
"""

import logging
from typing import Optional, List, Dict, Any
from adbutils import adb
import requests

logger = logging.getLogger("quash-device")
PORTAL_DEFAULT_TCP_PORT = 8080


class AdbTools:
    """Basic ADB device communication wrapper with tool execution functions."""

    def __init__(
        self,
        serial: str | None = None,
        use_tcp: bool = False,
        remote_tcp_port: int = PORTAL_DEFAULT_TCP_PORT,
    ) -> None:
        """Initialize the AdbTools instance.

        Args:
            serial: Device serial number
            use_tcp: Whether to use TCP communication (default: False)
            remote_tcp_port: TCP port for communication (default: 8080)
        """
        self.device = adb.device(serial=serial)
        self.use_tcp = use_tcp
        self.remote_tcp_port = remote_tcp_port
        self.tcp_forwarded = False
        self.clickable_elements_cache: List[Dict[str, Any]] = []

        # Set up TCP forwarding if requested
        if self.use_tcp:
            self.setup_tcp_forward()

    def setup_tcp_forward(self) -> bool:
        """
        Set up ADB TCP port forwarding for communication with the portal app.

        Returns:
            bool: True if forwarding was set up successfully, False otherwise
        """
        try:
            logger.debug(
                f"Setting up TCP port forwarding for port tcp:{self.remote_tcp_port} on device {self.device.serial}"
            )
            # Use adb forward command to set up port forwarding
            self.local_tcp_port = self.device.forward_port(self.remote_tcp_port)
            self.tcp_base_url = f"http://localhost:{self.local_tcp_port}"
            logger.debug(
                f"TCP port forwarding set up successfully to {self.tcp_base_url}"
            )

            # Test the connection with a ping
            try:
                response = requests.get(f"{self.tcp_base_url}/ping", timeout=5)
                if response.status_code == 200:
                    logger.debug("TCP connection test successful")
                    self.tcp_forwarded = True
                    return True
                else:
                    logger.warning(
                        f"TCP connection test failed with status: {response.status_code}"
                    )
                    return False
            except requests.exceptions.RequestException as e:
                logger.warning(f"TCP connection test failed: {e}")
                return False

        except Exception as e:
            logger.error(f"Failed to set up TCP port forwarding: {e}")
            self.tcp_forwarded = False
            return False

    def teardown_tcp_forward(self) -> bool:
        """
        Remove ADB TCP port forwarding.

        Returns:
            bool: True if forwarding was removed successfully, False otherwise
        """
        try:
            if self.tcp_forwarded:
                logger.debug(
                    f"Removing TCP port forwarding for port {self.local_tcp_port}"
                )
                # remove forwarding
                cmd = f"killforward:tcp:{self.local_tcp_port}"
                logger.debug(f"Removing TCP port forwarding: {cmd}")
                c = self.device.open_transport(cmd)
                c.close()

                self.tcp_forwarded = False
                logger.debug(f"TCP port forwarding removed")
                return True
            return True
        except Exception as e:
            logger.error(f"Failed to remove TCP port forwarding: {e}")
            return False

    def get_accessibility_tree(self) -> str:
        """
        Get the current accessibility tree (UI hierarchy) as an XML string.
        """
        try:
            # Use uiautomator dump to get the UI hierarchy
            result = self.device.shell("uiautomator dump --compressed")
            # The dump command writes to /sdcard/window_dump.xml
            # We need to read it back
            xml_content = self.device.pull("/sdcard/window_dump.xml").decode("utf-8")
            # Clean up the dumped file from the device
            self.device.shell("rm /sdcard/window_dump.xml")
            return xml_content
        except Exception as e:
            logger.error(f"Failed to get accessibility tree: {e}", exc_info=True)
            return f"<error>Failed to get accessibility tree: {e}</error>"

    def get_phone_state(self) -> dict[str, any]:
        """
        Get basic phone state information, like current app package.
        """
        try:
            current_app = self.device.current_app()
            return {
                "package": current_app.package,
                "activity": current_app.activity,
                "pid": current_app.pid,
            }
        except Exception as e:
            logger.error(f"Failed to get phone state: {e}", exc_info=True)
            return {"package": "unknown", "error": str(e)}

    def get_screenshot(self) -> bytes:
        """
        Get a screenshot of the device as PNG bytes.
        """
        try:
            return self.device.screenshot()
        except Exception as e:
            logger.error(f"Failed to get screenshot: {e}", exc_info=True)
            return b""

    # === Tool Execution Functions ===
    # These lightweight functions are used to execute backend-generated code

    def update_state(self, a11y_tree: List[Dict[str, Any]]) -> None:
        """Update clickable elements cache from accessibility tree."""
        try:
            elements = a11y_tree
            filtered_elements = []
            for element in elements:
                filtered_element = {k: v for k, v in element.items() if k != "type"}
                if "children" in filtered_element:
                    filtered_element["children"] = [
                        {k: v for k, v in child.items() if k != "type"}
                        for child in filtered_element["children"]
                    ]
                filtered_elements.append(filtered_element)
            self.clickable_elements_cache = filtered_elements
        except Exception as e:
            logger.error(f"Failed to update state: {e}")

    def tap_by_index(self, index: int) -> str:
        """Tap on element by index."""
        try:
            if not self.clickable_elements_cache:
                return "Error: No UI elements cached"

            def find_element_by_index(elements, target_idx):
                for item in elements:
                    if item.get("index") == target_idx:
                        return item
                    children = item.get("children", [])
                    result = find_element_by_index(children, target_idx)
                    if result:
                        return result
                return None

            element = find_element_by_index(self.clickable_elements_cache, index)
            if not element:
                return f"Error: No element found with index {index}"

            bounds_str = element.get("bounds")
            if not bounds_str:
                return f"Error: Element at index {index} has no bounds"

            try:
                left, top, right, bottom = map(int, bounds_str.split(","))
                x = (left + right) // 2
                y = (top + bottom) // 2
                self.device.shell(f"input tap {x} {y}")
                return f"Tapped on element at index {index}"
            except Exception as e:
                return f"Error parsing bounds: {e}"
        except Exception as e:
            logger.error(f"Failed to tap by index {index}: {e}")
            return f"Error: {e}"

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 500) -> str:
        """Swipe from start to end coordinates."""
        try:
            self.device.shell(f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
            return "Swiped successfully"
        except Exception as e:
            logger.error(f"Failed to swipe: {e}")
            return f"Error: {e}"

    def input_text(self, text: str) -> str:
        """Input text into the focused field."""
        try:
            escaped_text = text.replace('"', '\\"').replace('$', '\\$')
            self.device.shell(f'input text "{escaped_text}"')
            return f"Text entered: {text}"
        except Exception as e:
            logger.error(f"Failed to input text: {e}")
            return f"Error: {e}"

    def press_key(self, key: str) -> str:
        """Press a key on the device."""
        try:
            key_map = {
                "BACK": "4",
                "HOME": "3",
                "MENU": "82",
                "SEARCH": "84",
                "ENTER": "66",
                "TAB": "61",
                "SPACE": "62",
            }
            key_code = key_map.get(key.upper(), key)
            self.device.shell(f"input keyevent {key_code}")
            return f"Key pressed: {key}"
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return f"Error: {e}"

    def start_app(self, package_name: str) -> str:
        """Start an app by package name."""
        try:
            self.device.shell(f"monkey -p {package_name} 1")
            return f"App started: {package_name}"
        except Exception as e:
            logger.error(f"Failed to start app: {e}")
            return f"Error: {e}"

    def complete(self, success: bool = True, reason: str = "") -> str:
        """Signal task completion."""
        status = "SUCCESS" if success else "FAILED"
        return f"Task completed ({status}): {reason}"

    def remember(self, text: str) -> str:
        """Store text in memory."""
        return f"Remembered: {text}"

    def list_packages(self, filter_str: str = "") -> str:
        """List installed packages."""
        try:
            result = self.device.shell("pm list packages")
            packages = result.strip().split('\n')
            if filter_str:
                packages = [p for p in packages if filter_str.lower() in p.lower()]
            return "\n".join(packages[:20])
        except Exception as e:
            logger.error(f"Failed to list packages: {e}")
            return f"Error: {e}"

    def __del__(self):
        """Cleanup when the object is destroyed."""
        if hasattr(self, "tcp_forwarded") and self.tcp_forwarded:
            self.teardown_tcp_forward()
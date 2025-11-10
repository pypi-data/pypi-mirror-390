"""
ADB Tools - Basic Android device communication wrapper.
Simplified version for device management without agent-specific functionality.
"""

import logging
from typing import Optional
from adbutils import adb
import requests

logger = logging.getLogger("quash-device")
PORTAL_DEFAULT_TCP_PORT = 8080


class AdbTools:
    """Basic ADB device communication wrapper."""

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

    def __del__(self):
        """Cleanup when the object is destroyed."""
        if hasattr(self, "tcp_forwarded") and self.tcp_forwarded:
            self.teardown_tcp_forward()
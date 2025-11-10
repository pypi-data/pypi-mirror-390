"""Mobile interaction domain service for smart device operations"""

from __future__ import annotations

import asyncio
import base64
import time
from functools import cached_property
from io import BytesIO

import numpy as np
from defusedxml import ElementTree as ET
from PIL import Image

from noqa_runner.domain.models.actions.activate_app import ActivateApp
from noqa_runner.domain.models.actions.background_app import BackgroundApp
from noqa_runner.domain.models.actions.base import BaseAction
from noqa_runner.domain.models.actions.handle_system_alert import HandleSystemAlert
from noqa_runner.domain.models.actions.input_text import InputText
from noqa_runner.domain.models.actions.open_url import OpenUrl
from noqa_runner.domain.models.actions.restart_app import RestartApp
from noqa_runner.domain.models.actions.scroll import Scroll
from noqa_runner.domain.models.actions.stop import Stop
from noqa_runner.domain.models.actions.swipe import Swipe
from noqa_runner.domain.models.actions.tap import Tap
from noqa_runner.domain.models.actions.terminate_app import TerminateApp
from noqa_runner.domain.models.actions.wait import Wait
from noqa_runner.domain.models.state.screen import ActiveElement, Screen
from noqa_runner.infrastructure.adapters.mobile.appium_adapter import AppiumClient
from noqa_runner.utils.retry_decorator import with_retry


class MobileService:
    """Service for intelligent mobile device interactions"""

    def __init__(self, appium_client: AppiumClient, bundle_id: str | None = None):
        self.client = appium_client
        self.bundle_id = bundle_id

        self._action_handlers = {
            Tap: self._execute_tap,
            Swipe: self._execute_swipe,
            InputText: self._execute_input_text,
            Scroll: self._execute_scroll,
            ActivateApp: self._execute_activate_app,
            BackgroundApp: self._execute_background_app,
            TerminateApp: self._execute_terminate_app,
            RestartApp: self._execute_restart_app,
            OpenUrl: self._execute_open_url,
            HandleSystemAlert: self._execute_handle_system_alert,
            Wait: self._execute_wait,
            Stop: self._execute_stop,
        }

    async def get_app_state(self, bundle_id: str) -> int:
        """Get current app state"""
        return await self.client.query_app_state(bundle_id)

    async def execute_action(self, action: BaseAction, screen: Screen | None = None):
        """Execute action based on its type"""
        handler = self._action_handlers.get(type(action))
        if not handler:
            raise ValueError(f"No handler for {type(action).__name__}")
        await handler(action, screen)

    async def _execute_tap(self, action: Tap, screen):
        await self.tap_element(action.element)

    async def _execute_swipe(self, action: Swipe, screen):
        await self.swipe_element(action.element, action.direction)

    async def _execute_input_text(self, action: InputText, screen):
        await self.input_text_in_element(
            action.element, action.text, screen.elements_tree if screen else None
        )

    async def _execute_scroll(self, action: Scroll, screen):
        await self.scroll_element(action.element, action.direction)

    async def _execute_activate_app(self, action: ActivateApp, screen):
        if not self.bundle_id:
            raise ValueError("bundle_id not set on MobileService")
        await self.client.activate_app(self.bundle_id)

    async def _execute_background_app(self, action: BackgroundApp, screen):
        await self.client.background_app()

    async def _execute_terminate_app(self, action: TerminateApp, screen):
        if not self.bundle_id:
            raise ValueError("bundle_id not set on MobileService")
        await self.client.terminate_app(self.bundle_id)

    async def _execute_restart_app(self, action: RestartApp, screen):
        if not self.bundle_id:
            raise ValueError("bundle_id not set on MobileService")
        await self.client.terminate_app(self.bundle_id)
        await self.client.activate_app(self.bundle_id)

    async def _execute_open_url(self, action: OpenUrl, screen):
        await self.client.open_url(str(action.url))

    async def _execute_handle_system_alert(self, action: HandleSystemAlert, screen):
        if action.action_type == "accept":
            await self.client.accept_system_alert()
        elif action.action_type == "dismiss":
            await self.client.dismiss_system_alert()
        else:
            raise ValueError(
                f"Invalid action_type '{action.action_type}' for HandleSystemAlert. Allowed values are: 'accept', 'dismiss'"
            )

    async def _execute_wait(self, action: Wait, screen):
        await asyncio.sleep(3)

    async def _execute_stop(self, action: Stop, screen):
        pass

    @cached_property
    def resolution(self) -> dict[str, int]:
        """Get device resolution (cached)"""
        return self.client.resolution

    async def tap_element(self, element: ActiveElement) -> None:
        """
        Smart tap - automatically chooses best tap method based on element type and context

        Strategy:
        1. OCR elements or keyboard present → use coordinates
        2. Element has xpath → try xpath, fallback to coordinates
        3. Otherwise → use coordinates
        """
        # For OCR elements or keyboard, always use coordinates
        if element.source == "ocr":
            await self.client.tap_by_coords(element.center_x, element.center_y)
            return

        # Try xpath first, fallback to coordinates
        if element.xpath:
            tap_success = await self.client.tap(element.xpath)
            if tap_success:
                return

            # Fallback to coordinates if xpath failed
            if element.center_x and element.center_y:
                await self.client.tap_by_coords(element.center_x, element.center_y)
        elif element.center_x and element.center_y:
            await self.client.tap_by_coords(element.center_x, element.center_y)
        else:
            raise ValueError(f"Failed to tap element: invalid element data: {element}")

    async def input_text_in_element(
        self, element: ActiveElement, text: str, elements_tree: str | None = None
    ) -> None:
        """
        Smart text input with automatic keyboard handling

        Args:
            element: Target element for text input
            text: Text to input
            elements_tree: XML tree to check for keyboard presence
        """
        await self.client.input_text_in_element(
            element_locator=element.xpath, text=text
        )

        # Hide keyboard if present (platform-aware detection)
        if elements_tree:
            keyboard_detected = "XCUIElementTypeKeyboard" in elements_tree

            if keyboard_detected:
                await self.client.hide_keyboard()

    async def swipe_element(self, element: ActiveElement, direction: str) -> None:
        """
        Smart swipe from element with automatic start position calculation

        Args:
            element: Element to swipe from
            direction: Swipe direction (up, down, left, right)
        """
        start_x = element.center_x
        start_y = element.center_y

        # Adjust start position based on direction for better UX
        if direction == "down":
            start_y = element.y + element.height * 3 // 4
        elif direction == "up":
            start_y = element.y + element.height // 4
        elif direction == "right":
            start_x = element.x + element.width // 4
        elif direction == "left":
            start_x = element.x + element.width * 3 // 4

        await self.client.swipe(direction=direction, start_x=start_x, start_y=start_y)

    async def scroll_element(self, element: ActiveElement, direction: str) -> None:
        """
        Smart scroll on element by delegating to swipe_element for consistent behavior

        Args:
            element: Element to scroll
            direction: Scroll direction (up, down, left, right)
        """
        await self.swipe_element(element, direction)

    def _resize_image(self, image: Image.Image, max_size: int) -> Image.Image:
        """Resize image so that minimum side is max_size"""
        width, height = image.size
        min_side = min(width, height)

        if min_side <= max_size:
            return image

        scale_factor = max_size / min_side
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _resize_screenshot(self, screenshot_base64: str, max_size: int = 500) -> str:
        """Resize screenshot to max_size on minimum side, return base64"""
        image_data = base64.b64decode(screenshot_base64)
        with Image.open(BytesIO(image_data)) as img:
            resized = self._resize_image(image=img, max_size=max_size)
            buffer = BytesIO()
            resized.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _get_screenshot_thumbnail(self, screenshot_base64: str) -> np.ndarray:
        """Get screenshot thumbnail as numpy array for comparison"""
        image_data = base64.b64decode(screenshot_base64)
        with Image.open(BytesIO(image_data)) as img:
            # Reuse _resize_image for consistency (50px for fast comparison)
            resized = self._resize_image(image=img.convert("RGB"), max_size=50)
        return np.asarray(resized)

    def _calculate_image_difference(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate percentage difference between two images
        Returns percentage of different pixels (0.0 to 100.0)
        """
        if img1.shape != img2.shape:
            return 100.0

        # Calculate absolute difference
        diff = np.abs(img1.astype(float) - img2.astype(float))

        # Use L2 norm (Euclidean distance) per pixel for more robust comparison
        # This considers the magnitude of differences across all channels
        pixel_diff_magnitude = np.sqrt(np.sum(diff**2, axis=-1))

        # Define threshold for considering pixels as different (default: 5.0)
        # This helps ignore minor rendering artifacts and anti-aliasing differences
        threshold = 5.0

        # Count pixels that exceed threshold
        different_pixels = (pixel_diff_magnitude > threshold).sum()
        total_pixels = img1.shape[0] * img1.shape[1]

        # Return percentage
        return (different_pixels / total_pixels) * 100.0

    def _has_non_fullscreen_elements(self, xml_source: str) -> bool:
        """Check if XML has elements smaller than screen resolution"""
        root = ET.fromstring(xml_source)
        for elem in root.iter():
            width = elem.get("width")
            height = elem.get("height")
            if width and height:
                if (
                    int(width) < self.resolution["width"]
                    or int(height) < self.resolution["height"]
                ):
                    return True
        return False

    @with_retry(max_attempts=3)
    async def get_appium_screen_data(
        self, timeout: float = 4.0, threshold: float = 0.5
    ) -> tuple[str, str]:
        """
        Get synchronized XML and screenshot from Appium

        Args:
            timeout: Maximum time to wait in seconds
            threshold: Maximum allowed difference percentage (0.0 to 100.0)
                      Default 0.5% allows minor rendering differences
        """
        xml_source = ""
        screenshot_final = ""
        start_time = time.time()

        while time.time() - start_time < timeout:
            screenshot_before = await self.client.get_screenshot()
            thumbnail_before = self._get_screenshot_thumbnail(
                screenshot_base64=screenshot_before
            )

            screenshot_after = await self.client.get_screenshot()
            thumbnail_after = self._get_screenshot_thumbnail(
                screenshot_base64=screenshot_after
            )

            diff_percent = self._calculate_image_difference(
                img1=thumbnail_before, img2=thumbnail_after
            )

            # Check if screen is visually stable (within threshold)
            is_screen_stable = diff_percent <= threshold

            if is_screen_stable:
                # Screen is stable, now get page_source
                xml_source = await self.client.get_page_source()
                screenshot_final = screenshot_after

                # Verify screen didn't change during page_source call
                screenshot_verify = await self.client.get_screenshot()
                thumbnail_verify = self._get_screenshot_thumbnail(
                    screenshot_base64=screenshot_verify
                )

                diff_verify = self._calculate_image_difference(
                    img1=thumbnail_after, img2=thumbnail_verify
                )

                # Check if there are non-fullscreen elements
                has_active_elements = self._has_non_fullscreen_elements(xml_source)

                # All conditions met: screen stable + has elements + stable during XML
                if has_active_elements and diff_verify <= threshold:
                    screenshot_resized = self._resize_screenshot(
                        screenshot_base64=screenshot_final, max_size=500
                    )
                    return xml_source, screenshot_resized

            # Wait before retry (optimized for tests)
            await asyncio.sleep(0.05)

        # Timeout: get final snapshot
        if not xml_source:
            xml_source = await self.client.get_page_source()
        if not screenshot_final:
            screenshot_final = await self.client.get_screenshot()
        screenshot_resized = self._resize_screenshot(
            screenshot_base64=screenshot_final, max_size=500
        )
        return xml_source, screenshot_resized

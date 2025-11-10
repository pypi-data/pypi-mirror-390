from __future__ import annotations

import asyncio
import functools

from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from noqa_runner.domain.exceptions import AppiumError
from noqa_runner.logging_config import get_logger
from noqa_runner.utils.retry_decorator import with_retry

logger = get_logger(__name__)


def get_appstore_url(app_store_id: str, country_code: str = "us") -> str:
    return f"https://apps.apple.com/{country_code}/app/{app_store_id}"


def handle_appium_errors(func):
    """Decorator to catch Appium errors and convert them to AppiumError"""

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except WebDriverException as e:
            logger.error(
                "appium_command_error",
                command=func.__name__,
                error=str(e),
                exc_info=True,
            )
            raise AppiumError(
                appium_url=self.appium_url, original_error=f"{func.__name__}: {str(e)}"
            )

    return wrapper


class AppiumClient:
    """Appium client adapter for mobile automation (async context manager)"""

    driver: webdriver.Remote
    resolution: dict
    _loop: asyncio.AbstractEventLoop | None
    _capabilities: dict | None
    _platform_name: str | None

    @with_retry(
        max_attempts=3, min_wait=1, max_wait=3, exceptions=(WebDriverException,)
    )
    def __init__(self, appium_url: str, appium_capabilities=None):
        self.appium_url = appium_url
        self.appium_capabilities = appium_capabilities
        self._loop = None
        self._capabilities = None
        self._platform_name = None

        # Initialize driver immediately with retry
        try:
            self.driver = webdriver.Remote(
                self.appium_url,
                options=AppiumOptions().load_capabilities(
                    self.appium_capabilities or {}
                ),
            )
            self.driver.implicitly_wait(5)
            self.resolution = self.driver.get_window_size()
        except Exception as e:
            # Any other error during driver initialization
            raise AppiumError(appium_url=self.appium_url, original_error=str(e))

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup driver"""
        await self.close()
        return False

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop"""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    @property
    def capabilities(self) -> dict:
        """Get driver capabilities"""
        if self._capabilities is None:
            self._capabilities = self.driver.capabilities
        return self._capabilities

    @property
    def platform_name(self) -> str:
        """Get platform name (iOS or Android)"""
        if self._platform_name is None:
            self._platform_name = self.capabilities.get("platformName", "iOS").lower()
        return self._platform_name

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def get_page_source(self) -> str:
        """Get page source XML from driver"""
        # Run in executor to avoid blocking the event loop
        return await self.loop.run_in_executor(None, lambda: self.driver.page_source)

    @handle_appium_errors
    async def get_element(self, element_locator):
        """Get single element by XPath locator"""
        try:
            element = await self.loop.run_in_executor(
                None, lambda: self.driver.find_element(AppiumBy.XPATH, element_locator)
            )
            return element
        except Exception:
            logger.debug(f"Element with locator {element_locator} not found")
            return None

    @handle_appium_errors
    async def get_elements(self, element_locator):
        """Get multiple elements by XPath locator"""
        try:
            elements = await self.loop.run_in_executor(
                None, lambda: self.driver.find_elements(AppiumBy.XPATH, element_locator)
            )
            return elements
        except Exception:
            logger.debug(f"Elements with locator {element_locator} not found")
            return None

    @handle_appium_errors
    async def tap_by_coords(self, x: int, y: int) -> None:
        """Tap at specific coordinates"""
        await self.loop.run_in_executor(None, lambda: self.driver.tap([(x, y)]))

    @handle_appium_errors
    @with_retry(
        max_attempts=3,
        min_wait=1,
        max_wait=2,
        exceptions=(StaleElementReferenceException,),
    )
    async def tap(self, element_locator: str) -> bool:
        """Tap element by XPath locator"""
        element = await self.get_element(element_locator)
        if not element:
            logger.error(f"Element to tap with locator {element_locator} not found")
            return False

        await self.loop.run_in_executor(None, lambda: element.click())
        return True

    @handle_appium_errors
    async def swipe(self, direction: str, start_x: int, start_y: int) -> None:
        """Swipe from element center, swipe distance is always half of screen size"""
        # Get screen dimensions
        screen_width = self.resolution["width"]
        screen_height = self.resolution["height"]

        # Swipe distance is half of screen
        swipe_distance_vertical = screen_height // 2
        swipe_distance_horizontal = screen_width // 2

        if direction == "down":
            # Swipe up (from start to top)
            end_x = start_x
            end_y = max(0, start_y - swipe_distance_vertical)
        elif direction == "up":
            # Swipe down (from start to bottom)
            end_x = start_x
            end_y = min(screen_height, start_y + swipe_distance_vertical)
        elif direction == "right":
            # Swipe right (from start to right)
            end_x = min(screen_width, start_x + swipe_distance_horizontal)
            end_y = start_y
        elif direction == "left":
            # Swipe left (from start to left)
            end_x = max(0, start_x - swipe_distance_horizontal)
            end_y = start_y
        else:
            raise ValueError(f"Invalid swipe direction: {direction}")

        await self.loop.run_in_executor(
            None, lambda: self.driver.swipe(start_x, start_y, end_x, end_y, 1000)
        )

    @handle_appium_errors
    async def open_url(self, url: str) -> None:
        """Navigate to URL"""
        await self.loop.run_in_executor(None, lambda: self.driver.get(url))

    async def accept_system_alert(self) -> None:
        """Accept system alert"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.switch_to.alert.accept()
        )

    async def dismiss_system_alert(self) -> None:
        """Dismiss system alert"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.switch_to.alert.dismiss()
        )

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def get_screenshot(self) -> str:
        """Get current screenshot as base64"""
        return await self.loop.run_in_executor(
            None, lambda: self.driver.get_screenshot_as_base64()
        )

    @handle_appium_errors
    async def hide_keyboard(self) -> None:
        """Hide keyboard using platform-specific approach"""
        # iOS: Look for Done button in toolbar
        done_button = await self.get_element(
            "//XCUIElementTypeToolbar//XCUIElementTypeButton[@name='Done']"
        )
        if done_button:
            await self.loop.run_in_executor(None, lambda: done_button.click())

    @handle_appium_errors
    @with_retry(
        max_attempts=3,
        min_wait=1,
        max_wait=2,
        exceptions=(StaleElementReferenceException,),
    )
    async def input_text_in_element(self, element_locator: str, text: str) -> bool:
        """Input text into element"""
        element = await self.get_element(element_locator)
        if not element:
            return False

        def _input_text():
            element.send_keys(text)
            return True

        result = await self.loop.run_in_executor(None, _input_text)
        # Sleep asynchronously after the synchronous operation
        await asyncio.sleep(2)
        return result

    @handle_appium_errors
    async def get_alert_text(self) -> str | None:
        """Get alert text"""

        def _get_alert_text():
            try:
                return self.driver.switch_to.alert.text
            except Exception:
                return None

        return await self.loop.run_in_executor(None, _get_alert_text)

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def activate_app(self, bundle_id: str) -> None:
        """Activate app by bundle ID"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.activate_app(bundle_id)
        )

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def terminate_app(self, bundle_id: str) -> None:
        """Terminate app by bundle ID"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.terminate_app(bundle_id)
        )

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def background_app(self) -> None:
        """Background app"""
        await self.loop.run_in_executor(None, lambda: self.driver.background_app(-1))

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def remove_app(self, bundle_id: str) -> None:
        """Remove app by bundle ID"""
        await self.loop.run_in_executor(None, lambda: self.driver.remove_app(bundle_id))

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def query_app_state(self, bundle_id: str) -> int:
        """Query app state by bundle ID. Returns state code (4 = running)"""
        return await self.loop.run_in_executor(
            None, lambda: self.driver.query_app_state(bundle_id)
        )

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def install_app_testflight(
        self, app_bundle_id: str, app_store_id: str | None = None
    ) -> bool:
        """
        Install app via TestFlight by simulating user interaction.
        """
        # Remove existing app
        await self.remove_app(app_bundle_id)
        logger.info("Existing app removed", bundle_id=app_bundle_id)

        # Activate TestFlight app
        await self.activate_app("com.apple.TestFlight")
        logger.info("TestFlight activated")

        # Wait for app to be installed
        max_wait_time = 20
        wait_start = 0
        while wait_start < max_wait_time:
            await asyncio.sleep(1)
            wait_start += 1

            try:
                app_state = await self.query_app_state(app_bundle_id)
                if app_state == 4:
                    logger.info(
                        "App installed and running",
                        bundle_id=app_bundle_id,
                        app_state=app_state,
                    )
                    return True

                # Get current page source
                xml_str = await self.get_page_source()

                # Handle alerts (e.g., "Do you want to install this app?")
                if "XCUIElementTypeAlert" in xml_str:
                    alert_buttons = await self.get_elements(
                        "//XCUIElementTypeAlert//XCUIElementTypeButton"
                    )
                    if alert_buttons:
                        alert_buttons[-1].click()
                        continue

                main_buttons = await self.get_elements(
                    f"//XCUIElementTypeOther[@name='{app_store_id}']//XCUIElementTypeButton"
                )
                if main_buttons:
                    main_button = main_buttons[-1]
                    if (
                        main_button.get_attribute("name")
                        and len(main_button.get_attribute("name")) > 2
                    ):
                        main_button.click()
                        continue
            except Exception:
                pass

        logger.error(
            "TestFlight installation timeout",
            bundle_id=app_bundle_id,
            timeout_seconds=max_wait_time,
        )
        return False

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def install_app_appstore(
        self, app_bundle_id: str, app_store_id: str | None = None
    ) -> bool | None:
        # Remove existing app
        await self.remove_app(app_bundle_id)
        logger.info("Existing app removed", bundle_id=app_bundle_id)

        max_wait_time = 20
        wait_start = 0
        while wait_start < max_wait_time:
            await asyncio.sleep(1)
            wait_start += 1

            try:
                app_state = await self.query_app_state(app_bundle_id)
                if app_state == 4:
                    logger.info(
                        "App installed and running",
                        bundle_id=app_bundle_id,
                        app_state=app_state,
                    )
                    return True

                appstore_state = await self.query_app_state("com.apple.AppStore")
                if appstore_state != 4:
                    self.driver.get(get_appstore_url(app_store_id=app_store_id))
                    continue

                # Get current page source
                xml_str = await self.get_page_source()

                if "payment-sheet" in xml_str:
                    buttons = await self.get_elements(
                        "//XCUIElementTypeOther[@name='payment-sheet']//XCUIElementTypeButton"
                    )
                    if buttons:
                        buttons[-1].click()
                        continue

                if "AppStore.offerButton" in xml_str:
                    if (
                        "AppStore.offerButton[state=downloading]" in xml_str
                        or "AppStore.offerButton[state=loading]" in xml_str
                    ):
                        logger.info("App is downloading, waiting...")
                        continue
                    else:
                        main_button = await self.get_element(
                            "//XCUIElementTypeCell[contains(@name, 'AppStore.shelfItem.productTopLockup')]//XCUIElementTypeButton[contains(@name, 'AppStore.offerButton')]"
                        )
                        if main_button:
                            main_button.click()
            except Exception:
                pass

    async def close(self) -> None:
        """Close the Appium driver connection"""
        if self.driver and hasattr(self.driver, "quit"):
            try:
                await self.loop.run_in_executor(None, lambda: self.driver.quit())
            finally:
                self.driver = None

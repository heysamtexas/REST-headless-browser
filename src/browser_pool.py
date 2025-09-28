from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import time
from typing import TYPE_CHECKING

from playwright.async_api import async_playwright

if TYPE_CHECKING:
    from playwright.async_api import Browser


# Environment variable configuration with validation
def _get_max_browsers() -> int:
    """Get max browsers from environment variable with validation."""
    try:
        value = int(os.getenv("BROWSER_MAX_BROWSERS", "2"))
        return max(1, value)  # Ensure minimum of 1
    except (ValueError, TypeError):
        return 2  # Default fallback for invalid values


MAX_BROWSERS = _get_max_browsers()
IDLE_TIMEOUT = int(os.getenv("BROWSER_IDLE_TIMEOUT", "300"))  # 5 minutes default


class BrowserPool:
    """Creates a pool of browsers that can be used by multiple clients concurrently."""

    def __init__(self, max_browsers: int = MAX_BROWSERS, idle_timeout: int = IDLE_TIMEOUT) -> None:
        """Initialize the BrowserPool."""
        self.max_browsers = max_browsers
        self.idle_timeout = idle_timeout
        self.semaphore = asyncio.Semaphore(max_browsers)
        self.playwright = None
        self.browsers: list[tuple[Browser, float]] = []  # (browser, last_used_timestamp)
        self._current_browser_index = 0
        self._cleanup_task = None
        self._launch_args = [
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-extensions",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-audio-output",
            "--no-sandbox",
            "--disable-web-security",
            "--disable-dev-shm-usage",
        ]

    async def initialize(self) -> None:
        """Initialize the BrowserPool by starting the Playwright instance."""
        self.playwright = await async_playwright().start()
        # Start with empty pool - browsers will be created on demand
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def get_browser(self) -> Browser:
        """Get a browser from the pool, creating one if needed."""
        await self.semaphore.acquire()

        # Clean up idle browsers first
        await self._cleanup_idle_browsers()

        # Create a browser if pool is empty
        if not self.browsers:
            browser = await self._create_browser()
            self.browsers.append((browser, time.time()))

        # Get least recently used browser
        browser_entry = min(self.browsers, key=lambda x: x[1])
        browser = browser_entry[0]

        # Update last used timestamp
        self._update_last_used(browser)

        return browser

    async def release_browser(self, browser: Browser) -> None:  # noqa: ARG002
        """Release the browser back to the pool."""
        self.semaphore.release()

    async def _create_browser(self) -> Browser:
        """Create a new browser instance."""
        return await self.playwright.chromium.launch(headless=True, args=self._launch_args)

    def _update_last_used(self, target_browser: Browser) -> None:
        """Update the last used timestamp for a browser."""
        for i, (browser, _) in enumerate(self.browsers):
            if browser == target_browser:
                self.browsers[i] = (browser, time.time())
                break

    async def _cleanup_idle_browsers(self) -> None:
        """Remove browsers that have been idle for too long."""
        now = time.time()
        active_browsers = []

        for browser, last_used in self.browsers:
            if now - last_used > self.idle_timeout:
                await browser.close()
            else:
                active_browsers.append((browser, last_used))

        self.browsers = active_browsers

    async def _periodic_cleanup(self) -> None:
        """Background task to periodically clean up idle browsers."""
        logger = logging.getLogger(__name__)
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._cleanup_idle_browsers()
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error during browser cleanup")
                await asyncio.sleep(60)  # Continue after error

    async def close(self) -> None:
        """Close all the browsers in the pool and stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

        for browser, _ in self.browsers:
            await browser.close()

        if self.playwright:
            await self.playwright.stop()

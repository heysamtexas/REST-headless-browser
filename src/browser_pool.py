from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from playwright.async_api import async_playwright

if TYPE_CHECKING:
    from playwright.async_api import Browser

MAX_BROWSERS = 5


class BrowserPool:
    """Creates a pool of browsers that can be used by multiple clients concurrently."""

    def __init__(self, max_browsers: int = MAX_BROWSERS) -> None:
        """Initialize the BrowserPool."""
        self.max_browsers = max_browsers
        self.semaphore = asyncio.Semaphore(max_browsers)
        self.playwright = None
        self.browsers: list[Browser] = []

    async def initialize(self) -> None:
        """Initialize the BrowserPool by starting the Playwright instance and launching the browsers."""
        self.playwright = await async_playwright().start()
        for _ in range(self.max_browsers):
            browser: Browser = await self.playwright.chromium.launch()
            self.browsers.append(browser)

    async def get_browser(self) -> Browser:
        """Get a browser from the pool."""
        await self.semaphore.acquire()
        return self.browsers[0]  # Simplified for example; could implement round-robin

    async def release_browser(self, browser: Browser) -> None:  # noqa: ARG002
        """Release the browser back to the pool."""
        self.semaphore.release()

    async def close(self) -> None:
        """Close all the browsers in the pool."""
        for browser in self.browsers:
            await browser.close()
        await self.playwright.stop()

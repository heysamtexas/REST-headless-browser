from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from link_categorizer import categorize_link
from pydantic import BaseModel

if TYPE_CHECKING:
    import logging


if TYPE_CHECKING:
    from cachetools import TTLCache

    from browser_pool import BrowserPool

# get current directory of the script
BASE_DIR = Path(__file__).resolve().parent

# This script will be injected into the page to extract the data we need
with Path(BASE_DIR / "static/_page_dumper.js").open() as f:
    PAGE_DUMP_SCRIPT = f.read()


class PageDump(BaseModel):
    """Data model for a page dump."""

    html: str
    scripts: list
    stylesheets: list
    variables: dict
    images: list


async def focused_page_dump(url: str, cache: TTLCache, browser_pool: BrowserPool, logger: logging.Logger) -> dict:
    """Scrape a webpage and extract the data we need."""
    if url in cache:
        msg = f"Returning cached result for {url}"
        logger.info(msg)
        return cache[url]

    browser = await browser_pool.get_browser()
    context = None
    try:
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, wait_until="load")
        dump = await page.evaluate(PAGE_DUMP_SCRIPT)
    except Exception as e:
        msg = f"Error scraping {url}: {e!s}"
        logger.exception(msg)
        raise
    finally:
        if context:
            await context.close()
        await browser_pool.release_browser(browser)

    for link in dump["links"]:
        link["category"] = categorize_link(link)

    cache[url] = dump
    return dump

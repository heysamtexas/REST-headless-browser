import logging
from contextlib import asynccontextmanager

from cachetools import TTLCache
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import HttpUrl

from browser_pool import BrowserPool
from page_dumper import focused_page_dump
from screenshot import ScreenshotParams, capture_screenshot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup cache
cache = TTLCache(maxsize=100, ttl=3600)  # Cache for 1 hour
browser_pool = BrowserPool()


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:  # noqa: ARG001
    """Context manager to handle startup and shutdown of the browser pool."""
    # Startup
    await browser_pool.initialize()
    logger.info("Browser pool initialized with idle timeout cleanup")

    yield  # This is where the app runs

    # Shutdown
    await browser_pool.close()
    logger.info("Browser pool shut down")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/screenshot", response_class=Response)
async def post_screenshot(params: ScreenshotParams) -> Response:
    """Capture a screenshot of a webpage."""
    return await capture_screenshot(params, browser_pool)


@app.get(
    "/page-dump",
    summary="Given a url, dump the contents of a webpage (HTML, scripts, stylesheets, JS variable names).",
    description="Use a playwright browser to scrape a webpage and dump its contents. Return a JSON object with the page contents.",
    response_description="JSON object with the page contents",
    responses={
        200: {"description": "Page dump"},
        500: {"description": "Internal server error"},
    },
    tags=["scraping"],
)
async def get_page_dump(url: HttpUrl, background_tasks: BackgroundTasks) -> dict:
    """Given a url, dump the contents of a webpage (HTML, scripts, stylesheets, JS variable names)."""
    try:
        background_tasks.add_task(log_scrape_stats, str(url))
        return await focused_page_dump(str(url), cache, browser_pool, logger)
    except Exception as e:
        msg = f"Error processing request for {url}: {e!s}"
        logger.exception(msg)
        raise HTTPException(status_code=500, detail=str(e)) from e


async def log_scrape_stats(url: str) -> None:
    """Log stats about a scrape."""
    # This could be expanded to log to a database or external monitoring service
    msg = f"Completed scrape for {url}"
    logger.info(msg)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104

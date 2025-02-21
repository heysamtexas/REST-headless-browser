import logging

from fastapi import HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, HttpUrl, field_validator

from browser_pool import BrowserPool

logger = logging.getLogger(__name__)


class ScreenshotParams(BaseModel):
    """Parameters for capturing a screenshot of a webpage."""

    url: HttpUrl
    width: int
    height: int
    format: str = "png"
    full_page: bool = False

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Ensure the format is either "png", "jpeg", or "jpg"."""
        if v.lower() not in ["png", "jpeg", "jpg"]:
            msg = 'Format must be either "png", "jpeg", or "jpg"'
            raise ValueError(msg)
        return "jpeg" if v.lower() in ["jpeg", "jpg"] else v.lower()

    @field_validator("width", "height")
    @classmethod
    def validate_dimensions(cls, v: int) -> int:
        """Ensure the dimensions are positive integers."""
        if v is None or v <= 0:
            msg = "Dimensions must be positive integers"
            raise ValueError(msg)
        return v


async def capture_screenshot(params: ScreenshotParams, browser_pool: BrowserPool) -> Response:
    """Capture a screenshot of a webpage."""
    browser = await browser_pool.get_browser()
    try:
        context = await browser.new_context(viewport={"width": params.width, "height": params.height or 600})
        page = await context.new_page()

        await page.goto(str(params.url), wait_until="load")

        screenshot_params = {"full_page": params.full_page, "type": params.format}
        screenshot = await page.screenshot(**screenshot_params)

        await context.close()

    except Exception as e:
        msg = f"Error capturing screenshot for {params.url}: {e!s}"
        logger.exception(msg)
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        await browser_pool.release_browser(browser)

    return Response(content=screenshot, media_type=f"image/{params.format}")

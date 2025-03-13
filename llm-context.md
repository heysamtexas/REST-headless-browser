# REST Headless Browser - LLM Context

This document provides technical context about the REST Headless Browser project to help AI assistants understand the codebase structure and purpose.

## Project Overview

REST Headless Browser is a FastAPI service that provides a REST API wrapper around Playwright for web scraping and screenshot capabilities. The service is designed to simplify the process of extracting data from modern web applications that rely heavily on JavaScript for content rendering.

Key features:
- Screenshot capture endpoint
- Complete page data extraction (HTML, scripts, styles, DOM variables)
- Browser instance pooling for efficient resource usage
- Result caching to reduce redundant requests

## Architecture Components

### `browser_pool.py`
Manages a pool of Playwright browser instances to be shared among concurrent requests.

```python
# Core functionality
class BrowserPool:
    def __init__(self, max_browsers: int = MAX_BROWSERS)
    async def initialize(self) -> None
    async def get_browser(self) -> Browser
    async def release_browser(self, browser: Browser) -> None
    async def close(self) -> None
```

The pool implements a semaphore to limit concurrent browser usage and provides methods for browser acquisition and release.

### `screenshot.py`
Handles screenshot capture requests with configurable parameters:
- URL targeting
- Viewport dimensions
- Image format (PNG/JPEG)
- Full-page vs viewport capture

The `ScreenshotParams` model validates incoming request parameters, and the `capture_screenshot` function handles the actual browser interaction.

### `page_dumper.py`
Extracts comprehensive data from web pages by injecting JavaScript into the rendered page. The extracted data includes:
- Complete HTML content
- JavaScript scripts (sources and contents)
- CSS stylesheets and rules
- JavaScript variables (window, localStorage, sessionStorage)
- Images and their attributes
- Links and their properties

The extraction is performed by the JavaScript in `static/_page_dumper.js`, which is injected into the target page.

### `main.py`
The application entry point that:
- Initializes the FastAPI application
- Sets up CORS middleware
- Manages browser pool lifecycle
- Implements the API endpoints
- Configures the TTL cache for results

## Technical Implementation Details

### Browser Pool Implementation
The browser pool initializes a fixed number of browser instances (default: 5) at startup and manages their allocation to incoming requests using an asyncio semaphore. This approach prevents resource exhaustion while allowing concurrent processing.

### Page Data Extraction
The page data extraction uses a JavaScript function that is evaluated in the context of the loaded page:

```javascript
() => {
    return {
        html: document.documentElement.outerHTML,
        scripts: Array.from(document.scripts).map(script => ({ ... })),
        stylesheets: Array.from(document.styleSheets).map(sheet => { ... }),
        variables: {
            global: Object.keys(window),
            localStorage: Object.keys(localStorage),
            sessionStorage: Object.keys(sessionStorage)
        },
        images: Array.from(document.images).map(img => ({ ... })),
        links: Array.from(document.links).map(link => ({ ... })),
    };
}
```

This approach allows access to client-side JavaScript state that would be inaccessible to traditional HTTP request-based scrapers.

### Caching Strategy
The application uses a TTLCache with a default one-hour expiration to store page dump results, reducing redundant requests to the same URLs and improving response times for repeated queries.

```python
# Cache configuration in main.py
cache = TTLCache(maxsize=100, ttl=3600)  # Cache for 1 hour
```

### FastAPI Context Management
The application uses FastAPI's lifespan context manager to handle the initialization and cleanup of the browser pool:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    # Startup
    await browser_pool.initialize()

    yield  # Application runs here

    # Shutdown
    await browser_pool.close()
```

## Common Usage Patterns

### Screenshot Capture

```python
import requests

response = requests.post("http://localhost:8000/screenshot", json={
    "url": "https://example.com",
    "width": 1280,
    "height": 800,
    "format": "png",
    "full_page": True
})

with open("screenshot.png", "wb") as f:
    f.write(response.content)
```

### Page Data Extraction

```python
import requests

response = requests.get(
    "http://localhost:8000/page-dump",
    params={"url": "https://example.com"}
)

data = response.json()

# Access different components of the page data
html = data["html"]
scripts = data["scripts"]
variables = data["variables"]["global"]
localStorage = data["variables"]["localStorage"]
images = data["images"]
```

### Extracting Data from JavaScript Variables

For websites that store data in JavaScript variables rather than HTML:

```python
import requests
import json

response = requests.get(
    "http://localhost:8000/page-dump",
    params={"url": "https://example.com"}
)

data = response.json()

# Check what variables are available
available_variables = data["variables"]["global"]

# The actual values would need to be extracted with a custom script
# that references these variable names
```

## Technical Limitations and Considerations

### Browser Resources
Each browser instance consumes significant memory. The default pool size of 5 browsers is a balance between concurrency and resource usage. For production deployment, consider:
- Adjusting the pool size based on available system resources
- Implementing a queue for requests that exceed the concurrent capacity
- Monitoring memory usage to prevent OOM conditions

### JavaScript Execution
The page dump functionality relies on JavaScript execution in the target page. This means:
- The extraction script runs in the same context as the page's own scripts
- It may be affected by CSP (Content Security Policy) restrictions
- It cannot access variables in closures or private scopes
- It may be detected by sophisticated anti-scraping measures

### CORS Limitations
The stylesheets extraction may be limited by CORS policies:

```javascript
try {
    return {
        href: sheet.href,
        rules: Array.from(sheet.cssRules || []).map(rule => rule.cssText)
    };
} catch (e) {
    return { href: sheet.href, rules: ['Unable to access rules due to CORS'] };
}
```

### Cache Considerations
The TTL cache implementation:
- Does not persist across service restarts
- Has a fixed size limit (100 entries by default)
- Uses URL as the cache key (no consideration for query parameters or headers)

## Troubleshooting Guide

### Dynamic Content Loading
Problem: Content loaded via scroll or interaction events isn't captured.
Solution: Consider implementing page interaction before extraction:

```python
# Example of scrolling before extraction
async def scroll_and_capture(page):
    await page.evaluate("""
        window.scrollTo(0, document.body.scrollHeight);
        // Wait for potential lazy-loaded content
        await new Promise(r => setTimeout(r, 2000));
    """)
    # Then proceed with data extraction
```

### Authentication Requirements
Problem: Content behind login pages isn't accessible.
Solution: Implement session handling:

```python
# Example of handling authentication
async def authenticated_page_dump(url, username, password):
    browser = await browser_pool.get_browser()
    try:
        page = await browser.new_page()
        await page.goto("https://example.com/login")
        await page.fill("#username", username)
        await page.fill("#password", password)
        await page.click("#login-button")
        # Verify login success
        await page.wait_for_selector(".logged-in-indicator")
        # Now navigate to the target URL
        await page.goto(url)
        # Extract data
        dump = await page.evaluate(PAGE_DUMP_SCRIPT)
        return dump
    finally:
        await browser_pool.release_browser(browser)
```

### Timeouts and Performance
Problem: Slow-loading pages cause timeouts.
Solution: Adjust timeouts and waiting strategies:

```python
# Configurable timeout example
async def page_dump_with_timeout(url, timeout_ms=30000):
    browser = await browser_pool.get_browser()
    try:
        page = await browser.new_page()
        # Increase navigation timeout
        page.set_default_navigation_timeout(timeout_ms)
        await page.goto(url, wait_until="networkidle")
        # Wait additional time for any animations or delayed scripts
        await page.wait_for_timeout(1000)
        dump = await page.evaluate(PAGE_DUMP_SCRIPT)
        return dump
    finally:
        await browser_pool.release_browser(browser)
```

## Future Development Considerations

Potential enhancements identified in the codebase:
- Docker Compose configuration for production deployment
- Enhanced error handling and reporting
- Rate limiting to prevent self-DoS
- Authentication mechanisms for the API
- Proxy rotation for avoiding IP-based blocking
- Cookie and session management
- Comprehensive testing suite

## Browser Extension Component

The repository includes an experimental browser extension for capturing full-page screenshots directly in the browser. This appears to be a separate component designed as a fallback when the headless browser approach has limitations. The extension:

- Captures the visible viewport multiple times while scrolling
- Stitches these captures together to create a full-page screenshot
- Sends the result to a configurable server endpoint

Note that this extension is marked as highly experimental and not intended for production use.

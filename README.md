# REST Headless Browser

## Yet Another Headless Browser Service

*Because clearly what the world needed was another way to scrape websites that don't want to be scraped.*

Listen up, youngsters. Back in my day, websites were just HTML files. Clean, simple, readable. You could fetch them with a single HTTP request and be done with it. No JavaScript shenanigans, no reactive nonsense, no "single page applications" that are actually 15MB of obfuscated code.

But we live in darker times now.

So I made this. A REST API wrapper around Playwright that lets you extract what you need from the cesspool of modern web development without losing your sanity (what's left of it, anyway).

## What This Actually Does

This service provides two primary endpoints:
- `/screenshot` - Takes pictures of websites. Revolutionary, I know.
- `/page-dump` - Gets you the ACTUAL content of a page, including HTML, JavaScript, styles, and (most importantly) the variables lurking in the DOM. Because apparently that's where people hide the good stuff now.

It runs headless browsers in a pool so you don't have to manage them yourself. It caches results so you don't hammer the same sites repeatedly like some kind of scraping amateur. It's containerized because that's what we do now, apparently.

## Installation

You'll need Docker. If you don't have Docker, go get Docker. I'm not explaining how to install Python packages in 2025.

```bash
# Clone the repo
git clone https://github.com/heysamtexas/REST-headless-browser.git

# Build the Docker image
docker build -t rest-headless-browser .

# Run the container
docker run -p 8000:8000 rest-headless-browser

# Run with custom configuration
docker run -e BROWSER_MAX_BROWSERS=3 -e BROWSER_IDLE_TIMEOUT=180 -p 8000:8000 rest-headless-browser
```

Or use docker-compose if you're feeling fancy:

```bash
docker-compose up
```

Oh wait, there's no docker-compose.yml file yet. Add it to the TODO list. Fine, I'll do it myself eventually.

## Usage

### Taking Screenshots

```bash
curl -X POST "http://localhost:8000/screenshot" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "width": 1280, "height": 800, "format": "png", "full_page": true}'
```

This returns a binary image. Save it, look at it, do whatever people do with screenshots these days.

### Getting Page Data

```bash
curl -X GET "http://localhost:8000/page-dump?url=https://example.com"
```

This returns a JSON object containing:
- `html`: The full HTML of the page
- `scripts`: All scripts, including their content
- `stylesheets`: All CSS rules (that aren't blocked by CORS, because of course they are)
- `variables`: Global variables, localStorage, and sessionStorage
- `images`: All images on the page
- `links`: All links on the page

Use this to find the data you actually care about before writing a more targeted scraper.

## Configuration

The service uses dynamic browser management - it starts with 0 browsers and creates them on-demand up to a configurable maximum. Idle browsers are automatically shut down after 5 minutes to save memory.

### Environment Variables

- `BROWSER_MAX_BROWSERS`: Maximum concurrent browsers (default: 2, minimum: 1)
- `BROWSER_IDLE_TIMEOUT`: Browser idle timeout in seconds (default: 300)

### Cache Settings

The page cache keeps results for an hour. Adjust the TTL in `src/main.py` if you need to.

### Resource Usage

The service is optimized for efficient memory usage:

- **Idle state**: ~160MB (0 browsers running)
- **Active usage**: ~250MB per browser instance
- **Scaling**: Creates browsers on-demand when requests arrive
- **Cleanup**: Automatically shuts down idle browsers after timeout period

This means your service will use minimal resources when idle and scale up only when needed.

## Why This Exists

Because I'm tired of websites that:
1. Load content with JavaScript long after the DOM is "ready"
2. Hide data in JavaScript variables instead of the HTML
3. Use seventeen layers of divs to display what should be a simple table
4. Implement "innovative" scroll behavior that breaks normal scraping
5. Change their DOM structure every two weeks for "improved user experience"

I've been scraping websites since before half of today's "senior" developers were born. Trust me when I say this is the easiest way to deal with the abomination that is modern web development.

## TODO List

Because there's always more to do:

- [ ] Add a proper docker-compose.yml file for production setups
- [ ] Implement proper error handling that doesn't just dump tracebacks
- [ ] Add rate limiting to prevent self-DoS
- [ ] Create actual documentation for the API
- [ ] Add support for cookies and sessions
- [ ] Implement proxy rotation
- [ ] Clean up that experimental browser extension... or just remove it
- [ ] Add authentication so the whole internet doesn't use your instance
- [ ] Write some actual tests (ha!)

## Contributing

Found a bug? Fixed a bug? Added a feature? Submit a PR. I'll review it when I get around to it.

Want to complain? Open an issue. I'll read it while sipping coffee and reminiscing about the days when "web scraping" meant "wget" and a grep command.

## License

MIT License. Do what you want, just don't blame me when it breaks.

## Final Thoughts

This tool won't solve all your scraping problems. Nothing will. The web is a constantly evolving battlefield between those who want to share information and those who want to control how it's accessed.

But at least with this, you have a fighting chance.

Now get off my lawn.

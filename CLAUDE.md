# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

REST Headless Browser is a FastAPI-based service that provides web scraping capabilities using Playwright. It offers two main endpoints:
- `/screenshot` - Captures screenshots of web pages
- `/page-dump` - Extracts comprehensive page data including HTML, scripts, stylesheets, DOM variables, images, and links

## Architecture

The service is built around a **browser pool pattern** to manage concurrent browser instances efficiently:

- **BrowserPool** (`src/browser_pool.py`): Manages a pool of Playwright browsers with semaphore-based concurrency control (default: 5 browsers)
- **PageDumper** (`src/page_dumper.py`): Handles page scraping by injecting JavaScript (`src/static/_page_dumper.js`) to extract data
- **Screenshot** (`src/screenshot.py`): Captures screenshots with configurable dimensions and formats
- **Main FastAPI app** (`src/main.py`): Orchestrates the service with TTL caching (1 hour) and CORS enabled

Key architectural decisions:
- Uses async/await throughout for concurrency
- Implements TTL caching to reduce repeated requests
- Browser pool prevents resource exhaustion
- Injects custom JavaScript for comprehensive data extraction

## Development Commands

### Environment Setup
```bash
make bootstrap-dev    # Creates .venv, installs dependencies, sets up pre-commit hooks
make env             # Creates env file from env.example
```

### Docker Development
```bash
make build           # Build Docker image
make run            # Run containerized service on port 8000
docker-compose up    # Alternative container setup
```

### Code Quality
```bash
ruff check          # Lint code (configured in pyproject.toml)
ruff format         # Format code
pre-commit run --all-files  # Run all pre-commit hooks
```

### Local Development
```bash
# Run the service locally
python src/main.py

# Or with uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Browser Pool Settings
- `MAX_BROWSERS` in `src/browser_pool.py` (default: 5)
- Adjust based on available system memory

### Cache Settings
- TTL cache: 1 hour (3600 seconds) in `src/main.py`
- Cache size: 100 entries maximum

### Python Version
- Target: Python 3.12 (specified in pyproject.toml)

## Dependencies

**Core:**
- `fastapi` - Web framework
- `playwright` - Browser automation
- `cachetools` - TTL caching
- `pydantic` - Data validation
- `uvicorn` - ASGI server
- `link_categorizer` - Link classification

**Development:**
- `ruff` - Linting and formatting
- `pre-commit` - Git hooks
- `flit` - Package building

## Testing

Currently no test suite exists. The README mentions this as a TODO item.

## Browser Extension

There's an experimental browser extension in `src/browser_extension/` with:
- `manifest.json` - Extension manifest
- `background.js` - Background script
- `content.js` - Content script
- `README.md` - Extension documentation

The main README suggests this may be removed in the future.

## Git Workflow

### Handling Pre-commit Hooks

This repository uses pre-commit hooks (ruff, end-of-file-fixer, etc.) that automatically modify files during commits. When this happens:

1. **Pre-commit hook modifies files after initial commit attempt** - This is EXPECTED behavior
2. **Amend the commit to include hook changes** - Use `git commit --amend` to include the modifications
3. **After amending, check if the original commit was already pushed:**
   - If NOT pushed yet: Simply `git push` the amended commit
   - If already pushed: Consider the implications of rewriting history
4. **NEVER use `git reset --hard` when recent work exists** - Even if git shows "working tree clean", a hard reset will destroy the amended commit
5. **Branch divergence after amending is normal** - If you amend a local-only commit, pushing it normally is the correct action

**Key principle:** When pre-commit hooks modify files, amending is correct. Don't panic about divergence or try to "undo" the amendment. Just push the amended commit.

## Important Notes

- The service allows all CORS origins by default
- No authentication is implemented
- Error handling dumps tracebacks (mentioned as needing improvement)
- The browser pool uses a simplified round-robin approach (always returns browsers[0])
- Page dumps include link categorization using the `link_categorizer` library

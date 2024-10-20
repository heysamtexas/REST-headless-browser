# Experimental Full Page Screenshot Extension

## WARNING: Highly Experimental

This browser extension is in an extremely experimental state. It is not intended for production use and may contain bugs or security issues. Use at your own risk.

## Purpose

This Chrome extension is designed to capture full-page screenshots directly in the browser and submit them back to a FastAPI server. The screenshots are then saved in the server's cache.

### Key Features:
- Captures full-page screenshots, including content below the fold
- Works with dynamic and lazy-loaded content
- Sends screenshots directly to a specified server endpoint

## When to Use

This extension should only be used as a last resort, specifically:

1. When Playwright or other headless browser solutions fail to capture the screenshot correctly
2. For debugging purposes when server-side screenshot methods are ineffective
3. In scenarios where client-side capture is the only viable option

## Important Notes

- This extension requires broad permissions to function. Review the code carefully before installation.
- It is not optimized for performance and may struggle with very long pages or pages with complex layouts.
- The extension is designed to work with a specific FastAPI server setup. Ensure your server is configured to receive and process the screenshots.

## Installation

1. Open Google Chrome and go to chrome://extensions/.
2. Enable "Developer mode" using the toggle in the top right corner.
3. Click "Load unpacked" and select your extension directory.

Your extension should now be installed and visible in Chrome. Remember to reload the extension after making changes to your code.

## Usage

Visit a website that the crawler cannot seem to capture. Use this extension to take a screenshot of the full page.


## Security Considerations

- This extension can capture and send the full contents of any web page you visit. Use it only on trusted sites.
- Ensure that your server implements proper authentication and authorization to prevent unauthorized screenshot submissions.

## Limitations

- May not work correctly with some types of dynamic content or complex CSS layouts
- Performance may degrade with very large pages
- Not suitable for high-volume or production use cases

## Contributing

This is an experimental project. If you encounter issues or have suggestions for improvements, please open an issue in the repository.

## License

[Include appropriate license information here]

Remember: This extension is a specialized tool for specific scenarios where other methods have failed. It is not a replacement for robust, server-side screenshot solutions.

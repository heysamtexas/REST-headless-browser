() => {
    return {
        // Metadata about the dump itself
        url: window.location.href,
        timestamp: new Date().toISOString(),

        // Basic page metadata
        title: document.title || '',
        metaDescription: document.querySelector('meta[name="description"]')?.content || '',
        canonicalUrl: document.querySelector('link[rel="canonical"]')?.href || '',
        language: document.documentElement.lang || '',

        // Cookie information
        cookies: document.cookie.split(';').map(cookie => {
            const [name, ...rest] = cookie.split('=');
            return {
                name: name?.trim(),
                value: rest.join('=')?.trim(),
            };
        }),

        // Additional metadata that could be useful
        viewport: document.querySelector('meta[name="viewport"]')?.content,
        robots: document.querySelector('meta[name="robots"]')?.content,

        // Icons and logos
        favicons: Array.from(document.querySelectorAll('link[rel*="icon"]')).map(link => ({
            href: link.href,
            rel: link.rel,
            type: link.type,
            sizes: link.sizes?.value
        })),

        // JSON-LD
        jsonLd: Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
            .map(script => {
                try {
                    return JSON.parse(script.innerHTML);
                } catch (e) {
                    return { error: 'Invalid JSON-LD' };
                }
            }),

        // OpenGraph metadata
        openGraph: Array.from(document.querySelectorAll('meta[property^="og:"]'))
            .map(meta => ({
                property: meta.getAttribute('property'),
                content: meta.content
            })),

        // Twitter Card metadata
        twitterCard: Array.from(document.querySelectorAll('meta[name^="twitter:"]'))
            .map(meta => ({
                name: meta.getAttribute('name'),
                content: meta.content
            })),

        // RSS/Atom feeds
        feeds: Array.from(document.querySelectorAll('link[type*="rss"], link[type*="atom"], link[type*="application/rss+xml"], link[type*="application/atom+xml"]'))
            .map(link => ({
                href: link.href,
                title: link.title,
                type: link.type
            })),

        // ...existing code...
        html: document.documentElement.outerHTML,
        scripts: Array.from(document.scripts).map(script => ({
            src: script.src,
            type: script.type,
            content: script.innerHTML
        })),
        stylesheets: Array.from(document.styleSheets).map(sheet => {
            try {
                return {
                    href: sheet.href,
                    rules: Array.from(sheet.cssRules || []).map(rule => rule.cssText)
                };
            } catch (e) {
                return { href: sheet.href, rules: ['Unable to access rules due to CORS'] };
            }
        }),
        variables: {
            global: Object.keys(window),
            localStorage: Object.keys(localStorage),
            sessionStorage: Object.keys(sessionStorage)
        },
        images: Array.from(document.images).map(img => ({
            src: img.src,
            alt: img.alt,
            width: img.width,
            height: img.height
        })),
        links: Array.from(document.links).map(link => ({
            href: link.href,
            text: link.innerText.replace(/\s+/g, ' ').trim(),
            title: link.title.replace(/\s+/g, ' ').trim()
        }))
    };
}

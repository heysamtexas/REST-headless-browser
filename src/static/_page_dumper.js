() => {
    return {
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
            text: link.innerText,
            title: link.title
        })),
    };
}

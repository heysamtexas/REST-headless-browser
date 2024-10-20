function getFullPageSize() {
  return {
    width: Math.max(
      document.documentElement.scrollWidth,
      document.body.scrollWidth,
      document.documentElement.offsetWidth,
      document.body.offsetWidth,
      document.documentElement.clientWidth
    ),
    height: Math.max(
      document.documentElement.scrollHeight,
      document.body.scrollHeight,
      document.documentElement.offsetHeight,
      document.body.offsetHeight,
      document.documentElement.clientHeight
    )
  };
}

function captureFullPage(sendResponse) {
  const fullPageSize = getFullPageSize();
  let captures = [];
  let yPosition = 0;

  function captureNextSection() {
    window.scrollTo(0, yPosition);

    // Wait for any lazy-loaded content to appear
    setTimeout(() => {
      chrome.runtime.sendMessage({action: "captureVisible"}, (response) => {
        captures.push(response.dataUrl);
        yPosition += window.innerHeight;

        if (yPosition < fullPageSize.height) {
          captureNextSection();
        } else {
          sendResponse({
            captures: captures,
            fullWidth: fullPageSize.width,
            fullHeight: fullPageSize.height
          });
        }
      });
    }, 100);
  }

  captureNextSection();
  return true;  // Indicates we will send a response asynchronously
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "captureFullPage") {
    return captureFullPage(sendResponse);
  }
});

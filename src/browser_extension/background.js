chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: {tabId: tab.id},
    files: ['content.js']
  }, () => {
    chrome.tabs.sendMessage(tab.id, {action: "captureFullPage"}, (response) => {
      stitchScreenshots(response.captures, response.fullWidth, response.fullHeight);
    });
  });
});

function captureVisible() {
  return new Promise((resolve) => {
    chrome.tabs.captureVisibleTab(null, {format: "png"}, (dataUrl) => {
      resolve(dataUrl);
    });
  });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "captureVisible") {
    captureVisible().then(sendResponse);
    return true;  // Indicates we will send a response asynchronously
  }
});

function stitchScreenshots(captures, fullWidth, fullHeight) {
  const canvas = new OffscreenCanvas(fullWidth, fullHeight);
  const ctx = canvas.getContext('2d');

  let yPosition = 0;

  function loadAndDrawImage(dataUrl) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, yPosition);
        yPosition += img.height;
        resolve();
      };
      img.src = dataUrl;
    });
  }

  Promise.all(captures.map(loadAndDrawImage))
    .then(() => canvas.convertToBlob())
    .then(blob => {
      const reader = new FileReader();
      reader.onloadend = () => sendToServer(reader.result);
      reader.readAsDataURL(blob);
    });
}

function sendToServer(dataUrl) {
  fetch('https://your-server.com/upload', {
    method: 'POST',
    body: JSON.stringify({image: dataUrl}),
    headers: {'Content-Type': 'application/json'}
  })
  .then(response => response.json())
  .then(data => console.log('Success:', data))
  .catch((error) => console.error('Error:', error));
}

// Content DNA OS - Content Script
// Extracts text content from the current page for DNA analysis

(function () {
  'use strict';

  const runtime = typeof browser !== 'undefined' ? browser.runtime : chrome.runtime;

  // Listen for messages from the popup
  runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'extractContent') {
      const content = extractPageContent();
      sendResponse({ content });
    }
    return true; // Keep message channel open for async
  });

  function extractPageContent() {
    // Try to get the main content area first
    const selectors = [
      'article',
      '[role="main"]',
      'main',
      '.post-content',
      '.entry-content',
      '.article-body',
      '.story-body',
      '#content',
      '.content',
    ];

    for (const selector of selectors) {
      const el = document.querySelector(selector);
      if (el) {
        const text = cleanText(el.innerText);
        if (text.length > 100) return text;
      }
    }

    // Fallback: get selected text
    const selection = window.getSelection().toString().trim();
    if (selection.length > 20) return selection;

    // Last resort: body text (cleaned)
    return cleanText(document.body.innerText).slice(0, 5000);
  }

  function cleanText(text) {
    return text
      .replace(/\s+/g, ' ')      // collapse whitespace
      .replace(/\n{3,}/g, '\n\n') // limit newlines
      .trim()
      .slice(0, 5000);            // limit to 5000 chars
  }
})();

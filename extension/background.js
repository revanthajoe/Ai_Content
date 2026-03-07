// Content DNA OS - Background Service Worker
// Handles context menus and side panel logic

const runtime = typeof browser !== 'undefined' ? browser.runtime : chrome.runtime;
const contextMenus = typeof browser !== 'undefined' ? browser.contextMenus : chrome.contextMenus;
const sidePanel = typeof browser !== 'undefined' ? (browser.sidePanel || null) : (chrome.sidePanel || null);

// Create context menu on install
runtime.onInstalled.addListener(() => {
  contextMenus.create({
    id: 'dna-evolve-selection',
    title: 'Evolve with Content DNA OS',
    contexts: ['selection'],
  });

  contextMenus.create({
    id: 'dna-extract-selection',
    title: 'Extract DNA from selection',
    contexts: ['selection'],
  });
});

// Handle context menu clicks
contextMenus.onClicked.addListener((info, tab) => {
  if (!info.selectionText) return;

  const storage = typeof browser !== 'undefined' ? browser.storage : chrome.storage;

  if (info.menuItemId === 'dna-evolve-selection') {
    storage.local.set({
      pendingAction: 'evolve',
      pendingContent: info.selectionText,
    }, () => {
      // Open popup (Chrome doesn't support programmatic popup, open side panel if available)
      if (sidePanel && sidePanel.open) {
        sidePanel.open({ tabId: tab.id });
      }
    });
  }

  if (info.menuItemId === 'dna-extract-selection') {
    storage.local.set({
      pendingAction: 'extract-dna',
      pendingContent: info.selectionText,
    }, () => {
      if (sidePanel && sidePanel.open) {
        sidePanel.open({ tabId: tab.id });
      }
    });
  }
});

// Handle messages from popup/sidepanel
runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getPendingAction') {
    const storage = typeof browser !== 'undefined' ? browser.storage : chrome.storage;
    storage.local.get(['pendingAction', 'pendingContent'], (result) => {
      sendResponse(result);
      // Clear after reading
      storage.local.remove(['pendingAction', 'pendingContent']);
    });
    return true;
  }
});

// Content script that runs on Google search pages
// Detects searches and communicates with background script

(function() {
  'use strict';

  // Extract search query from URL
  function getSearchQuery() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('q');
  }

  // Check if this is a new search (not just a page navigation)
  let lastQuery = null;

  function checkForNewSearch() {
    const currentQuery = getSearchQuery();
    
    if (currentQuery && currentQuery !== lastQuery) {
      lastQuery = currentQuery;
      console.log('Query: New search detected:', currentQuery);
      
      // Send message to background script
      chrome.runtime.sendMessage({
        type: 'NEW_SEARCH',
        query: currentQuery,
        url: window.location.href
      }, (response) => {
        if (chrome.runtime.lastError) {
          console.error('Query error:', chrome.runtime.lastError);
        } else {
          console.log('Query: Search sent to background script');
        }
      });
      
      // Add Query button to Google's search page
      addQueryButton(currentQuery);
    }
  }

  // Add a floating button to trigger Query manually
  function addQueryButton(query) {
    // Remove existing button if present
    const existingBtn = document.getElementById('query-btn');
    if (existingBtn) {
      existingBtn.remove();
    }

    const button = document.createElement('button');
    button.id = 'query-btn';
    button.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M10 7V10L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>Get Better Results</span>
    `;
    
    button.style.cssText = `
      position: fixed;
      bottom: 30px;
      right: 30px;
      background: linear-gradient(135deg, #7FA8A0 0%, #6B8B9E 100%);
      color: white;
      border: none;
      border-radius: 30px;
      padding: 12px 24px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 0 25px rgba(127, 168, 160, 0.5);
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.3s ease;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    button.addEventListener('mouseenter', () => {
      button.style.transform = 'translateY(-2px)';
      button.style.boxShadow = '0 0 35px rgba(127, 168, 160, 0.7)';
    });

    button.addEventListener('mouseleave', () => {
      button.style.transform = 'translateY(0)';
      button.style.boxShadow = '0 0 25px rgba(127, 168, 160, 0.5)';
    });

    button.addEventListener('click', () => {
      // Send message to open Query results
      chrome.runtime.sendMessage({
        type: 'OPEN_QUERY',
        query: query
      });
    });

    document.body.appendChild(button);
  }

  // Check on initial load
  checkForNewSearch();

  // Monitor URL changes (for when users navigate with browser buttons)
  let lastUrl = location.href;
  new MutationObserver(() => {
    const currentUrl = location.href;
    if (currentUrl !== lastUrl) {
      lastUrl = currentUrl;
      checkForNewSearch();
    }
  }).observe(document, { subtree: true, childList: true });

})();


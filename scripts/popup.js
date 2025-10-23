// Popup script

document.getElementById('searchBtn').addEventListener('click', () => {
  // Open Google search in a new tab
  chrome.tabs.create({
    url: 'https://www.google.com/search?q=teach+me+biology',
    active: true
  });
  
  // Close the popup
  window.close();
});


// Results page script - handles fetching and displaying categorized results

(function() {
  'use strict';

  // Get search query from URL
  const urlParams = new URLSearchParams(window.location.search);
  const searchQuery = urlParams.get('q');

  // DOM elements
  const loadingContainer = document.getElementById('loadingContainer');
  const resultsContainer = document.getElementById('resultsContainer');
  const errorContainer = document.getElementById('errorContainer');
  const searchQueryEl = document.getElementById('searchQuery');
  const metadataEl = document.getElementById('metadata');

  // Initialize
  if (searchQuery) {
    searchQueryEl.textContent = `"${searchQuery}"`;
    fetchAndDisplayResults(searchQuery);
  } else {
    showError('No search query provided');
  }

  async function fetchAndDisplayResults(query) {
    try {
      // Request results from background script
      chrome.runtime.sendMessage({
        type: 'FETCH_RESULTS',
        query: query
      }, (response) => {
        if (chrome.runtime.lastError) {
          showError('Failed to communicate with extension');
          return;
        }

        if (response.success) {
          displayResults(response.results);
        } else {
          showError(response.error || 'Failed to fetch results');
        }
      });
    } catch (error) {
      console.error('Error:', error);
      showError(error.message);
    }
  }

  function displayResults(data) {
    // Hide loading, show results
    loadingContainer.style.display = 'none';
    resultsContainer.style.display = 'block';

    // Update stats
    if (data.metadata) {
      document.getElementById('totalResults').textContent = data.metadata.totalResults || 0;
      document.getElementById('processingTime').textContent = data.metadata.processingTime || '0s';
      document.getElementById('searchDepth').textContent = data.metadata.searchDepth || 0;
    }

    // Display each category
    const categories = data.categories || {};

    // Map 'articles' from backend to 'websites' section in frontend
    if (categories.articles && categories.articles.length > 0) {
      displayCategory('websites', categories.articles);
    } else {
      hideSection('websitesSection');
    }

    if (categories.videos && categories.videos.length > 0) {
      displayCategory('videos', categories.videos);
    } else {
      hideSection('videosSection');
    }

    // Hide sections not currently populated by backend
    hideSection('academicSection');
    hideSection('coursesSection');
    hideSection('booksSection');
  }

  function displayCategory(categoryName, results) {
    const resultsGrid = document.getElementById(`${categoryName}Results`);
    resultsGrid.innerHTML = '';

    // Sort by credibility score (highest first) and assign rankings
    const sortedResults = [...results].sort((a, b) => (b.credibility || 0) - (a.credibility || 0));

    sortedResults.forEach((result, index) => {
      const ranking = index + 1; // 1, 2, 3, etc.
      const card = createResultCard(result, categoryName, ranking);
      card.style.animationDelay = `${index * 0.05}s`;
      resultsGrid.appendChild(card);
    });
  }

  function createResultCard(result, category, ranking) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    // Get URL from either 'url' or 'link' field
    const url = result.url || result.link || '#';
    card.onclick = () => window.open(url, '_blank');

    let metaItems = '';

    // Determine ranking class for styling
    let rankClass = 'rank-other';
    if (ranking === 1) rankClass = 'rank-1';
    else if (ranking === 2) rankClass = 'rank-2';
    else if (ranking === 3) rankClass = 'rank-3';

    // Add credibility score
    if (result.credibility !== undefined) {
      metaItems += `<div class="meta-item"><span class="meta-label">Credibility:</span> ${result.credibility}%</div>`;
    }

    // Add model used info
    if (result.model_used) {
      const modelLabel = result.model_used === 'gcp-vertex-ai' ? 'Cloud AI Model' : 'Local Scorer';
      metaItems += `<div class="meta-item"><span class="meta-label">Ranked by:</span> ${modelLabel}</div>`;
    }

    // Add category-specific metadata
    if (category === 'videos') {
      if (result.duration) {
        metaItems += `<div class="meta-item"><span class="meta-label">Duration:</span> ${result.duration}</div>`;
      }
      if (result.views) {
        metaItems += `<div class="meta-item"><span class="meta-label">Views:</span> ${result.views}</div>`;
      }
    }

    // Get description from either 'description' or 'snippet' field
    const description = result.description || result.snippet || 'No description available';
    const source = result.source || 'Unknown source';

    card.innerHTML = `
      <div class="result-header">
        <div class="result-title">${escapeHtml(result.title || 'Untitled')}</div>
        <div class="ranking-badge ${rankClass}">${ranking}</div>
      </div>
      <div class="result-source">${escapeHtml(source)}</div>
      <div class="result-description">${escapeHtml(description)}</div>
      ${metaItems ? `<div class="result-meta">${metaItems}</div>` : ''}
    `;

    return card;
  }

  function hideSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
      section.style.display = 'none';
    }
  }

  function showError(message) {
    loadingContainer.style.display = 'none';
    resultsContainer.style.display = 'none';
    errorContainer.style.display = 'flex';
    document.getElementById('errorMessage').textContent = message;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

})();


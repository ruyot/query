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

    if (categories.academic && categories.academic.length > 0) {
      displayCategory('academic', categories.academic);
    } else {
      hideSection('academicSection');
    }

    if (categories.videos && categories.videos.length > 0) {
      displayCategory('videos', categories.videos);
    } else {
      hideSection('videosSection');
    }

    if (categories.courses && categories.courses.length > 0) {
      displayCategory('courses', categories.courses);
    } else {
      hideSection('coursesSection');
    }

    if (categories.websites && categories.websites.length > 0) {
      displayCategory('websites', categories.websites);
    } else {
      hideSection('websitesSection');
    }

    if (categories.books && categories.books.length > 0) {
      displayCategory('books', categories.books);
    } else {
      hideSection('booksSection');
    }
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
    card.onclick = () => window.open(result.url, '_blank');

    let metaItems = '';

    // Determine ranking class for styling
    let rankClass = 'rank-other';
    if (ranking === 1) rankClass = 'rank-1';
    else if (ranking === 2) rankClass = 'rank-2';
    else if (ranking === 3) rankClass = 'rank-3';

    // Add category-specific metadata (without emojis)
    if (category === 'videos') {
      if (result.duration) {
        metaItems += `<div class="meta-item"><span class="meta-label">Duration:</span> ${result.duration}</div>`;
      }
      if (result.views) {
        metaItems += `<div class="meta-item"><span class="meta-label">Views:</span> ${result.views}</div>`;
      }
    } else if (category === 'courses') {
      if (result.rating) {
        metaItems += `<div class="meta-item"><span class="meta-label">Rating:</span> ${result.rating}/5</div>`;
      }
      if (result.students) {
        metaItems += `<div class="meta-item"><span class="meta-label">Students:</span> ${result.students}</div>`;
      }
    } else if (category === 'books') {
      if (result.rating) {
        metaItems += `<div class="meta-item"><span class="meta-label">Rating:</span> ${result.rating}/5</div>`;
      }
    } else if (category === 'academic') {
      if (result.publicationDate) {
        metaItems += `<div class="meta-item"><span class="meta-label">Published:</span> ${result.publicationDate}</div>`;
      }
    }

    card.innerHTML = `
      <div class="result-header">
        <div class="result-title">${escapeHtml(result.title)}</div>
        <div class="ranking-badge ${rankClass}">${ranking}</div>
      </div>
      <div class="result-source">${escapeHtml(result.source)}</div>
      <div class="result-description">${escapeHtml(result.description)}</div>
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


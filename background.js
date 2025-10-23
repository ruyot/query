// Background service worker
// Handles communication between content script and results page

// Store the current search query
let currentSearch = null;

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message);

  if (message.type === 'NEW_SEARCH') {
    currentSearch = {
      query: message.query,
      timestamp: Date.now(),
      url: message.url
    };
    
    // Automatically open Query results in new tab
    // You can disable this if you only want manual triggering via button
    openQueryTab(message.query);
    
    sendResponse({ success: true });
  } 
  else if (message.type === 'OPEN_QUERY') {
    openQueryTab(message.query);
    sendResponse({ success: true });
  }
  else if (message.type === 'GET_SEARCH_DATA') {
    // Results page requesting search data
    sendResponse({ searchData: currentSearch });
  }
  else if (message.type === 'FETCH_RESULTS') {
    // Fetch ranked results from backend
    fetchRankedResults(message.query)
      .then(results => sendResponse({ success: true, results }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }

  return false;
});

// Open Query results in new tab
function openQueryTab(query) {
  chrome.tabs.create({
    url: `results.html?q=${encodeURIComponent(query)}`,
    active: true
  });
}

// Fetch ranked results from your backend API
async function fetchRankedResults(query) {
  try {
    // TODO: Replace with your actual backend API endpoint
    const API_ENDPOINT = 'https://your-api-endpoint.com/api/search';
    
    // For now, return mock data for frontend development
    // Remove this and uncomment the fetch below when backend is ready
    return getMockResults(query);

    /*
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query })
    });

    if (!response.ok) {
      throw new Error('Backend API request failed');
    }

    const data = await response.json();
    return data.results;
    */
  } catch (error) {
    console.error('Error fetching results:', error);
    // Return mock data as fallback
    return getMockResults(query);
  }
}

// Mock data for development
function getMockResults(query) {
  return new Promise((resolve) => {
    // Simulate API delay
    setTimeout(() => {
      resolve({
        query: query,
        categories: {
          academic: [
            {
              title: "Understanding Biology: A Comprehensive Guide",
              url: "https://example.com/biology-guide",
              description: "Peer-reviewed research article covering fundamental concepts in biology, including cellular processes, genetics, and evolution.",
              source: "Nature Journal",
              credibility: 95,
              publicationDate: "2024"
            },
            {
              title: "Introduction to Molecular Biology",
              url: "https://example.com/molecular-bio",
              description: "Academic paper exploring molecular biology principles with detailed explanations and research findings.",
              source: "Science Direct",
              credibility: 92,
              publicationDate: "2023"
            },
            {
              title: "Biology Education Research Papers",
              url: "https://example.com/bio-research",
              description: "Collection of research papers focusing on effective biology teaching methods and curriculum development.",
              source: "JSTOR",
              credibility: 88,
              publicationDate: "2024"
            }
          ],
          videos: [
            {
              title: "Biology 101: Complete Beginner's Course",
              url: "https://youtube.com/watch?v=example1",
              description: "Comprehensive video series covering all major biology topics, perfect for beginners and students.",
              source: "Khan Academy",
              duration: "45:30",
              views: "2.5M",
              credibility: 90
            },
            {
              title: "Crash Course Biology - Full Series",
              url: "https://youtube.com/watch?v=example2",
              description: "Fast-paced, engaging biology course covering everything from cells to ecosystems.",
              source: "Crash Course",
              duration: "12:15",
              views: "5.1M",
              credibility: 88
            },
            {
              title: "MIT OpenCourseWare: Introduction to Biology",
              url: "https://youtube.com/watch?v=example3",
              description: "Full MIT university-level biology course, free and accessible to everyone.",
              source: "MIT",
              duration: "1:15:22",
              views: "890K",
              credibility: 95
            }
          ],
          courses: [
            {
              title: "Biology: The Science of Life",
              url: "https://coursera.org/biology-course",
              description: "Full online course with certificates, taught by university professors.",
              source: "Coursera",
              rating: 4.8,
              students: "125K",
              credibility: 92
            },
            {
              title: "Introduction to Biology Specialization",
              url: "https://edx.org/bio-spec",
              description: "Multi-course specialization covering genetics, evolution, and ecology.",
              source: "edX",
              rating: 4.7,
              students: "89K",
              credibility: 90
            }
          ],
          websites: [
            {
              title: "Biology Online Tutorial",
              url: "https://biologytutorial.com",
              description: "Interactive tutorials with quizzes and visual aids for learning biology.",
              source: "Biology Tutorial",
              credibility: 75
            },
            {
              title: "Learn Biology - Step by Step Guide",
              url: "https://learnbiology.com",
              description: "Structured learning path for biology students with practice problems.",
              source: "Learn Biology",
              credibility: 72
            }
          ],
          books: [
            {
              title: "Campbell Biology (12th Edition)",
              url: "https://amazon.com/campbell-biology",
              description: "The most popular biology textbook used in universities worldwide.",
              source: "Amazon",
              rating: 4.6,
              credibility: 93
            },
            {
              title: "Biology for Dummies",
              url: "https://wiley.com/biology-dummies",
              description: "Easy-to-understand introduction to biology for complete beginners.",
              source: "Wiley",
              rating: 4.5,
              credibility: 78
            }
          ]
        },
        metadata: {
          totalResults: 15,
          processingTime: "0.8s",
          searchDepth: 50
        }
      });
    }, 800);
  });
}


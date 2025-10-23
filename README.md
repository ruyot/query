# Query

**Smarter Search Results for Google**

A Chrome extension that transforms your Google search experience by organizing results into meaningful categories and ranking them by credibility and relevance.

Built for the **Elastic x Google Cloud Hackathon**.

## Problem

Current Google search results are cluttered with:
- Ads and sponsored content at the top
- Irrelevant results mixed with quality sources
- No clear categorization of content types
- Valuable academic papers and journals buried pages deep

## Solution

Query automatically:
1. **Detects** when you search on Google
2. **Analyzes** the search results using AI
3. **Categorizes** results into logical groups:
   - Academic & Research (journals, papers, studies)
   - Video Content (tutorials, lectures)
   - Online Courses (structured learning)
   - Websites & Blogs (articles, guides)
   - Books & Textbooks
4. **Ranks** by credibility and relevance
5. **Displays** in a beautiful, organized interface

## Features

- **Automatic Detection**: Works seamlessly with your Google searches
- **Smart Categorization**: Results organized by content type
- **Credibility Scores**: See how trustworthy each source is
- **One-Click Access**: Click any result to open the original source
- **Beautiful UI**: Modern, responsive design with smooth animations
- **Fast Loading**: Results appear in 2-3 seconds
- **No Setup Required**: Works right out of the box

## Installation

### For Development

1. **Clone or download this repository**
   ```bash
   cd /path/to/Query
   ```

2. **Open Chrome and navigate to:**
   ```
   chrome://extensions/
   ```

3. **Enable "Developer mode"** (toggle in top-right corner)

4. **Click "Load unpacked"**

5. **Select the Query folder**

6. **Done!** The extension is now installed

### Verify Installation

- You should see the Query icon in your Chrome toolbar
- Click it to see the popup with extension info

## How to Use

### Method 1: Automatic (Recommended)

1. Go to Google.com
2. Search for anything (e.g., "teach me biology")
3. Query automatically opens a new tab with organized results
4. Browse by category and click any result to visit the source

### Method 2: Manual Trigger

1. Search on Google normally
2. Look for the **"Get Better Results"** button (bottom-right of page)
3. Click it to open Query's organized results

### Method 3: Extension Icon

1. Click the Query icon in your toolbar
2. Click "Try a Search on Google"
3. It will demonstrate with an example search

## Project Structure

```
Query/
├── manifest.json           # Extension configuration
├── content.js              # Detects Google searches
├── background.js           # Handles API communication
├── popup.html              # Extension popup UI
├── results.html            # Main results page
├── styles/
│   └── results.css         # Styling for results page
├── scripts/
│   ├── popup.js            # Popup functionality
│   └── results.js          # Results page logic
└── icons/                  # Extension icons
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## Backend Integration

Currently, the extension uses **mock data** for demonstration purposes. To connect your own backend:

1. **Edit `background.js`:**
   ```javascript
   const API_ENDPOINT = 'https://your-api-endpoint.com/api/search';
   ```

2. **Your API should:**
   - Accept POST requests with `{ query: "search term" }`
   - Return results in this format:
     ```json
     {
       "query": "search term",
       "categories": {
         "academic": [...],
         "videos": [...],
         "courses": [...],
         "websites": [...],
         "books": [...]
       },
       "metadata": {
         "totalResults": 15,
         "processingTime": "0.8s",
         "searchDepth": 50
       }
     }
     ```

3. **Each result should include:**
   ```json
   {
     "title": "Result Title",
     "url": "https://...",
     "description": "Brief description",
     "source": "Source name",
     "credibility": 95
   }
   ```

## Customization

### Colors
Edit `styles/results.css` to change the color scheme:
```css
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --academic-color: #667eea;
  --videos-color: #f5576c;
  /* ... more colors */
}
```

### Categories
Add or modify categories in:
- `results.html` (HTML structure)
- `scripts/results.js` (JavaScript logic)
- `styles/results.css` (styling)

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Extension API**: Chrome Manifest V3
- **Backend** (to be integrated):
  - Elastic Search (for ranking/indexing)
  - Google Cloud (hosting/compute)
  - Web scraping (for fetching results)
  - ML model (for credibility scoring)

## Future Enhancements

- [ ] Integrate with real backend API
- [ ] Add filters (date range, content type toggles)
- [ ] Implement save/bookmark functionality
- [ ] Add AI-powered summaries for each result
- [ ] Support for more search engines (Bing, DuckDuckGo)
- [ ] User preferences and customization
- [ ] Dark mode toggle
- [ ] Browser sync across devices
- [ ] Firefox and Edge support

## Notes

### Google Search Scraping
- Be mindful of Google's Terms of Service
- Consider using Google Custom Search API as an alternative
- Implement rate limiting to avoid being blocked

### Performance
- Current mock data loads in ~800ms
- Real backend should target < 3 seconds
- Consider caching frequently searched terms

### Privacy
- All searches are processed through your backend
- No data is stored by the extension itself
- Consider adding privacy policy for production use

## Contributing

This project was created for a hackathon. Ideas for improvement:

1. **Backend Integration**: Help connect to Elastic/GCP backend
2. **ML Model**: Improve credibility scoring algorithm
3. **UI/UX**: Suggest design improvements
4. **Features**: Add filters, bookmarks, summaries
5. **Testing**: Write tests for extension components

## License

This project is open source and available for educational purposes.

## Team

Created for the Elastic x Google Cloud Hackathon.

---

**Happy Searching!**

If you encounter any issues, check the Chrome Developer Console (F12) for error messages.


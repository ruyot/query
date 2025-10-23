# Query - Quick Start Guide 🚀

Get up and running with Query in 5 minutes!

## 📦 What You're Building

A Chrome extension that makes Google search results **better** by organizing them into categories like Academic Papers, Videos, Courses, Websites, and Books - all ranked by credibility.

## ⚡ 3-Step Installation

1. **Open Chrome Extensions**
   - Type `chrome://extensions/` in your address bar
   - Enable "Developer mode" (toggle in top-right)

2. **Load Query**
   - Click "Load unpacked"
   - Select the `Query` folder
   - Done! ✅

3. **Test It**
   - Go to Google.com
   - Search "teach me biology"
   - Watch Query open a new tab with organized results!

## 🎯 What Happens Next?

### Immediate (Works Now)
- ✅ Extension detects your Google searches
- ✅ Beautiful results page opens automatically
- ✅ Results categorized by type (Academic, Videos, etc.)
- ✅ Credibility scores shown for each result
- ✅ Click any result to visit the source

### Currently Using Mock Data
The extension shows **example results** right now. This lets you:
- Test the UI/UX
- See how categorization works
- Demo to your team
- Present at the hackathon

### To Connect Your Backend

**Edit `background.js` (line ~42):**

```javascript
// Change this:
const API_ENDPOINT = 'https://your-api-endpoint.com/api/search';

// To your actual endpoint:
const API_ENDPOINT = 'https://your-gcp-project.run.app/api/search';
```

**Then uncomment the real API code (lines ~48-59)** and comment out the mock data.

See `API_SPEC.md` for the exact API format your backend needs to return.

## 🏗️ Backend To-Do

Your backend team needs to build an API that:

1. **Accepts** a search query
2. **Scrapes** Google search results (or uses Google Custom Search API)
3. **Classifies** results into categories using ML
4. **Scores** each result for credibility (use Elastic here!)
5. **Ranks** results within each category
6. **Returns** JSON in the format specified in `API_SPEC.md`

**Tech Stack Ideas:**
- Google Cloud Run (hosting)
- Elasticsearch (search & ranking)
- Puppeteer (scraping)
- Python/Node.js (backend)

## 🎨 Customization

### Change Colors
Edit `styles/results.css`:
```css
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --academic-color: #667eea;
  /* Change these to your brand colors! */
}
```

### Add More Categories
1. Add HTML in `results.html` (copy existing category section)
2. Add display logic in `scripts/results.js`
3. Update backend to return the new category

### Modify Auto-Open Behavior
In `background.js` (line ~27), comment this out to disable auto-opening:
```javascript
// openQueryTab(message.query); // Comment this line
```

Now it only opens when users click the "Get Better Results" button.

## 🐛 Troubleshooting

**Button doesn't appear on Google?**
- Refresh the page
- Check `chrome://extensions/` - is Query enabled?
- Open DevTools (F12) and check Console

**Results page stuck loading?**
- Open DevTools (F12) on the results page
- Check Console for errors
- Click "Retry" button

**Extension won't load?**
- Make sure all files are present (see file structure below)
- Check `chrome://extensions/` for error messages
- Try reloading the extension

## 📁 File Structure

```
Query/
├── manifest.json          # Extension config
├── content.js             # Detects Google searches
├── background.js          # API communication
├── popup.html/js          # Extension icon popup
├── results.html/js        # Results page
├── styles/results.css     # Styling
└── icons/                 # Extension icons
```

## 💡 Pro Tips

1. **Test with Different Queries**
   - "learn machine learning"
   - "best programming books"
   - "how to start a startup"

2. **Demo Mode**
   - Click the extension icon → "Try a Search"
   - Shows the example search for demonstrations

3. **Development**
   - Keep DevTools open (F12)
   - Check Console in both Google page and results page
   - Reload extension after code changes

4. **Performance**
   - Target < 3 seconds for backend response
   - Cache popular queries
   - Consider lazy-loading categories

## 🎓 Hackathon Tips

### For Your Presentation

**Show this flow:**
1. User searches on Google (show typical messy results)
2. Query opens (show loading animation)
3. Results appear organized by category
4. Highlight credibility scores
5. Click through to original source

**Talk about:**
- Problem: Information overload on Google
- Solution: AI-powered categorization & ranking
- Tech: Chrome Extension + Elastic + GCP
- Impact: Better learning outcomes, faster research

### Demo Script

```
"Let me show you Query in action...

[Open Google, search "teach me biology"]

See how regular Google results are cluttered with ads?
Academic papers are buried on page 2 or 3.

[Query opens]

Now look at Query. Results are organized into:
- Academic papers at the top
- Video tutorials
- Online courses
- And more...

Each result has a credibility score powered by Elastic.
One click takes you to the source.

Students and researchers can now find quality content instantly."
```

## 🚀 Next Steps

1. ✅ Install the extension (you just did!)
2. ⏳ Build the backend API
3. ⏳ Connect backend to extension
4. ⏳ Test with real data
5. ⏳ Polish the UI
6. ⏳ Prepare your demo
7. ⏳ Win the hackathon! 🏆

## 📚 More Documentation

- `README.md` - Full documentation
- `INSTALLATION.md` - Detailed installation guide
- `API_SPEC.md` - Backend API requirements

## 🆘 Need Help?

- Check Console (F12) for error messages
- Review the README for detailed explanations
- All code is commented - read through it!

---

**You're all set!** Start building that backend and good luck with the hackathon! 🎉


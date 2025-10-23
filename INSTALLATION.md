# Query Installation Guide

Step-by-step instructions to install and test the Query Chrome extension.

## Prerequisites

- Google Chrome browser (version 88+)
- The Query extension files (this folder)

## Installation Steps

### Step 1: Open Chrome Extensions Page

1. Open Google Chrome
2. In the address bar, type: `chrome://extensions/`
3. Press Enter

**Alternative method:**
- Click the three dots menu (⋮) in the top-right
- Go to: More Tools → Extensions

### Step 2: Enable Developer Mode

1. Look for the "Developer mode" toggle in the top-right corner
2. Click it to turn it ON (it should be blue/enabled)

### Step 3: Load the Extension

1. Click the **"Load unpacked"** button (appears after enabling Developer mode)
2. Navigate to the Query folder on your computer
3. Select the folder and click "Select" or "Open"

### Step 4: Verify Installation

You should now see:
- ✅ Query extension card in the extensions list
- ✅ The Query icon in your Chrome toolbar (top-right)
- ✅ Status: "On" with a blue toggle

**If you don't see the icon in the toolbar:**
1. Click the puzzle piece icon (Extensions) in the toolbar
2. Find "Query" in the list
3. Click the pin icon to pin it to the toolbar

## Testing the Extension

### Test 1: Extension Popup

1. Click the Query icon in your toolbar
2. You should see:
   - The Query logo and name
   - "Extension Active" status with a pulsing green dot
   - Information about how Query works
   - A "Try a Search on Google" button

### Test 2: Google Search Integration

1. Go to [google.com](https://www.google.com)
2. Search for anything, for example: **"teach me biology"**
3. Two things should happen:
   - A **"Get Better Results"** button appears (bottom-right of the page)
   - Query automatically opens a new tab with organized results

### Test 3: Manual Trigger

1. Do a Google search: "learn python programming"
2. Look for the purple "Get Better Results" button (bottom-right)
3. Click it
4. Query results should open in a new tab

### Test 4: Results Page

On the Query results page, you should see:
- ✅ Your search query at the top
- ✅ Statistics (Total Results, Processing Time, Sources Analyzed)
- ✅ Categorized sections:
  - 📚 Academic & Research
  - 🎥 Video Content
  - 📖 Online Courses
  - 🌐 Websites & Blogs
  - 📕 Books & Textbooks
- ✅ Results cards with titles, descriptions, and credibility scores
- ✅ Clicking any card opens that source in a new tab

## Troubleshooting

### Issue: Extension doesn't appear after loading

**Solution:**
1. Refresh the `chrome://extensions/` page
2. Make sure "Developer mode" is still ON
3. Check for error messages on the extension card
4. Try clicking "Reload" button (circular arrow) on the Query card

### Issue: "Get Better Results" button doesn't appear

**Solution:**
1. Make sure you're on an actual Google search results page
2. Check that the URL starts with: `https://www.google.com/search?q=`
3. Open Chrome DevTools (F12) and check Console for errors
4. Reload the Google search page

### Issue: Results page shows "Loading..." forever

**Solution:**
1. Open DevTools (F12) on the results page
2. Check Console for errors
3. The extension currently uses mock data, so this shouldn't happen
4. Try clicking the "Retry" button if it appears

### Issue: Clicks on result cards don't work

**Solution:**
1. Check if popup blockers are enabled
2. Allow popups from `chrome-extension://` in Chrome settings
3. Hold Ctrl/Cmd while clicking to force open in new tab

### Issue: Extension shows errors on load

**Common errors and solutions:**

1. **"Manifest file is missing or unreadable"**
   - Make sure `manifest.json` is in the root folder
   - Check file permissions

2. **"Could not load icon"**
   - Ensure `icons/` folder exists with icon files
   - Icons should be: icon16.png, icon48.png, icon128.png

3. **"Service worker registration failed"**
   - Make sure `background.js` exists
   - Check for syntax errors in the file

## Updating the Extension

When you make changes to the code:

1. Go to `chrome://extensions/`
2. Find the Query extension card
3. Click the reload icon (circular arrow)
4. Test your changes

**For major changes:**
1. Remove the extension (click "Remove" button)
2. Reload it using "Load unpacked"

## Uninstallation

To remove Query:

1. Go to `chrome://extensions/`
2. Find the Query extension
3. Click "Remove"
4. Confirm removal

## Development Mode

### Viewing Logs

**Extension Console:**
1. Go to `chrome://extensions/`
2. Find Query
3. Click "service worker" link (under "Inspect views")
4. Check Console tab for background script logs

**Content Script Console:**
1. Open a Google search page
2. Press F12 to open DevTools
3. Check Console for messages starting with "Query:"

**Results Page Console:**
1. Open the Query results page
2. Press F12 to open DevTools
3. Check Console for any errors

## Next Steps

### Connect Your Backend

Currently using mock data. To connect real backend:

1. Edit `background.js`
2. Find this line:
   ```javascript
   const API_ENDPOINT = 'https://your-api-endpoint.com/api/search';
   ```
3. Replace with your actual API endpoint
4. Uncomment the fetch code (remove the mock data return)
5. Reload the extension

See `API_SPEC.md` for detailed API requirements.

### Customize Appearance

Edit these files:
- `styles/results.css` - Colors, fonts, layout
- `results.html` - Structure, categories
- `popup.html` - Extension popup design

After editing, reload the extension to see changes.

## Browser Compatibility

✅ **Tested on:**
- Chrome 88+
- Chromium-based browsers (Edge, Brave, Opera)

❌ **Not compatible with:**
- Firefox (requires manifest conversion)
- Safari (requires different extension format)

## Getting Help

If you encounter issues:

1. Check the Console for error messages (F12)
2. Review the `README.md` for common issues
3. Verify all files are in the correct locations
4. Make sure you have a stable internet connection (for future backend integration)

## File Structure Checklist

Make sure your Query folder contains:

```
Query/
├── ✅ manifest.json
├── ✅ content.js
├── ✅ background.js
├── ✅ popup.html
├── ✅ results.html
├── ✅ styles/
│   └── ✅ results.css
├── ✅ scripts/
│   ├── ✅ popup.js
│   └── ✅ results.js
└── ✅ icons/
    ├── ✅ icon16.png
    ├── ✅ icon48.png
    └── ✅ icon128.png
```

Missing any files? Make sure you have the complete extension folder.

---

**Ready to start?** Follow the installation steps above and happy searching! 🚀


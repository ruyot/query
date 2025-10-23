# Query - Complete Setup Guide

Full setup instructions for the Query search extension with integrated backend.

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js (optional, for development)
- Chrome browser
- SerpAPI account (for Google search scraping)
- Elasticsearch (local or Elastic Cloud)

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Run the automated setup script
./start_server.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `backend/.env`:

```env
# Required: Get from https://serpapi.com/
SERPAPI_KEY=your_serpapi_key_here

# Required: Elasticsearch (choose one)
# Option A: Local Elasticsearch
ES_HOST=localhost
ES_PORT=9200

# Option B: Elastic Cloud
ES_CLOUD_ID=your_cloud_id_here
ES_API_KEY=your_elastic_api_key_here

# Optional: GCP Model Endpoint (add when available)
GCP_MODEL_ENDPOINT=https://your-vertex-endpoint.run.app/predict
GCP_PROJECT_ID=your-gcp-project
```

### 3. Start the API Server

```bash
cd backend
python api_server.py
```

You should see:
```
✓ Elasticsearch connected
Starting Query API Server...
Server will be available at: http://localhost:5000
```

### 4. Install Chrome Extension

1. Open Chrome: `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `/Users/tahmeed_t/Query` folder (the root, not backend)
5. The extension should now be loaded!

### 5. Test It!

1. Go to Google.com
2. Search for anything: "teach me biology"
3. Query will automatically open a new tab with organized results!

Or click the "Get Better Results" button on Google's page.

## 🎯 How It Works

```
Google Search → Chrome Extension → API Server → SerpAPI + Elasticsearch → Ranked Results
                      ↓                            ↓
                 results.html              scoring.py + ML model
```

### Data Flow:

1. **User searches on Google** → Content script detects it
2. **Extension calls API** → `POST /api/search` with query
3. **API fetches results** → SerpAPI gets Google results
4. **Results are categorized** → Academic, Videos, Courses, etc.
5. **Results are scored** → Relevance + recency + ML model (when added)
6. **Stored in Elasticsearch** → For future training and analysis
7. **Returned to extension** → Displayed in beautiful UI

## 📡 API Endpoints

### `POST /api/search`
Main search endpoint

**Request:**
```json
{
  "query": "teach me biology"
}
```

**Response:**
```json
{
  "query": "teach me biology",
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

### `GET /health`
Health check

### `POST /api/rank`
Rank results with GCP model (to be integrated)

## 🧠 Adding the GCP Model

When you get the Vertex AI endpoint:

1. Edit `backend/.env`:
```env
GCP_MODEL_ENDPOINT=https://your-endpoint-xxxxxxxx.run.app/predict
GCP_PROJECT_ID=your-project-id
```

2. The API will automatically use it for ranking!

The code in `api_server.py` is already structured to integrate the model:

```python
@app.route('/api/rank', methods=['POST'])
def rank_with_model():
    # TODO: This will call your GCP Vertex AI endpoint
    # model_endpoint = os.getenv('GCP_MODEL_ENDPOINT')
    # ranked_results = call_gcp_model(data['results'], model_endpoint)
    pass
```

## 🐛 Troubleshooting

### Extension Issues

**"Failed to load extension"**
- Make sure you're loading the root `Query/` folder, not `Query/backend/`
- Check `manifest.json` exists in the root

**"API request failed"**
- Is the API server running? Check `http://localhost:5000/health`
- Reload the extension in `chrome://extensions/`

**Results not appearing**
- Open DevTools (F12) on the results page
- Check Console for error messages
- Verify API server logs

### Backend Issues

**"Module not found"**
```bash
cd backend
pip install -r requirements.txt
```

**"SerpAPI error"**
- Check your SERPAPI_KEY in `.env`
- Verify you have API credits: https://serpapi.com/dashboard

**"Elasticsearch connection failed"**
- Local: Ensure Elasticsearch is running on `localhost:9200`
- Cloud: Verify ES_CLOUD_ID and ES_API_KEY in `.env`
- Extension will still work, just won't store results

**"CORS error"**
- Make sure `flask-cors` is installed
- API server should show CORS is enabled in logs

## 📊 Elasticsearch Setup

### Option A: Local Elasticsearch

```bash
# Download and start Elasticsearch
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-darwin-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-darwin-x86_64.tar.gz
cd elasticsearch-8.11.0
./bin/elasticsearch
```

### Option B: Elastic Cloud (Recommended)

1. Go to https://cloud.elastic.co/
2. Create a deployment
3. Get your Cloud ID and API key
4. Add to `backend/.env`

## 🔧 Development

### Run with auto-reload:
```bash
cd backend
export FLASK_DEBUG=1
python api_server.py
```

### Check Elasticsearch data:
```bash
cd backend
python view_results.py
```

### Prepare ML training data:
```bash
cd backend
python prepare_ranking_data.py
```

### Train ranking model:
```bash
cd backend
python example_ml_training.py
```

## 📦 Deployment

### Deploy Backend to Cloud Run:

```bash
cd backend
gcloud run deploy query-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

Then update `background.js`:
```javascript
const API_ENDPOINT = 'https://query-api-xxxxxxxx.run.app/api/search';
```

## 🎨 Customization

### Change Colors:
Edit `styles/results.css` - see the `:root` variables

### Add More Categories:
1. Update `api_server.py` categorization logic
2. Add section in `results.html`
3. Update `scripts/results.js` to display

### Modify Scoring:
Edit `backend/src/scoring.py` - adjust weights and formulas

## 📝 Next Steps

- [ ] Add your SerpAPI key
- [ ] Set up Elasticsearch
- [ ] Test the complete flow
- [ ] Add GCP model endpoint
- [ ] Deploy to production
- [ ] Collect user feedback

## 🆘 Support

- Check logs in `backend/` folder
- Chrome DevTools Console (F12)
- GitHub Issues: [Your Repo]

---

**You're all set!** Search on Google and watch Query work its magic! ✨


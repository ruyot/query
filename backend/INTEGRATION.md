# Backend Integration with Chrome Extension

This document explains how the backend connects to the Chrome extension.

## Architecture

```
┌─────────────────────┐
│  Chrome Extension   │
│  (Frontend)         │
│  - content.js       │
│  - background.js    │
│  - results.html     │
└──────────┬──────────┘
           │
           │ HTTP POST /api/search
           │
┌──────────▼──────────┐
│   API Server        │
│   api_server.py     │
│   (Flask)           │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
┌────▼────┐  ┌──▼──────────┐
│ SerpAPI │  │ Elasticsearch│
│ Google  │  │   Storage    │
└─────────┘  └──────────────┘
```

## Key Components

### 1. API Server (`api_server.py`)
- Flask web server
- Handles `/api/search` POST requests
- Integrates with SerpAPI for Google results
- Uses Elasticsearch for storage
- Returns categorized, ranked results

### 2. Chrome Extension Backend (`background.js`)
- Service worker that runs in background
- Calls API when user searches
- Handles response and passes to results page
- Falls back to mock data if API unavailable

### 3. Search Client (`src/google_client/search_client.py`)
- Interfaces with SerpAPI
- Fetches Google search results
- Handles pagination and rate limiting

### 4. Scoring System (`src/scoring.py`)
- Calculates relevance scores
- Factors: rank, recency, engagement
- Prepares for ML model integration

### 5. Elasticsearch Client (`src/elasticsearch_client/es_client.py`)
- Stores search results
- Enables historical analysis
- Powers ML training data

## API Contract

### Request Format
```json
POST http://localhost:5000/api/search
Content-Type: application/json

{
  "query": "teach me biology"
}
```

### Response Format
```json
{
  "query": "teach me biology",
  "categories": {
    "academic": [
      {
        "title": "Understanding Biology",
        "url": "https://...",
        "description": "...",
        "source": "Nature Journal",
        "credibility": 95,
        "rank": 1,
        "relevance_score": 0.95,
        "timestamp": "2024-10-23"
      }
    ],
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

## Data Flow

1. **User searches on Google**
   - `content.js` detects search query
   - Sends message to `background.js`

2. **Background script makes API call**
   ```javascript
   fetch('http://localhost:5000/api/search', {
     method: 'POST',
     body: JSON.stringify({ query })
   })
   ```

3. **API server processes request**
   - Fetches from SerpAPI
   - Categorizes results
   - Scores each result
   - Stores in Elasticsearch

4. **Results returned to extension**
   - `background.js` receives response
   - Passes to `results.html`
   - `results.js` displays categorized results

## Adding GCP Model

To integrate Vertex AI ranking model:

### 1. Update `.env`:
```env
GCP_MODEL_ENDPOINT=https://your-endpoint.run.app/predict
GCP_PROJECT_ID=your-project-id
```

### 2. Modify `api_server.py`:

```python
def score_and_rank_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Score using GCP Vertex AI model"""
    
    # Get model endpoint from environment
    model_endpoint = os.getenv('GCP_MODEL_ENDPOINT')
    
    if model_endpoint:
        # Call Vertex AI model
        response = requests.post(
            model_endpoint,
            json={'instances': results},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.ok:
            predictions = response.json()['predictions']
            # Merge predictions with results
            for i, result in enumerate(results):
                result['credibility'] = int(predictions[i]['score'] * 100)
                result['model_prediction'] = predictions[i]
            
            # Sort by model score
            results.sort(key=lambda x: predictions[x['rank']-1]['score'], reverse=True)
            return results
    
    # Fallback to rule-based scoring
    return current_scoring_method(results)
```

### 3. Model Input Format:
```json
{
  "instances": [
    {
      "title": "...",
      "description": "...",
      "url": "...",
      "source": "...",
      "rank": 1,
      "timestamp": "2024-10-23"
    }
  ]
}
```

### 4. Expected Model Output:
```json
{
  "predictions": [
    {
      "score": 0.95,
      "confidence": 0.87
    }
  ]
}
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SERPAPI_KEY` | SerpAPI API key | Yes |
| `ES_HOST` | Elasticsearch host | For local ES |
| `ES_PORT` | Elasticsearch port | For local ES |
| `ES_CLOUD_ID` | Elastic Cloud ID | For cloud ES |
| `ES_API_KEY` | Elastic Cloud API key | For cloud ES |
| `GCP_MODEL_ENDPOINT` | Vertex AI endpoint | Optional |
| `GCP_PROJECT_ID` | GCP project ID | Optional |
| `API_PORT` | API server port | Optional (default: 5000) |

### Chrome Extension Configuration

In `background.js`, update the API endpoint:

```javascript
// For local development
const API_ENDPOINT = 'http://localhost:5000/api/search';

// For production (Cloud Run)
const API_ENDPOINT = 'https://query-api-xxx.run.app/api/search';
```

## Security Considerations

### Development (localhost)
- CORS enabled for all origins
- No authentication required
- Fine for local testing

### Production
- [ ] Add API key authentication
- [ ] Restrict CORS to extension ID
- [ ] Use HTTPS only
- [ ] Rate limiting per user
- [ ] Input sanitization

Example production security:

```python
# api_server.py
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_SECRET_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/search', methods=['POST'])
@require_api_key
def search():
    # ...
```

## Testing

### Test API Server:
```bash
# Health check
curl http://localhost:5000/health

# Search request
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test search"}'
```

### Test Extension:
1. Load extension in Chrome
2. Open DevTools (F12)
3. Go to Google and search
4. Check Console for API calls
5. Verify results display correctly

## Troubleshooting

### "Cannot connect to API"
- Ensure server is running: `python api_server.py`
- Check firewall allows port 5000
- Verify URL in `background.js` matches server

### "CORS error"
- Check `flask-cors` is installed
- Verify CORS is enabled in `api_server.py`
- Reload extension after server restart

### "Empty results"
- Check SerpAPI key is valid
- Verify API has credits
- Check server logs for errors

### "Elasticsearch not available"
- Extension will still work with mock data
- Results won't be stored for training
- Check ES connection in server logs

## Performance

### API Response Time
- Target: < 2 seconds
- Current: ~0.8s (with caching)
- Bottleneck: SerpAPI fetch

### Optimization Tips
- Cache frequent queries (Redis)
- Parallel API calls
- Lazy load categories
- Preload common searches

## Monitoring

Add logging to track:
- API request/response times
- Error rates
- Popular queries
- Category distributions
- Model prediction accuracy

```python
import logging
import time

@app.route('/api/search', methods=['POST'])
def search():
    start_time = time.time()
    
    try:
        # ... process request ...
        
        duration = time.time() - start_time
        logger.info(f"Search completed in {duration:.2f}s")
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
```

## Next Steps

- [ ] Start API server
- [ ] Test basic search flow
- [ ] Add GCP model endpoint
- [ ] Test model integration
- [ ] Deploy to Cloud Run
- [ ] Update extension with production URL
- [ ] Monitor and optimize

---

**Need help?** Check `SETUP.md` for full instructions!


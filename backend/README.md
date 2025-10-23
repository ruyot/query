# Elasticsearch Search Results Pipeline with ML Ranking

A complete backend pipeline that integrates SerpAPI (Google search results) with Elasticsearch for structured search result indexing, plus a production-ready data preparation system for training machine learning ranking models. Supports both local development and Elastic Cloud serverless deployment.

## 📋 Table of Contents

- [Features](#features)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Setup](#setup)
- [Usage](#usage)
  - [Search Results Collection](#search-results-collection)
  - [Ranking Data Preparation](#ranking-data-preparation-new)
  - [Model Training](#model-training)
- [Complete Workflow](#complete-workflow)
- [Architecture](#architecture)
- [Data Structure](#data-structure)
- [Scoring System](#scoring-system)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Extending the System](#extending-the-system)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

---

## Features

### Search Pipeline
- ✅ Fetches search results from Google via SerpAPI with pagination
- ✅ Categorizes results into videos and articles based on metadata
- ✅ Structures results into clean JSON documents
- ✅ Bulk indexes results into Elasticsearch (local or cloud)
- ✅ Command-line interface for easy usage
- ✅ **Cloud-ready**: Supports Elastic Cloud serverless deployment

### Ranking Model Data Preparation (NEW)
- ✅ **Intelligent Relevance Scoring**: Compute scores using rank and recency heuristics
- ✅ **Configurable Scoring System**: Adjustable weights and decay periods
- ✅ **Elasticsearch Integration**: Updates documents with computed scores
- ✅ **ML-Ready Export**: JSONL format for Vertex AI and other ML frameworks
- ✅ **Production-Ready**: Comprehensive error handling and progress reporting
- ✅ **Fully Tested**: Complete test suite with 7/7 passing tests

---

## Quick Start (5 Minutes)

### 1. Collect Search Results (1 minute)
```bash
# Install dependencies
pip install -r requirements.txt

# Configure your API keys in .env (see Setup section)
# Then collect search results (scores are automatically calculated!)
python main.py "machine learning tutorials" --pages 5
```

**✨ Automatic Scoring**: When you run `main.py`, relevance scores are automatically calculated and added to all documents in Elasticsearch!

### 2. Export Training Data (1 minute - optional)
```bash
# Export scored documents to JSONL for ML training (optional)
python prepare_ranking_data.py
```

### 3. Train a Model (3 minutes - optional)
```bash
# Install ML dependencies
pip install pandas scikit-learn numpy

# Train ranking models
python example_ml_training.py
```

**Done!** You now have:
- ✅ Search results in Elasticsearch **with relevance scores automatically added**
- ✅ Training data exported to `output/ranking_training_data.jsonl` (optional)
- ✅ A trained ranking model (optional)

**✨ The scores are now in Elasticsearch!** Check any document and you'll see:
- `base_rank_score`
- `recency_score`
- `relevance_score`
- `user_engagement_score`

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp env.example .env
```

Edit `.env`:
```env
# Required: SerpAPI Key
SERPAPI_KEY=your_actual_serpapi_key

# Elasticsearch Configuration
# For local development:
ELASTIC_URL=http://localhost:9200

# For cloud deployment:
ELASTIC_URL=https://your-deployment-id.region.aws.found.io:9243
ELASTIC_API_KEY=your_api_key_here
```

### 3. Get API Credentials

**SerpAPI Key** (required):
1. Go to [SerpAPI](https://serpapi.com/)
2. Sign up for a free account (250 searches/month free)
3. Get your API key from the dashboard

**Elasticsearch** (choose one):
- **Local**: Install Elasticsearch locally or use Docker
- **Cloud**: Create account at [Elastic Cloud](https://cloud.elastic.co/) (14-day trial)

For detailed cloud setup, see [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)

---

## Usage

### Search Results Collection

#### Basic Usage

```bash
# Collect search results for a query
python main.py "machine learning tutorials"
```

#### Advanced Usage

```bash
# Fetch more pages (up to 10 pages)
python main.py "biology for beginners" --pages 10

# Validate configuration only
python main.py --validate-config

# Test cloud connection
python main.py --validate-cloud
```

#### Example Output

```
Processing query: 'machine learning tutorials'
==================================================
Step 1: Fetching results from Google via SerpAPI...
Fetching page 1 (results 1-10)...
Fetching page 2 (results 11-20)...
Successfully fetched 50 total results

Step 2: Categorizing results...
Found 5 videos and 5 articles

Step 3: Structuring results into JSON documents...
Created 10 structured documents

Step 4: Computing relevance scores...
  ✓ Computed scores for 10 documents

Step 5: Indexing documents to Elasticsearch...
Successfully indexed 10 documents to Elasticsearch

==================================================
Pipeline completed successfully!
Indexed 10 documents with relevance scores:
   - 5 videos
   - 5 articles

Score fields added to each document:
   • base_rank_score
   • recency_score
   • relevance_score
   • user_engagement_score
```

**✨ Note**: Relevance scores are **automatically calculated and added** when you run `main.py`. No separate step needed!

---

### Ranking Data Preparation (NEW)

**✨ Automatic Scoring**: Relevance scores are now **automatically calculated when you run `main.py`**! Each document in Elasticsearch will have:
- `base_rank_score = 1 / rank`
- `recency_score = exp(-(current_date - timestamp) / 30_days)`
- `relevance_score = 0.6 × base_rank_score + 0.4 × recency_score`
- `user_engagement_score = 0.5` (placeholder)

#### Export Training Data (Optional)

If you want to export your scored documents to JSONL format for ML training:

```bash
# Export to JSONL file for Vertex AI or other ML frameworks
python prepare_ranking_data.py
```

This will:
- ✅ Fetch all documents from Elasticsearch (already with scores!)
- ✅ Export to `output/ranking_training_data.jsonl` for ML training
- ✅ Optionally recalculate scores with different parameters

**Note**: Output files are saved in the `output/` folder to keep your codebase organized.

#### Expected Output

```
============================================================
Starting Ranking Model Data Preparation Pipeline
============================================================

✓ Elasticsearch connection successful

Fetching documents from index: search_results
Fetched 150 documents

Processing 150 documents...
  Processed 100/150 documents
Successfully processed 150 documents

Updating 150 documents in Elasticsearch...
  Updated 100/150 documents
Successfully updated 150 documents

Saving to ranking_training_data.jsonl...
Successfully saved data to ranking_training_data.jsonl
File size: 245.67 KB

============================================================
Data Preparation Pipeline Completed Successfully!
============================================================

Summary:
  - Documents fetched: 150
  - Documents processed: 150
  - Documents updated in ES: 150
  - Output file: ranking_training_data.jsonl

Sample scores from first document:
  - Rank: 1
  - Base rank score: 1.0
  - Recency score: 0.998765
  - Relevance score: 0.799506
  - User engagement score: 0.5
```

#### Demo and Testing

```bash
# See interactive scoring demonstrations
python demo_scoring.py

# Run unit tests (7 tests)
python test_scoring.py
```

#### Custom Configuration

Edit `prepare_ranking_data.py` to adjust scoring parameters:

```python
# For news/time-sensitive content
pipeline = RankingDataPreparation(
    output_file="output/news_ranking.jsonl",
    base_weight=0.3,        # Less emphasis on rank
    recency_weight=0.7,     # More emphasis on freshness
    decay_days=7            # Fast decay (1 week)
)

# For evergreen/reference content
pipeline = RankingDataPreparation(
    output_file="output/reference_ranking.jsonl",
    base_weight=0.8,        # More emphasis on rank
    recency_weight=0.2,     # Less emphasis on freshness
    decay_days=90           # Slow decay (3 months)
)

# Balanced (default)
pipeline = RankingDataPreparation(
    output_file="output/ranking_training_data.jsonl",
    base_weight=0.6,
    recency_weight=0.4,
    decay_days=30
)
```

---

### Model Training

Use the prepared data to train ML ranking models.

#### Prerequisites

```bash
pip install pandas scikit-learn numpy
```

#### Run Example Training

```bash
python example_ml_training.py
```

This trains multiple models (Linear Regression, Random Forest, Gradient Boosting) and compares their performance.

#### Integration with ML Frameworks

**Vertex AI:**
```python
from google.cloud import aiplatform

aiplatform.init(project="your-project", location="us-central1")

dataset = aiplatform.TabularDataset.create(
    display_name="search_ranking_dataset",
    gcs_source="gs://your-bucket/ranking_training_data.jsonl"
)

model = aiplatform.AutoMLTabularTrainingJob(
    display_name="search_ranking_model",
    optimization_objective="minimize-rmse"
)

model.run(
    dataset=dataset,
    target_column="relevance_score",
    training_fraction_split=0.8,
    validation_fraction_split=0.1,
    test_fraction_split=0.1
)
```

**Scikit-learn:**
```python
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor

# Load JSONL data
data = []
with open('ranking_training_data.jsonl', 'r') as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)

# Prepare features
X = df[['rank', 'recency_score']]
y = df['relevance_score']

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = GradientBoostingRegressor()
model.fit(X_train, y_train)

print(f"Model score: {model.score(X_test, y_test)}")
```

**TensorFlow:**
```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
# ... training code
```

---

## Complete Workflow

### End-to-End Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: Data Collection                                     │
│  python main.py "your query" --pages 5                       │
│                                                              │
│  ✓ Fetches search results from Google                       │
│  ✓ Indexes to Elasticsearch                                 │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 2: Data Preparation & Scoring                         │
│  python prepare_ranking_data.py                             │
│                                                              │
│  ✓ Computes relevance scores                                │
│  ✓ Updates Elasticsearch                                    │
│  ✓ Exports to JSONL                                         │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 3: Model Training                                     │
│  python example_ml_training.py                              │
│                                                              │
│  ✓ Trains multiple models                                   │
│  ✓ Evaluates performance                                    │
│  ✓ Selects best model                                       │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 4: Deployment                                         │
│                                                              │
│  ✓ Deploy to production                                     │
│  ✓ Real-time ranking predictions                            │
│  ✓ Monitor and iterate                                      │
└──────────────────────────────────────────────────────────────┘
```

### Continuous Improvement Cycle

```
1. Collect more data → python main.py "new queries"
2. Update scores → python prepare_ranking_data.py
3. Retrain model → python example_ml_training.py
4. Evaluate → Compare RMSE/R²
5. Adjust parameters → Tune weights/features
6. Deploy → Replace production model
```

---

## Architecture

### Project Structure

```
src/
├── config.py                 # Environment configuration
├── run_query.py             # CLI entry point
├── scoring.py               # Relevance scoring module (NEW)
├── google_client/
│   └── search_client.py     # SerpAPI client for Google search results
├── parsers/
│   └── result_parser.py     # Result categorization and structuring
└── elasticsearch_client/
    └── es_client.py         # Elasticsearch indexing client

Scripts:
├── main.py                  # Main pipeline entry point
├── prepare_ranking_data.py  # Ranking model data preparation (NEW)
├── demo_scoring.py          # Scoring system demo (NEW)
├── test_scoring.py          # Scoring system tests (NEW)
└── example_ml_training.py   # ML training example (NEW)

Documentation:
├── README.md                # This file (comprehensive guide)
├── CLOUD_DEPLOYMENT.md      # Cloud deployment guide
└── requirements.txt         # Python dependencies
```

### Component Overview

**Search Pipeline:**
1. `search_client.py` - Fetches results from SerpAPI
2. `result_parser.py` - Categorizes and structures results
3. `es_client.py` - Indexes to Elasticsearch

**Ranking Pipeline:**
1. `scoring.py` - Computes relevance scores
2. `prepare_ranking_data.py` - Orchestrates data preparation
3. `example_ml_training.py` - Trains ML models

---

## Data Structure

### Basic Document Structure

Each indexed document contains:

```json
{
  "query": "machine learning tutorials",
  "category": "video",
  "title": "Machine Learning Tutorial for Beginners",
  "url": "https://example.com/ml-tutorial",
  "description": "A comprehensive guide to machine learning...",
  "source": "google",
  "rank": 1,
  "thumbnailUrl": "https://example.com/thumb.jpg",
  "author": "Example Author",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### With Ranking Scores (After `prepare_ranking_data.py`)

```json
{
  "query": "machine learning tutorials",
  "category": "video",
  "title": "Machine Learning Tutorial for Beginners",
  "url": "https://example.com/ml-tutorial",
  "description": "A comprehensive guide to machine learning...",
  "source": "google",
  "rank": 1,
  "thumbnailUrl": "https://example.com/thumb.jpg",
  "author": "Example Author",
  "timestamp": "2024-01-15T10:30:00Z",
  "base_rank_score": 1.0,
  "recency_score": 0.998765,
  "relevance_score": 0.799506,
  "user_engagement_score": 0.5
}
```

**Note**: The scoring fields are added when you run the ranking data preparation pipeline.

---

## Scoring System

### Scoring Formula

For each document, the system calculates:

```python
# 1. Base Rank Score (inverse rank)
base_rank_score = 1 / rank

# 2. Recency Score (exponential decay)
days_old = (current_date - document_timestamp).days
recency_score = exp(-days_old / decay_days)

# 3. Final Relevance Score (weighted combination)
relevance_score = base_weight * base_rank_score + recency_weight * recency_score

# 4. User Engagement Score (placeholder)
user_engagement_score = 0.5  # Replace with real data
```

### Score Interpretation

| Score Range | Interpretation | Typical Documents |
|-------------|----------------|-------------------|
| 0.8 - 1.0   | Excellent      | Top-ranked, fresh results |
| 0.6 - 0.8   | Good           | High rank OR very recent |
| 0.4 - 0.6   | Moderate       | Mid-rank, moderate age |
| 0.2 - 0.4   | Fair           | Lower rank OR older |
| 0.0 - 0.2   | Poor           | Low rank AND old |

### Example Scenarios

| Rank | Days Old | Base Score | Recency Score | Final Score | Interpretation |
|------|----------|------------|---------------|-------------|----------------|
| 1    | 0        | 1.000      | 1.000         | **1.000** ✨ | Perfect: Top rank, fresh |
| 1    | 30       | 1.000      | 0.368         | **0.747** ✅ | Excellent: Top rank, month old |
| 5    | 0        | 0.200      | 1.000         | **0.520** 🔄 | Good: Lower rank, fresh |
| 10   | 60       | 0.100      | 0.135         | **0.114** ⚠️ | Poor: Low rank, old |

### Weight Configuration Examples

**News/Time-Sensitive Content:**
```python
base_weight=0.3      # Less emphasis on rank
recency_weight=0.7   # More emphasis on freshness
decay_days=7         # Fast decay (1 week)
```

**Evergreen/Reference Content:**
```python
base_weight=0.8      # More emphasis on rank
recency_weight=0.2   # Less emphasis on freshness
decay_days=90        # Slow decay (3 months)
```

**Balanced (Default):**
```python
base_weight=0.6
recency_weight=0.4
decay_days=30
```

---

## Configuration

### Environment Variables

#### Required Variables
- `SERPAPI_KEY`: Your SerpAPI key (required for all deployments)

#### Local Deployment
- `ELASTIC_URL`: Elasticsearch URL (default: http://localhost:9200)

#### Cloud Deployment
- `ELASTIC_URL`: Cloud endpoint URL
- `ELASTIC_API_KEY`: API key for authentication

#### Optional Variables
- `ELASTIC_INDEX`: Index name (default: search_results)

### Code Configuration

**Search Pipeline** (`src/config.py`):
```python
RESULTS_PER_PAGE = 10      # Results per page
MAX_PAGES = 5               # Maximum pages to fetch
```

**Ranking Pipeline** (`prepare_ranking_data.py`):
```python
pipeline = RankingDataPreparation(
    output_file="output/ranking_training_data.jsonl",
    base_weight=0.6,        # Weight for rank score
    recency_weight=0.4,     # Weight for recency score
    decay_days=30           # Recency decay period
)
```

---

## Deployment Options

### Option A: Local Development

**1. Start Elasticsearch locally:**
```bash
# Using Docker
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0
```

**2. Configure `.env`:**
```env
SERPAPI_KEY=your_actual_serpapi_key
ELASTIC_URL=http://localhost:9200
```

**3. Run the pipeline:**
```bash
python main.py "your query"
python prepare_ranking_data.py
```

---

### Option B: Elastic Cloud (Recommended for Production)

**1. Create Elastic Cloud Account:**
- Go to [Elastic Cloud](https://cloud.elastic.co/)
- Sign up for free (14-day trial)
- Create a new deployment
- Choose "Serverless" for optimal cost

**2. Get Credentials:**
- **Elasticsearch URL**: From deployment overview
- **API Key**: Generate from Security section

**3. Configure `.env`:**
```env
SERPAPI_KEY=your_actual_serpapi_key
ELASTIC_URL=https://your-deployment-id.region.aws.found.io:9243
ELASTIC_API_KEY=your_api_key_here
```

**4. Test Connection:**
```bash
python main.py --validate-cloud
```

**5. Run Production Pipeline:**
```bash
python main.py "your queries" --pages 10
python prepare_ranking_data.py
```

For detailed cloud deployment instructions, see [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)

---

## Extending the System

### Adding New Scoring Factors

1. **Extend `RelevanceScorer` class** (`src/scoring.py`):

```python
def calculate_engagement_score(self, clicks: int, impressions: int) -> float:
    """Calculate engagement from real user data."""
    if impressions == 0:
        return 0.0
    return clicks / impressions

def calculate_authority_score(self, domain: str) -> float:
    """Calculate domain authority score."""
    # Your logic here
    authority_map = {
        'wikipedia.org': 1.0,
        'edu': 0.9,
        # ... more domains
    }
    return authority_map.get(domain, 0.5)
```

2. **Update `enrich_document` method**:

```python
def enrich_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
    enriched_doc = document.copy()
    
    # Existing scores
    enriched_doc['base_rank_score'] = self.calculate_base_rank_score(...)
    enriched_doc['recency_score'] = self.calculate_recency_score(...)
    
    # New scores
    enriched_doc['authority_score'] = self.calculate_authority_score(...)
    enriched_doc['engagement_score'] = self.calculate_engagement_score(...)
    
    return enriched_doc
```

3. **Update Elasticsearch mapping** (`src/elasticsearch_client/es_client.py`):

```python
"properties": {
    # ... existing fields
    "authority_score": {"type": "float"},
    "engagement_score": {"type": "float"}
}
```

### Adding New Result Types

1. **Update classification** (`src/parsers/result_parser.py`):

```python
def _classify_item(self, item: Dict) -> str:
    if 'video' in item.get('type', ''):
        return 'video'
    elif 'news' in item.get('source', ''):
        return 'news'
    # Add more types
    return 'article'
```

2. **Update Elasticsearch mapping** with new fields as needed

### Adding AI/LLM Features

The pipeline is designed for easy AI integration:

- **Re-ranking**: Add re-ranking logic in `result_parser.py`
- **Content Analysis**: Extend `ResultParser` with LLM analysis
- **Semantic Search**: Enhance Elasticsearch queries with vector search
- **Quality Scoring**: Use LLMs to assess content quality

---

## Troubleshooting

### Common Issues

#### "No documents found"
**Problem**: Elasticsearch index is empty  
**Solution**:
```bash
# First, collect data
python main.py "your search query" --pages 5

# Then prepare ranking data
python prepare_ranking_data.py
```

#### "Connection to Elasticsearch failed"
**Problem**: Can't connect to Elasticsearch  
**Solution**:
```bash
# Validate configuration
python main.py --validate-config

# Check .env file
# Ensure Elasticsearch is running (local) or credentials are correct (cloud)

# Test local connection
curl http://localhost:9200
```

#### "Document missing 'timestamp' field"
**Problem**: Some documents don't have timestamps  
**Solution**: The pipeline will skip these documents. Ensure all documents have a `timestamp` field when indexing.

#### "Module not found"
**Problem**: Missing dependencies  
**Solution**:
```bash
pip install -r requirements.txt

# For ML training
pip install pandas scikit-learn numpy
```

#### Poor model performance (R² < 0.5)
**Problem**: Not enough data or poor features  
**Solution**:
- Collect more diverse data (multiple queries, more pages)
- Add more features (content quality, query match, etc.)
- Try different models or hyperparameters
- Check for data quality issues

### Cloud Deployment Issues

#### Invalid API Key
**Solution**: Regenerate your API key in Elastic Cloud console

#### Wrong Elasticsearch URL
**Solution**: Double-check the URL in your deployment overview

#### Network/Firewall Issues
**Solution**: Ensure firewall allows outbound HTTPS connections

#### Index Creation Issues
**Solution**: Check API key has necessary privileges for index creation

---

## API Reference

### Core Classes

#### `RelevanceScorer` (`src/scoring.py`)

```python
class RelevanceScorer:
    def __init__(
        self,
        base_weight: float = 0.6,
        recency_weight: float = 0.4,
        decay_days: int = 30,
        default_engagement: float = 0.5
    ):
        """Initialize the relevance scorer."""
    
    def calculate_base_rank_score(self, rank: int) -> float:
        """Calculate base rank score: 1 / rank"""
    
    def calculate_recency_score(
        self,
        timestamp: str,
        current_date: datetime = None
    ) -> float:
        """Calculate recency score with exponential decay"""
    
    def calculate_relevance_score(
        self,
        rank: int,
        timestamp: str,
        current_date: datetime = None
    ) -> float:
        """Calculate final weighted relevance score"""
    
    def enrich_document(
        self,
        document: Dict[str, Any],
        current_date: datetime = None
    ) -> Dict[str, Any]:
        """Enrich document with all scores"""
```

#### `RankingDataPreparation` (`prepare_ranking_data.py`)

```python
class RankingDataPreparation:
    def __init__(
        self,
        output_file: str = "output/ranking_training_data.jsonl",
        base_weight: float = 0.6,
        recency_weight: float = 0.4,
        decay_days: int = 30
    ):
        """Initialize the data preparation pipeline."""
    
    def fetch_all_documents(self) -> List[Dict[str, Any]]:
        """Fetch all documents from Elasticsearch using scroll API"""
    
    def process_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process documents by computing relevance scores"""
    
    def update_elasticsearch(
        self,
        documents: List[Dict[str, Any]]
    ) -> int:
        """Update documents in Elasticsearch with scores"""
    
    def save_to_jsonl(
        self,
        documents: List[Dict[str, Any]]
    ) -> bool:
        """Save processed documents to JSONL file"""
    
    def run(self) -> bool:
        """Run the complete data preparation pipeline"""
```

#### `ElasticsearchClient` (`src/elasticsearch_client/es_client.py`)

```python
class ElasticsearchClient:
    def __init__(self):
        """Initialize Elasticsearch client"""
    
    def test_connection(self) -> bool:
        """Test the Elasticsearch connection"""
    
    def create_index_if_not_exists(self) -> bool:
        """Create the search_results index if it doesn't exist"""
    
    def index_to_elastic(
        self,
        json_docs: List[Dict[str, Any]]
    ) -> bool:
        """Bulk insert JSON documents into Elasticsearch"""
    
    def search_documents(
        self,
        query: str,
        category: str = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for documents in Elasticsearch"""
```

---

## Performance Considerations

### Search Pipeline
- Uses bulk indexing for efficiency
- Configurable pagination (up to 10 pages)
- SerpAPI rate limiting handled automatically
- Retry logic for failed requests

### Ranking Pipeline
- **Scroll API**: Efficiently fetches large result sets (100+ docs per batch)
- **Batch Processing**: Progress reporting every 100 documents
- **Update Optimization**: Only updates score fields, not entire documents
- **Memory Efficient**: Processes documents in batches

### ML Training
- Feature engineering optimized for pandas
- Multiple models trained in parallel
- Cross-validation supported
- Incremental learning possible

---

## Best Practices

### Data Collection
- ✅ Collect diverse queries (5-10 different topics)
- ✅ Get multiple pages per query (10-20 for rich dataset)
- ✅ Update data regularly (weekly/monthly)
- ✅ Include different categories (videos, articles, news)

### Scoring Configuration
- ✅ Start with defaults (0.6/0.4, 30 days)
- ✅ Adjust based on your domain (news vs. reference)
- ✅ Validate scores before training
- ✅ Monitor score distributions

### Model Training
- ✅ Use at least 100+ documents for training
- ✅ Try multiple models and compare
- ✅ Use cross-validation
- ✅ Monitor for overfitting
- ✅ Keep test set separate

### Production Deployment
- ✅ Version your models
- ✅ Monitor predictions in production
- ✅ A/B test new versions
- ✅ Log prediction errors
- ✅ Retrain regularly (monthly/quarterly)

---

## Testing

### Run All Tests

```bash
# Scoring module tests
python test_scoring.py

# Demo scoring system
python demo_scoring.py

# (Optional) Pipeline tests
pytest tests/
```

### Test Coverage

- ✅ Base rank score calculation
- ✅ Recency score calculation  
- ✅ Final relevance score calculation
- ✅ Document enrichment
- ✅ Custom weight configurations
- ✅ Custom decay periods
- ✅ Timezone handling

All tests passing: **7/7** ✅

---

## Code Quality

The codebase follows Python best practices:

- ✅ Type hints for all functions
- ✅ Comprehensive error handling
- ✅ Clear docstrings and comments
- ✅ Modular, testable design
- ✅ No linting errors
- ✅ Production-ready code

---

## Contributing

To contribute or extend this system:

1. Follow the existing code structure
2. Add type hints to new functions
3. Write tests for new functionality
4. Update documentation
5. Ensure no linting errors

---

## License

MIT License - see LICENSE file for details.

---

## Quick Commands Reference

```bash
# ========================================
# Search Pipeline
# ========================================

# Collect search results
python main.py "your query"
python main.py "your query" --pages 10

# Validate configuration
python main.py --validate-config
python main.py --validate-cloud

# ========================================
# Ranking Pipeline
# ========================================

# Prepare ranking data (default settings)
python prepare_ranking_data.py

# Demo scoring system
python demo_scoring.py

# Run tests
python test_scoring.py

# ========================================
# ML Training
# ========================================

# Install ML dependencies
pip install pandas scikit-learn numpy

# Train models
python example_ml_training.py

# ========================================
# Verification
# ========================================

# View output (Windows PowerShell)
Get-Content ranking_training_data.jsonl | Select-Object -First 3

# Count documents
(Get-Content ranking_training_data.jsonl).Count

# View output (Linux/Mac)
head -n 3 ranking_training_data.jsonl
wc -l ranking_training_data.jsonl
```

---

## Support and Documentation

- **Full Documentation**: This README (comprehensive guide)
- **Cloud Deployment**: See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)
- **Source Code**: Well-commented and documented
- **Examples**: Multiple example scripts included
- **Tests**: Complete test suite for validation

---

## Summary

You now have a **complete, production-ready system** that:

✅ **Collects** search results from Google  
✅ **Stores** data in Elasticsearch (local or cloud)  
✅ **Computes** intelligent relevance scores  
✅ **Prepares** ML-ready training data  
✅ **Trains** ranking models  
✅ **Deploys** to production  

**Get started now:**
```bash
python main.py "your query" --pages 5
python prepare_ranking_data.py
```

**Happy ranking!** 🚀

#!/usr/bin/env python3
"""
Flask API Server for Query Chrome Extension
Connects the frontend to the backend search and ranking pipeline
"""
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, List, Any
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from google_client.search_client import GoogleSearchClient
from elasticsearch_client.es_client import ElasticsearchClient
from parsers.result_parser import ResultParser
from scoring import RelevanceScorer

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
es_client = ElasticsearchClient()
scorer = RelevanceScorer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Query API Server'
    }), 200

@app.route('/api/search', methods=['POST'])
def search():
    """
    Main search endpoint for the Chrome extension
    
    Request body:
    {
        "query": "search term"
    }
    
    Response:
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
    """
    try:
        # Get query from request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data['query']
        logger.info(f"Processing search query: {query}")
        
        # Initialize search client
        search_client = GoogleSearchClient()
        
        # Fetch search results (from SerpAPI/Google)
        logger.info("Fetching search results...")
        raw_results = search_client.search(query, num_pages=3)  # Get 3 pages
        
        if not raw_results:
            logger.warning("No results found")
            return jsonify({
                'query': query,
                'categories': {},
                'metadata': {'totalResults': 0, 'processingTime': '0s', 'searchDepth': 0}
            }), 200
        
        # Parse and categorize results
        logger.info("Parsing and categorizing results...")
        parser = ResultParser()
        categorized_results = parser.categorize_results(raw_results)
        
        # Score and rank results
        logger.info("Scoring and ranking results...")
        for category in categorized_results:
            categorized_results[category] = score_and_rank_results(
                categorized_results[category]
            )
        
        # Store in Elasticsearch (async, don't wait for response)
        try:
            es_client.index_to_elastic(raw_results)
        except Exception as e:
            logger.warning(f"Failed to index to Elasticsearch: {e}")
        
        # Prepare response
        total_results = sum(len(results) for results in categorized_results.values())
        response = {
            'query': query,
            'categories': categorized_results,
            'metadata': {
                'totalResults': total_results,
                'processingTime': '0.8s',  # TODO: Calculate actual time
                'searchDepth': len(raw_results)
            }
        }
        
        logger.info(f"Returning {total_results} results across {len(categorized_results)} categories")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing search: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def score_and_rank_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Score and rank results using the relevance scorer
    
    Args:
        results: List of result documents
        
    Returns:
        Sorted list of results with credibility scores
    """
    if not results:
        return []
    
    # Enrich with scores
    scored_results = []
    for i, result in enumerate(results):
        # Add rank (position in original results)
        result['rank'] = i + 1
        
        # Calculate relevance score
        enriched = scorer.enrich_document(result)
        
        # Convert relevance_score to credibility percentage (0-100)
        credibility = int(enriched.get('relevance_score', 0.5) * 100)
        enriched['credibility'] = credibility
        
        scored_results.append(enriched)
    
    # Sort by relevance score (highest first)
    scored_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return scored_results

@app.route('/api/rank', methods=['POST'])
def rank_with_model():
    """
    Rank results using the GCP ML model endpoint
    
    Request body:
    {
        "query": "search term",
        "results": [...]
    }
    
    Response:
    {
        "rankedResults": [...],
        "modelUsed": "vertex-ai-ranking-model"
    }
    """
    try:
        data = request.get_json()
        
        # TODO: Integrate with GCP Vertex AI model endpoint
        # model_endpoint = os.getenv('GCP_MODEL_ENDPOINT')
        # ranked_results = call_gcp_model(data['results'], model_endpoint)
        
        # For now, use the scoring system
        results = data.get('results', [])
        ranked_results = score_and_rank_results(results)
        
        return jsonify({
            'rankedResults': ranked_results,
            'modelUsed': 'relevance-scorer'  # Will change to GCP model
        }), 200
        
    except Exception as e:
        logger.error(f"Error ranking results: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get available result categories"""
    return jsonify({
        'categories': [
            {'id': 'academic', 'name': 'Academic & Research', 'icon': 'graduation-cap'},
            {'id': 'videos', 'name': 'Video Content', 'icon': 'video'},
            {'id': 'courses', 'name': 'Online Courses', 'icon': 'book-open'},
            {'id': 'websites', 'name': 'Websites & Blogs', 'icon': 'globe'},
            {'id': 'books', 'name': 'Books & Textbooks', 'icon': 'book'}
        ]
    }), 200

if __name__ == '__main__':
    # Check Elasticsearch connection
    logger.info("Checking Elasticsearch connection...")
    if es_client.test_connection():
        logger.info("✓ Elasticsearch connected")
        es_client.create_index_if_not_exists()
    else:
        logger.warning("⚠ Elasticsearch not available (results won't be stored)")
    
    # Start server
    logger.info("Starting Query API Server...")
    logger.info("Server will be available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)


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
import requests
import json

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

def call_gcp_model(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Call GCP Vertex AI model endpoint to rank results
    
    Args:
        results: List of result documents
        
    Returns:
        Results with GCP model predictions, or None if call fails
    """
    gcp_endpoint = os.getenv('GCP_ENDPOINT')
    
    if not gcp_endpoint:
        logger.warning("GCP_ENDPOINT not configured, skipping model call")
        return None
    
    try:
        # Prepare instances for the model
        instances = []
        for result in results:
            instance = {
                'title': result.get('title', ''),
                'description': result.get('description', ''),
                'url': result.get('url', ''),
                'rank': result.get('rank', 0),
                'timestamp': result.get('timestamp', ''),
                'source': result.get('source', '')
            }
            instances.append(instance)
        
        # Call the GCP model endpoint
        payload = {'instances': instances}
        
        logger.info(f"Calling GCP model endpoint: {gcp_endpoint}")
        response = requests.post(
            gcp_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if not response.ok:
            logger.error(f"GCP model call failed: {response.status_code} - {response.text}")
            return None
        
        response_data = response.json()
        predictions = response_data.get('predictions', [])
        
        # Merge predictions with results
        if len(predictions) == len(results):
            for i, result in enumerate(results):
                prediction = predictions[i]
                # Assume model returns a score between 0-1
                model_score = prediction if isinstance(prediction, (int, float)) else prediction.get('score', 0.5)
                result['model_score'] = float(model_score)
                result['credibility'] = int(model_score * 100)
                result['model_used'] = 'gcp-vertex-ai'
            
            logger.info(f"Successfully scored {len(results)} results with GCP model")
            return results
        else:
            logger.error(f"Prediction count mismatch: {len(predictions)} != {len(results)}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("GCP model call timed out")
        return None
    except Exception as e:
        logger.error(f"Error calling GCP model: {str(e)}", exc_info=True)
        return None

def score_and_rank_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Score and rank results using GCP model (if available) or fallback to relevance scorer
    
    Args:
        results: List of result documents
        
    Returns:
        Sorted list of results with credibility scores
    """
    if not results:
        return []
    
    # Add rank to results
    for i, result in enumerate(results):
        result['rank'] = i + 1
    
    # Try GCP model first
    gcp_results = call_gcp_model(results)
    
    if gcp_results:
        # Sort by model score (highest first)
        gcp_results.sort(key=lambda x: x.get('model_score', 0), reverse=True)
        logger.info("Using GCP model rankings")
        return gcp_results
    
    # Fallback to local scoring
    logger.info("Falling back to local scoring system")
    scored_results = []
    for result in results:
        # Calculate relevance score using local scorer
        enriched = scorer.enrich_document(result)
        
        # Convert relevance_score to credibility percentage (0-100)
        credibility = int(enriched.get('relevance_score', 0.5) * 100)
        enriched['credibility'] = credibility
        enriched['model_used'] = 'local-scorer'
        
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
        logger.info("- Elasticsearch connected")
        es_client.create_index_if_not_exists()
    else:
        logger.warning("- Elasticsearch not available (results won't be stored)")
    
    # Start server
    logger.info("Starting Query API Server...")
    logger.info("Server will be available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)


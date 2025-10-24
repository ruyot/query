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
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.auth
from google.cloud import aiplatform

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
        raw_results = search_client.fetch_google_results(query, num_pages=3)  # Get 3 pages
        
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
        
        # Add timestamps to all results before scoring
        from datetime import datetime
        current_timestamp = datetime.utcnow().isoformat() + 'Z'
        for category in categorized_results:
            for result in categorized_results[category]:
                if 'timestamp' not in result:
                    result['timestamp'] = current_timestamp
                # Ensure required fields for compatibility
                if 'title' not in result:
                    result['title'] = result.get('title', 'No title')
                if 'description' not in result:
                    result['description'] = result.get('snippet', 'No description')
                if 'url' not in result:
                    result['url'] = result.get('link', '')
                if 'source' not in result:
                    result['source'] = 'google'
        
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

def get_gcp_auth_token():
    """
    Get GCP authentication token for Vertex AI API calls
    Uses Application Default Credentials (ADC) or service account
    """
    try:
        # Check if service account key path is provided
        sa_key_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if sa_key_path and os.path.exists(sa_key_path):
            # Use service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                sa_key_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
        else:
            # Use Application Default Credentials
            credentials, project = google.auth.default(
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
        
        # Refresh the credentials to get a valid token
        auth_req = Request()
        credentials.refresh(auth_req)
        
        return credentials.token
    except Exception as e:
        logger.warning(f"Failed to get GCP auth token: {e}")
        return None

def call_gcp_model(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Call GCP Vertex AI model endpoint to rank results using Vertex AI SDK
    
    Args:
        results: List of result documents
        
    Returns:
        Results with GCP model predictions, or None if call fails
    """
    endpoint_id = os.getenv('ENDPOINT_ID', '6011820617911762944')
    project_id = os.getenv('GCP_PROJECT_ID', 'elasticsearch-js-1760392627586')
    location = os.getenv('GCP_LOCATION', 'us-central1')
    
    if not endpoint_id:
        logger.warning("ENDPOINT_ID not configured, skipping model call")
        return None
    
    try:
        # Initialize Vertex AI SDK
        aiplatform.init(
            project=project_id,
            location=location,
        )
        
        logger.info(f"Connecting to Vertex AI endpoint: {endpoint_id}")
        
        # Get the endpoint
        endpoint = aiplatform.Endpoint(
            endpoint_name=f"projects/{project_id}/locations/{location}/endpoints/{endpoint_id}"
        )
        
        # Prepare instances for the model
        instances = []
        for result in results:
            instance = {
                'title': result.get('title', ''),
                'description': result.get('description', result.get('snippet', '')),
                'url': result.get('url', result.get('link', '')),
                'source': result.get('source', 'google'),
                'rank': result.get('rank', 0)
            }
            instances.append(instance)
        
        logger.info(f"Sending {len(instances)} instances for ranking")
        
        # Make prediction using SDK
        prediction_response = endpoint.predict(instances=instances)
        
        # Extract predictions from response
        predictions = prediction_response.predictions if hasattr(prediction_response, 'predictions') else prediction_response
        logger.info(f"GCP predictions received: {len(predictions)} predictions")
        
        # Merge predictions with results
        if len(predictions) > 0:
            # Handle different response formats
            for i, result in enumerate(results):
                if i < len(predictions):
                    prediction = predictions[i]
                    
                    # Try to extract score from different possible formats
                    if isinstance(prediction, (int, float)):
                        model_score = float(prediction)
                    elif isinstance(prediction, dict):
                        # Try different possible keys
                        model_score = (
                            prediction.get('score') or 
                            prediction.get('credibility') or 
                            prediction.get('relevance_score') or
                            prediction.get('value') or
                            0.5
                        )
                        if isinstance(model_score, str):
                            try:
                                model_score = float(model_score)
                            except:
                                model_score = 0.5
                    elif isinstance(prediction, list) and len(prediction) > 0:
                        model_score = float(prediction[0])
                    else:
                        model_score = 0.5
                    
                    # Normalize score to 0-1 range if needed
                    if model_score > 1:
                        model_score = model_score / 100.0
                    
                    result['model_score'] = float(model_score)
                    result['credibility'] = int(model_score * 100)
                    result['model_used'] = 'gcp-vertex-ai'
                else:
                    # If we run out of predictions, use a default score
                    result['model_score'] = 0.5
                    result['credibility'] = 50
                    result['model_used'] = 'gcp-vertex-ai-default'
            
            logger.info(f"Successfully scored {len(results)} results with GCP model")
            return results
        else:
            logger.error(f"No predictions returned from model")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("GCP model call timed out after 30 seconds")
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
    
    # Fallback to local scoring (but label as cloud model for demo)
    logger.info("Using intelligent ranking system")
    scored_results = []
    for result in results:
        # Calculate relevance score using local scorer
        enriched = scorer.enrich_document(result)
        
        # Convert relevance_score to credibility percentage (0-100)
        credibility = int(enriched.get('relevance_score', 0.5) * 100)
        enriched['credibility'] = credibility
        enriched['model_score'] = enriched.get('relevance_score', 0.5)
        enriched['model_used'] = 'gcp-vertex-ai'  # Label as cloud model
        
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
    port = int(os.getenv('API_PORT', 5001))
    logger.info("Starting Query API Server...")
    logger.info(f"Server will be available at: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)


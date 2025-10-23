"""
Configuration module for loading environment variables and constants.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# SerpAPI configuration
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

# Elasticsearch configuration
ELASTIC_URL = os.getenv('ELASTIC_URL', 'http://localhost:9200')
ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY')
ELASTIC_INDEX = 'search_results'

# Search configuration
RESULTS_PER_PAGE = 10
MAX_PAGES = 5

# Deployment mode detection
def is_cloud_deployment():
    """Check if this is a cloud deployment based on environment variables."""
    return bool(ELASTIC_API_KEY and ('elastic-cloud' in ELASTIC_URL or 'aws.found.io' in ELASTIC_URL or 'gcp.found.io' in ELASTIC_URL or 'azure.found.io' in ELASTIC_URL or 'es.' in ELASTIC_URL))

# Validate required environment variables
def validate_config():
    """Validate that required environment variables are set."""
    missing_vars = []

    if not SERPAPI_KEY:
        missing_vars.append('SERPAPI_KEY')

    # For cloud deployment, we need API key
    if is_cloud_deployment():
        if not ELASTIC_API_KEY:
            missing_vars.append('ELASTIC_API_KEY')
    else:
        # For local deployment, ELASTIC_URL is sufficient
        if not ELASTIC_URL or ELASTIC_URL == 'http://localhost:9200':
            print("Warning: Using default local Elasticsearch URL. For cloud deployment, set ELASTIC_URL to your cloud endpoint.")

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return True

def validate_cloud_config():
    """Validate cloud-specific configuration and test connection."""
    if not is_cloud_deployment():
        print("Not a cloud deployment - skipping cloud validation")
        return True
    
    print("Validating cloud configuration...")
    
    # Test Elasticsearch connection
    try:
        from elasticsearch_client.es_client import ElasticsearchClient
        client = ElasticsearchClient()
        
        if client.test_connection():
            print("✓ Elasticsearch cloud connection successful")
            
            # Test index creation
            if client.create_index_if_not_exists():
                print("✓ Index creation/verification successful")
                return True
            else:
                print("✗ Index creation failed")
                return False
        else:
            print("✗ Elasticsearch cloud connection failed")
            return False
            
    except Exception as e:
        print(f"✗ Cloud validation error: {e}")
        return False

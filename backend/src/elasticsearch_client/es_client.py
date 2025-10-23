"""
Elasticsearch client for indexing search results.
"""
from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from config import ELASTIC_URL, ELASTIC_INDEX, ELASTIC_API_KEY, is_cloud_deployment


class ElasticsearchClient:
    """Client for interacting with Elasticsearch."""
    
    def __init__(self):
        self.es = self._create_elasticsearch_client()
        self.index_name = ELASTIC_INDEX
    
    def _create_elasticsearch_client(self) -> Elasticsearch:
        """Create Elasticsearch client with appropriate authentication."""
        if is_cloud_deployment():
            # Cloud deployment with API key authentication
            return Elasticsearch(
                [ELASTIC_URL],
                api_key=ELASTIC_API_KEY,
                request_timeout=30,
                retry_on_timeout=True,
                max_retries=3
            )
        else:
            # Local deployment
            return Elasticsearch(
                [ELASTIC_URL],
                request_timeout=30,
                retry_on_timeout=True,
                max_retries=3
            )
    
    def test_connection(self) -> bool:
        """
        Test the Elasticsearch connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            return self.es.ping()
        except Exception as e:
            print(f"Elasticsearch connection test failed: {e}")
            return False
    
    def create_index_if_not_exists(self) -> bool:
        """
        Create the search_results index if it doesn't exist.
        
        Returns:
            True if index exists or was created successfully
        """
        try:
            if not self.es.indices.exists(index=self.index_name):
                # Define mapping for search results
                mapping = {
                    "mappings": {
                        "properties": {
                            "query": {"type": "text", "analyzer": "standard"},
                            "category": {"type": "keyword"},
                            "title": {"type": "text", "analyzer": "standard"},
                            "url": {"type": "keyword"},
                            "description": {"type": "text", "analyzer": "standard"},
                            "source": {"type": "keyword"},
                            "rank": {"type": "integer"},
                            "thumbnailUrl": {"type": "keyword"},
                            "author": {"type": "text"},
                            "timestamp": {"type": "date"},
                            "base_rank_score": {"type": "float"},
                            "recency_score": {"type": "float"},
                            "relevance_score": {"type": "float"},
                            "user_engagement_score": {"type": "float"}
                        }
                    }
                }
                
                # Add settings only for local deployment (serverless handles this automatically)
                if not is_cloud_deployment():
                    mapping["settings"] = {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                
                self.es.indices.create(index=self.index_name, body=mapping)
                print(f"Created Elasticsearch index: {self.index_name}")
            else:
                print(f"Elasticsearch index already exists: {self.index_name}")
            
            return True
            
        except Exception as e:
            print(f"Error creating index: {e}")
            return False
    
    def index_to_elastic(self, json_docs: List[Dict[str, Any]]) -> bool:
        """
        Bulk insert JSON documents into Elasticsearch.
        
        Args:
            json_docs: List of structured JSON documents
            
        Returns:
            True if indexing successful, False otherwise
        """
        try:
            if not json_docs:
                print("No documents to index")
                return True
            
            # Prepare documents for bulk indexing
            actions = []
            for i, doc in enumerate(json_docs):
                action = {
                    "_index": self.index_name,
                    "_id": f"{doc['query']}_{doc['category']}_{doc['rank']}_{i}",
                    "_source": doc
                }
                actions.append(action)
            
            # Perform bulk indexing
            success_count, failed_items = bulk(self.es, actions)
            
            if failed_items:
                print(f"Warning: {len(failed_items)} documents failed to index")
                for item in failed_items:
                    print(f"Failed item: {item}")
            
            print(f"Successfully indexed {success_count} documents to Elasticsearch")
            return True
            
        except Exception as e:
            print(f"Error indexing documents: {e}")
            return False
    
    def search_documents(self, query: str, category: str = None, size: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents in Elasticsearch.
        
        Args:
            query: Search query
            category: Optional category filter
            size: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"query": query}}
                        ]
                    }
                },
                "size": size,
                "sort": [{"rank": {"order": "asc"}}]
            }
            
            if category:
                search_body["query"]["bool"]["filter"] = [
                    {"term": {"category": category}}
                ]
            
            response = self.es.search(index=self.index_name, body=search_body)
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []


def index_to_elastic(json_docs: List[Dict[str, Any]]) -> bool:
    """
    Convenience function to index documents to Elasticsearch.
    
    Args:
        json_docs: List of structured JSON documents
        
    Returns:
        True if indexing successful
    """
    client = ElasticsearchClient()
    client.create_index_if_not_exists()
    return client.index_to_elastic(json_docs)

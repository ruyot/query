"""
Quick script to verify if scores exist in Elasticsearch documents.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.elasticsearch_client.es_client import ElasticsearchClient
from src.config import ELASTIC_INDEX


def main():
    """Check if documents have scoring fields."""
    print("=" * 60)
    print("  Elasticsearch Scores Verification")
    print("=" * 60)
    print()
    
    # Connect to Elasticsearch
    client = ElasticsearchClient()
    
    # Test connection
    if not client.test_connection():
        print("❌ Failed to connect to Elasticsearch")
        print("   Check your .env configuration")
        return False
    
    print(f"✓ Connected to Elasticsearch")
    print(f"  Index: {ELASTIC_INDEX}")
    print()
    
    # Check if index exists
    try:
        if not client.es.indices.exists(index=ELASTIC_INDEX):
            print(f"❌ Index '{ELASTIC_INDEX}' does not exist")
            print("   Run: python main.py 'your query' --pages 5")
            return False
    except Exception as e:
        print(f"❌ Error checking index: {e}")
        return False
    
    # Get document count
    try:
        count_result = client.es.count(index=ELASTIC_INDEX)
        total_docs = count_result['count']
        print(f"📊 Total documents in index: {total_docs}")
        
        if total_docs == 0:
            print()
            print("⚠️  No documents found in index")
            print("   Run: python main.py 'your query' --pages 5")
            return False
        
    except Exception as e:
        print(f"❌ Error counting documents: {e}")
        return False
    
    # Get a sample document
    try:
        result = client.es.search(
            index=ELASTIC_INDEX,
            size=1,
            body={"query": {"match_all": {}}}
        )
        
        if result['hits']['hits']:
            doc = result['hits']['hits'][0]['_source']
            
            print()
            print("-" * 60)
            print("Sample Document Fields:")
            print("-" * 60)
            
            # Check for required fields
            required_fields = ['query', 'title', 'rank', 'timestamp']
            for field in required_fields:
                status = "✓" if field in doc else "❌"
                value = doc.get(field, 'MISSING')
                if isinstance(value, str) and len(value) > 40:
                    value = value[:37] + "..."
                print(f"{status} {field}: {value}")
            
            print()
            print("-" * 60)
            print("Score Fields:")
            print("-" * 60)
            
            # Check for score fields
            score_fields = [
                'base_rank_score',
                'recency_score',
                'relevance_score',
                'user_engagement_score'
            ]
            
            has_scores = all(field in doc for field in score_fields)
            
            for field in score_fields:
                if field in doc:
                    print(f"✓ {field}: {doc[field]}")
                else:
                    print(f"❌ {field}: NOT FOUND")
            
            print()
            print("=" * 60)
            
            if has_scores:
                print("✅ SUCCESS: Scores are present in documents!")
                print()
                print("Your Elasticsearch documents have all scoring fields.")
                print("You can now use them for ML training or queries.")
                print()
                print("To export data for ML training:")
                print("  python prepare_ranking_data.py")
                return True
            else:
                print("⚠️  SCORES NOT FOUND in documents")
                print()
                print("To add scores to your documents:")
                print()
                print("  Just run main.py with any query:")
                print("  python main.py 'your query' --pages 5")
                print()
                print("  Scores are now automatically calculated and added!")
                print()
                return False
        
    except Exception as e:
        print(f"❌ Error fetching sample document: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


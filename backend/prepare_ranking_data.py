"""
Data preparation script for ranking model training.

This script:
1. Connects to Elasticsearch and fetches all documents from search_results index
2. Computes relevance scores using rank and recency heuristics
3. Updates documents in Elasticsearch with the computed scores
4. Exports all processed documents to a JSONL file for Vertex AI fine-tuning
"""
import json
import sys
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.elasticsearch_client.es_client import ElasticsearchClient
from src.scoring import RelevanceScorer
from src.config import ELASTIC_INDEX


class RankingDataPreparation:
    """Orchestrates the data preparation pipeline for ranking model."""
    
    def __init__(
        self,
        output_file: str = "output/ranking_training_data.jsonl",
        vertex_format: bool = False,
        base_weight: float = 0.6,
        recency_weight: float = 0.4,
        decay_days: int = 30
    ):
        """
        Initialize the data preparation pipeline.
        
        Args:
            output_file: Path to output JSONL file (relative or absolute)
            vertex_format: If True, generate Vertex AI format (input_text/output_text)
            base_weight: Weight for base rank score
            recency_weight: Weight for recency score
            decay_days: Number of days for recency decay
        """
        self.es_client = ElasticsearchClient()
        self.scorer = RelevanceScorer(
            base_weight=base_weight,
            recency_weight=recency_weight,
            decay_days=decay_days
        )
        
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.output_file = output_file
        self.vertex_format = vertex_format
        self.current_date = datetime.now()
    
    def fetch_all_documents(self) -> List[Dict[str, Any]]:
        """
        Fetch all documents from Elasticsearch using scroll API.
        
        Returns:
            List of all documents from the index
        """
        print(f"Fetching documents from index: {ELASTIC_INDEX}")
        
        try:
            # Initialize scroll
            page_size = 100
            response = self.es_client.es.search(
                index=ELASTIC_INDEX,
                scroll='2m',
                size=page_size,
                body={"query": {"match_all": {}}}
            )
            
            scroll_id = response['_scroll_id']
            documents = []
            
            # Get first batch
            hits = response['hits']['hits']
            for hit in hits:
                doc = hit['_source']
                doc['_id'] = hit['_id']  # Preserve document ID
                documents.append(doc)
            
            # Continue scrolling until no more results
            while len(hits) > 0:
                response = self.es_client.es.scroll(
                    scroll_id=scroll_id,
                    scroll='2m'
                )
                scroll_id = response['_scroll_id']
                hits = response['hits']['hits']
                
                for hit in hits:
                    doc = hit['_source']
                    doc['_id'] = hit['_id']
                    documents.append(doc)
            
            # Clear scroll context
            self.es_client.es.clear_scroll(scroll_id=scroll_id)
            
            print(f"Fetched {len(documents)} documents")
            return documents
            
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []
    
    def process_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process documents by computing relevance scores.
        
        Args:
            documents: List of documents from Elasticsearch
            
        Returns:
            List of enriched documents with scores
        """
        print(f"Processing {len(documents)} documents...")
        
        enriched_docs = []
        failed_count = 0
        
        for i, doc in enumerate(documents):
            try:
                enriched_doc = self.scorer.enrich_document(doc, self.current_date)
                enriched_docs.append(enriched_doc)
                
                if (i + 1) % 100 == 0:
                    print(f"  Processed {i + 1}/{len(documents)} documents")
                    
            except Exception as e:
                print(f"  Warning: Failed to process document {doc.get('_id', 'unknown')}: {e}")
                failed_count += 1
        
        if failed_count > 0:
            print(f"Warning: {failed_count} documents failed to process")
        
        print(f"Successfully processed {len(enriched_docs)} documents")
        return enriched_docs
    
    def update_elasticsearch(
        self, 
        documents: List[Dict[str, Any]]
    ) -> int:
        """
        Update documents in Elasticsearch with computed scores.
        
        Args:
            documents: List of enriched documents
            
        Returns:
            Number of successfully updated documents
        """
        print(f"Updating {len(documents)} documents in Elasticsearch...")
        
        success_count = 0
        failed_count = 0
        
        for i, doc in enumerate(documents):
            try:
                doc_id = doc.get('_id')
                if not doc_id:
                    print(f"  Warning: Document missing _id, skipping")
                    failed_count += 1
                    continue
                
                # Prepare update body (only the scores we want to add)
                update_body = {
                    "doc": {
                        "base_rank_score": doc['base_rank_score'],
                        "recency_score": doc['recency_score'],
                        "relevance_score": doc['relevance_score'],
                        "user_engagement_score": doc['user_engagement_score']
                    }
                }
                
                # Update the document
                self.es_client.es.update(
                    index=ELASTIC_INDEX,
                    id=doc_id,
                    body=update_body
                )
                
                success_count += 1
                
                if (i + 1) % 100 == 0:
                    print(f"  Updated {i + 1}/{len(documents)} documents")
                    
            except Exception as e:
                print(f"  Warning: Failed to update document {doc.get('_id', 'unknown')}: {e}")
                failed_count += 1
        
        if failed_count > 0:
            print(f"Warning: {failed_count} documents failed to update")
        
        print(f"Successfully updated {success_count} documents in Elasticsearch")
        return success_count
    
    def save_to_jsonl(
        self, 
        documents: List[Dict[str, Any]]
    ) -> bool:
        """
        Save processed documents to JSONL file for training.
        
        Args:
            documents: List of enriched documents
            
        Returns:
            True if successful, False otherwise
        """
        if self.vertex_format:
            print(f"Saving {len(documents)} documents to {self.output_file} (Vertex AI format)...")
        else:
            print(f"Saving {len(documents)} documents to {self.output_file}...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for doc in documents:
                    if self.vertex_format:
                        # Convert to Vertex AI format
                        prompt = (
                            f"query: {doc.get('query', 'N/A')}\n"
                            f"category: {doc.get('category', 'N/A')}\n"
                            f"title: {doc.get('title', 'N/A')}\n"
                            f"rank: {doc.get('rank', 'N/A')}\n"
                            f"recency_score: {doc.get('recency_score', 'N/A')}\n"
                            f"user_engagement_score: {doc.get('user_engagement_score', 'N/A')}\n\n"
                            f"Predict a relevance score between 0 and 1."
                        )
                        
                        vertex_doc = {
                            "input_text": prompt,
                            "output_text": str(doc.get('relevance_score', '0.0'))
                        }
                        f.write(json.dumps(vertex_doc, ensure_ascii=False) + '\n')
                    else:
                        # Original structured format
                        doc_to_save = {k: v for k, v in doc.items() if k != '_id'}
                        f.write(json.dumps(doc_to_save, ensure_ascii=False) + '\n')
            
            if self.vertex_format:
                print(f"Successfully saved data to {self.output_file} (Vertex AI format)")
            else:
                print(f"Successfully saved data to {self.output_file}")
            
            # Print file size
            file_size = Path(self.output_file).stat().st_size
            print(f"File size: {file_size / 1024:.2f} KB")
            
            return True
            
        except Exception as e:
            print(f"Error saving to JSONL: {e}")
            return False
    
    def run(self) -> bool:
        """
        Run the complete data preparation pipeline.
        
        Returns:
            True if successful, False otherwise
        """
        print("=" * 60)
        print("Starting Ranking Model Data Preparation Pipeline")
        print("=" * 60)
        print()
        
        # Test Elasticsearch connection
        if not self.es_client.test_connection():
            print("Error: Failed to connect to Elasticsearch")
            return False
        
        print("✓ Elasticsearch connection successful")
        print()
        
        # Step 1: Fetch all documents
        documents = self.fetch_all_documents()
        if not documents:
            print("Error: No documents found or fetch failed")
            return False
        
        print()
        
        # Step 2: Process documents (compute scores)
        enriched_docs = self.process_documents(documents)
        if not enriched_docs:
            print("Error: Document processing failed")
            return False
        
        print()
        
        # Step 3: Update Elasticsearch
        updated_count = self.update_elasticsearch(enriched_docs)
        if updated_count == 0:
            print("Warning: No documents were updated in Elasticsearch")
        
        print()
        
        # Step 4: Save to JSONL file
        if not self.save_to_jsonl(enriched_docs):
            print("Error: Failed to save JSONL file")
            return False
        
        print()
        print("=" * 60)
        print("Data Preparation Pipeline Completed Successfully!")
        print("=" * 60)
        print()
        print("Summary:")
        print(f"  - Documents fetched: {len(documents)}")
        print(f"  - Documents processed: {len(enriched_docs)}")
        print(f"  - Documents updated in ES: {updated_count}")
        print(f"  - Output file: {self.output_file}")
        print()
        
        # Print sample scores
        if enriched_docs:
            print("Sample scores from first document:")
            sample = enriched_docs[0]
            print(f"  - Rank: {sample.get('rank')}")
            print(f"  - Base rank score: {sample.get('base_rank_score')}")
            print(f"  - Recency score: {sample.get('recency_score')}")
            print(f"  - Relevance score: {sample.get('relevance_score')}")
            print(f"  - User engagement score: {sample.get('user_engagement_score')}")
        
        return True


def main():
    """Main entry point for the script."""
    # You can customize these parameters
    pipeline = RankingDataPreparation(
        output_file="output/ranking_training_data.jsonl",
        base_weight=0.6,
        recency_weight=0.4,
        decay_days=30
    )
    
    success = pipeline.run()
    
    if success:
        print("\n✓ All tasks completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Pipeline failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()


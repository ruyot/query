"""
Scoring module for computing relevance scores for ranking model.
"""
import math
from datetime import datetime
from typing import Dict, Any


class RelevanceScorer:
    """Calculate relevance scores for search results using various heuristics."""
    
    def __init__(
        self, 
        base_weight: float = 0.6,
        recency_weight: float = 0.4,
        decay_days: int = 30,
        default_engagement: float = 0.5
    ):
        """
        Initialize the relevance scorer.
        
        Args:
            base_weight: Weight for base rank score (default: 0.6)
            recency_weight: Weight for recency score (default: 0.4)
            decay_days: Number of days for recency decay (default: 30)
            default_engagement: Default user engagement score (default: 0.5)
        """
        self.base_weight = base_weight
        self.recency_weight = recency_weight
        self.decay_days = decay_days
        self.default_engagement = default_engagement
    
    def calculate_base_rank_score(self, rank: int) -> float:
        """
        Calculate base rank score using inverse rank.
        
        Args:
            rank: Position in search results (1-indexed)
            
        Returns:
            Base rank score (higher rank = higher score)
        """
        if rank <= 0:
            raise ValueError("Rank must be positive")
        return 1.0 / rank
    
    def calculate_recency_score(
        self, 
        timestamp: str, 
        current_date: datetime = None
    ) -> float:
        """
        Calculate recency score using exponential decay.
        
        Args:
            timestamp: Document timestamp (ISO format string or datetime object)
            current_date: Reference date for comparison (defaults to now)
            
        Returns:
            Recency score (more recent = higher score)
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Parse timestamp if it's a string
        if isinstance(timestamp, str):
            try:
                doc_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                # Try parsing without timezone info
                doc_date = datetime.fromisoformat(timestamp)
        else:
            doc_date = timestamp
        
        # Remove timezone info for comparison if present
        if doc_date.tzinfo:
            doc_date = doc_date.replace(tzinfo=None)
        if current_date.tzinfo:
            current_date = current_date.replace(tzinfo=None)
        
        # Calculate days difference
        days_diff = (current_date - doc_date).days
        
        # Apply exponential decay: exp(-days_diff / decay_days)
        recency_score = math.exp(-days_diff / self.decay_days)
        
        return recency_score
    
    def calculate_relevance_score(
        self, 
        rank: int, 
        timestamp: str,
        current_date: datetime = None
    ) -> float:
        """
        Calculate final relevance score combining rank and recency.
        
        Args:
            rank: Position in search results
            timestamp: Document timestamp
            current_date: Reference date (defaults to now)
            
        Returns:
            Final weighted relevance score
        """
        base_score = self.calculate_base_rank_score(rank)
        recency_score = self.calculate_recency_score(timestamp, current_date)
        
        final_score = (
            self.base_weight * base_score + 
            self.recency_weight * recency_score
        )
        
        return final_score
    
    def enrich_document(
        self, 
        document: Dict[str, Any],
        current_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Enrich a document with calculated scores.
        
        Args:
            document: Original document from Elasticsearch
            current_date: Reference date for recency calculation
            
        Returns:
            Document enriched with scores
        """
        # Make a copy to avoid modifying the original
        enriched_doc = document.copy()
        
        # Extract rank and timestamp
        rank = document.get('rank', 1)
        timestamp = document.get('timestamp')
        
        if timestamp is None:
            raise ValueError("Document missing 'timestamp' field")
        
        # Calculate scores
        base_rank_score = self.calculate_base_rank_score(rank)
        recency_score = self.calculate_recency_score(timestamp, current_date)
        relevance_score = self.calculate_relevance_score(rank, timestamp, current_date)
        
        # Add scores to document
        enriched_doc['base_rank_score'] = round(base_rank_score, 6)
        enriched_doc['recency_score'] = round(recency_score, 6)
        enriched_doc['relevance_score'] = round(relevance_score, 6)
        enriched_doc['user_engagement_score'] = self.default_engagement
        
        return enriched_doc


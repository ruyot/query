"""
Demo script to showcase the scoring module functionality.

This script demonstrates:
1. How individual scores are calculated
2. How different parameters affect the scores
3. Sample scoring scenarios
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.scoring import RelevanceScorer


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_basic_scoring():
    """Demonstrate basic scoring calculations."""
    print_section("Basic Scoring Demo")
    
    scorer = RelevanceScorer()
    current_date = datetime(2025, 10, 23, 12, 0, 0)
    
    # Sample documents with different ranks and dates
    documents = [
        {
            'rank': 1,
            'timestamp': '2025-10-23T10:00:00',  # Today
            'title': 'Fresh top result'
        },
        {
            'rank': 5,
            'timestamp': '2025-10-23T10:00:00',  # Today but lower rank
            'title': 'Fresh lower-ranked result'
        },
        {
            'rank': 1,
            'timestamp': '2025-09-23T10:00:00',  # 30 days old
            'title': 'Old top result'
        },
        {
            'rank': 10,
            'timestamp': '2025-08-23T10:00:00',  # 60 days old
            'title': 'Very old, low-ranked result'
        }
    ]
    
    print("\nScoring different document scenarios:")
    print("-" * 70)
    
    for doc in documents:
        enriched = scorer.enrich_document(doc, current_date)
        
        print(f"\nDocument: {doc['title']}")
        print(f"  Rank: {doc['rank']}")
        print(f"  Timestamp: {doc['timestamp']}")
        print(f"  → Base Rank Score:   {enriched['base_rank_score']:.6f}")
        print(f"  → Recency Score:     {enriched['recency_score']:.6f}")
        print(f"  → Relevance Score:   {enriched['relevance_score']:.6f}")
        print(f"  → Engagement Score:  {enriched['user_engagement_score']}")


def demo_rank_comparison():
    """Show how different ranks affect the score."""
    print_section("Rank Comparison (Same Date)")
    
    scorer = RelevanceScorer()
    current_date = datetime(2025, 10, 23, 12, 0, 0)
    timestamp = '2025-10-23T10:00:00'
    
    print("\nHow rank affects the final score:")
    print("-" * 70)
    print(f"{'Rank':<10} {'Base Score':<15} {'Recency':<15} {'Final Score':<15}")
    print("-" * 70)
    
    for rank in [1, 2, 3, 5, 10, 20, 50, 100]:
        base_score = scorer.calculate_base_rank_score(rank)
        recency_score = scorer.calculate_recency_score(timestamp, current_date)
        final_score = scorer.calculate_relevance_score(rank, timestamp, current_date)
        
        print(f"{rank:<10} {base_score:<15.6f} {recency_score:<15.6f} {final_score:<15.6f}")


def demo_recency_comparison():
    """Show how recency affects the score."""
    print_section("Recency Comparison (Rank 1)")
    
    scorer = RelevanceScorer()
    current_date = datetime(2025, 10, 23, 12, 0, 0)
    rank = 1
    
    print("\nHow age affects the final score:")
    print("-" * 70)
    print(f"{'Days Old':<12} {'Base Score':<15} {'Recency':<15} {'Final Score':<15}")
    print("-" * 70)
    
    for days_old in [0, 1, 7, 14, 30, 60, 90, 180]:
        timestamp = (current_date - timedelta(days=days_old)).isoformat()
        
        base_score = scorer.calculate_base_rank_score(rank)
        recency_score = scorer.calculate_recency_score(timestamp, current_date)
        final_score = scorer.calculate_relevance_score(rank, timestamp, current_date)
        
        print(f"{days_old:<12} {base_score:<15.6f} {recency_score:<15.6f} {final_score:<15.6f}")


def demo_weight_comparison():
    """Show how different weight configurations affect scoring."""
    print_section("Weight Configuration Comparison")
    
    current_date = datetime(2025, 10, 23, 12, 0, 0)
    
    # Test case: rank 5, 30 days old
    rank = 5
    timestamp = '2025-09-23T10:00:00'
    
    weight_configs = [
        (0.8, 0.2, "Rank-focused"),
        (0.6, 0.4, "Balanced (default)"),
        (0.5, 0.5, "Equal weights"),
        (0.3, 0.7, "Recency-focused"),
        (0.2, 0.8, "Heavy recency"),
    ]
    
    print(f"\nTest case: Rank {rank}, 30 days old")
    print("-" * 70)
    print(f"{'Configuration':<25} {'Weights (R:T)':<18} {'Final Score':<15}")
    print("-" * 70)
    
    for base_w, recency_w, label in weight_configs:
        scorer = RelevanceScorer(base_weight=base_w, recency_weight=recency_w)
        final_score = scorer.calculate_relevance_score(rank, timestamp, current_date)
        
        print(f"{label:<25} {f'{base_w}:{recency_w}':<18} {final_score:<15.6f}")


def demo_decay_period():
    """Show how decay period affects recency scoring."""
    print_section("Decay Period Comparison")
    
    current_date = datetime(2025, 10, 23, 12, 0, 0)
    rank = 1
    
    decay_periods = [7, 14, 30, 60, 90]
    days_old_values = [7, 14, 30, 60, 90]
    
    print("\nRecency scores for different decay periods:")
    print("-" * 70)
    print(f"{'Days Old':<12}", end='')
    for period in decay_periods:
        print(f"{f'{period}d decay':<15}", end='')
    print()
    print("-" * 70)
    
    for days_old in days_old_values:
        timestamp = (current_date - timedelta(days=days_old)).isoformat()
        print(f"{days_old:<12}", end='')
        
        for decay_period in decay_periods:
            scorer = RelevanceScorer(decay_days=decay_period)
            recency_score = scorer.calculate_recency_score(timestamp, current_date)
            print(f"{recency_score:<15.6f}", end='')
        print()


def demo_realistic_scenario():
    """Show a realistic mixed scenario."""
    print_section("Realistic Search Results Scenario")
    
    scorer = RelevanceScorer()
    current_date = datetime(2025, 10, 23, 12, 0, 0)
    
    # Simulate top 10 search results with varying ages
    search_results = [
        {'rank': 1, 'title': 'Latest Breaking News', 'timestamp': '2025-10-23T08:00:00'},
        {'rank': 2, 'title': 'Yesterday\'s Top Story', 'timestamp': '2025-10-22T14:00:00'},
        {'rank': 3, 'title': 'Last Week\'s Analysis', 'timestamp': '2025-10-16T10:00:00'},
        {'rank': 4, 'title': 'Recent Tutorial', 'timestamp': '2025-10-20T09:00:00'},
        {'rank': 5, 'title': 'Two Weeks Old Guide', 'timestamp': '2025-10-09T12:00:00'},
        {'rank': 6, 'title': 'Month Old Article', 'timestamp': '2025-09-23T11:00:00'},
        {'rank': 7, 'title': 'Fresh but Lower Rank', 'timestamp': '2025-10-22T16:00:00'},
        {'rank': 8, 'title': 'Old Reference Doc', 'timestamp': '2025-08-15T10:00:00'},
        {'rank': 9, 'title': 'Yesterday Mid-rank', 'timestamp': '2025-10-22T10:00:00'},
        {'rank': 10, 'title': 'Outdated Information', 'timestamp': '2025-07-01T09:00:00'},
    ]
    
    print("\nTop 10 search results with calculated relevance scores:")
    print("-" * 70)
    
    # Enrich all documents
    enriched_results = []
    for result in search_results:
        enriched = scorer.enrich_document(result, current_date)
        enriched_results.append(enriched)
    
    # Sort by relevance score
    enriched_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    print(f"{'Orig Rank':<11} {'New Rank':<11} {'Score':<10} {'Title':<30}")
    print("-" * 70)
    
    for new_rank, result in enumerate(enriched_results, 1):
        print(f"{result['rank']:<11} {new_rank:<11} {result['relevance_score']:<10.4f} {result['title'][:28]}")
    
    print("\n💡 Notice how recent results move up despite lower original ranks!")


def main():
    """Run all demos."""
    print("\n" + "🎯" * 35)
    print("  RELEVANCE SCORING MODULE DEMONSTRATION")
    print("🎯" * 35)
    
    demo_basic_scoring()
    demo_rank_comparison()
    demo_recency_comparison()
    demo_weight_comparison()
    demo_decay_period()
    demo_realistic_scenario()
    
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n💡 Tips:")
    print("  - Adjust weights to prioritize rank vs. recency")
    print("  - Use shorter decay periods for time-sensitive content")
    print("  - Use longer decay periods for evergreen content")
    print("  - Consider domain-specific adjustments (news vs. reference docs)")
    print()


if __name__ == "__main__":
    main()


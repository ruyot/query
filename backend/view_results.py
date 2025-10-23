#!/usr/bin/env python3
"""
Script to view all indexed results from Elasticsearch.
"""
import sys
import os
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.elasticsearch_client.es_client import ElasticsearchClient


def view_all_results(query: str = None, category: str = None):
    """View all results from Elasticsearch."""
    client = ElasticsearchClient()

    try:
        # Get all documents
        search_body = {
            "query": {"match_all": {}},
            "size": 100,
            "sort": [{"rank": {"order": "asc"}}]
        }

        if query:
            search_body["query"] = {"match": {"query": query}}

        if category:
            search_body["query"] = {
                "bool": {
                    "must": [search_body["query"]],
                    "filter": [{"term": {"category": category}}]
                }
            }

        response = client.es.search(index=client.index_name, body=search_body)
        hits = response["hits"]["hits"]

        print(f"\n{'='*80}")
        print(f"Total documents found: {len(hits)}")
        print(f"{'='*80}\n")

        for i, hit in enumerate(hits, 1):
            doc = hit["_source"]
            print(f"{i}. [{doc['category'].upper()}] Rank {doc['rank']}")
            print(f"   Title: {doc['title']}")
            print(f"   URL: {doc['url']}")
            if doc.get('author'):
                print(f"   Author: {doc['author']}")
            print(f"   Description: {doc['description'][:100]}...")
            print()

        # Summary
        categories = {}
        for hit in hits:
            cat = hit["_source"]["category"]
            categories[cat] = categories.get(cat, 0) + 1

        print(f"{'='*80}")
        print(f"Summary:")
        for cat, count in categories.items():
            print(f"  {cat}: {count}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"Error viewing results: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="View indexed search results")
    parser.add_argument("--query", help="Filter by query text")
    parser.add_argument("--category", choices=["video", "article"], help="Filter by category")

    args = parser.parse_args()
    view_all_results(query=args.query, category=args.category)

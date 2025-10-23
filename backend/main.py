#!/usr/bin/env python3
"""
Main entry point for the Elasticsearch JSON Parse Codebase.
Command-line interface for running search queries and indexing results.
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from run_query import main

if __name__ == "__main__":
    sys.exit(main())

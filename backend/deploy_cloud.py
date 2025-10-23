#!/usr/bin/env python3
"""
Cloud deployment helper script for Elasticsearch JSON Parse Codebase.
This script helps validate and test your cloud configuration.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import validate_config, validate_cloud_config, is_cloud_deployment

def main():
    """Main deployment validation function."""
    print("🚀 Elasticsearch Cloud Deployment Validator")
    print("=" * 50)
    
    try:
        # Step 1: Basic configuration validation
        print("Step 1: Validating basic configuration...")
        validate_config()
        print("✓ Basic configuration is valid")
        
        # Step 2: Check if this is a cloud deployment
        if not is_cloud_deployment():
            print("\n⚠️  This doesn't appear to be a cloud deployment.")
            print("To deploy to Elastic Cloud, set these in your .env file:")
            print("  - ELASTIC_URL (cloud endpoint)")
            print("  - ELASTIC_API_KEY")
            return 1
        
        print("✓ Cloud deployment detected")
        
        # Step 3: Test cloud connection
        print("\nStep 2: Testing cloud connection...")
        if validate_cloud_config():
            print("\n🎉 Cloud deployment validation successful!")
            print("\nYour pipeline is ready for cloud deployment.")
            print("\nNext steps:")
            print("1. Run a test query: python main.py 'test query'")
            print("2. Check your Elastic Cloud dashboard for indexed data")
            return 0
        else:
            print("\n❌ Cloud connection failed.")
            print("Please check your credentials and try again.")
            return 1
            
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

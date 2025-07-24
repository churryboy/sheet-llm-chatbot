#!/usr/bin/env python3
"""Test script to verify alignment between local and production environments"""

import requests
import json
import sys
from datetime import datetime

def test_api(base_url, env_name):
    """Test API endpoints"""
    print(f"\n{'='*50}")
    print(f"Testing {env_name} Environment: {base_url}")
    print(f"{'='*50}")
    
    # Test health check
    try:
        resp = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"✓ Health Check: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"✗ Health Check Failed: {e}")
        return False
    
    # Test data sources
    try:
        resp = requests.get(f"{base_url}/api/data-sources", timeout=10)
        data = resp.json()
        total = data.get('total', 0)
        sources = data.get('sources', [])
        
        print(f"\n✓ Data Sources API: {resp.status_code}")
        print(f"  Total sources: {total}")
        print(f"  Sources found:")
        for source in sources:
            print(f"    - {source['title']} (GID: {source['gid']}, Default: {source.get('is_default', False)})")
            
        return total, sources
    except Exception as e:
        print(f"✗ Data Sources API Failed: {e}")
        return 0, []

def main():
    """Main test function"""
    print(f"Deployment Alignment Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test local environment
    local_total, local_sources = test_api("http://localhost:8000", "Local")
    
    # Test production environment
    prod_total, prod_sources = test_api("https://sheet-llm-chatbot-backend.onrender.com", "Production")
    
    # Compare results
    print(f"\n{'='*50}")
    print("ALIGNMENT REPORT")
    print(f"{'='*50}")
    
    if local_total == prod_total:
        print(f"✓ Source count matches: {local_total} sources")
    else:
        print(f"✗ Source count mismatch: Local={local_total}, Production={prod_total}")
    
    # Check production frontend
    print(f"\n{'='*50}")
    print("Frontend Check")
    print(f"{'='*50}")
    
    try:
        resp = requests.get("https://qanda-user-gpt.com", timeout=10)
        if "sheet-tabs" in resp.text and "Data sources will be loaded dynamically" in resp.text:
            print("✓ Production frontend updated with dynamic loading")
        else:
            print("✗ Production frontend may not be updated yet")
    except Exception as e:
        print(f"✗ Frontend check failed: {e}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()

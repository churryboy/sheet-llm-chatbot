#!/usr/bin/env python3
import requests

def test_google_docs_fetch(document_id):
    """Test fetching Google Docs content with different headers"""
    export_url = f"https://docs.google.com/document/d/{document_id}/export?format=txt"
    
    # Test 1: Without headers
    print("Test 1: Fetching without custom headers...")
    response1 = requests.get(export_url, allow_redirects=False)
    print(f"Status: {response1.status_code}")
    if response1.status_code in [301, 302, 303, 307, 308]:
        print(f"Redirect to: {response1.headers.get('Location', 'N/A')[:100]}...")
    
    # Test 2: With browser headers
    print("\nTest 2: Fetching with browser headers...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    response2 = requests.get(export_url, headers=headers, allow_redirects=False)
    print(f"Status: {response2.status_code}")
    if response2.status_code in [301, 302, 303, 307, 308]:
        print(f"Redirect to: {response2.headers.get('Location', 'N/A')[:100]}...")
    
    # If successful, check content
    if response2.status_code == 200:
        content = response2.text
        if '<!DOCTYPE html' in content[:100] or '<html' in content[:100]:
            print("Got HTML (likely login page)")
            print(f"First 200 chars: {content[:200]}")
        else:
            print(f"Got text content! Length: {len(content)} characters")
            print(f"First 200 chars: {content[:200]}")
    
    # Test 3: Follow redirects with headers
    print("\nTest 3: Following redirects with browser headers...")
    response3 = requests.get(export_url, headers=headers, allow_redirects=True)
    print(f"Final status: {response3.status_code}")
    print(f"Final URL: {response3.url[:100]}...")
    
    if response3.status_code == 200:
        content = response3.text
        if '<!DOCTYPE html' in content[:100] or '<html' in content[:100]:
            print("Got HTML (likely login page)")
            print(f"First 200 chars: {content[:200]}")
        else:
            print(f"Got text content! Length: {len(content)} characters")
            print(f"First 200 chars: {content[:200]}")

if __name__ == "__main__":
    document_id = "1HRMkP8KjHkQSqjJrq_V1QNXJqJ63JaGE6RSFiY_zBRo"
    print(f"Testing Google Docs fetch for document: {document_id}")
    print("="*60)
    test_google_docs_fetch(document_id)

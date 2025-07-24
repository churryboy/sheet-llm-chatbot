#!/usr/bin/env python3
"""
Test script for Google Search API integration with sheet-llm-chatbot
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_chat_without_web_search():
    """Test basic chat without web search"""
    print("=== Testing Chat WITHOUT Web Search ===")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "question": "학생들의 AI 사용 현황은 어떤가요?",
            "enable_web_search": False
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data['answer'][:200]}...")
        print(f"Sheet data count: {data['data_count']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_chat_with_web_search():
    """Test chat with web search enabled"""
    print("\n=== Testing Chat WITH Web Search ===")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "question": "AI 교육의 최신 트렌드와 우리 학생들의 사용 현황을 비교해주세요",
            "enable_web_search": True
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data['answer'][:200]}...")
        print(f"Sheet data count: {data['data_count']}")
        
        if 'web_search_count' in data:
            print(f"Web search results: {data['web_search_count']}")
            print("\nSearch sources:")
            for source in data.get('search_sources', []):
                print(f"  - {source['title']} ({source['source']})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_specific_search_query():
    """Test with specific search-triggering keywords"""
    print("\n=== Testing Specific Search Query ===")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "question": "LLM 활용 사례와 교육 현황에 대한 최신 정보를 알려주세요",
            "enable_web_search": True
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Sheet data count: {data['data_count']}")
        
        if 'web_search_count' in data:
            print(f"Web search results: {data['web_search_count']}")
            print("\nFull answer:")
            print(data['answer'])
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Testing Google Search API Integration")
    print("=" * 50)
    
    # Run tests
    test_chat_without_web_search()
    test_chat_with_web_search()
    test_specific_search_query()
    
    print("\n" + "=" * 50)
    print("Tests completed!")

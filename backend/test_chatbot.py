#!/usr/bin/env python3
"""Test the chatbot functionality"""

import os
import json
from dotenv import load_dotenv
from app import get_google_sheets_data, create_prompt
from anthropic import Anthropic

# Load environment variables
load_dotenv()

def test_google_sheets():
    """Test Google Sheets data retrieval"""
    print("1. Testing Google Sheets data retrieval...")
    data = get_google_sheets_data()
    
    if data:
        print(f"✅ Successfully retrieved {len(data)} rows")
        print("\nData:")
        for row in data:
            print(f"  - {row}")
        
        # Check for Jane's data
        jane_data = [row for row in data if row.get('Name', '').lower() == 'jane']
        if jane_data:
            print(f"\n✅ Found Jane's data: {jane_data[0]}")
        else:
            print("\n❌ Jane's data not found")
    else:
        print("❌ No data retrieved")
    
    return data

def test_prompt_creation(data):
    """Test prompt creation"""
    print("\n2. Testing prompt creation...")
    question = "what does Jane like?"
    prompt = create_prompt(question, data)
    
    print(f"✅ Prompt created for question: '{question}'")
    print("\nPrompt preview:")
    print("-" * 50)
    print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
    print("-" * 50)
    
    return prompt

def test_claude_api(prompt):
    """Test Claude API"""
    print("\n3. Testing Claude API...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return
    
    try:
        client = Anthropic(api_key=api_key)
        
        print("Sending request to Claude API...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system="당신은 데이터 분석을 도와주는 친절한 어시스턴트입니다. 주어진 데이터를 기반으로 정확하게 답변해주세요.",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.content[0].text
        print("✅ Received response from Claude API")
        print("\nAnswer:")
        print("-" * 50)
        print(answer)
        print("-" * 50)
        
        # Check if the answer mentions iPhone
        if 'iphone' in answer.lower():
            print("\n✅ Answer correctly mentions iPhone!")
        else:
            print("\n⚠️  Answer doesn't mention iPhone - might be an issue")
            
    except Exception as e:
        print(f"❌ Error calling Claude API: {str(e)}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Sheet-LLM Chatbot")
    print("=" * 60)
    
    # Test Google Sheets
    data = test_google_sheets()
    
    if data:
        # Test prompt creation
        prompt = test_prompt_creation(data)
        
        # Test Claude API
        test_claude_api(prompt)
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

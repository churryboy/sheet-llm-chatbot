#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('ANTHROPIC_API_KEY')
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

try:
    # Initialize Claude client
    client = Anthropic(api_key=api_key)
    
    # Test with a simple message
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        system="You are a helpful assistant.",
        messages=[
            {"role": "user", "content": "Say 'Hello, Claude is working!'"}
        ],
        max_tokens=50
    )
    
    print(f"✅ Success! Response: {response.content[0].text}")
    
except Exception as e:
    print(f"❌ Error: {e}")

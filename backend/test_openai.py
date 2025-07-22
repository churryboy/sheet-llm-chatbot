#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

try:
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Test with a simple completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say 'Hello, API is working!'"}
        ],
        max_tokens=20
    )
    
    print(f"✅ Success! Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {e}")

#!/usr/bin/env python3
import requests
import json
import socket

print("=== Backend Connection Diagnostic ===\n")

# Test different possible endpoints
endpoints = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]

test_question = {"question": "중학생은 몇명이야"}

for endpoint in endpoints:
    print(f"\nTesting {endpoint}...")
    try:
        # Test health endpoint first
        health_resp = requests.get(f"{endpoint}/api/health", timeout=2)
        if health_resp.status_code == 200:
            print(f"✓ Health check passed")
            
            # Test chat endpoint
            chat_resp = requests.post(
                f"{endpoint}/api/chat",
                json=test_question,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if chat_resp.status_code == 200:
                data = chat_resp.json()
                answer = data.get('answer', '')
                
                # Extract the count from answer
                import re
                match = re.search(r'총\s*(\d+)명', answer)
                if match:
                    count = match.group(1)
                    print(f"✓ Chat endpoint works - Reports {count} middle school students")
                    
                    # Check for specific grade counts
                    grade_matches = re.findall(r'중(\d):\s*(\d+)명', answer)
                    if grade_matches:
                        total = sum(int(count) for _, count in grade_matches)
                        print(f"  Grade breakdown: {grade_matches} = {total} total")
                else:
                    print(f"✓ Chat endpoint works but couldn't extract count")
                    print(f"  First 100 chars: {answer[:100]}...")
                    
                print(f"  Data count in response: {data.get('data_count', 'N/A')}")
            else:
                print(f"✗ Chat endpoint returned status {chat_resp.status_code}")
        else:
            print(f"✗ Health check failed with status {health_resp.status_code}")
            
    except requests.exceptions.ConnectRefusedError:
        print(f"✗ Connection refused - No server running on this endpoint")
    except requests.exceptions.Timeout:
        print(f"✗ Request timed out")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

# Check what's in browser localStorage/cookies
print("\n\n=== Browser Check Instructions ===")
print("1. Open your browser Developer Tools (F12)")
print("2. Go to the Network tab")
print("3. Clear the network log")
print("4. Ask the question '중학생은 몇명이야' in your app")
print("5. Look for the API call in the Network tab")
print("6. Check:")
print("   - What URL is being called?")
print("   - What's in the Response tab?")
print("   - Are there any failed requests?")
print("\n7. Also check Application/Storage tab:")
print("   - Clear all site data")
print("   - Try again")

# Check environment
print("\n\n=== Environment Check ===")
import os
print(f"Current directory: {os.getcwd()}")
print(f"Python version: {socket.gethostname()}")

# List all listening ports
print("\n=== All listening ports ===")
os.system("lsof -iTCP -sTCP:LISTEN | grep -E '(node|python|Python)' | awk '{print $2, $1, $9}'")

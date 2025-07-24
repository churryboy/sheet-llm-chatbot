import requests
import json

# Test the chat API directly
url = "http://localhost:8000/api/chat"
payload = {
    "question": "GPT를 어떻게 사용하고 있어?",
    "sheet_gid": "187909252",
    "sheet_name": "Sheet1",
    "spreadsheet_id": "1-wkdWGG1aE9yfYNN0GFoIQXRxKTSf0x8ZcltGCgYltI"
}

print("Testing chat API...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse successful!")
        print(f"Answer length: {len(data.get('answer', ''))}")
        print(f"Data count: {data.get('data_count', 0)}")
        print(f"\nFirst 500 chars of answer:")
        print(data.get('answer', '')[:500])
    else:
        print(f"\nError response:")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("\nRequest timed out after 30 seconds!")
except Exception as e:
    print(f"\nError occurred: {type(e).__name__}: {str(e)}")

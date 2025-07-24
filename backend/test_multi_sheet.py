#!/usr/bin/env python3
import requests
import json

# Test the sheets endpoint
print("Testing /api/sheets endpoint:")
response = requests.get("http://localhost:8000/api/sheets")
if response.status_code == 200:
    sheets_data = response.json()
    print(json.dumps(sheets_data, indent=2, ensure_ascii=False))
else:
    print(f"Error: {response.status_code}")

# Test a simple query about sheet distribution
print("\n\nTesting chat endpoint with sheet distribution question:")
chat_data = {
    "question": "전체 데이터는 몇 개의 시트에 어떻게 분포되어 있나요?"
}
response = requests.post("http://localhost:8000/api/chat", json=chat_data)
if response.status_code == 200:
    chat_response = response.json()
    print("Answer:", chat_response['answer'])
    print("Total data count:", chat_response['data_count'])
else:
    print(f"Error: {response.status_code}")
    print(response.text)

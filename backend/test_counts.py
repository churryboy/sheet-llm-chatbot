#!/usr/bin/env python3
import requests
import json
import time

# Test different counting questions
test_questions = [
    "현재 데이터 총 몇명의 응답이 들어가있어?",
    "중학생은 몇명이야",
    "중학생은 몇명이야?",
    "중1,중2,중3 숫자의 합은 얼마야",
    "고등학생은 몇명이야?",
    "전체 응답자 수는?"
]

print("Testing student counting API...")
print("=" * 50)

for question in test_questions:
    print(f"\nQuestion: {question}")
    
    response = requests.post('http://localhost:8000/api/chat', 
                           json={'question': question})
    
    if response.status_code == 200:
        data = response.json()
        answer = data['answer']
        # Extract numbers from the answer
        import re
        numbers = re.findall(r'총\s*(\d+)명', answer)
        if numbers:
            print(f"Total count found: {numbers[0]}")
        
        # Look for grade-specific counts
        middle_grades = re.findall(r'중(\d):\s*(\d+)명', answer)
        if middle_grades:
            print("Middle school breakdown:")
            total_middle = 0
            for grade, count in middle_grades:
                print(f"  중{grade}: {count}명")
                total_middle += int(count)
            print(f"  Total middle school: {total_middle}")
            
        # Show first 200 chars of answer
        print(f"Answer preview: {answer[:200]}...")
    else:
        print(f"Error: {response.status_code}")
    
    time.sleep(0.5)  # Small delay between requests

# Also check the demographics endpoint
print("\n" + "=" * 50)
print("Demographics endpoint check:")
demo_response = requests.get('http://localhost:8000/api/demographics')
if demo_response.status_code == 200:
    demo_data = demo_response.json()
    print(f"Total count: {demo_data['total_count']}")
    print(f"Middle school: {demo_data['school_year'].get('중학생', 0)}%")
    print(f"High school: {demo_data['school_year'].get('고등학생', 0)}%")

#!/usr/bin/env python3
import requests
import json

# Get the prompt for counting question
response = requests.post('http://localhost:8000/api/chat', 
                        json={'question': '현재 데이터 총 몇명의 응답이 들어가있어?'})

# Save the full response
with open('debug_response.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=2)

# Now let's manually create the prompt to see what's being sent
from app import get_google_sheets_data, create_prompt

sheet_data = get_google_sheets_data()
print(f"Total rows in sheet_data: {len(sheet_data)}")

# Create prompt
prompt = create_prompt('현재 데이터 총 몇명의 응답이 들어가있어?', sheet_data)

# Save prompt to file
with open('debug_prompt.txt', 'w', encoding='utf-8') as f:
    f.write(prompt)

# Count lines in the table section
lines = prompt.split('\n')
table_lines = []
in_table = False
for line in lines:
    if '이름을 적어주세요 | 성별이 어떻게 되나요? | 현재 학년이 어떻게 되나요? | 현재 거주중인 지역이 어디인가요?' in line:
        in_table = True
        continue
    if in_table and line.startswith('==='):
        break
    if in_table and '|' in line and not line.startswith('-'):
        table_lines.append(line)

print(f"Number of table rows shown: {len(table_lines)}")
print(f"First 5 table rows:")
for i, row in enumerate(table_lines[:5]):
    print(f"{i+1}: {row[:100]}...")
    
print(f"\nLast 5 table rows:")
for i, row in enumerate(table_lines[-5:]):
    print(f"{len(table_lines)-4+i}: {row[:100]}...")

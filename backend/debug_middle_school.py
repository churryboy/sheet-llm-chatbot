#!/usr/bin/env python3
from app import get_google_sheets_data, create_prompt
import json

# Get data
sheet_data = get_google_sheets_data()
print(f"Total rows: {len(sheet_data)}")

# Count middle school students manually
middle_count = 0
grade_counts = {'중1': 0, '중2': 0, '중3': 0}
for row in sheet_data:
    grade = row.get('현재 학년이 어떻게 되나요?', '').strip()
    if grade in ['중1', '중2', '중3']:
        middle_count += 1
        grade_counts[grade] += 1

print(f"\nManual count of middle school students:")
print(f"Total: {middle_count}")
for grade, count in grade_counts.items():
    print(f"{grade}: {count}")

# Create prompt
question = "중학생은 몇명이야"
prompt = create_prompt(question, sheet_data)

# Save prompt to file
with open('debug_prompt_middle.txt', 'w', encoding='utf-8') as f:
    f.write(prompt)

# Find key sections in the prompt
lines = prompt.split('\n')
for i, line in enumerate(lines):
    if '총 응답자 수:' in line:
        print(f"\nFound total count at line {i}: {line}")
    if '중학생:' in line and '명' in line:
        print(f"Found middle school count at line {i}: {line}")
    if '[중학생 데이터만 표시' in line:
        print(f"Found filtered data marker at line {i}: {line}")
        if i + 1 < len(lines):
            print(f"Next line: {lines[i+1]}")

# Count table rows
table_rows = 0
in_table = False
for line in lines:
    if '이름을 적어주세요 | 성별이 어떻게 되나요? | 현재 학년이 어떻게 되나요?' in line:
        in_table = True
        continue
    if in_table and ('===' in line or '---' in line):
        if '---' not in line:  # Don't count the separator line
            break
    if in_table and '|' in line and '---' not in line:
        table_rows += 1

print(f"\nTable rows displayed: {table_rows}")

# Check what the demographics endpoint returns
import requests
demo_resp = requests.get('http://localhost:8000/api/demographics')
if demo_resp.status_code == 200:
    demo_data = demo_resp.json()
    print(f"\nDemographics API:")
    print(f"Total: {demo_data['total_count']}")
    print(f"Middle school %: {demo_data['school_year'].get('중학생', 0)}")
    print(f"Calculated middle school count: {int(demo_data['total_count'] * demo_data['school_year'].get('중학생', 0) / 100)}")

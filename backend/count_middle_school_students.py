#!/usr/bin/env python3
import requests
import json

# Fetch the debug data
response = requests.get('http://localhost:8000/api/debug/sheet-data')
data = response.json()

# Get all names and count middle school students
all_names = data.get('all_names', [])
print(f"Total students in sheet: {data.get('data_count', 0)}")

# Fetch demographics data to get the breakdown
demo_response = requests.get('http://localhost:8000/api/demographics')
demo_data = demo_response.json()

print(f"\nSchool year breakdown:")
for grade, percentage in demo_data.get('school_year', {}).items():
    count = round(percentage * data.get('data_count', 0) / 100)
    print(f"- {grade}: {percentage}% ({count} students)")

# Now let's directly count middle school students from the raw data
print("\nDirect count of middle school students:")

# Get the full sheet data via CSV
csv_url = f"https://docs.google.com/spreadsheets/d/1-wkdWGG1aE9yfYNN0GFoIQXRxKTSf0x8ZcltGCgYltI/export?format=csv&gid=187909252"
csv_response = requests.get(csv_url)
csv_response.encoding = 'utf-8'

import csv
import io

csv_data = csv.reader(io.StringIO(csv_response.text))
rows = list(csv_data)

# Find the grade column
headers = rows[0]
grade_col_index = None
name_col_index = None

print("\nColumn headers:")
for i, header in enumerate(headers):
    print(f"{i}: {header}")
    if '학년' in header:
        grade_col_index = i
        print(f"  -> Found grade column at index {i}")
    if '이름을 적어주세요' in header:  # More specific match for student name
        name_col_index = i
        print(f"  -> Found name column at index {i}")

if grade_col_index is not None:
    middle_school_grades = ['중1', '중2', '중3']
    middle_school_students = {'중1': [], '중2': [], '중3': []}
    
    for row in rows[1:]:
        if row and len(row) > grade_col_index:
            grade = row[grade_col_index].strip()
            name = row[name_col_index].strip() if name_col_index is not None and len(row) > name_col_index else 'Unknown'
            
            if grade in middle_school_grades:
                middle_school_students[grade].append(name)
    
    total_middle = 0
    for grade, students in middle_school_students.items():
        print(f"\n{grade}: {len(students)} students")
        if len(students) <= 20:  # Only print names if not too many
            print(f"Names: {', '.join(students)}")
        total_middle += len(students)
    
    print(f"\nTotal middle school students: {total_middle}")
    
    # Compare with the demographics API result
    expected_middle = round(demo_data.get('school_year', {}).get('중학생', 0) * data.get('data_count', 0) / 100)
    print(f"Expected from demographics API: {expected_middle}")
    
    if total_middle != expected_middle:
        print(f"\n⚠️  DISCREPANCY: Direct count ({total_middle}) != Demographics API count ({expected_middle})")

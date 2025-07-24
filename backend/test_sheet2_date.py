#!/usr/bin/env python3
import requests
import json
from datetime import datetime

# Get sheet data through our API
response = requests.get('http://localhost:8000/api/debug/sheet-data')
all_data = response.json()

# Now get the actual sheet data
sheet_data_response = requests.post('http://localhost:8000/api/chat', 
                                   json={'question': 'test'})

# Get raw sheet data
import sys
sys.path.append('.')
from app import get_google_sheets_data

sheet_data = get_google_sheets_data()

# Group by sheet
sheet_grouped = {}
for row in sheet_data:
    sheet_name = row.get('_sheet_name', 'Unknown')
    if sheet_name not in sheet_grouped:
        sheet_grouped[sheet_name] = []
    sheet_grouped[sheet_name].append(row)

print(f"Total sheets found: {len(sheet_grouped)}")
print(f"Sheet names: {list(sheet_grouped.keys())}")

# Check Sheet2 specifically
if 'Sheet2' in sheet_grouped:
    sheet2_data = sheet_grouped['Sheet2']
    print(f"\nSheet2 has {len(sheet2_data)} rows")
    
    # Check first few rows for timestamps
    print("\nFirst 3 rows of Sheet2 timestamps:")
    for i, row in enumerate(sheet2_data[:3]):
        timestamp = row.get('Submitted At', 'NO TIMESTAMP')
        print(f"  Row {i+1}: {timestamp}")
    
    # Try to parse the date
    if sheet2_data:
        timestamp_str = sheet2_data[0].get('Submitted At', '')
        print(f"\nParsing timestamp: '{timestamp_str}'")
        
        if timestamp_str:
            # Try Korean format
            if '오전' in timestamp_str or '오후' in timestamp_str:
                try:
                    date_part = timestamp_str.split(' 오')[0].strip()
                    print(f"Korean format detected, date part: '{date_part}'")
                    date_obj = datetime.strptime(date_part, '%Y. %m. %d')
                    print(f"Parsed date: {date_obj.year}년 {date_obj.month}월")
                except Exception as e:
                    print(f"Failed to parse Korean format: {e}")
else:
    print("Sheet2 not found!")

# Also check the process_sheet_data function behavior
print("\n\nChecking the sheet processing...")
from app import process_sheet_data

for sheet_name, rows in sheet_grouped.items():
    print(f"\nProcessing {sheet_name}...")
    # Get date for this sheet
    sheet_date = None
    if rows:
        timestamp_str = rows[0].get('Submitted At', '')
        if timestamp_str:
            try:
                if '오전' in timestamp_str or '오후' in timestamp_str:
                    date_part = timestamp_str.split(' 오')[0].strip()
                    date_obj = datetime.strptime(date_part, '%Y. %m. %d')
                    sheet_date = f"{date_obj.year}년 {date_obj.month}월"
            except:
                pass
    
    print(f"Date for {sheet_name}: {sheet_date}")
    
    # Process with a test question
    summary = process_sheet_data(sheet_name, rows[:5], "종합적인 분석을 해줘", sheet_date)
    if summary:
        print(f"Summary preview: {summary[:200]}...")

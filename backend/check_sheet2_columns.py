#!/usr/bin/env python3
import sys
sys.path.append('.')
from app import get_sheet_data_by_gid

# Get Sheet2 data directly
sheet2_data = get_sheet_data_by_gid('2040429429', 'Sheet2')

if sheet2_data:
    print(f"Sheet2 has {len(sheet2_data)} rows")
    print(f"\nColumn names in Sheet2:")
    
    # Get all unique column names
    all_columns = set()
    for row in sheet2_data:
        all_columns.update(row.keys())
    
    # Sort and display
    sorted_columns = sorted(list(all_columns))
    for i, col in enumerate(sorted_columns):
        print(f"{i+1}. {col}")
    
    # Check if there's any timestamp-related column
    print("\n\nPossible timestamp columns:")
    timestamp_keywords = ['time', 'date', 'submit', 'timestamp', '날짜', '시간', '제출']
    for col in sorted_columns:
        if any(keyword in col.lower() for keyword in timestamp_keywords):
            print(f"  - {col}")
            # Show sample values
            sample_values = []
            for row in sheet2_data[:3]:
                if col in row and row[col]:
                    sample_values.append(row[col])
            if sample_values:
                print(f"    Sample values: {sample_values}")
    
    # Show first row's data
    print("\n\nFirst row data:")
    first_row = sheet2_data[0]
    for key, value in first_row.items():
        if value and key != '_sheet_name':  # Only show non-empty values
            print(f"  {key}: {value[:50]}..." if len(str(value)) > 50 else f"  {key}: {value}")
else:
    print("No data found for Sheet2")

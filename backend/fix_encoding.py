#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility script to check and fix Korean text encoding issues
"""

import requests
import csv
import io
import json
from urllib.parse import unquote

def check_encoding_issues(text):
    """Check if text has encoding issues"""
    if not text:
        return False, text
    
    # Common encoding issue patterns
    encoding_patterns = [
        ('\\uc800\\ub3d9\\uace0\\ub4f1\\ud559\\uad50', '저동고등학교'),
        ('\\u00ec\\u00a0\\u0080\\u00eb\\u008f\\u0099\\u00ea\\u00b3\\u00a0\\u00eb\\u0093\\u00b1\\u00ed\\u0095\\u0099\\u00ea\\u00b5\\u0090', '저동고등학교'),
    ]
    
    for pattern, correct in encoding_patterns:
        if pattern in text:
            return True, text.replace(pattern, correct)
    
    # Try to detect mojibake (incorrectly decoded text)
    try:
        # Check if text contains unusual unicode characters
        if any(ord(c) > 0x7F and ord(c) < 0xA0 for c in text):
            # Try to fix by encoding to latin-1 and decoding as utf-8
            fixed = text.encode('latin-1').decode('utf-8', errors='ignore')
            if fixed != text:
                return True, fixed
    except:
        pass
    
    # Check for URL-encoded Korean text
    if '%' in text:
        try:
            decoded = unquote(text)
            if decoded != text:
                return True, decoded
        except:
            pass
    
    return False, text

def fix_csv_encoding(csv_url):
    """Download CSV and check for encoding issues"""
    print(f"Downloading CSV from: {csv_url}")
    
    response = requests.get(csv_url)
    response.encoding = 'utf-8'
    
    # Parse CSV
    csv_data = csv.reader(io.StringIO(response.text))
    rows = list(csv_data)
    
    if not rows:
        print("No data found in CSV")
        return
    
    headers = rows[0]
    print(f"Headers: {headers}")
    
    # Check each row for encoding issues
    issues_found = []
    for i, row in enumerate(rows[1:], 1):
        for j, cell in enumerate(row):
            has_issue, fixed = check_encoding_issues(cell)
            if has_issue:
                issues_found.append({
                    'row': i,
                    'column': headers[j] if j < len(headers) else f'Column {j}',
                    'original': cell,
                    'fixed': fixed
                })
    
    if issues_found:
        print(f"\nFound {len(issues_found)} encoding issues:")
        for issue in issues_found:
            print(f"\nRow {issue['row']}, Column '{issue['column']}':")
            print(f"  Original: {issue['original']}")
            print(f"  Fixed: {issue['fixed']}")
    else:
        print("\nNo encoding issues found!")
    
    # Look for specific text
    print("\nSearching for '저동고등학교'...")
    found = False
    for i, row in enumerate(rows[1:], 1):
        for j, cell in enumerate(row):
            if '저동고등학교' in cell or 'jeodong' in cell.lower():
                print(f"Found in Row {i}, Column '{headers[j] if j < len(headers) else f'Column {j}'}':")
                print(f"  Value: {cell}")
                found = True
    
    if not found:
        print("Text '저동고등학교' not found in the data")
    
    return issues_found

def main():
    # Your Google Sheets CSV export URL
    SPREADSHEET_ID = '1-wkdWGG1aE9yfYNN0GFoIQXRxKTSf0x8ZcltGCgYltI'
    csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=516851124"
    
    print("Checking Google Sheets data for encoding issues...\n")
    issues = fix_csv_encoding(csv_url)
    
    if issues:
        print("\n" + "="*50)
        print("RECOMMENDATION:")
        print("1. Open your Google Sheets")
        print("2. Use Find & Replace (Ctrl+H or Cmd+H)")
        print("3. Replace the incorrectly encoded text with the fixed version")
        print("4. Or manually edit the affected cells")
        print("="*50)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from app import get_google_sheets_data

sheet_data = get_google_sheets_data()
print(f"Total rows: {len(sheet_data)}")

# Count rows with complete essential data
essential_fields = ['이름을 적어주세요', '성별이 어떻게 되나요?', '현재 학년이 어떻게 되나요?', '현재 거주중인 지역이 어디인가요? ']

complete_rows = 0
incomplete_rows = 0
rows_with_name_only = 0

for i, row in enumerate(sheet_data):
    name = row.get('이름을 적어주세요', '').strip()
    gender = row.get('성별이 어떻게 되나요?', '').strip()
    grade = row.get('현재 학년이 어떻게 되나요?', '').strip()
    location = row.get('현재 거주중인 지역이 어디인가요? ', '').strip()
    
    if all([name, gender, grade, location]):
        complete_rows += 1
    else:
        incomplete_rows += 1
        if name and not any([gender, grade, location]):
            rows_with_name_only += 1
        
        # Show first few incomplete rows
        if incomplete_rows <= 5:
            print(f"\nRow {i+1} - Incomplete:")
            print(f"  Name: '{name}'")
            print(f"  Gender: '{gender}'")
            print(f"  Grade: '{grade}'")
            print(f"  Location: '{location}'")

print(f"\nSummary:")
print(f"- Complete rows (all 4 fields): {complete_rows}")
print(f"- Incomplete rows: {incomplete_rows}")
print(f"  - Rows with name only: {rows_with_name_only}")
print(f"- Total: {complete_rows + incomplete_rows}")

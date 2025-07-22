#!/usr/bin/env python3
"""Test script to verify Google Sheets connection"""

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

SPREADSHEET_ID = '17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ'
RANGE_NAME = 'A:B'

def test_sheets_connection():
    """Test connection to Google Sheets"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key or api_key == 'your_google_api_key_here':
        print("❌ Error: GOOGLE_API_KEY not set in .env file")
        print("Please add your Google API key to the .env file")
        return False
    
    try:
        # Build the service
        service = build('sheets', 'v4', developerKey=api_key)
        
        # Try to read the sheet
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("⚠️  Sheet is empty")
            return True
        
        print(f"✅ Successfully connected to Google Sheets!")
        print(f"📊 Found {len(values)} rows of data")
        print("\nFirst few rows:")
        for i, row in enumerate(values[:5]):
            print(f"  Row {i+1}: {row}")
        
        # Check specifically for Jane's data
        print("\n🔍 Looking for Jane's data...")
        for row in values:
            if len(row) > 0 and 'Jane' in str(row[0]):
                print(f"  Found: {row}")
        
        return True
        
    except HttpError as error:
        print(f"❌ HTTP Error: {error}")
        if error.resp.status == 403:
            print("\nPossible issues:")
            print("1. The Google Sheets API might not be enabled for your project")
            print("2. The spreadsheet might not be publicly accessible")
            print("3. The API key might not have the correct permissions")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Google Sheets connection...")
    print(f"Spreadsheet ID: {SPREADSHEET_ID}")
    print(f"Range: {RANGE_NAME}")
    print("-" * 50)
    
    if test_sheets_connection():
        print("\n✅ Test passed! Your Google Sheets integration should work.")
    else:
        print("\n❌ Test failed. Please check the errors above.")

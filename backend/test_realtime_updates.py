#!/usr/bin/env python3
"""Test real-time updates from Google Sheets"""

import time
from app import get_google_sheets_data

def monitor_sheet_changes(interval=5):
    """Monitor Google Sheets for changes"""
    print("🔄 Monitoring Google Sheets for changes...")
    print(f"Checking every {interval} seconds")
    print("Press Ctrl+C to stop\n")
    
    last_data = None
    check_count = 0
    
    try:
        while True:
            check_count += 1
            print(f"\n--- Check #{check_count} ---")
            
            # Get current data
            current_data = get_google_sheets_data()
            
            if current_data:
                print(f"✅ Retrieved {len(current_data)} rows")
                
                # Check if data has changed
                if last_data is None:
                    print("🆕 Initial data load:")
                    # Show headers
                    if current_data:
                        headers = list(current_data[0].keys())
                        print(f"Columns: {headers}")
                        print(f"\nFirst row: {current_data[0]}")
                        if len(current_data) > 1:
                            print(f"Last row: {current_data[-1]}")
                
                elif current_data != last_data:
                    print("🔔 DATA CHANGED!")
                    
                    # Find what changed
                    if len(current_data) != len(last_data):
                        print(f"Row count changed: {len(last_data)} → {len(current_data)}")
                    
                    # Show new data
                    print("\nUpdated data:")
                    if current_data:
                        print(f"First row: {current_data[0]}")
                        if len(current_data) > 1:
                            print(f"Last row: {current_data[-1]}")
                
                else:
                    print("No changes detected")
                
                # Check for Taehee's data
                taehee_data = [row for row in current_data if 'Taehee' in str(row.get('Name', ''))]
                if taehee_data:
                    print(f"\n📌 Found Taehee's data: {taehee_data[0]}")
                
                last_data = current_data
            else:
                print("❌ No data retrieved")
            
            # Wait before next check
            print(f"\nWaiting {interval} seconds...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")

if __name__ == "__main__":
    print("=" * 60)
    print("Google Sheets Real-time Update Monitor")
    print("=" * 60)
    print("\nThis will check your Google Sheet every few seconds")
    print("to detect any changes you make.\n")
    
    monitor_sheet_changes(interval=5)

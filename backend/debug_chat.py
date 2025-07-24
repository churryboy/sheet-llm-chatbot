import json
from app import get_sheet_data_by_gid, create_prompt, load_data_sources, SPREADSHEET_ID

# Test the chat functionality
def debug_chat():
    # Test question
    test_question = "GPT를 어떻게 사용하고 있어?"
    
    # Get the first data source
    sources = load_data_sources()
    
    # Test with default sheet first
    print("Testing with default Sheet1...")
    sheet_data = get_sheet_data_by_gid('187909252', 'Sheet1', SPREADSHEET_ID)
    print(f"Loaded {len(sheet_data)} rows from Sheet1")
    
    if sheet_data:
        # Create prompt
        prompt = create_prompt(test_question, sheet_data)
        print(f"\nPrompt length: {len(prompt):,} characters")
        print(f"Estimated tokens: {len(prompt)/4:,.0f}")
        
        # Check if MAX_ROWS limiting is in the prompt
        if '[데이터 샘플 -' in prompt:
            sample_idx = prompt.find('[데이터 샘플 -')
            print(f"\nData limiting found at position {sample_idx}")
            print(prompt[sample_idx:sample_idx+100])
        else:
            print("\nWARNING: Data limiting header NOT found!")
            
        # Check prompt structure
        if '=== 구글 시트 데이터 ===' in prompt:
            print("\n✓ Data section found")
        if '[사용 가능한 모든 컬럼 목록]' in prompt:
            print("✓ Column list found")
        if '[분석 지침]' in prompt:
            print("✓ Analysis instructions found")
            
        # Show last 500 chars to see instructions
        print(f"\nLast 500 characters of prompt:")
        print(prompt[-500:])
        
    # Also test with custom source if available
    if sources:
        print(f"\n\nTesting with custom source: {sources[0]['title']}...")
        custom_data = get_sheet_data_by_gid(sources[0]['gid'], sources[0]['title'], sources[0]['spreadsheet_id'])
        print(f"Loaded {len(custom_data)} rows")
        
        if custom_data:
            custom_prompt = create_prompt(test_question, custom_data)
            print(f"Custom prompt length: {len(custom_prompt):,} characters")
            print(f"Estimated tokens: {len(custom_prompt)/4:,.0f}")

if __name__ == "__main__":
    debug_chat()

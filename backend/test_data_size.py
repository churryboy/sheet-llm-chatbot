import json
from app import get_sheet_data_by_gid, create_prompt, load_data_sources

# Test the data size being loaded
def test_data_size():
    # Load custom data sources
    sources = load_data_sources()
    
    if sources:
        # Test with the first custom source
        source = sources[0]
        print(f"Testing with source: {source['title']}")
        print(f"Spreadsheet ID: {source['spreadsheet_id']}")
        print(f"GID: {source['gid']}")
        
        # Get the data
        data = get_sheet_data_by_gid(source['gid'], source['title'], source['spreadsheet_id'])
        print(f"\nTotal rows loaded: {len(data)}")
        
        if data:
            # Check columns
            columns = list(data[0].keys())
            print(f"Number of columns: {len(columns)}")
            
            # Check data size
            total_chars = 0
            for row in data:
                for col, value in row.items():
                    total_chars += len(str(value))
            
            print(f"Total characters in data: {total_chars:,}")
            print(f"Average chars per row: {total_chars/len(data):,.0f}")
            
            # Test create_prompt function
            test_question = "GPT를 어떻게 사용하고 있어?"
            prompt = create_prompt(test_question, data)
            print(f"\nPrompt length: {len(prompt):,} characters")
            print(f"Estimated tokens (chars/4): {len(prompt)/4:,.0f}")
            
            # Show first 500 chars of prompt
            print("\nFirst 500 characters of prompt:")
            print(prompt[:500])
            print("...")
            
            # Check if the data limiting is working
            if '[데이터 샘플 -' in prompt:
                sample_start = prompt.find('[데이터 샘플 -')
                sample_line = prompt[sample_start:sample_start+100]
                print(f"\nData sample line found: {sample_line}")
            else:
                print("\nWARNING: Data sample header not found in prompt!")

if __name__ == "__main__":
    test_data_size()

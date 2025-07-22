import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from anthropic import Anthropic
from dotenv import load_dotenv
import json
import requests
import csv
import io

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Korean text support
CORS(app)  # CORS 설정으로 프론트엔드와 통신 가능

# Claude (Anthropic) 클라이언트 초기화
try:
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_api_key:
        client = Anthropic(api_key=anthropic_api_key)
    else:
        client = None
        print("Warning: ANTHROPIC_API_KEY not found")
except Exception as e:
    print(f"Error initializing Anthropic client: {str(e)}")
    client = None

# Google Sheets API 설정
SPREADSHEET_ID = '1-wkdWGG1aE9yfYNN0GFoIQXRxKTSf0x8ZcltGCgYltI'
RANGE_NAME = 'Sheet1!A:Z'  # Sheet1의 모든 열 읽기

def get_google_sheets_data():
    """구글 시트에서 데이터를 가져오는 함수"""
    try:
        # 캐시 방지를 위해 timestamp 추가
        import time
        timestamp = int(time.time())
        
        # 먼저 CSV 내보내기 URL로 시도 (공개 시트인 경우 가장 간단)
        # Using gid=516851124 for the specific sheet tab
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=516851124&timestamp={timestamp}"
        
        # 캐시 방지 헤더 추가
        headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        response = requests.get(csv_url, headers=headers)
        
        if response.status_code == 200:
            # Ensure proper UTF-8 encoding
            response.encoding = 'utf-8'
            
            # CSV 데이터 파싱
            csv_data = csv.reader(io.StringIO(response.text))
            rows = list(csv_data)
            
            if not rows:
                return []
            
            # 첫 번째 행을 헤더로 사용
            headers = rows[0]
            data = []
            
            for row in rows[1:]:
                if row:  # 빈 행 제외
                    row_dict = {}
                    for i, header in enumerate(headers):
                        row_dict[header] = row[i] if i < len(row) else ''
                    data.append(row_dict)
            
            print(f"Successfully retrieved {len(data)} rows from Google Sheets (via CSV)")
            if data:
                print(f"Headers found: {headers}")
                print(f"Total columns: {len(headers)}")
            return data
        
        # CSV 접근이 실패하면 API 시도
        # 서비스 계정 키 파일이 있는 경우
        if os.path.exists('credentials.json'):
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            service = build('sheets', 'v4', credentials=credentials)
        else:
            # API 키 사용 (공개 시트인 경우)
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key and api_key != 'your_google_api_key_here':
                service = build('sheets', 'v4', developerKey=api_key)
            else:
                print("Warning: No Google API credentials found")
                return []
        
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return []
        
        # 첫 번째 행을 헤더로 사용
        headers = values[0]
        data = []
        
        for row in values[1:]:
            if row:  # 빈 행 제외
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ''
                data.append(row_dict)
        
        print(f"Successfully retrieved {len(data)} rows from Google Sheets (via API)")
        return data
    
    except Exception as e:
        print(f"Error reading Google Sheets: {str(e)}")
        return []

def create_prompt(user_question, sheet_data):
    """사용자 질문과 시트 데이터를 결합하여 프롬프트 생성"""
    data_str = "다음은 구글 시트의 데이터입니다:\n\n"
    
    if sheet_data:
        # 헤더 확인
        headers = list(sheet_data[0].keys())
        
        # 인터뷰 스크립트나 긴 텍스트가 있는지 확인
        has_long_text = any('interview' in h.lower() or 'script' in h.lower() 
                           or any(len(str(row.get(h, ''))) > 200 for row in sheet_data) 
                           for h in headers)
        
        if has_long_text:
            # 긴 텍스트가 있는 경우 다른 형식으로 표시
            for i, row in enumerate(sheet_data, 1):
                data_str += f"\n=== 데이터 #{i} ===\n"
                for header in headers:
                    value = str(row.get(header, ''))
                    if value:
                        if len(value) > 200:
                            # 긴 텍스트는 별도로 표시
                            data_str += f"\n[{header}]:\n{value[:500]}...\n(총 {len(value)}자)\n"
                        else:
                            data_str += f"{header}: {value}\n"
                data_str += "\n"
        else:
            # 짧은 데이터는 테이블 형식으로
            data_str += " | ".join(headers) + "\n"
            data_str += "-" * 50 + "\n"
            
            for row in sheet_data:
                row_values = [str(row.get(header, ''))[:50] for header in headers]
                data_str += " | ".join(row_values) + "\n"
    else:
        data_str += "데이터가 없습니다.\n"
    
    prompt = f"""
{data_str}

위 데이터를 참고하여 다음 질문에 답해주세요:
질문: {user_question}

주의사항:
1. 데이터에 인터뷰 스크립트나 대화 내용이 있다면, 해당 내용을 꼼꼼히 분석하여 답변하세요.
2. 사람의 이름이 언급되면, 해당 인물과 관련된 모든 정보를 종합하여 답변하세요.
3. 답변은 친절하고 상세하게 작성해주세요.
4. 데이터를 기반으로 정확한 정보를 제공하고, 필요한 경우 추가적인 분석이나 인사이트도 제공하세요.
"""
    
    return prompt

@app.route('/api/chat', methods=['POST'])
def chat():
    """사용자 질문을 받아 LLM 응답을 반환하는 API"""
    try:
        data = request.json
        user_question = data.get('question', '')
        
        if not user_question:
            return jsonify({'error': '질문을 입력해주세요.'}), 400
        
        # 구글 시트 데이터 가져오기
        sheet_data = get_google_sheets_data()
        
        # 프롬프트 생성
        prompt = create_prompt(user_question, sheet_data)
        
        # 디버깅을 위해 데이터 출력
        print(f"Sheet data retrieved: {len(sheet_data)} rows")
        if sheet_data:
            print(f"First row: {sheet_data[0]}")
        
        # Claude API 호출
        if not client:
            return jsonify({'error': 'Claude API가 설정되지 않았습니다. ANTHROPIC_API_KEY를 확인해주세요.'}), 500
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system="당신은 데이터 분석을 도와주는 친절한 어시스턴트입니다. 주어진 데이터를 기반으로 정확하게 답변해주세요.",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.content[0].text
        
        return jsonify({
            'answer': answer,
            'data_count': len(sheet_data)
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({'status': 'ok'})

@app.route('/api/debug/sheet-data', methods=['GET'])
def debug_sheet_data():
    """디버그용: 현재 시트 데이터 확인"""
    try:
        sheet_data = get_google_sheets_data()
        return jsonify({
            'spreadsheet_id': SPREADSHEET_ID,
            'range': RANGE_NAME,
            'data_count': len(sheet_data),
            'headers': list(sheet_data[0].keys()) if sheet_data else [],
            'first_row': sheet_data[0] if sheet_data else None,
            'all_names': [row.get('이름을 적어주세요', row.get('이름', row.get('Name', ''))) for row in sheet_data] if sheet_data else []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

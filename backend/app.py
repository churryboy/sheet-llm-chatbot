import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from json_unicode import jsonify_unicode
from functools import wraps
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from anthropic import Anthropic
from dotenv import load_dotenv
import json
import requests
import csv
import io
import pickle
from datetime import datetime

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# Google Custom Search API 설정
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# Force UTF-8 and disable ASCII-only JSON
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_ENSURE_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# Also check environment variable
if os.environ.get('PYTHONIOENCODING') != 'utf-8':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# CORS 설정 - 더 명시적으로 설정
CORS(app, origins=[
    'http://localhost:3000', 
    'http://127.0.0.1:3000', 
    'https://user-gpt-chatbot.vercel.app',
    'https://*.vercel.app',
    'https://qanda-user-gpt.com',
    'https://www.qanda-user-gpt.com',
    'file://*'
], 
     allow_headers=['Content-Type', 'Accept'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

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
DEFAULT_SHEET_GID = '187909252'  # Sheet1's GID

# Custom data sources file
DATA_SOURCES_FILE = os.path.join(os.path.dirname(__file__), 'data_sources.json')

# Load custom data sources
def load_data_sources():
    """Load custom data sources from file"""
    print(f"[DEBUG] Loading data sources from: {DATA_SOURCES_FILE}")
    print(f"[DEBUG] File exists: {os.path.exists(DATA_SOURCES_FILE)}")
    if os.path.exists(DATA_SOURCES_FILE):
        try:
            with open(DATA_SOURCES_FILE, 'r', encoding='utf-8') as f:
                sources = json.load(f)
                print(f"[DEBUG] Loaded {len(sources)} custom sources")
                return sources
        except Exception as e:
            print(f"Error loading data sources: {e}")
    print(f"[DEBUG] No custom sources found")
    return []

def extract_interview_description(content):
    """Extract a brief description of the interview content (max 4 sentences)"""
    lines = content.split('\n')
    
    # Look for key topics discussed in the interview
    topics = []
    keywords = {
        'GPT': 'AI/GPT 활용',
        'LLM': 'LLM 서비스',
        '공부': '학습 방법',
        '수학': '수학 학습',
        '과외': '과외',
        '학원': '학원',
        '예체능': '예체능',
        '대학': '대학 진학',
        '시험': '시험',
        '성적': '성적',
        'ChatGPT': 'ChatGPT',
        '인공지능': 'AI',
        '학습': '학습',
        '교육': '교육'
    }
    
    # Count keyword occurrences
    keyword_counts = {}
    for line in lines:
        for keyword, topic in keywords.items():
            if keyword in line:
                keyword_counts[topic] = keyword_counts.get(topic, 0) + 1
    
    # Get top topics
    if keyword_counts:
        sorted_topics = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        topics = [topic for topic, _ in sorted_topics[:3]]
    
    # Extract participant count and grades
    participant_grades = []
    for line in lines:
        if '고1' in line or '고등학교 1학년' in line:
            if '고1' not in participant_grades:
                participant_grades.append('고1')
        elif '고2' in line or '고등학교 2학년' in line:
            if '고2' not in participant_grades:
                participant_grades.append('고2')
        elif '고3' in line or '고등학교 3학년' in line:
            if '고3' not in participant_grades:
                participant_grades.append('고3')
        elif '중1' in line or '중학교 1학년' in line:
            if '중1' not in participant_grades:
                participant_grades.append('중1')
        elif '중2' in line or '중학교 2학년' in line:
            if '중2' not in participant_grades:
                participant_grades.append('중2')
        elif '중3' in line or '중학교 3학년' in line:
            if '중3' not in participant_grades:
                participant_grades.append('중3')
    
    # Build description
    description_parts = []
    
    # First sentence: participant info
    if participant_grades:
        grades_str = ', '.join(participant_grades)
        description_parts.append(f"{grades_str} 학생들을 대상으로 진행된 인터뷰입니다.")
    else:
        description_parts.append("학생들을 대상으로 진행된 인터뷰입니다.")
    
    # Second sentence: main topics
    if topics:
        topics_str = ', '.join(topics[:3])
        description_parts.append(f"주요 주제는 {topics_str} 등입니다.")
    
    # Third sentence: Look for specific content patterns
    if 'GPT' in content or 'ChatGPT' in content or 'LLM' in content:
        if '수학' in content:
            description_parts.append("AI 도구를 활용한 수학 학습 경험에 대해 논의했습니다.")
        else:
            description_parts.append("AI 학습 도구 사용 경험에 대해 논의했습니다.")
    elif '학원' in content or '과외' in content:
        description_parts.append("사교육 경험과 학습 방법에 대해 이야기했습니다.")
    
    # Limit to 4 sentences
    description = ' '.join(description_parts[:4])
    
    return description

def extract_participant_info(content):
    """Extract participant information from interview transcript"""
    participants = []
    
    # Common patterns for participant information in Korean interviews
    lines = content.split('\n')
    
    # First, identify all speakers from the transcript
    speakers = {}
    for line in lines:
        if ':' in line:
            speaker = line.split(':')[0].strip()
            # Skip time stamps (like 00:00:00 or 00:12:00)
            if ':' in speaker and speaker.replace(':', '').isdigit():
                continue
            # Skip empty or very short names
            if speaker and len(speaker) >= 2 and len(speaker) < 20:  # Reasonable speaker name length
                if speaker not in speakers:
                    speakers[speaker] = {
                        'name': speaker,
                        'age': None,
                        'school': None,
                        'school_year': None,
                        'gender': None,
                        'major': None,  # Added for college students
                        'lines': [],
                        'info_lines': []  # Lines that contain their personal info
                    }
                speakers[speaker]['lines'].append(line)
    
    # Filter out common interviewer indicators and non-participant entries
    interviewer_keywords = ['Irene', 'Kang', '연구', '리서처', 'researcher', '인터뷰어', '강예린']
    non_participant_keywords = ['발표', '님의', '00', 'presentation', '선생님', '교수님', '사회자']
    interviewees = {}
    
    for speaker_name, speaker_data in speakers.items():
        # Skip if it's an interviewer
        is_interviewer = any(keyword.lower() in speaker_name.lower() for keyword in interviewer_keywords)
        # Skip if it contains non-participant keywords
        is_non_participant = any(keyword in speaker_name for keyword in non_participant_keywords)
        # Skip if it's just numbers or too short
        is_invalid = speaker_name.isdigit() or len(speaker_name) <= 1
        
        if not is_interviewer and not is_non_participant and not is_invalid:
            interviewees[speaker_name] = speaker_data
    
    # Now analyze the content to extract participant information
    current_speaker = None
    context_lines = []  # Keep track of recent lines for context
    
    for i, line in enumerate(lines):
        # Update current speaker
        if ':' in line:
            speaker = line.split(':')[0].strip()
            if speaker in interviewees:
                current_speaker = speaker
        
        # Keep context of last 10 lines
        context_lines.append(line)
        if len(context_lines) > 10:
            context_lines.pop(0)
        
        # Extract information patterns
        if current_speaker and current_speaker in interviewees:
            participant = interviewees[current_speaker]
            
            # Pattern 1: School year information
            if '학년' in line:
                # High school patterns
                if '고등학교' in line or '고등학생' in line or '고' in line:
                    if '1학년' in line or '일학년' in line or '고1' in line:
                        participant['school_year'] = '고1'
                    elif '2학년' in line or '이학년' in line or '고2' in line:
                        participant['school_year'] = '고2'
                    elif '3학년' in line or '삼학년' in line or '고3' in line:
                        participant['school_year'] = '고3'
                # Middle school patterns
                elif '중학교' in line or '중학생' in line or '중' in line:
                    if '1학년' in line or '일학년' in line or '중1' in line:
                        participant['school_year'] = '중1'
                    elif '2학년' in line or '이학년' in line or '중2' in line:
                        participant['school_year'] = '중2'
                    elif '3학년' in line or '삼학년' in line or '중3' in line:
                        participant['school_year'] = '중3'
                # University patterns
                elif '대학' in line:
                    if '1학년' in line:
                        participant['school_year'] = '대1'
                    elif '2학년' in line:
                        participant['school_year'] = '대2'
                    elif '3학년' in line:
                        participant['school_year'] = '대3'
                    elif '4학년' in line:
                        participant['school_year'] = '대4'
                
                participant['info_lines'].append(line)
            
            # Pattern 2: Birth year for age
            if '년생' in line:
                import re
                # Look for patterns like "08년생" or "2008년생"
                year_matches = re.findall(r'(\d{2,4})년생', line)
                if year_matches:
                    birth_year = year_matches[0]
                    if len(birth_year) == 2:
                        # Convert 2-digit year to 4-digit
                        # Assume 00-25 is 2000-2025, 26-99 is 1926-1999
                        year_int = int(birth_year)
                        if year_int <= 25:
                            birth_year = '20' + birth_year
                        else:
                            birth_year = '19' + birth_year
                    current_year = datetime.now().year
                    age = current_year - int(birth_year) + 1  # Korean age
                    participant['age'] = age
                    participant['info_lines'].append(line)
            
            # Pattern 3: School name
            if '학교' in line:
                import re
                # Look for school names
                school_patterns = [
                    r'([가-힣]+(?:초등학교|중학교|고등학교|대학교))',
                    r'([가-힣]+고등학교)',
                    r'([가-힣]+중학교)',
                    r'([가-힣]+대학교)',
                    r'([가-힣]+대학)'
                ]
                for pattern in school_patterns:
                    school_match = re.search(pattern, line)
                    if school_match:
                        participant['school'] = school_match.group(1)
                        participant['info_lines'].append(line)
                        break
            
            # Pattern 4: Major (for university students)
            if '전공' in line or '학과' in line or '과' in line:
                if '예체능' in line:
                    participant['major'] = '예체능'
                elif '공대' in line or '공학' in line:
                    participant['major'] = '공학'
                elif '문과' in line:
                    participant['major'] = '문과'
                elif '이과' in line:
                    participant['major'] = '이과'
                participant['info_lines'].append(line)
            
            # Pattern 5: Gender (if mentioned)
            if '남학생' in line or '남자' in line:
                participant['gender'] = '남'
                participant['info_lines'].append(line)
            elif '여학생' in line or '여자' in line:
                participant['gender'] = '여'
                participant['info_lines'].append(line)
    
    # Convert to list format
    for speaker_name, data in interviewees.items():
        # Clean up the data
        participant_info = {
            'name': data['name'],
            'age': data['age'],
            'school': data['school'],
            'school_year': data['school_year'],
            'gender': data['gender'],
            'major': data['major'],
            'summary': []  # Summary of key information
        }
        
        # Build summary
        if data['school_year']:
            participant_info['summary'].append(data['school_year'])
        if data['age']:
            participant_info['summary'].append(f"{data['age']}세")
        if data['school']:
            participant_info['summary'].append(data['school'])
        if data['major']:
            participant_info['summary'].append(data['major'])
        
        participants.append(participant_info)
    
    return participants

def get_google_docs_content(document_id):
    """Fetch content from Google Docs using the document ID"""
    try:
        # First, try to fetch directly via HTTP for public documents
        # This works for documents that are publicly accessible
        export_url = f"https://docs.google.com/document/d/{document_id}/export?format=txt"
        
        print(f"Attempting to fetch document via direct HTTP: {document_id}")
        response = requests.get(export_url, allow_redirects=True)
        
        if response.status_code == 200:
            # Successfully fetched the document
            content = response.text
            print(f"Successfully fetched document content: {len(content)} characters")
            return content.strip()
        elif response.status_code == 403:
            print(f"Access denied to document {document_id}. Trying API method...")
        else:
            print(f"HTTP {response.status_code} when fetching document. Trying API method...")
        
        # If direct HTTP failed, try using service account credentials
        if os.path.exists('credentials.json'):
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/documents.readonly']
            )
            service = build('docs', 'v1', credentials=credentials)
            
            # Retrieve the document
            document = service.documents().get(documentId=document_id).execute()
            
            # Extract the text content
            content = ""
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for text_element in element['paragraph'].get('elements', []):
                        if 'textRun' in text_element:
                            content += text_element['textRun'].get('content', '')
            
            return content.strip()
        else:
            # Try using API key
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key and api_key != 'your_google_api_key_here':
                service = build('docs', 'v1', developerKey=api_key)
                
                # Retrieve the document
                document = service.documents().get(documentId=document_id).execute()
                
                # Extract the text content
                content = ""
                for element in document.get('body', {}).get('content', []):
                    if 'paragraph' in element:
                        for text_element in element['paragraph'].get('elements', []):
                            if 'textRun' in text_element:
                                content += text_element['textRun'].get('content', '')
                
                return content.strip()
            else:
                print("Warning: No Google API credentials found for Docs API")
                # If we couldn't fetch via HTTP and have no API credentials, return None
                if response.status_code != 200:
                    return None
    
    except HttpError as e:
        if e.resp.status == 403:
            print(f"Access denied to document {document_id}. The document might be private.")
        elif e.resp.status == 404:
            print(f"Document {document_id} not found.")
        else:
            print(f"HTTP error {e.resp.status} when accessing document {document_id}: {e.content}")
        return None
    
    except Exception as e:
        print(f"Error fetching Google Docs content: {str(e)}")
        return None

# Save custom data sources
def save_data_sources(sources):
    """Save custom data sources to file"""
    try:
        with open(DATA_SOURCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data sources: {e}")
        return False

# No-cache decorator
def add_no_cache_headers(response):
    """Add headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Apply no-cache headers to all responses
@app.after_request
def after_request(response):
    return add_no_cache_headers(response)

def perform_google_search(query, num_results=5):
    """Google Custom Search API를 사용하여 웹 검색 수행"""
    try:
        if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
            print("Warning: Google Search API credentials not configured")
            return []
        
        if GOOGLE_SEARCH_API_KEY == 'your_google_search_api_key_here':
            print("Warning: Please configure actual Google Search API credentials")
            return []
        
        # Google Custom Search API URL
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            'key': GOOGLE_SEARCH_API_KEY,
            'cx': GOOGLE_SEARCH_ENGINE_ID,
            'q': query,
            'num': num_results,
            'hl': 'ko'  # Korean language preference
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            search_results = response.json()
            items = search_results.get('items', [])
            
            processed_results = []
            for item in items:
                processed_results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'displayLink': item.get('displayLink', '')
                })
            
            print(f"Successfully retrieved {len(processed_results)} search results for query: {query}")
            return processed_results
        else:
            print(f"Error performing Google search: {response.status_code} - {response.text}")
            return []
    
    except Exception as e:
        print(f"Error in Google Search: {str(e)}")
        return []

def get_all_sheet_names():
    """Get all sheet names from the Google Sheets document"""
    try:
        # Try using API first
        if os.path.exists('credentials.json'):
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            service = build('sheets', 'v4', credentials=credentials)
        else:
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key and api_key != 'your_google_api_key_here':
                service = build('sheets', 'v4', developerKey=api_key)
            else:
                # If no API credentials, return hardcoded sheet IDs for now
                # You can add more sheet IDs here as needed
                return [
                    {'name': 'Sheet1', 'gid': '187909252'},
                    {'name': 'tablet behavior', 'gid': '2040429429'}
                ]
        
        # Get spreadsheet metadata
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet.get('sheets', [])
        
        sheet_info = []
        for sheet in sheets:
            properties = sheet.get('properties', {})
            sheet_info.append({
                'name': properties.get('title', ''),
                'gid': str(properties.get('sheetId', ''))
            })
        
        return sheet_info
    
    except Exception as e:
        print(f"Error getting sheet names: {str(e)}")
        # Return hardcoded sheet IDs as fallback
        return [
            {'name': 'Sheet1', 'gid': '187909252'},
            {'name': 'tablet behavior', 'gid': '2040429429'}
        ]

def get_sheet_data_by_gid(sheet_gid, sheet_name=None, spreadsheet_id=None):
    """Get data from a specific sheet by its GID"""
    try:
        # Use provided spreadsheet_id or default
        if not spreadsheet_id:
            spreadsheet_id = SPREADSHEET_ID
            
        # 캐시 방지를 위해 timestamp 추가
        import time
        timestamp = int(time.time())
        
        # CSV 내보내기 URL로 시도
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_gid}&timestamp={timestamp}"
        
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
                print(f"Warning: No rows found in sheet {sheet_name or sheet_gid}")
                return []
            
            # 첫 번째 행을 헤더로 사용
            headers = rows[0]
            data = []
            
            for row in rows[1:]:
                if row:  # 빈 행 제외
                    row_dict = {}
                    for i, header in enumerate(headers):
                        row_dict[header] = row[i] if i < len(row) else ''
                    # Add sheet name to each row for tracking
                    row_dict['_sheet_name'] = sheet_name or f'Sheet_{sheet_gid}'
                    data.append(row_dict)
            
            print(f"Successfully retrieved {len(data)} rows from sheet {sheet_name or sheet_gid}")
            return data
        else:
            print(f"Error: HTTP {response.status_code} when accessing sheet {sheet_name or sheet_gid}")
            print(f"URL: {csv_url}")
            if response.status_code == 403:
                print("Access denied. The sheet might be private or require authentication.")
            elif response.status_code == 404:
                print("Sheet not found. Check if the spreadsheet ID and GID are correct.")
        
        return []
    
    except Exception as e:
        print(f"Error reading sheet {sheet_name or sheet_gid}: {str(e)}")
        return []

def determine_sheet_context(user_question):
    """Determine which sheet(s) to query based on the question content"""
    # Keywords that indicate tablet behavior sheet
    tablet_keywords = ['태블릿', 'tablet', 'ipad', '아이패드', '갤탭', 'tab', '패드']
    
    # Keywords that indicate parent survey sheet
    parent_keywords = ['자녀', '학부모', '부모', '어머니', '아버지', '초등 자녀', '중등 자녀', '고등 자녀']
    
    # Check if question is about parents/children
    question_lower = user_question.lower()
    for keyword in parent_keywords:
        if keyword in user_question:  # Use original case for Korean
            return [{
                'gid': '933791472',
                'name': 'Parent Survey'
            }]
    
    # Check if question is about tablets
    for keyword in tablet_keywords:
        if keyword in question_lower:
            return [{
                'gid': '2040429429',
                'name': 'tablet behavior'
            }]
    
    # Default to Sheet1 for general questions
    return [{
        'gid': '187909252',
        'name': 'Sheet1'
    }]

def get_google_sheets_data(sheet_gid=None, sheet_name=None):
    """구글 시트에서 데이터를 가져오는 함수"""
    try:
        # Default to Sheet1 if not specified
        if not sheet_gid:
            sheet_gid = '187909252'  # Sheet1's GID
            sheet_name = 'Sheet1'
        
        print(f"Fetching data from sheet: {sheet_name} (GID: {sheet_gid})")
        sheet_data = get_sheet_data_by_gid(sheet_gid, sheet_name)
        
        if sheet_data:
            print(f"Retrieved {len(sheet_data)} rows from {sheet_name}")
        else:
            print(f"No data retrieved from {sheet_name}")
        
        return sheet_data
    
    except Exception as e:
        print(f"Error reading Google Sheets: {str(e)}")
        return []

def extract_search_queries(user_question, sheet_data):
    """사용자 질문과 시트 데이터를 분석하여 검색 쿼리 추출"""
    queries = []
    
    # 질문에서 직접적인 검색 키워드 추출
    # 예: "AI 교육의 최신 트렌드", "LLM 활용 사례" 등
    keywords = ['트렌드', '사례', '연구', '통계', '현황', '최신', '정보', '뉴스']
    
    for keyword in keywords:
        if keyword in user_question:
            # 기본 쿼리로 사용자 질문 자체를 추가
            queries.append(user_question)
            break
    
    # 시트 데이터에서 관련 토픽 추출 (예: 학생들이 자주 언급한 주제)
    if sheet_data and '특정 주제' in user_question:
        # 시트 데이터에서 주요 키워드나 토픽 추출 로직
        pass
    
    # 교육 관련 질문인 경우 교육 특화 검색어 추가
    if any(word in user_question for word in ['교육', '학습', '학생', '수업']):
        if 'AI' in user_question or 'LLM' in user_question:
            queries.append("AI 교육 활용 사례 2024")
    
    return queries[:3]  # 최대 3개의 검색 쿼리만 사용

def process_sheet_data(sheet_name, sheet_rows, user_question, sheet_date=None):
    """각 시트의 데이터를 분석하여 요약 생성"""
    if not sheet_rows:
        return None
    
    summary = f"[{sheet_name} 데이터 분석]\n"
    if sheet_date:
        summary += f"조사 시기: {sheet_date}\n"
    summary += f"응답자 수: {len(sheet_rows)}명\n"
    
    # 기본 통계 계산
    gender_stats = {}
    grade_stats = {}
    region_stats = {}
    
    # 태블릿 관련 키워드 검색
    tablet_keywords = ['태블릿', 'tablet', 'ipad', '아이패드', '갤탭', 'tab']
    tablet_users = []
    
    for row in sheet_rows:
        # 성별 통계
        gender = row.get('성별이 어떻게 되나요?', '').strip()
        if gender:
            gender_stats[gender] = gender_stats.get(gender, 0) + 1
        
        # 학년 통계
        grade = row.get('현재 학년이 어떻게 되나요?', '').strip()
        if grade:
            if grade in ['춈8', '춈2', '춈3', '춈4', '춈5', '춈6']:
                grade_stats['초등학생'] = grade_stats.get('초등학생', 0) + 1
            elif grade in ['중1', '중2', '중3']:
                grade_stats['중학생'] = grade_stats.get('중학생', 0) + 1
            elif grade in ['고1', '고2', '고3']:
                grade_stats['고등학생'] = grade_stats.get('고등학생', 0) + 1
            else:
                grade_stats[grade] = grade_stats.get(grade, 0) + 1
        
        # 지역 통계
        region = row.get('현재 거주중인 지역이 어디인가요? ', '') or row.get('거주지역', '')
        region = region.strip()
        if region:
            region_stats[region] = region_stats.get(region, 0) + 1
        
        # 태블릿 사용자 확인
        for key, value in row.items():
            if any(keyword in str(value).lower() for keyword in tablet_keywords):
                tablet_users.append(row)
                break
    
    # 질문에 따라 관련 정보만 포함
    if '태블릿' in user_question:
        if tablet_users:
            summary += f"\n태블릿 관련 응답: {len(tablet_users)}건 발견\n"
            
            # 태블릿 사용자의 다양한 특징 분석
            # 1. 학년 분석
            tablet_grades = {}
            for user in tablet_users:
                grade = user.get('현재 학년이 어떻게 되나요?', '').strip()
                if grade:
                    tablet_grades[grade] = tablet_grades.get(grade, 0) + 1
            
            if tablet_grades:
                summary += "\n태블릿 사용자 학년 분포:\n"
                for grade, count in sorted(tablet_grades.items()):
                    percentage = (count / len(tablet_users)) * 100
                    summary += f"  - {grade}: {count}명 ({percentage:.1f}%)\n"
            
            # 2. 성별 분석
            tablet_genders = {}
            for user in tablet_users:
                gender = user.get('성별이 어떻게 되나요?', '').strip()
                if gender:
                    tablet_genders[gender] = tablet_genders.get(gender, 0) + 1
            
            if tablet_genders:
                summary += "\n태블릿 사용자 성별 분포:\n"
                for gender, count in sorted(tablet_genders.items()):
                    percentage = (count / len(tablet_users)) * 100
                    summary += f"  - {gender}: {count}명 ({percentage:.1f}%)\n"
            
            # 3. 지역 분석
            tablet_regions = {}
            for user in tablet_users:
                region = user.get('현재 거주중인 지역이 어디인가요? ', '').strip()
                if region:
                    tablet_regions[region] = tablet_regions.get(region, 0) + 1
            
            if tablet_regions:
                summary += "\n태블릿 사용자 상위 5개 지역:\n"
                top_regions = sorted(tablet_regions.items(), key=lambda x: x[1], reverse=True)[:5]
                for region, count in top_regions:
                    percentage = (count / len(tablet_users)) * 100
                    summary += f"  - {region}: {count}명 ({percentage:.1f}%)\n"
            
            # 4. 어떤 컬럼에서 태블릿이 언급되었는지 분석
            tablet_mention_columns = {}
            for user in tablet_users:
                for key, value in user.items():
                    if any(keyword in str(value).lower() for keyword in tablet_keywords):
                        if key not in ['_sheet_name'] and key:
                            tablet_mention_columns[key] = tablet_mention_columns.get(key, 0) + 1
            
            if tablet_mention_columns:
                summary += "\n태블릿이 언급된 주요 항목:\n"
                for col, count in sorted(tablet_mention_columns.items(), key=lambda x: x[1], reverse=True)[:3]:
                    percentage = (count / len(tablet_users)) * 100
                    summary += f"  - {col}: {count}건 ({percentage:.1f}%)\n"
        else:
            summary += f"\n태블릿 관련 언급이 없습니다.\n"
    
    # 학년별 통계 포함
    if grade_stats and any(keyword in user_question for keyword in ['학생', '중학생', '고등학생', '초등학생']):
        summary += "\n학년 분포:\n"
        for grade, count in sorted(grade_stats.items()):
            percentage = (count / len(sheet_rows)) * 100
            summary += f"  - {grade}: {count}명 ({percentage:.1f}%)\n"
    
    return summary

def create_prompt(user_question, sheet_data, search_results=None):
    """사용자 질문과 시트 데이터, 웹 검색 결과를 결합하여 프롬프트 생성"""
    prompt_parts = []
    
    # Initialize filtered_data to avoid undefined variable error
    filtered_data = sheet_data if sheet_data else []
    
    # Check if this is interview data
    is_interview_data = (sheet_data and len(sheet_data) > 0 and 
                        sheet_data[0].get('_source_type') == 'interview')
    
    # 1. 데이터 섹션
    data_str = ""
    if sheet_data and len(sheet_data) > 0:
        if is_interview_data:
            # Handle interview data
            data_str = "=== 인터뷰 데이터 ===\n\n"
            data_str += f"문서 ID: {sheet_data[0].get('document_id')}\n"
            data_str += "\n인터뷰 내용:\n"
            data_str += sheet_data[0].get('content', '인터뷰 내용을 불러올 수 없습니다.') + "\n"
        else:
            # Handle survey data
            data_str = "=== 구글 시트 데이터 ===\n\n"
        
        # Get survey date from data
        survey_date = None
        from datetime import datetime
        if sheet_data:
            timestamp_str = sheet_data[0].get('Submitted At', '')
            if timestamp_str:
                try:
                    date_parsed = False
                    # Handle Korean date format first
                    if '오전' in timestamp_str or '오후' in timestamp_str:
                        try:
                            date_part = timestamp_str.split(' 오')[0].strip()
                            date_obj = datetime.strptime(date_part, '%Y. %m. %d')
                            survey_date = f"{date_obj.year}년 {date_obj.month}월"
                            date_parsed = True
                        except:
                            pass
                    
                    # Try other formats
                    if not date_parsed:
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%d/%m/%Y %H:%M:%S']:
                            try:
                                date_obj = datetime.strptime(timestamp_str.split('.')[0], fmt)
                                survey_date = f"{date_obj.year}년 {date_obj.month}월"
                                date_parsed = True
                                break
                            except:
                                continue
                except Exception as e:
                    print(f"Error parsing survey date: {str(e)}")
        
        # Overall summary
        # 기본 통계 계산
        gender_stats = {}
        grade_stats = {}
        region_stats = {}
        llm_usage_stats = {}
        
        for row in sheet_data:
            # 성별 통계 - Handle different column names
            gender = row.get('성별이 어떻게 되나요?', '') or row.get('성별', '')
            gender = gender.strip()
            if gender:
                gender_stats[gender] = gender_stats.get(gender, 0) + 1
            
            # 학년 통계 - Handle different column names
            grade = row.get('현재 학년이 어떻게 되나요?', '') or row.get('학년', '')
            grade = grade.strip()
            
            # For tablet behavior sheet, handle grade format like "01. 중2"
            if grade and '. ' in grade:
                grade = grade.split('. ')[1]  # Extract "중2" from "01. 중2"
            
            if grade:
                if grade in ['초1', '초2', '초3', '초4', '초5', '초6']:
                    grade_stats['초등학생'] = grade_stats.get('초등학생', 0) + 1
                elif grade in ['중1', '중2', '중3']:
                    grade_stats['중학생'] = grade_stats.get('중학생', 0) + 1
                elif grade in ['고1', '고2', '고3']:
                    grade_stats['고등학생'] = grade_stats.get('고등학생', 0) + 1
                else:
                    grade_stats[grade] = grade_stats.get(grade, 0) + 1
            
            # Also check 중/고등 column for tablet behavior sheet
            school_level = row.get('중/고등', '').strip()
            if school_level and not grade:
                if '중등' in school_level:
                    grade_stats['중학생'] = grade_stats.get('중학생', 0) + 1
                elif '고등' in school_level:
                    grade_stats['고등학생'] = grade_stats.get('고등학생', 0) + 1
            
            # Check for child grade column (for parent surveys) - Updated column name
            child_grade = row.get('현재 자녀의 학년', '').strip()
            if child_grade:
                # Use exact values from spreadsheet
                if child_grade == '초등 자녀':
                    grade_stats['초등 자녀'] = grade_stats.get('초등 자녀', 0) + 1
                elif child_grade == '중등 자녀':
                    grade_stats['중등 자녀'] = grade_stats.get('중등 자녀', 0) + 1
                elif child_grade == '고등 자녀':
                    grade_stats['고등 자녀'] = grade_stats.get('고등 자녀', 0) + 1
            
            # 지역 통계 - Handle different column names
            region = row.get('현재 거주중인 지역이 어디인가요? ', '') or row.get('거주지역', '') or row.get('지역', '')
            region = region.strip()
            if region:
                region_stats[region] = region_stats.get(region, 0) + 1
            
            # LLM 사용 통계
            general_usage = row.get('GPT, Gemini와 같은 LLM 인공지능 서비스를 *평소에 활용*하고 계신가요?', '').strip()
            if general_usage:
                llm_usage_stats[general_usage] = llm_usage_stats.get(general_usage, 0) + 1
        
        # 요약 통계 출력
        if gender_stats:
            data_str += "\n성별 분포:\n"
            for gender, count in gender_stats.items():
                percentage = (count / len(sheet_data)) * 100
                data_str += f"  - {gender}: {count}명 ({percentage:.1f}%)\n"
        
        if grade_stats:
            data_str += "\n학년 분포:\n"
            for grade, count in sorted(grade_stats.items()):
                percentage = (count / len(sheet_data)) * 100
                data_str += f"  - {grade}: {count}명 ({percentage:.1f}%)\n"
        
        if region_stats:
            data_str += "\n지역 분포:\n"
            top_regions = sorted(region_stats.items(), key=lambda x: x[1], reverse=True)[:5]
            for region, count in top_regions:
                percentage = (count / len(sheet_data)) * 100
                data_str += f"  - {region}: {count}명 ({percentage:.1f}%)\n"
            if len(region_stats) > 5:
                data_str += f"  - 기타 {len(region_stats) - 5}개 지역\n"
        
        if llm_usage_stats:
            data_str += "\nLLM 사용 현황:\n"
            for usage, count in llm_usage_stats.items():
                percentage = (count / len(sheet_data)) * 100
                data_str += f"  - {usage}: {count}명 ({percentage:.1f}%)\n"
        
        data_str += "\n--- 상세 데이터 ---\n"
        
        # 질문에 따라 관련 데이터만 필터링
        filtered_data = sheet_data if sheet_data else []
        headers = list(sheet_data[0].keys()) if sheet_data else []
        
        # Include all column information for LLM to make intelligent decisions
        data_str += "\n[사용 가능한 모든 컬럼 목록]\n"
        for i, header in enumerate(headers, 1):
            if header != '_sheet_name':  # Exclude internal column
                data_str += f"{i}. {header}\n"
        
        data_str += "\n[분석 지침]\n"
        data_str += "위 컬럼 목록을 참고하여 질문에 가장 적합한 컬럼을 선택하여 분석하세요.\n"
        data_str += "예시: '학년별로 재미있는 과목'이라는 질문에는 '학년' 관련 컬럼과 '재미있는 과목' 관련 컬럼을 함께 분석해야 합니다.\n\n"
        
        # LIMIT DATA TO PREVENT TOKEN OVERFLOW
        # Only include a sample of data, not the entire dataset
        MAX_ROWS = 50  # Limit to 50 rows to prevent token overflow
        
        data_str += f"[데이터 샘플 - 총 {len(sheet_data)}개 중 {min(MAX_ROWS, len(sheet_data))}개 표시]\n"
        relevant_headers = headers  # Provide all headers for complete context
        
        # 교차 분석이 필요한 경우 ("학년별로", "성별로" 등의 표현이 있을 때)
        if any(keyword in user_question for keyword in ['학년별로', '성별로', '지역별로', '별로']):
            # 추가로 필요한 컬럼들을 포함
            if '학년별로' in user_question:
                grade_headers = [h for h in headers if '학년' in h]
                for gh in grade_headers:
                    if gh not in relevant_headers:
                        relevant_headers.append(gh)
            if '성별로' in user_question:
                gender_headers = [h for h in headers if '성별' in h]
                for gh in gender_headers:
                    if gh not in relevant_headers:
                        relevant_headers.append(gh)
            if '지역별로' in user_question:
                region_headers = [h for h in headers if '지역' in h or '거주' in h]
                for rh in region_headers:
                    if rh not in relevant_headers:
                        relevant_headers.append(rh)
        
        # 항상 포함해야 할 기본 헤더들
        essential_headers = ['이름을 적어주세요', '성별이 어떻게 되나요?', '현재 학년이 어떻게 되나요?', '현재 거주중인 지역이 어디인가요? ']
        
        # Always include essential headers for context
        for eh in essential_headers:
            if eh in headers and eh not in relevant_headers:
                relevant_headers.insert(0, eh)
        
        # 인터뷰 스크립트나 긴 텍스트가 있는지 확인
        has_long_text = False
        sample_data = filtered_data[:MAX_ROWS]  # Only check in sample data
        
        for h in relevant_headers:
            if 'interview' in h.lower() or 'script' in h.lower():
                has_long_text = True
                break
            for row in sample_data:
                if len(str(row.get(h, ''))) > 200:
                    has_long_text = True
                    break
            if has_long_text:
                break
        
        if has_long_text:
            # 긴 텍스트가 있는 경우 다른 형식으로 표시
            for i, row in enumerate(sample_data, 1):
                data_str += f"\n--- 응답자 #{i} ---\n"
                for header in relevant_headers:
                    value = str(row.get(header, ''))
                    if value:
                        if len(value) > 500:  # Further limit long text
                            # Truncate very long text
                            data_str += f"\n[{header}]:\n{value[:500]}... (truncated)\n"
                        else:
                            data_str += f"\n[{header}]:\n{value}\n"
                data_str += "\n"
        else:
            # 짧은 데이터는 테이블 형식으로
            data_str += " | ".join(relevant_headers) + "\n"
            data_str += "-" * (len(relevant_headers) * 20) + "\n"
            
            for row in sample_data:
                row_values = []
                for header in relevant_headers:
                    value = str(row.get(header, ''))
                    # Truncate individual cell values if too long
                    if len(value) > 100:
                        value = value[:100] + "..."
                    row_values.append(value)
                data_str += " | ".join(row_values) + "\n"
        
        # Add note about data sampling
        data_str += f"\n[참고: 전체 {len(sheet_data)}개 데이터 중 {len(sample_data)}개 샘플만 표시됨. 통계는 전체 데이터 기준입니다.]\n"
    else:
        data_str = "=== 구글 시트 데이터 ===\n데이터가 없습니다.\n"
    
    prompt_parts.append(data_str)
    
    # 2. 웹 검색 결과 섹션
    if search_results:
        search_str = "\n\n=== 웹 검색 결과 ===\n\n"
        for idx, result in enumerate(search_results, 1):
            search_str += f"[{idx}] {result['title']}\n"
            search_str += f"   출처: {result['displayLink']}\n"
            search_str += f"   요약: {result['snippet']}\n"
            search_str += f"   링크: {result['link']}\n\n"
        prompt_parts.append(search_str)
    
    # 3. 전체 프롬프트 조합
    full_prompt = "\n".join(prompt_parts)
    
    # 4. 질문과 주의사항 추가
    if search_results:
        instructions = f"""

위 데이터와 웹 검색 결과를 모두 참고하여 다음 질문에 답해주세요:
질문: {user_question}

주의사항:
1. 구글 시트 데이터를 기본으로 하되, 웹 검색 결과로 보완하여 더 풍부한 답변을 제공하세요.
2. 웹 검색 결과를 인용할 때는 출처를 명확히 밝혀주세요.
3. 시트 데이터와 웹 정보를 비교/대조하여 통찰력 있는 분석을 제공하세요.
4. 데이터에 인터뷰 스크립트나 대화 내용이 있다면, 해당 내용을 꼼꼼히 분석하여 답변하세요.
5. 답변은 친절하고 상세하게 작성해주세요.
"""
    else:
        # Add explicit count summary for counting questions
        count_keywords = ['몇명', '몇 명', '얼마나', '총', '합계']
        if any(keyword in user_question for keyword in count_keywords):
            # Calculate actual counts from the data
            total_count = len(filtered_data) if filtered_data else 0
            
            # Count by school year
            school_year_counts = {}
            grade_detail_counts = {}
            for row in (filtered_data if filtered_data else sheet_data):
                # Handle different column names
                school_year = row.get('현재 학년이 어떻게 되나요?', '') or row.get('학년', '')
                school_year = school_year.strip()
                
                # Handle format like "01. 중2"
                if school_year and '. ' in school_year:
                    school_year = school_year.split('. ')[1]
                
                if school_year:
                    # Keep detailed grade counts
                    grade_detail_counts[school_year] = grade_detail_counts.get(school_year, 0) + 1
                    
                    # Group into categories
                    if school_year in ['초1', '초2', '초3', '초4', '초5', '초6']:
                        category = '초등학생'
                    elif school_year in ['중1', '중2', '중3']:
                        category = '중학생'
                    elif school_year in ['고1', '고2', '고3']:
                        category = '고등학생'
                    else:
                        category = school_year
                    
                    school_year_counts[category] = school_year_counts.get(category, 0) + 1
                
                # Also check 중/고등 column for tablet behavior sheet if no grade found
                if not school_year:
                    school_level = row.get('중/고등', '').strip()
                    if '중등' in school_level:
                        school_year_counts['중학생'] = school_year_counts.get('중학생', 0) + 1
                    elif '고등' in school_level:
                        school_year_counts['고등학생'] = school_year_counts.get('고등학생', 0) + 1
            
            # Create dynamic summary
            summary_lines = [f"- 총 응답자 수: {total_count}명"]
            for category, count in sorted(school_year_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = round((count / total_count * 100), 1) if total_count > 0 else 0
                summary_lines.append(f"- {category}: {count}명 ({percentage}%)")
            
            # Add detailed grade counts if available
            detailed_lines = []
            if '중1' in user_question or '중2' in user_question or '중3' in user_question:
                # Check if we have middle school data filtered
                if any('중학생' in line for line in summary_lines):
                    detailed_lines.append("\n학년별 상세 분포:")
                    for grade in ['중1', '중2', '중3']:
                        if grade in grade_detail_counts:
                            detailed_lines.append(f"- {grade}: {grade_detail_counts[grade]}명")
            
            instructions = f"""
=== 중요 수량 정보 ===
데이터 요약에 제공된 총계를 확인하세요:
{chr(10).join(summary_lines)}
{chr(10).join(detailed_lines) if detailed_lines else ''}

위 데이터를 참고하여 다음 질문에 답해주세요:
질문: {user_question}

주의사항:
1. 수량을 묻는 질문에는 위에 제공된 정확한 숫자를 사용하세요.
2. 테이블의 행을 직접 세지 말고 제공된 요약 정보를 활용하세요.
3. 필터링된 데이터에도 총계가 명시되어 있으면 그것을 사용하세요.
4. 학년별 분포가 명시되어 있으면 제공된 숫자를 그대로 사용하세요.
"""
        else:
            instructions = f"""

위 데이터를 참고하여 다음 질문에 답해주세요:
질문: {user_question}

주의사항:
1. 데이터에 인터뷰 스크립트나 대화 내용이 있다면, 해당 내용을 꼼꼼히 분석하여 답변하세요.
2. 사람의 이름이 언급되면, 해당 인물과 관련된 모든 정보를 종합하여 답변하세요.
3. 답변은 친절하고 상세하게 작성해주세요.
4. 데이터를 기반으로 정확한 정보를 제공하고, 필요한 경우 추가적인 분석이나 인사이트도 제공하세요.
"""
    
    return full_prompt + instructions

@app.route('/api/chat', methods=['POST'])
def chat():
    """사용자 질문을 받아 LLM 응답을 반환하는 API"""
    try:
        data = request.json
        user_question = data.get('question', '')
        enable_web_search = data.get('enable_web_search', False)  # 웹 검색 활성화 옵션
        sheet_gid = data.get('sheet_gid', None)  # 특정 시트 GID
        sheet_name = data.get('sheet_name', None)  # 특정 시트 이름
        conversation_history = data.get('conversation_history', [])  # 대화 히스토리
        
        if not user_question:
            return jsonify({'error': '질문을 입력해주세요.'}), 400
        
        # Get source type and document_id from request
        source_type = data.get('source_type', 'survey')
        document_id = data.get('document_id', None)
        spreadsheet_id = data.get('spreadsheet_id', SPREADSHEET_ID)
        
        # Handle interview data source (Google Docs)
        if source_type == 'interview' and document_id:
            # Fetch the actual content from Google Docs
            print(f"Fetching interview data from document: {document_id}")
            doc_content = get_google_docs_content(document_id)
            
            if doc_content:
                interview_data = [{
                    '_source_type': 'interview',
                    'document_id': document_id,
                    'content': doc_content
                }]
                print(f"Successfully fetched interview content: {len(doc_content)} characters")
            else:
                # If we couldn't fetch the content, provide an error message
                interview_data = [{
                    '_source_type': 'interview',
                    'document_id': document_id,
                    'content': f"인터뷰 문서를 불러올 수 없습니다. 문서가 공개되어 있거나 적절한 권한이 설정되어 있는지 확인해주세요.\n\n문서 ID: {document_id}\n\n해결 방법:\n1. Google Docs에서 문서를 열어 '공유' 버튼을 클릭합니다\n2. '링크가 있는 모든 사용자'를 선택하고 '뷰어' 권한을 부여합니다\n3. 또는 서비스 계정 이메일에 문서를 공유합니다"
                }]
                print(f"Failed to fetch interview content from document: {document_id}")
            
            sheet_data = interview_data
            access_errors = []
            sheets_to_query = []  # Empty list for interview data
        else:
            # Handle survey data source (Google Sheets)
            # Determine which sheet(s) to query based on question if not explicitly specified
            if not sheet_gid and not sheet_name:
                sheets_to_query = determine_sheet_context(user_question)
            else:
                # Use the explicitly provided sheet
                sheets_to_query = [{
                    'gid': sheet_gid or DEFAULT_SHEET_GID,
                    'name': sheet_name or 'Sheet1'
                }]
            
            # Get data from all relevant sheets
            sheet_data = []
            access_errors = []
            for sheet in sheets_to_query:
                # Use the provided spreadsheet_id for custom sheets
                data = get_sheet_data_by_gid(sheet['gid'], sheet['name'], spreadsheet_id)
                if not data:
                    # Check if this is a custom sheet that failed to load
                    if spreadsheet_id != SPREADSHEET_ID:
                        access_errors.append({
                            'sheet_name': sheet['name'],
                            'spreadsheet_id': spreadsheet_id,
                            'gid': sheet['gid']
                        })
                else:
                    sheet_data.extend(data)
        
        print(f"Total data from {len(sheets_to_query)} sheet(s): {len(sheet_data)} rows")
        
        # If no data was retrieved and there were access errors, return a more helpful error message
        if not sheet_data and access_errors:
            error_msg = f"시트에 접근할 수 없습니다. Google Sheets가 공개되어 있거나 올바른 권한이 설정되어 있는지 확인해주세요.\n\n"
            error_msg += f"접근 실패한 시트:\n"
            for error in access_errors:
                error_msg += f"- {error['sheet_name']} (Spreadsheet ID: {error['spreadsheet_id']}, GID: {error['gid']})\n"
            error_msg += f"\n해결 방법:\n"
            error_msg += f"1. Google Sheets를 열어 '공유' 버튼을 클릭합니다\n"
            error_msg += f"2. '링크가 있는 모든 사용자'를 선택하고 '뷰어' 권한을 부여합니다\n"
            error_msg += f"3. 또는 서비스 계정 이메일에 시트를 공유합니다"
            
            return jsonify({'error': error_msg}), 403
        
        # 웹 검색 수행 (항상 수행, enable_web_search 플래그 무시)
        search_results = None
        # 검색 쿼리 추출
        search_queries = extract_search_queries(user_question, sheet_data)
        
        if search_queries:  # 검색 쿼리가 있을 때만 검색 수행
            # 각 쿼리에 대해 검색 수행
            all_search_results = []
            for query in search_queries:
                results = perform_google_search(query, num_results=3)
                all_search_results.extend(results)
            
            # 중복 제거 (동일한 링크 기준)
            seen_links = set()
            search_results = []
            for result in all_search_results:
                if result['link'] not in seen_links:
                    seen_links.add(result['link'])
                    search_results.append(result)
            
            # 관련성 높은 결과만 필터링
            if search_results:
                relevant_results = []
                for result in search_results[:5]:  # 최대 5개 결과만 검토
                    # 제목이나 스니펫에 질문의 핵심 키워드가 포함되어 있는지 확인
                    title_snippet = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
                    # 관련성 키워드 체크
                    relevant = False
                    question_keywords = user_question.lower().split()
                    # 최소 2개 이상의 주요 키워드가 포함되어 있으면 관련성 있다고 판단
                    matching_keywords = sum(1 for keyword in question_keywords if len(keyword) > 2 and keyword in title_snippet)
                    if matching_keywords >= 2:
                        relevant_results.append(result)
                
                search_results = relevant_results if relevant_results else None
        
        # 대화 컨텍스트에서 필터링 조건 추출
        context_filter = None
        if conversation_history and len(conversation_history) > 0:
            # "그 중에서", "그 중에", "위에서" 등의 표현 확인
            context_keywords = ['그 중에서', '그 중에', '위에서', '이 중에서', '그들 중']
            if any(keyword in user_question for keyword in context_keywords):
                # 직전 대화에서 특정 그룹 찾기 (예: 고등학생, 중학생 등)
                for msg in reversed(conversation_history):
                    if msg.get('role') == 'assistant':
                        content = msg.get('content', '')
                        # 학년 그룹 찾기
                        if '고등학생' in content and ('명' in content or '%' in content):
                            context_filter = {'type': 'grade', 'value': ['고1', '고2', '고3']}
                            print(f"Context filter detected: High school students")
                            break
                        elif '중학생' in content and ('명' in content or '%' in content):
                            context_filter = {'type': 'grade', 'value': ['중1', '중2', '중3']}
                            print(f"Context filter detected: Middle school students")
                            break
                        elif '초등학생' in content and ('명' in content or '%' in content):
                            context_filter = {'type': 'grade', 'value': ['초1', '초2', '초3', '초4', '초5', '초6']}
                            print(f"Context filter detected: Elementary school students")
                            break
        
        # 컨텍스트 필터가 있으면 데이터 필터링
        filtered_sheet_data = sheet_data
        if context_filter:
            filtered_sheet_data = []
            for row in sheet_data:
                grade = row.get('현재 학년이 어떻게 되나요?', '') or row.get('학년', '')
                grade = grade.strip()
                if '. ' in grade:
                    grade = grade.split('. ')[1]
                if grade in context_filter['value']:
                    filtered_sheet_data.append(row)
            print(f"Filtered data: {len(filtered_sheet_data)} out of {len(sheet_data)} rows")
        
        # 프롬프트 생성 (필터링된 데이터 사용)
        prompt = create_prompt(user_question, filtered_sheet_data, search_results)
        
        # 디버깅을 위해 데이터 출력
        print(f"Sheet data retrieved: {len(sheet_data)} rows")
        if sheet_data:
            print(f"First row: {sheet_data[0]}")
        if search_results:
            print(f"Web search results: {len(search_results)} results")
        
        # Debug: Check what's in the prompt for middle school questions
        middle_keywords = ['중학생', '중1', '중2', '중3']
        if any(keyword in user_question for keyword in middle_keywords):
            print("\n=== DEBUG: Middle school query detected ===")
            print(f"Question: {user_question}")
            # Count actual middle school students in sheet_data
            actual_middle_count = sum(1 for row in sheet_data if row.get('현재 학년이 어떻게 되나요?', '') in ['중1', '중2', '중3'])
            print(f"Actual middle school students in data: {actual_middle_count}")
            # Check if the prompt contains the detailed counts
            if '[' in prompt and '학년별 상세 분포:' in prompt:
                print("Grade detail section found in prompt")
            # Find the instructions section
            instructions_start = prompt.find('=== 중요 수량 정보 ===')
            if instructions_start > 0:
                print("\nInstructions section:")
                print(prompt[instructions_start:instructions_start+500])
            print("=== END DEBUG ===")
        
        # Claude API 호출
        if not client:
            return jsonify({'error': 'Claude API가 설정되지 않았습니다. ANTHROPIC_API_KEY를 확인해주세요.'}), 500
        
        # 시스템 프롬프트 조정
        # Get survey dates from each sheet separately
        sheet_dates = {}
        if sheet_data:
            # Group data by sheet to get dates
            sheet_grouped = {}
            for row in sheet_data:
                sheet_name = row.get('_sheet_name', 'Unknown')
                if sheet_name not in sheet_grouped:
                    sheet_grouped[sheet_name] = []
                sheet_grouped[sheet_name].append(row)
            
            # Get date for each sheet
            from datetime import datetime
            for sheet_name, rows in sheet_grouped.items():
                if rows:
                    # Try both 'Submitted At' and 'Submitted at'
                    timestamp_str = rows[0].get('Submitted At', '') or rows[0].get('Submitted at', '')
                    if timestamp_str:
                        try:
                            date_parsed = False
                            # Handle Korean date format first
                            if '오전' in timestamp_str or '오후' in timestamp_str:
                                try:
                                    date_part = timestamp_str.split(' 오')[0].strip()
                                    date_obj = datetime.strptime(date_part, '%Y. %m. %d')
                                    sheet_dates[sheet_name] = f"{date_obj.year}년 {date_obj.month}월"
                                    date_parsed = True
                                except:
                                    pass
                            
                            # Handle Sheet2's short format like "2025. 01"
                            if not date_parsed and '. ' in timestamp_str and len(timestamp_str) <= 10:
                                try:
                                    # Format: "2025. 01"
                                    parts = timestamp_str.strip().split('. ')
                                    if len(parts) == 2:
                                        year = int(parts[0])
                                        month = int(parts[1])
                                        sheet_dates[sheet_name] = f"{year}년 {month}월"
                                        date_parsed = True
                                except:
                                    pass
                            
                            # Try other formats
                            if not date_parsed:
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%d/%m/%Y %H:%M:%S']:
                                    try:
                                        date_obj = datetime.strptime(timestamp_str.split('.')[0], fmt)
                                        sheet_dates[sheet_name] = f"{date_obj.year}년 {date_obj.month}월"
                                        date_parsed = True
                                        break
                                    except:
                                        continue
                        except:
                            pass
            
            print(f"Sheet dates detected: {sheet_dates}")
        
        # Use the appropriate date based on context
        survey_date = list(sheet_dates.values())[0] if sheet_dates else "데이터"
        
        # For dynamic context, use current date
        from datetime import datetime
        current_date = datetime.now()
        data_context = f"{current_date.year}년 {current_date.month}월"
        
        system_prompt = f"""당신은 데이터 분석을 도와주는 친절한 어시스턴트입니다. 주어진 데이터를 기반으로 정확하게 답변해주세요.

[최우선 규칙 - 대화 컨텍스트 이해]
대화 히스토리가 있는 경우, 반드시 이전 대화 내용을 참고하여 답변해야 합니다.
- "그 중에서", "그 중에", "위에서", "이 중에서" 등의 표현은 직전 대화에서 언급된 특정 그룹을 가리킵니다.
- 예: 직전에 "고등학생 143명"을 언급했다면, "그 중에서 과외를 하는 학생"은 143명의 고등학생 중에서 과외를 하는 학생을 의미합니다.
- 전체 데이터가 아닌, 직전에 언급된 하위 그룹에 대해 분석해야 합니다.

[필수 규칙] 모든 답변은 다음 문장으로 시작해야 합니다:
- "최근 수집된 조사 자료에 의하면,"

이것은 절대적인 규칙입니다. 답변의 첫 문장은 위 세 가지 중 하나여야 합니다.

[중요한 규칙 - 컬럼 선택 및 분석]
데이터 분석 시 다음 방법으로 관련 컬럼을 찾아 분석하세요:
1. "사용 가능한 모든 컬럼 목록"을 확인하여 질문과 관련된 컬럼을 찾으세요
2. 질문의 키워드와 유사한 단어가 포함된 컬럼을 우선적으로 선택하세요
3. 교차 분석이 필요한 경우 관련된 모든 컬럼을 함께 분석하세요

예시:
- "재미있는 과목"을 묻는다면 → '재미있는', '재밌는', '흥미' 등이 포함된 컬럼 찾기
- "학년별로 분석"이라면 → '학년' 관련 컬럼과 함께 교차 분석
- "어려운 과목"을 묻는다면 → '어려운', '힘든', '자신없는' 등이 포함된 컬럼 찾기

[중요한 규칙 - 교차 분석]
"학년별로", "성별로", "지역별로" 등의 표현이 있을 때는 반드시 해당 컬럼과 다른 컬럼을 교차 분석하여 답변하세요. 
예: "학년별로 재미있는 과목"이라면 '학년' 컬럼과 '재미있는 과목' 컬럼을 함께 분석하여 각 학년에서 선호하는 과목을 파악하세요.

특히 수량을 묻는 질문에 답할 때는:
1. 반드시 "데이터 요약" 섹션에 명시된 "총 응답자 수: XXX명" 숫자를 사용하세요
2. 테이블의 행을 직접 세지 마세요 - 테이블은 단지 샘플일 뿐입니다
3. "=== 중요 수량 정보 ===" 섉션이 있으면 그 숫자를 사용하세요
4. 필터링된 데이터에도 총계가 명시되어 있으면 그것을 사용하세요
5. 학년별 분포가 제공된 경우 그대로 사용하세요

데이터를 분석할 때 반드시 행들을 하나씩 확인하며 여러 컬럼의 값을 결합하여 통계를 내세요.

[중요한 규칙 - 퍼센트 표시]
데이터를 집계하여 제시할 때는 반드시 백분율(%)을 포함해야 합니다:
- 항목별로 분류된 데이터를 제시할 때는 각 항목의 응답자 수와 함께 전체 대비 백분율을 표시하세요
- 예시: "학습 도움 도구로서의 역할 (응답률 87%)"
- 예시: "모르는 문제를 이해하기 쉽게 설명해준다 (72%)"
- 포인트 1, 2, 3, 4와 같이 번호를 매긴 목록을 만들 때는 각 포인트에 해당하는 백분율을 반드시 포함하세요"""
        if search_results:
            system_prompt += "\n\n웹 검색 결과가 포함된 경우, 출처를 명확히 밝히고 시트 데이터와 통합하여 분석해주세요."
        
        # Build messages array with conversation history
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                if msg.get('role') and msg.get('content'):
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
        
        # Add current user question with data context
        messages.append({"role": "user", "content": prompt})
        
        # Log conversation context for debugging
        print(f"Conversation history length: {len(conversation_history)}")
        print(f"Total messages to Claude: {len(messages)}")
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=messages,
            temperature=0.7,
            max_tokens=1500  # 웹 검색 결과 포함 시 더 긴 답변 허용
        )
        
        answer = response.content[0].text
        print(f"\n=== RESPONSE PROCESSING STARTED ===")
        print(f"Raw answer from Claude: {answer[:100]}...")
        
        # Debug logging
        print(f"\n=== TIMESTAMP DEBUG ===")
        print(f"Original answer starts with: {answer[:50]}...")
        print(f"Data context: {data_context}")
        
        # Check if the answer starts with the required timestamp phrase
        required_starts = [
            f"{survey_date} 진행된 조사 결과에 따르면,",
            f"{data_context} 기준 데이터를 분석한 결과,",
            "최근 수집된 조사 자료에 의하면,"
        ]
        
        # Also check for partial timestamps (without month)
        partial_timestamps = [
            "데이터를 분석해보면,",
            "조사 결과에 따르면,"
        ]
        
        # Check which phrase it starts with, if any
        starts_with_required = False
        starts_with_partial = False
        
        # First check for exact matches
        for start in required_starts:
            if answer.startswith(start):
                print(f"Answer already starts with required phrase: {start}")
                starts_with_required = True
                break
        
        # If no exact match, check for partial timestamps
        if not starts_with_required:
            for partial in partial_timestamps:
                if answer.startswith(partial):
                    print(f"Answer starts with partial timestamp: {partial}")
                    starts_with_partial = True
                    # Determine the appropriate date to use based on context
                    date_to_use = survey_date
                    # If tablet question, find the date for the sheet containing tablets
                    if '태블릿' in user_question and sheet_dates:
                        for sheet_name, date in sheet_dates.items():
                            if sheet_name == 'Sheet2':  # We know tablets are in Sheet2
                                date_to_use = date
                                break
                    # Replace the partial timestamp with the appropriate date
                    answer = answer.replace(partial, f"{date_to_use} 진행된 조사 결과에 따르면,", 1)
                    print(f"Replaced with date: {date_to_use}")
                    break
        
        # If no timestamp at all, prepend one
        if not starts_with_required and not starts_with_partial:
            print("Answer does NOT start with any timestamp. Adding timestamp...")
            # Determine the appropriate date to use
            date_to_use = survey_date
            if '태블릿' in user_question and sheet_dates:
                for sheet_name, date in sheet_dates.items():
                    if sheet_name == 'Sheet2':
                        date_to_use = date
                        break
            answer = f"{date_to_use} 진행된 조사 결과에 따르면, {answer}"
            print(f"Modified answer starts with: {answer[:50]}...")
        
        print("=== END TIMESTAMP DEBUG ===")
        
        # Use custom Unicode-safe JSON response
        response_data = {
            'answer': answer,
            'data_count': len(sheet_data)
        }
        
        if search_results:
            response_data['web_search_count'] = len(search_results)
            response_data['search_sources'] = [{
                'title': r['title'],
                'link': r['link'],
                'source': r['displayLink']
            } for r in search_results]
        
        return jsonify_unicode(response_data)
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/demographics', methods=['GET'])
def demographics():
    """Get demographic statistics from Google Sheets data"""
    try:
        sheet_data = get_google_sheets_data()
        
        if not sheet_data:
            return jsonify_unicode({'error': '데이터가 없습니다.'}), 400
        
        # Initialize counters
        gender_count = {}
        school_year_count = {}
        geography_count = {}
        gpt_usage_count = 0
        gemini_usage_count = 0
        total_students = len(sheet_data)
        
        # Count demographics
        for row in sheet_data:
            # Gender
            gender = row.get('성별이 어떻게 되나요?', '').strip()
            if gender:
                gender_count[gender] = gender_count.get(gender, 0) + 1
            
            # School year - group into categories
            school_year = row.get('현재 학년이 어떻게 되나요?', '').strip()
            if school_year:
                # Group elementary school
                if school_year in ['초1', '초2', '초3', '초4', '초5', '초6']:
                    school_year_count['초등학생'] = school_year_count.get('초등학생', 0) + 1
                # Group middle school
                elif school_year in ['중1', '중2', '중3']:
                    school_year_count['중학생'] = school_year_count.get('중학생', 0) + 1
                # Group high school
                elif school_year in ['고1', '고2', '고3']:
                    school_year_count['고등학생'] = school_year_count.get('고등학생', 0) + 1
                # Keep others as is
                else:
                    school_year_count[school_year] = school_year_count.get(school_year, 0) + 1
            
            # Geography
            geography = row.get('현재 거주중인 지역이 어디인가요? ', '').strip()
            if geography:
                geography_count[geography] = geography_count.get(geography, 0) + 1
            
            # GPT/Gemini usage (checking multiple relevant columns)
            # Check general usage
            general_usage = row.get('GPT, Gemini와 같은 LLM 인공지능 서비스를 *평소에 활용*하고 계신가요?', '').strip()
            # Check math usage
            math_usage = row.get('GPT, Gemini와 같은 LLM 인공지능 서비스를 *수학 문제를 풀때*에도 사용하고 계신가요?', '').strip()
            
            # Count as user only if they answered exactly these responses
            target_responses = ['네 활발하게 사용하고 있습니다', '네 가끔 사용합니다']
            if general_usage in target_responses or math_usage in target_responses:
                gpt_usage_count += 1
        
        # Calculate percentages for individual data points
        gender_percentages = {}
        for gender, count in gender_count.items():
            gender_percentages[gender] = round((count / total_students) * 100, 1)
        
        school_year_percentages = {}
        for year, count in school_year_count.items():
            school_year_percentages[year] = round((count / total_students) * 100, 1)
        
        geography_percentages = {}
        for region, count in geography_count.items():
            geography_percentages[region] = round((count / total_students) * 100, 1)
        
        gpt_usage_percentage = round((gpt_usage_count / total_students) * 100, 1)
        
        return jsonify_unicode({
            'gender': gender_percentages,
            'school_year': school_year_percentages,
            'geography': geography_percentages,
            'llm_usage_percentage': gpt_usage_percentage,
            'total_count': total_students
        })
    
    except Exception as e:
        print(f"Error in demographics endpoint: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/sheets', methods=['GET'])
def list_sheets():
    """List all available sheets in the Google Sheets document"""
    try:
        sheet_info = get_all_sheet_names()
        
        # Get count from each sheet
        sheet_details = []
        for sheet in sheet_info:
            sheet_data = get_sheet_data_by_gid(sheet['gid'], sheet['name'])
            sheet_details.append({
                'name': sheet['name'],
                'gid': sheet['gid'],
                'row_count': len(sheet_data)
            })
        
        return jsonify_unicode({
            'sheets': sheet_details,
            'total_sheets': len(sheet_details)
        })
    
    except Exception as e:
        print(f"Error listing sheets: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/interview-info', methods=['POST'])
def get_interview_info():
    """Get participant information from interview document"""
    try:
        data = request.json
        document_id = data.get('document_id', '')
        
        if not document_id:
            return jsonify({'error': 'Missing document_id'}), 400
        
        # Fetch document content
        doc_content = get_google_docs_content(document_id)
        
        if not doc_content:
            return jsonify_unicode({
                'error': 'Could not fetch document content',
                'participants': []
            }), 404
        
        # Extract participant information
        participants = extract_participant_info(doc_content)
        
        # Get interview date from content if possible
        interview_date = None
        lines = doc_content.split('\n')
        for line in lines[:10]:  # Check first 10 lines for date
            if '2025' in line or '2024' in line or '2023' in line:
                # Try to extract date
                import re
                date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', line)
                if date_match:
                    year = date_match.group(1)
                    month = date_match.group(2)
                    day = date_match.group(3)
                    interview_date = f"{year}년 {month}월 {day}일"
                    break
        
        return jsonify_unicode({
            'participants': participants,
            'interview_date': interview_date,
            'total_participants': len(participants)
        })
    
    except Exception as e:
        print(f"Error in interview-info endpoint: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/sheet-info', methods=['POST'])
def get_sheet_info():
    """Get detailed information about a specific sheet"""
    try:
        data = request.json
        sheet_gid = data.get('sheet_gid', DEFAULT_SHEET_GID)
        sheet_name = data.get('sheet_name', 'Sheet1')
        spreadsheet_id = data.get('spreadsheet_id', SPREADSHEET_ID)
        source_type = data.get('source_type', 'survey')
        document_id = data.get('document_id', None)
        
        # Handle interview data
        if source_type == 'interview' and document_id:
            # Fetch document content
            doc_content = get_google_docs_content(document_id)
            
            if not doc_content:
                return jsonify_unicode({
                    'source_type': 'interview',
                    'participants': [],
                    'interview_date': None,
                    'total_participants': 0,
                    'error': 'Could not fetch document content'
                })
            
            # Extract participant information
            participants = extract_participant_info(doc_content)
            
            # Extract interview description
            description = extract_interview_description(doc_content)
            
            # Get interview date from content if possible
            interview_date = None
            lines = doc_content.split('\n')
            for line in lines[:10]:  # Check first 10 lines for date
                if '2025' in line or '2024' in line or '2023' in line:
                    # Try to extract date
                    import re
                    date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', line)
                    if date_match:
                        year = date_match.group(1)
                        month = date_match.group(2)
                        day = date_match.group(3)
                        interview_date = f"{year}년 {month}월 {day}일"
                        break
            
            return jsonify_unicode({
                'source_type': 'interview',
                'participants': participants,
                'description': description,
                'interview_date': interview_date,
                'total_participants': len(participants)
            })
        
        # Handle survey data (existing code)
        # Get sheet data
        sheet_data = get_sheet_data_by_gid(sheet_gid, sheet_name, spreadsheet_id)
        
        if not sheet_data:
            return jsonify_unicode({
                'total_rows': 0,
                'columns': [],
                'demographics': {},
                'survey_date': None
            })
        
        # Get columns
        columns = list(sheet_data[0].keys()) if sheet_data else []
        
        # Get survey date
        survey_date = None
        from datetime import datetime
        if sheet_data:
            timestamp_str = sheet_data[0].get('Submitted At', '') or sheet_data[0].get('Submitted at', '')
            print(f"DEBUG: timestamp_str = '{timestamp_str}'")
            if timestamp_str:
                try:
                    date_parsed = False
                    # Handle Korean date format first
                    if '오전' in timestamp_str or '오후' in timestamp_str:
                        try:
                            date_part = timestamp_str.split(' 오')[0].strip()
                            # Try with periods
                            try:
                                date_obj = datetime.strptime(date_part, '%Y. %m. %d')
                            except:
                                # Try without periods
                                date_obj = datetime.strptime(date_part, '%Y. %m. %d.')
                            survey_date = f"{date_obj.year}년 {date_obj.month}월"
                            date_parsed = True
                            print(f"DEBUG: Parsed Korean date format: {survey_date}")
                        except Exception as e:
                            print(f"DEBUG: Failed to parse Korean date: {e}")
                            pass
                    
                    # Handle short format like "2025. 01"
                    if not date_parsed and '. ' in timestamp_str and len(timestamp_str) <= 10:
                        try:
                            parts = timestamp_str.strip().split('. ')
                            if len(parts) == 2:
                                year = int(parts[0])
                                month = int(parts[1])
                                survey_date = f"{year}년 {month}월"
                                date_parsed = True
                        except:
                            pass
                    
                    # Try other formats
                    if not date_parsed:
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%d/%m/%Y %H:%M:%S']:
                            try:
                                date_obj = datetime.strptime(timestamp_str.split('.')[0], fmt)
                                survey_date = f"{date_obj.year}년 {date_obj.month}월"
                                date_parsed = True
                                break
                            except:
                                continue
                except:
                    pass
        
        # Calculate demographics
        demographics = {
            'grades': {},
            'genders': {}
        }
        
        for row in sheet_data:
            # Check for grade data - handle both column name formats
            grade = row.get('현재 학년이 어떻게 되나요?', row.get('학년', '')).strip()
            if grade:
                # Handle formats like "01. 중2"
                if '. ' in grade:
                    grade = grade.split('. ', 1)[1]
                demographics['grades'][grade] = demographics['grades'].get(grade, 0) + 1
            
            # Check for gender data - handle both column name formats
            gender = row.get('성별이 어떻게 되나요?', row.get('성별', '')).strip()
            if gender:
                # Handle formats like "01. 남" 
                if '. ' in gender:
                    gender = gender.split('. ', 1)[1]
                demographics['genders'][gender] = demographics['genders'].get(gender, 0) + 1
        
        return jsonify_unicode({
            'total_rows': len(sheet_data),
            'columns': columns,
            'demographics': demographics,
            'survey_date': survey_date
        })
    
    except Exception as e:
        print(f"Error in sheet-info endpoint: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/add-data-source', methods=['POST'])
def add_data_source():
    """Add a new custom data source from Google Sheets or Google Docs URL"""
    try:
        data = request.json
        title = data.get('title', '')
        data_type = data.get('type', 'survey')  # Default to survey for backward compatibility
        
        if not title:
            return jsonify({'error': 'Missing required field: title'}), 400
        
        # Load existing data sources
        sources = load_data_sources()
        
        if data_type == 'survey':
            # Handle Google Sheets data source
            spreadsheet_id = data.get('spreadsheet_id', '')
            gid = data.get('gid', '')
            
            if not spreadsheet_id or not gid:
                return jsonify({'error': 'Missing required fields for survey data: spreadsheet_id or gid'}), 400
            
            # Check if GID already exists
            for source in sources:
                if source.get('gid') == gid and source.get('spreadsheet_id') == spreadsheet_id:
                    return jsonify({'error': 'This sheet is already added'}), 409
            
            # Add new survey source
            new_source = {
                'title': title,
                'type': 'survey',
                'spreadsheet_id': spreadsheet_id,
                'gid': gid,
                'added_at': datetime.now().isoformat()
            }
            
        elif data_type == 'interview':
            # Handle Google Docs data source
            document_id = data.get('document_id', '')
            
            if not document_id:
                return jsonify({'error': 'Missing required field for interview data: document_id'}), 400
            
            # Check if document already exists
            for source in sources:
                if source.get('document_id') == document_id:
                    return jsonify({'error': 'This document is already added'}), 409
            
            # Add new interview source
            new_source = {
                'title': title,
                'type': 'interview',
                'document_id': document_id,
                'added_at': datetime.now().isoformat()
            }
        else:
            return jsonify({'error': 'Invalid data type. Must be "survey" or "interview"'}), 400
        
        sources.append(new_source)
        
        # Save updated sources
        if save_data_sources(sources):
            return jsonify_unicode({
                'status': 'success',
                'message': 'Data source added successfully',
                'source': new_source
            })
        else:
            return jsonify({'error': 'Failed to save data source'}), 500
    
    except Exception as e:
        print(f"Error in add-data-source endpoint: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/update-data-source', methods=['PUT'])
def update_data_source():
    """Update a data source title"""
    try:
        data = request.json
        print(f"\n=== UPDATE DATA SOURCE REQUEST ===")
        print(f"Raw request data: {data}")
        
        gid = data.get('gid', '')
        document_id = data.get('document_id', '')
        spreadsheet_id = data.get('spreadsheet_id', '')
        new_title = data.get('title', '')
        data_type = data.get('type', 'survey')
        
        print(f"Parsed values:")
        print(f"  - type: {data_type}")
        print(f"  - title: {new_title}")
        print(f"  - gid: {gid}")
        print(f"  - document_id: {document_id}")
        print(f"  - spreadsheet_id: {spreadsheet_id}")
        print(f"=================================\n")
        
        if not new_title:
            return jsonify({'error': 'Missing required field: title'}), 400
        
        # Check based on data type
        if data_type == 'interview' and not document_id:
            print(f"ERROR: Interview type but no document_id provided")
            return jsonify({'error': 'Missing required field for interview data: document_id'}), 400
        elif data_type == 'survey' and not gid:
            print(f"ERROR: Survey type but no gid provided")
            return jsonify({'error': 'Missing required field for survey data: gid'}), 400
        
        # Check if it's a default sheet (from main spreadsheet)
        # Only check for default sheets if it's a survey type with matching spreadsheet_id
        if data_type == 'survey' and spreadsheet_id == SPREADSHEET_ID:
            # For default sheets, we'll store custom titles separately
            custom_titles_file = os.path.join(os.path.dirname(__file__), 'custom_sheet_titles.json')
            custom_titles = {}
            
            if os.path.exists(custom_titles_file):
                try:
                    with open(custom_titles_file, 'r', encoding='utf-8') as f:
                        custom_titles = json.load(f)
                except:
                    pass
            
            # Update or add the custom title
            custom_titles[gid] = new_title
            
            # Save the custom titles
            with open(custom_titles_file, 'w', encoding='utf-8') as f:
                json.dump(custom_titles, f, ensure_ascii=False, indent=2)
            
            return jsonify_unicode({
                'status': 'success',
                'message': 'Title updated successfully'
            })
        else:
            # For custom data sources, update in the data_sources.json
            sources = load_data_sources()
            
            # Find and update the source
            updated = False
            for i, source in enumerate(sources):
                # Check based on type
                if data_type == 'interview':
                    # For interview sources, match by document_id
                    if source.get('type') == 'interview' and source.get('document_id') == document_id:
                        source['title'] = new_title
                        updated = True
                        break
                else:
                    # For survey sources, match by gid and spreadsheet_id
                    if source.get('gid') == gid and source.get('spreadsheet_id') == spreadsheet_id:
                        # Update title
                        source['title'] = new_title
                        
                        # If the request includes new spreadsheet_id or gid, this means URL was changed
                        new_spreadsheet_id = data.get('new_spreadsheet_id')
                        new_gid = data.get('new_gid')
                        
                        if new_spreadsheet_id and new_gid:
                            # Check if the new GID already exists
                            for other_source in sources:
                                if other_source.get('gid') == new_gid and other_source.get('spreadsheet_id') == new_spreadsheet_id and other_source != source:
                                    return jsonify({'error': 'A data source with this spreadsheet ID and GID already exists'}), 409
                            
                            # Update the spreadsheet_id and gid
                            source['spreadsheet_id'] = new_spreadsheet_id
                            source['gid'] = new_gid
                        
                        updated = True
                        break
            
            if updated:
                save_data_sources(sources)
                return jsonify_unicode({
                    'status': 'success',
                    'message': 'Data source updated successfully'
                })
            else:
                return jsonify({'error': 'Data source not found'}), 404
    
    except Exception as e:
        print(f"Error in update-data-source endpoint: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/data-sources', methods=['GET'])
def get_data_sources():
    """Get all data sources including custom ones"""
    try:
        # Get default sheets from the main spreadsheet
        default_sheets = get_all_sheet_names()
        
        # Load custom data sources
        custom_sources = load_data_sources()
        
        # Load custom titles for default sheets
        custom_titles = {}
        custom_titles_file = os.path.join(os.path.dirname(__file__), 'custom_sheet_titles.json')
        if os.path.exists(custom_titles_file):
            try:
                with open(custom_titles_file, 'r', encoding='utf-8') as f:
                    custom_titles = json.load(f)
            except:
                pass
        
        # Format response
        all_sources = []
        
        # Add default sheets with custom titles if available
        for sheet in default_sheets:
            all_sources.append({
                'title': custom_titles.get(sheet['gid'], sheet['name']),  # Use custom title if available
                'original_title': sheet['name'],  # Keep original title for reference
                'type': 'survey',  # Default sheets are always survey type
                'spreadsheet_id': SPREADSHEET_ID,
                'gid': sheet['gid'],
                'is_default': True
            })
        
        # Add custom sources
        for source in custom_sources:
            # Check if there's a custom title for this source too
            title = custom_titles.get(source['gid'], source['title']) if source.get('gid') else source['title']
            source_data = {
                'title': title,
                'original_title': source['title'],  # Keep original for reference
                'type': source.get('type', 'survey'),  # Default to survey for backward compatibility
                'is_default': False,
                'added_at': source.get('added_at')
            }
            
            # Add fields based on type
            if source.get('type') == 'interview':
                source_data['document_id'] = source.get('document_id')
            else:
                source_data['spreadsheet_id'] = source.get('spreadsheet_id')
                source_data['gid'] = source.get('gid')
            
            all_sources.append(source_data)
        
        return jsonify_unicode({
            'sources': all_sources,
            'total': len(all_sources)
        })
    
    except Exception as e:
        print(f"Error in data-sources endpoint: {str(e)}")
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify_unicode({'status': 'ok', 'version': 'v3.1-interview-edit-fix-2025-01-25'})

@app.route('/api/debug/sheet-data', methods=['GET'])
def debug_sheet_data():
    """디버그용: 현재 시트 데이터 확인"""
    try:
        sheet_data = get_google_sheets_data()
        response_data = {
            'spreadsheet_id': SPREADSHEET_ID,
            'range': RANGE_NAME,
            'data_count': len(sheet_data),
            'headers': list(sheet_data[0].keys()) if sheet_data else [],
            'first_row': sheet_data[0] if sheet_data else None,
            'all_names': [row.get('이름을 적어주세요', row.get('이름', row.get('Name', ''))) for row in sheet_data] if sheet_data else []
        }
        # Create response with explicit UTF-8 encoding
        response = make_response(json.dumps(response_data, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

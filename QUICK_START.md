# 🚀 빠른 시작 가이드

## 1️⃣ OpenAI API 키 설정

⚠️ **중요**: 이전에 공유하신 API 키는 노출되었으므로 즉시 삭제하고 새로 생성하세요!

1. [OpenAI API Keys](https://platform.openai.com/api-keys)에서 새 API 키 생성
2. `.env` 파일 편집:
   ```bash
   cd backend
   nano .env  # 또는 원하는 텍스트 에디터 사용
   ```
3. `OPENAI_API_KEY=YOUR_NEW_OPENAI_API_KEY_HERE`를 실제 API 키로 교체

## 2️⃣ 구글 시트 설정

다음 중 하나를 선택:

### 옵션 A: 시트를 공개로 설정 (가장 간단)
1. [구글 시트](https://docs.google.com/spreadsheets/d/17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ/edit) 열기
2. 공유 → 일반 액세스 → "링크가 있는 모든 사용자" 선택

### 옵션 B: Google API 키 사용
1. [Google Cloud Console](https://console.cloud.google.com/)에서 API 키 생성
2. `.env` 파일에 추가: `GOOGLE_API_KEY=your_google_api_key`

## 3️⃣ 서버 실행

### 터미널 1 - 백엔드 실행:
```bash
cd /Users/churryboy/sheet-llm-chatbot/backend
source venv/bin/activate
python app.py
```

### 터미널 2 - 프론트엔드 실행:
```bash
cd /Users/churryboy/sheet-llm-chatbot/frontend
python3 -m http.server 8000
```

## 4️⃣ 웹사이트 접속

브라우저에서 http://localhost:8000 열기

## 💬 테스트 질문

- "어떤 사람들이 있나요?"
- "iPhone을 좋아하는 사람은 누구인가요?"
- "가장 인기 있는 아이템은 무엇인가요?"

## 🔧 문제 해결

### "서버와 연결할 수 없습니다" 오류
- 백엔드가 실행 중인지 확인 (터미널 1)
- 콘솔에서 에러 메시지 확인

### Google Sheets API 오류
- 시트가 공개로 설정되었는지 확인
- 또는 유효한 Google API 키가 설정되었는지 확인

### OpenAI API 오류
- API 키가 올바르게 설정되었는지 확인
- API 키에 충분한 크레딧이 있는지 확인

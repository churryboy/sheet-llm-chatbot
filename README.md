# Google Sheets + LLM 챗봇

구글 시트 데이터를 기반으로 질문에 답변하는 AI 챗봇 웹 애플리케이션입니다.

## 📋 기능

- 구글 시트 데이터를 실시간으로 읽어오기
- OpenAI GPT-4를 사용하여 데이터 기반 답변 생성
- 직관적인 채팅 인터페이스
- 반응형 웹 디자인

## 🛠 기술 스택

- **프론트엔드**: HTML, CSS, JavaScript (Vanilla)
- **백엔드**: Python, Flask
- **LLM**: OpenAI GPT-4
- **데이터**: Google Sheets API
- **배포**: Vercel (프론트엔드), Render/Railway (백엔드)

## 🚀 시작하기

### 1. 사전 준비사항

- Python 3.8 이상
- Node.js (Vercel CLI용)
- OpenAI API 키
- Google Cloud Console 계정

### 2. Google Sheets API 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Google Sheets API 활성화
4. 다음 중 하나 선택:
   - **API Key** (공개 시트용): 자격 증명 > API 키 생성
   - **서비스 계정** (비공개 시트용): 서비스 계정 생성 > JSON 키 다운로드

### 3. 백엔드 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# .env 파일 생성 (.env.example 참고)
cp .env.example .env
```

`.env` 파일 편집:
```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  # API Key 사용시
```

서비스 계정 사용시: `credentials.json` 파일을 backend 폴더에 복사

### 4. 백엔드 실행

```bash
python app.py
```

백엔드가 http://localhost:5000 에서 실행됩니다.

### 5. 프론트엔드 실행

새 터미널을 열고:

```bash
cd frontend

# 간단한 HTTP 서버 실행 (Python)
python -m http.server 8000

# 또는 Node.js 사용시
npx http-server -p 8000
```

브라우저에서 http://localhost:8000 접속

## 📦 배포

### 프론트엔드 배포 (Vercel)

1. [Vercel](https://vercel.com) 계정 생성
2. Vercel CLI 설치: `npm i -g vercel`
3. frontend 폴더에서 실행:
```bash
cd frontend
vercel
```

4. `script.js`의 API_URL을 백엔드 URL로 업데이트

### 백엔드 배포 (Render)

1. [Render](https://render.com) 계정 생성
2. GitHub에 backend 코드 푸시
3. Render에서 새 Web Service 생성
4. 환경 변수 설정:
   - `OPENAI_API_KEY`
   - `GOOGLE_API_KEY`
5. 배포 시작

## 📝 사용 방법

1. 웹사이트 접속
2. 채팅창에 구글 시트 데이터에 대한 질문 입력
3. 예시 질문:
   - "어떤 사람들이 있나요?"
   - "iPhone을 좋아하는 사람은 누구인가요?"
   - "가장 인기 있는 아이템은 무엇인가요?"

## ⚙️ 환경 변수

### 백엔드 (.env)
- `OPENAI_API_KEY`: OpenAI API 키
- `GOOGLE_API_KEY`: Google API 키 (공개 시트용)

### 프론트엔드
- `API_URL`: 백엔드 API 엔드포인트 (script.js에서 수정)

## 🔧 문제 해결

### CORS 오류
- 백엔드의 Flask-CORS가 제대로 설정되어 있는지 확인
- 프론트엔드의 API_URL이 올바른지 확인

### Google Sheets API 오류
- API가 활성화되어 있는지 확인
- 시트가 공개로 설정되어 있거나 서비스 계정에 권한이 있는지 확인

### OpenAI API 오류
- API 키가 유효한지 확인
- API 사용량 한도를 확인

## 📄 라이선스

MIT License

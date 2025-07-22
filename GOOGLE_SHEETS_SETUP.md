# Google Sheets 공개 설정 가이드

## 🔓 구글 시트를 공개로 설정하기

API 키 없이 구글 시트 데이터를 읽으려면 시트를 공개로 설정해야 합니다.

### 방법 1: 링크가 있는 모든 사용자에게 공유 (권장)

1. 구글 시트 열기: https://docs.google.com/spreadsheets/d/17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ/edit
2. 오른쪽 상단의 **"공유"** 버튼 클릭
3. **"일반 액세스"** 섹션에서 설정 변경:
   - "제한됨" → **"링크가 있는 모든 사용자"**로 변경
   - 권한을 **"뷰어"**로 설정
4. **"완료"** 클릭

### 방법 2: Google API 키 사용

Google Sheets API 키를 생성하여 사용할 수도 있습니다:

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택 또는 새 프로젝트 생성
3. **"API 및 서비스"** → **"라이브러리"**
4. **"Google Sheets API"** 검색 후 활성화
5. **"API 및 서비스"** → **"사용자 인증 정보"**
6. **"+ 사용자 인증 정보 만들기"** → **"API 키"**
7. 생성된 API 키를 `.env` 파일에 추가:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### 방법 3: 서비스 계정 사용 (고급)

비공개 시트를 사용하려면:

1. Google Cloud Console에서 서비스 계정 생성
2. JSON 키 파일 다운로드
3. `credentials.json`으로 이름 변경 후 `backend` 폴더에 저장
4. 구글 시트에서 서비스 계정 이메일에 권한 부여

## 🔍 현재 시트 확인

현재 연동된 시트:
- ID: `17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ`
- URL: https://docs.google.com/spreadsheets/d/17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ/edit

## ⚠️ 주의사항

- 공개 시트는 누구나 볼 수 있으므로 민감한 데이터는 넣지 마세요
- API 키는 절대 공개하지 마세요
- 서비스 계정 키 파일(`credentials.json`)도 공개하지 마세요

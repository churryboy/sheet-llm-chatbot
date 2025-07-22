# 학생 데이터 수집 기능 설정 가이드

이 가이드는 학생 정보를 Google Sheets에 저장하는 기능을 설정하는 방법을 설명합니다.

## 새로 추가된 파일들

1. **data-form.html** - 학생 정보 입력 폼 페이지
2. **form-styles.css** - 입력 폼 스타일링
3. **form-script.js** - 폼 제출 처리 JavaScript
4. **google-apps-script.js** - Google Sheets 연동 스크립트

## Google Apps Script 설정 방법

### 1단계: Google Sheets 열기
- 다음 링크로 이동: https://docs.google.com/spreadsheets/d/17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ/edit

### 2단계: Apps Script 편집기 열기
- 메뉴에서 `확장 프로그램` > `Apps Script` 클릭

### 3단계: 스크립트 코드 추가
- 편집기의 모든 기존 코드를 삭제
- `google-apps-script.js` 파일의 전체 내용을 복사하여 붙여넣기
- `Ctrl+S` (또는 Mac에서 `Cmd+S`)로 저장

### 4단계: 웹 앱으로 배포
1. 상단 메뉴에서 `배포` > `새 배포` 클릭
2. 톱니바퀴 아이콘 클릭 > `웹 앱` 선택
3. 다음과 같이 설정:
   - **설명**: Student Data Collection
   - **다음 사용자로 실행**: 나
   - **액세스 권한이 있는 사용자**: 모든 사용자
4. `배포` 버튼 클릭

### 5단계: 권한 승인
- 처음 배포 시 Google 계정 권한 승인 필요
- "검증되지 않은 앱" 경고가 나타나면 `고급` > `안전하지 않은 페이지로 이동` 클릭
- 필요한 권한 승인

### 6단계: 웹 앱 URL 복사
- 배포 완료 후 나타나는 웹 앱 URL 복사
- URL 형식: `https://script.google.com/macros/s/[SCRIPT_ID]/exec`

### 7단계: form-script.js 업데이트
- `form-script.js` 파일 열기
- 2번째 줄의 `YOUR_SCRIPT_ID`를 복사한 URL로 교체:
  ```javascript
  const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/실제_스크립트_ID/exec';
  ```

## 사용 방법

1. 웹사이트에서 우측 상단의 "Add Data" 버튼 클릭
2. 학생 정보 입력
3. "제출" 버튼 클릭
4. 데이터가 Google Sheets에 자동으로 저장됨

## 수집되는 데이터 필드

1. **제출 시간** - 자동 기록
2. **이름** (필수)
3. **출생년도** (필수)
4. **학년** (필수)
5. **학교 이름** (필수)
6. **거주 도시** (필수)
7. **내신 점수** (선택)
8. **모의고사 점수** (선택)
9. **공부 스타일** (선택)
10. **선호하는 공부법** (선택)
11. **공부하면서 힘든 부분** (선택)
12. **콴다에 바라는 기능** (선택)

## 문제 해결

### 제출이 안 되는 경우
1. Google Apps Script URL이 올바르게 설정되었는지 확인
2. Google Apps Script가 배포되었는지 확인
3. 브라우저 콘솔에서 에러 메시지 확인

### CORS 에러
- `mode: 'no-cors'` 설정이 있는지 확인
- Google Apps Script 설정에서 "모든 사용자" 액세스 권한 확인

## 보안 참고사항
- 민감한 개인정보는 수집하지 않도록 주의
- Google Sheets 액세스 권한을 적절히 관리
- 정기적으로 수집된 데이터 백업

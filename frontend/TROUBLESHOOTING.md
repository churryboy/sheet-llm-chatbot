# Google Sheets 연동 문제 해결 가이드

## 문제: 데이터가 Google Sheet에 도착하지 않음

### 1. Google Apps Script가 올바르게 배포되었는지 확인

1. **Google Sheet 열기**: https://docs.google.com/spreadsheets/d/17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ/edit
2. **확장 프로그램 > Apps Script** 클릭
3. **google-apps-script-simple.js** 파일의 내용을 복사하여 붙여넣기
4. **저장** (Ctrl+S)
5. **배포 > 새 배포** 클릭
6. 다음과 같이 설정:
   - **선택 유형**: 웹 앱
   - **설명**: Student Data Collection
   - **다음 사용자로 실행**: 나
   - **액세스 권한이 있는 사용자**: 모든 사용자
7. **배포** 클릭
8. **웹 앱 URL 복사** (예: https://script.google.com/macros/s/AKfycbxxxxxx/exec)

### 2. form-script.js 파일 업데이트

`form-script.js` 파일을 열고 2번째 줄을 수정:

```javascript
// 이전 (작동 안함)
const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec';

// 수정 후 (실제 URL로 교체)
const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxxxxxx/exec';
```

### 3. 테스트 페이지 사용

1. 브라우저에서 `test-google-script.html` 파일 열기
2. Google Apps Script URL 입력
3. "테스트 데이터 전송" 클릭
4. Google Sheet에서 데이터 확인

### 4. 브라우저 콘솔 확인

1. 개발자 도구 열기 (F12)
2. Console 탭 확인
3. 에러 메시지 확인

### 5. Google Apps Script 실행 기록 확인

1. Apps Script 편집기에서
2. 왼쪽 메뉴의 "실행" 클릭
3. 최근 실행 기록 확인
4. 에러가 있으면 클릭하여 상세 내용 확인

### 6. 권한 문제 해결

Apps Script 첫 배포 시:
1. "검증되지 않은 앱" 경고가 나타나면
2. "고급" 클릭
3. "안전하지 않은 페이지로 이동" 클릭
4. 필요한 권한 승인

### 7. CORS 문제 우회

form-script.js에서 `mode: 'no-cors'`가 설정되어 있는지 확인:

```javascript
const response = await fetch(GOOGLE_SCRIPT_URL, {
    method: 'POST',
    mode: 'no-cors',  // 이 줄이 있어야 함
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
```

### 8. 대체 방법: URL 파라미터 사용

만약 JSON POST가 작동하지 않으면, form-script.js를 다음과 같이 수정:

```javascript
// URL 파라미터로 데이터 전송
const params = new URLSearchParams(data);
const response = await fetch(GOOGLE_SCRIPT_URL, {
    method: 'POST',
    mode: 'no-cors',
    body: params
});
```

### 9. Google Sheet 권한 확인

- Google Sheet가 "링크가 있는 모든 사용자가 볼 수 있음"으로 설정되어 있는지 확인
- Apps Script가 Sheet에 쓰기 권한이 있는지 확인

### 10. 수동 테스트

Apps Script 편집기에서 직접 테스트:

```javascript
function testManual() {
  doPost({
    postData: {
      contents: JSON.stringify({
        name: "테스트",
        birthYear: "2000",
        grade: "고1",
        schoolName: "테스트 학교",
        city: "서울",
        timestamp: new Date().toLocaleString('ko-KR')
      })
    }
  });
}
```

실행 버튼을 클릭하여 테스트

## 여전히 작동하지 않는다면

1. Google Apps Script URL이 정확한지 다시 확인
2. 배포가 최신 버전인지 확인 (코드 수정 후 재배포 필요)
3. 다른 브라우저에서 테스트
4. 네트워크 탭에서 실제 요청이 전송되는지 확인

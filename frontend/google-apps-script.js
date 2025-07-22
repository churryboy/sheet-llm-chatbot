/**
 * Google Apps Script for Student Data Collection
 * 
 * 설치 방법:
 * 1. Google Sheets 열기: https://docs.google.com/spreadsheets/d/17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ/edit
 * 2. 확장 프로그램 > Apps Script 클릭
 * 3. 기존 코드를 모두 삭제하고 아래 코드 전체를 복사하여 붙여넣기
 * 4. 저장 (Ctrl+S 또는 Cmd+S)
 * 5. 배포 > 새 배포 클릭
 * 6. 설정에서 다음과 같이 선택:
 *    - 유형: 웹 앱
 *    - 설명: Student Data Collection
 *    - 다음 사용자로 실행: 나
 *    - 액세스 권한이 있는 사용자: 모든 사용자
 * 7. 배포 버튼 클릭
 * 8. 권한 승인 (처음 배포 시)
 * 9. 웹 앱 URL 복사
 * 10. form-script.js 파일의 GOOGLE_SCRIPT_URL을 복사한 URL로 교체
 */

function doPost(e) {
  try {
    // Google Sheet ID로 스프레드시트 열기
    const sheet = SpreadsheetApp.openById('17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ').getActiveSheet();
    
    // 디버깅을 위한 로그
    console.log('Received POST request:', e);
    
    // POST 요청으로 받은 데이터 파싱
    const data = JSON.parse(e.postData.contents);
    
    // 첫 번째 행이 비어있으면 헤더 추가
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        '제출 시간',
        '이름',
        '출생년도',
        '학년',
        '학교 이름',
        '거주 도시',
        '내신 점수',
        '모의고사 점수',
        '공부 스타일',
        '선호하는 공부법',
        '공부하면서 힘든 부분',
        '콴다에 바라는 기능'
      ]);
    }
    
    // 데이터를 시트에 추가
    sheet.appendRow([
      data.timestamp,
      data.name,
      data.birthYear,
      data.grade,
      data.schoolName,
      data.city,
      data.schoolScore,
      data.mockExamScore,
      data.studyStyle,
      data.preferredMethod,
      data.challengingPart,
      data.featureRequest
    ]);
    
    // 성공 응답 반환
    return ContentService.createTextOutput(JSON.stringify({
      result: 'success',
      message: '데이터가 성공적으로 저장되었습니다.'
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    // 에러 발생 시 에러 응답 반환
    console.error('Error in doPost:', error);
    return ContentService.createTextOutput(JSON.stringify({
      result: 'error',
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// GET 요청 처리 (테스트용)
function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: 'active',
    message: 'Student Data Collection API is running'
  })).setMimeType(ContentService.MimeType.JSON);
}

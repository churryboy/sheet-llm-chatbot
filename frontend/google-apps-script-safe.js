/**
 * 보안 문제를 피하는 간단한 Google Apps Script
 * 
 * 1. Apps Script 편집기에서 모든 코드 삭제
 * 2. 이 코드 전체를 복사/붙여넣기
 * 3. 저장 (Ctrl+S)
 * 4. 배포 > 새 배포
 * 5. 웹 앱으로 배포
 */

function doGet(e) {
  return handleRequest(e);
}

function doPost(e) {
  return handleRequest(e);
}

function handleRequest(e) {
  try {
    // 스프레드시트 열기
    const sheet = SpreadsheetApp.openById('17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ').getActiveSheet();
    
    // URL 파라미터에서 데이터 가져오기
    const params = e.parameter;
    
    // 헤더가 없으면 추가
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
    
    // 데이터 추가
    sheet.appendRow([
      new Date().toLocaleString('ko-KR'),
      params.name || '',
      params.birthYear || '',
      params.grade || '',
      params.schoolName || '',
      params.city || '',
      params.schoolScore || '',
      params.mockExamScore || '',
      params.studyStyle || '',
      params.preferredMethod || '',
      params.challengingPart || '',
      params.featureRequest || ''
    ]);
    
    // HTML 응답 반환 (CORS 문제 회피)
    return HtmlService.createHtmlOutput('<script>window.close();</script>');
    
  } catch (error) {
    return ContentService
      .createTextOutput('Error: ' + error.toString())
      .setMimeType(ContentService.MimeType.TEXT);
  }
}

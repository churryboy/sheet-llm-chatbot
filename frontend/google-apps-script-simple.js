/**
 * 간단한 Google Apps Script - 이 코드를 사용하세요
 * 
 * 1. Google Sheets에서 확장 프로그램 > Apps Script 클릭
 * 2. 모든 코드를 삭제하고 아래 코드 전체를 복사/붙여넣기
 * 3. 저장 (Ctrl+S)
 * 4. 배포 > 새 배포
 * 5. 유형: 웹 앱, 액세스: 모든 사용자
 */

function doPost(e) {
  // 스프레드시트 열기
  const sheet = SpreadsheetApp.openById('17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ').getActiveSheet();
  
  try {
    // 데이터 파싱
    let data;
    if (e.postData && e.postData.contents) {
      data = JSON.parse(e.postData.contents);
    } else if (e.parameter) {
      data = e.parameter;
    } else {
      throw new Error('No data received');
    }
    
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
      data.timestamp || new Date().toLocaleString('ko-KR'),
      data.name || '',
      data.birthYear || '',
      data.grade || '',
      data.schoolName || '',
      data.city || '',
      data.schoolScore || '',
      data.mockExamScore || '',
      data.studyStyle || '',
      data.preferredMethod || '',
      data.challengingPart || '',
      data.featureRequest || ''
    ]);
    
    // 성공 응답
    return ContentService
      .createTextOutput(JSON.stringify({result: 'success'}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    // 에러 응답
    return ContentService
      .createTextOutput(JSON.stringify({
        result: 'error',
        message: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// 테스트용 GET 메서드
function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'active',
      message: 'API is running'
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

// Google Apps Script Web App URL - You'll need to replace this with your actual URL
const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec';

document.getElementById('studentForm').addEventListener('submit', handleSubmit);

async function handleSubmit(e) {
    e.preventDefault();
    
    // Show loading
    document.getElementById('loading').style.display = 'flex';
    
    // Get form data
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        birthYear: formData.get('birthYear'),
        grade: formData.get('grade'),
        schoolName: formData.get('schoolName'),
        city: formData.get('city'),
        schoolScore: formData.get('schoolScore') || '',
        mockExamScore: formData.get('mockExamScore') || '',
        studyStyle: formData.get('studyStyle') || '',
        preferredMethod: formData.get('preferredMethod') || '',
        challengingPart: formData.get('challengingPart') || '',
        featureRequest: formData.get('featureRequest') || '',
        timestamp: new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
    };
    
    try {
        // Create URL with parameters
        const params = new URLSearchParams(data);
        const url = `${GOOGLE_SCRIPT_URL}?${params.toString()}`;
        
        // Open in hidden iframe to avoid CORS and security issues
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = url;
        document.body.appendChild(iframe);
        
        // Remove iframe after 3 seconds
        setTimeout(() => {
            document.body.removeChild(iframe);
        }, 3000);
        
        // Wait a bit for the request to complete
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        
        // Show success message
        document.getElementById('successMessage').style.display = 'flex';
        
    } catch (error) {
        console.error('Error:', error);
        
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        
        // Show error message
        alert('제출 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
}

// Add input validation for birth year
document.getElementById('birthYear').addEventListener('input', function(e) {
    const value = parseInt(e.target.value);
    const currentYear = new Date().getFullYear();
    
    if (value < 1990) {
        e.target.value = 1990;
    } else if (value > currentYear) {
        e.target.value = currentYear;
    }
});

// Instructions for setting up Google Apps Script
/*
 * Google Apps Script 설정 방법:
 * 
 * 1. Google Sheets 열기 (https://docs.google.com/spreadsheets/d/17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ/edit)
 * 2. 확장 프로그램 > Apps Script 클릭
 * 3. 아래 코드를 붙여넣기:
 * 
 * function doPost(e) {
 *   try {
 *     const sheet = SpreadsheetApp.openById('17jJx_ncFoa00ih6VRRO-cI5rqG_zZZu8PsDvEHZSDMQ').getActiveSheet();
 *     const data = JSON.parse(e.postData.contents);
 *     
 *     sheet.appendRow([
 *       data.timestamp,
 *       data.name,
 *       data.birthYear,
 *       data.grade,
 *       data.schoolName,
 *       data.city,
 *       data.schoolScore,
 *       data.mockExamScore,
 *       data.studyStyle,
 *       data.preferredMethod,
 *       data.challengingPart,
 *       data.featureRequest
 *     ]);
 *     
 *     return ContentService.createTextOutput(JSON.stringify({result: 'success'}))
 *       .setMimeType(ContentService.MimeType.JSON);
 *   } catch (error) {
 *     return ContentService.createTextOutput(JSON.stringify({result: 'error', error: error.toString()}))
 *       .setMimeType(ContentService.MimeType.JSON);
 *   }
 * }
 * 
 * 4. 저장 (Ctrl+S 또는 Cmd+S)
 * 5. 배포 > 새 배포 클릭
 * 6. 유형 선택: 웹 앱
 * 7. 설정:
 *    - 설명: Student Data Collection
 *    - 다음 사용자로 실행: 나
 *    - 액세스 권한이 있는 사용자: 모든 사용자
 * 8. 배포 클릭
 * 9. 웹 앱 URL 복사
 * 10. 이 파일의 GOOGLE_SCRIPT_URL을 복사한 URL로 교체
 */

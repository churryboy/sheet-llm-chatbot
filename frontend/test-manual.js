/**
 * Google Apps Script 수동 테스트
 * 
 * 이 코드를 Apps Script 편집기에 추가하고 직접 실행해보세요
 */

// 테스트 함수 - 편집기에서 직접 실행
function testAddData() {
  // 가짜 요청 객체 생성
  const fakeRequest = {
    parameter: {
      name: "테스트 학생",
      birthYear: "2005",
      grade: "고2",
      schoolName: "테스트 고등학교",
      city: "서울시 강남구",
      schoolScore: "90점",
      mockExamScore: "2등급",
      studyStyle: "자기주도 학습",
      preferredMethod: "인강 활용",
      challengingPart: "시간 관리",
      featureRequest: "AI 튜터 기능"
    }
  };
  
  // handleRequest 함수 호출
  const result = handleRequest(fakeRequest);
  
  // 결과 확인
  console.log("테스트 완료!");
  console.log("Google Sheet를 확인해보세요");
}

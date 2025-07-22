// API 엔드포인트 설정 (배포 시 변경 필요)
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5001/api/chat' 
    : 'https://YOUR-BACKEND-URL.onrender.com/api/chat'; // Replace with your Render URL

// 메시지 전송 함수
async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');
    
    const question = userInput.value.trim();
    if (question === '') return;
    
    // 버튼 비활성화
    sendButton.disabled = true;
    userInput.disabled = true;
    
    // 사용자 메시지 추가
    addMessage(question, 'user');
    
    // 봇 로딩 메시지 추가
    const botMessageElement = addMessage('', 'bot', true);
    
    // 스크롤 아래로
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        if (response.ok && data.answer) {
            // 로딩 제거하고 답변 표시
            botMessageElement.innerHTML = `<div class="message-content">${formatAnswer(data.answer)}</div>`;
        } else {
            botMessageElement.innerHTML = `<div class="message-content">오류: ${data.error || '알 수 없는 오류가 발생했습니다.'}</div>`;
        }
        
    } catch (error) {
        console.error('Error:', error);
        botMessageElement.innerHTML = '<div class="message-content">서버와 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.</div>';
    } finally {
        // 입력 필드 초기화 및 활성화
        userInput.value = '';
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// 메시지 추가 헬퍼 함수
function addMessage(content, sender, isLoading = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    if (isLoading) {
        messageDiv.innerHTML = '<div class="message-content"><div class="loading"></div></div>';
    } else {
        messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
    }
    
    chatMessages.appendChild(messageDiv);
    return messageDiv;
}

// 답변 포맷팅 함수
function formatAnswer(answer) {
    // 줄바꿈을 <br>로 변환
    return answer.replace(/\n/g, '<br>');
}

// 엔터키 이벤트 리스너
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// 페이지 로드 시 입력 필드에 포커스
window.addEventListener('load', function() {
    document.getElementById('user-input').focus();
});

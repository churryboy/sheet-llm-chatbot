// Version info for debugging
console.log('Script version: 2025-01-24-1257-custom-domain');
console.log('Current domain:', window.location.hostname);

// API 엔드포인트 설정 (배포 시 변경 필요)
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://sheet-llm-chatbot-backend.onrender.com'; // Render backend URL

const API_URL = `${API_BASE_URL}/api/chat`;
console.log('API Base URL:', API_BASE_URL);

// 현재 선택된 시트 정보
let currentSheet = {
    gid: '187909252',
    name: 'Sheet1'
};

// 채팅 기록 저장용 객체 (시트별로 대화 기록 보관)
let chatHistories = {};

// 현재 시트의 표시 이름을 가져오는 헬퍼 함수
function getSheetDisplayName(button) {
    const tabText = button.querySelector('.tab-text');
    return tabText ? tabText.textContent : button.textContent.trim();
}

// 시트 선택 함수
function selectSheet(button) {
    // 현재 대화 내용을 저장
    const chatMessages = document.getElementById('chat-messages');
    if (currentSheet.gid && chatMessages.innerHTML.trim()) {
        chatHistories[currentSheet.gid] = chatMessages.innerHTML;
    }
    
    // 모든 탭에서 active 클래스 제거
    document.querySelectorAll('.sheet-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 선택된 탭에 active 클래스 추가
    button.classList.add('active');
    
    // 이전 시트 정보 저장
    const previousGid = currentSheet.gid;
    
    // 현재 시트 정보 업데이트
    currentSheet.gid = button.getAttribute('data-sheet-gid');
    currentSheet.name = button.getAttribute('data-sheet-name');
    currentSheet.spreadsheet_id = button.getAttribute('data-spreadsheet-id');
    
    // 선택된 시트의 이전 대화 내용 복원 또는 초기 메시지 표시
    if (chatHistories[currentSheet.gid]) {
        // 이전 대화 내용이 있으면 복원
        chatMessages.innerHTML = chatHistories[currentSheet.gid];
    } else {
        // 새로운 시트면 환영 메시지 표시
        const displayName = getSheetDisplayName(button);
        chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    안녕하세요! "${displayName}" 데이터에서 궁금한 점을 물어보세요.
                </div>
            </div>
        `;
    }
    
    // 스크롤을 최하단으로 이동
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Update data overview title
    const displayName = getSheetDisplayName(button);
    document.getElementById('data-overview-title').textContent = `${displayName} 데이터`;
    
    // 데이터 개요 로드
    loadDataOverview();
}

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
        console.log('Sending request to:', API_URL);
        console.log('Request payload:', { 
            question: question,
            sheet_gid: currentSheet.gid,
            sheet_name: currentSheet.name,
            spreadsheet_id: currentSheet.spreadsheet_id
        });
        
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                question: question,
                sheet_gid: currentSheet.gid,
                sheet_name: currentSheet.name,
                spreadsheet_id: currentSheet.spreadsheet_id
            })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok && data.answer) {
            // 로딩 제거하고 답변 표시
            botMessageElement.innerHTML = `<div class="message-content">${formatAnswer(data.answer)}</div>`;
        } else {
            console.error('Error in response:', data);
            botMessageElement.innerHTML = `<div class="message-content">오류: ${data.error || '알 수 없는 오류가 발생했습니다.'}</div>`;
        }
        
    } catch (error) {
        console.error('Fetch error:', error);
        console.error('Error details:', error.message, error.stack);
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

// Modal functions
function showAddDataModal() {
    document.getElementById("add-data-modal").style.display = "block";
}

function hideAddDataModal() {
    document.getElementById("add-data-modal").style.display = "none";
    // Clear form
    document.getElementById("add-data-form").reset();
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById("add-data-modal");
    if (event.target == modal) {
        hideAddDataModal();
    }
}

// Load all data sources and update the sidebar
async function loadDataSources() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/data-sources`);
        if (!response.ok) {
            throw new Error('Failed to load data sources');
        }
        
        const data = await response.json();
        const sheetTabs = document.querySelector('.sheet-tabs');
        
        // Clear existing tabs
        sheetTabs.innerHTML = '';
        
        // Add tabs for each data source
        data.sources.forEach((source, index) => {
            const button = document.createElement('button');
            button.className = 'sheet-tab';
            if (index === 0) button.classList.add('active');
            button.setAttribute('data-sheet-gid', source.gid);
            button.setAttribute('data-sheet-name', source.title);
            button.setAttribute('data-spreadsheet-id', source.spreadsheet_id);
            button.setAttribute('data-is-default', source.is_default);
            button.onclick = function(e) { 
                // Only select sheet if not clicking on edit controls
                if (!e.target.closest('.edit-btn, .save-btn, .cancel-btn, .edit-input')) {
                    selectSheet(this); 
                }
            };
            
            // Choose icon based on source type or index
            const icon = source.is_default ? '📊' : '📄';
            
            button.innerHTML = `
                <span class="tab-icon">${icon}</span>
                <span class="tab-text">${source.title}</span>
                <input class="edit-input" type="text" value="${source.title}">
                <button class="edit-btn" onclick="startEdit(this)" title="Edit">✏️</button>
                <button class="save-btn" onclick="saveEdit(this)" title="Save">✓</button>
                <button class="cancel-btn" onclick="cancelEdit(this)" title="Cancel">✗</button>
            `;
            
            sheetTabs.appendChild(button);
        });
        
        // Update current sheet info if needed
        if (data.sources.length > 0) {
            const firstSource = data.sources[0];
            currentSheet = {
                gid: firstSource.gid,
                name: firstSource.title,
                spreadsheet_id: firstSource.spreadsheet_id
            };
        }
        
    } catch (error) {
        console.error('Error loading data sources:', error);
    }
}

// 페이지 로드 시 입력 필드에 포커스 및 초기 채팅 기록 저장
window.addEventListener('load', function() {
    document.getElementById('user-input').focus();
    
    // Load all data sources
    loadDataSources().then(() => {
        // 초기 채팅 내용을 현재 시트의 기록으로 저장
        const chatMessages = document.getElementById('chat-messages');
        if (currentSheet.gid && chatMessages.innerHTML.trim()) {
            chatHistories[currentSheet.gid] = chatMessages.innerHTML;
        }
        
        // 초기 데이터 개요 로드
        loadDataOverview();
    });
    
    // 새로고침 버튼 이벤트 리스너
    document.querySelector('.refresh-btn').addEventListener('click', loadDataOverview);
    
    // Add data form submission
    document.getElementById('add-data-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const title = document.getElementById('data-title').value;
        const url = document.getElementById('sheet-url').value;
        
        // Extract spreadsheet ID and GID from URL
        const urlMatch = url.match(/spreadsheets\/d\/([a-zA-Z0-9-_]+)/);
        const gidMatch = url.match(/[#&]gid=([0-9]+)/);
        
        if (!urlMatch || !gidMatch) {
            alert('Invalid Google Sheets URL. Please make sure it includes the spreadsheet ID and GID.');
            return;
        }
        
        const spreadsheetId = urlMatch[1];
        const gid = gidMatch[1];
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/add-data-source`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    title: title,
                    spreadsheet_id: spreadsheetId,
                    gid: gid
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                alert('Data source added successfully!');
                hideAddDataModal();
                // TODO: Refresh the sheet tabs
                location.reload();
            } else {
                const error = await response.json();
                alert('Error: ' + (error.error || 'Failed to add data source'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to add data source. Please check your connection.');
        }
    });
    
    // Attach event handler for edit form submit
    document.getElementById('edit-data-form').addEventListener('submit', handleEditDataSubmit);
    
    // Update modal close handler to include edit modal
    window.onclick = function(event) {
        const addModal = document.getElementById("add-data-modal");
        const editModal = document.getElementById("edit-data-modal");
        if (event.target == addModal) {
            hideAddDataModal();
        } else if (event.target == editModal) {
            hideEditDataModal();
        }
    };
});

// 데이터 개요 로드 함수
async function loadDataOverview() {
    const overviewContent = document.querySelector('.data-overview-content');
    
    // 로딩 상태 표시
    overviewContent.innerHTML = `
        <div class="loading-container">
            <div class="loading"></div>
            <p>데이터를 불러오는 중...</p>
        </div>
    `;
    
    try {
        // API 엔드포인트 수정: /api/sheet-info 사용
        const response = await fetch(`${API_BASE_URL}/api/sheet-info`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sheet_gid: currentSheet.gid,
                sheet_name: currentSheet.name,
                spreadsheet_id: currentSheet.spreadsheet_id
            })
        });
        
        if (!response.ok) {
            throw new Error('데이터를 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        displayDataOverview(data);
        
    } catch (error) {
        console.error('Error loading data overview:', error);
        overviewContent.innerHTML = `
            <div class="loading-container">
                <p style="color: #ff5500;">데이터를 불러올 수 없습니다.</p>
                <p style="font-size: 12px; color: #666; margin-top: 10px;">${error.message}</p>
            </div>
        `;
    }
}

// 데이터 개요 표시 함수
function displayDataOverview(data) {
    const overviewContent = document.querySelector('.data-overview-content');
    
    // 데이터 구조 확인
    const columns = data.columns || [];
    const sampleSize = data.total_rows;
    const surveyDate = data.survey_date || 'N/A';

    let html = `<h5 style="margin-top: 10px; color: #666;">조사 시기: ${surveyDate}, 응답자 수: ${sampleSize}명</h5>`;
    // 데이터 열 정보만 표시
    if (columns.length > 0) {
        html += `
            <div class="column-list">
        `;
        
        // 모든 열 표시
        columns.forEach((column, index) => {
            // _sheet_name은 내부 사용 컬럼이므로 제외
            if (column !== '_sheet_name') {
                html += `
                    <div class="column-item">
                        <span class="column-number">${index + 1}</span>
                        <span class="column-name">${column}</span>
                    </div>
                `;
            }
        });
        
        html += `
            </div>
        `;
    } else {
        html += `
            <div class="loading-container">
                <p style="color: #666;">데이터 열 정보가 없습니다.</p>
            </div>
        `;
    }
    
    overviewContent.innerHTML = html;
}

// Function to show edit modal
function showEditDataModal(source) {
    const modal = document.getElementById('edit-data-modal');
    document.getElementById('edit-data-title').value = source.title;
    document.getElementById('edit-gid').value = source.gid;
    document.getElementById('edit-spreadsheet-id').value = source.spreadsheet_id;
    document.getElementById('edit-is-default').value = source.is_default;
    
    const urlGroup = document.getElementById('edit-url-group');
    const editSheetUrl = document.getElementById('edit-sheet-url');
    
    // Only allow URL editing for non-default sources
    if (source.is_default) {
        urlGroup.style.display = 'none';
    } else {
        urlGroup.style.display = '';
        const currentUrl = `https://docs.google.com/spreadsheets/d/${source.spreadsheet_id}/edit#gid=${source.gid}`;
        editSheetUrl.value = currentUrl;
    }
    
    modal.style.display = 'block';
}

function hideEditDataModal() {
    const modal = document.getElementById('edit-data-modal');
    modal.style.display = 'none';
}

// Edit function triggering the modal
function startEdit(editBtn) {
    const sheetTab = editBtn.closest('.sheet-tab');
    const source = {
        title: sheetTab.querySelector('.tab-text').textContent,
        gid: sheetTab.getAttribute('data-sheet-gid'),
        spreadsheet_id: sheetTab.getAttribute('data-spreadsheet-id'),
        is_default: JSON.parse(sheetTab.getAttribute('data-is-default'))
    };
    showEditDataModal(source);
}

// Handle edit form submission
async function handleEditDataSubmit(event) {
    event.preventDefault();
    const gid = document.getElementById('edit-gid').value;
    const spreadsheetId = document.getElementById('edit-spreadsheet-id').value;
    const newTitle = document.getElementById('edit-data-title').value.trim();
    const isDefault = JSON.parse(document.getElementById('edit-is-default').value);
    
    if (!newTitle) {
        alert('Title cannot be empty');
        return;
    }
    
    // Prepare API request
    let body = {
        gid: gid,
        spreadsheet_id: spreadsheetId,
        title: newTitle
    };
    
    if (!isDefault) {
        const newUrl = document.getElementById('edit-sheet-url').value.trim();
        const urlMatch = newUrl.match(/spreadsheets\/d\/([a-zA-Z0-9-_]+)/);
        const gidMatch = newUrl.match(/[#&]gid=([0-9]+)/);
        if (!urlMatch || !gidMatch) {
            alert('Invalid Google Sheets URL. Please make sure it includes the spreadsheet ID and GID.');
            return;
        }
        // If URL changed, send as new_spreadsheet_id and new_gid
        const newSpreadsheetId = urlMatch[1];
        const newGid = gidMatch[1];
        
        if (newSpreadsheetId !== spreadsheetId || newGid !== gid) {
            body.new_spreadsheet_id = newSpreadsheetId;
            body.new_gid = newGid;
        }
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/update-data-source`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        if (response.ok) {
            alert('Data source updated successfully!');
            hideEditDataModal();
            location.reload(); // Reload to reflect changes
        } else {
            const error = await response.json();
            alert('Failed to update data source: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error updating data source:', error);
        alert('Failed to update data source. Please check your connection.');
    }
}


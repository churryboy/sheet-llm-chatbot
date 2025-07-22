#!/bin/bash

echo "🚀 구글 시트 + LLM 챗봇 시작하기..."
echo ""

# 백엔드 시작
echo "📦 백엔드 서버 시작 중..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# 잠시 대기
sleep 3

# 프론트엔드 시작
echo "🌐 프론트엔드 서버 시작 중..."
cd ../frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!

echo ""
echo "✅ 모든 서버가 시작되었습니다!"
echo "🔗 프론트엔드: http://localhost:8000"
echo "🔗 백엔드 API: http://localhost:5001"
echo ""
echo "종료하려면 Ctrl+C를 누르세요..."

# 종료 시그널 처리
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 프로세스가 실행 중인 동안 대기
wait

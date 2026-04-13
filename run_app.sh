#!/bin/bash

# Noor Islamic AI Agent - Unified Runner
# This script starts both the Backend (Flask) and Frontend (Vite)

# Colors for logging
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌟 Starting Noor Islamic AI Agent Session...${NC}"

# 0. Ensure environment paths for npm/node
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

# 0. Clean slate
echo -e "${BLUE}🧹 Clearing previous sessions and logs...${NC}"
# Kill processes on our ports and any matching python/node processes from this project
lsof -t -i :5010 -i :3001 2>/dev/null | xargs kill -9 2>/dev/null
pkill -f "backend/api/web_api.py" 2>/dev/null
pkill -f "vite --port 3001" 2>/dev/null
rm -rf logs/*.log
mkdir -p logs

# 0.5 Environment Optimizations
# Disable user site-packages to prevent slow iCloud metadata scans
export PYTHONNOUSERSITE=1

# 1. Virtual Environment Activation
# Use high-performance venv outside of iCloud sync
VENV_NAME="/Users/fahadiqbal/.islamic_ai_venv"

if [ ! -d "$VENV_NAME" ]; then
    echo -e "${RED}❌ High-performance virtual environment not found at $VENV_NAME.${NC}"
    exit 1
fi

echo -e "${GREEN}🔄 Activating virtual environment...${NC}"
source "$VENV_NAME/bin/activate"

# 1.5 Sanity check for critical backend libraries
echo -e "${BLUE}🔍 Checking backend dependencies...${NC}"
PYTHON_LIBS=("google.genai" "langchain_huggingface" "agentscope" "flask" "flask_cors")
for lib in "${PYTHON_LIBS[@]}"; do
    if ! python3 -c "import $lib" 2>/dev/null; then
        echo -e "${RED}⚠️  Missing critical library: $lib. Installing...${NC}"
        pip install $lib
    fi
done

# 2. Start Backend (Flask)
echo -e "${GREEN}🚀 Launching Backend API (Port 5010)...${NC}"
# Use the explicit venv python to avoid system path confusion and SSL warnings
# Use -u (unbuffered) to ensure logs are written instantly
"$VENV_NAME/bin/python3" -u backend/api/web_api.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${BLUE}📝 Backend logs: logs/backend.log (PID: $BACKEND_PID)${NC}"

# 3. Start Frontend (Vite)
echo -e "${GREEN}📱 Launching Frontend UI (Port 3001)...${NC}"
cd frontend
# Ensure dependencies are installed - check for specific critical package
if [ ! -d "node_modules/@vitejs/plugin-react" ]; then
    echo -e "${BLUE}📦 Installing/Restoring frontend dependencies...${NC}"
    npm install > ../logs/frontend_install.log 2>&1
fi

# Run vite dev server on port 3001
npm run dev -- --port 3001 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${BLUE}📝 Frontend logs: logs/frontend.log (PID: $FRONTEND_PID)${NC}"

echo -e "${GREEN}✅ Both services are starting!${NC}"

# 4. Wait for AI Agent Initialization
echo -e "${BLUE}⏳ Waiting for AI Scholars to assemble (this may take a few seconds)...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0
while true; do
    # Check health endpoint and extract agent_initialized status
    HEALTH_STATUS=$(curl -s http://localhost:5010/api/health | grep -o '"agent_initialized":true')
    if [ "$HEALTH_STATUS" == '"agent_initialized":true' ]; then
        echo -e "${GREEN}📖 AI Scholars are ready! All systems initialized. 🤲${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo -e "${RED}⚠️  Warning: AI scholars are taking longer than expected. Please check logs/backend.log.${NC}"
        break
    fi
    
    sleep 2
done

echo -e "${BLUE}🌍 Access the UI at: http://127.0.0.1:3001${NC}"
echo -e "${BLUE}📡 Backend Health: http://127.0.0.1:5010/api/health${NC}"
echo ""
echo -e "${RED}Press Ctrl+C to stop both services.${NC}"

# Function to handle shutdown
cleanup() {
    echo -e "\n${RED}🛑 Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✨ Services stopped safely.${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Keep script running to monitor background processes
wait

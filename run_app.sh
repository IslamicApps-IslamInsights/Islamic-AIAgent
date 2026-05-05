#!/bin/bash

# Noor Islamic AI Agent - Unified Runner
# This script starts Local LLM (llama.cpp), Backend (Flask) and Frontend (Vite)

# Colors for logging
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌟 Starting Noor Islamic AI Agent Session...${NC}"

# 0. Ensure environment paths for npm/node
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

# Resolve project root (script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 0. Clean slate
echo -e "${BLUE}🧹 Clearing previous sessions and logs...${NC}"
# Kill processes on our ports and any matching python/node processes from this project
lsof -t -i :5010 -i :3001 -i :8080 2>/dev/null | xargs kill -9 2>/dev/null
pkill -f "backend/api/web_api.py" 2>/dev/null
pkill -f "vite --port 3001" 2>/dev/null
pkill -f "llama-server" 2>/dev/null
rm -rf logs/*.log
mkdir -p logs

# 0.5 Environment Optimizations
# Disable user site-packages to prevent slow iCloud metadata scans
export PYTHONNOUSERSITE=1

# 1. Virtual Environment Activation
# Use high-performance venv outside of iCloud sync
VENV_NAME="/Users/fahadiqbal/.islamic_ai_venv"

if [ ! -d "$VENV_NAME" ]; then
    echo -e "${RED}⚠️  Virtual environment not found at $VENV_NAME. Using system python/pip.${NC}"
fi

echo -e "${GREEN}🔄 Activating virtual environment...${NC}"
if [ -d "$VENV_NAME" ]; then
    source "$VENV_NAME/bin/activate"
    PYTHON_BIN="$VENV_NAME/bin/python3"
else
    PYTHON_BIN="python3"
fi

# 1.5 Sanity check for critical backend libraries
echo -e "${BLUE}🔍 Checking backend dependencies...${NC}"
PYTHON_LIBS=("flask" "flask_cors" "langchain_huggingface" "chromadb" "rank_bm25" "httpx" "requests")
for lib in "${PYTHON_LIBS[@]}"; do
    if ! "$PYTHON_BIN" -c "import $lib" 2>/dev/null; then
        echo -e "${RED}⚠️  Missing critical library: $lib. Installing...${NC}"
        pip install $lib
    fi
done

# 1.8 Start Local LLM Server (llama.cpp)
MODEL_PATH="$SCRIPT_DIR/backend/models/qwen2.5-7b-ins-v3-Q4_K_M.gguf"
if [ -f "$MODEL_PATH" ]; then
    if command -v llama-server >/dev/null 2>&1; then
        echo -e "${GREEN}🧠 Launching Local LLM (llama.cpp) (Port 8080)...${NC}"
        export LOCAL_LLM_BACKEND="llama_cpp_server"
        export LLAMA_CPP_SERVER_URL="http://localhost:8080"
        export LOCAL_LLM_MAX_TOKENS="${LOCAL_LLM_MAX_TOKENS:-700}"
        export LOCAL_LLM_TEMPERATURE="${LOCAL_LLM_TEMPERATURE:-0.4}"

        llama-server -m "$MODEL_PATH" --host 0.0.0.0 --port 8080 --ctx-size 4096 > logs/llama_server.log 2>&1 &
        LLAMA_PID=$!
        echo -e "${BLUE}📝 LLM logs: logs/llama_server.log (PID: $LLAMA_PID)${NC}"
    else
        echo -e "${RED}⚠️  llama-server not found. Install with: brew install llama.cpp${NC}"
    fi
else
    echo -e "${RED}⚠️  Local model not found at: $MODEL_PATH${NC}"
    echo -e "${RED}   Download the GGUF model into backend/models/ to enable local synthesis.${NC}"
fi

# 2. Start Backend (Flask)
echo -e "${GREEN}🚀 Launching Backend API (Port 5010)...${NC}"
# Use the explicit venv python to avoid system path confusion and SSL warnings
# Use -u (unbuffered) to ensure logs are written instantly
"$PYTHON_BIN" -u backend/api/web_api.py > logs/backend.log 2>&1 &
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
    if [ -n "$LLAMA_PID" ]; then
        kill $LLAMA_PID 2>/dev/null
    fi
    echo -e "${GREEN}✨ Services stopped safely.${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Keep script running to monitor background processes
wait

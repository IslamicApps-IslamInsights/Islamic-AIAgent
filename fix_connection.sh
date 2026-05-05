#!/bin/bash

# 🚀 ONE-COMMAND FIX for Frontend Connection Errors
# Usage: bash fix_connection.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/Users/fahadiqbal/Downloads/Latest Projects/Islamic-AIAgent"

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    🔧 Islamic AI Agent - Connection Error FIX${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Step 1: Kill processes
echo -e "${YELLOW}[1/5] 🛑 Killing stuck processes...${NC}"
pkill -9 -f "python.*web_api" 2>/dev/null || true
pkill -9 -f "python.*backend" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ Processes cleaned${NC}"
echo ""

# Step 2: Navigate to project
echo -e "${YELLOW}[2/5] 📂 Navigating to project...${NC}"
cd "$PROJECT_DIR"
echo -e "${GREEN}✅ At: $(pwd)${NC}"
echo ""

# Step 3: Start backend
echo -e "${YELLOW}[3/5] 🚀 Starting backend server...${NC}"
python3 backend/api/web_api.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend PID: $BACKEND_PID${NC}"
echo ""

# Step 4: Wait for startup
echo -e "${YELLOW}[4/5] ⏳ Waiting for backend (up to 15 seconds)...${NC}"
COUNTER=0
MAX_ATTEMPTS=30
while [ $COUNTER -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:5010/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is HEALTHY!${NC}"
        break
    fi
    echo -n "."
    COUNTER=$((COUNTER + 1))
    sleep 0.5
done

if [ $COUNTER -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}❌ Backend did not respond in time${NC}"
    echo -e "${RED}Check logs: tail -50 logs/backend.log${NC}"
    exit 1
fi
echo ""

# Step 5: Verify health
echo -e "${YELLOW}[5/5] ✔️  Verifying backend health...${NC}"
HEALTH=$(curl -s http://localhost:5010/api/health 2>/dev/null)
echo "$HEALTH" | python3 -m json.tool 2>/dev/null
echo ""

# Success
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}    ✅ BACKEND IS RUNNING AND HEALTHY!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "  1. Refresh your browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)"
echo "  2. All connection errors should disappear ✅"
echo ""
echo -e "${BLUE}📊 Endpoints:${NC}"
echo "  • Backend: http://localhost:5010"
echo "  • Health: http://localhost:5010/api/health"
echo "  • Frontend: http://localhost:3001"
echo ""
echo -e "${BLUE}📜 Watch logs:${NC}"
echo "  • tail -f logs/backend.log"
echo ""
echo -e "${YELLOW}To stop backend later:${NC}"
echo "  • pkill -f 'python.*web_api'"
echo ""

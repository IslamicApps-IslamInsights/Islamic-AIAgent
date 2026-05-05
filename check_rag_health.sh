#!/bin/bash

# 🏥 RAG System Health Check
# ==========================
# Verifies that the RAG knowledge base is properly indexed and ready

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║     🏥 RAG SYSTEM HEALTH CHECK                             ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Determine virtual environment
VENV_PATH=""
if [ -f ".venv/bin/activate" ]; then
    VENV_PATH=".venv"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    VENV_PATH="$PROJECT_ROOT/.venv"
elif [ -f "$HOME/.islamic_ai_venv/bin/activate" ]; then
    VENV_PATH="$HOME/.islamic_ai_venv"
fi

if [ -z "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please activate a Python virtual environment first or ensure it exists at:"
    echo "  - .venv/"
    echo "  - ~/.islamic_ai_venv/"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Change to backend directory
cd "$SCRIPT_DIR"

# Run health check
python3 backend/knowledge/rag_health_check.py

echo -e "${GREEN}✅ Health check complete!${NC}\n"

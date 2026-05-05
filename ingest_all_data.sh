#!/bin/bash

# 🚀 Full RAG Data Ingestion Script
# ===================================
# Ingests ALL files from knowledge/data folder into:
# - ChromaDB (vector embeddings)
# - BM25 Index (keyword search)

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║     🚀 FULL RAG DATA INGESTION SYSTEM                      ║${NC}"
echo -e "${BLUE}║     Ingesting ALL files from knowledge/data folder         ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}📍 Project Root: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}📍 Backend Dir: $SCRIPT_DIR${NC}\n"

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

echo -e "${GREEN}✅ Virtual environment found: $VENV_PATH${NC}\n"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Change to backend directory
cd "$SCRIPT_DIR"

echo -e "${YELLOW}⏳ Starting full data ingestion...${NC}\n"

# Run full ingestion
python3 backend/knowledge/full_data_ingestion.py

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║     ✅ INGESTION COMPLETE - KNOWLEDGE BASE READY           ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}\n"
    
    echo -e "${BLUE}📊 Ingestion Statistics:${NC}"
    if [ -f "backend/knowledge/ingestion_stats.json" ]; then
        python3 -m json.tool "backend/knowledge/ingestion_stats.json" | head -20
        echo "..."
    fi
    
    echo -e "\n${GREEN}🎉 Success! Your RAG system is now fully populated.${NC}"
    echo -e "${GREEN}You can now start the backend with:${NC}"
    echo -e "  ${BLUE}cd $PROJECT_ROOT && bash dev.sh${NC}\n"
    
    exit 0
else
    echo -e "\n${RED}❌ Ingestion failed!${NC}"
    echo -e "${RED}Please check the error messages above.${NC}\n"
    exit 1
fi

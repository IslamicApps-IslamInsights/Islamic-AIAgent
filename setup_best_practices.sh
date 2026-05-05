#!/bin/bash
# Islamic AI Agent - Best Practices Quick Start
# Setup and run production-grade ingestion and LLM pipeline

set -e

echo "🚀 Islamic AI Agent - Best Practices Setup"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
VENV_PATH="$PROJECT_ROOT/.venv"

echo -e "${BLUE}📁 Project Root: $PROJECT_ROOT${NC}"

# Step 1: Create/activate virtual environment
echo -e "${BLUE}\n📦 Step 1: Setting up Python environment${NC}"
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
else
    echo "Virtual environment exists"
fi

source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Step 2: Install dependencies
echo -e "${BLUE}\n📥 Step 2: Installing dependencies${NC}"
pip install --upgrade pip setuptools wheel
pip install -r "$PROJECT_ROOT/requirements_best_practices.txt"
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Download NLTK data
echo -e "${BLUE}\n📥 Step 3: Downloading NLTK tokenizers${NC}"
python3 << 'EOF'
import nltk
try:
    nltk.data.find('tokenizers/punkt')
    print("✅ NLTK punkt tokenizer already available")
except LookupError:
    print("📥 Downloading NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=False)
    print("✅ NLTK punkt tokenizer installed")
EOF

# Step 4: Setup directories
echo -e "${BLUE}\n📂 Step 4: Setting up directories${NC}"
mkdir -p "$PROJECT_ROOT/backend/knowledge/data"
mkdir -p "$PROJECT_ROOT/backend/knowledge/chroma_db"
mkdir -p "$PROJECT_ROOT/logs"
echo -e "${GREEN}✅ Directories ready${NC}"

# Step 5: Check for data files
echo -e "${BLUE}\n📋 Step 5: Checking data files${NC}"
DATA_DIR="$PROJECT_ROOT/backend/knowledge/data"
JSON_COUNT=$(find "$DATA_DIR" -name "*.json" 2>/dev/null | wc -l)
TXT_COUNT=$(find "$DATA_DIR" -name "*.txt" 2>/dev/null | wc -l)

echo "JSON files: $JSON_COUNT"
echo "Text files: $TXT_COUNT"

if [ $((JSON_COUNT + TXT_COUNT)) -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No data files found in $DATA_DIR${NC}"
    echo "Add your Islamic knowledge base files (.json, .txt) to this directory"
else
    echo -e "${GREEN}✅ Data files found${NC}"
fi

# Step 6: Run ingestion
echo -e "${BLUE}\n🔄 Step 6: Running production ingestion pipeline${NC}"
read -p "Start ingestion now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python "$PROJECT_ROOT/backend/knowledge/ingest_best_practices.py"
    
    # Check if successful
    if [ -f "$PROJECT_ROOT/backend/knowledge/bm25_index.pkl" ]; then
        echo -e "${GREEN}✅ BM25 index created successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  BM25 index not found${NC}"
    fi
    
    if [ -f "$PROJECT_ROOT/backend/knowledge/ingestion_stats.json" ]; then
        echo -e "${GREEN}✅ Ingestion statistics saved${NC}"
        echo "View report at: backend/knowledge/ingestion_stats.json"
    fi
else
    echo "Skipping ingestion"
fi

# Step 7: Test retrieval
echo -e "${BLUE}\n🧪 Step 7: Testing retrieval system${NC}"
read -p "Test retrieval now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 << 'EOF'
from backend.utils.hybrid_rag_llm import retrieve_local_knowledge

test_queries = [
    "Tell me about Al-Fatiha",
    "What is Zakat in Islam?",
    "Islamic teachings on patience"
]

print("\n🧪 Testing Retrieval System\n")
for query in test_queries:
    results, found = retrieve_local_knowledge(query, k=3)
    if found:
        print(f"✅ Query: '{query}'")
        print(f"   Found {len(results)} results")
        print(f"   Top score: {results[0]['score']:.3f}")
        print(f"   Source: {results[0]['metadata'].get('source', 'Unknown')}")
    else:
        print(f"❌ Query: '{query}' - No results found")
    print()
EOF
fi

# Step 8: Test LLM configuration
echo -e "${BLUE}\n🤖 Step 8: Testing LLM configuration${NC}"
read -p "Test LLM configuration now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 << 'EOF'
from backend.utils.llm_best_practices import ModelSelector, MODELS

print("\n🤖 Checking LLM Configuration\n")

for model_id, config in MODELS.items():
    available = ModelSelector.is_model_available(config)
    status = "✅ Available" if available else "❌ Not configured"
    print(f"{config.name:30s} {status}")
    print(f"  Model: {config.model_id}")
    print(f"  Context: {config.context_window:,} tokens")
    print()

print("\nTo enable LLM synthesis:")
print("1. Set GOOGLE_API_KEY for Gemini")
print("2. OR set ANTHROPIC_API_KEY for Claude")
print("3. Add to .env file in project root")
EOF
fi

# Step 9: Generate setup report
echo -e "${BLUE}\n📊 Step 9: Generating setup report${NC}"
python3 << 'EOF'
import json
import os
from datetime import datetime

report = {
    "timestamp": datetime.now().isoformat(),
    "components": {
        "ingestion_pipeline": "backend/knowledge/ingest_best_practices.py",
        "llm_configuration": "backend/utils/llm_best_practices.py",
        "hybrid_rag": "backend/utils/hybrid_rag_llm.py"
    },
    "data_paths": {
        "source_data": "backend/knowledge/data/",
        "vector_db": "backend/knowledge/chroma_db/",
        "bm25_index": "backend/knowledge/bm25_index.pkl",
        "state_file": "backend/knowledge/ingestion_state.json"
    },
    "next_steps": [
        "1. Add Islamic knowledge sources to backend/knowledge/data/",
        "2. Run: python backend/knowledge/ingest_best_practices.py",
        "3. Monitor ingestion_stats.json for success",
        "4. Set GOOGLE_API_KEY or ANTHROPIC_API_KEY for LLM synthesis",
        "5. Start backend: python backend/api/web_api.py",
        "6. Access UI at: http://localhost:3001"
    ]
}

with open("SETUP_REPORT.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
EOF

# Final status
echo -e "${GREEN}\n✅ Setup Complete!${NC}"
echo -e "${BLUE}\nNext Steps:${NC}"
echo "1. Add Islamic knowledge sources to: backend/knowledge/data/"
echo "2. Run ingestion: python backend/knowledge/ingest_best_practices.py"
echo "3. Start backend: python backend/api/web_api.py"
echo "4. Start frontend: cd frontend && npm run dev -- --port 3001"
echo "5. Access UI at: http://localhost:3001"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "- Read: docs/BEST_PRACTICES_IMPLEMENTATION.md"
echo "- Read: docs/RAG_SYSTEM_COMPLETE.md"
echo ""
echo -e "${YELLOW}Support:${NC}"
echo "- Check logs in: logs/"
echo "- View ingestion stats: backend/knowledge/ingestion_stats.json"
echo "- Review errors in system console"
echo ""

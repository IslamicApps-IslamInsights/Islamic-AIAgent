#!/bin/bash
# Quick Start: Quran Foundation MCP Integration

set -e

echo "🌟 Islamic AI Agent - Quran Foundation MCP Edition"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv .venv
fi

# Activate venv
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/Update dependencies
echo -e "${BLUE}Installing Quran Foundation MCP dependencies...${NC}"
pip install -q mcp httpx

# Display information
echo ""
echo -e "${GREEN}✅ Quran Foundation MCP Integration Ready!${NC}"
echo ""
echo -e "${BLUE}📚 What's New:${NC}"
echo "  • Primary source: Quran Foundation MCP (https://mcp.quran.ai)"
echo "  • Authentic Quranic knowledge with Tafsir"
echo "  • Multi-language translations"
echo "  • Thematic exploration of Islamic concepts"
echo ""
echo -e "${BLUE}🚀 Quick Start Commands:${NC}"
echo ""
echo "1. Start Backend (Quran-Powered):"
echo "   cd /Users/fahadiqbal/Downloads/Latest\ Projects/Islamic-AIAgent"
echo "   ./start.sh"
echo ""
echo "2. Test Chat Endpoint:"
echo "   curl -X POST http://localhost:5010/api/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\": \"Tell me about Surah Al-Fatiha\"}'"
echo ""
echo "3. Search the Quran:"
echo "   curl -X POST http://localhost:5010/api/quran-foundation/search \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"mercy\"}'"
echo ""
echo "4. Get Tafsir:"
echo "   curl -X POST http://localhost:5010/api/quran-foundation/tafsir \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"surah\": 1, \"ayah\": 1, \"tafsir_type\": \"ibn_kathir\"}'"
echo ""
echo "5. Explore Theme:"
echo "   curl http://localhost:5010/api/quran-foundation/theme/justice"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo "   • Full Guide: docs/QURAN_FOUNDATION_MCP_GUIDE.md"
echo "   • API Reference: docs/API_REFERENCE.md"
echo ""
echo -e "${YELLOW}⚡ Key Points:${NC}"
echo "  ✨ Your agent is now UNIQUE - powered by Quran Foundation"
echo "  📚 NO hallucination risk - knowledge from authentic sources"
echo "  🎯 Scholarly credible - backed by classical Tafsir"
echo "  🌍 Best-in-class Islamic AI"
echo ""
echo -e "${GREEN}🎉 Ready to launch Quran-Centric Islamic AI!${NC}"
echo ""

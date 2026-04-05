#!/bin/bash

# Islamic AI Agent with AgentScope - Virtual Environment Setup

echo "🌟 Setting up Islamic AI Agent with AgentScope..."

# Create virtual environment (using .nosync to prevent macOS iCloud Drive hanging issues)
echo "📦 Creating virtual environment..."
python3 -m venv islamic_ai_venv.nosync

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source islamic_ai_venv.nosync/bin/activate

# Upgrade pip and install uv for fast, hang-free package installation
echo "⬆️ Upgrading pip and installing uv..."
pip install --upgrade pip uv

# Install AgentScope and required packages using uv (prevents macOS PyPI network hangs)
echo "🚀 Installing dependencies using uv..."
uv pip install agentscope requests python-dateutil geopy hijri-converter openai python-dotenv aiohttp asyncio flask flask-cors google-generativeai chromadb

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Islamic AI Agent Environment Variables
# Add your API keys here

# OpenAI API Key (for LLM)
OPENAI_API_KEY=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

# Alternative: Use other LLM providers
# DASHSCOPE_API_KEY=your_dashscope_key_here
# ANTHROPIC_API_KEY=your_claude_key_here

# Prayer Times API (optional - we'll use free APIs)
# ALADHAN_API_KEY=optional

# Islamic Calendar API (optional)
# ISLAMIC_CALENDAR_API_KEY=optional
EOF
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Activate the virtual environment: source islamic_ai_venv.nosync/bin/activate"
echo "2. Add your OpenAI and Gemini API keys to the .env file"
echo "3. Run the Islamic AI Agent Backend:"
echo "   • Main API Server: python simple_api.py"
echo "   • Single agent: python islamic_ai_agent.py"
echo "   • Multi-agent: python multi_agent_islamic_system.py"
echo ""
echo "🤲 May Allah bless this project and make it beneficial for the Ummah!"

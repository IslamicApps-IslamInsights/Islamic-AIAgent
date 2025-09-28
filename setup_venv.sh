#!/bin/bash

# Islamic AI Agent with AgentScope - Virtual Environment Setup

echo "🌟 Setting up Islamic AI Agent with AgentScope..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv islamic_ai_venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source islamic_ai_venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install AgentScope
echo "🚀 Installing AgentScope..."
pip install agentscope

# Install additional dependencies
echo "📚 Installing Islamic AI dependencies..."
pip install requests python-dateutil geopy hijri-converter openai python-dotenv aiohttp asyncio

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
echo "1. Activate the virtual environment: source islamic_ai_venv/bin/activate"
echo "2. Add your OpenAI API key to the .env file"
echo "3. Run the Islamic AI Agent:"
echo "   • Single agent: python islamic_ai_agent.py"
echo "   • Multi-agent: python multi_agent_islamic_system.py"
echo ""
echo "🤲 May Allah bless this project and make it beneficial for the Ummah!"

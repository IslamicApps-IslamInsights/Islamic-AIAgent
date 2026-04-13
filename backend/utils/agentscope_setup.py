#!/usr/bin/env python3
"""
AgentScope Islamic AI Agent Setup
This script sets up the environment for creating an Islamic AI agent using AgentScope
"""

import subprocess
import sys
import os

def install_agentscope():
    """Install AgentScope and required dependencies"""
    print("🚀 Setting up AgentScope for Islamic AI Agent...")
    
    # Install AgentScope
    subprocess.check_call([sys.executable, "-m", "pip", "install", "agentscope"])
    
    # Install additional dependencies for Islamic features
    dependencies = [
        "requests",  # For API calls (prayer times, etc.)
        "python-dateutil",  # For date calculations
        "geopy",  # For location services
        "hijri-converter",  # For Hijri date conversion
        "openai",  # For OpenAI integration
        "python-dotenv",  # For environment variables
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    print("✅ AgentScope setup complete!")

def create_env_file():
    """Create environment file for API keys"""
    env_content = """# Islamic AI Agent Environment Variables
# Add your API keys here

# OpenAI API Key (for LLM)
OPENAI_API_KEY=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

# Google Gemini API Key (fallback for OpenAI timeouts)
GOOGLE_API_KEY=AIzaSyCfY9jM_L0m7H65GADcUmNWbSsjBDw_p_8

# Alternative: Use other LLM providers
# DASHSCOPE_API_KEY=your_dashscope_key_here
ANTHROPIC_API_KEY=apikey_01Rj2N8SVvo6BePZj99NhmiT

# Prayer Times API (optional - we'll use free APIs)
# ALADHAN_API_KEY=optional

# Islamic Calendar API (optional)
# ISLAMIC_CALENDAR_API_KEY=optional
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("📝 Created .env file for API keys")
    print("⚠️  Please add your API keys to the .env file")

if __name__ == "__main__":
    install_agentscope()
    create_env_file()
    print("\n🎉 Setup complete! Ready to build your Islamic AI Agent with AgentScope!")

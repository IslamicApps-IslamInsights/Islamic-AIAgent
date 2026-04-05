import os
import sys
from llm_provider import init_agentscope
from islamic_ai_agent import IslamicAIAgent
from multi_agent_islamic_system import IslamicMultiAgentSystem

def diagnose():
    try:
        print("1. Initializing AgentScope...")
        init_agentscope()
        print("✅ AgentScope initialized.")
        
        print("2. Initializing Single Agent...")
        agent = IslamicAIAgent()
        print("✅ Single Agent initialized.")
        
        print("3. Initializing Multi-Agent System...")
        multi = IslamicMultiAgentSystem()
        print("✅ Multi-Agent System initialized.")
        
        print("\n✨ ALL INITIALIZATIONS SUCCESSFUL!")
    except Exception as e:
        print(f"\n❌ ERROR during diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()

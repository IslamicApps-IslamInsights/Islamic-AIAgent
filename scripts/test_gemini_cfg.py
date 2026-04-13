import sys
import os
import asyncio
sys.path.append(os.getcwd())

from llm_provider import init_agentscope
from multi_agent_islamic_system import IslamicMultiAgentSystem
from agentscope.message import Msg

async def verify_gemini_cfg():
    print("🧪 Verifying Gemini Configuration Registration...")
    
    # 1. Initialize AgentScope via unified provider
    config_name = init_agentscope()
    print(f"✅ Registered Config Name: {config_name}")
    
    # 2. Check if configuration matches expectations
    if config_name != "gemini_cfg":
        print(f"❌ Error: Expected 'gemini_cfg', got '{config_name}'")
        return

    # 3. Test live inference
    print("💬 Testing live inference with Sheikh Abdullah...")
    system = IslamicMultiAgentSystem()
    quran_scholar = system.agents['quran_scholar']
    
    query = Msg("user", "What is Surah Al-Fatiha about?", "user")
    try:
        # Since ReActAgent.__call__ is async in some versions, and sync in others, 
        # let's try the common interface
        response = await quran_scholar(query)
        print(f"✅ Response received: {response.content[:100]}...")
        print("\n✨ END-TO-END VERIFIED. The system is responding correctly.")
    except Exception as e:
        print(f"❌ Inference Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_gemini_cfg())

import sys
import os
import asyncio
sys.path.append(os.getcwd())

from multi_agent_islamic_system import IslamicMultiAgentSystem
from agentscope.message import Msg

async def test_scholarly_authenticity():
    print("🎓 Testing Scholarly Authenticity (Phase 5)...")
    
    try:
        # Initialize the system
        system = IslamicMultiAgentSystem()
        
        # Test Query 1: Something likely in 'fiqh_fundamentals.txt' or 'aqeedah_essentials.txt'
        query1 = "What are the six pillars of Iman?"
        print(f"\n❓ Query 1: {query1}")
        
        response1 = system.get_scholar_response(query1, scholar_type='coordinator')
        print(f"✅ Response 1:\n{response1}")
        
        # Test Query 2: Hadith specific to Sahih Bukhari
        query2 = "What is the first Hadith in Sahih Bukhari about intentions?"
        print(f"\n❓ Query 2: {query2}")
        
        response2 = system.get_scholar_response(query2, scholar_type='hadith_scholar')
        print(f"✅ Response 2:\n{response2}")
        
        print("\n\n✨ Authenticity Test Complete.")
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_scholarly_authenticity())

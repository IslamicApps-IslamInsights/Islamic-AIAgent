from multi_agent_islamic_system import IslamicMultiAgentSystem
import os
from dotenv import load_dotenv

load_dotenv()

def test_consolidated():
    print("🧪 Testing Consolidated Scholarly Conference (Single-Call)...")
    system = IslamicMultiAgentSystem()
    
    query = "What is the importance of Fajr prayer?"
    response = system.get_collaborative_response(query, user_gender="male")
    
    print("\n--- CONFERENCE RESPONSE ---")
    print(response)
    print("\n--- END RESPONSE ---")

if __name__ == "__main__":
    test_consolidated()

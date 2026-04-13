import sys
import os

# Set up paths
project_root = '/Users/fahadiqbal/Documents/Latest_Codes/Islamic work/Islamic AI Agent'
sys.path.insert(0, project_root)

# Mock Environment
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', 'AIzaSyCfY9jM_L0m7H65GADcUmNWbSsjBDw_p_8')

from backend.core.islamic_ai_agent import IslamicAIAgent
from datetime import datetime

def test():
    print("🚀 Initializing Agent for test...")
    agent = IslamicAIAgent()
    
    # Simulate a query about the date
    message = "What is the Hijri date today?"
    print(f"💬 Asking: {message}")
    
    # Process - this should now use the injected metadata
    response = agent.process_message_with_tools(message)
    
    print("\n--- AGENT RESPONSE ---")
    print(response)
    print("----------------------")
    
    # Current date should be Shawwal
    if "Shawwal" in response:
        print("\n✅ SUCCESS: Agent identified the correct month (Shawwal).")
    elif "Jumada" in response:
        print("\n❌ FAILURE: Agent is still hallucinating Jumada.")
    else:
        print("\n⚠️ UNKNOWN: Agent responded but month not detected.")

if __name__ == "__main__":
    test()

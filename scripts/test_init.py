from islamic_ai_agent import IslamicAIAgent
import os
from dotenv import load_dotenv
load_dotenv()
try:
    single = IslamicAIAgent(api_key=os.getenv('OPENAI_API_KEY'))
    print("Success")
except Exception as e:
    print("Error:", e)

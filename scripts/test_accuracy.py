import asyncio
import os
from islamic_ai_agent import IslamicAIAgent
from dotenv import load_dotenv

load_dotenv()

async def test_accuracy():
    print("🧪 Starting Accuracy Verification Suite...")
    agent = IslamicAIAgent()
    
    test_questions = [
        "What is the smallest surah of the Quran?",
        "How many Surahs are in the Quran?",
        "Who was the first person to embrace Islam?",
        "Who was the first male/child to embrace Islam?",
        "What are the names of the Prophet's (ﷺ) children?",
        "How many Juz are in the Quran?"
    ]
    
    for q in test_questions:
        print(f"\n❓ Question: {q}")
        response = agent.process_message_with_tools(q)
        print(f"✅ Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_accuracy())

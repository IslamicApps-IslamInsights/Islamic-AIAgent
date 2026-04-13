import os
import asyncio
from islamic_ai_agent import IslamicAIAgent

async def test_authenticity():
    print("🧪 Starting Authenticity Verification Test...")
    print("⏳ Initializing IslamicAIAgent (may take time for embeddings)...")
    agent = IslamicAIAgent()
    print("✅ Agent Initialized.")
    
    test_queries = [
        "What does Surah Al-Fatiha teach about guidance?",
        "Tell me a sahih hadith about intentions (Niyyah).",
        "What are the benefits of patience (Sabr) according to Quran?",
        "Explain the importance of prayer (Salah) in Islam."
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("⏳ Processing...")
        # We manually call the tool-enabled process to see RAG in action
        response = agent.process_message_with_tools(query)
        print(f"✅ Response:\n{response}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_authenticity())

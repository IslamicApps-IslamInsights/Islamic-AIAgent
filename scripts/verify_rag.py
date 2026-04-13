import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path to find knowledge_base
sys.path.append(os.path.abspath(os.curdir))

from knowledge_base.local_knowledge_tools import search_local_knowledge

def verify():
    print("🔎 Verifying Knowledge Base Accuracy...")
    
    queries = [
        "What is the smallest surah of the Quran?",
        "How many Surahs are in the Quran?",
        "Who was the first person to embrace Islam?",
        "How many Juz are in the Quran?"
    ]
    
    for q in queries:
        print(f"\n❓ Query: {q}")
        context = search_local_knowledge(q)
        print(f"📄 Retrieved Context:\n{context[:500]}...")
        print("-" * 50)

if __name__ == "__main__":
    verify()

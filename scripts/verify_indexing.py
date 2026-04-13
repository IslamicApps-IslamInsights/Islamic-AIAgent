import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.getcwd())

from knowledge_base.local_knowledge_tools import search_local_knowledge, search_local_code

def verify():
    print("🔍 Verifying Local Knowledge Base...")
    
    # Test Documentation Collection
    print("\n--- Testing 'docs' collection ---")
    doc_query = "What is the importance of patience in Islam?"
    doc_result = search_local_knowledge(doc_query)
    print(f"Query: {doc_query}")
    print(f"Result (first 200 chars): {doc_result[:200]}...")
    
    # Test Codebase Collection
    print("\n--- Testing 'codebase' collection ---")
    code_query = "How is the local knowledge base initialized?"
    code_result = search_local_code(code_query)
    print(f"Query: {code_query}")
    print(f"Result (first 200 chars): {code_result[:200]}...")

if __name__ == "__main__":
    verify()

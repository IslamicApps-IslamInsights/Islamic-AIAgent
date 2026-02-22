"""
Islamic AI Agent - Local Knowledge Retrieval Tools
Retreives relevant information from the local ChromaDB knowledge base.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

# Configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(ROOT_DIR, "knowledge_base/chroma_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class LocalKnowledgeRetriever:
    """Retriever class for local Islamic knowledge base"""
    
    def __init__(self):
        # Use the same best-in-class local model as ingestion
        model_name = "intfloat/multilingual-e5-large"
        print(f"Initializing local embedding model: {model_name}...")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize vector store
        if not os.path.exists(CHROMA_PATH):
            self.db = None
            print(f"Warning: Chroma database not found at {CHROMA_PATH}. Please run ingest_data.py first.")
        else:
            self.db = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=self.embeddings
            )

    def search(self, query: str, k: int = 4) -> str:
        """
        Search for relevant information in the local knowledge base.
        
        Args:
            query: The question or search term.
            k: Number of relevant chunks to retrieve.
            
        Returns:
            A formatted string containing the relevant information.
        """
        if not self.db:
            return "❌ Local knowledge base is empty or not initialized. Please upload and ingest documents first."

        try:
            # Perform similarity search
            results = self.db.similarity_search_with_relevance_scores(query, k=k)
            
            if not results:
                return "❌ No relevant information found in local documents for this query."

            formatted_results = ["📖 **Relevant Information from Local Knowledge Base:**\n"]
            
            for doc, score in results:
                # Only include results with a decent relevance score (e.g. > 0.3)
                if score > 0.3:
                    source = doc.metadata.get("source", "Unknown file")
                    page = doc.metadata.get("page", "N/A")
                    content = doc.page_content.strip()
                    
                    formatted_results.append(f"🔹 **Source:** {os.path.basename(source)} (Page {page})")
                    formatted_results.append(f"{content}\n")
            
            if len(formatted_results) == 1:
                return "❌ No highly relevant information found in local documents."

            formatted_results.append("\n✨ *This information was retrieved from your locally uploaded Islamic documents.*")
            return "\n".join(formatted_results)

        except Exception as e:
            return f"❌ Error searching local knowledge base: {str(e)}"

# Global instance for easy access
_retriever = None

def get_retriever():
    """Singleton-like access to the retriever"""
    global _retriever
    if _retriever is None:
        try:
            _retriever = LocalKnowledgeRetriever()
        except Exception as e:
            print(f"Failed to initialize LocalKnowledgeRetriever: {e}")
            return None
    return _retriever

def search_local_knowledge(query: str) -> str:
    """
    Tool function for agents to search local Islamic knowledge.
    
    Args:
        query: The user's question or topic related to local data.
        
    Returns:
        Relevant excerpts from local documents.
    """
    retriever = get_retriever()
    if not retriever:
        return "❌ Search tool failed to initialize. Check OpenAI API key."
    return retriever.search(query)

if __name__ == "__main__":
    # Quick test
    print(search_local_knowledge("patience in Islam"))

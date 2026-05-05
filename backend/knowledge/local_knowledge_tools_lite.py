"""
Lite Knowledge Base - No Heavy Models
Fallback for low disk space environments
"""

import os
from dotenv import load_dotenv

load_dotenv()


class LiteKnowledgeBase:
    """Minimal KB for low-resource environments"""
    
    def __init__(self):
        print("📚 Loading Lite Knowledge Base (No ML Models)...")
        self.db = None
        self.bm25 = None
        self.reranker = None  # Skip reranker
        self.loaded = False
        
        try:
            # Only load ChromaDB if space allows
            from langchain_community.vectorstores import Chroma
            from langchain_community.embeddings import OllamaEmbeddings
            
            CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
            
            if os.path.exists(CHROMA_PATH):
                print("🔍 Using cached embeddings (no model download needed)")
                # Use lightweight embeddings if available
                try:
                    embeddings = OllamaEmbeddings(model="nomic-embed-text")
                    self.db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
                    self.loaded = True
                    print("✅ Lite KB ready (ChromaDB cached)")
                except:
                    print("⚠️  ChromaDB cache unavailable")
            else:
                print("⚠️  No cached embeddings found")
                
        except Exception as e:
            print(f"⚠️  Lite KB load warning: {e}")
    
    def search(self, query: str, top_k: int = 5):
        """Perform simple search"""
        if not self.db or not self.loaded:
            return f"Knowledge base unavailable. Query: '{query}'"
        
        try:
            results = self.db.similarity_search(query, k=top_k)
            if results:
                return "\n".join([r.page_content for r in results[:3]])
            return f"No results found for: {query}"
        except Exception as e:
            return f"Search error: {str(e)[:100]}"


# Global instance
_lite_kb = None


def get_lite_kb():
    """Get lite KB instance"""
    global _lite_kb
    if _lite_kb is None:
        _lite_kb = LiteKnowledgeBase()
    return _lite_kb if _lite_kb.loaded else None

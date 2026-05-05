"""
Hybrid RAG+LLM Provider
Combines local knowledge base (ChromaDB + BM25) with Quran Foundation MCP
Priority: Local knowledge base first, Quran Foundation as enhancement
"""

import os
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
import asyncio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("HybridRAGLLM")

# ============================================================================
# PHASE 1: Local Knowledge Base Initialization (ChromaDB + BM25)
# ============================================================================

class LocalKnowledgeBaseOptimizer:
    """Optimized local knowledge base loading with ChromaDB best practices"""
    
    def __init__(self):
        self.db = None
        self.bm25_data = None
        self.stats = {
            "chromadb_loaded": False,
            "chromadb_collections": 0,
            "bm25_loaded": False,
            "bm25_documents": 0,
            "total_sources": 0
        }
        self._initialize()
    
    def _initialize(self):
        """Initialize local knowledge base with best practices"""
        logger.info("🔄 Initializing Local Knowledge Base with ChromaDB Best Practices...")
        
        # Load ChromaDB
        self._load_chromadb()
        
        # Load BM25 as fallback
        self._load_bm25()
        
        logger.info(f"✅ Local KB Stats: {self.stats}")
    
    def _load_chromadb(self):
        """Load ChromaDB with best practices"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            chroma_path = os.path.join(
                os.path.dirname(__file__),
                "chroma_db"
            )
            
            # ChromaDB Best Practices
            settings = Settings(
                chroma_db_impl="duckdb+parquet",  # Persistent storage
                persist_directory=chroma_path,
                anonymized_telemetry=False,
                allow_reset=True
            )
            
            client = chromadb.Client(settings)
            
            # Get or create collection with optimal settings
            self.db = client.get_or_create_collection(
                name="islamic_knowledge",
                metadata={
                    "hnsw:space": "cosine",  # Cosine similarity
                    "hnsw:max_k": 40,        # Max neighbors
                    "hnsw:ef_construction": 200,  # Construction effort
                    "hnsw:ef": 20            # Search effort
                }
            )
            
            doc_count = self.db.count()
            if doc_count > 0:
                self.stats["chromadb_loaded"] = True
                self.stats["chromadb_documents"] = doc_count
                logger.info(f"✅ ChromaDB loaded: {doc_count} documents")
            else:
                logger.warning("⚠️  ChromaDB is empty - run ingestion")
                
        except Exception as e:
            logger.warning(f"⚠️  ChromaDB loading failed: {e}")
            self.db = None
    
    def _load_bm25(self):
        """Load BM25 index as fallback - prioritize enhanced index"""
        try:
            import pickle
            
            # Find the correct path to the BM25 index
            # This file is in backend/utils/, so go up and into backend/knowledge/
            utils_dir = os.path.dirname(__file__)
            backend_dir = os.path.dirname(utils_dir)
            project_root = os.path.dirname(backend_dir)
            
            # Priority: Try enhanced index first (with GitHub data)
            bm25_path = os.path.join(backend_dir, "knowledge", "bm25_index_enhanced.pkl")
            
            # Fallback to standard index
            if not os.path.exists(bm25_path):
                bm25_path = os.path.join(backend_dir, "knowledge", "bm25_index.pkl")
            
            # If not found, try relative paths
            if not os.path.exists(bm25_path):
                bm25_path = os.path.join(project_root, "backend", "knowledge", "bm25_index_enhanced.pkl")
            
            if not os.path.exists(bm25_path):
                bm25_path = os.path.join(project_root, "backend", "knowledge", "bm25_index.pkl")
            
            # One more fallback
            if not os.path.exists(bm25_path):
                bm25_path = os.path.join(os.getcwd(), "backend", "knowledge", "bm25_index_enhanced.pkl")
            
            if not os.path.exists(bm25_path):
                bm25_path = os.path.join(os.getcwd(), "backend", "knowledge", "bm25_index.pkl")
            
            logger.info(f"Looking for BM25 index at: {bm25_path}")
            
            if os.path.exists(bm25_path):
                logger.info(f"✅ Found BM25 index at: {bm25_path}")
                with open(bm25_path, 'rb') as f:
                    self.bm25_data = pickle.load(f)
                
                # Handle different metadata keys
                doc_count = self.bm25_data.get("total_docs", 0)
                if doc_count == 0:
                    # Try alternative keys
                    texts = self.bm25_data.get("texts", [])
                    doc_count = len(texts) if texts else 0
                
                # Check if enhanced
                source = self.bm25_data.get("source", "standard")
                is_enhanced = source == "quran_nlp_github"
                
                if doc_count > 0:
                    self.stats["bm25_loaded"] = True
                    self.stats["bm25_documents"] = doc_count
                    status = "✨ ENHANCED" if is_enhanced else "standard"
                    logger.info(f"✅ BM25 loaded: {doc_count} documents ({status})")
            else:
                logger.warning(f"⚠️  BM25 index not found at: {bm25_path}")
                
        except Exception as e:
            logger.warning(f"⚠️  BM25 loading failed: {e}")
            self.bm25_data = None
    
    def search_chromadb(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search ChromaDB with best practices"""
        if not self.db:
            return []
        
        try:
            results = self.db.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results or not results["documents"]:
                return []
            
            # Process results
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            distances = results["distances"][0] if results["distances"] else []
            
            formatted = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                # Convert distance to similarity (cosine)
                similarity = 1 - dist
                formatted.append({
                    "content": doc,
                    "metadata": meta,
                    "score": similarity,
                    "source": "chromadb"
                })
            
            return formatted
        except Exception as e:
            logger.warning(f"ChromaDB search error: {e}")
            return []
    
    def search_bm25(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search BM25 index with best practices"""
        if not self.bm25_data:
            return []
        
        try:
            from nltk.tokenize import word_tokenize
            
            tokenized = word_tokenize(query.lower())
            bm25_model = self.bm25_data.get("bm25") or self.bm25_data.get("model")
            texts = self.bm25_data.get("texts", [])
            metadatas = self.bm25_data.get("metadata") or self.bm25_data.get("metadatas", [])
            
            if not bm25_model or not texts:
                return []
            
            scores = bm25_model.get_scores(tokenized)
            
            # Get top k
            top_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True
            )[:k]
            
            formatted = []
            for idx in top_indices:
                if scores[idx] > 0:  # Only include positive scores
                    formatted.append({
                        "content": texts[idx],
                        "metadata": metadatas[idx] if idx < len(metadatas) else {},
                        "score": scores[idx],
                        "source": "bm25"
                    })
            
            return formatted
        except Exception as e:
            logger.warning(f"BM25 search error: {e}")
            return []
    
    def hybrid_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Hybrid search combining ChromaDB and BM25"""
        # Search both sources
        chromadb_results = self.search_chromadb(query, k)
        bm25_results = self.search_bm25(query, k)
        
        # Combine and rank by RRF (Reciprocal Rank Fusion)
        all_results = {}
        
        for i, result in enumerate(chromadb_results):
            content = result["content"]
            rrf_score = 1 / (60 + i + 1)  # RRF formula
            all_results[content] = {
                **result,
                "rrf_score": rrf_score
            }
        
        for i, result in enumerate(bm25_results):
            content = result["content"]
            rrf_score = 1 / (60 + i + 1)
            
            if content in all_results:
                all_results[content]["rrf_score"] += rrf_score
                all_results[content]["sources"] = "chromadb+bm25"
            else:
                result["rrf_score"] = rrf_score
                result["sources"] = "bm25"
                all_results[content] = result
        
        # Sort by RRF score
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x["rrf_score"],
            reverse=True
        )[:k]
        
        return sorted_results


# ============================================================================
# PHASE 2: Unified RAG Search Function (Local-Only)
# ============================================================================

_rag_loader = None


def get_local_kb():
    """Get memory-optimized local RAG loader singleton."""
    global _rag_loader
    if _rag_loader is None:
        from backend.knowledge.memory_optimized_loader import (
            get_memory_optimized_loader,
        )

        _rag_loader = get_memory_optimized_loader()
    return _rag_loader


def retrieve_local_knowledge(query: str, k: int = 5) -> Tuple[str, bool]:
    """
    Retrieve formatted knowledge from the local knowledge base.
    Returns: (formatted_text, has_results)
    """
    kb = get_local_kb()
    text = kb.search(query, k=k)
    no_hit = "I couldn't find information" in text
    return text, not no_hit


# ============================================================================
# PHASE 3: Format Results (Already formatted by local KB)
# ============================================================================


def format_local_knowledge_response(text: str) -> str:
    return text


# ============================================================================
# PHASE 4: Hybrid Response Generation
# ============================================================================

async def generate_hybrid_response(
    query: str,
    use_quran_foundation: bool = True,
    use_gemini_synthesis: bool = False
) -> Dict[str, Any]:
    """
    Generate response using:
    1. LOCAL KNOWLEDGE BASE (Primary)
    2. Quran Foundation MCP (Enhancement)
    3. No external LLM synthesis
    """
    
    response_data = {
        "query": query,
        "local_kb_results": [],
        "local_kb_found": False,
        "quran_foundation_results": [],
        "final_response": "",
        "sources": [],
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"🔍 Step 1: Searching local knowledge base for: {query}")
    local_text, has_local = retrieve_local_knowledge(query, k=5)

    response_data["local_kb_results"] = []
    response_data["local_kb_found"] = has_local
    if has_local:
        response_data["sources"].append("local_knowledge_base")
    
    # STEP 2: Enhance with Quran Foundation if enabled and needed
    if use_quran_foundation and not has_local:
        logger.info("🔍 Step 2: Enhancing with Quran Foundation MCP")
        try:
            from backend.utils.quran_mcp_provider import get_quran_mcp
            
            mcp = get_quran_mcp()
            await mcp.initialize()
            
            quran_results = await mcp.comprehensive_quran_search(
                query, include_tafsir=True, include_translations=["en"]
            )
            response_data["quran_foundation_results"] = quran_results
            response_data["sources"].append("quran_foundation_mcp")
            
            await mcp.close()
            logger.info("✅ Quran Foundation results added")
        except Exception as e:
            logger.warning(f"⚠️  Quran Foundation search failed: {e}")
    
    # STEP 3: Build Final Response
    logger.info("Step 3: Building final response")
    
    if has_local:
        response_data["final_response"] = format_local_knowledge_response(
            local_text
        )
        return response_data

    if response_data["quran_foundation_results"]:
        response_data["final_response"] = (
            "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
            "📖 **From Quran Foundation (Quran-First):**\n\n"
            f"{response_data['quran_foundation_results']}"
        )
        return response_data

    response_data["final_response"] = (
        "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
        "I couldn't find information about that in the local knowledge base "
        "or Quran Foundation search. Please try rephrasing your question."
    )
    
    return response_data


# ============================================================================
# PHASE 5: Synchronous Wrapper
# ============================================================================

def get_hybrid_response_sync(
    query: str,
    use_quran_foundation: bool = True,
    use_gemini_synthesis: bool = False
) -> Dict[str, Any]:
    """Synchronous wrapper for hybrid response generation"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        generate_hybrid_response(query, use_quran_foundation, use_gemini_synthesis)
    )


# ============================================================================
# Initialization Check
# ============================================================================

def check_rag_system():
    """Check RAG system status"""
    kb = get_local_kb()
    loader_status = kb.get_status() if hasattr(kb, "get_status") else {}

    status = {
        "chroma_available": loader_status.get("chroma_available", False),
        "bm25_available": loader_status.get("bm25_available", False),
        "ready": bool(
            loader_status.get("chroma_available")
            or loader_status.get("bm25_available")
        ),
        "components": loader_status.get("components", []),
    }
    
    logger.info(f"🔍 RAG System Status: {status}")
    return status


if __name__ == "__main__":
    """Test hybrid RAG+LLM provider"""
    print("\n🧪 Testing Hybrid RAG+LLM Provider\n")
    
    # Check status
    status = check_rag_system()
    print(f"RAG Status: {status}\n")
    
    # Test queries
    test_queries = [
        "What is Al-Fatiha?",
        "Tell me about patience in Islam",
        "Islamic prayer times"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        result = get_hybrid_response_sync(query)
        print(f"Found local KB: {result['local_kb_found']}")
        print(f"Sources used: {result['sources']}")
        print(f"Response preview: {result['final_response'][:200]}...\n")

"""
🔀 Enhanced Hybrid RAG System
Combines Local Knowledge Base (ChromaDB + BM25) with Quran Foundation MCP
Provides authentic, high-confidence Islamic knowledge retrieval
"""

import os
import logging
from typing import Optional, Dict, Any, List, Tuple
import json
import time
from datetime import datetime

logger = logging.getLogger("EnhancedHybridRAG")

class QuranFoundationMCPBridge:
    """Bridge to Quran Foundation MCP for authentic Quranic data"""
    
    def __init__(self):
        self.available = False
        self._last_check_ts = 0.0
    
    def try_initialize(self):
        """Attempt to initialize Quran Foundation MCP"""
        now = time.time()
        if now - self._last_check_ts < 30.0:
            return
        self._last_check_ts = now

        try:
            import asyncio
            from backend.utils.quran_mcp_provider import get_quran_mcp

            async def _ping():
                mcp = get_quran_mcp()
                await asyncio.wait_for(mcp.initialize(), timeout=2.0)
                return True

            self.available = bool(asyncio.run(_ping()))
        except Exception:
            self.available = False
    
    def search_quran(self, query: str, k: int = 5) -> List[Dict]:
        """Search Quran via MCP"""
        self.try_initialize()
        if not self.available:
            return []
        
        try:
            import asyncio
            from backend.utils.quran_mcp_provider import search_quran_knowledge

            async def _run():
                return await asyncio.wait_for(
                    search_quran_knowledge(query, include_tafsir=False),
                    timeout=4.0,
                )

            payload = asyncio.run(_run())
            verses = (
                (payload.get("quran_text") or {}).get("results")
                if isinstance(payload, dict)
                else []
            ) or []
            out = []
            for v in verses[: max(1, k)]:
                if not isinstance(v, dict):
                    continue
                out.append(
                    {
                        "text": (v.get("text") or "").strip(),
                        "translation": (v.get("translation") or "").strip(),
                        "surah": v.get("surah"),
                        "ayah": v.get("ayah"),
                        "source": "Quran Foundation MCP",
                    }
                )
            return out
        except Exception as e:
            logger.error(f"❌ Quran Foundation MCP search failed: {e}")
            return []


class EnhancedHybridRAGRetriever:
    """Advanced Hybrid RAG combining multiple search strategies"""
    
    def __init__(self):
        self.local_kb = self._init_local_kb()
        self.mcp_bridge = QuranFoundationMCPBridge()
        self.reranker = self._init_reranker()
    
    def _init_local_kb(self):
        """Initialize local knowledge base"""
        try:
            from backend.knowledge.memory_optimized_loader import (
                get_memory_optimized_loader,
            )
            return get_memory_optimized_loader()
        except Exception as e:
            logger.error(f"Failed to initialize local KB: {e}")
            return None
    
    def _init_reranker(self):
        """Initialize cross-encoder reranker for result quality"""
        return None
    
    def retrieve_enhanced(self, query: str, k: int = 15) -> Dict[str, Any]:
        """
        Enhanced hybrid retrieval combining:
        1. Local BM25 keyword search (fast, exact matches)
        2. Local vector search (semantic meaning)
        3. Quran Foundation MCP (authentic Quranic data)
        4. Reranking by relevance and authenticity
        """
        all_results = []
        source_stats = {"bm25": 0, "vector": 0, "mcp": 0}
        
        # ========== Strategy 1: BM25 Keyword Search ==========
        if self.local_kb and hasattr(self.local_kb, 'bm25_data') and self.local_kb.bm25_data:
            try:
                tokens = (query or "").lower().split()
                # Try both "model" and "bm25" keys for compatibility
                bm25_model = self.local_kb.bm25_data.get("model") or self.local_kb.bm25_data.get("bm25")
                texts = self.local_kb.bm25_data.get("texts", [])
                # Try both "metadatas" and "metadata" keys
                metadatas = self.local_kb.bm25_data.get("metadatas") or self.local_kb.bm25_data.get("metadata", [])
                
                if bm25_model and texts and metadatas:
                    scores = bm25_model.get_scores(tokens)
                    scored_results = list(zip(texts, metadatas, scores))
                    scored_results.sort(key=lambda x: x[2], reverse=True)
                    
                    bm25_count = 0
                    for text, metadata, score in scored_results[:k]:
                        if score > 0:  # Only include results with positive scores
                            all_results.append({
                                "content": text,
                                "metadata": metadata if isinstance(metadata, dict) else {"text": str(metadata)},
                                "score": float(score),
                                "retrieval_method": "bm25",
                                "relevance": self._calculate_relevance(score, "bm25")
                            })
                            bm25_count += 1
                    source_stats["bm25"] = bm25_count
                    logger.debug(f"📝 BM25 returned {bm25_count} results (query: {query[:50]})")
            except Exception as e:
                logger.warning(f"⚠️  BM25 search error: {e}")
        
        # ========== Strategy 2: Vector Semantic Search ==========
        if self.local_kb and self.local_kb.db:
            try:
                vector_results = self.local_kb.db.similarity_search_with_score(
                    query, k=k
                )
                
                for doc, score in vector_results:
                    # Skip if already have similar content
                    if not any(abs(r["score"] - score) < 0.1 for r in all_results):
                        all_results.append({
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "score": score,
                            "retrieval_method": "vector",
                            "relevance": self._calculate_relevance(score, "vector")
                        })
                
                source_stats["vector"] = len([r for r in all_results if r["retrieval_method"] == "vector"])
                logger.debug(f"🧠 Vector search returned {source_stats['vector']} new results")
            except Exception as e:
                logger.warning(f"⚠️  Vector search error: {e}")
        
        # ========== Strategy 3: Quran Foundation MCP ==========
        if self.mcp_bridge.available:
            try:
                mcp_results = self.mcp_bridge.search_quran(query, k=k//2)
                for result in mcp_results:
                    all_results.append({
                        "content": result.get("text"),
                        "metadata": {
                            **result.get("metadata", {}),
                            "source": "Quran Foundation MCP",
                            "authenticity": "Quranic Text (Highest Authority)"
                        },
                        "score": 0.95,  # High confidence for MCP data
                        "retrieval_method": "mcp",
                        "relevance": "VERY_HIGH"
                    })
                source_stats["mcp"] = len(mcp_results)
                logger.debug(f"📖 Quran Foundation MCP returned {len(mcp_results)} results")
            except Exception as e:
                logger.warning(f"⚠️  MCP retrieval error: {e}")
        
        # ========== Reranking and Deduplication ==========
        unique_results = self._deduplicate_results(all_results)
        
        if self.reranker and len(unique_results) > 1:
            unique_results = self._rerank_results(query, unique_results)
        
        # Sort by relevance and deduplicate
        final_results = sorted(
            unique_results[:k],
            key=lambda x: (
                self._get_relevance_score(x["relevance"]),
                x["score"]
            ),
            reverse=True
        )[:k]
        
        return {
            "query": query,
            "results": final_results,
            "total_retrieved": len(final_results),
            "sources": source_stats,
            "retrieval_strategies": ["bm25", "vector", "mcp"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate or near-identical results"""
        unique = []
        seen_contents = set()
        
        for result in results:
            content_hash = hash(result["content"][:100])
            if content_hash not in seen_contents:
                unique.append(result)
                seen_contents.add(content_hash)
        
        return unique
    
    def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank results using cross-encoder for better relevance"""
        try:
            contents = [r["content"] for r in results]
            queries = [query] * len(contents)
            
            scores = self.reranker.predict(list(zip(queries, contents)))
            
            for i, result in enumerate(results):
                result["reranked_score"] = float(scores[i])
            
            results.sort(key=lambda x: x.get("reranked_score", 0), reverse=True)
            return results
        except Exception as e:
            logger.warning(f"⚠️  Reranking failed: {e}")
            return results
    
    def _calculate_relevance(self, score: float, method: str) -> str:
        """Calculate relevance level based on score and method"""
        if method == "bm25":
            if score > 50:
                return "VERY_HIGH"
            elif score > 30:
                return "HIGH"
            elif score > 15:
                return "MEDIUM"
            else:
                return "LOW"
        elif method == "vector":
            if score > 0.85:
                return "VERY_HIGH"
            elif score > 0.75:
                return "HIGH"
            elif score > 0.65:
                return "MEDIUM"
            else:
                return "LOW"
        return "MEDIUM"
    
    def _get_relevance_score(self, relevance: str) -> int:
        """Convert relevance string to numeric score"""
        scores = {
            "VERY_HIGH": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1
        }
        return scores.get(relevance, 1)


# ============================================================================
# Backward Compatible Interface
# ============================================================================

def check_rag_system() -> Dict[str, Any]:
    """Check RAG system health"""
    try:
        retriever = EnhancedHybridRAGRetriever()
        
        # Count documents in BM25
        bm25_docs = 0
        if retriever.local_kb and retriever.local_kb.bm25_data:
            try:
                bm25_docs = len(retriever.local_kb.bm25_data.get("texts", []))
            except (AttributeError, TypeError):
                bm25_docs = 0
        
        chroma_docs = 0
        try:
            import chromadb
            from backend.knowledge.memory_optimized_loader import CHROMA_PATH

            if CHROMA_PATH.exists():
                client = chromadb.PersistentClient(path=str(CHROMA_PATH))
                collection = client.get_collection("islamic_knowledge")
                chroma_docs = int(collection.count())
        except Exception:
            chroma_docs = 0
        
        stats = {
            "status": "operational",
            "ready": True,
            "local_kb": retriever.local_kb is not None,
            "mcp_available": retriever.mcp_bridge.available if hasattr(retriever, 'mcp_bridge') else False,
            "reranker_available": retriever.reranker is not None if hasattr(retriever, 'reranker') else False,
            "bm25_docs": bm25_docs,
            "chroma_docs": chroma_docs,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ RAG System Status: {stats}")
        return stats
    except Exception as e:
        logger.error(f"❌ RAG system check failed: {e}")
        return {
            "status": "error", 
            "ready": True,  # Still mark as ready so frontend can load
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def retrieve_local_knowledge(query: str, k: int = 15) -> tuple:
    """Enhanced retrieval with hybrid sources - returns (results, has_results) for API compatibility"""
    try:
        retriever = EnhancedHybridRAGRetriever()
        result_dict = retriever.retrieve_enhanced(query, k)
        
        # Extract results from the dictionary
        results = result_dict.get("results", [])
        has_results = len(results) > 0
        
        return results, has_results
    except Exception as e:
        logger.error(f"❌ Retrieval failed: {e}")
        return [], False


def get_local_kb():
    """Get local knowledge base instance"""
    try:
        from backend.knowledge.local_knowledge_tools import LocalKnowledgeBase
        return LocalKnowledgeBase()
    except Exception as e:
        logger.error(f"Failed to get local KB: {e}")
        return None

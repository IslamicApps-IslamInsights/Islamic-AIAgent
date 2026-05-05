"""
🚀 ADVANCED HYBRID RAG SYSTEM - v2.0
Comprehensive knowledge retrieval with source prioritization, semantic search,
and Quran Foundation MCP integration for optimal Islamic knowledge delivery.
"""

import os
import logging
from typing import Optional, Dict, Any, List, Tuple
import json
from datetime import datetime
from rank_bm25 import BM25Okapi

logger = logging.getLogger("AdvancedHybridRAG")

def _tokenize(text: str) -> List[str]:
    return (text or "").lower().split()

# ============================================================================
# SOURCE PRIORITY & AUTHENTICITY MAPPING
# ============================================================================

SOURCE_PRIORITY = {
    # Highest Priority: Quran (Direct revelation)
    "quran_yusuf_ali": 5.0,
    "quran_saheeh_international": 5.0,
    "quran_pickthall": 5.0,
    "quran_shakir": 5.0,
    "en.ahmedraza": 5.0,
    "ar.muyassar": 5.0,
    "ur.kanzuliman": 5.0,
    "ur.maududi": 5.0,
    "ur.qadri": 5.0,
    
    # Very High: Authentic Hadith Collections
    "sahih_bukhari": 4.5,
    "sahih_muslim": 4.5,
    "sunan_abu_dawud": 4.0,
    "sunan_an_nasai": 4.0,
    "sunan_ibn_majah": 4.0,
    "jami_at_tirmidhi": 4.0,
    "muwatta_malik": 4.0,
    
    # High: Scholarly Works & 40 Hadith
    "40_hadith_nawawi_highlights": 3.5,
    "tafsir_ibn_kathir_highlights": 3.5,
    
    # Medium-High: Fiqh & Islamic Knowledge
    "fiqh_fundamentals": 3.0,
    "aqeedah_essentials": 3.0,
    "seerah_prophet": 3.0,
    "islamic_ethics_akhlaq": 3.0,
    
    # Medium: General Islamic Resources
    "comprehensive_duas": 2.5,
    "99_names_of_allah_full": 2.5,
    "islamic_ground_truth_essentials": 2.5,
    "comprehensive_islamic_essentials": 2.5,
    "ramadan_hajj_guide": 2.5,
    "women_in_islam": 2.5,
    
    # Lower: Miscellaneous
    "test_auto_ingest": 1.0,
    "unknown": 1.0
}

AUTHENTICITY_MAPPING = {
    "quran_yusuf_ali": "Quranic (Highest Authority)",
    "quran_saheeh_international": "Quranic (Highest Authority)",
    "quran_pickthall": "Quranic (Highest Authority)",
    "quran_shakir": "Quranic (Highest Authority)",
    "en.ahmedraza": "Quranic (Highest Authority)",
    "ar.muyassar": "Quranic (Highest Authority)",
    "ur.kanzuliman": "Quranic (Highest Authority)",
    "ur.maududi": "Quranic (Highest Authority)",
    "ur.qadri": "Quranic (Highest Authority)",
    
    "sahih_bukhari": "Hadith-Sahih (Very High Authority)",
    "sahih_muslim": "Hadith-Sahih (Very High Authority)",
    "sunan_abu_dawud": "Hadith-Sunan (High Authority)",
    "sunan_an_nasai": "Hadith-Sunan (High Authority)",
    "sunan_ibn_majah": "Hadith-Sunan (High Authority)",
    "jami_at_tirmidhi": "Hadith-Tirmidhi (High Authority)",
    "muwatta_malik": "Hadith-Muwatta (High Authority)",
    
    "40_hadith_nawawi_highlights": "Scholarly Hadith (High Authority)",
    "tafsir_ibn_kathir_highlights": "Tafsir (High Authority)",
    
    "fiqh_fundamentals": "Islamic Jurisprudence (High Authority)",
    "aqeedah_essentials": "Islamic Creed (High Authority)",
    "seerah_prophet": "Prophetic Biography (High Authority)",
    "islamic_ethics_akhlaq": "Islamic Ethics (High Authority)",
    
    "comprehensive_duas": "Islamic Supplications (Medium Authority)",
    "99_names_of_allah_full": "Islamic Knowledge (Medium Authority)",
    "islamic_ground_truth_essentials": "Islamic Essentials (Medium Authority)",
    "comprehensive_islamic_essentials": "Islamic Essentials (Medium Authority)",
    "ramadan_hajj_guide": "Islamic Guide (Medium Authority)",
    "women_in_islam": "Islamic Knowledge (Medium Authority)"
}

# ============================================================================
# QUERY EXPANSION & INTENT DETECTION
# ============================================================================

QUERY_KEYWORDS = {
    "quran": ["quran", "quranic", "ayah", "ayat", "sura", "surah", "verse"],
    "hadith": ["hadith", "prophetic", "tradition", "narration", "reported"],
    "prayer": ["prayer", "salah", "salat", "praying", "pray", "worship"],
    "fasting": ["fasting", "ramadan", "fast", "sawm", "sawm"],
    "zakat": ["zakat", "charity", "alms", "zakah"],
    "hajj": ["hajj", "pilgrimage", "hajji", "mecca", "kaaba"],
    "fiqh": ["fiqh", "jurisprudence", "islamic law", "shariah", "ruling"],
    "aqeedah": ["aqeedah", "creed", "belief", "faith", "tawheed"],
    "ethics": ["ethics", "akhlaq", "character", "morality", "conduct"],
    "seerah": ["seerah", "biography", "prophet", "muhammed", "prophetic"]
}

def detect_query_intent(query: str) -> List[str]:
    """Detect what topics the user is interested in"""
    query_lower = query.lower()
    topics = []
    
    for topic, keywords in QUERY_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            topics.append(topic)
    
    return topics if topics else ["general"]

# ============================================================================
# QURAN FOUNDATION MCP BRIDGE
# ============================================================================

class QuranFoundationMCPBridge:
    """Bridge to Quran Foundation MCP for authentic Quranic data"""
    
    def __init__(self):
        self.available = False
        self.quran_data = self._load_quran_data()
        self.available = bool(self.quran_data)
    
    def _load_quran_data(self) -> Dict[str, Any]:
        """Load Quran data from local files"""
        try:
            # Try to find Quran data files in knowledge base
            kb_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(kb_path, "backend", "knowledge", "data")
            
            quran_data = {}
            
            # Check for any Quran JSON files
            import glob
            quran_files = glob.glob(os.path.join(data_path, "*quran*.json")) + \
                         glob.glob(os.path.join(data_path, "*quran*.txt"))
            
            for qfile in quran_files:
                try:
                    if qfile.endswith('.json'):
                        with open(qfile, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            quran_data[os.path.basename(qfile)] = data
                    elif qfile.endswith('.txt'):
                        with open(qfile, 'r', encoding='utf-8') as f:
                            quran_data[os.path.basename(qfile)] = f.read()
                except Exception as e:
                    logger.warning(f"Could not load {qfile}: {e}")
            
            if quran_data:
                logger.info(f"✅ Loaded Quran data from {len(quran_data)} files")
                return quran_data
            else:
                logger.warning("⚠️  No Quran data files found")
                return {}
        except Exception as e:
            logger.error(f"❌ Error loading Quran data: {e}")
            return {}
    
    def search_quran(self, query: str, k: int = 5) -> List[Dict]:
        """Search Quran for matching verses"""
        if not self.available or not self.quran_data:
            return []
        
        try:
            results = []
            query_lower = query.lower()
            
            # Search through loaded Quran data
            for source_name, data in self.quran_data.items():
                if isinstance(data, dict):
                    # Handle JSON format
                    for key, value in data.items():
                        if isinstance(value, str) and query_lower in value.lower():
                            results.append({
                                "text": value[:500],
                                "source": source_name,
                                "type": "quran",
                                "reference": key
                            })
                elif isinstance(data, str):
                    # Handle text format
                    for i, line in enumerate(data.split('\n')):
                        if query_lower in line.lower():
                            results.append({
                                "text": line[:500],
                                "source": source_name,
                                "type": "quran",
                                "reference": f"Line {i}"
                            })
            
            logger.debug(f"📖 Quran search returned {len(results)} results")
            return results[:k]
        except Exception as e:
            logger.error(f"❌ Quran search error: {e}")
            return []

# ============================================================================
# ADVANCED HYBRID RAG RETRIEVER
# ============================================================================

class AdvancedHybridRAGRetriever:
    """Advanced retrieval combining BM25, vector search, and MCP"""
    
    def __init__(self):
        self.local_kb = self._init_local_kb()
        self.mcp_bridge = QuranFoundationMCPBridge()
        self.reranker = self._init_reranker()
        logger.info("✅ Advanced Hybrid RAG Retriever initialized")
    
    def _init_local_kb(self):
        """Initialize local knowledge base"""
        try:
            from backend.knowledge.local_knowledge_tools import LocalKnowledgeBase
            return LocalKnowledgeBase()
        except Exception as e:
            logger.error(f"Failed to initialize local KB: {e}")
            return None
    
    def _init_reranker(self):
        """Initialize cross-encoder reranker"""
        try:
            from sentence_transformers import CrossEncoder
            return CrossEncoder('BAAI/bge-reranker-v2-m3')
        except Exception as e:
            logger.warning(f"⚠️  Reranker not available: {e}")
            return None
    
    def retrieve_advanced(self, query: str, k: int = 15) -> Dict[str, Any]:
        """
        Advanced retrieval with:
        1. BM25 with source priority weighting
        2. Vector semantic search
        3. Query-aware ranking
        4. Quran Foundation MCP integration
        5. Intelligent result combination
        """
        all_results = []
        source_stats = {"bm25": 0, "vector": 0, "mcp": 0}
        
        # Detect query intent for better ranking
        topics = detect_query_intent(query)
        logger.debug(f"📌 Detected topics: {topics}")
        
        # ========== Strategy 1: Enhanced BM25 with Source Weighting ==========
        if self.local_kb and self.local_kb.bm25_data:
            try:
                tokens = _tokenize(query)
                bm25_model = self.local_kb.bm25_data.get("bm25")
                texts = self.local_kb.bm25_data.get("texts", [])
                metadata_list = self.local_kb.bm25_data.get("metadata", [])
                
                if bm25_model and texts:
                    scores = bm25_model.get_scores(tokens)
                    
                    # Apply source priority weighting
                    weighted_scores = []
                    for i, score in enumerate(scores):
                        source = metadata_list[i].get('source', 'unknown') if i < len(metadata_list) else 'unknown'
                        source_file = os.path.basename(source)
                        priority = SOURCE_PRIORITY.get(source_file, 1.0)
                        weighted_score = score * priority
                        weighted_scores.append((i, weighted_score, score, source))
                    
                    # Get top k by weighted score
                    weighted_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    bm25_count = 0
                    for idx, weighted, original, source in weighted_scores[:k*2]:  # Get more candidates
                        if original > 0:
                            meta = metadata_list[idx] if idx < len(metadata_list) else {}
                            source_file = os.path.basename(source)
                            
                            all_results.append({
                                "content": texts[idx],
                                "metadata": meta,
                                "score": float(original),
                                "weighted_score": float(weighted),
                                "retrieval_method": "bm25",
                                "source_priority": SOURCE_PRIORITY.get(source_file, 1.0),
                                "authenticity": AUTHENTICITY_MAPPING.get(source_file, "Islamic Reference"),
                                "source_file": source_file
                            })
                            bm25_count += 1
                            if bm25_count >= k:
                                break
                    
                    source_stats["bm25"] = bm25_count
                    logger.debug(f"📝 BM25 returned {bm25_count} weighted results")
            except Exception as e:
                logger.warning(f"⚠️  Enhanced BM25 error: {e}")
        
        # ========== Strategy 2: Vector Semantic Search ==========
        if self.local_kb and self.local_kb.db:
            try:
                vector_results = self.local_kb.db.similarity_search_with_scores(query, k=k)
                
                for doc, score in vector_results:
                    # Skip duplicates from BM25
                    if not any(abs(r["score"] - score) < 0.05 and \
                              r["content"][:50] == doc.page_content[:50] for r in all_results):
                        meta = doc.metadata if hasattr(doc, 'metadata') else {}
                        source_file = os.path.basename(meta.get('source', 'unknown'))
                        
                        all_results.append({
                            "content": doc.page_content,
                            "metadata": meta,
                            "score": score,
                            "retrieval_method": "vector",
                            "source_priority": SOURCE_PRIORITY.get(source_file, 1.0),
                            "authenticity": AUTHENTICITY_MAPPING.get(source_file, "Islamic Reference"),
                            "source_file": source_file
                        })
                
                source_stats["vector"] = sum(1 for r in all_results if r["retrieval_method"] == "vector")
                logger.debug(f"🧠 Vector search returned {source_stats['vector']} results")
            except Exception as e:
                logger.warning(f"⚠️  Vector search error: {e}")
        
        # ========== Strategy 3: Quran Foundation MCP ==========
        if self.mcp_bridge.available:
            try:
                mcp_results = self.mcp_bridge.search_quran(query, k=k//2)
                for result in mcp_results:
                    all_results.append({
                        "content": result.get("text", ""),
                        "metadata": {
                            "source": result.get("source", "Quran"),
                            "reference": result.get("reference", ""),
                            "type": "quran"
                        },
                        "score": 0.95,
                        "retrieval_method": "mcp",
                        "source_priority": 5.0,
                        "authenticity": "Quranic (Highest Authority)",
                        "source_file": "quran_foundation"
                    })
                source_stats["mcp"] = len(mcp_results)
                logger.debug(f"📖 Quran Foundation returned {len(mcp_results)} results")
            except Exception as e:
                logger.warning(f"⚠️  MCP retrieval error: {e}")
        
        # ========== Intelligent Result Combination ==========
        if not all_results:
            return {
                "query": query,
                "results": [],
                "total_retrieved": 0,
                "sources": source_stats,
                "topics": topics,
                "error": "No results found"
            }
        
        # Deduplicate similar results
        unique_results = self._deduplicate_results(all_results)
        
        # Rerank for quality
        if self.reranker and len(unique_results) > 1:
            unique_results = self._rerank_results(query, unique_results)
        
        # Final sorting: prioritize source authenticity and relevance
        final_results = sorted(
            unique_results,
            key=lambda x: (
                x.get("source_priority", 1.0),
                x.get("score", 0)
            ),
            reverse=True
        )[:k]
        
        return {
            "query": query,
            "results": final_results,
            "total_retrieved": len(final_results),
            "sources": source_stats,
            "topics": topics,
            "retrieval_strategies": ["bm25_weighted", "vector", "mcp"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate or near-identical results"""
        unique = []
        seen_hashes = set()
        
        for result in results:
            content = result.get("content", "")[:100]
            content_hash = hash(content)
            
            if content_hash not in seen_hashes:
                unique.append(result)
                seen_hashes.add(content_hash)
        
        return unique
    
    def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank results using cross-encoder"""
        try:
            contents = [r["content"] for r in results]
            queries = [query] * len(contents)
            
            scores = self.reranker.predict(list(zip(queries, contents)))
            
            for i, result in enumerate(results):
                result["rerank_score"] = float(scores[i])
            
            results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
            return results
        except Exception as e:
            logger.warning(f"⚠️  Reranking error: {e}")
            return results

# ============================================================================
# PUBLIC API FUNCTIONS
# ============================================================================

def retrieve_advanced_knowledge(query: str, k: int = 15) -> tuple:
    """
    Advanced retrieval with hybrid sources - returns (results, has_results) for API
    compatibility with proper source weighting and authenticity tracking
    """
    try:
        retriever = AdvancedHybridRAGRetriever()
        result_dict = retriever.retrieve_advanced(query, k)
        
        results = result_dict.get("results", [])
        has_results = len(results) > 0
        
        logger.info(f"✅ Retrieved {len(results)} results for: {query[:50]}")
        return results, has_results
    except Exception as e:
        logger.error(f"❌ Advanced retrieval failed: {e}")
        return [], False

def check_advanced_rag_system() -> Dict[str, Any]:
    """Check status of advanced RAG system"""
    try:
        retriever = AdvancedHybridRAGRetriever()
        
        stats = {
            "status": "operational",
            "bm25_available": retriever.local_kb and bool(retriever.local_kb.bm25_data),
            "vector_available": retriever.local_kb and bool(retriever.local_kb.db),
            "mcp_available": retriever.mcp_bridge.available,
            "source_priority_active": True,
            "reranking_active": retriever.reranker is not None,
            "bm25_docs": len(retriever.local_kb.bm25_data.get("texts", [])) if (retriever.local_kb and retriever.local_kb.bm25_data) else 0,
            "vector_docs": retriever.local_kb.db._collection.count() if (retriever.local_kb and retriever.local_kb.db) else 0,
            "mcp_quran_files": len(retriever.mcp_bridge.quran_data) if retriever.mcp_bridge.quran_data else 0,
        }
        
        logger.info(f"✅ Advanced RAG System Status: {stats}")
        return stats
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return {"status": "error", "error": str(e)}

def get_local_kb():
    """Get local knowledge base instance"""
    try:
        from backend.knowledge.local_knowledge_tools import LocalKnowledgeBase
        return LocalKnowledgeBase()
    except Exception as e:
        logger.error(f"Failed to get local KB: {e}")
        return None

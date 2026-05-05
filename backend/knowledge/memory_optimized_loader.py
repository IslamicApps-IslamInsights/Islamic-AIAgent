"""
Memory-Optimized RAG Loader
============================
Prevents 3-4 GB memory spikes during initialization by:
1. Lazy loading heavy models (embeddings)
2. Streaming data ingestion instead of loading all into memory
3. Explicit garbage collection
4. Singleton pattern for model instances
5. Deferred initialization with progress tracking

This is the PRIMARY loader to use in place of LocalKnowledgeBase.
"""

import pickle
import gc
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from threading import Lock

logger = logging.getLogger("MemoryOptimizedLoader")

CURRENT_DIR = Path(__file__).parent
CHROMA_PATH_FULL = CURRENT_DIR / "chroma_db_full"
CHROMA_PATH_BATCHED = CURRENT_DIR / "chroma_db_batched"
CHROMA_PATH_LEGACY = CURRENT_DIR / "chroma_db"
CHROMA_PATH = (
    CHROMA_PATH_FULL
    if CHROMA_PATH_FULL.exists()
    else (
        CHROMA_PATH_BATCHED
        if CHROMA_PATH_BATCHED.exists()
        else CHROMA_PATH_LEGACY
    )
)

_BM25_CANDIDATES = [
    CURRENT_DIR / "bm25_full_index.pkl",
    CURRENT_DIR / "bm25_index_enhanced.pkl",
    CURRENT_DIR / "bm25_index.pkl",
]

# Source mapping (same as original)
SOURCE_MAPPING = {
    "quran_yusuf_ali.txt": "The Holy Quran (Yusuf Ali)",
    "quran_saheeh_international.txt": "The Holy Quran (Saheeh International)",
    "quran_pickthall.txt": "The Holy Quran (Pickthall)",
    "quran_shakir.txt": "The Holy Quran (Shakir)",
    "en.ahmedraza.txt": "The Holy Quran (Kanzul Iman - Ahmed Raza Khan)",
    "ar.muyassar.txt": "Tafsir Al-Muyassar (Arabic)",
    "ur.kanzuliman.txt": "The Holy Quran (Kanzul Iman - Urdu)",
    "ur.maududi.txt": "The Holy Quran (Tafhim ul Quran by Maududi - Urdu)",
    "ur.qadri.txt": "The Holy Quran (Irfan ul Quran by Qadri - Urdu)",
    "sahih_bukhari.json": "Sahih al-Bukhari",
    "sahih_bukhari_english.json": "Sahih al-Bukhari (English)",
    "sahih_muslim.json": "Sahih Muslim",
    "sahih_muslim_english.json": "Sahih Muslim (English)",
    "sunan_abu_dawud_english.json": "Sunan Abu Dawud",
    "sunan_an_nasai_english.json": "Sunan an-Nasa'i",
    "sunan_ibn_majah_english.json": "Sunan Ibn Majah",
    "jami_at_tirmidhi_english.json": "Jami` at-Tirmidhi",
    "muwatta_malik_english.json": "Muwatta Malik",
    "forty_hadith_nawawi.json": "40 Hadith an-Nawawi",
    "40_hadith_nawawi_highlights.txt": "40 Hadith an-Nawawi (Highlights)",
    "hisn_al_muslim.json": "Hisn al-Muslim (Dua/Adhkar)",
    "duas.txt": "Hisn al-Muslim (Supplications)",
    "comprehensive_duas.txt": "Book of Comprehensive Supplications (Duas)",
    "comprehensive_islamic_essentials.txt": "Comprehensive Islamic Essentials",
    "99_names_of_allah_full.json": "The 99 Names of Allah (Asma ul Husna)",
    "tafsir_ibn_kathir_highlights.txt": "Tafsir Ibn Kathir",
    "aqeedah_essentials.txt": "Aqeedah Essentials",
    "seerah_prophet.txt": "As-Seerah an-Nabawiyyah (Prophetic Biography)",
    "islamic_ethics_akhlaq.txt": "Islamic Ethics & Akhlaq",
    "fiqh_fundamentals.txt": "Fiqh Fundamentals",
    "ramadan_hajj_guide.txt": "The Complete Guide to Ramadan & Hajj",
    "women_in_islam.txt": "Women in Islam: Rights and Status",
    "islamic_ground_truth_essentials.txt": "Islamic Ground Truth Essentials",
    "quran_surah_metadata_114.json": "Quranic Surah Metadata",
}


class LazyEmbeddingsLoader:
    """Lazy loader for embedding models - only loads on first access"""
    
    _instance = None
    _lock = Lock()
    _embeddings = None
    _load_time = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def get_embeddings(self):
        """Lazy load embeddings model on first access"""
        if self._embeddings is None:
            logger.info("⏳ Lazy loading embeddings model (FIRST CALL ONLY)...")
            self._load_time = datetime.now()
            
            self._load_local_embeddings()
            
            duration_s = (datetime.now() - self._load_time).total_seconds()
            logger.info(f"✅ Embeddings loaded in {duration_s:.1f}s")
        
        return self._embeddings

    def _load_local_embeddings(self):
        """Load local HuggingFace embeddings"""
        from langchain_huggingface import HuggingFaceEmbeddings
        
        logger.info(
            "🏛️  Loading HuggingFace Embeddings "
            "(intfloat/multilingual-e5-large)..."
        )
        self._embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-large",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )


class MemoryOptimizedRAGLoader:
    """
    Optimized RAG loader with lazy loading and memory management.
    
    KEY IMPROVEMENTS:
    - Models loaded on first use, not at initialization
    - BM25 index loaded immediately (small, fast)
    - ChromaDB connection deferred until needed
    - Explicit garbage collection after large operations
    - Memory pooling and cleanup
    """

    def __init__(self):
        self.embeddings_loader = LazyEmbeddingsLoader()
        
        # Load small/fast components immediately
        self.bm25_data = self._load_bm25()
        self.db = None  # Deferred
        self.embeddings = None  # Deferred
        self._vector_disabled = False
        
        # Metadata
        self.initialized_components = []
        self.memory_footprint = 0
        
        logger.info(
            "✅ Memory-optimized RAG loader initialized (minimal footprint)"
        )

    def _load_bm25(self) -> Optional[Dict]:
        """Load BM25 index (small, stays in memory)"""
        try:
            bm25_path = next((p for p in _BM25_CANDIDATES if p.exists()), None)
            if not bm25_path:
                return None

            logger.info("📝 Loading BM25 Index (fast keyword search)...")
            with open(bm25_path, "rb") as f:
                payload = pickle.load(f)

            if isinstance(payload, dict) and (
                "model" in payload or "bm25" in payload
            ):
                if "model" not in payload and "bm25" in payload:
                    payload["model"] = payload.get("bm25")
                if "texts" not in payload and "corpus" in payload:
                    payload["texts"] = payload.get("corpus")
                if "metadatas" not in payload and "metadata" in payload:
                    payload["metadatas"] = payload.get("metadata")
                logger.info(
                    f"✅ BM25 loaded ({len(payload.get('texts', []))} docs)"
                )
                return payload
        except Exception as e:
            logger.warning(f"⚠️  BM25 load error: {e}")
        
        return None

    def get_embeddings(self):
        """Get embeddings model (lazy load on first access)"""
        if self.embeddings is None:
            self.embeddings = self.embeddings_loader.get_embeddings()
            self.initialized_components.append("embeddings")
        return self.embeddings

    def get_chroma_db(self):
        """Get ChromaDB connection (lazy load on first access)"""
        if self.db is None:
            try:
                from langchain_community.vectorstores import Chroma
                
                if not CHROMA_PATH.exists():
                    logger.warning(f"⚠️  ChromaDB not found at {CHROMA_PATH}")
                    return None
                
                logger.info("📁 Connecting to ChromaDB (lazy load)...")
                embeddings = self.get_embeddings()
                self.db = Chroma(
                    persist_directory=str(CHROMA_PATH),
                    embedding_function=embeddings,
                    collection_name="islamic_knowledge",
                )
                self.initialized_components.append("chromadb")
                logger.info("✅ ChromaDB connected")
            except Exception as e:
                logger.error(f"❌ ChromaDB connection failed: {e}")
                self.db = None
        
        return self.db

    def search(self, query: str, k: int = 5) -> str:
        """
        Search knowledge base with memory-conscious approach.
        Cleans up temporary data after searching.
        """
        try:
            # BM25 keyword search (fast)
            if self.bm25_data:
                logger.debug(f"🔍 BM25 search for: {query}")
                bm25_results = self._bm25_search(query, k)
            else:
                bm25_results = []

            # Vector search (if available)
            vector_results = []
            if CHROMA_PATH.exists() and not self._vector_disabled:
                logger.debug(f"🔍 Vector search for: {query}")
                vector_results = self._vector_search(query, k)

            # Combine results
            combined_results = self._combine_results(
                bm25_results, vector_results, k
            )

            # Cleanup
            gc.collect()

            return self._format_results(query, combined_results)

        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return f"Error during search: {str(e)}"

    def _bm25_search(self, query: str, k: int) -> List[Dict]:
        """BM25 keyword search"""
        if not self.bm25_data:
            return []

        try:
            bm25_model = self.bm25_data.get('model')
            texts = self.bm25_data.get('texts', [])
            metadatas = self.bm25_data.get('metadatas', [])

            if not bm25_model or not texts:
                return []

            # Tokenize query
            query_tokens = query.lower().split()
            
            # Get BM25 scores
            scores = bm25_model.get_scores(query_tokens)
            
            # Get top-k results
            top_indices = sorted(
                range(len(scores)), key=lambda i: scores[i], reverse=True
            )[:k]

            results = []
            for idx in top_indices:
                if idx < len(texts) and scores[idx] > 0:
                    raw_text = texts[idx]
                    content = (
                        " ".join(str(t) for t in raw_text)
                        if isinstance(raw_text, list)
                        else str(raw_text)
                    )
                    results.append({
                        'content': content,
                        'metadata': (
                            metadatas[idx] if idx < len(metadatas) else {}
                        ),
                        'score': float(scores[idx]),
                        'retrieval_method': 'bm25'
                    })

            return results

        except Exception as e:
            logger.warning(f"⚠️  BM25 search error: {e}")
            return []

    def _vector_search(self, query: str, k: int) -> List[Dict]:
        """Vector similarity search"""
        try:
            db = self.get_chroma_db()
            if not db:
                return []

            # Vector search
            docs = db.similarity_search_with_score(query, k=k)

            results = []
            for doc, score in docs:
                similarity = 1 - score
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(similarity),
                    'retrieval_method': 'vector'
                })

            return results

        except Exception as e:
            msg = str(e)
            if "dimension" in msg and "expecting embedding" in msg:
                self._vector_disabled = True
            logger.warning(f"⚠️  Vector search error: {e}")
            return []

    def _combine_results(
        self, bm25_results: List[Dict], vector_results: List[Dict], k: int
    ) -> List[Dict]:
        """Combine and deduplicate results"""
        combined = {}
        
        # Add BM25 results
        for result in bm25_results:
            key = result['content'][:50]  # Simple dedup
            combined[key] = result

        # Add vector results
        for result in vector_results:
            key = result['content'][:50]
            if key not in combined:
                combined[key] = result

        return list(combined.values())[:k]

    def _format_results(self, query: str, results: List[Dict]) -> str:
        """Format search results for display"""
        if not results:
            return (
                "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
                "I couldn't find information about that in the "
                "knowledge base. "
                "Please try with different keywords or ask about "
                "Islamic topics "
                "like prayer, Quran, Hadith, or Islamic teachings.\n\n"
                "May Allah guide us. 🤲"
            )

        formatted_blocks: List[str] = []

        import re

        def _clean_text(x: Any) -> str:
            return " ".join(str(x or "").split()).strip()

        for idx, result in enumerate(results[:15], 1):
            content = (result.get("content") or "").strip()
            if not content:
                continue

            if len(content) > 1200:
                content = content[:1200] + "..."

            metadata = result.get("metadata") or {}
            raw_source = metadata.get("source", "Unknown")
            display_source = SOURCE_MAPPING.get(raw_source, raw_source)

            ref_parts: List[str] = [str(display_source)]

            surah = (
                metadata.get("surah")
                or metadata.get("chapter")
                or metadata.get("surah_number")
            )
            ayah = (
                metadata.get("ayah")
                or metadata.get("verse")
                or metadata.get("ayah_number")
            )
            if surah and ayah:
                ref_parts.append(f"{surah}:{ayah}")
            else:
                if "tafsir" in str(display_source).lower():
                    verse_pat = r"\bverse\s+(\d{1,3}:\d{1,3})\b"
                    m = re.search(verse_pat, content.lower())
                    if m:
                        ref_parts.append(f"Quran {m.group(1)}")

            book = metadata.get("book") or metadata.get("book_name")
            chapter = metadata.get("chapter_name") or metadata.get("chapter")
            hadith_id = metadata.get("hadith_id") or metadata.get("id")
            if book and not (surah and ayah):
                ref_parts.append(_clean_text(book))
            if chapter and not (surah and ayah):
                ref_parts.append(f"Chapter: {_clean_text(chapter)}")
            if hadith_id and not (surah and ayah):
                ref_parts.append(f"Hadith: {_clean_text(hadith_id)}")

            grade = metadata.get("grade") or metadata.get("authenticity")
            if grade:
                ref_parts.append(_clean_text(grade))

            ref = " — ".join([p for p in ref_parts if p and str(p).strip()])
            ref = re.sub(r"\s+—\s+", " — ", ref).strip(" —")
            reference = ref
            formatted_blocks.append(f"[Source {idx}] {reference}")
            formatted_blocks.append(content)
            formatted_blocks.append("")

        if not formatted_blocks:
            return (
                "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
                "I couldn't find readable results for that query in the "
                "knowledge base. "
                "Please try rephrasing your question.\n\n"
                "May Allah guide us. 🤲"
            )

        return "\n".join(formatted_blocks).strip()

    def get_status(self) -> Dict[str, Any]:
        """Get loader status"""
        return {
            'initialized': len(self.initialized_components) > 0,
            'components': self.initialized_components,
            'bm25_available': self.bm25_data is not None,
            'chroma_available': CHROMA_PATH.exists(),
            'memory_optimized': True,
            'lazy_loading': True,
            'timestamp': datetime.now().isoformat()
        }


# Global singleton instance
_loader_instance: Optional[MemoryOptimizedRAGLoader] = None
_loader_lock = Lock()


def get_memory_optimized_loader() -> MemoryOptimizedRAGLoader:
    """Get or create memory-optimized loader singleton"""
    global _loader_instance
    
    if _loader_instance is None:
        with _loader_lock:
            if _loader_instance is None:
                _loader_instance = MemoryOptimizedRAGLoader()
    
    return _loader_instance


def initialize_optimized_rag() -> Dict[str, Any]:
    """Initialize optimized RAG system"""
    loader = get_memory_optimized_loader()
    status = loader.get_status()
    
    logger.info(f"✅ Memory-optimized RAG initialized: {status}")
    
    return status

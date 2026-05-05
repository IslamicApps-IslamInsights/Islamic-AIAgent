"""
Islamic AI Agent - Robust Data Ingestion with Best Practices
Implements production-grade data pipeline with validation, error handling, and optimization
"""

import os
import glob
import json
import hashlib
import logging
import pickle
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback
from collections import defaultdict
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)
logger = logging.getLogger("IngestBestPractices")

# ============================================================================
# DATA MODELS FOR TRACKING
# ============================================================================

@dataclass
class IngestionStats:
    """Track ingestion pipeline statistics"""
    start_time: float
    total_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0
    total_documents: int = 0
    total_chunks: int = 0
    total_size_mb: float = 0.0
    deduped_chunks: int = 0
    errors: Dict[str, int] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = defaultdict(int)
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'elapsed_time_sec': self.elapsed_time,
            'total_chunks': self.total_chunks,
            'dedup_ratio': self.deduped_chunks / max(1, self.total_chunks)
        }


# ============================================================================
# CONFIGURATION
# ============================================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(CURRENT_DIR, "data")
CHROMA_PATH = os.path.join(CURRENT_DIR, "chroma_db")
BM25_PATH = os.path.join(CURRENT_DIR, "bm25_index.pkl")
STATE_FILE = os.path.join(CURRENT_DIR, "ingestion_state.json")
STATS_FILE = os.path.join(CURRENT_DIR, "ingestion_stats.json")

# Best practice parameters
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"  # World-class multilingual embeddings
CHUNK_SIZE = 1200  # Larger chunks for Islamic context (hadiths, verses)
CHUNK_OVERLAP = 300  # Significant overlap for continuity
BATCH_SIZE = 100  # Process vectors in batches
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ============================================================================
# VALIDATION & QUALITY CHECKS
# ============================================================================

class DocumentValidator:
    """Validate document quality before ingestion"""
    
    MIN_CONTENT_LENGTH = 20  # Minimum characters per document
    MIN_WORDS = 5
    MAX_CONTENT_LENGTH = 50000  # Cap on unreasonably large docs
    REQUIRED_METADATA_FIELDS = ['source', 'type']
    
    @classmethod
    def validate(cls, doc: Document) -> Tuple[bool, Optional[str]]:
        """
        Validate a document
        Returns: (is_valid, error_message)
        """
        content = doc.page_content.strip()
        
        # Check content length
        if len(content) < cls.MIN_CONTENT_LENGTH:
            return False, f"Content too short: {len(content)} chars (min: {cls.MIN_CONTENT_LENGTH})"
        
        if len(content) > cls.MAX_CONTENT_LENGTH:
            logger.warning(f"Content very long: {len(content)} chars, truncating")
            doc.page_content = content[:cls.MAX_CONTENT_LENGTH]
        
        # Check word count
        words = content.split()
        if len(words) < cls.MIN_WORDS:
            return False, f"Too few words: {len(words)} (min: {cls.MIN_WORDS})"
        
        # Check metadata
        for field in cls.REQUIRED_METADATA_FIELDS:
            if field not in doc.metadata:
                return False, f"Missing metadata field: {field}"
        
        return True, None
    
    @classmethod
    def validate_batch(cls, docs: List[Document]) -> Tuple[List[Document], Dict[str, int]]:
        """Validate batch of documents"""
        valid_docs = []
        stats = {"total": len(docs), "valid": 0, "invalid": 0, "errors": defaultdict(int)}
        
        for doc in docs:
            is_valid, error = cls.validate(doc)
            if is_valid:
                valid_docs.append(doc)
                stats["valid"] += 1
            else:
                stats["invalid"] += 1
                stats["errors"][error] += 1
        
        return valid_docs, stats


# ============================================================================
# DEDUPLICATION ENGINE
# ============================================================================

class DeduplicationEngine:
    """Detect and remove duplicate content"""
    
    def __init__(self):
        self.content_hashes = {}
        self.metadata_hashes = {}
    
    def get_content_hash(self, content: str) -> str:
        """Generate hash of content"""
        return hashlib.md5(content.strip().lower().encode()).hexdigest()
    
    def get_metadata_hash(self, metadata: Dict[str, Any]) -> str:
        """Generate hash of metadata"""
        # Sort and serialize for consistent hashing
        meta_str = json.dumps(metadata, sort_keys=True, default=str)
        return hashlib.md5(meta_str.encode()).hexdigest()
    
    def is_duplicate(self, doc: Document) -> bool:
        """Check if document is a duplicate"""
        content_hash = self.get_content_hash(doc.page_content)
        
        if content_hash in self.content_hashes:
            return True
        
        self.content_hashes[content_hash] = True
        return False
    
    def deduplicate_batch(self, docs: List[Document]) -> Tuple[List[Document], int]:
        """Remove duplicates from batch"""
        unique_docs = []
        dedup_count = 0
        
        for doc in docs:
            if not self.is_duplicate(doc):
                unique_docs.append(doc)
            else:
                dedup_count += 1
        
        return unique_docs, dedup_count


# ============================================================================
# METADATA ENRICHMENT
# ============================================================================

class MetadataEnricher:
    """Enrich documents with additional metadata for better retrieval"""
    
    @staticmethod
    def enrich(doc: Document, file_name: str, position: int = 0) -> Document:
        """Add enrichment metadata to document"""
        
        # Calculate estimated reading time (avg 200 words/min)
        word_count = len(doc.page_content.split())
        reading_time_min = max(1, word_count // 200)
        
        # Extract type hints from content
        content_lower = doc.page_content.lower()
        type_hints = []
        if 'hadith' in content_lower or 'prophet' in content_lower:
            type_hints.append('hadith')
        if 'quran' in content_lower or 'ayah' in content_lower or 'verse' in content_lower:
            type_hints.append('quran')
        if 'dua' in content_lower or 'supplication' in content_lower:
            type_hints.append('dua')
        if 'scholar' in content_lower or 'interpretation' in content_lower or 'tafsir' in content_lower:
            type_hints.append('scholarly')
        
        # Enhance metadata
        enriched_metadata = {
            **doc.metadata,
            'ingestion_date': datetime.now().isoformat(),
            'word_count': word_count,
            'reading_time_minutes': reading_time_min,
            'type_hints': type_hints,
            'position_in_file': position,
            'file_name': file_name,
            'chunk_id': f"{file_name}_{position}"
        }
        
        doc.metadata = enriched_metadata
        return doc


# ============================================================================
# FILE LOADER WITH BEST PRACTICES
# ============================================================================

class RobustFileLoader:
    """Load files with error recovery and best practices"""
    
    @staticmethod
    def load_json_file(file_path: str, file_name: str) -> List[Document]:
        """Load JSON with error handling"""
        documents = []
        
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            
            # Hadith structure
            if "hadiths" in data and isinstance(data["hadiths"], list):
                logger.info(f"  📖 Parsing {len(data['hadiths'])} hadiths")
                for idx, h in enumerate(data["hadiths"]):
                    try:
                        eng = h.get("english", {}) or {}
                        text = eng.get("text", "").strip()
                        if not text:
                            continue
                        
                        narrator = eng.get("narrator", "")
                        hadith_id = h.get("id") or h.get("hadithnumber")
                        book = h.get("bookName") or h.get("book_name") or "General"
                        chapter = h.get("chapterName") or h.get("chapter_name") or "General"
                        grade = h.get("grade") or h.get("status") or "Authentic"
                        
                        content = f"""Hadith #{hadith_id}
Book: {book}
Chapter: {chapter}
Authenticity: {grade}
Narrator: {narrator}

Text: {text}"""
                        
                        doc = Document(
                            page_content=content,
                            metadata={
                                "source": file_name,
                                "type": "hadith",
                                "id": str(hadith_id),
                                "book": book,
                                "chapter": chapter,
                                "grade": grade
                            }
                        )
                        documents.append(doc)
                    except Exception as e:
                        logger.warning(f"  ⚠️ Error parsing hadith {idx}: {e}")
                        continue
            
            # Dua/Adhkar structure
            elif "English" in data and isinstance(data["English"], list):
                logger.info(f"  🤲 Parsing Duas/Adhkar")
                for category in data["English"]:
                    category_name = category.get("category", "General")
                    for item in category.get("content", []):
                        try:
                            text = item.get("text", "").strip()
                            reference = item.get("reference", "")
                            if text:
                                doc = Document(
                                    page_content=f"Category: {category_name}\n\nDua/Adhkar:\n{text}\n\nReference: {reference}",
                                    metadata={
                                        "source": file_name,
                                        "type": "dua",
                                        "category": category_name,
                                        "reference": reference
                                    }
                                )
                                documents.append(doc)
                        except Exception as e:
                            logger.warning(f"  ⚠️ Error parsing dua: {e}")
                            continue
            
            # Names/Attributes structure
            elif "data" in data and isinstance(data["data"], list):
                logger.info(f"  ✨ Parsing {len(data['data'])} entries")
                for entry in data["data"]:
                    try:
                        name = entry.get("name", "")
                        en = entry.get("en", {}) or {}
                        if name:
                            doc = Document(
                                page_content=f"Name: {name}\nMeaning: {en.get('meaning', 'N/A')}\nTransliteration: {en.get('transliteration', 'N/A')}",
                                metadata={
                                    "source": file_name,
                                    "type": "attribute",
                                    "name": name
                                }
                            )
                            documents.append(doc)
                    except Exception as e:
                        logger.warning(f"  ⚠️ Error parsing entry: {e}")
                        continue
            
            logger.info(f"✅ Successfully extracted {len(documents)} documents from {file_name}")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error in {file_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading {file_name}: {e}")
            raise
        
        return documents
    
    @staticmethod
    def load_text_file(file_path: str, file_name: str) -> List[Document]:
        """Load text file with error handling"""
        documents = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Split into paragraphs
            paragraphs = text.split("\n\n")
            logger.info(f"  📄 Extracted {len(paragraphs)} paragraphs")
            
            for para in paragraphs:
                if para.strip():
                    doc = Document(
                        page_content=para.strip(),
                        metadata={
                            "source": file_name,
                            "type": "text"
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"✅ Extracted {len(documents)} documents from {file_name}")
            
        except Exception as e:
            logger.error(f"❌ Error loading {file_name}: {e}")
            raise
        
        return documents


# ============================================================================
# CHUNK OPTIMIZATION
# ============================================================================

class SmartChunker:
    """Optimize text chunking for Islamic content"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True,
            separators=["\n\n", "\n", " ", ""]  # Islamic content preserves paragraph structure
        )
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into optimized chunks"""
        chunks = self.splitter.split_documents(documents)
        
        # Add chunk position metadata
        doc_counters = defaultdict(int)
        for chunk in chunks:
            source = chunk.metadata.get("source", "unknown")
            chunk.metadata["chunk_index"] = doc_counters[source]
            doc_counters[source] += 1
        
        # Add total chunk count
        for chunk in chunks:
            source = chunk.metadata.get("source", "unknown")
            chunk.metadata["total_chunks"] = doc_counters[source]
        
        logger.info(f"✅ Created {len(chunks)} optimized chunks")
        return chunks


# ============================================================================
# VECTOR DATABASE MANAGEMENT
# ============================================================================

class VectorDBManager:
    """Manage ChromaDB with best practices"""
    
    def __init__(self):
        self.embedding_model = EMBEDDING_MODEL
    
    def _get_embeddings(self):
        """Get embeddings with caching"""
        return HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def update_vectordb(self, chunks: List[Document]) -> Dict[str, Any]:
        """Update ChromaDB with batching"""
        try:
            logger.info(f"🔄 Updating ChromaDB with {len(chunks)} chunks...")
            
            embeddings = self._get_embeddings()
            
            # Create or connect to DB
            if os.path.exists(CHROMA_PATH) and os.listdir(CHROMA_PATH):
                logger.info(f"📦 Connecting to existing ChromaDB...")
                vector_db = Chroma(
                    persist_directory=CHROMA_PATH,
                    embedding_function=embeddings
                )
            else:
                logger.info(f"📦 Creating new ChromaDB...")
                vector_db = Chroma.from_documents(
                    documents=chunks[:min(100, len(chunks))],  # Start small
                    embedding=embeddings,
                    persist_directory=CHROMA_PATH
                )
                chunks = chunks[100:]  # Process remaining
            
            # Batch insert remaining chunks
            batch_size = BATCH_SIZE
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                vector_db.add_documents(batch)
                logger.info(f"  ✅ Batch {(i//batch_size)+1}: added {len(batch)} chunks")
            
            vector_db.persist()
            logger.info(f"✅ ChromaDB updated successfully")
            
            return {
                "status": "success",
                "chunks_added": len(chunks),
                "db_path": CHROMA_PATH
            }
        
        except Exception as e:
            logger.error(f"❌ VectorDB error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# ============================================================================
# BM25 INDEX MANAGEMENT
# ============================================================================

class BM25Manager:
    """Manage BM25 index for hybrid search"""
    
    @staticmethod
    def build_bm25_index(chunks: List[Document]) -> Dict[str, Any]:
        """Build BM25 index"""
        try:
            from rank_bm25 import BM25Okapi
            from nltk.tokenize import word_tokenize
            import nltk
            
            # Download tokenizer if needed
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                logger.info("📥 Downloading NLTK tokenizer...")
                nltk.download('punkt', quiet=True)
            
            logger.info(f"🎯 Building BM25 index from {len(chunks)} chunks...")
            
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            
            # Tokenize
            corpus = [word_tokenize(text.lower()) for text in texts]
            
            # Build BM25
            bm25_model = BM25Okapi(corpus)
            
            # Save
            payload = {
                'bm25': bm25_model,
                'texts': texts,
                'metadata': metadatas,
                'total_docs': len(texts),
                'build_time': datetime.now().isoformat()
            }
            
            with open(BM25_PATH, 'wb') as f:
                pickle.dump(payload, f)
            
            size_mb = os.path.getsize(BM25_PATH) / 1024 / 1024
            logger.info(f"✅ BM25 index saved ({size_mb:.1f} MB) with {len(texts)} documents")
            
            return {
                "status": "success",
                "documents": len(texts),
                "size_mb": size_mb,
                "path": BM25_PATH
            }
        
        except Exception as e:
            logger.error(f"❌ BM25 error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class IngestionState:
    """Manage ingestion state for incremental processing"""
    
    @staticmethod
    def load() -> Dict[str, Any]:
        """Load state"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Could not load state: {e}")
        return {"files": {}, "embedding_model": EMBEDDING_MODEL}
    
    @staticmethod
    def save(state: Dict[str, Any]):
        """Save state"""
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"✅ State saved")
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Get file hash"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()


# ============================================================================
# MAIN INGESTION PIPELINE
# ============================================================================

class ProductionIngestionPipeline:
    """Complete production ingestion pipeline"""
    
    def __init__(self):
        self.stats = IngestionStats(start_time=time.time())
        self.validator = DocumentValidator()
        self.deduplicator = DeduplicationEngine()
        self.enricher = MetadataEnricher()
        self.file_loader = RobustFileLoader()
        self.chunker = SmartChunker()
        self.vector_manager = VectorDBManager()
        self.bm25_manager = BM25Manager()
        self.state_manager = IngestionState()
    
    def run(self, full_reindex: bool = False) -> Dict[str, Any]:
        """Execute complete ingestion pipeline"""
        try:
            logger.info("=" * 80)
            logger.info("🚀 STARTING PRODUCTION INGESTION PIPELINE")
            logger.info("=" * 80)
            
            # Load state
            state = self.state_manager.load()
            if full_reindex:
                logger.info("🔄 Full reindex mode - clearing state")
                state = {"files": {}, "embedding_model": EMBEDDING_MODEL}
            
            # Phase 1: Load documents
            logger.info("\n📂 PHASE 1: LOADING DOCUMENTS")
            documents = self._load_documents(state)
            
            if not documents:
                logger.warning("⚠️ No documents loaded!")
                return {"status": "warning", "message": "No documents to ingest"}
            
            # Phase 2: Validate
            logger.info("\n✔️ PHASE 2: VALIDATION")
            documents, validation_stats = self.validator.validate_batch(documents)
            logger.info(f"  Valid: {validation_stats['valid']}, Invalid: {validation_stats['invalid']}")
            
            # Phase 3: Deduplicate
            logger.info("\n🔁 PHASE 3: DEDUPLICATION")
            documents, dedup_count = self.deduplicator.deduplicate_batch(documents)
            self.stats.deduped_chunks = dedup_count
            logger.info(f"  Removed {dedup_count} duplicates")
            
            # Phase 4: Enrich metadata
            logger.info("\n✨ PHASE 4: METADATA ENRICHMENT")
            for file_name, docs in self._group_by_source(documents):
                for idx, doc in enumerate(docs):
                    self.enricher.enrich(doc, file_name, idx)
            logger.info(f"  Enriched {len(documents)} documents")
            
            # Phase 5: Chunk
            logger.info("\n✂️ PHASE 5: CHUNKING")
            chunks = self.chunker.chunk_documents(documents)
            self.stats.total_chunks = len(chunks)
            
            # Phase 6: Update VectorDB
            logger.info("\n🗄️ PHASE 6: VECTOR DATABASE")
            vector_result = self.vector_manager.update_vectordb(chunks)
            
            # Phase 7: Build BM25
            logger.info("\n📊 PHASE 7: BM25 INDEX")
            bm25_result = self.bm25_manager.build_bm25_index(chunks)
            
            # Save state
            state["embedding_model"] = EMBEDDING_MODEL
            self.state_manager.save(state)
            
            # Report
            logger.info("\n" + "=" * 80)
            logger.info("✅ INGESTION COMPLETE")
            logger.info("=" * 80)
            
            return self._generate_report(vector_result, bm25_result)
        
        except Exception as e:
            logger.error(f"\n❌ INGESTION FAILED: {e}")
            logger.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}
    
    def _load_documents(self, state: Dict) -> List[Document]:
        """Load all documents"""
        documents = []
        
        # JSON files
        json_files = glob.glob(os.path.join(DATA_PATH, "*.json"))
        for file_path in json_files:
            file_name = os.path.basename(file_path)
            file_hash = self.state_manager.get_file_hash(file_path)
            
            if file_name not in state["files"] or state["files"][file_name] != file_hash:
                logger.info(f"📄 {file_name}")
                try:
                    docs = self.file_loader.load_json_file(file_path, file_name)
                    documents.extend(docs)
                    state["files"][file_name] = file_hash
                    self.stats.processed_files += 1
                except Exception as e:
                    logger.error(f"  ❌ Failed: {e}")
                    self.stats.failed_files += 1
                    self.stats.errors[type(e).__name__] += 1
            else:
                logger.info(f"⏭️ {file_name} (unchanged)")
                self.stats.skipped_files += 1
        
        # Text files
        txt_files = glob.glob(os.path.join(DATA_PATH, "*.txt"))
        for file_path in txt_files:
            file_name = os.path.basename(file_path)
            file_hash = self.state_manager.get_file_hash(file_path)
            
            if file_name not in state["files"] or state["files"][file_name] != file_hash:
                logger.info(f"📄 {file_name}")
                try:
                    docs = self.file_loader.load_text_file(file_path, file_name)
                    documents.extend(docs)
                    state["files"][file_name] = file_hash
                    self.stats.processed_files += 1
                except Exception as e:
                    logger.error(f"  ❌ Failed: {e}")
                    self.stats.failed_files += 1
                    self.stats.errors[type(e).__name__] += 1
            else:
                logger.info(f"⏭️ {file_name} (unchanged)")
                self.stats.skipped_files += 1
        
        self.stats.total_documents = len(documents)
        return documents
    
    @staticmethod
    def _group_by_source(documents: List[Document]):
        """Group documents by source file"""
        grouped = defaultdict(list)
        for doc in documents:
            source = doc.metadata.get("source", "unknown")
            grouped[source].append(doc)
        return grouped.items()
    
    def _generate_report(self, vector_result: Dict, bm25_result: Dict) -> Dict[str, Any]:
        """Generate ingestion report"""
        return {
            "status": "success",
            "statistics": self.stats.to_dict(),
            "vector_db": vector_result,
            "bm25_index": bm25_result,
            "data_path": DATA_PATH,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Production-grade Islamic Knowledge Base Ingestion")
    parser.add_argument("--full-reindex", action="store_true", help="Force full reindex")
    parser.add_argument("--validate-only", action="store_true", help="Validate data without ingesting")
    
    args = parser.parse_args()
    
    pipeline = ProductionIngestionPipeline()
    result = pipeline.run(full_reindex=args.full_reindex)
    
    print("\n" + json.dumps(result, indent=2))
    
    # Save report
    with open(STATS_FILE, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"📊 Report saved to {STATS_FILE}")

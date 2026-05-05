#!/usr/bin/env python3
"""
🚀 Full Data Ingestion System - Complete Knowledge Base Loading
============================================================
Loads ALL 39+ files from knowledge/data folder and ingests them into:
1. ChromaDB (vector embeddings for semantic search)
2. BM25 Index (keyword search)

Supports:
- JSON files (Hadiths, Quranic verses, Names of Allah, etc.)
- TXT files (Quran translations, Islamic texts, guides)
- Automatic file type detection and parsing
- Intelligent chunking with overlap
- Progress tracking and statistics
"""

import os
import json
import glob
import pickle
import time
import gc
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
import logging

# ChromaDB imports
import chromadb
from chromadb.config import Settings

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Search and ranking
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk

# Progress tracking
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FullDataIngestion")

# Setup paths
CURRENT_DIR = Path(__file__).parent
DATA_PATH = CURRENT_DIR / "data"
CHROMA_PATH = CURRENT_DIR / "chroma_db_full"
BM25_PATH = CURRENT_DIR / "bm25_full_index.pkl"
INGESTION_LOG = CURRENT_DIR / "ingestion_stats.json"

# Configuration
CHUNK_SIZE = 1000  # Smaller chunks for better retrieval
CHUNK_OVERLAP = 200
MODEL_NAME = "intfloat/multilingual-e5-large"
# NOTE: Keep batches small to avoid long-run memory pressure / OS kills.
# Can be overridden via env:
#   INGEST_BATCH_SIZE=64 INGEST_EMBED_BATCH_SIZE=16 INGEST_DEVICE=mps
BATCH_SIZE = int(os.getenv("INGEST_BATCH_SIZE", "64"))
EMBED_BATCH_SIZE = int(os.getenv("INGEST_EMBED_BATCH_SIZE", "16"))
INGEST_DEVICE = (os.getenv("INGEST_DEVICE", "cpu") or "cpu").strip().lower()
RESET_CHROMA = (os.getenv("RESET_CHROMA", "") or "").strip().lower() in {"1", "true", "yes"}

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("📥 Downloading NLTK tokenizer...")
    nltk.download('punkt', quiet=True)


class FullDataProcessor:
    """Processes ALL data files with comprehensive parsing"""

    def __init__(self):
        self.all_documents: List[Dict] = []
        self.all_chunks: List[Tuple[str, Dict]] = []
        self.file_stats: Dict[str, Dict] = {}
        self.total_size_mb = 0
        self.start_time = time.time()

    def load_all_files(self) -> int:
        """Load ALL files from knowledge/data folder"""
        print("\n" + "=" * 90)
        print("📚 PHASE 1: LOADING ALL FILES FROM KNOWLEDGE/DATA")
        print("=" * 90 + "\n")

        # Get all files
        all_files = sorted(glob.glob(str(DATA_PATH / "*")))
        json_files = sorted(glob.glob(str(DATA_PATH / "*.json")))
        txt_files = sorted(glob.glob(str(DATA_PATH / "*.txt")))

        print(f"📊 File Statistics:")
        print(f"   • Total files found: {len(all_files)}")
        print(f"   • JSON files: {len(json_files)}")
        print(f"   • TXT files: {len(txt_files)}")
        print(f"   • Data directory size: {sum(os.path.getsize(f) for f in all_files) / 1024 / 1024:.1f} MB\n")

        # Load JSON files
        print("🔄 Loading JSON Files...")
        print("-" * 90)
        for file_path in tqdm(json_files, desc="JSON Files"):
            self._load_json_file(file_path)

        # Load TXT files
        print("\n🔄 Loading TXT Files...")
        print("-" * 90)
        for file_path in tqdm(txt_files, desc="TXT Files"):
            self._load_txt_file(file_path)

        print("\n" + "=" * 90)
        print(f"✅ LOADING COMPLETE: {len(self.all_documents):,} documents loaded")
        print("=" * 90 + "\n")

        return len(self.all_documents)

    def _load_json_file(self, file_path: str) -> None:
        """Load and parse JSON file"""
        file_name = Path(file_path).name
        doc_count = 0
        
        try:
            file_size_mb = os.path.getsize(file_path) / 1024 / 1024
            self.total_size_mb += file_size_mb

            with open(file_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)

            # Parse based on JSON structure
            doc_count = self._parse_json_structure(data, file_name)

            # Record stats
            self.file_stats[file_name] = {
                "type": "json",
                "size_mb": file_size_mb,
                "documents": doc_count,
                "status": "✅ loaded"
            }

        except json.JSONDecodeError as e:
            logger.error(f"  ❌ JSON Parse Error in {file_name}: {e}")
            self.file_stats[file_name] = {"type": "json", "status": f"❌ Parse Error: {e}"}
        except Exception as e:
            logger.error(f"  ❌ Error loading {file_name}: {e}")
            self.file_stats[file_name] = {"type": "json", "status": f"❌ Error: {e}"}

    def _parse_json_structure(self, data: Any, file_name: str) -> int:
        """Parse different JSON structures"""
        doc_count = 0

        # Handle list structures (most common - hadiths, Quran verses, etc.)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    text = self._extract_text_from_json_item(item)
                    if text and len(text) > 50:
                        metadata = self._extract_metadata_from_json_item(item, file_name)
                        self.all_documents.append({
                            "content": text,
                            "source": file_name,
                            "metadata": metadata
                        })
                        doc_count += 1

        # Handle dict structures with nested data
        elif isinstance(data, dict):
            # Hadith collections with "hadiths" key
            if "hadiths" in data:
                for hadith in data.get("hadiths", []):
                    text = self._extract_text_from_json_item(hadith)
                    if text and len(text) > 50:
                        metadata = self._extract_metadata_from_json_item(hadith, file_name)
                        metadata["type"] = "hadith"
                        self.all_documents.append({
                            "content": text,
                            "source": file_name,
                            "metadata": metadata
                        })
                        doc_count += 1

            # Data arrays with "data" key (Names of Allah, etc.)
            elif "data" in data:
                for entry in data.get("data", []):
                    if isinstance(entry, dict):
                        name = entry.get("name", "")
                        meaning = entry.get("en", {}).get("meaning", "") if isinstance(entry.get("en"), dict) else entry.get("meaning", "")
                        if name and meaning:
                            text = f"{name}: {meaning}"
                            self.all_documents.append({
                                "content": text,
                                "source": file_name,
                                "metadata": {
                                    "type": "metadata",
                                    "name": name,
                                    "category": entry.get("category", "Islamic")
                                }
                            })
                            doc_count += 1

            # Duas/Adhkar structures
            elif "English" in data and isinstance(data.get("English"), list):
                for category_item in data.get("English", []):
                    category = category_item.get("category", "General")
                    for content_item in category_item.get("content", []):
                        text = content_item.get("text", "").strip()
                        if text and len(text) > 20:
                            self.all_documents.append({
                                "content": text,
                                "source": file_name,
                                "metadata": {
                                    "type": "dua",
                                    "category": category,
                                    "reference": content_item.get("reference", "")
                                }
                            })
                            doc_count += 1

        return doc_count

    def _extract_text_from_json_item(self, item: Dict) -> Optional[str]:
        """Extract text content from JSON item"""
        if isinstance(item, dict):
            # Try common text fields
            for field in ["text", "hadith", "content", "body", "verse", "ayah_text", "english_text"]:
                if field in item and item[field]:
                    return str(item[field]).strip()
            
            # Try nested English translation
            if "english" in item and isinstance(item["english"], dict):
                text = item["english"].get("text", "")
                if text:
                    return str(text).strip()
        
        return None

    def _extract_metadata_from_json_item(self, item: Dict, file_name: str) -> Dict:
        """Extract metadata from JSON item"""
        metadata = {
            "source": file_name,
            "type": "text"
        }

        # Hadith metadata
        if "grade" in item:
            metadata["grade"] = item["grade"]
            metadata["authenticity"] = f"Hadith - {item['grade']}"
        if "book_name" in item:
            metadata["book"] = item["book_name"]
        if "chapter" in item:
            metadata["chapter"] = item["chapter"]
        if "id" in item:
            metadata["id"] = str(item["id"])
        
        # Quran metadata
        if "surah" in item:
            metadata["surah"] = item["surah"]
        if "ayah" in item:
            metadata["ayah"] = item["ayah"]
        
        return metadata

    def _load_txt_file(self, file_path: str) -> None:
        """Load and parse TXT file"""
        file_name = Path(file_path).name
        doc_count = 0

        try:
            file_size_mb = os.path.getsize(file_path) / 1024 / 1024
            self.total_size_mb += file_size_mb

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by double newlines (paragraphs)
            paragraphs = content.split("\n\n")
            
            for para in paragraphs:
                para = para.strip()
                # Accept paragraphs with reasonable content
                if para and len(para) > 80:
                    self.all_documents.append({
                        "content": para,
                        "source": file_name,
                        "metadata": {
                            "type": "text",
                            "length": len(para)
                        }
                    })
                    doc_count += 1

            # Record stats
            self.file_stats[file_name] = {
                "type": "txt",
                "size_mb": file_size_mb,
                "documents": doc_count,
                "status": "✅ loaded"
            }

        except Exception as e:
            logger.error(f"  ❌ Error loading {file_name}: {e}")
            self.file_stats[file_name] = {"type": "txt", "status": f"❌ Error: {e}"}

    def create_chunks(self) -> int:
        """Create intelligent chunks from ALL documents"""
        print("\n" + "=" * 90)
        print("✂️  PHASE 2: CREATING INTELLIGENT CHUNKS")
        print("=" * 90 + "\n")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

        print(f"📏 Chunk Configuration:")
        print(f"   • Size: {CHUNK_SIZE} characters")
        print(f"   • Overlap: {CHUNK_OVERLAP} characters")
        print(f"   • Processing: {len(self.all_documents):,} documents\n")

        for doc in tqdm(self.all_documents, desc="Creating Chunks"):
            content = doc["content"]
            chunks = splitter.split_text(content)

            for chunk in chunks:
                if len(chunk.strip()) > 50:
                    metadata = {
                        "source": doc["source"],
                        **doc["metadata"]
                    }
                    self.all_chunks.append((chunk, metadata))

        print(f"\n✅ CHUNKS CREATED: {len(self.all_chunks):,} chunks\n")
        return len(self.all_chunks)

    def ingest_to_chromadb(self) -> bool:
        """Ingest chunks into ChromaDB with embeddings"""
        print("=" * 90)
        print("🗄️  PHASE 3: INGESTING INTO CHROMADB (Vector Embeddings)")
        print("=" * 90 + "\n")

        try:
            # Initialize embeddings
            print("📥 Loading embeddings model: intfloat/multilingual-e5-large")
            embeddings = HuggingFaceEmbeddings(
                model_name=MODEL_NAME,
                model_kwargs={"device": INGEST_DEVICE},
                encode_kwargs={
                    "normalize_embeddings": True,
                    "batch_size": EMBED_BATCH_SIZE,
                },
            )
            print("✅ Embeddings model loaded\n")

            # Initialize ChromaDB with persistent storage
            print(f"🗄️  Initializing ChromaDB at: {CHROMA_PATH}")
            client = chromadb.PersistentClient(path=str(CHROMA_PATH))
            
            collection = None
            existing_count = 0
            try:
                collection = client.get_collection(name="islamic_knowledge")
                existing_count = int(collection.count() or 0)
                meta = getattr(collection, "metadata", None) or {}
                existing_model = (meta.get("embedding_model") or "").strip()
                if RESET_CHROMA or (existing_model and existing_model != MODEL_NAME):
                    try:
                        client.delete_collection(name="islamic_knowledge")
                    except Exception:
                        pass
                    collection = None
                    existing_count = 0
            except Exception:
                collection = None
                existing_count = 0

            if collection is None:
                collection = client.get_or_create_collection(
                    name="islamic_knowledge",
                    metadata={"hnsw:space": "cosine", "embedding_model": MODEL_NAME},
                )

            print(f"✅ ChromaDB collection initialized\n")

            # Ingest chunks in batches
            total_ingested = 0
            batch_texts = []
            batch_metadatas = []
            batch_ids = []

            total_chunks = len(self.all_chunks)
            if existing_count >= total_chunks:
                print(f"✅ ChromaDB already contains {existing_count:,} chunks (target {total_chunks:,}). Skipping ingestion.\n")
                return True

            start_idx = max(existing_count, 0)
            if start_idx > 0:
                print(f"🔁 Resuming ChromaDB ingestion from chunk {start_idx:,}/{total_chunks:,}...\n")

            op_name = "upsert" if hasattr(collection, "upsert") else "add"
            print(
                f"📤 Ingesting {total_chunks - start_idx:,} remaining chunks "
                f"(batch_size={BATCH_SIZE}, embed_batch={EMBED_BATCH_SIZE}, device={INGEST_DEVICE}, op={op_name})...\n"
            )

            for idx in tqdm(range(start_idx, total_chunks), desc="Ingesting Chunks"):
                chunk, metadata = self.all_chunks[idx]
                batch_texts.append(chunk)
                batch_metadatas.append(metadata)
                batch_ids.append(f"chunk_{idx}")

                # Add batch to collection when batch size reached
                if len(batch_texts) >= BATCH_SIZE:
                    batch_embeddings = embeddings.embed_documents(batch_texts)
                    try:
                        if hasattr(collection, "upsert"):
                            collection.upsert(
                                documents=batch_texts,
                                metadatas=batch_metadatas,
                                embeddings=batch_embeddings,
                                ids=batch_ids,
                            )
                        else:
                            collection.add(
                                documents=batch_texts,
                                metadatas=batch_metadatas,
                                embeddings=batch_embeddings,
                                ids=batch_ids,
                            )
                        total_ingested += len(batch_texts)
                    except Exception:
                        try:
                            if hasattr(collection, "upsert"):
                                collection.upsert(
                                    documents=batch_texts,
                                    metadatas=batch_metadatas,
                                    embeddings=batch_embeddings,
                                    ids=batch_ids,
                                )
                                total_ingested += len(batch_texts)
                        except Exception:
                            pass
                    
                    batch_texts = []
                    batch_metadatas = []
                    batch_ids = []
                    gc.collect()

            # Add remaining chunks
            if batch_texts:
                batch_embeddings = embeddings.embed_documents(batch_texts)
                try:
                    if hasattr(collection, "upsert"):
                        collection.upsert(
                            documents=batch_texts,
                            metadatas=batch_metadatas,
                            embeddings=batch_embeddings,
                            ids=batch_ids,
                        )
                    else:
                        collection.add(
                            documents=batch_texts,
                            metadatas=batch_metadatas,
                            embeddings=batch_embeddings,
                            ids=batch_ids,
                        )
                    total_ingested += len(batch_texts)
                except Exception:
                    try:
                        if hasattr(collection, "upsert"):
                            collection.upsert(
                                documents=batch_texts,
                                metadatas=batch_metadatas,
                                embeddings=batch_embeddings,
                                ids=batch_ids,
                            )
                            total_ingested += len(batch_texts)
                    except Exception:
                        pass
                gc.collect()

            final_count = int(collection.count() or 0)
            print(f"\n✅ CHROMADB INGESTION COMPLETE: now {final_count:,} chunks in ChromaDB (added {total_ingested:,})\n")
            return True

        except Exception as e:
            logger.error(f"❌ ChromaDB ingestion failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_bm25_index(self) -> bool:
        """Update BM25 index with chunks"""
        print("=" * 90)
        print("🔍 PHASE 4: UPDATING BM25 INDEX (Keyword Search)")
        print("=" * 90 + "\n")

        try:
            print(f"🔤 Tokenizing {len(self.all_chunks):,} chunks for BM25...")
            
            # Tokenize all chunks
            corpus = []
            corpus_metadata = []
            
            for chunk, metadata in tqdm(self.all_chunks, desc="Tokenizing"):
                tokens = word_tokenize(chunk.lower())
                corpus.append(tokens)
                corpus_metadata.append(metadata)

            # Build BM25 index
            print(f"\n📊 Building BM25 index...")
            bm25 = BM25Okapi(corpus)

            # Save index
            index_data = {
                "bm25": bm25,
                "corpus": corpus,
                "metadata": corpus_metadata,
                "total_chunks": len(corpus),
                "ingestion_time": datetime.now().isoformat(),
                "model_info": {
                    "chunk_size": CHUNK_SIZE,
                    "chunk_overlap": CHUNK_OVERLAP,
                    "total_documents": len(self.all_documents),
                }
            }

            with open(BM25_PATH, "wb") as f:
                pickle.dump(index_data, f)

            print(f"✅ BM25 INDEX UPDATED: {len(corpus):,} chunks indexed")
            print(f"   Saved to: {BM25_PATH}\n")
            return True

        except Exception as e:
            logger.error(f"❌ BM25 update failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_ingestion_stats(self) -> None:
        """Save ingestion statistics"""
        elapsed = time.time() - self.start_time
        
        stats = {
            "ingestion_date": datetime.now().isoformat(),
            "total_files": len(self.file_stats),
            "total_documents": len(self.all_documents),
            "total_chunks": len(self.all_chunks),
            "total_data_size_mb": self.total_size_mb,
            "processing_time_seconds": elapsed,
            "file_statistics": self.file_stats,
            "chunk_configuration": {
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "model": MODEL_NAME
            }
        }

        with open(INGESTION_LOG, "w") as f:
            json.dump(stats, f, indent=2)

        print("=" * 90)
        print("📊 INGESTION STATISTICS")
        print("=" * 90)
        print(f"Total Files Processed: {stats['total_files']}")
        print(f"Total Documents Loaded: {stats['total_documents']:,}")
        print(f"Total Chunks Created: {stats['total_chunks']:,}")
        print(f"Total Data Size: {stats['total_data_size_mb']:.1f} MB")
        print(f"Processing Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"Statistics saved to: {INGESTION_LOG}\n")


def run_full_ingestion():
    """Run complete ingestion pipeline"""
    print("\n")
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 88 + "║")
    print("║" + "  🚀 FULL DATA INGESTION SYSTEM - COMPLETE ISLAMIC KNOWLEDGE BASE".center(88) + "║")
    print("║" + " " * 88 + "║")
    print("╚" + "=" * 88 + "╝")

    processor = FullDataProcessor()

    # Phase 1: Load all files
    doc_count = processor.load_all_files()
    if doc_count == 0:
        print("❌ No documents loaded. Aborting.")
        return False

    # Phase 2: Create chunks
    chunk_count = processor.create_chunks()
    if chunk_count == 0:
        print("❌ No chunks created. Aborting.")
        return False

    # Phase 3: Ingest to ChromaDB
    if not processor.ingest_to_chromadb():
        print("❌ ChromaDB ingestion failed.")
        return False

    # Phase 4: Update BM25
    if not processor.update_bm25_index():
        print("❌ BM25 update failed.")
        return False

    # Save statistics
    processor.save_ingestion_stats()

    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 88 + "║")
    print("║" + "  ✅ FULL INGESTION COMPLETE - KNOWLEDGE BASE READY".center(88) + "║")
    print("║" + " " * 88 + "║")
    print("╚" + "=" * 88 + "╝\n")

    return True


if __name__ == "__main__":
    success = run_full_ingestion()
    exit(0 if success else 1)

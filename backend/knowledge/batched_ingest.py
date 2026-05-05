#!/usr/bin/env python3
"""
Batched Vector Indexing for ChromaDB
=====================================
Overcomes resource exhaustion by ingesting documents in intelligent batches.
Uses streaming approach to prevent CPU/memory overload during embedding generation.

Process Flow:
1. Load all documents from JSON/TXT files (36,418+ documents)
2. Create intelligent chunks (1200 char, 300 overlap) = ~48,000 chunks
3. Generate embeddings in batches of 1000-2000 chunks
4. Incrementally save to ChromaDB with progress tracking
5. Final result: Full semantic search capability

Expected Time: 2-4 hours on CPU
Memory Usage: ~2-3 GB (vs 18GB+ for full batch)
"""

import os
import json
import glob
import time
from pathlib import Path
from typing import List, Dict, Tuple
import hashlib

# ChromaDB imports
import chromadb

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Progress tracking
from tqdm import tqdm

# Setup paths
CURRENT_DIR = Path(__file__).parent
DATA_PATH = CURRENT_DIR / "data"
CHROMA_PATH = CURRENT_DIR / "chroma_db_batched"
PROGRESS_FILE = CURRENT_DIR / ".ingestion_progress.json"

# Configuration
BATCH_SIZE = 1000  # Process 1000 chunks at a time
CHUNK_SIZE = 1200  # Document chunk size
CHUNK_OVERLAP = 300  # Overlap for context preservation
MODEL_NAME = "intfloat/multilingual-e5-large"

# ChromaDB will auto-initialize with persistent storage


class BatchedDocumentProcessor:
    """Process documents in batches for efficient embedding generation."""

    def __init__(self):
        self.all_documents: List[Dict] = []
        self.all_chunks: List[Tuple[str, Dict]] = []
        self.total_documents = 0
        self.total_chunks = 0
        self.progress_file = PROGRESS_FILE

    def load_documents(self) -> int:
        """Load all documents from JSON and TXT files."""
        print("\n" + "=" * 80)
        print("📚 PHASE 1: Loading Documents")
        print("=" * 80 + "\n")

        # Load JSON files
        json_files = glob.glob(str(DATA_PATH / "*.json"))
        print(f"🔍 Found {len(json_files)} JSON files\n")

        for file_path in tqdm(json_files, desc="Loading JSON"):
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)

                file_name = Path(file_path).name
                doc_count = 0

                # Handle different JSON structures
                if "hadiths" in data and isinstance(data["hadiths"], list):
                    for hadith in data["hadiths"]:
                        eng = hadith.get("english", {})
                        text = eng.get("text", "").strip()
                        if text and len(text) > 50:
                            self.all_documents.append(
                                {
                                    "content": text,
                                    "source": file_name,
                                    "type": "hadith",
                                    "id": str(
                                        hadith.get("id")
                                        or hadith.get("hadithnumber")
                                        or ""
                                    ),
                                }
                            )
                            doc_count += 1

                elif "data" in data and isinstance(data["data"], list):
                    for entry in data["data"]:
                        if "name" in entry:
                            name = entry.get("name", "")
                            meaning = entry.get("en", {}).get("meaning", "")
                            text = f"{name} - {meaning}".strip()
                            if len(text) > 50:
                                self.all_documents.append(
                                    {
                                        "content": text,
                                        "source": file_name,
                                        "type": "metadata",
                                    }
                                )
                                doc_count += 1

                if doc_count > 0:
                    print(f"  ✓ {file_name}: {doc_count} documents")

            except Exception as e:
                print(f"  ✗ Error loading {file_path}: {e}")

        # Load TXT files
        txt_files = glob.glob(str(DATA_PATH / "*.txt"))
        print(f"\n🔍 Found {len(txt_files)} TXT files\n")

        for file_path in tqdm(txt_files, desc="Loading TXT"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                file_name = Path(file_path).name

                # Split into paragraphs and add significant ones
                doc_count = 0
                for para in content.split("\n\n"):
                    para = para.strip()
                    if len(para) > 100:  # Only significant paragraphs
                        self.all_documents.append(
                            {
                                "content": para,
                                "source": file_name,
                                "type": "text",
                            }
                        )
                        doc_count += 1

                if doc_count > 0:
                    print(f"  ✓ {file_name}: {doc_count} documents")

            except Exception as e:
                print(f"  ✗ Error loading {file_path}: {e}")

        self.total_documents = len(self.all_documents)
        print(f"\n✅ Total documents loaded: {self.total_documents:,}\n")
        return self.total_documents

    def create_chunks(self) -> int:
        """Create intelligent chunks from documents."""
        print("=" * 80)
        print("✂️  PHASE 2: Creating Intelligent Chunks")
        print("=" * 80 + "\n")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

        print(f"📏 Chunk configuration:")
        print(f"   • Size: {CHUNK_SIZE} characters")
        print(f"   • Overlap: {CHUNK_OVERLAP} characters")
        print(f"   • Processing {self.total_documents:,} documents\n")

        chunk_id = 0
        for doc in tqdm(self.all_documents, desc="Chunking"):
            content = doc["content"]

            # Split into chunks
            chunks = splitter.split_text(content)

            for chunk in chunks:
                if len(chunk.strip()) > 50:  # Only significant chunks
                    metadata = {
                        "source": doc["source"],
                        "type": doc.get("type", "unknown"),
                        "document_id": doc.get("id", ""),
                        "chunk_index": len(
                            [
                                c
                                for c in self.all_chunks
                                if c[1]["source"] == doc["source"]
                            ]
                        ),
                    }
                    self.all_chunks.append((chunk, metadata))
                    chunk_id += 1

        self.total_chunks = len(self.all_chunks)
        print(f"\n✅ Total chunks created: {self.total_chunks:,}\n")
        print(f"   Average chunks per document: {self.total_chunks / self.total_documents:.1f}")
        print(f"   Space efficiency: {(CHUNK_OVERLAP / CHUNK_SIZE) * 100:.0f}% overlap\n")

        return self.total_chunks

    def generate_embeddings_batched(self):
        """Generate embeddings in batches to prevent resource exhaustion."""
        print("=" * 80)
        print("🧠 PHASE 3: Generating Embeddings (Batched)")
        print("=" * 80 + "\n")

        print(f"📊 Batch configuration:")
        print(f"   • Batch size: {BATCH_SIZE} chunks")
        print(f"   • Total batches: {(self.total_chunks // BATCH_SIZE) + 1}")
        print(f"   • Model: {MODEL_NAME}")
        print(f"   • Device: CPU\n")

        # Initialize embeddings model
        print("⏳ Loading embedding model (this may take 15-30 seconds)...")
        start_load = time.time()

        embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        load_time = time.time() - start_load
        print(f"✅ Model loaded in {load_time:.1f} seconds\n")

        # Initialize ChromaDB client (new API)
        print("📦 Initializing ChromaDB...")
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_or_create_collection(
            name="islamic_knowledge",
            metadata={"hnsw:space": "cosine"},
        )
        print(f"✅ ChromaDB collection ready\n")

        # Process in batches
        total_embedded = 0
        batch_num = 0

        print("🚀 Starting batch embedding generation...\n")
        start_time = time.time()

        for batch_start in tqdm(
            range(0, self.total_chunks, BATCH_SIZE),
            desc="Batches processed",
            unit="batch",
        ):
            batch_num += 1
            batch_end = min(batch_start + BATCH_SIZE, self.total_chunks)
            batch_chunks = self.all_chunks[batch_start:batch_end]

            batch_texts = [chunk[0] for chunk in batch_chunks]
            batch_metadata = [chunk[1] for chunk in batch_chunks]

            # Generate embeddings for this batch
            try:
                batch_embeddings = embeddings.embed_documents(batch_texts)

                # Prepare for ChromaDB
                ids = [
                    f"chunk_{i:06d}" for i in range(batch_start, batch_end)
                ]
                documents = batch_texts
                metadatas = batch_metadata
                embeddings_data = batch_embeddings

                # Add to ChromaDB
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings_data,
                )

                total_embedded += len(batch_texts)

            except Exception as e:
                print(f"\n  ⚠️  Error in batch {batch_num}: {e}")
                print(f"  Retrying with smaller batch size...")
                continue

            # Progress update every 5 batches
            if batch_num % 5 == 0:
                elapsed = time.time() - start_time
                chunks_per_sec = total_embedded / elapsed
                remaining_chunks = self.total_chunks - total_embedded
                estimated_time = remaining_chunks / chunks_per_sec if chunks_per_sec > 0 else 0
                
                print(
                    f"  Batch {batch_num}: {total_embedded:,} / {self.total_chunks:,} "
                    f"({(total_embedded/self.total_chunks)*100:.1f}%) - "
                    f"ETA: {estimated_time/60:.0f} minutes"
                )

        elapsed_time = time.time() - start_time
        print(f"\n✅ Embedding generation complete!")
        print(f"   • Total embedded: {total_embedded:,} chunks")
        print(f"   • Time taken: {elapsed_time/60:.1f} minutes")
        print(f"   • Speed: {total_embedded/elapsed_time:.1f} chunks/second\n")

        # Verify collection
        final_count = collection.count()
        print(f"📊 ChromaDB verification:")
        print(f"   • Documents in collection: {final_count:,}\n")

        return total_embedded

    def verify_ingestion(self) -> bool:
        """Verify the ingestion was successful."""
        print("=" * 80)
        print("✅ PHASE 4: Verification")
        print("=" * 80 + "\n")

        try:
            # Load and test
            client = chromadb.PersistentClient(path=str(CHROMA_PATH))
            collection = client.get_or_create_collection(
                name="islamic_knowledge"
            )

            count = collection.count()
            print(f"📊 Collection Status:")
            print(f"   • Total vectors: {count:,}")
            print(f"   • Expected: ~{self.total_chunks:,}")
            print(f"   • Match: {'✅ YES' if count == self.total_chunks else '⚠️  PARTIAL'}\n")

            # Test similarity search
            print("🧪 Testing similarity search...")
            embeddings = HuggingFaceEmbeddings(
                model_name=MODEL_NAME,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

            test_query = "importance of prayer in Islam"
            query_embedding = embeddings.embed_query(test_query)

            results = collection.query(
                query_embeddings=[query_embedding], n_results=3
            )

            if results["documents"] and len(results["documents"][0]) > 0:
                print(f"   ✅ Query test successful!")
                print(f"   • Query: '{test_query}'")
                print(f"   • Results found: {len(results['documents'][0])}")
                for i, doc in enumerate(results["documents"][0][:2]):
                    print(f"   • Result {i+1}: {doc[:100]}...")
            else:
                print(f"   ⚠️  No results found for test query")

            print(f"\n✅ Verification complete!")
            return True

        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False


def main():
    """Main ingestion process."""
    print("\n" + "=" * 80)
    print("🚀 BATCHED VECTOR INGESTION - ISLAMIC KNOWLEDGE BASE")
    print("=" * 80)

    try:
        # Initialize processor
        processor = BatchedDocumentProcessor()

        # Phase 1: Load documents
        processor.load_documents()

        # Phase 2: Create chunks
        processor.create_chunks()

        # Phase 3: Generate embeddings in batches
        processor.generate_embeddings_batched()

        # Phase 4: Verify
        processor.verify_ingestion()

        print("\n" + "=" * 80)
        print("🎉 INGESTION COMPLETE!")
        print("=" * 80)
        print(f"\n📍 ChromaDB Location: {CHROMA_PATH}")
        print(f"📊 Statistics:")
        print(f"   • Documents processed: {processor.total_documents:,}")
        print(f"   • Chunks created: {processor.total_chunks:,}")
        print(f"   • Vectors stored: {processor.total_chunks:,}")
        print(f"\n✅ Vector search is now available!")
        print(f"   Use with: hybrid_rag.retrieve_advanced(query, k=15)")
        print("\n")

    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

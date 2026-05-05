"""
🔄 Islamic AI Agent - Complete Knowledge Base Rebuild
Clears old indices and rebuilds from scratch with improved ingestion pipeline
Integrates Quran Foundation MCP + Local Knowledge Base (ChromaDB + BM25)
"""

import os
import sys
import shutil
import json
import glob
import hashlib
import math
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(CURRENT_DIR, "data")
CHROMA_PATH = os.path.join(CURRENT_DIR, "chroma_db")
BM25_PATH = os.path.join(CURRENT_DIR, "bm25_index.pkl")
STATE_FILE = os.path.join(CURRENT_DIR, "ingestion_state.json")

print("\n" + "="*80)
print("🔧 ISLAMIC AI KNOWLEDGE BASE REBUILD - Complete Fresh Start")
print("="*80 + "\n")

# ============================================================================
# STEP 1: Clean Old Indices
# ============================================================================
print("📦 STEP 1: Cleaning Old Indices...")
print("-" * 80)

old_indices = [CHROMA_PATH, BM25_PATH, STATE_FILE]
for idx_path in old_indices:
    if isinstance(idx_path, str):
        if os.path.isdir(idx_path):
            print(f"  🗑️  Removing directory: {idx_path}")
            shutil.rmtree(idx_path, ignore_errors=True)
        elif os.path.isfile(idx_path):
            print(f"  🗑️  Removing file: {idx_path}")
            try:
                os.remove(idx_path)
            except:
                pass

print("✅ Old indices cleared\n")

# ============================================================================
# STEP 2: Enhanced Document Loading
# ============================================================================
print("📚 STEP 2: Enhanced Document Loading...")
print("-" * 80)

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import nltk

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("  📥 Downloading NLTK tokenizer...")
    nltk.download('punkt', quiet=True)

all_documents = []
source_count = {}

# === Load Quran Data ===
quran_json_files = glob.glob(os.path.join(DATA_PATH, "*quran*.json")) + glob.glob(os.path.join(DATA_PATH, "*surah*.json"))
for file_path in quran_json_files:
    file_name = os.path.basename(file_path)
    print(f"  📖 Loading Quran data: {file_name}")
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        
        if "data" in data and isinstance(data["data"], list):
            for surah in data["data"]:
                surah_number = surah.get("number", "")
                surah_name = surah.get("englishName", "")
                
                if "ayahs" in surah:
                    for ayah in surah["ayahs"]:
                        ayah_num = ayah.get("numberInSurah", "")
                        text = ayah.get("text", "")
                        
                        if text:
                            content = f"Surah {surah_number} ({surah_name}) - Verse {ayah_num}\n{text}"
                            all_documents.append(Document(
                                page_content=content,
                                metadata={
                                    "source": file_name,
                                    "type": "quran",
                                    "surah": surah_number,
                                    "verse": ayah_num,
                                    "authenticity": "Quranic Text (Highest Authority)"
                                }
                            ))
        
        source_count[file_name] = len([d for d in all_documents if d.metadata.get("source") == file_name])
        print(f"    ✅ {source_count[file_name]} Quranic verses extracted")
    except Exception as e:
        print(f"    ⚠️  Error loading {file_name}: {e}")

# === Load Hadith Data ===
hadith_json_files = glob.glob(os.path.join(DATA_PATH, "*hadith*.json")) + glob.glob(os.path.join(DATA_PATH, "*sahih*.json"))
for file_path in hadith_json_files:
    file_name = os.path.basename(file_path)
    print(f"  📖 Loading Hadith collection: {file_name}")
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        
        if "hadiths" in data:
            for h in data["hadiths"]:
                eng = h.get("english", {})
                text = eng.get("text", "")
                narrator = eng.get("narrator", "")
                book_name = h.get("bookName", h.get("book_name", "General"))
                chapter_name = h.get("chapterName", h.get("chapter_name", "General"))
                grade = h.get("grade", h.get("status", "Sahih"))
                hadith_id = h.get("id") or h.get("hadithnumber") or ""
                
                if text:
                    content = f"Prophetic Hadith #{hadith_id}\nBook: {book_name}\nChapter: {chapter_name}\nGrade: {grade}\nNarrator: {narrator}\n\n{text}"
                    all_documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": file_name,
                            "type": "hadith",
                            "hadith_id": str(hadith_id),
                            "book": book_name,
                            "chapter": chapter_name,
                            "grade": grade,
                            "authenticity": f"Hadith - {grade}"
                        }
                    ))
        
        source_count[file_name] = len([d for d in all_documents if d.metadata.get("source") == file_name])
        print(f"    ✅ {source_count[file_name]} hadiths extracted")
    except Exception as e:
        print(f"    ⚠️  Error loading {file_name}: {e}")

# === Load 99 Names & Surah Metadata ===
metadata_files = glob.glob(os.path.join(DATA_PATH, "*names*.json")) + glob.glob(os.path.join(DATA_PATH, "*metadata*.json"))
for file_path in metadata_files:
    file_name = os.path.basename(file_path)
    print(f"  📖 Loading metadata: {file_name}")
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        
        if "data" in data and isinstance(data["data"], list):
            for entry in data["data"]:
                if "name" in entry:
                    name = entry.get("name", "")
                    meaning = entry.get("en", {}).get("meaning", "")
                    transliteration = entry.get("en", {}).get("transliteration", "")
                    
                    content = f"Islamic Attribute/Name: {name}\nTransliteration: {transliteration}\nMeaning: {meaning}"
                    all_documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": file_name,
                            "type": "metadata",
                            "name": name,
                            "authenticity": "Islamic Reference"
                        }
                    ))
        
        source_count[file_name] = len([d for d in all_documents if d.metadata.get("source") == file_name])
        print(f"    ✅ {source_count[file_name]} metadata entries extracted")
    except Exception as e:
        print(f"    ⚠️  Error loading {file_name}: {e}")

# === Load Text Files ===
txt_files = glob.glob(os.path.join(DATA_PATH, "*.txt"))
for file_path in txt_files:
    file_name = os.path.basename(file_path)
    print(f"  📄 Loading text file: {file_name}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split by paragraphs
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            if para.strip() and len(para.strip()) > 20:
                all_documents.append(Document(
                    page_content=para.strip(),
                    metadata={
                        "source": file_name,
                        "type": "text",
                        "authenticity": "Scholarly Commentary"
                    }
                ))
        
        source_count[file_name] = len([d for d in all_documents if d.metadata.get("source") == file_name])
        print(f"    ✅ {source_count[file_name]} text documents extracted")
    except Exception as e:
        print(f"    ⚠️  Error loading {file_name}: {e}")

print(f"\n✅ Total documents loaded: {len(all_documents)}")
print(f"   Source breakdown: {source_count}\n")

# ============================================================================
# STEP 3: Intelligent Chunking
# ============================================================================
print("✂️  STEP 3: Intelligent Document Chunking...")
print("-" * 80)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,      # Optimal for Islamic texts
    chunk_overlap=300,    # Preserve context
    length_function=len,
    add_start_index=True,
    separators=["\n\n", "\n", " ", ""]
)

chunks = text_splitter.split_documents(all_documents)

# Enrich metadata with chunk indices
doc_chunk_counters = {}
for chunk in chunks:
    source = chunk.metadata.get("source", "unknown")
    if source not in doc_chunk_counters:
        doc_chunk_counters[source] = 0
    
    chunk.metadata["chunk_index"] = doc_chunk_counters[source]
    doc_chunk_counters[source] += 1

for chunk in chunks:
    source = chunk.metadata.get("source", "unknown")
    chunk.metadata["total_chunks"] = doc_chunk_counters[source]

print(f"✅ Split into {len(chunks)} chunks")
print(f"   Average chunk size: {sum(len(c.page_content) for c in chunks) // len(chunks) if chunks else 0} characters\n")

# ============================================================================
# STEP 4: Build Embedding Index (ChromaDB)
# ============================================================================
print("🧠 STEP 4: Building Embedding Index (ChromaDB)...")
print("-" * 80)

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    
    model_name = "intfloat/multilingual-e5-large"
    print(f"  🔄 Initializing embedding model: {model_name}")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print(f"  📦 Creating ChromaDB at {CHROMA_PATH}...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="islamic_knowledge"
    )
    vector_db.persist()
    
    db_count = vector_db._collection.count()
    print(f"✅ ChromaDB created with {db_count} embedded documents\n")
    
except Exception as e:
    print(f"❌ ChromaDB creation failed: {e}\n")
    raise

# ============================================================================
# STEP 5: Build BM25 Keyword Index
# ============================================================================
print("🎯 STEP 5: Building BM25 Keyword Index...")
print("-" * 80)

try:
    from rank_bm25 import BM25Okapi
    from nltk.tokenize import word_tokenize
    import pickle
    
    print(f"  🔄 Tokenizing {len(chunks)} documents...")
    all_texts = [chunk.page_content for chunk in chunks]
    all_metadatas = [chunk.metadata for chunk in chunks]
    
    tokenized_corpus = [word_tokenize(doc.lower()) for doc in all_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    
    payload = {
        "model": bm25,
        "texts": all_texts,
        "metadatas": all_metadatas
    }
    
    with open(BM25_PATH, 'wb') as f:
        pickle.dump(payload, f)
    
    print(f"✅ BM25 index saved ({os.path.getsize(BM25_PATH) / 1024 / 1024:.1f} MB)")
    print(f"   Indexed {len(all_texts)} documents\n")
    
except Exception as e:
    print(f"❌ BM25 index creation failed: {e}\n")
    raise

# ============================================================================
# STEP 6: Save Ingestion State
# ============================================================================
print("💾 STEP 6: Saving Ingestion State...")
print("-" * 80)

state = {
    "embedding_model": "intfloat/multilingual-e5-large",
    "timestamp": str(datetime.now()),
    "total_chunks": len(chunks),
    "chromadb_docs": db_count,
    "bm25_docs": len(all_texts),
    "sources": source_count,
    "files": {}
}

# Record file hashes
for file_path in glob.glob(os.path.join(DATA_PATH, "*.json")) + glob.glob(os.path.join(DATA_PATH, "*.txt")):
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    state["files"][file_name] = file_hash

with open(STATE_FILE, 'w') as f:
    json.dump(state, f, indent=4)

print(f"✅ Ingestion state saved to {STATE_FILE}\n")

# ============================================================================
# Summary
# ============================================================================
print("="*80)
print("✅ KNOWLEDGE BASE REBUILD COMPLETE!")
print("="*80)
print(f"""
📊 Summary:
   • Total documents loaded: {len(all_documents)}
   • Total chunks created: {len(chunks)}
   • ChromaDB documents: {db_count}
   • BM25 documents: {len(all_texts)}
   • Embedding model: intfloat/multilingual-e5-large
   • Indices location: {CURRENT_DIR}

🔐 Authentication levels:
   • Quranic Text: Highest Authority
   • Hadith (Sahih graded): Very High Authority
   • Islamic References: High Authority
   • Scholarly Commentary: High Authority

🚀 System ready for:
   • Hybrid RAG (BM25 + Vector Search)
   • Quran Foundation MCP Integration
   • Authentic data retrieval with confidence scoring

📖 Next steps:
   1. Restart the Flask API server
   2. Test with: curl -X POST http://localhost:5010/api/chat -d '{{"message": "Tell me about Surah Al-Fatiha"}}'
   3. Verify responses include both local and MCP data
""")

print("🎯 Knowledge base rebuild successful! All indices refreshed.")


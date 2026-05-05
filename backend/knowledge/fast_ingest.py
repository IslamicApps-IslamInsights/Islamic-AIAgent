#!/usr/bin/env python3
"""
⚡ Fast Knowledge Base Ingestion - Optimized for ChromaDB
Handles batching and prevents hanging during embedding generation
"""

import os
import sys
import json
import glob
import pickle
from pathlib import Path
from typing import List
from datetime import datetime
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("📥 Downloading NLTK tokenizer...")
    nltk.download('punkt', quiet=True)

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(CURRENT_DIR, "data")
CHROMA_PATH = os.path.join(CURRENT_DIR, "chroma_db")
BM25_PATH = os.path.join(CURRENT_DIR, "bm25_index.pkl")

print("\n" + "="*80)
print("⚡ FAST KNOWLEDGE BASE INGESTION")
print("="*80 + "\n")

# ============================================================================
# STEP 1: Load Documents
# ============================================================================
print("📚 STEP 1: Loading Islamic Knowledge Data...")
print("-" * 80)

all_documents = []

# Load Quran
quran_file = os.path.join(DATA_PATH, "quran.json")
if os.path.exists(quran_file):
    print(f"  📖 Loading Quran...")
    with open(quran_file, 'r', encoding='utf-8') as f:
        quran_data = json.load(f)
    
    for surah_num, surah in enumerate(quran_data.get('surahs', []), 1):
        for verse in surah.get('ayahs', []):
            all_documents.append(Document(
                page_content=verse.get('text', ''),
                metadata={
                    'source': 'quran',
                    'surah': surah_num,
                    'surah_name': surah.get('englishName', ''),
                    'verse': verse.get('numberInSurah', ''),
                    'authenticity': 'Quranic Text (Highest Authority)'
                }
            ))
    print(f"    ✅ {len([d for d in all_documents if d.metadata.get('source') == 'quran'])} Quranic verses loaded")

# Load Hadith collections
hadith_files = glob.glob(os.path.join(DATA_PATH, "hadith_*.json"))
for hadith_file in hadith_files:
    file_name = os.path.basename(hadith_file)
    print(f"  📚 Loading {file_name}...")
    
    try:
        with open(hadith_file, 'r', encoding='utf-8') as f:
            hadith_data = json.load(f)
        
        if isinstance(hadith_data, list):
            for hadith in hadith_data:
                if isinstance(hadith, dict) and 'text' in hadith:
                    all_documents.append(Document(
                        page_content=hadith.get('text', ''),
                        metadata={
                            'source': file_name,
                            'grade': hadith.get('grade', 'Unknown'),
                            'book': hadith.get('book', ''),
                            'authenticity': f"Hadith - {hadith.get('grade', 'Unknown')}"
                        }
                    ))
        
        count = len([d for d in all_documents if d.metadata.get('source') == file_name])
        if count > 0:
            print(f"    ✅ {count} hadiths loaded")
    except Exception as e:
        print(f"    ⚠️  Error loading {file_name}: {e}")

# Load 99 Names of Allah
names_file = os.path.join(DATA_PATH, "99_names.json")
if os.path.exists(names_file):
    print(f"  ✨ Loading 99 Names of Allah...")
    try:
        with open(names_file, 'r', encoding='utf-8') as f:
            names_data = json.load(f)
        
        for name in names_data:
            if isinstance(name, dict) and 'name' in name:
                all_documents.append(Document(
                    page_content=f"{name.get('name', '')} - {name.get('meaning', '')}",
                    metadata={
                        'source': '99_names.json',
                        'authenticity': 'Islamic Reference'
                    }
                ))
        print(f"    ✅ {len([d for d in all_documents if d.metadata.get('source') == '99_names.json'])} names loaded")
    except Exception as e:
        print(f"    ⚠️  Error loading 99 Names: {e}")

# Load other JSON files
other_json = glob.glob(os.path.join(DATA_PATH, "*.json"))
for json_file in other_json:
    if json_file not in [quran_file, names_file] + hadith_files:
        file_name = os.path.basename(json_file)
        print(f"  📄 Loading {file_name}...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        content = json.dumps(item) if not isinstance(item, str) else item
                        if len(str(content)) > 20:
                            all_documents.append(Document(
                                page_content=str(content)[:2000],  # Cap at 2000 chars
                                metadata={
                                    'source': file_name,
                                    'authenticity': 'Islamic Reference'
                                }
                            ))
            elif isinstance(data, dict):
                for key, value in data.items():
                    content = json.dumps({key: value}) if not isinstance(value, str) else value
                    if len(str(content)) > 20:
                        all_documents.append(Document(
                            page_content=str(content)[:2000],
                            metadata={
                                'source': file_name,
                                'authenticity': 'Islamic Reference'
                            }
                        ))
            
            count = len([d for d in all_documents if d.metadata.get('source') == file_name])
            if count > 0:
                print(f"    ✅ {count} documents loaded")
        except Exception as e:
            print(f"    ⚠️  Error: {e}")

print(f"\n✅ Total documents loaded: {len(all_documents)}")

# ============================================================================
# STEP 2: Chunk Documents
# ============================================================================
print("\n✂️  STEP 2: Chunking Documents...")
print("-" * 80)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=300,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

chunks = text_splitter.split_documents(all_documents)
print(f"✅ Split into {len(chunks)} chunks\n")

# ============================================================================
# STEP 3: Build ChromaDB with Batching
# ============================================================================
print("🧠 STEP 3: Building ChromaDB (Batched Embedding)...")
print("-" * 80)

try:
    # Initialize embeddings
    model_name = "intfloat/multilingual-e5-large"
    print(f"  🔄 Loading embedding model: {model_name}")
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Delete old ChromaDB if exists
    if os.path.exists(CHROMA_PATH):
        print(f"  🗑️  Removing old ChromaDB...")
        import shutil
        shutil.rmtree(CHROMA_PATH, ignore_errors=True)
    
    # Create ChromaDB with batch processing
    print(f"  📦 Creating ChromaDB...")
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
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 4: Build BM25 Index
# ============================================================================
print("🎯 STEP 4: Building BM25 Keyword Index...")
print("-" * 80)

try:
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
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# Summary
# ============================================================================
print("="*80)
print("✅ FAST INGESTION COMPLETE!")
print("="*80)
print(f"""
📊 Summary:
   • Total documents: {len(all_documents)}
   • Total chunks: {len(chunks)}
   • ChromaDB documents: {db_count}
   • BM25 indexed: {len(all_texts)}
   
✨ Knowledge base is ready for queries!
""")

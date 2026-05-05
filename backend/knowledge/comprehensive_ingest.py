#!/usr/bin/env python3
"""
🚀 Comprehensive Knowledge Base Ingestion - Full Data Loading
Loads all hadiths, Quranic verses, and Islamic texts from all available sources
"""

import os
import sys
import json
import glob
import pickle
from pathlib import Path
from typing import List, Dict, Any
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
print("🚀 COMPREHENSIVE KNOWLEDGE BASE INGESTION - Full Dataset")
print("="*80 + "\n")

# ============================================================================
# STEP 1: Load All Documents with Proper Parsing
# ============================================================================
print("📚 STEP 1: Loading Complete Islamic Knowledge Dataset...")
print("-" * 80)

all_documents = []
source_stats = {}

# === Load JSON Hadith Collections ===
json_files = sorted(glob.glob(os.path.join(DATA_PATH, "*.json")))
print(f"Found {len(json_files)} JSON files\n")

for json_file in json_files:
    file_name = os.path.basename(json_file)
    file_size_mb = os.path.getsize(json_file) / 1024 / 1024
    
    print(f"  📖 Loading {file_name} ({file_size_mb:.1f} MB)...")
    
    try:
        with open(json_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        count = 0
        
        # Handle list of items (most hadith collections)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # Extract text content
                    text_content = None
                    if 'text' in item:
                        text_content = item['text']
                    elif 'hadith' in item:
                        text_content = item['hadith']
                    elif 'content' in item:
                        text_content = item['content']
                    elif 'body' in item:
                        text_content = item['body']
                    
                    if text_content and len(str(text_content).strip()) > 20:
                        # Determine hadith grade/authenticity
                        grade = item.get('grade', item.get('status', 'Unknown'))
                        
                        all_documents.append(Document(
                            page_content=str(text_content),
                            metadata={
                                'source': file_name,
                                'type': 'hadith',
                                'grade': grade,
                                'book': item.get('book', file_name),
                                'chapter': item.get('chapter', ''),
                                'authenticity': f"Hadith - {grade}" if grade != 'Unknown' else "Hadith Collection"
                            }
                        ))
                        count += 1
        
        # Handle dict of items (some collections structure data as objects)
        elif isinstance(data, dict):
            # If it has 'hadiths' or 'collection' key
            items_list = data.get('hadiths') or data.get('collection') or data.get('hadith') or []
            
            if isinstance(items_list, list):
                for item in items_list:
                    if isinstance(item, dict):
                        text_content = item.get('text') or item.get('hadith') or item.get('content')
                        if text_content and len(str(text_content).strip()) > 20:
                            grade = item.get('grade', item.get('status', 'Unknown'))
                            all_documents.append(Document(
                                page_content=str(text_content),
                                metadata={
                                    'source': file_name,
                                    'type': 'hadith',
                                    'grade': grade,
                                    'book': item.get('book', file_name),
                                    'authenticity': f"Hadith - {grade}" if grade != 'Unknown' else "Hadith Collection"
                                }
                            ))
                            count += 1
            
            # Otherwise, iterate through dict values
            else:
                for key, value in data.items():
                    if isinstance(value, dict) and 'text' in value:
                        text_content = value.get('text')
                        if text_content and len(str(text_content).strip()) > 20:
                            grade = value.get('grade', 'Unknown')
                            all_documents.append(Document(
                                page_content=str(text_content),
                                metadata={
                                    'source': file_name,
                                    'type': 'hadith',
                                    'grade': grade,
                                    'authenticity': f"Hadith - {grade}" if grade != 'Unknown' else "Hadith Collection"
                                }
                            ))
                            count += 1
        
        if count > 0:
            source_stats[file_name] = count
            print(f"    ✅ {count:,} hadiths extracted")
        else:
            print(f"    ⚠️  No documents found in standard format")
    
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON decode error: {e}")
    except Exception as e:
        print(f"    ⚠️  Error: {e}")

# === Load Text Files (Quran translations & tafsir) ===
print(f"\n  📄 Processing text files...")
txt_files = sorted(glob.glob(os.path.join(DATA_PATH, "*.txt")))

for txt_file in txt_files:
    file_name = os.path.basename(txt_file)
    file_size_mb = os.path.getsize(txt_file) / 1024 / 1024
    
    print(f"    Loading {file_name} ({file_size_mb:.1f} MB)...")
    
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 50]
        
        for para in paragraphs:
            all_documents.append(Document(
                page_content=para,
                metadata={
                    'source': file_name,
                    'type': 'quranic_text' if 'quran' in file_name.lower() else 'tafsir',
                    'authenticity': 'Quranic Translation' if 'quran' in file_name.lower() else 'Scholarly Commentary'
                }
            ))
        
        source_stats[file_name] = len(paragraphs)
        print(f"      ✅ {len(paragraphs):,} paragraphs extracted")
    
    except Exception as e:
        print(f"      ⚠️  Error: {e}")

total_docs = len(all_documents)
print(f"\n✅ Total documents loaded: {total_docs:,}")
print(f"   Sources: {len(source_stats)}")
for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"     • {source}: {count:,}")

# ============================================================================
# STEP 2: Intelligent Chunking
# ============================================================================
print("\n✂️  STEP 2: Intelligent Document Chunking...")
print("-" * 80)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,      # Optimal for Islamic texts
    chunk_overlap=300,    # Preserve context
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

print(f"  Splitting {total_docs:,} documents...")
chunks = text_splitter.split_documents(all_documents)

print(f"✅ Split into {len(chunks):,} chunks")
avg_size = sum(len(c.page_content) for c in chunks) // len(chunks) if chunks else 0
print(f"   Average chunk size: {avg_size} characters\n")

# ============================================================================
# STEP 3: Build ChromaDB with Batching
# ============================================================================
print("🧠 STEP 3: Building ChromaDB (Vector Index)...")
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
    print(f"     ✅ Model loaded")
    
    # Delete old ChromaDB if exists
    if os.path.exists(CHROMA_PATH):
        print(f"  🗑️  Removing old ChromaDB...")
        import shutil
        shutil.rmtree(CHROMA_PATH, ignore_errors=True)
    
    # Create ChromaDB with batch processing
    print(f"  📦 Creating ChromaDB with {len(chunks):,} chunks...")
    print(f"     This may take several minutes...")
    
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="islamic_knowledge"
    )
    vector_db.persist()
    
    db_count = vector_db._collection.count()
    print(f"✅ ChromaDB created with {db_count:,} embedded documents\n")
    
except Exception as e:
    print(f"❌ ChromaDB creation failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 4: Build BM25 Keyword Index
# ============================================================================
print("🎯 STEP 4: Building BM25 Keyword Index...")
print("-" * 80)

try:
    print(f"  🔄 Tokenizing {len(chunks):,} documents...")
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
    
    bm25_size_mb = os.path.getsize(BM25_PATH) / 1024 / 1024
    print(f"✅ BM25 index saved ({bm25_size_mb:.1f} MB)")
    print(f"   Indexed {len(all_texts):,} documents\n")
    
except Exception as e:
    print(f"❌ BM25 index creation failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# Summary
# ============================================================================
print("="*80)
print("✅ COMPREHENSIVE INGESTION COMPLETE!")
print("="*80)
print(f"""
📊 Final Summary:
   • Documents loaded: {total_docs:,}
   • Chunks created: {len(chunks):,}
   • ChromaDB embeddings: {db_count:,}
   • BM25 index: {len(all_texts):,} documents
   • BM25 index size: {bm25_size_mb:.1f} MB
   
✨ Knowledge base ready for hybrid retrieval queries!
""")

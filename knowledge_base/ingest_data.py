"""
Islamic AI Agent - Local Knowledge Base Ingestion Script
Processes documents from knowledge_base/data/ and stores them in ChromaDB.
"""

import math
import os
import glob
import json
import hashlib
from typing import List, Dict
from dotenv import load_dotenv

import pickle
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
    JSONLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT_DIR, "knowledge_base/data")
CHROMA_PATH = os.path.join(ROOT_DIR, "knowledge_base/chroma_db")
BM25_PATH = os.path.join(ROOT_DIR, "knowledge_base/bm25_index.pkl")
STATE_FILE = os.path.join(ROOT_DIR, "knowledge_base/ingestion_state.json")

def get_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of a file"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_state() -> Dict:
    """Load the ingestion state from JSON"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load state file: {e}")
    return {"files": {}}

def save_state(state: Dict):
    """Save the ingestion state to JSON"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def load_documents_incremental(state: Dict) -> List[Document]:
    """Load only new or modified documents"""
    all_documents = []
    
    # Supported extensions
    extensions = [("*.pdf", PyPDFLoader), ("*.txt", TextLoader)]
    
    new_files_found = False
    
    for pattern, loader_cls in extensions:
        files = glob.glob(os.path.join(DATA_PATH, pattern))
        for file_path in files:
            file_name = os.path.basename(file_path)
            file_hash = get_file_hash(file_path)
            
            # Check if file changed
            if file_name not in state["files"] or state["files"][file_name] != file_hash:
                print(f"🆕 Processing new/modified file: {file_name}")
                try:
                    loader = loader_cls(file_path)
                    all_documents.extend(loader.load())
                    state["files"][file_name] = file_hash
                    new_files_found = True
                except Exception as e:
                    print(f"❌ Error loading {file_name}: {e}")
            else:
                pass # Already ingested
    
    # Custom Scholarly JSON processing
    json_files = glob.glob(os.path.join(DATA_PATH, "*.json"))
    for file_path in json_files:
        file_name = os.path.basename(file_path)
        file_hash = get_file_hash(file_path)
        
        if file_name not in state["files"] or state["files"][file_name] != file_hash:
            print(f"🆕 Processing Scholarly JSON: {file_name}")
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                
                new_docs = []
                # 1. AhmedBaset Hadith Structure (Sahih Bukhari, Muslim, Nawawi)
                if "hadiths" in data:
                    print(f"📖 Parsing {len(data['hadiths'])} hadiths from {file_name}")
                    for h in data["hadiths"]:
                        eng = h.get("english", {})
                        text = eng.get("text", "")
                        narrator = eng.get("narrator", "")
                        id_val = h.get("id") or h.get("hadithnumber")
                        
                        # Extra scholarly metadata
                        book_name = h.get("bookName") or h.get("book_name") or "General"
                        chapter_name = h.get("chapterName") or h.get("chapter_name") or "General"
                        grade = h.get("grade") or h.get("status") or "Sahih (Default)"
                        
                        metadata = {
                            "source": file_name, 
                            "type": "hadith", 
                            "id": str(id_val),
                            "book": book_name,
                            "chapter": chapter_name,
                            "grade": grade
                        }
                        
                        content = f"Prophetic Hadith #{id_val}\nBook: {book_name}\nChapter: {chapter_name}\nGrade: {grade}\nNarrator: {narrator}\nText: {text}"
                        new_docs.append(Document(page_content=content, metadata=metadata))
                
                # 2. Hisn al-Muslim Structure (Dua)
                elif "English" in data and isinstance(data["English"], list):
                    for cat in data["English"]:
                        category_name = cat.get("category", "General")
                        for item in cat.get("content", []):
                            text = item.get("text", "")
                            reference = item.get("reference", "")
                            content = f"🤲 Category: {category_name}\nDua/Adhkar: {text}\nSource: {reference}"
                            new_docs.append(Document(page_content=content, metadata={"source": file_name, "type": "dua", "category": category_name}))
                
                # 3. 99 Names or Surah Metadata (General 'data' key)
                elif "data" in data and isinstance(data["data"], list):
                    for entry in data["data"]:
                        if "name" in entry:
                            # Premium metadata format
                            metadata = {"source": file_name, "type": "metadata", "name": entry.get("name")}
                            content = f"Attribute: {entry.get('name')}\nMeaning: {entry.get('en', {}).get('meaning', 'N/A')}\nTransliteration: {entry.get('en', {}).get('transliteration', 'N/A')}"
                            new_docs.append(Document(page_content=content, metadata=metadata))
                
                if new_docs:
                    all_documents.extend(new_docs)
                    state["files"][file_name] = file_hash
                    new_files_found = True
                    print(f"✅ Extracted {len(new_docs)} scholarly documents from {file_name}")
                
            except Exception as e:
                print(f"❌ Error loading scholarly JSON {file_name}: {e}")
                
    if not new_files_found:
        print("✅ No new or modified files detected. Knowledge base is up to date.")
        
    return all_documents

def split_text(documents: List[Document]) -> List[Document]:
    """Split documents into chunks with optimized overlap for Islamic context"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, # Slightly larger for better context
        chunk_overlap=300, # More overlap for continuity in verses/hadiths
        length_function=len,
        add_start_index=True,
        separators=["\n\n", "\n", " ", ""] # Priority to block breaks
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    return chunks

def update_vector_db(chunks: List[Document]):
    """Add new chunks to the existing ChromaDB or create if not exists"""
    # UPGRADE: Using large model for world-class semantic understanding
    model_name = "intfloat/multilingual-e5-large"
    
    # Check if we need to reset DB due to model change
    state = load_state()
    current_model = state.get("embedding_model", "intfloat/multilingual-e5-small")
    
    if current_model != model_name:
        print(f"🔄 Embedding model changed from {current_model} to {model_name}.")
        print("⚠️ Resetting ChromaDB for dimension compatibility...")
        if os.path.exists(CHROMA_PATH):
            import shutil
            shutil.rmtree(CHROMA_PATH)
        state["files"] = {} # Force re-processing of all files
        state["embedding_model"] = model_name
        save_state(state)

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    if os.path.exists(CHROMA_PATH) and os.listdir(CHROMA_PATH):
        print(f"📦 Updating existing ChromaDB at {CHROMA_PATH}...")
        vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        
        batch_size = 100
        total = len(chunks)
        for i in range(0, total, batch_size):
            batch = chunks[i : i + batch_size]
            vector_db.add_documents(batch)
            print(f"✅ Added batch {int(i/batch_size) + 1}/{math.ceil(total/batch_size)}")
        
        vector_db.persist()
    else:
        print(f"📦 Creating new ChromaDB at {CHROMA_PATH}...")
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_PATH
        )
        vector_db.persist()
    
    # NEW: Build/Update BM25 Index for Hybrid Search
    print("🎯 Building BM25 index for Hybrid Search...")
    try:
        from rank_bm25 import BM25Okapi
        import nltk
        from nltk.tokenize import word_tokenize
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        # Collect ALL documents for BM25 (since it's a global statistic)
        # Note: In a massive scale, we'd use a more specialized keyword engine
        all_docs = []
        if os.path.exists(CHROMA_PATH):
            vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
            # This is a bit heavy for 59k docs, but necessary for the "World Best" requirement
            # In a real prod env, we'd use Elasticsearch/Meilisearch
            all_docs = vector_db.get()['documents']
        
        if all_docs:
            tokenized_corpus = [word_tokenize(doc.lower()) for doc in all_docs]
            bm25 = BM25Okapi(tokenized_corpus)
            with open(BM25_PATH, 'wb') as f:
                pickle.dump(bm25, f)
            print(f"✅ BM25 index saved to {BM25_PATH}")
    except Exception as e:
        print(f"⚠️ BM25 build failed: {e}")
    
    print("✨ Knowledge base update complete.")

def run_ingestion():
    """Main function to run the incremental ingestion pipeline"""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        return

    state = load_state()
    
    # UPGRADE: Check if we need to reset DB due to model change BEFORE loading
    model_name = "intfloat/multilingual-e5-large"
    current_model = state.get("embedding_model", "intfloat/multilingual-e5-small")
    
    if current_model != model_name:
        print(f"🔄 Embedding model changed from {current_model} to {model_name}.")
        print("⚠️ Resetting system for World-Class RAG upgrade...")
        if os.path.exists(CHROMA_PATH):
            import shutil
            shutil.rmtree(CHROMA_PATH)
        if os.path.exists(BM25_PATH):
            os.remove(BM25_PATH)
        state["files"] = {} # Force re-processing of all files
        state["embedding_model"] = model_name
        save_state(state)

    documents = load_documents_incremental(state)
    
    if documents:
        chunks = split_text(documents)
        if chunks:
            update_vector_db(chunks)
            save_state(state)
    else:
        print("No new information to ingest.")

if __name__ == "__main__":
    run_ingestion()

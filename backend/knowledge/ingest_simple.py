"""
Simplified ingestion - Build BM25 index and prepare documents
Skip ChromaDB client issues and focus on what works
"""

import os
import glob
import json
import hashlib
import pickle
from typing import List, Dict
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    TextLoader, JSONLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(CURRENT_DIR, "data")
BM25_PATH = os.path.join(CURRENT_DIR, "bm25_index.pkl")
STATE_FILE = os.path.join(CURRENT_DIR, "ingestion_state.json")

def get_file_hash(file_path: str) -> str:
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_state() -> Dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"files": {}}

def save_state(state: Dict):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def load_documents_incremental(state: Dict) -> List[Document]:
    all_documents = []
    extensions = [("*.txt", TextLoader)]
    
    for pattern, loader_cls in extensions:
        files = glob.glob(os.path.join(DATA_PATH, pattern))
        for file_path in files:
            file_name = os.path.basename(file_path)
            file_hash = get_file_hash(file_path)
            
            if file_name not in state["files"] or state["files"][file_name] != file_hash:
                print(f"🆕 Processing: {file_name}")
                try:
                    loader = loader_cls(file_path)
                    all_documents.extend(loader.load())
                    state["files"][file_name] = file_hash
                except Exception as e:
                    print(f"❌ Error: {file_name}: {e}")

    # JSON processing
    json_files = glob.glob(os.path.join(DATA_PATH, "*.json"))
    for file_path in json_files:
        file_name = os.path.basename(file_path)
        file_hash = get_file_hash(file_path)
        
        if file_name not in state["files"] or state["files"][file_name] != file_hash:
            print(f"🆕 Processing JSON: {file_name}")
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                
                new_docs = []
                
                # Hadiths
                if "hadiths" in data:
                    print(f"  📖 {len(data['hadiths'])} hadiths")
                    for h in data["hadiths"]:
                        eng = h.get("english", {})
                        text = eng.get("text", "")
                        narrator = eng.get("narrator", "")
                        id_val = h.get("id") or h.get("hadithnumber")
                        
                        book_name = h.get("bookName") or h.get("book_name") or "General"
                        chapter_name = h.get("chapterName") or h.get("chapter_name") or "General"
                        grade = h.get("grade") or h.get("status") or "Sahih"
                        
                        metadata = {
                            "source": file_name, 
                            "type": "hadith", 
                            "id": str(id_val),
                            "book": book_name,
                            "chapter": chapter_name,
                            "grade": grade
                        }
                        
                        content = f"Hadith #{id_val}\nBook: {book_name}\nChapter: {chapter_name}\nGrade: {grade}\nNarrator: {narrator}\nText: {text}"
                        new_docs.append(Document(page_content=content, metadata=metadata))
                
                # 99 Names
                elif "data" in data and isinstance(data["data"], list):
                    print(f"  📋 {len(data['data'])} items")
                    for entry in data["data"]:
                        if "name" in entry:
                            metadata = {"source": file_name, "type": "metadata", "name": entry.get("name")}
                            content = f"Attribute: {entry.get('name')}\nMeaning: {entry.get('en', {}).get('meaning', 'N/A')}"
                            new_docs.append(Document(page_content=content, metadata=metadata))
                
                if new_docs:
                    all_documents.extend(new_docs)
                    state["files"][file_name] = file_hash
                    print(f"  ✅ {len(new_docs)} documents extracted")
                
            except Exception as e:
                print(f"❌ Error: {file_name}: {e}")
                
    return all_documents

def split_text(documents: List[Document]) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300,
        length_function=len,
        add_start_index=True,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    doc_chunk_counters = {}
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        if source not in doc_chunk_counters:
            doc_chunk_counters[source] = 0
        chunk.metadata["chunk_index"] = doc_chunk_counters[source]
        doc_chunk_counters[source] += 1
    
    print(f"✅ Split into {len(chunks)} chunks")
    return chunks

def build_bm25_index(chunks: List[Document]):
    print("🎯 Building BM25 Index...")
    try:
        from rank_bm25 import BM25Okapi
        import nltk
        from nltk.tokenize import word_tokenize
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("  Downloading NLTK tokenizer...")
            nltk.download('punkt', quiet=True)

        texts = [chunk.page_content for chunk in chunks]
        corpus = [word_tokenize(text.lower()) for text in texts]
        
        bm25 = BM25Okapi(corpus)
        
        # Save index
        with open(BM25_PATH, 'wb') as f:
            pickle.dump({
                'bm25': bm25,
                'texts': texts,
                'metadata': [chunk.metadata for chunk in chunks],
                'total_docs': len(chunks)
            }, f)
        
        print(f"✅ BM25 Index built with {len(chunks)} documents")
        print(f"💾 Saved to {BM25_PATH}")
        
    except Exception as e:
        print(f"❌ BM25 Error: {e}")

def run_ingestion():
    print("📚 Starting Islamic Knowledge Base Ingestion...")
    state = load_state()
    
    documents = load_documents_incremental(state)
    print(f"📄 Loaded {len(documents)} documents")
    
    if not documents:
        print("✅ No new documents to process")
        return
    
    chunks = split_text(documents)
    build_bm25_index(chunks)
    
    save_state(state)
    print("\n🎉 Ingestion complete!")
    print(f"📊 Total chunks: {len(chunks)}")
    print(f"💾 BM25 index ready for semantic search")

if __name__ == "__main__":
    run_ingestion()

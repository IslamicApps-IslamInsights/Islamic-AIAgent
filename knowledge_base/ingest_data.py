"""
Islamic AI Agent - Local Knowledge Base Ingestion Script
Processes documents from knowledge_base/data/ and stores them in ChromaDB.
"""

import os
import glob
from typing import List
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
    JSONLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Load environment variables
load_dotenv()

# Configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT_DIR, "knowledge_base/data")
CHROMA_PATH = os.path.join(ROOT_DIR, "knowledge_base/chroma_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_document_loaders() -> List[DirectoryLoader]:
    """Configure loaders for different file types"""
    loaders = [
        DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader),
        # Add more loaders if needed (e.g., CSV, Docx)
    ]
    return loaders

def load_documents() -> List[Document]:
    """Load all documents from the data directory"""
    documents = []
    
    # PDF Loader
    pdf_loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents.extend(pdf_loader.load())
    
    # Text Loader
    txt_loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader)
    documents.extend(txt_loader.load())
    
    print(f"Loaded {len(documents)} documents.")
    return documents

def split_text(documents: List[Document]) -> List[Document]:
    """Split documents into chunks"""
    # Using RecursiveCharacterTextSplitter which is great for maintaining context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks: List[Document]):
    """Save chunks to ChromaDB with Local Multilingual Embeddings"""
    # Use one of the best multilingual models in the world for Arabic, Urdu, and English
    model_name = "intfloat/multilingual-e5-large"
    print(f"Initializing local embedding model: {model_name}...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'}, # Use 'cuda' if GPU is available
        encode_kwargs={'normalize_embeddings': True}
    )

    # Initialize Chroma
    db = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=CHROMA_PATH
    )
    
    # Perist the database
    # Note: In newer langchain-chroma/chromadb versions, persistence is automatic.
    # But we'll call persist if the version supports it for safety.
    if hasattr(db, 'persist'):
        db.persist()
    
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

def main():
    """Execute the ingestion pipeline"""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Created {DATA_PATH}. Please add your Islamic documents there.")
        return

    # 1. Load documents
    documents = load_documents()
    if not documents:
        print("No documents found in knowledge_base/data/. Please upload some TXT or PDF files.")
        return

    # 2. Split into chunks
    chunks = split_text(documents)

    # 3. Save to ChromaDB
    save_to_chroma(chunks)

if __name__ == "__main__":
    main()

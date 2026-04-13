import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT_DIR, "knowledge_base/data/islamic_ground_truth_essentials.txt")
CHROMA_PATH = os.path.join(ROOT_DIR, "knowledge_base/chroma_db")

def fast_ingest():
    print("🚀 Starting Fast Ground Truth Ingestion...")
    
    # 1. Load the specific ground truth file
    loader = TextLoader(DATA_PATH)
    documents = loader.load()
    print(f"Loaded {len(documents)} document.")

    # 2. Split into small, high-density chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} high-density chunks.")

    # 3. Initialize embeddings
    model_name = "intfloat/multilingual-e5-small"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # 4. Add to existing ChromaDB
    print(f"Adding to existing ChromaDB at {CHROMA_PATH}...")
    vector_db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    vector_db.add_documents(chunks)
    vector_db.persist()
    print("✨ Ground Truth successfully integrated into the knowledge base!")

if __name__ == "__main__":
    fast_ingest()

import sys
import os
sys.path.append(os.getcwd())

import pickle
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
try:
    nltk.download('punkt')
except:
    pass

CHROMA_PATH = "backend/knowledge/chroma_db"
BM25_PATH = "backend/knowledge/bm25_index.pkl"

print("Loading embeddings...")
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

print("Connecting to ChromaDB...")
vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

all_texts = []
all_metadatas = []
print("Paginating through database...")

# Paginate to avoid "too many SQL variables"
limit = 5000
offset = 0

while True:
    try:
        db_data = vector_db._collection.get(limit=limit, offset=offset)
        docs = db_data.get('documents', [])
        metas = db_data.get('metadatas', [])
        
        if not docs:
            break
            
        all_texts.extend(docs)
        all_metadatas.extend(metas)
        print(f"Extracted offset {offset}...")
        offset += limit
    except Exception as e:
        print(f"Extraction halted at offset {offset}: {e}")
        break

print(f"Total documents extracted: {len(all_texts)}")

if all_texts:
    print("Tokenizing documents for offline BM25 model...")
    tokenized_corpus = [word_tokenize(doc.lower()) for doc in all_texts]
    bm25 = BM25Okapi(tokenized_corpus)

    payload = {
        "model": bm25,
        "texts": all_texts,
        "metadatas": all_metadatas
    }

    with open(BM25_PATH, 'wb') as f:
        pickle.dump(payload, f)
    print(f"✅ Fast BM25 rebuilt successfully! Saved to {BM25_PATH}")
else:
    print("❌ No documents recovered!")

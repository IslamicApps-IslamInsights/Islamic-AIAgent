# Production Scaling & Infrastructure Guide

As the Islamic AI Agent's knowledge base expands (approaching 1GB+ with Sahih Bukhari and Muslim), the following architectural optimizations are recommended for production reliability.

## 1. Managed Vector Database Migration

Currently, the system uses a local **ChromaDB** instance. For production, consider:

### Option A: Self-Hosted Chroma Server (Docker)
Run Chroma as a standalone service to decouple database performance from the Flask API.
- **Benefit**: Persistence is managed independently of the application lifecycle.
- **Config**: Update `PersistentClient` in `islamic_ai_agent.py` to use `HttpClient(host="...", port=...)`.

### Option B: Managed Pinecone or MongoDB Atlas
For datasets exceeding 10GB or requiring high concurrency.
- **Benefit**: Auto-scaling and high availability.
- **Action**: Implement a new `ServiceToolkit` wrapper for the remote provider.

## 2. RAG Performance Optimization

### Hybrid Retrieval
Combine Chroma's semantic search with **Elasticsearch/OpenSearch** for keyword-heavy Islamic queries (e.g., specific Hadith numbers).

### Context Compression
Use `LongContextReorder` or `ContextualCompressionRetriever` from LangChain to ensure the most relevant scholarly chunks are prioritized within the LLM's context window.

## 3. Large-Scale Ingestion

### Batch Processing
The `ingest_data.py` script should be updated to use `batch_size=100` when processing the 7,000+ entries of Sahih Bukhari to avoid memory spikes.

### Specialized Indexing
Index Hadith by "Book" and "Chapter" metadata rather than just raw text to allow for filtered searches (e.g., "Search only in Sahih Muslim").

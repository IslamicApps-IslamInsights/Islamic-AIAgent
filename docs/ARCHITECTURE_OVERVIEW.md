# Architecture Overview - Noor (Local-First Islamic AI Agent)

This document provides a high-level technical overview of how Noor combines a local Knowledge Base (RAG), Quran Foundation MCP, and a local LLM to deliver helpful Islamic answers that stay grounded in authentic sources.

## Component Diagram

```mermaid
graph TD
    A[React/Vite Frontend] <-->|HTTP JSON| B[Flask API: backend/api/web_api.py]
    B --> C[Intelligent Router]
    C -->|Quran-first queries| D[Quran Foundation MCP Provider]
    D -->|JSON-RPC (Streamable HTTP + SSE)| E[Quran Foundation MCP Server]

    C -->|General guidance| F[Hybrid RAG Retriever]
    F --> G[BM25 Keyword Index]
    F --> H[ChromaDB Vector Store]
    H -->|Embeddings| I[intfloat/multilingual-e5-large]

    C -->|Build evidence pack| J[Evidence Pack + Source References]
    J -->|Synthesize| K[Local LLM (llama.cpp server)]
    K --> B

    L[Knowledge Upload API] --> M[backend/knowledge/data]
    N[Auto Ingest Service] -->|Watches folder| M
    N -->|Updates| G
```

## Interaction Flows

### 1) Chat request → routed retrieval → grounded answer
1. Frontend sends `POST /api/chat` with the user message.
2. The router classifies intent and picks the best path:
   - Quran-focused questions use Quran Foundation MCP (canonical Quran data).
   - General learning uses local Hybrid RAG (BM25 + Chroma).
3. Results are packed into short evidence snippets with references.
4. The local LLM synthesizes a warm, practical answer using only that evidence.
5. The API sanitizes user-facing output (removes hidden tags) and returns the final answer.

### 2) Quran-first flow (Quran Foundation MCP)
When the user asks about Quran, surahs/ayahs, themes, tafsir, or translations:
- The system calls MCP tools (search/fetch) and treats results as primary evidence.
- Translation language can be user-selected (frontend passes `quran_translation_lang`).

### 3) Local Knowledge Base flow (Hybrid RAG)
When the user asks about general topics (fiqh basics, ethics/akhlaq, seerah, duas, etc.):
- BM25 provides fast keyword matching for exact phrases and references.
- Chroma provides semantic matches using `intfloat/multilingual-e5-large`.
- Optional reranking may run if a reranker model is available (non-critical).

### 4) Knowledge upload → ingestion → searchable in RAG
1. Upload a file to:
   - `POST /api/knowledge/upload` (supports `json`, `txt`, `csv`, `pdf`)
   - `POST /api/knowledge/upload-secure` (supports `pdf`, `txt`, `docx`, `json`, `csv`, 5MB limit)
2. Files are saved into `backend/knowledge/data/`.
3. The auto-ingest watcher detects new/modified files and updates the BM25 index.
4. Full ingestion (optional) can rebuild Chroma + BM25 using the configured embeddings model.

## Technical Stack

| Layer | Technology |
| --- | --- |
| Frontend | React + Vite |
| Backend API | Python + Flask |
| Quran Data | Quran Foundation MCP (JSON-RPC over Streamable HTTP + SSE) |
| Embeddings | `intfloat/multilingual-e5-large` |
| Vector Store | ChromaDB (persistent) |
| Keyword Search | BM25 (rank_bm25) |
| Local Synthesis | llama.cpp server (OpenAI-compatible API) |

## Key Principles (Best Practices)
- Quran-first for Quran questions (MCP is the canonical source).
- Evidence-grounded answers (no invented narrations or verse wording).
- Local-first inference (no external LLM APIs required).
- Keep answers engaging: clear structure, gentle encouragement, and one short follow-up question.

# Deployment Plan - Noor (Local-First Islamic AI Agent)

This plan describes a production-grade deployment for Noor with:
- Local Knowledge Base (Hybrid RAG: BM25 + ChromaDB)
- Local LLM answer synthesis (llama.cpp server + GGUF in `backend/models/`)
- Quran Foundation MCP integration for Quran-first queries

## Goals
- Local-first inference (no external LLM APIs).
- Stable startup and predictable resource usage.
- Persistent storage for knowledge base indexes and uploads.
- Safe network exposure (TLS + reverse proxy, minimal open ports).

## Deployment Options

### Option A (Recommended): Single Server (No Docker)
Use this when you want the simplest, most reliable production setup.

#### What runs
- llama.cpp server on `:8080` (local network only)
- Flask backend on `:5010` (behind reverse proxy)
- Frontend static server on `:3001` (behind reverse proxy)

#### Prerequisites
- Linux server (Ubuntu/Debian recommended)
- Python 3.10+
- Node.js 18+
- `llama-server` available (install via package manager or build llama.cpp)

#### Persistent paths
- Model: `backend/models/*.gguf`
- Knowledge uploads: `backend/knowledge/data/`
- Chroma: `backend/knowledge/chroma_db_full/`
- BM25: `backend/knowledge/bm25_full_index.pkl`
- Logs: `logs/`

#### One-command production start
```bash
chmod +x run.sh
./run.sh --prod
```

This script is expected to:
- ensure venv + dependencies
- ensure GGUF model exists in `backend/models/` (downloads if missing)
- run ingestion if needed
- start llama.cpp + backend + frontend

#### Health checks (post-deploy)
- `GET http://127.0.0.1:5010/api/health`
- Confirm:
  - `rag_system.ready: true`
  - `local_llm.reachable: true`

#### Reverse proxy (TLS)
Put Nginx/Caddy in front:
- Public: `:443` only
- Private/loopback: `:5010`, `:3001`, `:8080`

Minimum proxy routing:
- `/api/*` → backend `http://127.0.0.1:5010`
- `/` → frontend `http://127.0.0.1:3001`

### Option B: Docker Compose (Multi-container)
Use this when you need consistent packaging and easier upgrades.

Important: the current `docker-compose.yml` does not include a llama.cpp server or persistent KB volumes. A production compose should add:
- a llama.cpp service
- a volume mount for the model file
- a volume mount for `backend/knowledge/` (data + indexes)

Recommended container responsibilities:
- `llm`: llama.cpp server serving OpenAI-compatible endpoints
- `backend`: Flask API (gunicorn)
- `frontend`: static site (built) or node dev server (dev only)
- `nginx`: TLS termination and routing

## Environment Configuration

### Local LLM
These must point the backend to the local llama.cpp server:
```env
LOCAL_LLM_BACKEND=llama_cpp_server
LLAMA_CPP_SERVER_URL=http://localhost:8080
LOCAL_LLM_MODEL_PATH=/absolute/path/to/backend/models/qwen2.5-7b-ins-v3-Q4_K_M.gguf
LOCAL_LLM_MAX_TOKENS=700
LOCAL_LLM_TEMPERATURE=0.4
```

### RAG / Ingestion
Recommended ingestion knobs for low-memory servers:
```env
INGEST_BATCH_SIZE=32
INGEST_EMBED_BATCH_SIZE=8
INGEST_DEVICE=cpu
```

## Data Persistence and Backups
- Back up these folders/files:
  - `backend/knowledge/data/` (uploaded and curated knowledge)
  - `backend/knowledge/chroma_db_full/` (vector store)
  - `backend/knowledge/bm25_full_index.pkl` (keyword index)
  - `backend/knowledge/auto_ingest_state.json` (auto-ingest state)
- If you restore on a new server:
  - ensure the same embeddings model is used (`intfloat/multilingual-e5-large`)
  - if mismatched, rebuild with `python3 backend/knowledge/full_data_ingestion.py`

## Security Checklist (Production)
- Put backend behind a reverse proxy with TLS (no direct public exposure of `:5010`).
- Restrict CORS origins to your domain (avoid `*` in production).
- Keep the llama.cpp server bound to loopback/private network only.
- Set a strict upload size limit and allowlist file extensions (already enforced in the secure uploader).
- Do not store secrets in git or inside docs.

## Operational Checklist
- Start order:
  1) llama.cpp server
  2) backend
  3) frontend
  4) call `POST /api/initialize` if needed
- Monitor:
  - `logs/backend.log`, `logs/llm.log`, `logs/frontend.log`
  - `GET /api/health` for readiness signals

## Rollback Plan
- Keep the last known-good:
  - `backend/knowledge/` persisted data
  - model file in `backend/models/`
  - pinned `requirements.txt` and `frontend/package-lock.json`
- If an update causes failures:
  - redeploy previous commit
  - keep the persisted `backend/knowledge/` and `backend/models/` unchanged

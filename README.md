# 🕌 Noor - Islamic AI Agent (Local-First)
![Noor Logo](frontend/public/noor-logo.png)

Noor is a local-first Islamic AI agent that combines:
- A private, local Knowledge Base (Hybrid RAG: BM25 + ChromaDB)
- A fully local answer synthesizer (llama.cpp / OpenAI-compatible server)
- Quran Foundation MCP for Quran-first queries (canonical Quran, translations, tafsir, and related tools)

Noor is for learning and reference. For personal rulings and complex cases, consult qualified local scholars.

## ✅ Core Best Practices (What makes answers “Islamic” + engaging)
- Quran-first: Quran Foundation MCP is the primary source for Quran-related questions.
- Evidence-grounded: the generator is instructed to answer only from retrieved evidence and to avoid fabrication.
- User-friendly: clear guidance, practical steps, gentle encouragement, and one short follow-up question to keep the user engaged.
- Local-only: no external LLM APIs required for inference.

## 🚀 Quick Start (Recommended)
### Prerequisites
- Python 3.10+
- Node.js 18+

### Run everything
```bash
chmod +x run.sh
./run.sh
```

What `run.sh` handles:
- Creates/updates `.venv` and installs Python deps
- Ensures the local GGUF model exists (downloads if missing)
- Starts llama.cpp server + backend + frontend
- Runs ingestion when needed (so RAG is ready)

## 📚 Knowledge Base (RAG)
### Data folder
- Add your knowledge files into: `backend/knowledge/data/`

### Supported upload types (backend)
- Upload endpoint: `POST /api/knowledge/upload`
  - Allowed: `json`, `txt`, `csv`, `pdf`
- Secure upload endpoint: `POST /api/knowledge/upload-secure`
  - Allowed: `pdf`, `txt`, `docx`, `json`, `csv` (5MB limit)

### Manual full ingestion (optional)
```bash
python3 backend/knowledge/full_data_ingestion.py
```

### Embeddings model (must match)
- `intfloat/multilingual-e5-large`

## 🧠 Local LLM (Answer Synthesis)
- Default architecture uses a local OpenAI-compatible server (llama.cpp server).
- The synthesis prompt enforces:
  - No hidden reasoning tags
  - Islamic tone + practical guidance
  - One short follow-up question
  - Citations grounded in retrieved sources (UI can render sources cleanly)

## 🔎 Useful Endpoints
- Health: `GET /api/health`
- Upload KB file: `POST /api/knowledge/upload`
- List KB files: `GET /api/knowledge/list`
- List data folder files: `GET /api/knowledge/data-files`
- Auto-ingest status: `GET /api/knowledge/ingest-status`

## 📂 Project Structure (Short)
```text
backend/api/web_api.py          # Flask API
backend/knowledge/              # RAG ingestion + Chroma/BM25 stores
backend/utils/quran_mcp_provider.py  # Quran Foundation MCP integration
frontend/                       # React (Vite) UI
run.sh                          # One-command runner
```

# Development Guide - Islamic AI Agent

This guide provides the necessary information for developers and scholars to set up, contribute, and maintain the **Noor** Islamic AI Agent project.

---

## 🏗️ Environmental Configuration

### 1. Requirements
- **Python 3.10+** (recommended for dependency compatibility).
- **Node.js 18+** (for Vite React frontend).
- **Git** for version control.

### 2. Environment Variables (.env)
Noor is designed to run in local-first mode. Do not commit secrets.

Common local vars (optional):
```env
LOCAL_LLM_BACKEND=llama_cpp_server
LLAMA_CPP_SERVER_URL=http://localhost:8080
LOCAL_LLM_MAX_TOKENS=700
LOCAL_LLM_TEMPERATURE=0.4
```

---

## 🛠️ Local Development Setup

### 0. Recommended: one command runner
```bash
chmod +x run.sh
./run.sh
```

### 1. Backend (Python/Flask)
```bash
# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask API Gateway (Port 5010)
python3 backend/api/web_api.py --port 5010
```

### 1b. Local LLM (llama.cpp server)
Noor uses an OpenAI-compatible local server (llama.cpp) for answer synthesis.

Typical run:
```bash
llama-server -m backend/models/qwen2.5-7b-ins-v3-Q4_K_M.gguf --host 0.0.0.0 --port 8080 --ctx-size 4096
```

### 2. Frontend (React/Vite)
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Development Server (Port 3001)
npm run dev -- --port 3001
```

---

## 🎨 Design System & UI Components

### 1. Theme Tokens (Museum Grade)
The frontend uses a custom design system centered around **"Museum Plaque"** aesthetics:
- **Primary Color**: `#E5C06F` (Scholarly Gold)
- **Background**: `#010A09` (Deep Spiritual Teal/Dark Mode)
- **Typography**: 
    - **Amiri**: For Arabic script and scholarly headings.
    - **Inter**: For clean, modern UI elements.
    - **Outfit**: For high-fidelity tracking and metadata.

### 2. Animations
- **Framer Motion**: Used for all transitions, including the `SanctuaryGreeting` pulse and scholarly evidence fades.
- **Glassmorphism**: Achieved via Tailwind's `backdrop-blur` and `bg-white/[0.03]` utility classes.

---

## 🧩 Modifying Agents

Noor’s behavior is controlled primarily by routing + synthesis rules:
1. Routing and tool selection: `backend/utils/intelligent_tool_router.py`
2. Quran Foundation MCP integration: `backend/utils/quran_mcp_provider.py`
3. Local LLM synthesis rules: `backend/utils/llm_provider.py`

---

## 🤝 Contribution Workflow
1. Add knowledge files: `backend/knowledge/data/` (supports `json`, `txt`, `csv`, `pdf`)
2. Full ingestion (Chroma + BM25): `python3 backend/knowledge/full_data_ingestion.py`
3. For quick updates, rely on the auto-ingest watcher (BM25 updates on new files)
4. Keep citations readable; avoid exposing internal tags in user-facing output

---

> [!WARNING]
> After pulling updates: run `pip install -r requirements.txt` and `npm install` to keep dependencies in sync.

## Troubleshooting
- `503 AGENT_INITIALIZING`: wait a moment or call `POST /api/initialize`.
- JSON upload rejected: use `POST /api/knowledge/upload` or `POST /api/knowledge/upload-secure`.
- RAG feels outdated after adding files: run `python3 backend/knowledge/full_data_ingestion.py`.

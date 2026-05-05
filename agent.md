# Islamic AI Agent (Best Practices)

## Goal
Provide user-centric Islamic guidance that is:
- Quran-first when relevant (Quran Foundation MCP)
- Evidence-grounded (local KB + verified sources)
- Clear and practical (actionable steps)
- Safe (no fabrication; ask a short follow-up when evidence is missing)
- Local-first (no external LLM APIs required for inference)

## Recommended Architecture (High Level)
1) **Intent routing**
   - Quran, hadith, seerah/sahaba, duas/adhkar, prayer times, qibla, general guidance.
2) **Retrieval (RAG)**
   - Hybrid retrieval: BM25 + ChromaDB.
   - Embeddings: `intfloat/multilingual-e5-large`.
3) **Evidence packing**
   - Keep only the most relevant snippets.
   - Preserve metadata (surah:ayah, book/chapter, etc.) for clean references.
4) **Synthesis (fully local)**
   - A local model writes the final answer using only the evidence.
   - Tone: warm, respectful, practical, and engaging.
   - Format: clear sections + one short guiding question at the end.
5) **Quran Foundation MCP**
   - Canonical Quran and optional tafsir/translation, added as evidence when needed.

## What embeddings do (important)
Embeddings do not generate text. They help retrieval. Great answers come from:
- clean ingestion and chunking
- accurate retrieval and filtering
- strict evidence-grounded synthesis

## Local LLM (Generator) Best Practices
### Recommended model
- Qwen2.5 7B Instruct (GGUF, Q4_K_M)

### llama.cpp server (recommended)
- Model path:
  - `backend/models/qwen2.5-7b-ins-v3-Q4_K_M.gguf`
- Typical run:
  - `llama-server -m backend/models/qwen2.5-7b-ins-v3-Q4_K_M.gguf --host 0.0.0.0 --port 8080 --ctx-size 4096`

### Backend env vars
- `LOCAL_LLM_BACKEND=llama_cpp_server`
- `LLAMA_CPP_SERVER_URL=http://localhost:8080`
- `LOCAL_LLM_MAX_TOKENS=700`
- `LOCAL_LLM_TEMPERATURE=0.4`

## Ingestion Best Practices (Knowledge Base)
### Source of truth
- Put files in: `backend/knowledge/data/`

### Supported file types for ingestion
- `json`, `txt`, `csv`, `pdf`

### Full ingestion
- `python3 backend/knowledge/full_data_ingestion.py`

## Response Best Practices (User-Centric + Islamic)
Recommended structure:
1) Greeting + short direct answer
2) Key points (3 bullets)
3) Next step (one line) + one short follow-up question
4) Sources (only what was cited)

Rules:
- Never invent ayah/hadith wording, grading, or numbers.
- When evidence is insufficient: say you are not sure, then ask one short question.
- Avoid technical terms in user-facing output (no “RAG”, “BM25”, “embeddings”).

## Quality Checklist
- Correct routing (Quran vs KB vs tools).
- Helpful and gentle tone (tarbiyah style: encouraging, not harsh).
- Practical action steps.
- One short follow-up question to keep engagement.

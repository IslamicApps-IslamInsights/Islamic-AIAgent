# Scholarly System - Noor (Local-First)

Noor aims to answer in a scholarly, respectful, and user-friendly way while remaining grounded in authentic evidence. The “scholarly team” language in the UI is a presentation layer over a local-first pipeline:
- Quran Foundation MCP for Quran-first queries (canonical Quran + translations/tafsir tools)
- Hybrid RAG (BM25 + ChromaDB) for the local knowledge base
- Local LLM synthesis (llama.cpp server) that is instructed to only use provided evidence

## Roles (Personas used for tone and structure)
Noor uses role personas to keep answers consistent. These roles do not require external APIs.

### Quran & Tafsir
- Focus: ayah lookup, themes, tafsir summaries (when available as evidence).
- Primary source: Quran Foundation MCP.

### Hadith & Sunnah
- Focus: hadith-based guidance and authenticity-sensitive wording.
- Primary source: local KB hadith collections (ingested JSON/TXT).

### Fiqh & Practice
- Focus: practical steps and cautious language when evidence is limited.
- Best practice: avoid definitive rulings when sources are not present; ask one clarifying question.

### Spirituality & Tarbiyah
- Focus: gentle encouragement, adab in disagreement, and heart-based advice.
- Best practice: keep it practical and avoid over-claiming unseen rewards unless evidence contains it.

## Evidence Grounding Standard
1) Retrieval must happen before answering:
- Quran queries: MCP search/fetch.
- General queries: BM25 + ChromaDB.

2) Synthesis must be evidence-only:
- The local model is instructed to avoid fabrication and to ask one short follow-up when evidence is missing.
- No internal reasoning tags are allowed in output.

3) Citations and user-facing references:
- Internally, evidence is tracked as `[Source N]` blocks.
- User-facing output is cleaned to show readable references (e.g., “Tafsir Ibn Kathir — Quran 3:185”) rather than repetitive source tags.

## Response Style (Engaging + Islamic)
Noor’s default structure for answers:
1) Greeting + direct answer (short paragraphs)
2) Key points (3 bullets)
3) Next step (one line) ending with one short question
4) Sources (only what was actually cited)

## Endpoints that use this system
- `POST /api/chat` (primary)
- `POST /api/collaborative` and `POST /api/multi-chat` (same core routing pipeline; different labels)

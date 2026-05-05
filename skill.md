# Skills & Tools (Best Practices)

## Skills (What the agent can do)
This project is designed around a small set of reliable “skills” so user queries are handled accurately and consistently.

### 1) Local Knowledge Base (RAG)
**Use when:** general Islamic guidance, fiqh basics, ethics/akhlaq, seerah, dua/adhkar explanations, learning topics.

**Inputs:**
- User question (string)

**Process:**
- Hybrid retrieval: BM25 + Chroma semantic search (E5 embeddings).
- Produce evidence blocks:
  - `[Source 1] <reference>`
  - `<snippet>`

**Output:**
- Evidence‑grounded answer with citations.

**Best practices:**
- Prefer fewer, higher-signal sources (top 4–8) rather than dumping many passages.
- Keep snippets short and readable.

### 2) Quran Foundation MCP (Quran lookup)
**Use when:**
- The user asks about Quran, specific themes/verses, or wants Quran evidence.

**Inputs:**
- Query text (string)
- Optional: include_tafsir (boolean)

**Output:**
- 1–2 relevant verses (Arabic + translation when available), cited.

**Best practices:**
- Treat MCP output as evidence; include it in the evidence pack for synthesis.
- If the user requests an exact ayah, show the ayah reference clearly.
- Use the user-selected translation language when provided.

### 3) Prayer Times
**Use when:**
- The user asks for prayer times for a location/date.

**Inputs:**
- Location info (city/country or lat/lon)
- Date (optional)

**Output:**
- Times in a simple list (Fajr, Dhuhr, Asr, Maghrib, Isha).

**Best practices:**
- Ask one follow-up if location is missing.

### 4) Qibla Direction
**Use when:**
- The user asks for qibla direction.

**Inputs:**
- User location or city

**Output:**
- Qibla direction in degrees + a simple instruction (“face northeast”, etc.) if available.

### 5) Daily Adhkar / Duas
**Use when:**
- The user asks for morning/evening adhkar, dua for anxiety, forgiveness, guidance, etc.

**Output:**
- Short set of duas/adhkar + how to practice them.

## Tool Choice Rules (Routing)
Best-practice routing logic:
- If the user explicitly asks for Quran/ayah/surah → use Quran MCP (+ optionally local KB for context).
- If the user asks about hadith authenticity / specific collection → prefer local KB hadith sources.
- If the user asks prayer time/qibla → use the dedicated tool.
- Otherwise → local KB RAG.

## Synthesis Rules (Local LLM)
When a local generator is enabled, it should:
- Use only provided evidence.
- Cite sources using `[Source N]`.
- Avoid technical terms (no “RAG”, “BM25”, “embeddings”).
- Ask a clarifying question if evidence is insufficient.
- Use an Islamic tone: greeting, gentle encouragement, and a practical next step.

## Knowledge Upload (RAG Ingestion)
The backend supports uploading new knowledge files into `backend/knowledge/data/`.
- `POST /api/knowledge/upload` supports: `json`, `txt`, `csv`, `pdf`
- `POST /api/knowledge/upload-secure` supports: `pdf`, `txt`, `docx`, `json`, `csv` (5MB limit)

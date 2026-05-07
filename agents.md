# 🕌 Noor - Islamic AI Multi-Agent System

Noor is a premium, local-first Islamic AI assistant designed to provide authentic scholarly guidance through a specialized multi-agent architecture. By combining Hybrid RAG (Retrieval-Augmented Generation) with high-fidelity agent coordination, Noor ensures that every response is grounded in the Quran, Sunnah, and classical Islamic jurisprudence.

## 🏛️ Multi-Agent Architecture

Noor employs a "Council of Scholars" approach, where specialized agents handle different domains of Islamic knowledge. This system is orchestrated by **Imam Hassan**, who ensures a unified and balanced scholarly perspective.

### 🎓 The Scholarly Council

| Scholar | Specialization | Role & Key Tools |
| :--- | :--- | :--- |
| **Sheikh Abdullah** | Quran & Tafsir | Analyzes Ulum al-Quran using `search_local_knowledge` and Quran Foundation MCP. |
| **Sheikha Aisha** | Hadith & Sunnah | Expert in Mustalah al-Hadith; verifies Isnad (chains) and authenticates narrations. |
| **Sheikh Omar** | Fiqh & Shariah | Provides balanced rulings across the four major Madhabs (Hanafi, Maliki, Shafi'i, Hanbali). |
| **Sheikha Fatima** | Spirituality & Dua | Focuses on Tazkiyah (purification of the heart), Adhkar, and authentic Duas. |
| **Imam Hassan** | System Coordinator | Synthesizes wisdom from all scholars and handles general coordination. |

### 🤝 Collaborative Strategies

- **Auto-Routing**: Intelligently detects the query's intent (e.g., "Quran" vs "Prayer Times") and routes it to the most qualified scholar.
- **Collaborative Conference**: A single high-fidelity session where multiple scholars contribute their perspectives simultaneously to provide a comprehensive "Premium" response.
- **Resilience Fallback**: If cloud APIs are unavailable or quotas are hit, the system automatically falls back to a deterministic **Local Knowledge Display** to ensure uninterrupted guidance.

---

## 🛠️ Technical Stack & Indexing

### 🧠 Backend (Python & AgentScope)
- **Framework**: Flask-based API with `AgentScope` for multi-agent orchestration.
- **LLM Strategy**: Multi-provider support (Gemini 2.5 Flash, Claude 3.5 Sonnet) with optimized parameters for scholarly accuracy.
- **Local Inference**: Supports `llama.cpp` for fully private, local-only synthesis.

### 📚 Knowledge Management (Hybrid RAG)
- **Vector Database**: `ChromaDB` for semantic similarity search using `intfloat/multilingual-e5-large` embeddings.
- **Lexical Search**: `BM25` for precise keyword matching (e.g., specific verse numbers or technical Fiqh terms).
- **Indexing Pipeline**: `ProjectIndexer` automatically analyzes the codebase and knowledge data to maintain a graph-based understanding of the system's capabilities.

### 🎨 Frontend (React & Framer Motion)
- **Aesthetic**: "Museum-grade" dark mode UI with gold-primary accents and glassmorphism.
- **Features**: Visual Isnad chains, Qibla compass, Quran audio player, and real-time scholarly status updates.

---

## ✅ Islamic AI Best Practices

The project adheres to a strict set of standards to maintain the sanctity and accuracy of Islamic knowledge:

### 1. Scholarly Accuracy & Determinism
- **Low Temperature (0.2 - 0.4)**: Ensures responses are grounded and deterministic, avoiding "creative" hallucinations in matters of faith.
- **Top-P Optimization**: Balanced to allow for scholarly depth while maintaining strict adherence to retrieved evidence.

### 2. Evidence-Grounded Synthesis
- **Scholarly Structure**: All responses must follow the **4-part structure**:
    1.  **Scholarly Essence**: Core Islamic principle.
    2.  **Detailed Guidance**: Full explanation with citations.
    3.  **Practical Steps**: Actionable advice.
    4.  **Authentic Sources**: List of cited evidence.
- **Local-First Priority**: The system is instructed to use the local Knowledge Base as the primary source of truth before relying on internal model weights.
- **Source Attribution**: All responses MUST include clear citations using standardized formats: `[Quran Surah:Ayah]` or `[Collection #Number]`.

### 3. Respectful Tone & Tarbiyah
- **Gender Awareness**: Dynamically adjusts addressals ("Akhi" / "Ukhti") and focuses on gender-specific Fiqh (e.g., Fiqh of Nisa) when appropriate.
- **Gentle Guidance**: Maintains a warm, encouraging, and non-harsh tone characteristic of Prophetic character (Akhlaq).
- **Engagement**: Always concludes with a practical next step and one short follow-up question to encourage further learning.

### 4. Technical Health & Validation
- **Continuous Validation**: `validate_best_practices.py` monitors the health of the RAG pipeline, API connectivity, and dependency status.
- **Response Validation**: Automated checks for Islamic greetings, source attribution, and relevance scores.

---

## 🚀 Getting Started

To explore the agent system and validation tools:
1. **Validate Health**: `python3 validate_best_practices.py`
2. **Ingest Knowledge**: `python3 backend/knowledge/ingest_best_practices.py`
3. **Start Council**: `./run.sh`

---
*Generated by Antigravity - Project Analysis & Indexing*

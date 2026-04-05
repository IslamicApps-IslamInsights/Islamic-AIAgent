# Islamic AI Agents - System Architecture

This document provides a quick overview of the intelligent agents powering the Islamic AI system. Built on the **AgentScope** framework, these agents combine specialized scholarly depth with advanced RAG (Retrieval-Augmented Generation) capabilities.

> [!TIP]
> For a more detailed breakdown, including citation protocols and technical RAG details, visit the **[Scholarly System Documentation](docs/SCHOLARLY_SYSTEM.md)**.

---

## 🌟 The Single Agent: "Noor"
**File**: [islamic_ai_agent.py](file:///Users/fahadiqbal/Documents/Latest%20Codes/Islamic%20work/Islamic%20AI%20Agent/islamic_ai_agent.py)

Noor is the primary interface for most users. Designed to be a kind, patient, and knowledgeable companion, Noor handles general queries and routes more complex questions to specialized tools.

---

## 👥 The Multi-Agent Scholarly System
**File**: [multi_agent_islamic_system.py](file:///Users/fahadiqbal/Documents/Latest%20Codes/Islamic%20work/Islamic%20AI%20Agent/multi_agent_islamic_system.py)

For users seeking in-depth scholarly consultation, the system activates a team of specialized agents:
- **Sheikh Abdullah**: Quranic Sciences & Tafsir.
- **Sheikha Aisha**: Hadith Authenticity & Sunnah.
- **Sheikh Omar**: Jurisprudence (Fiqh) across all four Madhabs.
- **Sheikha Fatima**: Spirituality & Dua (Heart Guide).
- **Imam Hassan**: The Synthesis Coordinator.

---

## 🔎 The Local Knowledge Base (RAG)
**Module**: [knowledge_base/local_knowledge_tools.py](file:///Users/fahadiqbal/Documents/Latest%20Codes/Islamic%20work/Islamic%20AI%20Agent/knowledge_base/local_knowledge_tools.py)

Ensures that the AI remains grounded in your specifically provided authentic texts.
- **Hybrid Search**: ChromaDB (Semantic) + BM25 (Keyword).
- **Reranking**: Advanced Cross-Encoder prioritization.

---

## 🛠 Integrated Tools Overview
Every agent has access to a `ServiceToolkit` containing:
- **Quranic Engine**: Real-time verses via Al-Quran Cloud.
- **Hadith API**: Direct access to verified Sunnah collections.
- **Prayer & Qibla**: Geospatial calculations via Aladhan API.
- **Halal Checker**: Ingredient analysis based on authentic datasets.
- **Islamic Calendar**: Precision Hijri-Gregorian conversion.

---

For technical setup and API details, please refer to the **[README.md](README.md)**.

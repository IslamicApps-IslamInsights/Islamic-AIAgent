# Islamic AI Agents - System Architecture

This document provides a detailed overview of the intelligent agents powering the Islamic AI system. Built on the **AgentScope** framework, these agents combine specialized scholarly depth with advanced RAG (Retrieval-Augmented Generation) capabilities.

---

## 🌟 The Single Agent: "Noor"
**File**: [islamic_ai_agent.py](file:///Users/fahadiqbal/Documents/Latest%20Codes/Islamic%20work/Islamic%20AI%20Agent/islamic_ai_agent.py)

Noor is the primary interface for most users. Designed to be a kind, patient, and knowledgeable companion, Noor handles general queries and routes more complex questions to specialized tools.

### Key Capabilities
- **Local-First Priority**: Noor is configured to search your local knowledge base before answering from general training.
- **13+ Integrated Tools**: Accesses real-time APIs for Quran, Hadith, Prayer Times, and more.
- **Gender Awareness**: Tailors language and guidance based on user-specified gender.

---

## 👥 The Multi-Agent Scholarly System
**File**: [multi_agent_islamic_system.py](file:///Users/fahadiqbal/Documents/Latest%20Codes/Islamic%20work/Islamic%20AI%20Agent/multi_agent_islamic_system.py)

For users seeking in-depth scholarly consultation, the system activates a team of specialized agents.

### 📖 Sheikh Abdullah (Quran & Tafsir)
- **Role**: Senior Quranic Scientist.
- **Focus**: Provides Uthmani script Arabic text, multiple translations, and synthesis of classical Tafsirs (Ibn Kathir, Tabari).
- **Standards**: Cross-references multiple sources for maximum precision.

### ⭐ Sheikha Aisha (Hadith & Sunnah)
- **Role**: Senior Hadith Authority.
- **Focus**: Authenticates Hadith gradings (Sahih, Hasan) and provides full chains (Isnad) where relevant.
- **Sources**: Primarily draws from Bukhari, Muslim, and the "Six Books."

### ⚖️ Sheikh Omar (Fiqh & Shariah)
- **Role**: Senior Jurisprudence Scholar.
- **Focus**: Presenting views across all four major Madhabs (Hanafi, Maliki, Shafi'i, Hanbali).
- **Specialization**: Addresses modern challenges like medical ethics and Islamic finance.

### 🤲 Sheikha Fatima (Spirituality & Dua)
- **Role**: Heart & Soul Guide.
- **Focus**: Spiritual purification (Tazkiyah), beautiful Arabic Duas with transliteration, and heart-based counseling.
- **Approach**: Warm, compassionate, and focused on divine connection.

### 👨‍🏫 Imam Hassan (The Coordinator)
- **Role**: System Synthesizer.
- **Focus**: Coordinates between the scholars and provides a balanced, comprehensive final response that honors all Islamic sciences.

---

## 🔎 The Local Knowledge Base Agent (The RAG Specialist)
**Module**: [knowledge_base/local_knowledge_tools.py](file:///Users/fahadiqbal/Documents/Latest%20Codes/Islamic%20work/Islamic%20AI%20Agent/knowledge_base/local_knowledge_tools.py)

The RAG (Retrieval-Augmented Generation) agent is the "brain" behind the local document priority. It ensures that the Islamic AI Agent remains grounded in your specifically provided authentic texts.

### Technical Implementation
- **Vector Database**: Uses **ChromaDB** for efficient similarity searching.
- **Embedding Model**: Powered by `intfloat/multilingual-e5-large`. This world-class model provides exceptional support for Arabic, English, Urdu, and many other languages.
- **Logic Chain**:
    1. **Query Processing**: The agent understands the semantic meaning of the user's question.
    2. **Similarity Search**: It retrieves the most relevant chunks from your uploaded PDFs or TXTs.
    3. **Relevance Filtering**: Only results with a high similarity score (>0.3) are used.
    4. **Contextual Synthesis**: The agent incorporates these excerpts into the final response with clear citations of the source file and page.

### Why Local-First?
This agent prevents "LLM Hallucination" by ensuring that if a user uploads a specific Hanafi Fiqh book or a family Islamic guide, the system uses *that* specific text as its primary source of truth, rather than generic Internet data.

---

## 🛠 Integrated Tools Overview
Every agent has access to a `ServiceToolkit` containing specialized functions:
- **Quranic Engine**: Real-time verses via Al-Quran Cloud.
- **Hadith API**: Direct access to verified Sunnah collections.
- **Prayer & Qibla**: Geospatial calculations via Aladhan API.
- **Halal Checker**: Ingredient analysis based on authentic datasets.
- **Islamic Calendar**: Precision Hijri-Gregorian conversion.

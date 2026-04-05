# 🕌 Noor - The Premium Islamic AI Agent

![Noor Logo](file:///Users/fahadiqbal/Documents/Latest%20Codes/Islamic%20work/Islamic%20AI%20Agent/islamic-ai-agent/public/noor-logo.png)

A state-of-the-art, "Museum Grade" scholarly AI companion designed for the modern Muslim. **Noor** combines advanced **Multi-Agent Deliberation** via AgentScope with a world-class **Multilingual RAG (Retrieval-Augmented Generation)** engine to provide authentic, citation-backed Islamic guidance.

---

## 🌟 Vision & Philosophy

Noor is built upon the synthesis of two worlds: **Authentic Tradition** and **Advanced AI**. Our mission is to provide an immersive, compassionate, and scholarly portal to Islamic knowledge while ensuring every response is grounded in primary Quranic and Prophetic sources.

> [!IMPORTANT]
> Noor is a tool for learning and reference. For complex Fiqh rulings or personal religious matters, users are always encouraged to consult with qualified local scholars.

---

## 🚀 Key Features

### 🏛️ Museum-Grade Scholarly Interface
- **Premium Aesthetics**: Immersive, glassmorphic UI with refined Arabic typography (Amiri & Inter).
- **Sanctuary Greeting**: A serene entry experience with interactive scholarly suggestion chips.
- **Evidence Boxes**: Professional rendering of Quranic verses and Hadiths with formal citations.

### 👥 Specialized Scholarly Team
- **Sheikh Abdullah**: Quranic Sciences & Tafsir.
- **Sheikha Aisha**: Hadith Authenticity & Sunnah.
- **Sheikh Omar**: Jurisprudence (Fiqh) across all four major Madhabs.
- **Sheikha Fatima**: Spirituality (Tazkiyah) and heart-based counseling.
- **Imam Hassan**: The Synthesis Coordinator for unified guidance.

### 🎯 Pro-Grade Knowledge Engine
- **Hybrid Search**: Combining semantic ChromaDB (vector) with exact-match BM25 (keyword).
- **Flash Reranking**: Advanced Cross-Encoder reranking for maximum precision.
- **Local-First Priority**: Always searches your private authentic library before general training.
- **Multimodal Mastery**: Process voice, images, and documents with Gemini 2.0 Flash level intelligence.

---

## 📂 Project Structure

```text
├── docs/                      # Comprehensive Documentation Suite
├── islamic-ai-agent/          # React (Vite) Frontend
├── knowledge_base/            # RAG Engine & Local Store
├── multi_agent_islamic_system.py # Specialized Scholarly Backend
├── islamic_ai_agent.py        # Single Agent Implementation
├── web_api.py                 # Unified Flask Bridge
└── llm_provider.py            # Gemini & AgentScope Manager
```

---

## 📚 Documentation Deep Dives

- **[Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)**: How everything connects.
- **[Scholarly System](docs/SCHOLARLY_SYSTEM.md)**: Deep dive into the agents and citation standards.
- **[Knowledge Base (RAG)](docs/KNOWLEDGE_BASE_TECHNICAL.md)**: Technical details on the vector store and hybrid search.
- **[API Reference](docs/API_REFERENCE.md)**: Documentation for backend endpoints.
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)**: Setup, environments, and contributing.

---

## 🛠️ Quick Start

### 1. Prerequisites
- **Python 3.9+** (3.10+ recommended)
- **Node.js 18+**
- **Google Gemini API Key**

### 2. Environment Setup
Create a `.env` file in the root:
```env
GOOGLE_API_KEY=your_gemini_key_here
```

### 3. Launch the Stack
```bash
# Start the Backend (Port 5010)
python3 web_api.py

# Start the Frontend (Port 3001)
cd islamic-ai-agent
npm install
npm run dev -- --port 3001
```

---

*Built with ❤️ for the Ummah by IslamInsights.com*

# 🕌 Islamic AI Agent - World-Class Spiritual Assistant

A comprehensive, AgentScope-powered Islamic AI system designed to be an authentic companion for the modern Muslim. Featuring a multi-agent scholarly system, local-first RAG (Retrieval-Augmented Generation), and 13+ specialized religious tools.

---

## 🌟 Key Features

### 🧠 Intelligent Islamic Agents
- **Local-First Knowledge (RAG)**: Prioritizes your uploaded Islamic documents (PDFs, TXTs) for authoritative, citation-backed answers.
- **Multi-Agent Scholarly Team**: Specialized agents for Quran, Hadith, Fiqh, and Spirituality.
- **Gender-Specific Guidance**: Tailored religious advice that respects the nuances of Fiqh for both men and women.

### 🛠 World-Class Religious Tools
- **Quranic Engine**: Arabic text, transliteration, and multiple Tafsirs.
- **Hadith Explorer**: Verified Sahih/Hasan collections with authentic gradings.
- **Prayer & Qibla**: Modern, GPS-based accurate calculations and visual compass.
- **Halal Checker**: Ingredient and E-code analysis for dietary guidance.
- **Interactive Guides**: Step-by-step Hajj & Umrah assistance and Adhkar Hub.
- **Hijri Dashboard**: Full Islamic calendar with major upcoming events.

### 🎨 Premium User Experience
- **Modern Web Interface**: Clean, aesthetic design with Arabic typography and glassmorphism.
- **Voice Integration**: Voice-to-text for natural Islamic queries.
- **Knowledge Ingestion**: Simple drag-and-drop dashboard to train the agent on your own authentic texts.
- **Trending Insights**: View anonymized local query trends within the community.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- OpenAI API Key

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd "Islamic AI Agent"

# Setup virtual environment
./setup_venv.sh
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_api_key_here
```

### 4. Running the System
```bash
# Start the Web API and UI
python3 web_api.py --port 8003
```
Open your browser and navigate to `http://localhost:8003`.

---

## 📚 Documentation
- **[Agents Architecture](agents.md)**: Detailed breakdown of the AI systems and the RAG engine.
- **[Dynamic Knowledge Guide](DYNAMIC_KNOWLEDGE_GUIDE.md)**: How to manage and ingest local Islamic documents.
- **[Web UI Guide](WEB_UI_GUIDE.md)**: Features overview for the frontend.

---

## 🛠 Tech Stack
- **Framework**: [AgentScope](https://github.com/modelscope/agentscope)
- **RAG Engine**: LangChain, ChromaDB, HuggingFace (multilingual-e5-large)
- **Backend**: Python, Flask
- **Frontend**: HTML5, Vanilla JS, Premium CSS
- **APIs**: Al-Quran Cloud, Aladhan API, Sunnah.com

---

## 🤲 Philosophy
Our mission is to provide **authentic, accessible, and high-quality** Islamic knowledge using state-of-the-art AI, while always emphasizing the importance of consulting qualified scholars for complex religious matters.

---
*Built with ❤️ for the Ummah by IslamInsights.com*

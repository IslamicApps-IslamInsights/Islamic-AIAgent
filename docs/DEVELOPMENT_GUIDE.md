# Development Guide - Islamic AI Agent

This guide provides the necessary information for developers and scholars to set up, contribute, and maintain the **Noor** Islamic AI Agent project.

---

## 🏗️ Environmental Configuration

### 1. Requirements
- **Python 3.9+** (3.10+ recommended for optimized library compatibility).
- **Node.js 18+** (for Vite React frontend).
- **Git** for version control.

### 2. Environment Variables (.env)
The project requires several environment variables for core functionality. Create a file named `.env` in the root directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
# Optional: OpenAI API Key (if switching models)
# OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🛠️ Local Development Setup

### 1. Backend (Python/Flask)
```bash
# Set up a virtual environment (MacOS/Linux)
./setup_venv.sh
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask API Gateway (Port 5010)
python3 web_api.py
```

### 2. Frontend (React/Vite)
```bash
# Navigate to the frontend directory
cd islamic-ai-agent

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

To update the behavior or system prompts of the scholarly agents:
1.  **Single Agent**: Modify `islamic_ai_agent.py`.
2.  **Multi-Agent Team**: Modify `multi_agent_islamic_system.py`.
3.  **Role System Prompts**: Look for the `SYSTEM_PROMPT` variable within each respective file to refine scholarly standards.

---

## 🤝 Contribution Workflow
1.  **Ingest New Data**: Place PDFs or TXTs in `knowledge_base/data/` and run `python3 knowledge_base/ingest_data.py`.
2.  **Add Tools**: Extend `enhanced_islamic_tools.py` with new religious APIs or Geospatial logic.
3.  **Refine Citations**: Update the `SOURCE_MAPPING` in `local_knowledge_tools.py` if adding new primary sources.

---

> [!WARNING]
> Always run `npm install` and `pip install -r requirements.txt` after pulling updates, as dependencies are frequently optimized for the M-series Mac architecture.

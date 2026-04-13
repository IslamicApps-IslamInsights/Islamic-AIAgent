# 🌟 Islamic AI Agent with AgentScope

A comprehensive Islamic AI assistant built using AgentScope framework, providing authentic Islamic knowledge, prayer times, Qibla direction, and spiritual guidance.

## 🚀 Features

### 🤖 **Single Agent Mode**
- **Noor** - Intelligent Islamic AI assistant
- Real-time prayer times and Qibla direction
- Quran verses with Arabic text and translations
- Authentic Hadith collections
- Islamic calendar and Hijri date conversion
- Duas for various occasions
- Comprehensive Islamic guidance

### 👥 **Multi-Agent System**
- **Sheikh Abdullah** - Quran & Tafsir specialist
- **Sheikh Aisha** - Hadith & Sunnah expert
- **Sheikh Omar** - Fiqh & Islamic Law scholar
- **Sheikh Fatima** - Spiritual guidance & Duas
- **Imam Hassan** - General coordinator

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- OpenAI API key (or other LLM provider)

### Step 1: Setup Environment
```bash
# Run the setup script
python agentscope_setup.py
```

### Step 2: Configure API Keys
Edit the `.env` file and add your API keys:
```env
OPENAI_API_KEY=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
```

### Step 3: Install Dependencies
```bash
pip install agentscope requests python-dateutil geopy hijri-converter openai python-dotenv
```

## 🎯 Usage

### Single Agent Mode
```bash
python islamic_ai_agent.py
```

**Example Interactions:**
- "Show me Surah Al-Fatiha"
- "What are today's prayer times?" (requires location)
- "Tell me a hadith about kindness"
- "What's a good morning dua?"
- "What's the current Hijri date?"
- "How do I perform Wudu?"

### Multi-Agent System
```bash
python multi_agent_islamic_system.py
```

**Modes Available:**
1. **Auto-routing**: Questions automatically routed to appropriate specialist
2. **Collaborative Consultation**: Multiple specialists provide input
3. **Group Discussion**: Scholars discuss topics together

## 🛠️ Available Tools

### Islamic Knowledge Tools
- `get_quran_verse(verse_name)` - Quran verses with Arabic & translation
- `get_hadith(topic)` - Authentic Hadith on specific topics
- `get_dua(occasion)` - Duas for morning, evening, etc.
- `get_islamic_guidance(topic)` - Guidance on Islamic topics

### Location-Based Tools
- `get_prayer_times(latitude, longitude)` - Accurate prayer times
- `get_qibla_direction(latitude, longitude)` - Qibla direction calculation

### Calendar Tools
- `get_hijri_date()` - Current Hijri date and Islamic events

## 🌟 Key Advantages of AgentScope

### 🔍 **Transparency**
- Full control over prompts and API calls
- Visible tool usage and decision making
- No hidden magic or deep encapsulation

### 🛠️ **Agentic Tools**
- Islamic knowledge base integration
- Real-time API calls for prayer times
- Location-based services

### 🧠 **Memory Management**
- Conversation context preservation
- User preference learning
- Long-term memory for personalization

### 🎯 **Real-time Steering**
- Handle interruptions gracefully
- Dynamic response adjustment
- Interactive conversation flow

### 🔄 **Model Agnostic**
- Works with OpenAI, Claude, local models
- Easy to switch between providers
- Consistent interface across models

## 📚 Example Conversations

### Basic Islamic Knowledge
```
User: "What are the five pillars of Islam?"
Noor: "🕌 The Five Pillars of Islam are:
1. Shahada (Declaration of Faith)
2. Salah (Prayer) - Five daily prayers
3. Zakat (Charity) - 2.5% annually
4. Sawm (Fasting) - During Ramadan
5. Hajj (Pilgrimage) - Once if able
These form the foundation of Islamic practice."
```

### Quran Verses
```
User: "Show me Surah Al-Fatiha"
Sheikh Abdullah: "📖 Surah Al-Fatiha (The Opening):

Arabic:
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ...

Translation:
In the name of Allah, the Entirely Merciful..."
```

### Prayer Times
```
User: "What are today's prayer times?"
Sheikh Omar: "🕐 Today's Prayer Times:
🌅 Fajr: 5:30 AM
☀️ Dhuhr: 12:45 PM
🌤️ Asr: 4:15 PM
🌅 Maghrib: 6:30 PM
🌙 Isha: 8:00 PM
📍 Location-based times for your area"
```

## 🔧 Customization

### Adding New Tools
```python
def custom_islamic_tool(parameter: str) -> str:
    """Your custom Islamic tool"""
    return "Custom response"

# Register with toolkit
toolkit.register_tool_function(custom_islamic_tool)
```

### Custom Agent Prompts
```python
custom_prompt = """You are a specialized Islamic AI for [specific purpose].
Focus on [specific area] and provide [specific type of guidance]."""

agent = ReActAgent(
    name="CustomAgent",
    sys_prompt=custom_prompt,
    # ... other parameters
)
```

### Different LLM Providers
```python
# For Claude
from agentscope.model import AnthropicChatModel
model = AnthropicChatModel(api_key="your_key")

# For local models
from agentscope.model import OllamaChatModel
model = OllamaChatModel(model_name="llama2")
```

## 🎯 Advanced Features

### Multi-Agent Collaboration
```python
# Collaborative consultation
await system.collaborative_consultation("What does Islam say about environmental protection?")

# Group discussion
await system.group_discussion()
```

### Memory and Context
```python
# Agents remember conversation context
# User preferences are learned over time
# Long-term memory for personalized responses
```

### Real-time Steering
```python
# Handle interruptions during responses
# Dynamic conversation flow
# User can guide conversation direction
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add Islamic knowledge or tools
4. Test with AgentScope framework
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **AgentScope Team** - For the excellent framework
- **Islamic Scholars** - For authentic knowledge sources
- **TheIslamInsights.com** - For Islamic guidance and resources
- **Muslim Community** - For feedback and support

## 📞 Support

For questions or support:
- Visit: TheIslamInsights.com
- Email: support@theislaminsights.com
- Issues: GitHub Issues page

---

**May Allah bless this project and make it beneficial for the Muslim Ummah. Ameen! 🤲**

*"And whoever seeks a path of knowledge, Allah will make easy for him a path to Paradise."* - Prophet Muhammad (ﷺ)

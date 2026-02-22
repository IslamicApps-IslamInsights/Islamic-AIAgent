"""
Islamic AI Agent using AgentScope
A comprehensive Islamic AI assistant with knowledge base and real-time features
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

import agentscope
# AgentScope imports
from agentscope.agents import ReActAgent, UserAgent
from agentscope.models import OpenAIChatWrapper
from agentscope.formatters import OpenAIFormatter
from agentscope.memory import TemporaryMemory
from agentscope.service import ServiceToolkit
from agentscope.message import Msg

# Import our enhanced Islamic tools with dynamic knowledge base
from enhanced_islamic_tools import (
    get_quran_verse,
    get_hadith,
    get_dua,
    get_prayer_times,
    get_qibla_direction,
    get_hijri_date,
    get_islamic_guidance,
    search_islamic_content,
    get_daily_islamic_content,
    get_surah_info
)

# Load environment variables
load_dotenv()

class IslamicAIAgent:
    """Islamic AI Agent powered by AgentScope"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Islamic AI Agent
        
        Args:
            api_key: OpenAI API key (optional, can be set in .env file)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file or pass as parameter.")
        
        # Initialize Agentscope global context
        agentscope.init(model_configs=[{
            "config_name": "openai_cfg",
            "model_type": "openai_chat",
            "model_name": "gpt-4o-mini",
            "api_key": self.api_key
        }])
        
        self.setup_agent()
    
    def setup_agent(self):
        """Set up the AgentScope Islamic AI agent"""
        
        # Create toolkit with Islamic tools
        self.toolkit = ServiceToolkit()
        
        # Register enhanced Islamic knowledge tools with dynamic API integration
        self.toolkit.add(get_quran_verse)
        self.toolkit.add(get_hadith)
        self.toolkit.add(get_dua)
        self.toolkit.add(get_prayer_times)
        self.toolkit.add(get_qibla_direction)
        self.toolkit.add(get_hijri_date)
        self.toolkit.add(get_islamic_guidance)
        self.toolkit.add(search_islamic_content)
        self.toolkit.add(get_daily_islamic_content)
        self.toolkit.add(get_surah_info)
        
        # Islamic AI system prompt
        system_prompt = """بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

You are an Islamic AI Assistant from TheIslamInsights.com, designed to provide authentic Islamic guidance based on the Quran and Sunnah. Your name is "Noor" (meaning "Light" in Arabic).

**Your Purpose:**
- Provide accurate Islamic knowledge and guidance
- Help Muslims with their daily religious practices
- Share authentic Hadith and Quran verses
- Assist with prayer times, Qibla direction, and Islamic calendar
- Offer spiritual guidance based on Islamic teachings

**Your Capabilities:**
- Access to Quran verses with Arabic text and translations
- Authentic Hadith collections from Sahih sources
- Prayer times calculation for any location
- Qibla direction calculation
- Islamic calendar and Hijri date conversion
- Duas for various occasions
- Islamic guidance on worship, fasting, charity, etc.

**Guidelines:**
1. Always provide authentic information based on Quran and Sunnah
2. Include Arabic text when sharing Quran verses or Duas
3. Cite sources for Hadith (e.g., Sahih Bukhari, Sahih Muslim)
4. Be respectful and use Islamic greetings
5. For complex religious matters, recommend consulting qualified scholars
6. Use tools to provide accurate prayer times and Qibla directions
7. Be helpful, patient, and kind in all interactions

**Available Tools (All with Dynamic API Integration):**
- get_quran_verse(verse_reference): Get Quran verses with Arabic and translation from Al-Quran Cloud API
- get_hadith(topic): Get authentic Hadith from verified collections via Hadith APIs
- get_dua(occasion): Get authentic Duas for various occasions
- get_prayer_times(latitude, longitude): Get accurate prayer times via Aladhan API
- get_qibla_direction(latitude, longitude): Calculate precise Qibla direction
- get_hijri_date(): Get current accurate Hijri date
- get_islamic_guidance(topic): Get comprehensive guidance from Quran and Hadith APIs
- search_islamic_content(query): Search both Quran and Hadith collections dynamically
- get_daily_islamic_content(): Get daily verse and hadith from authentic sources
- get_surah_info(surah_name_or_number): Get detailed information about Quranic chapters

**Response Style:**
- Start with "Assalamu Alaikum wa Rahmatullahi wa Barakatuh" for new conversations
- Use appropriate Islamic phrases (InshaAllah, MashaAllah, etc.)
- Format responses clearly with emojis and structure
- End with "May Allah guide us all. Ameen! 🤲"

Remember: You are here to serve Allah by helping His servants learn and practice Islam correctly."""

        # Create the Islamic AI agent
        self.agent = ReActAgent(
            name="Noor",
            model_config_name="openai_cfg",
            service_toolkit=self.toolkit,
            sys_prompt=system_prompt,
        )
        
        # Create user agent
        self.user = UserAgent(name="user")
        
        print("🌟 Islamic AI Agent 'Noor' is ready!")
        print("💬 Type 'exit' to end the conversation")
        print("🤲 May Allah bless your learning journey!")
    
    def _get_dynamic_welcome_message(self):
        """Get dynamic welcome message from configuration"""
        try:
            from islamic_config import islamic_config
            agent_name = islamic_config.get_agent_name('single')
            return f"""بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

Assalamu Alaikum wa Rahmatullahi wa Barakatuh! 🕌

Welcome to your Islamic AI Assistant. I'm {agent_name}, here to provide authentic Islamic guidance based on Quran and Sunnah.

✨ **How I can help:**
📖 Quranic verses with Arabic text & explanations
🕐 Prayer times & Qibla direction for your location
🤲 Duas from Quran & Sunnah with transliterations
⚖️ Fiqh rulings & Islamic law guidance
🌙 Islamic calendar & current Hijri date
📚 Authentic Hadith collections
💡 Daily Islamic reminders & spiritual guidance

**Try asking me:**
• "Show me Surah Al-Fatiha"
• "What are today's prayer times?" (I'll need your location)
• "Tell me a hadith about kindness"
• "What's a good morning dua?"
• "What's the current Hijri date?"

*Note: For complex religious matters, consult qualified Islamic scholars.*

How may I assist you in your Islamic journey today? 🌟"""
        except ImportError:
            # Fallback if config not available
            return """بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

Assalamu Alaikum wa Rahmatullahi wa Barakatuh! 🕌

Welcome to your Islamic AI Assistant. I'm here to provide authentic Islamic guidance based on Quran and Sunnah.

How may I assist you in your Islamic journey today? 🌟"""
    
    async def start_conversation(self):
        """Start the conversation with the Islamic AI agent"""
        
        # Welcome message
        welcome_msg = Msg(
            name="Noor",
            content=self._get_dynamic_welcome_message(),
            role="assistant"
        )
        
        msg = welcome_msg
        
        while True:
            try:
                # Agent responds
                msg = await self.agent(msg)
                
                # User input
                msg = await self.user(msg)
                
                # Check for exit
                if msg.get_text_content().lower() in ['exit', 'quit', 'bye']:
                    farewell_msg = Msg(
                        name="Noor",
                        content="""جزاك الله خيراً for using the Islamic AI Assistant! 🌟

May Allah bless you with knowledge, guidance, and righteousness.
May your prayers be accepted and your faith strengthened.

وَفِي ذَٰلِكَ فَلْيَتَنَافَسِ الْمُتَنَافِسُونَ
"And for this let the competitors compete." (Quran 83:26)

Barakallahu feeki! Until we meet again, Assalamu Alaikum wa Rahmatullahi wa Barakatuh! 🤲

Visit TheIslamInsights.com for more Islamic knowledge and guidance.""",
                        role="assistant"
                    )
                    print(f"\n🌟 {farewell_msg.content}")
                    break
                    
            except KeyboardInterrupt:
                print("\n\n🤲 Conversation ended. May Allah bless you!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'exit' to quit.")

def main():
    """Main function to run the Islamic AI Agent"""
    try:
        # Create and start the Islamic AI Agent
        islamic_agent = IslamicAIAgent()
        
        # Run the conversation
        asyncio.run(islamic_agent.start_conversation())
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your .env file and ensure OPENAI_API_KEY is set.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()

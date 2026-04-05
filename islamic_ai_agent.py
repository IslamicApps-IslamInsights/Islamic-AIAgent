"""
Islamic AI Agent using AgentScope
A comprehensive Islamic AI assistant with knowledge base and real-time features
"""

import os
import asyncio
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Agentscope imports will be deferred

# Import our enhanced Islamic tools with dynamic knowledge base
# Tool imports will be deferred

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
      
        # Agentscope global context will be initialized in setup_agent
        import agentscope
        
        self.model_params = None
        
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.agent = None
        self.user = None
        self.toolkit = None
        self.model_config = None
        self.formatter = None
        self.setup_agent()
    
    def setup_agent(self):
        """Set up the AgentScope Islamic AI agent"""
        
        # Create toolkit with Islamic tools
        print("  [Noor] Loading AgentScope components...")
        from agentscope.agents import ReActAgent
        from agentscope.service import ServiceToolkit as Toolkit
        from agentscope.formatters import GeminiFormatter as GeminiChatFormatter
        print("  [Noor] Setting up toolkit...")
        self.toolkit = Toolkit()
        
        formatter = GeminiChatFormatter()
        
        # Lazy imports for tools
        from enhanced_islamic_tools import (
            get_quran_verse, get_hadith, get_dua, get_prayer_times,
            get_qibla_direction, get_hijri_date, get_islamic_guidance,
            search_islamic_content, get_daily_islamic_content, get_surah_info,
            get_name_of_allah, get_adhkar, get_hajj_umrah_guidance,
            check_halal_guidance
        )
        
        # Register enhanced Islamic knowledge tools with dynamic API integration
        print("  [Noor] Registering tool functions...")
        from llm_provider import register_islamic_tool
        for tool_fn in [
            get_quran_verse, get_hadith, get_dua, get_prayer_times,
            get_qibla_direction, get_hijri_date, get_islamic_guidance,
            search_islamic_content, get_daily_islamic_content, get_surah_info,
            get_name_of_allah, get_adhkar, get_hajj_umrah_guidance,
            check_halal_guidance
        ]:
            register_islamic_tool(self.toolkit, tool_fn)
        print("  [Noor] Tool functions registered.")
        
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
        print("  [Noor] Initializing agentscope agents...")
        from agentscope.agents import ReActAgent, UserAgent
        
        # Initialize AgentScope via unified provider
        from llm_provider import get_agentscope_model
        model_config_name = get_agentscope_model()
        print(f"  [Noor] Model config registered")
            
        self.agent = ReActAgent(
            name="Noor",
            model_config_name=model_config_name, 
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
        from agentscope.message import Msg
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
                from agentscope.message import Msg
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

    def process_message_with_tools(self, message: str, user_gender: str = "not_specified", latitude: float = None, longitude: float = None) -> str:
        """
        Process message with local-first knowledge priority and AI synthesis.
        """
        # 1. Local Knowledge Base Priority (RAG)
        from knowledge_base.local_knowledge_tools import search_local_knowledge
        local_context = search_local_knowledge(message)
        has_local_data = local_context and "❌ No relevant information" not in local_context and "❌ Local knowledge base" not in local_context

        # 1.5 Real-time Metadata Injection
        now = datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Try to get Hijri date for the prompt
        try:
            from enhanced_islamic_tools import get_hijri_date
            hijri_info = get_hijri_date(latitude=latitude, longitude=longitude)
        except Exception:
            hijri_info = "Hijri date unavailable"

        context_str = f"LOCAL KNOWLEDGE CONTEXT:\n{local_context}\n" if has_local_data else "No specific local documents found for this query."
        
        synthesis_prompt = f"""
        REAL-TIME METADATA:
        - Current Gregorian Date/Time: {current_time_str}
        - Current Hijri/Islamic Date: {hijri_info}
        - User Location: {f'Lat: {latitude}, Lng: {longitude}' if latitude else 'Not provided'}
        
        User Message: {message}
        User Gender: {user_gender}
        
        {context_str}
        
        INSTRUCTIONS:
        1. If local knowledge context is provided, prioritize it and synthesize a beautiful, scholarly response.
        2. **GROUND TRUTH PRIORITY**: If the context contains 'ISLAMIC GROUND TRUTH ESSENTIALS', treat it as the absolute source of truth.
        3. **FORMATTING RULES (STRICT)**:
           - **NEVER** use '###' or any other markdown headers.
           - **NEVER** use the '>' blockquote symbol.
           - **NEVER** use '*' for bullet points; use '•' (bullets) or '1.' (numbered lists) instead.
           - **NEVER** use technical markers like '<<', '>>', or raw JSON keys.
           - Use ****Bold text**** ONLY for important section titles or emphasis.
           - Use clear double-paragraph breaks for readability.
           - Ensure the response is "Best Presentable", "Premium", and "User Centric".
        4. ALWAYS maintain the "Noor" persona (kind, patient, scholarly).
        5. Cite your sources clearly using the **Scholarly Reference** provided in the context (e.g., **The Holy Quran [17:78]**). Do not use technical filenames like .txt or .json.
        6. If you cannot find authentic information, say so respectfully.
        """
        
        try:
            # Use native GenAI SDK for more robust synthesis (bypasses AgentScope 404 issues)
            from google import genai
            native_client = genai.Client(api_key=self.api_key)
            native_model = "models/gemini-flash-latest"
            
            response = native_client.models.generate_content(
                model=native_model,
                contents=synthesis_prompt,
                config={
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "max_output_tokens": 2048,
                }
            )
            
            if response and response.text:
                return response.text
            else:
                return "🎓 Scholar Response Synthesized: (No content generated)"
        except Exception as e:
            print(f"Error in native AI synthesis: {e}")
            # Fallback to local context if even native fails
            if has_local_data:
                return local_context
            return "Assalamu Alaikum. I encountered an error while processing your request. Please try again. 🤲"

    def process_multimodal_message(self, message: str, file_data: str, mime_type: str, user_gender: str = 'not_specified', latitude: float = None, longitude: float = None) -> str:
        """
        Process a message with an attached file or audio using Gemini's multimodal capabilities
        """
        import base64
        from google import genai
        from google.genai import types
        
        # Get dynamic context (time, hijri, etc.)
        current_time = datetime.now()
        current_time_str = current_time.strftime("%A, %B %d, %Y (%I:%M %p)")
        
        # Determine if it's audio or document
        is_audio = mime_type.startswith('audio/')
        file_type_desc = "Audio Recording" if is_audio else "Attached Document"
        
        synthesis_prompt = f"""
        You are "Noor," a kind, patient, and highly knowledgeable Islamic AI Scholar.
        A user has sent you a message along with an {file_type_desc}.
        
        CONTEXT:
        - Current Gregorian Date/Time: {current_time_str}
        - User Message: {message}
        - User Gender: {user_gender}
        - User Location: {f'Lat: {latitude}, Lng: {longitude}' if latitude else 'Not provided'}
        
        INSTRUCTIONS:
        1. Analyze the attached {file_type_desc} carefully in the context of Islamic knowledge.
        2. If it is an audio recording, listen for the user's question or recitation and provide scholarly guidance.
        3. If it is a document (PDF/Image), extract relevant Islamic text or concepts and provide insights.
        4. **FORMATTING RULES (STRICT)**:
           - **NEVER** use '###' or any other markdown headers.
           - **NEVER** use the '>' blockquote symbol.
           - **NEVER** use '*' for bullet points; use '•' instead.
           - Use ****Bold text**** ONLY for emphasis.
        5. ALWAYS maintain the "Noor" persona.
        """
        
        try:
            native_client = genai.Client(api_key=self.api_key)
            native_model = "models/gemini-1.5-flash" # Use 1.5 for multimodal
            
            # Prepare multimodal content
            # file_data is expected to be base64 string
            raw_data = base64.b64decode(file_data)
            
            content_parts = [
                synthesis_prompt,
                types.Part(inline_data=types.Blob(data=raw_data, mime_type=mime_type))
            ]
            
            response = native_client.models.generate_content(
                model="models/gemini-flash-latest",
                contents=content_parts,
                config={
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "max_output_tokens": 2048,
                }
            )
            
            if response and response.text:
                return response.text
            else:
                return f"🎓 Scholar Analysis: I have processed your {file_type_desc} but could not generate a text response. Please try describing it."
        except Exception as e:
            print(f"Error in multimodal synthesis: {e}")
            return f"Assalamu Alaikum. I encountered an error while analyzing your {file_type_desc}. Please ensure the file format is supported. 🤲"

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

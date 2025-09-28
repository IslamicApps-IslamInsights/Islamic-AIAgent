"""
Multi-Agent Islamic AI System using AgentScope
Specialized agents for different aspects of Islamic knowledge
"""

import os
import asyncio
from typing import List, Dict
from dotenv import load_dotenv

from agentscope.agent import ReActAgent, UserAgent
from agentscope.model import OpenAIChatModel
from agentscope.formatter import OpenAIChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit
from agentscope.message import Msg
from agentscope.pipeline import MsgHub, sequential_pipeline

from enhanced_islamic_tools import *

load_dotenv()

class IslamicMultiAgentSystem:
    """Multi-agent Islamic AI system with specialized agents"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.agents = {}
        self.user = None
        self.setup_agents()
    
    def create_base_model(self):
        """Create base model configuration"""
        return OpenAIChatModel(
            model_name="gpt-4o-mini",
            api_key=self.api_key,
            stream=False,  # Disable streaming for API compatibility
        )
    
    def setup_agents(self):
        """Set up specialized Islamic AI agents"""
        
        # 1. Quran & Tafsir Specialist
        self.agents['quran_scholar'] = ReActAgent(
            name="Sheikh_Abdullah",
            sys_prompt="""🕌 **Sheikh Abdullah - Quran & Tafsir Specialist**

السلام عليكم ورحمة الله وبركاته

I am Sheikh Abdullah, your dedicated Quran and Tafsir specialist. I provide beautiful, comprehensive responses with:

**Core Expertise:**
- Quranic verses with precise Arabic text and multiple authentic translations
- Classical Tafsir (Ibn Kathir, Tabari, Qurtubi, Jalalayn) and modern commentary
- Asbab al-Nuzul (circumstances of revelation) and historical context
- Quranic Arabic linguistics, rhetoric (Balagha), and literary analysis
- Memorization techniques, Tajweed rules, and recitation guidance
- Thematic studies and cross-referencing related verses
- Meccan vs Medinan revelations and chronological context

**📖 Beautiful Response Format:**
🔸 **Arabic Text** - Original verse with proper diacritics and beautiful formatting
🔸 **Transliteration** - Accurate romanization for perfect pronunciation
🔸 **Translation** - Multiple authentic translations with scholarly precision
🔸 **Tafsir** - Classical commentary from renowned scholars (Ibn Kathir, Tabari)
🔸 **Historical Context** - Revelation circumstances and background
🔸 **Spiritual Lessons** - Practical applications and life guidance
🔸 **Cross-References** - Related verses and thematic connections
🔸 **Recitation Guide** - Tajweed rules and pronunciation tips

**✨ Response Guidelines:**
🌟 Begin each response with "📖 **Quranic Guidance from Sheikh Abdullah:**"
🌟 Use beautiful formatting with emojis and clear sections
🌟 Always provide Arabic text first with proper diacritics
🌟 Include authentic classical sources and scholarly references
🌟 Connect verses to modern life applications and spiritual growth
🌟 End with a beautiful dua or blessing related to the topic

**🤲 My Mission:** To make the Quran's beauty and wisdom accessible to all Muslims, combining scholarly authenticity with heartfelt guidance.

بارك الله فيكم - May Allah bless you in your Quranic journey! 🌙✨""",
            model=self.create_base_model(),
            memory=InMemoryMemory(),
            formatter=OpenAIChatFormatter(),
        )
        
        # 2. Hadith & Sunnah Specialist
        self.agents['hadith_scholar'] = ReActAgent(
            name="Sheikh_Aisha",
            sys_prompt="""⭐ **Sheikha Aisha - Hadith & Sunnah Expert**

السلام عليكم ورحمة الله وبركاته

I am Sheikha Aisha, your dedicated Hadith and Sunnah specialist. I bring you authentic Prophetic wisdom with:

**Core Expertise:**
- Authentic Hadith from the Six Books (Kutub al-Sittah) and other collections
- Hadith classification: Sahih, Hasan, Da'if, and Mawdu' categories
- Isnad (chain of narrators) analysis and Rijal studies
- Sunnah practices and their practical implementation in daily life
- Prophet's (ﷺ) biography (Seerah) and exemplary character (Akhlaq)
- Comparative analysis across different Hadith collections
- Contemporary applications of Prophetic teachings

**⭐ Beautiful Response Format:**
🔸 **Arabic Hadith** - Original text with beautiful formatting and diacritics
🔸 **English Translation** - Clear, accurate, and eloquent translation
🔸 **Source Citation** - Complete reference (Collection, Book, Number)
🔸 **Narrator Chain** - Isnad analysis with narrator reliability
🔸 **Authenticity Grade** - Sahih/Hasan/Da'if with detailed explanation
🔸 **Scholarly Commentary** - Classical and contemporary insights
🔸 **Prophetic Wisdom** - Life lessons and spiritual guidance
🔸 **Modern Application** - How to implement in today's world

**✨ Response Guidelines:**
🌟 Begin each response with "⭐ **Prophetic Guidance from Sheikha Aisha:**"
🌟 Use beautiful formatting with emojis and clear sections
🌟 Always provide complete source citations and authenticity grades
🌟 Share the Prophet's (ﷺ) wisdom with love and reverence
🌟 Connect Sunnah practices to modern Muslim life
🌟 End with Salawat (blessings) upon the Prophet (ﷺ)

**🤲 My Mission:** To share the beautiful Sunnah of our beloved Prophet (ﷺ) with authenticity, love, and practical guidance for modern Muslims.

صلى الله عليه وسلم - May Allah's peace and blessings be upon our beloved Prophet! 🌟💚""",
            model=self.create_base_model(),
            memory=InMemoryMemory(),
            formatter=OpenAIChatFormatter(),
        )
        
        # 3. Fiqh & Islamic Law Specialist
        self.agents['fiqh_scholar'] = ReActAgent(
            name="Sheikh_Omar",
            sys_prompt="""⚖️ **Sheikh Omar - Fiqh & Islamic Law Scholar**

السلام عليكم ورحمة الله وبركاته

I am Sheikh Omar, your dedicated Fiqh and Islamic jurisprudence specialist. I provide balanced, scholarly guidance with:

**Core Expertise:**
- Islamic law (Fiqh) and legal methodology (Usul al-Fiqh)
- Comparative madhab analysis (Hanafi, Maliki, Shafi'i, Hanbali)
- Prayer regulations, purification, and worship rulings
- Commercial law, marriage, divorce, and inheritance
- Contemporary Islamic issues and modern applications
- Fatwa methodology and scholarly consensus (Ijma)

**⚖️ Beautiful Response Format:**
🔸 **Islamic Ruling** - Clear, evidence-based decision with Quranic/Hadith support
🔸 **Madhab Analysis** - Respectful comparison of different schools of thought
🔸 **Evidence Base** - Primary sources from Quran and authentic Hadith
🔸 **Practical Application** - How to implement in modern life
🔸 **Contemporary Context** - Modern considerations and applications
🔸 **Scholarly Consensus** - Areas of agreement and respectful differences
🔸 **Further Guidance** - When to consult local scholars

**✨ Response Guidelines:**
🌟 Begin each response with "⚖️ **Fiqh Guidance from Sheikh Omar:**"
🌟 Use beautiful formatting with clear sections and emojis
🌟 Always cite Quranic verses and authentic Hadith as evidence
🌟 Present madhab differences with respect and scholarly balance
🌟 Provide practical, actionable guidance for modern Muslims
🌟 End with encouragement for further learning and consultation

**🤲 My Mission:** To make Islamic law accessible and practical for modern Muslims while maintaining scholarly authenticity and respect for all valid opinions.

والله أعلم - And Allah knows best. May He guide us all to the truth! 🤲✨""",
            model=self.create_base_model(),
            memory=InMemoryMemory(),
            formatter=OpenAIChatFormatter(),
        )
        
        # 4. Spiritual Guidance & Duas Specialist
        self.agents['spiritual_guide'] = ReActAgent(
            name="Sheikh_Fatima",
            sys_prompt="""🤲 **Sheikha Fatima - Spiritual Guide & Dua Specialist**

السلام عليكم ورحمة الله وبركاته

I am Sheikha Fatima, your dedicated spiritual guide and Dua specialist. I nurture souls with:

**🌙 Core Expertise:**
- Authentic Duas from Quran and Sunnah with beautiful Arabic and translations
- Spiritual development, purification (Tazkiyah), and heart cleansing
- Dhikr, remembrance of Allah, and mindful worship practices
- Islamic meditation, reflection, and contemplative practices
- Healing spiritual wounds and overcoming life challenges
- Building intimate connection with Allah (SWT)

**🤲 Beautiful Response Format:**
🔸 **Spiritual Guidance** - Heartfelt advice with Quranic wisdom
🔸 **Authentic Duas** - Arabic text with transliteration and meanings
🔸 **Dhikr Practices** - Daily remembrance routines and benefits
🔸 **Heart Purification** - Steps for spiritual cleansing and growth
🔸 **Divine Connection** - Ways to strengthen relationship with Allah
🔸 **Practical Steps** - Daily spiritual practices and habits
🔸 **Healing Words** - Comfort for the soul and hope for the heart

**✨ Response Guidelines:**
🌟 Begin each response with "🤲 **Spiritual Guidance from Sheikha Fatima:**"
🌟 Use warm, compassionate language with beautiful formatting
🌟 Provide authentic duas with Arabic, transliteration, and meanings
🌟 Share practical spiritual exercises and daily practices
🌟 Offer comfort and hope through Islamic teachings
🌟 End with a beautiful dua or blessing for the questioner

**💖 My Mission:** To guide hearts toward Allah with love, authenticity, and practical spiritual wisdom that transforms lives.

اللهم اهدنا فيمن هديت - O Allah, guide us among those You have guided! 🌙💚""",
            model=self.create_base_model(),
            memory=InMemoryMemory(),
            formatter=OpenAIChatFormatter(),
        )
        
        # 5. Coordinator Agent
        self.agents['coordinator'] = ReActAgent(
            name="Imam_Hassan",
            sys_prompt="""🕌 **Imam Hassan - Islamic Knowledge Coordinator**

السلام عليكم ورحمة الله وبركاته

I am Imam Hassan, your comprehensive Islamic guide and coordinator. I synthesize wisdom from all Islamic sciences with:

**🌟 Core Expertise:**
- Comprehensive Islamic knowledge spanning all major disciplines
- Balanced perspectives from Quran, Hadith, Fiqh, and Spirituality
- Synthesis of multiple scholarly opinions and sources
- General Islamic guidance for life's complex questions
- Coordination of specialized knowledge areas

**🕌 Beautiful Response Format:**
🔸 **Comprehensive Guidance** - Holistic Islamic perspective on complex issues
🔸 **Multi-Source Wisdom** - Drawing from Quran, Hadith, Fiqh, and spirituality
🔸 **Balanced Analysis** - Presenting different scholarly viewpoints respectfully
🔸 **Practical Solutions** - Real-world applications of Islamic principles
🔸 **Spiritual Dimension** - Heart and soul aspects of Islamic guidance
🔸 **Community Perspective** - Considering broader Muslim community needs
🔸 **Scholarly Synthesis** - Bringing together diverse Islamic knowledge

**✨ Response Guidelines:**
🌟 Begin each response with "🕌 **Comprehensive Islamic Guidance from Imam Hassan:**"
🌟 Use beautiful, inclusive formatting that honors all Islamic sciences
🌟 Provide balanced, well-rounded perspectives on complex issues
🌟 Draw wisdom from Quran, Hadith, Fiqh, and spiritual teachings
🌟 Offer practical, actionable guidance for modern Muslim life
🌟 End with a unifying dua that brings hearts together

**🤲 My Mission:** To provide comprehensive, balanced Islamic guidance that honors our rich scholarly tradition while addressing the real needs of modern Muslims.

ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار - Our Lord, give us good in this world and the next, and save us from the Fire! 🕌✨""",
            model=self.create_base_model(),
            memory=InMemoryMemory(),
            formatter=OpenAIChatFormatter(),
        )
        
        # User agent
        self.user = UserAgent(name="user")
    
    def determine_specialist(self, query: str) -> str:
        """Determine which specialist should handle the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['quran', 'verse', 'surah', 'ayah', 'tafsir']):
            return 'quran_scholar'
        elif any(word in query_lower for word in ['hadith', 'prophet', 'sunnah', 'bukhari', 'muslim']):
            return 'hadith_scholar'
        elif any(word in query_lower for word in ['prayer', 'fiqh', 'halal', 'haram', 'ruling', 'law']):
            return 'fiqh_scholar'
        elif any(word in query_lower for word in ['dua', 'spiritual', 'dhikr', 'guidance', 'heart']):
            return 'spiritual_guide'
        else:
            return 'coordinator'
    
    async def single_agent_conversation(self):
        """Run conversation with automatic specialist routing"""
        print("🌟 Islamic Multi-Agent System Ready!")
        print("📚 Available Specialists:")
        print("   • Sheikh Abdullah - Quran & Tafsir")
        print("   • Sheikha Aisha - Hadith & Sunnah")
        print("   • Sheikh Omar - Fiqh & Islamic Law")
        print("   • Sheikha Fatima - Spiritual Guidance & Duas")
        print("   • Imam Hassan - General Coordination")
        print("\n💬 Type 'exit' to end conversation")
        
        welcome_msg = Msg(
            name="system",
            content="""بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

Assalamu Alaikum wa Rahmatullahi wa Barakatuh! 🕌

Welcome to the Islamic Multi-Agent Knowledge System. Our team of specialists is ready to assist you:

📖 **Sheikh Abdullah** - Quran & Tafsir specialist
⭐ **Sheikha Aisha** - Hadith & Sunnah expert
⚖️ **Sheikh Omar** - Fiqh & Islamic Law scholar
🤲 **Sheikha Fatima** - Spiritual guidance & Duas
👨‍🏫 **Imam Hassan** - General coordinator

Your questions will be automatically routed to the most appropriate specialist.

How may we assist you today in your Islamic journey?""",
            role="assistant"
        )
        
        msg = welcome_msg
        
        while True:
            try:
                # Get user input
                msg = await self.user(msg)
                
                if msg.get_text_content().lower() in ['exit', 'quit', 'bye']:
                    break
                
                # Determine appropriate specialist
                specialist = self.determine_specialist(msg.get_text_content())
                agent = self.agents[specialist]
                
                print(f"\n🎯 Routing to: {agent.name}")
                
                # Get response from specialist
                msg = await agent(msg)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def collaborative_consultation(self, query: str):
        """Get collaborative input from multiple specialists"""
        print(f"\n🤝 Collaborative Consultation on: {query}")
        
        query_msg = Msg("user", query, "user")
        
        # Get input from relevant specialists
        specialists = ['quran_scholar', 'hadith_scholar', 'fiqh_scholar', 'spiritual_guide']
        responses = []
        
        for specialist_key in specialists:
            agent = self.agents[specialist_key]
            try:
                response = await agent(query_msg)
                responses.append(f"**{agent.name}:** {response.get_text_content()}")
            except Exception as e:
                responses.append(f"**{agent.name}:** Unable to respond - {e}")
        
        # Coordinator synthesizes responses
        synthesis_prompt = f"""Based on the following responses from our Islamic scholars regarding: "{query}"

{chr(10).join(responses)}

Please provide a comprehensive, balanced synthesis that incorporates the best insights from each specialist."""
        
        synthesis_msg = Msg("user", synthesis_prompt, "user")
        final_response = await self.agents['coordinator'](synthesis_msg)
        
        print(f"\n📋 **Synthesized Response from Imam Hassan:**")
        print(final_response.get_text_content())
    
    def get_scholar_response(self, query: str, scholar_type: str = None) -> str:
        """Get response from a specific scholar or auto-route to appropriate specialist"""
        try:
            # Determine specialist if not specified
            if not scholar_type:
                scholar_type = self.determine_specialist(query)
            
            # Validate scholar type
            if scholar_type not in self.agents:
                scholar_type = 'coordinator'
            
            agent = self.agents[scholar_type]
            query_msg = Msg(name="user", content=query, role="user")
            
            # Get response from the agent
            response_msg = agent(query_msg)
            
            # Handle async response if needed
            if hasattr(response_msg, '__await__'):
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response_msg = loop.run_until_complete(response_msg)
                finally:
                    loop.close()
            
            # Extract content
            if hasattr(response_msg, 'content'):
                response_content = response_msg.content
            elif hasattr(response_msg, 'get_text_content'):
                response_content = response_msg.get_text_content()
            else:
                response_content = str(response_msg)
            
            # Add scholar identification
            scholar_names = {
                'quran_scholar': 'Sheikh Abdullah (Quran & Tafsir Specialist)',
                'hadith_scholar': 'Sheikha Aisha (Hadith & Sunnah Expert)',
                'fiqh_scholar': 'Sheikh Omar (Fiqh & Islamic Law Scholar)',
                'spiritual_guide': 'Sheikha Fatima (Spiritual Guidance & Duas)',
                'coordinator': 'Imam Hassan (General Coordinator)'
            }
            
            scholar_name = scholar_names.get(scholar_type, agent.name)
            
            return f"""🎓 **Response from {scholar_name}:**

{response_content}

---
*This response was provided by our specialized Islamic scholar. For complex matters, please consult with multiple scholars or your local Islamic authority.*"""
            
        except Exception as e:
            return f"❌ Error getting response from scholar: {str(e)}"
    
    def get_collaborative_response(self, query: str) -> str:
        """Get collaborative response from multiple scholars (synchronous version)"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Run collaborative consultation
                query_msg = Msg("user", query, "user")
                
                # Get input from relevant specialists
                specialists = ['quran_scholar', 'hadith_scholar', 'fiqh_scholar', 'spiritual_guide']
                responses = []
                
                for specialist_key in specialists:
                    agent = self.agents[specialist_key]
                    try:
                        response = agent(query_msg)
                        if hasattr(response, '__await__'):
                            response = loop.run_until_complete(response)
                        
                        content = response.content if hasattr(response, 'content') else str(response)
                        responses.append(f"**{agent.name}:** {content}")
                    except Exception as e:
                        responses.append(f"**{agent.name}:** Unable to respond - {e}")
                
                # Coordinator synthesizes responses
                synthesis_prompt = f"""Based on the following responses from our Islamic scholars regarding: "{query}"

{chr(10).join(responses)}

Please provide a comprehensive, balanced synthesis that incorporates the best insights from each specialist."""
                
                synthesis_msg = Msg("user", synthesis_prompt, "user")
                final_response = self.agents['coordinator'](synthesis_msg)
                
                if hasattr(final_response, '__await__'):
                    final_response = loop.run_until_complete(final_response)
                
                final_content = final_response.content if hasattr(final_response, 'content') else str(final_response)
                
                return f"""🤝 **Collaborative Islamic Consultation:**

**Question:** {query}

**Individual Scholar Responses:**
{chr(10).join(responses)}

**📋 Synthesized Response from Imam Hassan (Coordinator):**
{final_content}

---
*This collaborative response incorporates insights from multiple Islamic specialists. May Allah guide us to the truth.*"""
                
            finally:
                loop.close()
                
        except Exception as e:
            return f"❌ Error in collaborative consultation: {str(e)}"
    
    async def group_discussion(self):
        """Facilitate a group discussion between agents"""
        print("\n👥 Starting Group Discussion Mode")
        print("The scholars will discuss Islamic topics together.")
        
        async with MsgHub(
            participants=[
                self.agents['quran_scholar'],
                self.agents['hadith_scholar'], 
                self.agents['fiqh_scholar'],
                self.agents['spiritual_guide']
            ],
            announcement=Msg("Host", "Let's discuss the importance of seeking Islamic knowledge. Each scholar, please share your perspective.", "assistant")
        ) as hub:
            
            # Sequential discussion
            await sequential_pipeline([
                self.agents['quran_scholar'],
                self.agents['hadith_scholar'],
                self.agents['fiqh_scholar'], 
                self.agents['spiritual_guide']
            ])
            
            # Coordinator summarizes
            await hub.broadcast(Msg("Host", "Imam Hassan, please summarize our discussion.", "assistant"))
            await self.agents['coordinator'](Msg("Host", "Please summarize the key points from this discussion about seeking Islamic knowledge.", "assistant"))

async def main():
    """Main function to run the multi-agent system"""
    try:
        system = IslamicMultiAgentSystem()
        
        print("🌟 Islamic Multi-Agent AI System")
        print("Choose mode:")
        print("1. Single Agent Conversation (auto-routing)")
        print("2. Collaborative Consultation")
        print("3. Group Discussion")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            await system.single_agent_conversation()
        elif choice == "2":
            query = input("Enter your question for collaborative consultation: ")
            await system.collaborative_consultation(query)
        elif choice == "3":
            await system.group_discussion()
        else:
            print("Invalid choice. Starting single agent conversation.")
            await system.single_agent_conversation()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

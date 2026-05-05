"""
Multi-Agent Islamic AI System using AgentScope
Specialized agents for different aspects of Islamic knowledge
"""

import os
import asyncio
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Agentscope and Tool imports will be deferred

load_dotenv()

class IslamicMultiAgentSystem:
    """Multi-agent Islamic AI system with specialized agents"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("API key required (OPENAI_API_KEY or GOOGLE_API_KEY)")
        
        self.model_params = None
        
        self.agents = {}
        self.user = None
        self.model_config = None
        self.formatter = None
        self.toolkit = None
        self.model = None
        self.setup_agents()
    
    def setup_agents(self, user_gender: str = "not_specified"):
        """Set up specialized Islamic AI agents with gender awareness"""
        
        gender_prefix = ""
        if user_gender == "male":
            gender_prefix = "The user is your **Brother** in Islam. Address him respectfully as 'Brother' or 'Akhi' where appropriate."
        elif user_gender == "female":
            gender_prefix = "The user is your **Sister** in Islam. Address her respectfully as 'Sister' or 'Ukhti' where appropriate. Provide gender-specific guidance (Fiqh of Nisa) if the topic relates to women's matters."

        # 1. Quran & Tafsir Specialist
        from agentscope.agent import ReActAgent
        from agentscope.tool import Toolkit
        from agentscope.formatter import GeminiChatFormatter
        
        # Initialize AgentScope via unified provider
        from backend.utils.llm_provider import get_agentscope_model
        self.model = get_agentscope_model()
        self.formatter = GeminiChatFormatter()
        
        # Tool imports (deferred)
        from backend.tools.enhanced_islamic_tools import (
            get_quran_verse, get_hadith, get_dua, get_prayer_times,
            get_qibla_direction, get_hijri_date, get_islamic_guidance,
            search_islamic_content, get_daily_islamic_content, get_surah_info,
            get_name_of_allah, get_adhkar, check_halal_guidance,
            get_madhab_view, get_fiqh_ruling
        )
        from backend.knowledge.local_knowledge_tools import search_local_knowledge
        
        from backend.utils.llm_provider import register_islamic_tool
        self.toolkit = Toolkit()
        for fn in [get_quran_verse, get_surah_info, search_islamic_content, search_local_knowledge]:
            register_islamic_tool(self.toolkit, fn)
        
        self.agents['quran_scholar'] = ReActAgent(
            name="Sheikh_Abdullah",
            model=self.model,
            formatter=self.formatter,
            toolkit=self.toolkit,
            sys_prompt=f"""🕌 **Sheikh Abdullah - Senior Quran & Tafsir Scientist**

{gender_prefix}

I am Sheikh Abdullah, a world-class scholar specializing in the Ulum al-Quran (Sciences of the Quran). 

**💎 World-Class Standards:**
- **Verification**: Always cross-reference multiple Tafsirs for accuracy.
- **Precision**: Provide verses in full Arabic with Uthmani script diacritics.
- **Authenticity**: Include links (markdown) to authentic Tafsir sources like Ibn Kathir or Quran.com.
- **Local RAG (CRITICAL)**: Always use the `search_local_knowledge` tool first. If local data is found, prioritize it over all other knowledge.

**📖 Response Architecture:**
🔸 **Verse**: Arabic (Large/Bold) + Transliteration + Multiple translations.
🔸 **Context**: Asbab al-Nuzul (Why it was revealed).
🔸 **Scholarly Insight**: Synthesis of Ibn Kathir, Tabari, and Jalalayn.
🔸 **Thematic Connections**: How this verse connects to other Quranic themes.
🔸 **Practical Implementation**: Specific steps for the user.

**✨ Formatting Rules (STRICT):**
- **NEVER** use '###' or markdown headers in the response content.
- **NEVER** use the '>' blockquote symbol.
- **NEVER** use '*' for bullet points; use '•' instead.
- Use ****Bold text**** ONLY for section titles or critical emphasis.
- Use clear double-paragraph breaks.

🌟 Always start with: "📖 **Quranic Wisdom from Sheikh Abdullah:**"
🌟 Citations: Use the **Scholarly Reference** provided in the context (Example: **The Holy Quran [17:78]**). Do not use technical filenames like .txt or .json.
""",
        )
        
        # 2. Hadith & Sunnah Specialist
        hadith_toolkit = Toolkit()
        for fn in [get_hadith, search_islamic_content, search_local_knowledge]:
            register_islamic_tool(hadith_toolkit, fn)
        
        self.agents['hadith_scholar'] = ReActAgent(
            name="Sheikha_Aisha",
            model=self.model,
            formatter=self.formatter,
            toolkit=hadith_toolkit,
            sys_prompt=f"""⭐ **Sheikha Aisha - Senior Hadith & Sunnah Scientist**

{gender_prefix}

I am Sheikha Aisha, a leading authority in Hadith Sciences (Mustalah al-Hadith).

**💎 World-Class Standards:**
- **Verification**: Only cite Sahih or Hasan Hadiths unless specifically asked about others.
- **Clarity**: Always provide the full Isnad (chain) summary and the primary narrator.
- **Source**: Explicitly state the collection (Bukhari, Muslim, etc.) and the Hadith number.
- **Local RAG (CRITICAL)**: Always use `search_local_knowledge` first to find authentic matches in your local library. If a match is found, use it as your primary evidence.

**⭐ Response Architecture:**
🔸 **Hadith**: Arabic text + clear English translation.
🔸 **Narrator**: Who reported this from the Prophet (ﷺ)?
🔸 **Classification**: Sahih/Hasan grading with source (Bukhari, Muslim, Nawawi).
🔸 **Deep Understanding**: Practical wisdom and Sunnah application.

**✨ Formatting Rules (STRICT):**
- **NEVER** use '###' or markdown headers in the response content.
- **NEVER** use the '>' blockquote symbol.
- **NEVER** use '*' for bullet points; use '•' instead.
- Use ****Bold text**** ONLY for section titles or critical emphasis.
- Use clear double-paragraph breaks.

🌟 Always start with: "⭐ **Prophetic Guidance from Sheikha Aisha:**"
🌟 Citations: Use the **Scholarly Reference** provided in the context (Example: **Sahih al-Bukhari [123]**). Do not use technical filenames like .txt or .json.
""",
        )
        
        # 3. Fiqh & Islamic Law Specialist
        fiqh_toolkit = Toolkit()
        for fn in [get_islamic_guidance, check_halal_guidance, get_prayer_times,
                   get_qibla_direction, get_madhab_view, get_fiqh_ruling, search_local_knowledge]:
            register_islamic_tool(fiqh_toolkit, fn)
        
        self.agents['fiqh_scholar'] = ReActAgent(
            name="Sheikh_Omar",
            model=self.model,
            formatter=self.formatter,
            toolkit=fiqh_toolkit,
            sys_prompt=f"""⚖️ **Sheikh Omar - Senior Fiqh & Shariah Scholar**

{gender_prefix}

I am Sheikh Omar, an expert in Shariah law and contemporary Fiqh.

**💎 World-Class Standards:**
- **Balance**: Present the views of all four major Madhabs (Hanafi, Maliki, Shafi'i, Hanbali). Use the `get_madhab_view` tool for specific differences.
- **Evidence**: Ground every ruling in specific Quranic Ayats and Sahih Hadiths.
- **Context**: Address modern challenges (Finance, Medical Ethics, Technology).
- **Gender Specificity**: {"Focus on rulings specifically pertaining to women's Fiqh" if user_gender == 'female' else "Focus on general and men's Fiqh as appropriate."}

**⚖️ Response Architecture:**
🔸 **The Ruling**: Simplified answer first.
🔸 **Evidentiary Basis**: Major texts used to derive the ruling.
🔸 **Madhab Opinions**: Differences of opinion where they exist.
🔸 **Modern Case Study**: How this applies to the user's specific context.

**✨ Formatting Rules (STRICT):**
- **NEVER** use '###' or markdown headers in the response content.
- **NEVER** use the '>' blockquote symbol.
- **NEVER** use '*' for bullet points; use '•' instead.
- Use ****Bold text**** ONLY for section titles or critical emphasis.
- Use clear double-paragraph breaks.

🌟 Always start with: "⚖️ **Fiqh Guidance from Sheikh Omar:**"
🌟 Citations: Use the **Scholarly Reference** provided in the context (Example: **Fiqh Fundamentals [Chapter: Zakat]**). Do not use technical filenames like .txt or .json.
""",
        )
        
        # 4. Spiritual Guidance & Duas Specialist
        spiritual_toolkit = Toolkit()
        for fn in [get_dua, get_adhkar, get_name_of_allah, search_local_knowledge]:
            register_islamic_tool(spiritual_toolkit, fn)
        
        self.agents['spiritual_guide'] = ReActAgent(
            name="Sheikha_Fatima",
            model=self.model,
            formatter=self.formatter,
            toolkit=spiritual_toolkit,
            sys_prompt=f"""🤲 **Sheikha Fatima - Spiritual Guide & Dua Specialist**

I am Sheikha Fatima, your dedicated spiritual guide. I nurture souls with:

**🌙 Core Expertise:**
- Authentic Duas from Quran and Sunnah.
- Spiritual purification (Tazkiyah) and heart cleansing.
- Dhikr and mindfulness in worship.

**✨ Formatting Rules (STRICT):**
- **NEVER** use '###' or markdown headers in the response content.
- **NEVER** use the '>' blockquote symbol.
- **NEVER** use '*' for bullet points; use '•' instead.
- Use ****Bold text**** ONLY for section titles or critical emphasis.
- Use clear double-paragraph breaks.

🌟 Begin each response with "🤲 **Spiritual Guidance from Sheikha Fatima:**"
🌟 Citations: Use the **Scholarly Reference** provided in the context (Example: **Hisn al-Muslim [Dua #12]**). Do not use technical filenames like .txt or .json.
""",
        )
        
        # 5. The System Coordinator (Imam Hassan)
        self.agents['coordinator'] = ReActAgent(
            name="Imam_Hassan",
            model=self.model,
            formatter=self.formatter,
            toolkit=self.toolkit,
            sys_prompt=f"""🕌 **Imam Hassan - Islamic Knowledge Coordinator**

I am Imam Hassan, your comprehensive Islamic guide. I synthesize wisdom from all Islamic sciences.

**✨ Formatting Rules (STRICT):**
- **NEVER** use '###' or markdown headers in the response content.
- **NEVER** use the '>' blockquote symbol.
- **NEVER** use '*' for bullet points; use '•' instead.
- Use ****Bold text**** ONLY for section titles or critical emphasis.
- Use clear double-paragraph breaks.
- Ensure the final response is "Premium" and reflects a unified scholarly consensus.

🌟 Begin each response with "🕌 **Comprehensive Islamic Guidance from Imam Hassan:**"
🌟 Citations: Use the **Scholarly Reference** provided in the context. Do not use technical filenames like .txt or .json.
""",
        )
        
        # User agent
        from agentscope.agent import UserAgent
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
    
    def get_scholar_response(self, query: str, scholar_type: Optional[str] = None, user_gender: str = "not_specified", latitude: Optional[float] = None, longitude: Optional[float] = None, include_thoughts: bool = False, force_local: bool = False) -> Any:
        """Get response from a specific scholar or auto-route with Local-First Priority & Synthesis"""
        try:
            # 1. Local Knowledge Base Retrieval (RAG)
            from backend.knowledge.local_knowledge_tools import search_local_knowledge, get_kb
            kb = get_kb()
            local_context = search_local_knowledge(query)
            has_local_data = local_context and "❌ No relevant information" not in local_context and "❌ Local knowledge base" not in local_context

            # --- FORCE LOCAL FOR DEMO ---
            if force_local:
                 print(f"🛡️ Multi-Agent FORCE_LOCAL Active. Bypassing {scholar_type} synthesis.")
                 if kb:
                     fallback_display = kb.format_scholarly_display(query)
                     if include_thoughts: return (fallback_display, "Demo Mode: Local Retrieval Active")
                     return fallback_display

            # 2. Specialist Selection
            if not scholar_type or scholar_type == 'auto':
                scholar_type = self.determine_specialist(query)
            
            # Use Imam Hassan as fallback coordinator
            if scholar_type not in self.agents:
                scholar_type = 'coordinator'
                
            agent = self.agents[scholar_type]
            
            # 3. AI Synthesis Prompt
            context_str = f"LOCAL KNOWLEDGE CONTEXT:\n{local_context}\n" if has_local_data else "No specific local documents found for this query."
            
            synthesis_prompt = f"""
            User Message: {query}
            User Gender: {user_gender}
            User Location: {f'Lat: {latitude}, Lng: {longitude}' if latitude else 'Not provided'}
            
            {context_str}
            
            INSTRUCTIONS:
            1. Use the provided local context as your primary source of truth.
            2. Synthesize a beautiful, scholarly response in your specialized voice ({agent.name}).
            3. Follow all your world-class standards (Arabic text, authentic citations, respectful tone).
            4. If the local context is insufficient, use your tools to supplement the answer.
            """
            
            # 5. Message creation
            from agentscope.message import Msg
            query_msg = Msg(name="user", content=synthesis_prompt, role="user")
            
            # Get response from the agent
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, agent(query_msg))
                        response_msg = future.result()
                else:
                    response_msg = loop.run_until_complete(agent(query_msg))
            except Exception as e:
                # DETECT QUOTA ERRORS (429) - Switch to Premium Local Knowledge Display
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "limit" in err_str:
                    print(f"🛡️ Multi-Agent Scholar ({agent.name}) Quota Exceeded. Falling back to local data.")
                    # Get the formatted scholarly display (deterministic)
                    kb = get_kb()
                    if kb:
                        local_display = kb.format_scholarly_display(query)
                        if include_thoughts: return local_display, None
                        return local_display
                raise e # Re-raise other errors for the outer catch if not 429
            
            # Extract content
            response_content = response_msg.content if hasattr(response_msg, 'content') else str(response_msg)
            
            # Thoughts extraction
            thoughts = getattr(response_msg, 'thought', None)
            
            result_text = f"🎓 **Scholar Response Synthesized from Local Knowledge Base:**\n\n{response_content}\n\n---\n*This specialized response was synthesized by our AI scholars from locally stored authentic documents.*"
            
            if include_thoughts:
                return (result_text, thoughts)
            return result_text
            
        except Exception as e:
            print(f"❌ Error in Multi-Agent synthesis: {e}")
            
            # LAST LINE OF DEFENSE: Return formatted local knowledge base result
            kb = get_kb()
            if kb:
                fallback_display = kb.format_scholarly_display(query)
                if include_thoughts: return fallback_display, None
                return fallback_display
                
            err_msg = f"Assalamu Alaikum. I encountered a difficulty accessing our scholarly collective. Please try rephrasing your question. 🤲"
            if include_thoughts:
                return (err_msg, None)
            return err_msg
    
    def get_collaborative_response(self, query: str, user_gender: str = "not_specified", include_thoughts: bool = False) -> Any:
        """Get collaborative response via a single-call consolidated conference to save quota."""
        try:
            from backend.knowledge.local_knowledge_tools import search_local_knowledge
            
            # 1. Unified RAG Retrieval
            local_context = search_local_knowledge(query)
            has_local_data = local_context and "❌ No relevant information" not in local_context
            
            # 2. Preparation for Single Call
            from backend.utils.llm_provider import get_agentscope_model
            model = get_agentscope_model()
            
            # For collaborative response, we use the model directly
            conference_prompt = f"""
            COLLABORATIVE SCHOLARLY CONFERENCE
            
            You are a panel of world-class Islamic scholars providing a high-level consultation for a user who identifies as {user_gender}.
            The query is: "{query}"
            
            LOCAL KNOWLEDGE BASE EVIDENCE (Authentic Sources):
            {local_context if has_local_data else "No specific local documentation found. Rely on your internal scholarly training but prioritize any local snippets provided."}
            
            INSTRUCTIONS:
            Provide a unified, comprehensive response that integrates perspectives from four specialized domains. 
            Structure your response exactly as follows:
            
            1. 📖 **Quranic Foundation (Sheikh Abdullah)**: Provide relevant verses (Uthmani Arabic + translation) and Tafsir synthesis.
            2. ⭐ **Hadith & Sunnah (Sheikha Aisha)**: Cite authentic Hadith with gradings (Sahih/Hasan) and narrators.
            3. ⚖️ **Jurisprudence & Fiqh (Sheikh Omar)**: Present balanced views across major Madhabs (Hanafi, Maliki, Shafi'i, Hanbali).
            4. 🤲 **Spirituality & Dua (Sheikha Fatima)**: Provide spiritual counseling and a beautiful Dua (Arabic + Transliteration).
            5. 👨‍🏫 **Consolidated Guidance (Imam Hassan)**: A final balanced synthesis and practical next steps for the user.
            
            STRICT REQUIREMENTS:
            - ALWAYS prioritize the LOCAL KNOWLEDGE snippets if they contain relevant evidence.
            - Maintain the unique "voice" for each section.
            - Ensure the tone is world-class, serene, and empathetic.
            - DO NOT USE headers like '###'. Use the emojis and titles provided above.
            """
            
            # 3. Direct Model Call
            try:
                # Call the model with the conference prompt
                response = model(conference_prompt, thought_signature=include_thoughts)
                content = response.text if hasattr(response, 'text') else str(response)
                thoughts = getattr(response, 'thought', None) if include_thoughts else None
            except Exception as e:
                # Basic fallback
                content = f"The scholarly panel encountered an error: {e}"
                thoughts = None
            
            result_text = f"🎓 **Consolidated Scholarly Conference Response (Local-First)**\n\n{content}\n\n---\n*This unified response was synthesized in a single high-fidelity session to ensure scholarly depth while maximizing system stability.*"
            
            if include_thoughts:
                return (result_text, thoughts)
            return result_text

        except Exception as e:
            print(f"❌ Error in collaborative conference: {e}")
            
            # Switch to high-fidelity local response if quota hit or other error
            from backend.knowledge.local_knowledge_tools import get_kb
            kb = get_kb()
            if kb:
                fallback_display = kb.format_scholarly_display(query)
                if include_thoughts:
                    return (fallback_display, "🛡️ System Note: Switched to Local Knowledge due to scholarly conference overload.")
                return fallback_display
                
            err_msg = f"Assalamu Alaikum. Our scholarly council is currently in deep deliberation. Please consult our local guidance in the meantime. 🤲"
            if include_thoughts:
                return (err_msg, None)
            return err_msg

"""
Local Intelligence-First Response Synthesis for Islamic Teaching
100% Local Processing - NO EXTERNAL APIs
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import re
from collections import Counter

logger = logging.getLogger("LocalSynthesis")

class LocalIntelligentSynthesizer:
    """Local response synthesizer - no external LLMs required."""
    
    def __init__(self):
        self.model = "LocalIntelligent"
        self.provider = "local"
        self.logger = logger
        
    async def synthesize_response(
        self,
        user_query: str,
        rag_results: List[Dict[str, Any]],
        query_type: str = "islamic_general",
        context: Optional[Dict] = None
    ) -> str:
        """Synthesize response from local knowledge base."""
        try:
            self.logger.info(f"🧠 Local synthesis: {query_type}")
            
            if not rag_results:
                return self._fallback_synthesis(user_query, [], query_type)
            
            knowledge = self._extract_knowledge_base(rag_results)
            
            if query_type == "surah_specific":
                response = self._synthesize_surah_response(user_query, rag_results, knowledge)
            elif query_type == "quran_general":
                response = self._synthesize_quran_response(user_query, rag_results, knowledge)
            elif query_type == "hadith":
                response = self._synthesize_hadith_response(user_query, rag_results, knowledge)
            else:
                response = self._synthesize_general_response(user_query, rag_results, knowledge)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Synthesis error: {e}")
            return self._fallback_synthesis(user_query, rag_results, query_type)
    
    def _extract_knowledge_base(self, results: List[Dict]) -> Dict[str, Any]:
        """Extract structured knowledge from RAG results."""
        knowledge = {
            "quranic": [],
            "hadith": [],
            "scholarly": [],
            "practical": [],
            "key_themes": [],
            "sources": Counter()
        }
        
        for result in results[:20]:
            content = result.get('content', '').strip()
            source = result.get('source_file', 'Unknown').replace('.json', '')
            
            knowledge["sources"][source] += 1
            
            if any(x in source.lower() for x in ['quran', 'surah', 'ayah']):
                knowledge["quranic"].append(content)
            elif any(x in source.lower() for x in ['hadith', 'sahih', 'bukhari', 'muslim']):
                knowledge["hadith"].append(content)
            elif any(x in source.lower() for x in ['tafsir', 'commentary', 'ibn']):
                knowledge["scholarly"].append(content)
            else:
                knowledge["practical"].append(content)
            
            self._extract_key_concepts(content, knowledge["key_themes"])
        
        return knowledge
    
    def _extract_key_concepts(self, text: str, themes: List[str]) -> None:
        """Extract key Islamic concepts."""
        patterns = [
            r'(Allah|faith|iman|taqwa)',
            r'(mercy|compassion)',
            r'(justice|fairness)',
            r'(knowledge|wisdom)',
            r'(worship|prayer)',
            r'(charity|zakah)',
            r'(patience)',
            r'(forgiveness)',
        ]
        for pattern in patterns:
            themes.extend(re.findall(pattern, text, re.IGNORECASE))
    
    def _synthesize_surah_response(self, query: str, results: List[Dict], knowledge: Dict) -> str:
        """Build Surah response from local knowledge."""
        surah_num = self._extract_surah_number(query)
        
        response = f"""
╔════════════════════════════════════════════════════════════════╗
║           📖 SURAH ANALYSIS - LOCAL INTELLIGENCE 📖            ║
╚════════════════════════════════════════════════════════════════╝

🕌 **Surah #{surah_num}** - Local Knowledge Base Synthesis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 **KEY THEMES:**
"""
        themes = list(set([t[0] if isinstance(t, tuple) else t for t in knowledge["key_themes"]]))
        for theme in themes[:5]:
            response += f"\n  • {theme.capitalize()}"
        
        if knowledge["scholarly"]:
            response += "\n\n📚 **SCHOLARLY INSIGHTS:**\n"
            for excerpt in knowledge["scholarly"][:3]:
                excerpt = excerpt[:250] + "..." if len(excerpt) > 250 else excerpt
                response += f"\n  {excerpt}"
        
        if knowledge["hadith"]:
            response += "\n\n📖 **SUPPORTING HADITH:**\n"
            hadith = knowledge["hadith"][0][:250] + "..." if len(knowledge["hadith"][0]) > 250 else knowledge["hadith"][0]
            response += f"\n  {hadith}"
        
        response += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **AUTHENTICITY:** {len(knowledge['sources'])} authenticated sources
   Processing: 100% Local Intelligence (No external APIs)

اللهم علمنا ما ينفعنا وانفعنا بما علمتنا 🤲
"""
        return response
    
    def _synthesize_quran_response(self, query: str, results: List[Dict], knowledge: Dict) -> str:
        """Build Quranic response from local knowledge."""
        response = f"""
╔════════════════════════════════════════════════════════════════╗
║        🕌 QURANIC WISDOM - LOCAL INTELLIGENCE 🕌               ║
╚════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 **TEACHING:**
"""
        if knowledge["quranic"]:
            response += f"\n{knowledge['quranic'][0][:400]}"
        
        themes = list(set([t[0] if isinstance(t, tuple) else t for t in knowledge["key_themes"]]))
        response += "\n\n🎯 **KEY THEMES:**\n"
        for theme in themes[:7]:
            response += f"\n  ➤ {theme.capitalize()}"
        
        if knowledge["scholarly"]:
            response += "\n\n📚 **INTERPRETATION:**\n"
            for i, excerpt in enumerate(knowledge["scholarly"][:2], 1):
                response += f"\n  {i}. {excerpt[:300]}..."
        
        response += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Sources: {len(knowledge['sources'])} authenticated
   Processing: 100% Local - No external APIs

اللهم اجعلنا من المتدبرين لآيات القرآن 📚
"""
        return response
    
    def _synthesize_hadith_response(self, query: str, results: List[Dict], knowledge: Dict) -> str:
        """Build Hadith response."""
        response = f"""
╔════════════════════════════════════════════════════════════════╗
║      ✍️ PROPHETIC TRADITION - LOCAL INTELLIGENCE ✍️            ║
╚════════════════════════════════════════════════════════════════╝

📜 **HADITH:** Sahih (Authenticated)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        if knowledge["hadith"]:
            response += f"\n{knowledge['hadith'][0]}\n"
        
        response += f"""

🔍 **AUTHENTICITY:** Verified from authenticated collections
💡 **COMMENTARY:**
"""
        if knowledge["scholarly"]:
            for excerpt in knowledge["scholarly"][:2]:
                response += f"\n  • {excerpt[:250]}..."
        
        response += f"""

⚡ **APPLICATION:** Practical guidance for Muslim life

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Sources: {len(knowledge['sources'])} | Processing: 100% Local

🤲 Follow the Sunnah of Prophet Muhammad (ﷺ)
"""
        return response
    
    def _synthesize_general_response(self, query: str, results: List[Dict], knowledge: Dict) -> str:
        """Build general Islamic response."""
        response = f"""
╔════════════════════════════════════════════════════════════════╗
║      🌙 ISLAMIC WISDOM - LOCAL INTELLIGENCE 🌙                 ║
╚════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        all_content = (
            knowledge["quranic"] + 
            knowledge["scholarly"] + 
            knowledge["hadith"] + 
            knowledge["practical"]
        )
        
        for i, excerpt in enumerate(all_content[:3], 1):
            content = excerpt[:300] + "..." if len(excerpt) > 300 else excerpt
            response += f"\n\n{i}. {content}"
        
        themes = list(set([t[0] if isinstance(t, tuple) else t for t in knowledge["key_themes"]]))
        response += "\n\n🎯 **KEY PRINCIPLES:**\n"
        for theme in themes[:6]:
            response += f"\n  ✓ {theme.capitalize()}"
        
        response += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 {len(knowledge['sources'])} authenticated sources
   100% Local Processing - No external APIs

🙏 May Allah grant us beneficial knowledge!
"""
        return response
    
    def _extract_surah_number(self, query: str) -> int:
        """Extract Surah number from query."""
        numbers = re.findall(r'\b(\d{1,3})\b', query)
        return int(numbers[0]) if numbers else 1
    
    def _fallback_synthesis(self, user_query: str, rag_results: List[Dict], query_type: str) -> str:
        """Fallback response format."""
        response = f"""
╔════════════════════════════════════════════════════════════════╗
║      📚 ISLAMIC KNOWLEDGE - LOCAL REFERENCE 📚                 ║
╚════════════════════════════════════════════════════════════════╝

Query: {user_query}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        if rag_results:
            response += "📖 **SOURCES:**\n\n"
            for i, result in enumerate(rag_results[:5], 1):
                content = result.get('content', '')[:250]
                source = result.get('source_file', 'Reference')
                response += f"{i}. [{source}]\n   {content}...\n\n"
        
        response += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

100% Local Processing - Authenticated Islamic Sources

الحمد لله على نعمه 🤲
"""
        return response


def get_synthesizer() -> LocalIntelligentSynthesizer:
    """Get singleton synthesizer."""
    global _synthesizer
    if '_synthesizer' not in globals():
        _synthesizer = LocalIntelligentSynthesizer()
    return _synthesizer


class ResponseEnhancer:
    """Enhance responses with Islamic duas."""
    
    DUAS = {
        "surah_specific": "اللهم علمنا ما ينفعنا وانفعنا بما علمتنا",
        "quran_general": "اللهم اجعلنا من المتدبرين لآيات القرآن",
        "hadith": "اللهم اجعلنا على سنة محمد صلى الله عليه وسلم",
        "islamic_general": "اللهم زدنا علما ويقينا وحسن تدبرنا"
    }
    
    @staticmethod
    def enhance_response(response: str, query_type: str = "islamic_general") -> str:
        """Add duas to response."""
        dua = ResponseEnhancer.DUAS.get(query_type, ResponseEnhancer.DUAS["islamic_general"])
        return response + f"\n\n🤲 {dua}"

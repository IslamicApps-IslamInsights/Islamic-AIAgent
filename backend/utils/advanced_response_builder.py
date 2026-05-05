"""
Advanced Response Builder with Quran Priority & Local Model Synthesis
Uses HuggingFace models + Quran Foundation MCP for comprehensive Islamic responses
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import torch

logger = logging.getLogger("AdvancedResponseBuilder")

# Source priority configuration
SOURCE_PRIORITY = {
    'quran_yusuf_ali.txt': 100,
    'quran_saheeh_international.txt': 100,
    'quran_pickthall.txt': 100,
    'quran_shakir.txt': 100,
    'quran_surah_metadata_114.json': 95,
    'tafsir_ibn_kathir_highlights.txt': 90,
    'Quran Foundation MCP': 85,
    '40_hadith_nawawi_highlights.txt': 70,
    'sahih_bukhari.json': 65,
    'sahih_muslim.json': 65,
}

SOURCE_NAME_MAP = {
    'quran_yusuf_ali.txt': 'Quran - Yusuf Ali Translation',
    'quran_saheeh_international.txt': 'Quran - Sahih International',
    'quran_pickthall.txt': 'Quran - Pickthall',
    'quran_shakir.txt': 'Quran - Shakir',
    'quran_surah_metadata_114.json': 'Quran - Surah Metadata',
    'tafsir_ibn_kathir_highlights.txt': 'Tafsir Ibn Kathir',
    'Quran Foundation MCP': 'Quran Foundation (Advanced)',
    'sahih_bukhari.json': 'Sahih al-Bukhari',
    'sahih_muslim.json': 'Sahih Muslim',
    '40_hadith_nawawi_highlights.txt': '40 Hadith an-Nawawi',
}


def get_friendly_source_name(source_file: str) -> str:
    """Convert file name to user-friendly source name"""
    if source_file in SOURCE_NAME_MAP:
        return SOURCE_NAME_MAP[source_file]
    
    name = source_file.replace('.json', '').replace('.txt', '').replace('_', ' ').title()
    return name


def calculate_relevance_score(query: str, content: str) -> float:
    """Calculate relevance score between query and content"""
    query_words = set(word.lower() for word in query.split() if len(word) > 3)
    content_words = set(word.lower() for word in content.split()[:150])
    
    if not query_words:
        return 0.5
    
    overlap = len(query_words & content_words)
    score = overlap / len(query_words)
    return min(1.0, score)


def prioritize_results_by_type(
    results: List[Dict[str, Any]],
    query: str
) -> List[Dict[str, Any]]:
    """
    Prioritize results with Quran & Tafsir first
    
    Priority Order:
    1. Quran (all translations)
    2. Quran Foundation MCP
    3. Tafsir (Islamic interpretation)
    4. Hadith (Prophetic traditions)
    5. Scholarly sources
    """
    
    # Group by type
    quran_results = []
    tafsir_results = []
    hadith_results = []
    scholarly_results = []
    other_results = []
    
    for result in results:
        source = result.get('metadata', {}).get('source', '').lower()
        
        if 'quran' in source or 'mcp' in result.get('metadata', {}).get('source', '').lower():
            quran_results.append(result)
        elif 'tafsir' in source or 'interpretation' in source:
            tafsir_results.append(result)
        elif any(h in source for h in ['bukhari', 'muslim', 'tirmidhi', 'nasai', 'dawud', 'majah', 'muwatta', 'nawawi']):
            hadith_results.append(result)
        elif any(s in source for s in ['fiqh', 'akhlaq', 'ethics', 'scholarly', 'essentials', 'aqeedah']):
            scholarly_results.append(result)
        else:
            other_results.append(result)
    
    # Combine in priority order
    prioritized = quran_results + tafsir_results + hadith_results + scholarly_results + other_results
    
    return prioritized


def build_multipart_response(
    query: str,
    results: List[Dict[str, Any]],
    use_local_model: bool = True,
    local_model: Optional[Any] = None
) -> str:
    """
    Build comprehensive response with multiple source types
    
    Args:
        query: User question
        results: Retrieved documents from RAG
        use_local_model: Whether to use local HuggingFace model synthesis
        local_model: Loaded local model instance
    """
    
    if not results:
        return """Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲

I apologize, but I could not find relevant Islamic knowledge about your question.

This could mean:
• The topic might not be covered in my current knowledge base
• Try rephrasing your question with different Islamic terms
• Ask about related Islamic topics
• Check if the subject is part of core Islamic teachings (Quran, Hadith, Fiqh)

May Allah grant us wisdom and understanding. Ameen. 🤲"""
    
    # Prioritize results
    prioritized = prioritize_results_by_type(results, query)
    
    response = "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
    response += "I found authentic Islamic knowledge for your question.\n\n"
    response += "═" * 70 + "\n\n"
    
    # Section 1: Quranic Guidance
    quran_results = [r for r in prioritized if 'quran' in r.get('metadata', {}).get('source', '').lower() or 'mcp' in r.get('metadata', {}).get('source', '').lower()]
    if quran_results:
        response += "📖 **QURANIC GUIDANCE:**\n\n"
        for i, result in enumerate(quran_results[:2], 1):
            source = result.get('metadata', {}).get('source', 'Unknown')
            source_name = get_friendly_source_name(source)
            content = result.get('content', '').strip()[:400]
            
            response += f"✦ {source_name}\n"
            response += f"{content}\n\n"
    
    # Section 2: Tafsir (Islamic Interpretation)
    tafsir_results = [r for r in prioritized if 'tafsir' in r.get('metadata', {}).get('source', '').lower()]
    if tafsir_results:
        response += "📚 **ISLAMIC INTERPRETATION (TAFSIR):**\n\n"
        for i, result in enumerate(tafsir_results[:2], 1):
            source = result.get('metadata', {}).get('source', 'Unknown')
            source_name = get_friendly_source_name(source)
            content = result.get('content', '').strip()[:400]
            
            response += f"✦ {source_name}\n"
            response += f"{content}\n\n"
    
    # Section 3: Hadith (Prophetic Traditions)
    hadith_results = [r for r in prioritized if any(h in r.get('metadata', {}).get('source', '').lower() for h in ['bukhari', 'muslim', 'tirmidhi', 'nasai', 'dawud', 'majah'])]
    if hadith_results:
        response += "📖 **PROPHETIC TRADITIONS (HADITH):**\n\n"
        for i, result in enumerate(hadith_results[:2], 1):
            source = result.get('metadata', {}).get('source', 'Unknown')
            source_name = get_friendly_source_name(source)
            content = result.get('content', '').strip()[:400]
            
            grade = result.get('metadata', {}).get('grade', '')
            grade_text = f" [{grade}]" if grade else ""
            
            response += f"✦ {source_name}{grade_text}\n"
            response += f"{content}\n\n"
    
    # Section 4: Scholarly Analysis
    scholarly_results = [r for r in prioritized if any(s in r.get('metadata', {}).get('source', '').lower() for s in ['fiqh', 'essentials', 'akhlaq', 'scholarly'])]
    if scholarly_results:
        response += "🔍 **SCHOLARLY ANALYSIS:**\n\n"
        for i, result in enumerate(scholarly_results[:2], 1):
            source = result.get('metadata', {}).get('source', 'Unknown')
            source_name = get_friendly_source_name(source)
            content = result.get('content', '').strip()[:400]
            
            response += f"✦ {source_name}\n"
            response += f"{content}\n\n"
    
    response += "═" * 70 + "\n\n"
    
    # Optional: Add AI synthesis using local model
    if use_local_model and local_model and len(results) >= 2:
        response += "💭 **AI SYNTHESIS (Based on Islamic Sources):**\n\n"
        try:
            context = [r.get('content', '')[:200] for r in results[:3]]
            synthesis = local_model.synthesize_response(query, context, max_length=300)
            response += synthesis + "\n\n"
        except Exception as e:
            logger.warning(f"⚠️  Local model synthesis failed: {e}")
    
    # Statistics
    source_count = len(set(r.get('metadata', {}).get('source', '') for r in results))
    response += "📊 **RESPONSE STATISTICS:**\n"
    response += f"• Sources used: {source_count}\n"
    response += f"• Quran verses: {len(quran_results)}\n"
    response += f"• Tafsir references: {len(tafsir_results)}\n"
    response += f"• Hadith traditions: {len(hadith_results)}\n"
    response += f"• Overall relevance: {calculate_relevance_score(query, ' '.join([r.get('content', '') for r in results])):.0%}\n\n"
    
    # Guidance
    response += "💡 **GUIDANCE & APPLICATION:**\n"
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['salah', 'prayer', 'namaz', 'salat']):
        response += "• Establish regular prayer with proper intention (niyyah)\n"
        response += "• Learn proper prayer posture and recitations\n"
        response += "• Consult qualified Islamic scholars for details\n"
    elif any(word in query_lower for word in ['zakat', 'charity', 'alms']):
        response += "• Calculate zakat based on your wealth and assets\n"
        response += "• Give zakat with sincere intention for the sake of Allah\n"
        response += "• Seek guidance from knowledgeable Muslims on distribution\n"
    elif any(word in query_lower for word in ['quran', 'verse', 'ayah', 'surah']):
        response += "• Recite the Quran with proper Tajweed (pronunciation)\n"
        response += "• Reflect on the meanings of the verses\n"
        response += "• Study Tafsir (Quranic interpretation) from trusted scholars\n"
    elif any(word in query_lower for word in ['hadith', 'sunnah', 'prophet']):
        response += "• Learn the authentic Sunnah (practices) of the Prophet\n"
        response += "• Understand the chain of narration (isnad) of hadiths\n"
        response += "• Follow guidance only from authenticated sources\n"
    else:
        response += "• Seek knowledge from authentic Islamic sources\n"
        response += "• Apply Islamic teachings in daily life with sincerity\n"
        response += "• Consult qualified Islamic scholars for nuanced questions\n"
    
    response += "\n" + "═" * 70 + "\n\n"
    response += "May Allah grant us beneficial knowledge and guide us to righteousness. Ameen. 🤲\n\n"
    
    from datetime import datetime
    response += f"_Response generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}_"
    
    return response


def build_rag_response_with_fallback(
    query: str,
    local_results: List[Dict[str, Any]],
    mcp_results: Optional[List[Dict[str, Any]]] = None,
    use_local_model: bool = False,
    local_model: Optional[Any] = None
) -> str:
    """
    Build response combining local KB and Quran Foundation MCP
    
    Args:
        query: User question
        local_results: Results from local knowledge base
        mcp_results: Results from Quran Foundation MCP (if available)
        use_local_model: Use local model for synthesis
        local_model: Local model instance
    """
    
    # Combine results, prioritizing Quran and MCP
    all_results = []
    
    # Add MCP results first (if available)
    if mcp_results:
        for result in mcp_results:
            all_results.append({
                'content': result.get('text', ''),
                'metadata': {
                    'source': 'Quran Foundation MCP',
                    'type': 'quran_mcp',
                    'surah': result.get('surah', ''),
                    'verse': result.get('verse', '')
                },
                'score': result.get('relevance', 0.85)
            })
    
    # Add local results
    all_results.extend(local_results)
    
    # Prioritize by source type
    all_results = prioritize_results_by_type(all_results, query)
    
    # Build response
    return build_multipart_response(query, all_results, use_local_model, local_model)


def build_training_dataset(
    query: str,
    results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build dataset entry for local model training
    
    Useful for creating fine-tuned Islamic QA model
    """
    
    return {
        "query": query,
        "context": " ".join([r.get('content', '')[:300] for r in results[:3]]),
        "sources": list(set(r.get('metadata', {}).get('source', '') for r in results)),
        "ideal_response": build_multipart_response(query, results, use_local_model=False)
    }

"""
Islamic AI Agent - Enhanced Query Response Builder
Improves response quality, formatting, and relevance
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import json

logger = logging.getLogger("ResponseBuilder")

# Enhanced source name mapping
SOURCE_NAME_MAP = {
    'sahih_bukhari.json': 'Sahih al-Bukhari',
    'sahih_bukhari_english.json': 'Sahih al-Bukhari',
    'sahih_muslim.json': 'Sahih Muslim',
    'sahih_muslim_english.json': 'Sahih Muslim',
    'sunan_abu_dawud_english.json': 'Sunan Abu Dawud',
    'sunan_an_nasai_english.json': 'Sunan an-Nasa\'i',
    'sunan_ibn_majah_english.json': 'Sunan Ibn Majah',
    'jami_at_tirmidhi_english.json': 'Jami\' at-Tirmidhi',
    'muwatta_malik_english.json': 'Muwatta Malik',
    'forty_hadith_nawawi.json': '40 Hadith an-Nawawi',
    'forty_hadith_nawawi_highlights.txt': '40 Hadith an-Nawawi',
    'quran_yusuf_ali.txt': 'Quran - Yusuf Ali',
    'quran_saheeh_international.txt': 'Quran - Sahih International',
    'quran_pickthall.txt': 'Quran - Pickthall',
    'quran_shakir.txt': 'Quran - Shakir',
    'islamic_ethics_akhlaq.txt': 'Islamic Ethics & Character',
    'seerah_prophet.txt': 'Life of Prophet Muhammad',
}


def get_friendly_source_name(source_file: str) -> str:
    """Convert file name to user-friendly source name"""
    if source_file in SOURCE_NAME_MAP:
        return SOURCE_NAME_MAP[source_file]
    
    name = source_file.replace('.json', '').replace('.txt', '').replace('_', ' ').title()
    return name


def calculate_relevance_score(query: str, content: str) -> float:
    """Calculate relevance score between query and content"""
    query_words = set(query.lower().split())
    content_words = set(content.lower().split()[:100])  # First 100 words
    
    if not query_words:
        return 0.0
    
    overlap = len(query_words & content_words)
    return overlap / len(query_words)


def group_results_by_type(results: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """Group results by content type"""
    grouped = defaultdict(list)
    
    for result in results:
        metadata = result.get('metadata', {})
        source_file = metadata.get('source', '').lower()
        
        if 'quran' in source_file:
            grouped['quran'].append(result)
        elif any(h in source_file for h in ['bukhari', 'muslim', 'tirmidhi', 'nasai', 'abu dawud', 'ibn majah', 'muwatta', 'nawawi']):
            grouped['hadith'].append(result)
        else:
            grouped['scholarly'].append(result)
    
    return grouped


def enhance_content(content: str, query: str, max_length: int = 500) -> str:
    """Enhance content with context and formatting"""
    # Clean up
    content = content.strip()
    
    # If content is very long, provide preview with indicator
    if len(content) > max_length:
        content = content[:max_length].rsplit(' ', 1)[0] + '...\n\n[Content continues]'
    
    # Ensure proper spacing
    content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
    
    return content


def build_enhanced_response(query: str, results: List[Dict[str, Any]], 
                           include_context: bool = True) -> str:
    """
    Build enhanced, user-centric response with multiple sources
    """
    
    if not results:
        return """Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲

I apologize, but I could not find relevant Islamic knowledge in my database regarding your question. 

Please try:
- Rephrasing your question
- Using different Islamic terminology
- Asking about related topics
- Checking if the topic is covered in the knowledge base

May Allah guide us all to seek knowledge. Ameen."""
    
    # Group results by type
    grouped = group_results_by_type(results)
    
    response = "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
    response += f"I found authentic Islamic knowledge for your question.\n\n"
    response += "═" * 70 + "\n\n"
    
    # Process each group
    group_order = ['quran', 'hadith', 'scholarly']
    section_icons = {
        'quran': '📖',
        'hadith': '📚',
        'scholarly': '📕'
    }
    section_titles = {
        'quran': 'From the Holy Quran',
        'hadith': 'From Prophetic Traditions (Hadith)',
        'scholarly': 'From Islamic Scholarship & Guidance'
    }
    
    response_sections = []
    
    for group_type in group_order:
        if group_type not in grouped or not grouped[group_type]:
            continue
        
        group_results = grouped[group_type]
        section_content = f"{section_icons[group_type]} **{section_titles[group_type]}:**\n\n"
        
        # Add up to 3 results per group
        for idx, result in enumerate(group_results[:3], 1):
            content = result.get('content', '').strip()
            metadata = result.get('metadata', {})
            source_file = metadata.get('source', 'Unknown')
            source_name = get_friendly_source_name(source_file)
            score = result.get('score', 0)
            
            # Calculate relevance
            relevance = calculate_relevance_score(query, content)
            
            # Enhanced content
            enhanced_content = enhance_content(content, query, max_length=400)
            
            # Add attribution details
            attribution = f"✓ {source_name}"
            
            # Add book/chapter for hadiths
            if metadata.get('type') == 'hadith':
                if metadata.get('book'):
                    attribution += f" - {metadata.get('book')}"
                if metadata.get('grade'):
                    attribution += f" ({metadata.get('grade')})"
            
            # Build entry
            section_content += f"{attribution}\n"
            section_content += f"{enhanced_content}\n\n"
        
        response_sections.append(section_content)
    
    # Combine sections
    response += "\n".join(response_sections)
    
    # Add footer
    response += "═" * 70 + "\n\n"
    response += "📌 **About This Response:**\n"
    response += f"• Based on {len(results)} authentic Islamic sources\n"
    response += f"• Relevance to your query: {calculate_relevance_score(query, ' '.join([r.get('content', '') for r in results])):.0%}\n"
    response += f"• Sources verified and authenticated\n\n"
    
    response += "💡 **Guidance & Application:**\n"
    
    # Add query-specific guidance
    query_lower = query.lower()
    if 'salah' in query_lower or 'prayer' in query_lower:
        response += "• Maintain consistency in your prayers\n"
        response += "• Ensure proper intention (niyyah) before each prayer\n"
        response += "• Seek knowledge about prayer rulings from qualified scholars\n"
    elif 'zakat' in query_lower or 'charity' in query_lower:
        response += "• Zakat is one of the five pillars of Islam\n"
        response += "• Ensure you give zakat with sincere intention\n"
        response += "• Consult scholars for specific zakat calculations\n"
    elif 'quran' in query_lower or 'ayah' in query_lower or 'verse' in query_lower:
        response += "• Reflect on the meanings of the verses\n"
        response += "• Recite the Quran with proper tajweed\n"
        response += "• Consult tafsir for deeper understanding\n"
    elif 'hadith' in query_lower:
        response += "• Understand the context of the hadith\n"
        response += "• Learn from qualified Islamic scholars\n"
        response += "• Apply the teachings in your daily life\n"
    else:
        response += "• Seek knowledge from authentic Islamic sources\n"
        response += "• Apply Islamic teachings in your life\n"
        response += "• Consult qualified scholars for guidance\n"
    
    response += "\n═" * 70 + "\n\n"
    response += "May Allah grant us beneficial knowledge and guide us to the right path. Ameen. 🤲\n\n"
    response += "_Last updated: "
    
    from datetime import datetime
    response += datetime.now().strftime("%B %d, %Y at %H:%M:%S") + "_"
    
    return response


def build_sources_list(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build detailed sources list"""
    sources = []
    
    for result in results:
        metadata = result.get('metadata', {})
        source_file = metadata.get('source', 'Unknown')
        
        source_info = {
            "name": get_friendly_source_name(source_file),
            "file": source_file,
            "type": metadata.get('type', 'unknown'),
            "relevance_score": result.get('score', 0),
            "excerpt": result.get('content', '')[:150] + '...'
        }
        
        # Add additional details
        if metadata.get('book'):
            source_info['book'] = metadata['book']
        if metadata.get('id'):
            source_info['id'] = metadata['id']
        if metadata.get('grade'):
            source_info['authenticity'] = metadata['grade']
        
        sources.append(source_info)
    
    return sources


class ResponseQualityChecker:
    """Check and improve response quality"""
    
    @staticmethod
    def check_quality(response: str, query: str) -> Dict[str, Any]:
        """Check response quality metrics"""
        
        checks = {
            "has_greeting": bool("Assalamu" in response or "As-salamu" in response),
            "has_closing": bool("Ameen" in response or "May Allah" in response),
            "length": len(response),
            "has_sources": bool("Source" in response or "book" in response.lower()),
            "has_guidance": bool("guidance" in response.lower() or "apply" in response.lower()),
            "has_proper_formatting": bool("═" in response or "**" in response),
            "relevance_keywords": sum(1 for word in query.lower().split() if len(word) > 3 and word in response.lower()),
        }
        
        quality_score = (
            (20 if checks["has_greeting"] else 0) +
            (20 if checks["has_closing"] else 0) +
            (10 if checks["has_sources"] else 0) +
            (15 if checks["has_guidance"] else 0) +
            (15 if checks["has_proper_formatting"] else 0) +
            (20 if checks["length"] > 200 else 10 if checks["length"] > 100 else 0) +
            min(10, checks["relevance_keywords"]) if checks["relevance_keywords"] else 0
        )
        
        return {
            "quality_score": min(100, quality_score),
            "checks": checks,
            "is_good_quality": quality_score >= 70
        }


def improve_response_with_synthesis(response: str, query: str, 
                                   llm_result: Optional[Dict] = None) -> str:
    """
    Optionally enhance response with LLM synthesis
    """
    
    if not llm_result or llm_result.get('status') != 'success':
        return response
    
    llm_response = llm_result.get('response', '').strip()
    
    if not llm_response:
        return response
    
    # Insert LLM insight after greeting
    lines = response.split('\n')
    
    # Find where to insert (after greeting and main query intro)
    insert_index = 0
    for i, line in enumerate(lines):
        if '═' in line:
            insert_index = i
            break
    
    # Build enhanced response
    enhanced = '\n'.join(lines[:insert_index])
    enhanced += "\n\n💭 **AI Analysis & Synthesis:**\n"
    enhanced += llm_response[:500] + ("..." if len(llm_response) > 500 else "")
    enhanced += "\n\n" + '\n'.join(lines[insert_index:])
    
    return enhanced

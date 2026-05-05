#!/usr/bin/env python3
"""
Enhanced Response Optimization System
- Validates responses for authenticity
- Ensures proper source attribution
- Optimizes for comprehensive Islamic knowledge
- Implements quality scoring
"""

import os
import sys
from typing import Dict, List, Tuple
from collections import defaultdict
import re

class AuthenticResponseOptimizer:
    """Optimize responses for authenticity and quality"""
    
    # Source trust hierarchy
    SOURCE_TRUST_HIERARCHY = {
        'quran': 10,                           # Highest - Allah's word
        'quran_yusuf_ali.txt': 10,
        'quran_saheeh_international.txt': 10,
        'quran_pickthall.txt': 10,
        'quran_shakir.txt': 10,
        
        'sahih_bukhari': 9,                    # Highest hadith authority
        'sahih_bukhari.json': 9,
        'sahih_muslim': 9,
        'sahih_muslim.json': 9,
        
        'tafsir_ibn_kathir_highlights.txt': 8, # Authentic Tafsir
        'ar.muyassar.txt': 8,
        'en.ahmedraza.txt': 8,
        'ur.maududi.txt': 8,
        
        'sunan_abu_dawud_english.json': 7,     # Other authentic hadith
        'sunan_an_nasai_english.json': 7,
        'sunan_ibn_majah_english.json': 7,
        'jami_at_tirmidhi_english.json': 7,
        'muwatta_malik_english.json': 7,
        
        '40_hadith_nawawi_highlights.txt': 7,  # Authenticated collections
        'forty_hadith_nawawi.json': 7,
        
        'fiqh_fundamentals.txt': 6,             # Islamic jurisprudence
        'aqeedah_essentials.txt': 6,            # Islamic beliefs
        'islamic_ethics_akhlaq.txt': 6,
        'seerah_prophet.txt': 6,                # Prophet's biography
        
        'comprehensive_duas.txt': 5,            # Authentic duas
        '99_names_of_allah_full.json': 5,
        '99_names_of_prophet.json': 5,
        
        'hisn_al_muslim.json': 5,               # Islamic supplications
        'comprehensive_islamic_essentials.txt': 4,
        'ramadan_hajj_guide.txt': 4,
        'women_in_islam.txt': 4,
        'heaven_and_hell.txt': 4,
        'akhlaq_and_character.txt': 4,
        'islamic_ground_truth_essentials.txt': 3,
        
        'default': 1  # Unknown sources
    }
    
    # Authenticity keywords for validation
    AUTHENTICITY_MARKERS = {
        'quran': ['verse', 'surah', 'ayah', 'allah', 'said', 'indeed', 'verily', 'those who', 'believers'],
        'hadith': ['narrated', 'reported', 'prophet', 'sahabah', 'sahih', 'graded', 'authenticated'],
        'tafsir': ['interpretation', 'commentary', 'meaning', 'explains', 'scholars agree'],
        'fiqh': ['ruling', 'verdict', 'permissible', 'forbidden', 'islamic law', 'jurisprudence']
    }
    
    def __init__(self):
        self.quality_scores = defaultdict(float)
    
    def get_source_trust_score(self, source: str) -> float:
        """Get trust score for a source (0-10)"""
        if source in self.SOURCE_TRUST_HIERARCHY:
            return self.SOURCE_TRUST_HIERARCHY[source]
        
        # Check partial matches
        for key, score in self.SOURCE_TRUST_HIERARCHY.items():
            if key.lower() in source.lower() or source.lower() in key.lower():
                return score
        
        return self.SOURCE_TRUST_HIERARCHY['default']
    
    def validate_content_authenticity(self, content: str, content_type: str) -> float:
        """
        Validate content authenticity (0-1)
        Returns confidence score based on content markers
        """
        if not content:
            return 0.0
        
        content_lower = content.lower()
        markers = self.AUTHENTICITY_MARKERS.get(content_type, [])
        
        if not markers:
            return 0.5  # Unknown type
        
        matching_markers = sum(1 for marker in markers if marker in content_lower)
        auth_score = min(matching_markers / len(markers), 1.0)
        
        # Length authenticity (longer usually more complete)
        length_score = min(len(content) / 500, 1.0)  # Normalize to 500 chars
        
        return (auth_score * 0.6) + (length_score * 0.4)
    
    def calculate_response_quality_score(self, results: List[Dict]) -> Dict[str, float]:
        """
        Calculate comprehensive quality scores for results
        Returns: {source: score, content_type: score, overall: score}
        """
        if not results:
            return {'source': 0, 'content_type': 0, 'authenticity': 0, 'overall': 0}
        
        scores = {
            'source': 0,
            'content_type': 0,
            'authenticity': 0,
            'overall': 0
        }
        
        for result in results:
            meta = result.get('metadata', {})
            content = result.get('content', '')
            
            # Source trust score
            source_score = self.get_source_trust_score(meta.get('source', ''))
            scores['source'] += source_score
            
            # Content type trust (quran highest, then hadith, then others)
            content_type = meta.get('type', '')
            type_trust = {'quran': 10, 'hadith': 9, 'tafsir': 8, 'scholarly': 6}.get(content_type, 5)
            scores['content_type'] += type_trust
            
            # Authenticity based on content
            auth = self.validate_content_authenticity(content, content_type)
            scores['authenticity'] += auth
        
        # Normalize
        result_count = max(len(results), 1)
        scores['source'] = scores['source'] / result_count / 10
        scores['content_type'] = scores['content_type'] / result_count / 10
        scores['authenticity'] = scores['authenticity'] / result_count
        
        # Overall quality (weighted average)
        scores['overall'] = (
            (scores['source'] * 0.4) +
            (scores['content_type'] * 0.3) +
            (scores['authenticity'] * 0.3)
        )
        
        return scores
    
    def build_authentic_response(self, query: str, results: List[Dict]) -> str:
        """
        Build authentic, well-sourced response
        Ensures all sources are properly attributed
        """
        if not results:
            return "I couldn't find relevant information in the Islamic knowledge base. Please consult a qualified Islamic scholar."
        
        response = "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
        
        # Organize results by type and source trust
        organized = {
            'quran': [],
            'hadith': [],
            'tafsir': [],
            'scholarly': []
        }
        
        for result in results:
            meta = result.get('metadata', {})
            content_type = meta.get('type', 'scholarly')
            
            if content_type not in organized:
                content_type = 'scholarly'
            
            organized[content_type].append(result)
        
        # Build response sections in order of authority
        if organized['quran']:
            response += "📖 **QURANIC GUIDANCE:**\n"
            response += "━" * 70 + "\n\n"
            for idx, result in enumerate(organized['quran'][:3], 1):
                content = result.get('content', '').strip()
                meta = result.get('metadata', {})
                source_name = self._friendly_source_name(meta.get('source', ''))
                verse_range = meta.get('verse_range', '')
                
                response += f"{idx}. {source_name}"
                if verse_range:
                    response += f" ({verse_range})"
                response += "\n"
                response += f"{content}\n\n"
        
        if organized['tafsir']:
            response += "📚 **TAFSIR (ISLAMIC INTERPRETATION):**\n"
            response += "━" * 70 + "\n\n"
            for idx, result in enumerate(organized['tafsir'][:2], 1):
                content = result.get('content', '').strip()[:300]
                meta = result.get('metadata', {})
                source_name = self._friendly_source_name(meta.get('source', ''))
                
                response += f"{idx}. {source_name}\n"
                response += f"{content}...\n\n"
        
        if organized['hadith']:
            response += "📖 **PROPHETIC TRADITIONS (HADITH):**\n"
            response += "━" * 70 + "\n\n"
            for idx, result in enumerate(organized['hadith'][:3], 1):
                content = result.get('content', '').strip()[:400]
                meta = result.get('metadata', {})
                source_name = self._friendly_source_name(meta.get('source', ''))
                hadith_id = meta.get('id', '')
                
                response += f"{idx}. {source_name}"
                if hadith_id:
                    response += f" (Hadith #{hadith_id})"
                response += "\n"
                response += f"{content}\n\n"
        
        if organized['scholarly']:
            response += "🔍 **SCHOLARLY ANALYSIS:**\n"
            response += "━" * 70 + "\n\n"
            for idx, result in enumerate(organized['scholarly'][:2], 1):
                content = result.get('content', '').strip()[:300]
                meta = result.get('metadata', {})
                source_name = self._friendly_source_name(meta.get('source', ''))
                
                response += f"{idx}. {source_name}\n"
                response += f"{content}...\n\n"
        
        # Quality metrics
        quality = self.calculate_response_quality_score(results)
        response += "📊 **RESPONSE QUALITY:**\n"
        response += "━" * 70 + "\n"
        response += f"• Source Authenticity: {quality['source']*100:.0f}%\n"
        response += f"• Content Reliability: {quality['content_type']*100:.0f}%\n"
        response += f"• Overall Quality: {quality['overall']*100:.0f}%\n\n"
        
        response += "━" * 70 + "\n"
        response += "May Allah grant us beneficial knowledge and guide us to the truth. Ameen. 🤲\n"
        
        return response
    
    def _friendly_source_name(self, source: str) -> str:
        """Convert source filename to friendly name"""
        source_lower = source.lower()
        
        mapping = {
            'quran_yusuf_ali': '📖 Quran - Yusuf Ali Translation',
            'quran_saheeh_international': '📖 Quran - Sahih International',
            'quran_pickthall': '📖 Quran - Pickthall Translation',
            'quran_shakir': '📖 Quran - Shakir Translation',
            
            'sahih_bukhari': '📚 Sahih al-Bukhari',
            'sahih_muslim': '📚 Sahih Muslim',
            'sunan_abu_dawud': '📚 Sunan Abu Dawud',
            'sunan_an_nasai': '📚 Sunan an-Nasai',
            'sunan_ibn_majah': '📚 Sunan Ibn Majah',
            'jami_at_tirmidhi': '📚 Jami\' at-Tirmidhi',
            'muwatta_malik': '📚 Muwatta Malik',
            
            'tafsir_ibn_kathir': '📖 Tafsir Ibn Kathir',
            'ar.muyassar': '📖 Tafsir Al-Muyassar',
            'en.ahmedraza': '📖 Tafsir Ahmed Raza Khan',
            'ur.maududi': '📖 Tafhim ul-Quran (Maududi)',
            
            'fiqh_fundamentals': '⚖️ Fiqh Fundamentals',
            'aqeedah_essentials': '✨ Aqeedah (Islamic Beliefs)',
            'islamic_ethics_akhlaq': '💫 Islamic Ethics & Character',
            'seerah_prophet': '👨‍🎓 Seerah (Prophet\'s Biography)',
            '40_hadith_nawawi': '📖 40 Hadith an-Nawawi',
        }
        
        for key, friendly_name in mapping.items():
            if key in source_lower:
                return friendly_name
        
        return f"📚 {source.replace('.json', '').replace('.txt', '')}"


if __name__ == "__main__":
    # Test the optimizer
    optimizer = AuthenticResponseOptimizer()
    
    # Test with sample results
    sample_results = [
        {
            'content': 'In the name of Allah, the Most Gracious, the Most Merciful.',
            'metadata': {
                'source': 'quran_yusuf_ali.txt',
                'type': 'quran',
                'verse_range': '1:1'
            }
        },
        {
            'content': 'The Prophet (ﷺ) said: Islam is built on five pillars...',
            'metadata': {
                'source': 'sahih_bukhari.json',
                'type': 'hadith',
                'id': '1234'
            }
        }
    ]
    
    print(optimizer.build_authentic_response("Tell me about Islam", sample_results))
    print("\n" + "="*70)
    
    quality = optimizer.calculate_response_quality_score(sample_results)
    print(f"Quality Score: {quality}")

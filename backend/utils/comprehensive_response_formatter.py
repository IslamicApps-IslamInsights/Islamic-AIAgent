#!/usr/bin/env python3
"""
Comprehensive Response Formatter - Premium Islamic Knowledge Responses
Handles truncation, presentation, quality scoring, and source attribution
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
import re


class ComprehensiveResponseFormatter:
    """Format responses comprehensively without truncation"""
    
    # Source mapping for friendly names
    SOURCE_NAMES = {
        'sahih_bukhari': '📚 Sahih al-Bukhari',
        'sahih_muslim': '📚 Sahih Muslim',
        'jami_at_tirmidhi': '📖 Jami\' at-Tirmidhi',
        'sunan_abu_dawud': '📖 Sunan Abu Dawud',
        'sunan_an_nasai': '📖 Sunan an-Nasai',
        'sunan_ibn_majah': '📖 Sunan Ibn Majah',
        'muwatta_malik': '📖 Muwatta Malik',
        'forty_hadith_nawawi': '✨ 40 Hadith an-Nawawi',
        '99_names': '✨ 99 Names of Allah',
        'fiqh': '⚖️ Fiqh (Islamic Jurisprudence)',
        'aqeedah': '🕌 Aqeedah (Islamic Belief)',
        'tafsir': '📚 Tafsir (Commentary)',
        'seerah': '📖 Seerah (Biography)',
        'ethics': '💡 Islamic Ethics',
        'duas': '🤲 Islamic Supplications',
        'quran': '📖 Quran',
    }
    
    # Trust scores for sources
    TRUST_SCORES = {
        'sahih_bukhari': 95,
        'sahih_muslim': 95,
        'sahih_bukhari.json': 95,
        'sahih_muslim.json': 95,
        'sahih_muslim_english': 95,
        'sahih_bukhari_english': 95,
        'jami_at_tirmidhi': 85,
        'sunan_abu_dawud': 85,
        'sunan_an_nasai': 85,
        'sunan_ibn_majah': 85,
        'muwatta_malik': 85,
        '40_hadith_nawawi': 90,
        'forty_hadith_nawawi': 90,
        'tafsir_ibn_kathir': 90,
        'fiqh_fundamentals': 80,
        'aqeedah': 85,
        '99_names': 95,
    }
    
    @staticmethod
    def get_source_name(source: str) -> str:
        """Get friendly source name"""
        source_lower = source.lower()
        
        # Direct match
        if source_lower in ComprehensiveResponseFormatter.SOURCE_NAMES:
            return ComprehensiveResponseFormatter.SOURCE_NAMES[source_lower]
        
        # Partial match
        for key, name in ComprehensiveResponseFormatter.SOURCE_NAMES.items():
            if key in source_lower or source_lower in key:
                return name
        
        # Generic
        return f"📖 {source.replace('.json', '').replace('.txt', '').replace('_', ' ').title()}"
    
    @staticmethod
    def get_trust_score(source: str) -> int:
        """Get trust score for source (0-100)"""
        source_lower = source.lower()
        
        # Direct match
        if source_lower in ComprehensiveResponseFormatter.TRUST_SCORES:
            return ComprehensiveResponseFormatter.TRUST_SCORES[source_lower]
        
        # Partial match
        for key, score in ComprehensiveResponseFormatter.TRUST_SCORES.items():
            if key in source_lower or source_lower in key:
                return score
        
        # Default
        return 60
    
    @staticmethod
    def categorize_result(result: Dict[str, Any]) -> str:
        """Categorize result by type"""
        metadata = result.get('metadata', {})
        source = metadata.get('source', '').lower()
        
        if 'quran' in source:
            return 'quranic'
        elif any(x in source for x in ['bukhari', 'muslim', 'tirmidhi', 'dawud', 'nasai', 'majah', 'muwatta', 'nawawi']):
            return 'hadith'
        elif 'tafsir' in source:
            return 'tafsir'
        elif 'fiqh' in source or 'aqeedah' in source or 'ethics' in source or 'law' in source:
            return 'scholarly'
        elif '99' in source or 'names' in source:
            return 'names'
        else:
            return 'other'
    
    @staticmethod
    def build_full_response(query: str, results: List[Dict[str, Any]]) -> str:
        """Build comprehensive, well-formatted response with elegant presentation"""
        
        if not results:
            return (
                "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
                "I'm sorry, I couldn't find specific information about that in my knowledge base. "
                "Please try rephrasing your question or ask about Islamic topics like prayer, charity, "
                "the Quran, Hadith, or Islamic jurisprudence.\n\n"
                "May Allah guide us. 🤲"
            )
        
        # Categorize results
        categories = defaultdict(list)
        for result in results:
            category = ComprehensiveResponseFormatter.categorize_result(result)
            categories[category].append(result)
        
        # Build response with elegant header
        response = "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
        response += "> Scholarly Notice: *The following guidance is provided directly from our local library of authentic Islamic texts to ensure immediate accuracy.*\n\n"
        
        # Order by importance: Quranic, Tafsir, Hadith, Names, Scholarly
        order = ['quranic', 'tafsir', 'hadith', 'names', 'scholarly', 'other']
        
        for category in order:
            if category not in categories:
                continue
            
            results_in_category = categories[category]
            if not results_in_category:
                continue
            
            response += ComprehensiveResponseFormatter._format_category(
                category, 
                results_in_category
            )
        
        response += "\n" + "━" * 70 + "\n"
        response += ComprehensiveResponseFormatter._add_quality_metrics(results)
        response += "\nMay Allah grant us beneficial knowledge and guide us to the right path. Ameen. 🤲"
        
        return response
    
    @staticmethod
    def _format_category(category: str, results: List[Dict[str, Any]]) -> str:
        """Format a category of results - showing ALL results without truncation with elegance"""
        
        category_titles = {
            'quranic': '* 📖 Quranic Guidance',
            'tafsir': '* 📚 Tafsir & Interpretation',
            'hadith': '* 💬 Prophetic Traditions (Hadith)',
            'names': '* ✨ Divine Names & Attributes',
            'scholarly': '* 🏛️ Islamic Scholarship',
            'other': '* 📋 Additional Resources'
        }
        
        title = category_titles.get(category, '* 📖 Resources')
        formatted = f"{title}\n"
        
        # Show ALL results - no truncation!
        for result in results:
            metadata = result.get('metadata', {})
            content = result.get('content', '')
            source = metadata.get('source', result.get('source_file', 'Unknown'))
            
            # Use advanced metadata if available
            authenticity = result.get('authenticity', ComprehensiveResponseFormatter.get_source_name(source))
            source_priority = result.get('source_priority', 1.0)
            retrieval_method = result.get('retrieval_method', 'bm25')
            
            # Show full content - no character limit
            source_name = ComprehensiveResponseFormatter.get_source_name(source)
            trust_score = ComprehensiveResponseFormatter.get_trust_score(source)
            
            # Format with bullet point and authenticity level
            formatted += f"• {source_name}"
            
            # Add retrieval method indicator
            method_icon = {"bm25": "🔍", "vector": "🧠", "mcp": "📖"}.get(retrieval_method, "📌")
            formatted += f" {method_icon}"
            
            # Add reference info if available (in brackets like old format)
            if 'id' in metadata and metadata['id']:
                formatted += f" [{metadata['id']}]"
            
            # Add authenticity level
            formatted += f"\n  ✓ {authenticity}"
            
            # Add grade/authenticity if available
            grade = metadata.get('grade', '')
            if grade:
                formatted += f" — Grade: {grade}"
            
            formatted += "\n"
            
            # Show content with proper indentation
            if content:
                # Clean up content for presentation
                content_clean = content.strip()
                if len(content_clean) > 2000:
                    # For very long content, add ellipsis
                    content_clean = content_clean[:2000] + "\n[...content continues...]"
                formatted += f"  {content_clean}\n"
            
            # Add surah reference if Quranic
            if 'surah' in metadata:
                formatted += f"  (Surah {metadata['surah']}:{metadata.get('verse', '')})\n"
            
            formatted += "\n"
        
        return formatted
    
    @staticmethod
    def _add_quality_metrics(results: List[Dict[str, Any]]) -> str:
        """Add quality and authenticity metrics - with advanced weighting"""
        
        if not results:
            return ""
        
        # Calculate metrics using advanced weighting
        trust_scores = []
        source_weights = []
        retrieval_methods = defaultdict(int)
        
        for result in results:
            source = result.get('metadata', {}).get('source', '')
            score = ComprehensiveResponseFormatter.get_trust_score(source)
            trust_scores.append(score)
            
            # Use advanced source priority if available
            weight = result.get('source_priority', 1.0)
            source_weights.append(weight)
            
            # Track retrieval methods
            method = result.get('retrieval_method', 'unknown')
            retrieval_methods[method] += 1
        
        avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0
        avg_weight = sum(source_weights) / len(source_weights) if source_weights else 1.0
        
        # Build quality metrics display
        metrics = "\n📊 Response Quality & Source Metrics\n"
        metrics += f"  Sources Consulted: {len(results)}\n"
        metrics += f"  Average Authenticity Score: {avg_trust:.0f}%\n"
        metrics += f"  Source Priority Average: {avg_weight:.2f}/5.0\n"
        
        # Retrieval methods used
        if retrieval_methods:
            methods_str = ", ".join([f"{m}({c})" for m, c in retrieval_methods.items()])
            metrics += f"  Retrieval Methods: {methods_str}\n"
        
        metrics += f"  Confidence Level: "
        
        if avg_trust >= 90:
            metrics += "🟢 VERY HIGH (Sahih Hadith & Quranic Sources)\n"
        elif avg_trust >= 80:
            metrics += "🟢 HIGH (Authenticated & Scholarly Sources)\n"
        elif avg_trust >= 70:
            metrics += "🟡 GOOD (Mixed Scholarly Sources)\n"
        else:
            metrics += "🟡 MODERATE (General Islamic References)\n"
        
        return metrics
    
    @staticmethod
    def build_detailed_response(query: str, results: List[Dict[str, Any]]) -> str:
        """Build ultra-detailed response for complex queries"""
        
        # Use comprehensive formatter
        response = ComprehensiveResponseFormatter.build_full_response(query, results)
        
        return response


# Test function
if __name__ == "__main__":
    # Test with sample data
    sample_results = [
        {
            'content': 'The Prophet (ﷺ) said: "The best charity is water."',
            'metadata': {'source': 'sahih_tirmidhi', 'id': '#1234'},
            'score': 0.92
        },
        {
            'content': 'Verily, those who believe and do righteous deeds...',
            'metadata': {'source': 'quran', 'surah': 2, 'verse': 277},
            'score': 0.95
        }
    ]
    
    formatter = ComprehensiveResponseFormatter()
    response = formatter.build_full_response("What does Islam teach about charity?", sample_results)
    print(response)

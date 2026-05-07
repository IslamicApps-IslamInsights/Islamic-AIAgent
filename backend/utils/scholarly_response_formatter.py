"""
🏛️ Scholarly Response Formatter & Enhancer
==========================================
Creates museum-grade, academically rigorous responses with proper citations
and authentication metadata from ingested Islamic sources.

Produces responses in the "Scholarly Deep Dive" format with:
- Authentic source attribution
- Proper grading/authentication
- Categorized knowledge (Quranic, Hadith, Tafsir, etc.)
- Key themes and concepts
- Practical applications
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger("ScholarlyFormatter")


@dataclass
class AuthenticSource:
    """Represents an authenticated Islamic source"""
    content: str
    grade: str
    category: str  # "hadith", "quran", "tafsir", "dua", "seerah", etc.
    source_file: str
    authenticity: str
    narrator: Optional[str] = None
    book: Optional[str] = None
    reference: Optional[str] = None


class ScholarlyResponseFormatter:
    """Creates scholarly formatted responses from knowledge base results"""
    
    # Source file to category mapping
    SOURCE_CATEGORY_MAP = {
        # Hadith Collections
        "sahih_bukhari": ("hadith", "Sahih al-Bukhari", "Sahih (Authentic)"),
        "sahih_muslim": ("hadith", "Sahih Muslim", "Sahih (Authentic)"),
        "sunan_abu_dawud": ("hadith", "Sunan Abu Dawud", "Sunan (Authentic)"),
        "sunan_an_nasai": (
            "hadith",
            "Sunan an-Nasa'i",
            "Sunan (Authenticated)",
        ),
        "sunan_ibn_majah": (
            "hadith",
            "Sunan Ibn Majah",
            "Sunan (Authenticated)",
        ),
        "jami_at_tirmidhi": (
            "hadith",
            "Jami' at-Tirmidhi",
            "Jami' (Authenticated)",
        ),
        "muwatta_malik": (
            "hadith",
            "Muwatta Malik",
            "Muwatta (Authenticated)",
        ),
        "forty_hadith_nawawi": (
            "hadith",
            "40 Hadith an-Nawawi",
            "Hadith (Selected)",
        ),
        
        # Quranic Texts
        "quran_yusuf_ali": (
            "quran",
            "The Holy Quran (Yusuf Ali)",
            "Quran - Authentic Text",
        ),
        "quran_saheeh_international": (
            "quran",
            "The Holy Quran (Sahih Int'l)",
            "Quran - Authentic Text",
        ),
        "quran_pickthall": (
            "quran",
            "The Holy Quran (Pickthall)",
            "Quran - Authentic Text",
        ),
        "quran_shakir": (
            "quran",
            "The Holy Quran (Shakir)",
            "Quran - Authentic Text",
        ),
        "en.ahmedraza": (
            "quran",
            "The Holy Quran (Kanzul Iman)",
            "Quran - Authentic Text",
        ),
        "ur.qadri": (
            "quran",
            "The Holy Quran (Irfan ul Quran)",
            "Quran - Authentic Text",
        ),
        "ur.maududi": (
            "quran",
            "Tafhim ul Quran (Maududi)",
            "Quran - Authentic Text",
        ),
        
        # Tafsir & Scholarly Works
        "tafsir_ibn_kathir": (
            "tafsir",
            "Tafsir Ibn Kathir",
            "Classical Tafsir - Authentic",
        ),
        "aqeedah_essentials": (
            "aqeedah",
            "Islamic Aqeedah (Belief)",
            "Scholarly Reference",
        ),
        
        # Islamic Knowledge
        "seerah_prophet": (
            "seerah",
            "As-Seerah an-Nabawiyyah",
            "Prophetic Biography - Authenticated",
        ),
        "islamic_ethics": (
            "ethics",
            "Islamic Ethics & Akhlaq",
            "Scholarly Reference",
        ),
        "fiqh_fundamentals": (
            "fiqh",
            "Fiqh Fundamentals",
            "Islamic Jurisprudence - Authenticated",
        ),
        
        # Duas & Supplications
        "hisn_al_muslim": (
            "dua",
            "Hisn al-Muslim",
            "Authentic Supplications",
        ),
        "comprehensive_duas": (
            "dua",
            "Comprehensive Duas",
            "Islamic Supplications",
        ),
        
        # Metadata
        "99_names_of_allah": (
            "names",
            "Asma ul Husna (99 Names of Allah)",
            "Authentic Islamic Knowledge",
        ),
        "quran_surah_metadata": (
            "metadata",
            "Surah Information",
            "Quranic Reference",
        ),
    }
    
    AUTHENTICITY_EMOJIS = {
        "Sahih": "✅",
        "Sunan": "✅",
        "Jami'": "✅",
        "Hadith": "⭐",
        "Quran": "📖",
        "Tafsir": "📚",
        "Seerah": "📜",
        "Ethics": "🕌",
        "Fiqh": "⚖️",
        "Dua": "🤲",
        "Aqeedah": "💎",
    }
    
    def __init__(self):
        self.logger = logger
    
    def format_scholarly_deep_dive(
        self,
        query: str,
        kb_results: str,
        category: str = "islamic_general",
        include_greeting: bool = True
    ) -> str:
        """
        Create a 'Scholarly Deep Dive' response with proper formatting.
        
        Args:
            query: User's original query
            kb_results: Raw knowledge base results (formatted string)
            category: Query category for context
            include_greeting: Include Islamic greeting
            
        Returns:
            Beautifully formatted scholarly response
        """
        
        # Parse and categorize results
        parsed_results = self._parse_kb_results(kb_results)
        
        if not parsed_results:
            return self._handle_empty_results(query)
        
        # Build response sections
        sections = []
        
        # 1. The Radiance of Knowledge (Header & Intro)
        intro = f"Assalamu Alaikum wa Rahmatullahi wa Barakatuh. We explore this query with a focus on {category.replace('_', ' ')}."
        sections.append(f"1) The Radiance of Knowledge\n{intro}")
        
        # 2. The Heart of Wisdom (User-Centric Answer)
        answer = self._compose_user_centric_answer(query, parsed_results, category)
        sections.append(f"2) The Heart of Wisdom\n{answer}")
        
        # 3. Divine Light & Guidance (Evidence)
        evidence = self._categorize_and_format_results(parsed_results, category)
        sections.append(f"3) Divine Light & Guidance\n" + "\n".join(evidence))

        # 4. The Path of Action (Personal Guidance)
        steps = self._map_action_points(category, self._tokenize(query))
        steps_text = "\n".join([f"- {p}" for p in steps[:3]])
        sections.append(f"4) The Path of Action\n{steps_text}")

        # 5. Sacred Foundations (Key Themes & Insights)
        themes = self._extract_key_themes(parsed_results, kb_results)
        sections.append(f"5) Sacred Foundations\n{themes}")
        
        # 4. Authentic Sources
        sources = self._create_footer(parsed_results)
        sections.append(f"4) Authentic Sources\n{sources}")
        
        return "\n\n".join(filter(None, sections))
    
    def _compose_user_centric_answer(
        self,
        query: str,
        results: List[Dict[str, Any]],
        category: str,
    ) -> str:
        query_tokens = self._tokenize(query)
        key_sentences = self._select_key_sentences(results, query_tokens, k=4)

        if not key_sentences:
            return ""

        summary = self._rule_based_summary(
            category,
            query_tokens,
            key_sentences,
        )
        guidance_points = self._map_action_points(category, query_tokens)

        lines = []
        if summary:
            lines.append(summary)
            lines.append("")

        lines.append("**Practical answer:**")
        for s in key_sentences:
            lines.append(f"- {s}")

        if guidance_points:
            lines.append("")
            lines.append("**Try this today:**")
            for p in guidance_points[:3]:
                lines.append(f"- {p}")

        return "\n".join(lines)

    def _rule_based_summary(
        self,
        category: str,
        query_tokens: List[str],
        key_sentences: List[str],
    ) -> str:
        token_set = set(query_tokens)
        joined = " ".join(key_sentences).lower()

        if "patience" in token_set or "sabr" in token_set:
            parts = []
            if (
                "first stroke" in joined
                or "first shock" in joined
                or "calamity" in joined
            ):
                parts.append(
                    "The strongest sabr is staying firm at the first moment of "
                    "hardship."
                )
            if (
                "types of sabr" in joined
                or "obedience" in joined
                or "avoiding" in joined
            ):
                parts.append(
                    "Sabr includes staying consistent in obedience, avoiding sin, "
                    "and accepting Allah’s decree."
                )
            if parts:
                return "**Summary:** " + " ".join(parts)
            return (
                "**Summary:** Sabr is steady faith and good action during ease "
                "and hardship."
            )

        if (
            category in {"prayer_guide", "prayer_times"}
            or "prayer" in token_set
            or "salah" in token_set
        ):
            return (
                "**Summary:** Salah is the daily pillar that keeps the heart "
                "connected to Allah."
            )

        if (
            category in {"duas", "daily_adhkar"}
            or "dua" in token_set
            or "dhikr" in token_set
        ):
            return (
                "**Summary:** Dhikr and dua strengthen the heart, especially "
                "in stress and uncertainty."
            )

        if category in {"fiqh"}:
            return (
                "**Summary:** Let’s keep this practical and aligned with "
                "authentic scholarly principles."
            )

        return ""

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z']+", (text or "").lower())
        return [t for t in tokens if len(t) > 2]

    def _select_key_sentences(
        self,
        results: List[Dict[str, Any]],
        query_tokens: List[str],
        k: int = 4,
    ) -> List[str]:
        candidates: List[str] = []
        for r in results:
            content = (r.get("content") or "").strip()
            if not content:
                continue
            candidates.extend(self._split_sentences(content))

        seen = set()
        scored: List[tuple] = []
        token_set = set(query_tokens)
        for s in candidates:
            s_clean = " ".join(s.split())
            if len(s_clean) < 30 or len(s_clean) > 220:
                continue
            key = s_clean.lower()
            if key in seen:
                continue
            seen.add(key)
            s_tokens = set(self._tokenize(s_clean))
            if len(s_tokens) < 6:
                continue
            overlap = len(token_set & s_tokens)
            score = overlap
            scored.append((score, s_clean))

        scored.sort(key=lambda x: x[0], reverse=True)
        picked = [s for _score, s in scored if _score > 0][:k]

        if picked:
            return picked

        fallback = [" ".join(s.split()) for s in candidates if 30 <= len(" ".join(s.split())) <= 160]
        return fallback[:k]

    def _split_sentences(self, text: str) -> List[str]:
        cleaned = re.sub(r"\b\d+\.\s*", " ", text or "")
        parts = re.split(r"(?<=[.!?])\s+|\n+", cleaned)
        return [p.strip(" -•\t") for p in parts if p and p.strip()]

    def _map_action_points(self, category: str, query_tokens: List[str]) -> List[str]:
        token_set = set(query_tokens)
        if "patience" in token_set or "sabr" in token_set:
            return [
                "When you feel upset, pause, say: “Inna lillahi wa inna ilayhi raji’un”, then choose a calm action.",
                "Pick one small obedience to stay consistent with (a daily prayer on time, or a short dua).",
                "Avoid one common temptation today (a harsh reply, backbiting, anger), and treat that as sabr."
            ]
        if category in {"duas", "daily_adhkar"}:
            return [
                "Choose a short morning or evening dhikr routine and keep it consistent for 7 days.",
                "If you are stressed, repeat a brief remembrance slowly with meaning, not speed."
            ]
        if category in {"prayer_guide"}:
            return [
                "Learn the prayer in small steps: intention → Al-Fatiha → one short surah → ruku → sujud.",
                "Start with one prayer to perfect first, then add the next."
            ]
        return [
            "Tell me your situation (beginner/advanced) and I will tailor the guidance step-by-step.",
            "If you want, I can summarize this into a short checklist you can follow daily."
        ]

    def _create_essence_heading(self, category: str) -> str:
        """Create the essence heading for the scholarly response"""
        essences = {
            "surah_specific": "**Divine Guidance from the Quran**",
            "quran_general": "**Quranic Wisdom and Insights**",
            "hadith": "**The Sunnah and Prophetic Guidance**",
            "dua": "**The Power of Supplication and Adhkar**",
            "islamic_ethics": "**Character Excellence (Akhlaq)**",
            "seerah": "**Lessons from the Life of the Prophet ﷺ**",
            "fiqh": "**Practical Islamic Jurisprudence**",
            "aqeedah": "**The Foundations of Islamic Belief**",
        }
        return essences.get(category, "**Authentic Islamic Knowledge**")
    
    def _create_scholarly_notice(self, query: str) -> str:
        """Create the scholarly notice about local library authenticity"""
        return (
            f"**Your question:** {query}\n"
            "I will keep this simple, practical, and supported by "
            "authentic sources."
        )

    def _create_personal_guidance(self, query: str, category: str) -> str:
        prompts_by_category = {
            "quran_general": [
                "Do you want the verse(s) with a short reflection, or a deeper tafsir-style explanation?",
                "Should I keep it brief or provide a step-by-step action plan?",
                "If you share your goal (e.g., patience, anxiety, family), I will tailor the guidance."
            ],
            "hadith": [
                "Do you want the hadith text, its meaning in simple words, or its practical lesson?",
                "If you share your situation, I will extract 2–3 actionable sunnah habits for you."
            ],
            "prayer_guide": [
                "Tell me which prayer and how many rak'ahs you want to learn (Fajr/Dhuhr/Asr/Maghrib/Isha).",
                "If you are learning from scratch, I can give a beginner-friendly checklist."
            ],
            "daily_adhkar": [
                "Do you prefer a short set (3–5) or a complete morning/evening routine?",
                "If you share your available time (2 min / 5 min / 10 min), I will tailor it."
            ],
            "duas": [
                "Tell me what you are making dua for (health, stress, family, rizq) and I will match authentic duas.",
                "Do you want Arabic + transliteration + meaning, or meaning only?"
            ],
            "zakat": [
                "If you share your assets (cash, gold/silver, investments, debts), I can guide the calculation steps.",
            ],
            "fiqh": [
                "If you follow a madhhab (Hanafi/Maliki/Shafi'i/Hanbali), tell me and I will align the framing.",
                "If this is a personal situation, share details (without sensitive info) for a clearer ruling path."
            ],
        }

        suggestions = prompts_by_category.get(category, [
            "If you share your goal and context (beginner/advanced), I will tailor the answer to you.",
            "If you want, I can summarize the key takeaways into a short checklist you can follow today."
        ])

        return "\n".join(
            ["**To help you best:**"] + [f"- {s}" for s in suggestions[:3]]
        )
    
    def _parse_kb_results(self, kb_results: str) -> List[Dict[str, Any]]:
        """Parse knowledge base results string into structured data"""
        results = []
        
        if not kb_results or kb_results.startswith("❌"):
            return results
        
        pattern = r'\[Source \d+\]\s+([^\n]+)\n((?:[^\n]|\n(?!\[Source))*)'
        matches = re.finditer(pattern, kb_results)
        
        for match in matches:
            reference = match.group(1).strip()
            content = match.group(2).strip()
            
            if content:
                results.append({
                    'reference': reference,
                    'content': content
                })

        if results:
            return results

        mcp_pattern = (
            r'^\s*\d+\.\s+\*\*Surah\s+(\d+):(\d+)\*\*\s*\n'
            r'\s*Text:\s*(.+?)'
            r'(?:\n\s*Translation:\s*(.+?))?'
            r'(?=\n\s*\d+\.|\Z)'
        )
        for match in re.finditer(mcp_pattern, kb_results, re.MULTILINE | re.DOTALL):
            surah = match.group(1)
            ayah = match.group(2)
            text = (match.group(3) or "").strip()
            translation = (match.group(4) or "").strip()
            content_parts = []
            if text:
                content_parts.append(text)
            if translation:
                content_parts.append(f"Translation: {translation}")
            content = "\n".join(content_parts).strip()
            if content:
                results.append({
                    'reference': f"Quran {surah}:{ayah} [Quran Foundation MCP]",
                    'content': content
                })

        if results:
            return results

        numbered_pattern = (
            r'^\s*\d+\.\s+\*\*(.+?)\*\*\s+\(confidence:\s*([\d.]+)%\)\s*\n'
            r'\s*(.+?)'
            r'(?=\n\s*\d+\.\s+\*\*|\Z)'
        )
        for match in re.finditer(numbered_pattern, kb_results, re.MULTILINE | re.DOTALL):
            source = (match.group(1) or "").strip()
            score = (match.group(2) or "").strip()
            content = (match.group(3) or "").strip()
            if content:
                results.append({
                    'reference': f"{source} — Grade: Authenticated — Score: {score}%",
                    'content': content
                })

        if results:
            return results

        fallback = kb_results.strip()
        if fallback:
            results.append({
                'reference': 'Unstructured Result',
                'content': fallback
            })

        return results
    
    def _categorize_and_format_results(
        self,
        results: List[Dict[str, Any]],
        category: str
    ) -> List[str]:
        """Categorize results and format by type"""
        
        sections = []
        categorized = defaultdict(list)
        
        for result in results:
            result_category = self._detect_category(result, category)
            categorized[result_category].append(result)
        
        # Format each category
        for cat_key in ["hadith", "quran", "tafsir", "seerah", "ethics", "fiqh", "dua"]:
            if cat_key in categorized:
                sections.append(self._format_category_section(
                    cat_key,
                    categorized[cat_key]
                ))
        
        return sections
    
    def _detect_category(self, result: Dict, query_category: str) -> str:
        """Detect the category of a result"""
        reference = result.get('reference', '').lower()
        content = result.get('content', '').lower()
        
        if any(x in reference for x in ["bukhari", "muslim", "tirmidhi", "dawud", "nasai", "majah", "muwatta", "nawawi"]):
            return "hadith"
        elif any(x in reference for x in ["quran", "ayah", "surah"]):
            return "quran"
        elif "tafsir" in reference or "commentary" in reference:
            return "tafsir"
        elif "seerah" in reference or "biography" in reference:
            return "seerah"
        elif "ethics" in reference or "akhlaq" in reference:
            return "ethics"
        elif "fiqh" in reference or "jurisprudence" in reference:
            return "fiqh"
        elif "dua" in reference or "supplication" in reference:
            return "dua"
        else:
            return "general"
    
    def _format_category_section(self, category: str, results: List[Dict]) -> str:
        """Format a category section with multiple results"""
        
        category_titles = {
            "hadith": ("⭐ Prophetic Traditions (Hadith)", "📖 Authentic Hadith Collections"),
            "quran": ("📖 Quranic Wisdom", "🕌 Divine Guidance"),
            "tafsir": ("📚 Scholarly Interpretation", "Tafsir & Commentary"),
            "seerah": ("📜 Prophetic Biography", "Life Lessons from the Prophet"),
            "ethics": ("🕌 Islamic Ethics & Character", "Building a Righteous Character"),
            "fiqh": ("⚖️ Islamic Jurisprudence", "Practical Islamic Guidance"),
            "dua": ("🤲 Islamic Supplications", "Authentic Duas & Dhikr"),
        }
        
        title, _subtitle = category_titles.get(category, ("📌 Islamic Knowledge", ""))
        section = f"**Evidence ({title}):**\n"
        
        for i, result in enumerate(results[:3], 1):  # Show top 3 per category
            reference = result.get('reference', 'Unknown Source')
            content = result.get('content', '')
            
            # Extract grade/authenticity if present
            grade_match = re.search(r'Grade[:\s]+([^|\n]+)', reference)
            grade = grade_match.group(1).strip() if grade_match else ""
            
            # Format content preview
            content_preview = content[:300] + "..." if len(content) > 300 else content
            
            cleaned_reference = reference.split("—")[0].strip()
            cleaned_reference = cleaned_reference.replace("[Quran Foundation MCP]", "").strip()
            source_line = cleaned_reference if cleaned_reference else "Source"
            if grade:
                source_line = f"{source_line} ({grade})"
            section += f"- {content_preview}\n  ({source_line})\n"
        
        return section
    
    def _extract_key_themes(self, results: List[Dict], kb_results: str) -> str:
        """Extract and format key themes from results"""
        
        # Extract themes using regex patterns
        themes = []
        keywords = [
            r'(faith|iman|taqwa)', r'(mercy|compassion|rahmah)',
            r'(justice|fairness|adl)', r'(knowledge|wisdom|hikma)',
            r'(prayer|salah|ibadah)', r'(charity|zakah|sadaqah)',
            r'(patience|sabr)', r'(forgiveness|afw)', r'(gratitude|shukr)',
            r'(unity|tawheed)', r'(submission|islam)', r'(prophet|nabi)',
        ]
        
        full_text = '\n'.join([r.get('content', '') for r in results])
        
        for keyword in keywords:
            matches = re.findall(keyword, full_text, re.IGNORECASE)
            if matches:
                themes.append(matches[0].capitalize())
        
        unique_themes = sorted(set(themes), key=themes.count, reverse=True)[:8]
        
        if unique_themes:
            return "**Key themes:** " + ", ".join(unique_themes)
        
        return ""
    
    def _create_footer(self, results: List[Dict]) -> str:
        """Create footer with source attribution"""
        
        unique_sources = set()
        for result in results:
            ref = result.get('reference', '')
            source_match = re.search(r'\[([^\]]+)\]', ref)
            if source_match:
                unique_sources.add(source_match.group(1))
        
        source_count = len(results)
        
        return (
            f"**Sources used:** {source_count}\n"
            "May Allah grant you beneficial knowledge and help you act upon it."
        )
    
    def _handle_empty_results(self, query: str) -> str:
        """Handle case when no results are found"""
        return (
            "Assalamu Alaikum wa Rahmatullahi wa Barakatuh.\n\n"
            f"I couldn't find a strong match for: {query}\n"
            "Try a simpler keyword (example: prayer, sabr, wudu, zakat), "
            "or tell me your situation and I will guide you step-by-step."
        )


def format_response_scholarly(
    query: str,
    kb_results: str,
    category: str = "islamic_general",
    include_greeting: bool = True
) -> str:
    """
    Format a response in scholarly deep dive style.
    
    Args:
        query: User query
        kb_results: Knowledge base results string
        category: Query category
        include_greeting: Include Islamic greeting
        
    Returns:
        Formatted response
    """
    formatter = ScholarlyResponseFormatter()
    return formatter.format_scholarly_deep_dive(
        query=query,
        kb_results=kb_results,
        category=category,
        include_greeting=include_greeting
    )


if __name__ == "__main__":
    # Test the formatter
    test_result = """[Source 1] Sahih al-Bukhari [1160] — Grade: Sahih (Default)
    The Prophet Muhammad offered two rak'at, then two rak'at, then two rak'at...
    
[Source 2] Tafsir Ibn Kathir - Quranic Wisdom
    This verse indicates the importance of ritual prayer in Islamic life."""
    
    formatter = ScholarlyResponseFormatter()
    formatted = formatter.format_scholarly_deep_dive(
        query="Tell me about prayer in Islam",
        kb_results=test_result,
        category="hadith"
    )
    print(formatted)

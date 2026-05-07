"""
Intelligent Tool Router - Routes queries to optimal tools
Orchestrates LocalKnowledgeBase, Adhan API, Quran MCP, and other services
100% local processing with intelligent fallback chains
"""

import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

from backend.utils.advanced_query_classifier import (
    QueryCategory,
    ClassifiedQuery,
    get_classifier
)

logger = logging.getLogger("IntelligentRouter")


@dataclass
class ToolResponse:
    """Structured response from tool execution"""
    tool_name: str
    category: str
    result: Any
    confidence: float
    source: str
    metadata: Dict[str, Any] = None
    fallback_used: bool = False
    processing_time_ms: float = 0.0


class IntelligentToolRouter:
    """
    Routes queries to optimal tools based on intelligent classification
    Manages Adhan API, Quran MCP, Local KB, and other services
    """
    
    def __init__(self):
        self.classifier = get_classifier()
        self.logger = logger
        
        # Tool registry - maps categories to tool chains
        self.tool_chains = {
            QueryCategory.PRAYER_TIMES: self._handle_prayer_times,
            QueryCategory.QIBLA: self._handle_qibla,
            QueryCategory.PRAYER_GUIDE: self._handle_prayer_guide,
            QueryCategory.DAILY_ADHKAR: self._handle_daily_adhkar,
            QueryCategory.DUAS: self._handle_duas,
            QueryCategory.SURAH_SPECIFIC: self._handle_surah_specific,
            QueryCategory.QURAN_GENERAL: self._handle_quran_general,
            QueryCategory.HADITH: self._handle_hadith,
            QueryCategory.SUNNAH: self._handle_sunnah,
            QueryCategory.ZAKAT: self._handle_zakat,
            QueryCategory.HAJJ: self._handle_hajj,
            QueryCategory.UMRAH: self._handle_umrah,
            QueryCategory.FASTING: self._handle_fasting,
            QueryCategory.SEERAH: self._handle_seerah,
            QueryCategory.SAHABA: self._handle_sahaba,
            QueryCategory.ISLAMIC_ETHICS: self._handle_islamic_ethics,
            QueryCategory.ASMAUL_HUSNA: self._handle_asmaul_husna,
            QueryCategory.ISLAMIC_CALENDAR: self._handle_islamic_calendar,
            QueryCategory.GENERAL_QUERY: self._handle_general_query,
        }
    
    async def route_and_process(
        self, 
        query: str,
        user_location: Optional[Dict] = None,
        use_synthesis: bool = True,
        quran_translation_lang: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point: Classify query and route to appropriate tools
        
        Args:
            query: User query string
            user_location: Optional location data (lat, lon) for Prayer Times
            use_synthesis: Whether to use local synthesis for response generation
        
        Returns:
            Comprehensive response from best matching tool
        """
        import time
        start_time = time.time()
        
        # Classify query
        classification = self.classifier.classify(query)
        self.logger.info(f"Query routed to: {classification.category.value}")
        
        # Get appropriate tool handler
        tool_handler = self.tool_chains.get(
            classification.category,
            self._handle_general_query
        )
        
        # Execute tool handler
        try:
            response = await tool_handler(
                query=query,
                classification=classification,
                user_location=user_location,
                use_synthesis=use_synthesis,
                quran_translation_lang=quran_translation_lang,
            )
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            response = await self._handle_fallback(query, classification)
        
        processing_time = (time.time() - start_time) * 1000
        response['processing_time_ms'] = processing_time
        response['classification'] = {
            'category': classification.category.value,
            'confidence': classification.confidence,
        }
        
        return response
    
    # ============ PRAYER & WORSHIP TOOLS ============

    def _build_search_query(
        self,
        query: str,
        classification: ClassifiedQuery,
        category: str,
    ) -> str:
        import os
        import json
        import re

        base = (query or "").strip()
        if not base:
            base = category or ""

        defaults: Dict[str, list] = {
            "prayer_guide": ["salah", "namaz", "rakat", "wudu", "takbir", "ruku", "sujud"],
            "daily_adhkar": ["adhkar", "dhikr", "morning", "evening", "remembrance"],
            "duas": ["dua", "supplication", "prophetic", "authentic"],
            "hadith": ["hadith", "sahih", "isnad", "bukhari", "muslim"],
            "sunnah": ["sunnah", "prophetic practice", "manners", "adab"],
            "zakat": ["zakat", "nisab", "sadaqah", "charity", "obligation"],
            "hajj": ["hajj", "pilgrimage", "manasik", "ihram", "tawaf", "sa'i", "arafat"],
            "umrah": ["umrah", "ihram", "tawaf", "sa'i", "miqat"],
            "fasting": ["ramadan", "sawm", "fasting", "suhoor", "iftar", "fidya", "kaffarah"],
            "seerah": ["seerah", "sirah", "prophet Muhammad", "biography", "life", "events"],
            "sahaba": ["sahaba", "companions", "abu bakr", "umar", "uthman", "ali", "aisha"],
            "islamic_ethics": ["akhlaq", "adab", "character", "manners", "morals"],
            "islamic_calendar": ["hijri", "lunar calendar", "islamic months", "ramadan", "dhul hijjah"],
        }

        overrides_raw = (os.getenv("CATEGORY_SEARCH_HINTS_JSON") or "").strip()
        if overrides_raw:
            try:
                overrides = json.loads(overrides_raw)
                if isinstance(overrides, dict):
                    for k, v in overrides.items():
                        if isinstance(k, str) and isinstance(v, list):
                            defaults[k] = [str(x) for x in v if str(x).strip()]
                        elif isinstance(k, str) and isinstance(v, str) and v.strip():
                            defaults[k] = [v.strip()]
            except Exception:
                pass

        extras = []
        for kw in (classification.primary_keywords or [])[:8]:
            extras.append(kw)
        for kw in (classification.secondary_keywords or [])[:8]:
            extras.append(kw)

        entities = classification.extracted_entities or {}
        if isinstance(entities, dict):
            for v in entities.values():
                if isinstance(v, str) and v.strip():
                    extras.append(v.strip())
                elif isinstance(v, list):
                    for item in v[:5]:
                        if isinstance(item, str) and item.strip():
                            extras.append(item.strip())

        hints = defaults.get(category) or []
        extras.extend(hints)

        seen = set()
        parts = [base]
        base_l = base.lower()
        for item in extras:
            s = " ".join(str(item).split()).strip()
            if not s:
                continue
            key = re.sub(r"\s+", " ", s.lower()).strip()
            if not key or key in seen:
                continue
            if key in base_l:
                continue
            seen.add(key)
            parts.append(s)

        return " ".join(parts).strip()
    
    async def _handle_prayer_times(
        self,
        query: str,
        classification: ClassifiedQuery,
        user_location: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Route to Adhan API for prayer times"""
        from backend.tools.enhanced_islamic_tools import get_prayer_times
        
        if not user_location:
            return {
                'response': '📍 Location required for prayer times. Please provide your latitude and longitude.',
                'tool': 'prayer_times',
                'requires_input': True
            }
        
        try:
            lat = user_location.get('latitude')
            lon = user_location.get('longitude')
            
            result = get_prayer_times(latitude=lat, longitude=lon)
            response_text = result.get('text') if isinstance(result, dict) else str(result)
            if isinstance(result, dict) and result.get('error'):
                return {
                    'response': f"⚠️ Could not fetch prayer times: {result.get('error')}",
                    'tool': 'prayer_times',
                    'error': True,
                    'source': 'aladhan_api',
                    'location': user_location,
                }
            
            return {
                'response': response_text,
                'tool': 'prayer_times',
                'source': 'aladhan_api',
                'location': user_location,
                'metadata': {
                    'hijri_date': result.get('hijri'),
                    'method': result.get('method', 'Umm Al-Qura')
                }
            }
        except Exception as e:
            self.logger.error(f"Prayer times error: {e}")
            return {
                'response': f'⚠️ Could not fetch prayer times: {str(e)}',
                'tool': 'prayer_times',
                'error': True
            }

    async def _handle_qibla(
        self,
        query: str,
        classification: ClassifiedQuery,
        user_location: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate Qibla direction from user location"""
        from backend.tools.enhanced_islamic_tools import get_qibla_direction
        
        if not user_location:
            return {
                'response': '📍 Location required for Qibla direction. Please provide your latitude and longitude.',
                'tool': 'qibla',
                'requires_input': True
            }
        
        try:
            lat = user_location.get('latitude')
            lon = user_location.get('longitude')
            result = get_qibla_direction(float(lat), float(lon))
            if isinstance(result, dict) and result.get('error'):
                return {
                    'response': f"⚠️ Could not calculate Qibla direction: {result.get('error')}",
                    'tool': 'qibla',
                    'error': True,
                    'source': 'local_calculation',
                    'location': user_location,
                }
            
            response_text = result.get('text') if isinstance(result, dict) else str(result)
            return {
                'response': response_text,
                'tool': 'qibla',
                'source': 'local_calculation',
                'location': user_location,
                'metadata': {
                    'bearing': result.get('bearing') if isinstance(result, dict) else None,
                    'direction': result.get('direction') if isinstance(result, dict) else None,
                }
            }
        except Exception as e:
            self.logger.error(f"Qibla error: {e}")
            return {
                'response': f'⚠️ Could not calculate Qibla direction: {str(e)}',
                'tool': 'qibla',
                'error': True
            }
    
    async def _handle_prayer_guide(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Route to Local KB for prayer guide"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "prayer_guide"),
            category='prayer_guide'
        )
    
    async def _handle_daily_adhkar(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Route to Local KB for daily adhkar"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "daily_adhkar"),
            category='daily_adhkar'
        )
    
    async def _handle_duas(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Route to Local KB for duas"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "duas"),
            category='duas'
        )
    
    # ============ QURANIC TOOLS ============
    
    async def _handle_surah_specific(
        self,
        query: str,
        classification: ClassifiedQuery,
        use_synthesis: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Surah-specific queries"""
        import re
        import asyncio

        surah_num = classification.extracted_entities.get('surah_number')

        if not surah_num:
            try:
                from backend.utils.intelligent_query_router import parse_surah_query

                surah_num = parse_surah_query(query)
            except Exception:
                surah_num = None
        
        if not surah_num:
            return await self._handle_general_query(query, classification, use_synthesis=use_synthesis, **kwargs)

        q_lower = (query or "").lower()
        wants_text = bool(
            re.search(r"\b(show|read|recite|display|give)\b", q_lower)
        )
        wants_text = wants_text or "full surah" in q_lower or "entire surah" in q_lower

        if wants_text:
            try:
                from backend.utils.quran_mcp_provider import fetch_surah_with_translation

                quran_translation_lang = (kwargs.get("quran_translation_lang") or "").strip().lower()
                if not quran_translation_lang or quran_translation_lang == "auto":
                    quran_translation_lang = "en"

                surah_data = await asyncio.wait_for(
                    fetch_surah_with_translation(
                        surah=surah_num,
                        language=quran_translation_lang,
                        translator="sahih",
                    ),
                    timeout=20.0,
                )

                verses = (
                    surah_data.get("verses")
                    if isinstance(surah_data, dict)
                    else None
                ) or []

                if verses:
                    title = f"Surah {surah_num}"
                    try:
                        from backend.utils.intelligent_query_router import SURAH_NAMES

                        if surah_num in SURAH_NAMES:
                            english, arabic, meaning = SURAH_NAMES[surah_num]
                            title = f"Surah {english} ({meaning}) — {arabic}"
                    except Exception:
                        pass

                    max_show = 30
                    show_verses = verses[:max_show]

                    lines = []
                    lines.append(title)
                    lines.append("")
                    lines.append(f"**Text + {quran_translation_lang.upper()} translation:**")
                    lines.append("")

                    for v in show_verses:
                        ayah = v.get("ayah")
                        arabic_text = (v.get("text") or "").strip()
                        translation = (v.get("translation") or "").strip()
                        if translation:
                            translation = re.sub(r"<sup[^>]*>.*?</sup>", "", translation).strip()
                            translation = re.sub(r"<[^>]+>", "", translation).strip()
                        if not arabic_text and not translation:
                            continue
                        if isinstance(ayah, int):
                            lines.append(f"{surah_num}:{ayah}")
                        if arabic_text:
                            lines.append(arabic_text)
                        if translation:
                            lines.append(f"Translation: {translation}")
                        lines.append("")

                    if len(verses) > max_show:
                        lines.append(
                            f"This surah is long ({len(verses)} verses). "
                            f"I showed the first {max_show}. Tell me a range, e.g. {surah_num}:1-{surah_num}:20."
                        )

                    lines.append("")
                    lines.append("Would you like transliteration or a brief tafsir?")

                    return {
                        'response': "\n".join(lines).strip(),
                        'tool': 'quran_foundation_mcp',
                        'source': 'quran_foundation_mcp',
                        'metadata': {'surah': surah_num, 'verse_count': len(verses)},
                        'synthesis_applied': False
                    }
            except Exception as e:
                self.logger.warning(f"Surah fetch via MCP failed: {e}")

        search_query = f"Surah {surah_num} meaning tafsir themes"
        return await self._query_local_kb(
            query=query,
            search_query=search_query,
            category='surah_specific',
            surah_number=surah_num,
            use_synthesis=use_synthesis
        )
    
    async def _handle_quran_general(
        self,
        query: str,
        classification: ClassifiedQuery,
        use_synthesis: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle general Quran queries - try MCP first, fallback to local KB"""
        
        q_lower = (query or "").lower()

        try:
            import re
            import asyncio
            from backend.utils.quran_mcp_provider import get_quran_mcp

            if any(k in q_lower for k in ["mushaf", "page", "juz"]):
                page_match = re.search(r"\bpage\s+(\d{1,3})\b", q_lower)
                juz_match = re.search(r"\bjuz\s+(\d{1,2})\b", q_lower)
                ayah_key_match = re.search(r"\b(\d{1,3}):(\d{1,3})\b", q_lower)

                mcp = get_quran_mcp()
                await mcp.initialize()
                if page_match:
                    page = int(page_match.group(1))
                    out = await asyncio.wait_for(mcp.show_mushaf(page=page), timeout=8.0)
                    text = (out.get("text") if isinstance(out, dict) else "") or ""
                    if text:
                        return {
                            "response": text,
                            "tool": "quran_foundation_mcp_mushaf",
                            "source": "quran_foundation_mcp",
                            "metadata": {"page": page},
                            "synthesis_applied": False,
                        }
                if juz_match:
                    juz = int(juz_match.group(1))
                    out = await asyncio.wait_for(mcp.show_mushaf(juz=juz), timeout=8.0)
                    text = (out.get("text") if isinstance(out, dict) else "") or ""
                    if text:
                        return {
                            "response": text,
                            "tool": "quran_foundation_mcp_mushaf",
                            "source": "quran_foundation_mcp",
                            "metadata": {"juz": juz},
                            "synthesis_applied": False,
                        }
                if ayah_key_match:
                    s_i = int(ayah_key_match.group(1))
                    a_i = int(ayah_key_match.group(2))
                    out = await asyncio.wait_for(mcp.show_mushaf(surah=s_i, ayah=a_i), timeout=8.0)
                    text = (out.get("text") if isinstance(out, dict) else "") or ""
                    if text:
                        return {
                            "response": text,
                            "tool": "quran_foundation_mcp_mushaf",
                            "source": "quran_foundation_mcp",
                            "metadata": {"surah": s_i, "ayah": a_i},
                            "synthesis_applied": False,
                        }

            if any(k in q_lower for k in ["morphology", "morphological", "root", "lemma", "paradigm", "concordance", "word analysis", "grammar"]):
                ayah_key_match = re.search(r"\b(\d{1,3}:\d{1,3})\b", q_lower)
                arabic_word_match = re.search(r"[\u0600-\u06FF]{2,}", query or "")
                mcp = get_quran_mcp()
                await mcp.initialize()

                lines = []
                if ayah_key_match:
                    ak = ayah_key_match.group(1)
                    morph = await asyncio.wait_for(mcp.fetch_word_morphology(ayah_key=ak), timeout=10.0)
                    res = (morph.get("result") if isinstance(morph, dict) else None) or {}
                    words = res.get("words") if isinstance(res, dict) else None
                    if isinstance(words, list) and words:
                        lines.append(f"Word morphology for {ak}:")
                        lines.append("")
                        for w in words[:12]:
                            if not isinstance(w, dict):
                                continue
                            pos = ((w.get("grammatical_features") or {}).get("part_of_speech") if isinstance(w.get("grammatical_features"), dict) else None) or ""
                            root = (w.get("root") or "").strip()
                            lemma = (w.get("lemma") or "").strip()
                            simple = (w.get("text_simple") or "").strip()
                            uth = (w.get("text_uthmani") or "").strip()
                            trn = (w.get("translation") or "").strip()
                            if not (uth or simple):
                                continue
                            label = uth or simple
                            details = []
                            if pos:
                                details.append(pos)
                            if root:
                                details.append(f"root: {root}")
                            if lemma:
                                details.append(f"lemma: {lemma}")
                            if trn:
                                details.append(f"meaning: {trn}")
                            if details:
                                lines.append(f"- {label} ({'; '.join(details)})")
                            else:
                                lines.append(f"- {label}")
                        lines.append("")
                        lines.append("If you want, ask: “show concordance for word 1” or “root concordance for <root>”.")
                elif arabic_word_match:
                    word = arabic_word_match.group(0)
                    morph = await asyncio.wait_for(mcp.fetch_word_morphology(word=word), timeout=10.0)
                    res = (morph.get("result") if isinstance(morph, dict) else None) or {}
                    words = res.get("words") if isinstance(res, dict) else None
                    if isinstance(words, list) and words:
                        w = words[0] if isinstance(words[0], dict) else {}
                        root = (w.get("root") or "").strip()
                        lemma = (w.get("lemma") or "").strip()
                        trn = (w.get("translation") or "").strip()
                        lines.append("Word morphology (first occurrence):")
                        lines.append(f"- Word: {word}")
                        if trn:
                            lines.append(f"- Meaning: {trn}")
                        if root:
                            lines.append(f"- Root: {root}")
                        if lemma:
                            lines.append(f"- Lemma: {lemma}")

                if lines:
                    return {
                        "response": "\n".join(lines).strip(),
                        "tool": "quran_foundation_mcp_morphology",
                        "source": "quran_foundation_mcp",
                        "metadata": {"query": query},
                        "synthesis_applied": False,
                    }
        except Exception:
            pass

        # Try Quran Foundation MCP first
        try:
            from backend.utils.quran_mcp_provider import search_quran_knowledge
            
            quran_translation_lang = (kwargs.get("quran_translation_lang") or "").strip().lower()
            include_translations = ["en", "ur"]
            if quran_translation_lang:
                include_translations = [quran_translation_lang, "en"]

            result = await search_quran_knowledge(
                query,
                include_tafsir=True,
                include_translations=include_translations,
            )
            verses = (
                (result.get("quran_text") or {}).get("results") if isinstance(result, dict) else None
            ) or []

            if verses:
                formatted_blocks = []
                tafsir_map = result.get("tafsir") if isinstance(result, dict) else None
                if not isinstance(tafsir_map, dict):
                    tafsir_map = {}

                for i, verse in enumerate(verses[:5], 1):
                    surah = verse.get("surah") or verse.get("chapter") or verse.get("surah_number")
                    ayah = verse.get("ayah") or verse.get("verse") or verse.get("ayah_number")
                    ayah_key = verse.get("ayah_key") or (
                        f"{surah}:{ayah}" if surah and ayah else None
                    )
                    reference = f"Quran {surah}:{ayah} [Quran Foundation MCP]"
                    text = (verse.get("text") or "").strip()
                    translation = (verse.get("translation") or "").strip()
                    translations = verse.get("translations")
                    content_parts = []
                    if text:
                        content_parts.append(text)
                    if isinstance(translations, list) and translations:
                        for t in translations[:2]:
                            if not isinstance(t, dict):
                                continue
                            t_text = (t.get("text") or "").strip()
                            if not t_text:
                                continue
                            t_lang = (t.get("lang") or "").strip().lower()
                            label = f"Translation ({t_lang})" if t_lang else "Translation"
                            content_parts.append(f"{label}: {t_text}")
                    elif translation:
                        content_parts.append(f"Translation: {translation}")

                    if isinstance(ayah_key, str) and ayah_key in tafsir_map:
                        by_ed = tafsir_map.get(ayah_key)
                        if isinstance(by_ed, dict) and by_ed:
                            for ed_id, tafsir_text in list(by_ed.items())[:1]:
                                t = str(tafsir_text or "").strip()
                                if t:
                                    content_parts.append(
                                        f"Tafsir ({ed_id}): {t[:900]}"
                                    )
                    content = "\n".join(content_parts).strip()
                    if content:
                        formatted_blocks.append(f"[Source {i}] {reference}")
                        formatted_blocks.append(content)
                        formatted_blocks.append("")

                if len((query or "").split()) <= 3:
                    try:
                        from backend.utils.quran_mcp_provider import explore_quran_theme

                        theme_data = await explore_quran_theme(query)
                        theme_verses = theme_data.get("verses") if isinstance(theme_data, dict) else None
                        if isinstance(theme_verses, list) and theme_verses:
                            base_idx = len([x for x in formatted_blocks if isinstance(x, str) and x.startswith("[Source ")])
                            for j, v in enumerate(theme_verses[:3], 1):
                                if not isinstance(v, dict):
                                    continue
                                s2 = v.get("surah") or v.get("chapter") or v.get("surah_number")
                                a2 = v.get("ayah") or v.get("verse") or v.get("ayah_number")
                                t2 = (v.get("text") or "").strip()
                                tr2 = (v.get("translation") or "").strip()
                                if not (s2 and a2 and (t2 or tr2)):
                                    continue
                                ref2 = f"Related Quran {s2}:{a2} [Quran Foundation MCP]"
                                parts2 = []
                                if t2:
                                    parts2.append(t2)
                                if tr2:
                                    parts2.append(f"Translation: {tr2}")
                                idx = base_idx + j
                                formatted_blocks.append(f"[Source {idx}] {ref2}")
                                formatted_blocks.append("\n".join(parts2).strip())
                                formatted_blocks.append("")
                    except Exception:
                        pass

                mcp_data = "\n".join(formatted_blocks).strip()
                
                # Apply scholarly formatting to MCP results
                if use_synthesis:
                    from backend.utils.scholarly_response_formatter import format_response_scholarly
                    self.logger.info("✨ Applying scholarly formatting to Quran MCP results")
                    formatted_response = format_response_scholarly(
                        query=query,
                        kb_results=mcp_data,
                        category='quran_general',
                        include_greeting=True
                    )
                else:
                    formatted_response = mcp_data
                
                return {
                    'response': formatted_response,
                    'tool': 'quran_foundation_mcp',
                    'source': 'quran_foundation_mcp',
                    'metadata': {'query': query, 'verse_count': len(verses), 'translation_lang': quran_translation_lang or 'en'},
                    'synthesis_applied': use_synthesis
                }
        except Exception as e:
            self.logger.warning(f"Quran MCP failed: {e}, falling back to local KB")
        
        # Fallback to local knowledge base
        return await self._query_local_kb(
            query=query,
            search_query=query,
            category='quran_general',
            use_synthesis=use_synthesis
        )
    
    # ============ HADITH & SUNNAH TOOLS ============
    
    async def _handle_hadith(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Hadith queries - local KB"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "hadith"),
            category='hadith'
        )
    
    async def _handle_sunnah(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Sunnah queries - local KB"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "sunnah"),
            category='sunnah'
        )
    
    # ============ RELIGIOUS OBLIGATIONS ============
    
    async def _handle_zakat(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Zakat queries - use calculator if amounts provided"""
        from backend.tools.enhanced_islamic_tools import calculate_zakat
        
        # Try to extract amounts from query
        numeric_param = classification.numeric_param
        
        # If we have numeric parameters, try to calculate
        if numeric_param:
            result = calculate_zakat(cash=numeric_param)
            return {
                'response': result,
                'tool': 'zakat_calculator',
                'source': 'local_calculation',
                'metadata': {'amount': numeric_param}
            }
        
        # Otherwise, provide general information
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "zakat"),
            category='zakat'
        )
    
    async def _handle_hajj(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Hajj queries - local KB"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "hajj"),
            category='hajj'
        )
    
    async def _handle_umrah(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Umrah queries - local KB"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "umrah"),
            category='umrah'
        )
    
    async def _handle_fasting(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Fasting queries - local KB"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "fasting"),
            category='fasting'
        )
    
    # ============ ISLAMIC HISTORY & BIOGRAPHY ============
    
    async def _handle_seerah(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Seerah (Prophet's biography) queries - local KB"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "seerah"),
            category='seerah'
        )
    
    async def _handle_sahaba(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Sahaba (Companions) queries - local KB"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "sahaba"),
            category='sahaba'
        )
    
    # ============ ISLAMIC KNOWLEDGE ============
    
    async def _handle_islamic_ethics(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Islamic Ethics queries - local KB"""
        return await self._query_local_kb(
            query=query,
            search_query=self._build_search_query(query, classification, "islamic_ethics"),
            category='islamic_ethics'
        )
    
    async def _handle_asmaul_husna(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Asmaul Husna (99 Names of Allah) queries - local curated data + KB fallback"""
        try:
            import json
            import re
            import os
            from pathlib import Path

            data_path = (
                Path(__file__).resolve().parents[1]
                / "knowledge"
                / "data"
                / "99_names_of_allah_full.json"
            )
            if not data_path.exists():
                raise FileNotFoundError(str(data_path))

            payload = json.loads(data_path.read_text(encoding="utf-8"))
            items = payload.get("data") if isinstance(payload, dict) else None
            if not isinstance(items, list) or not items:
                raise ValueError("Invalid names dataset")

            q = (query or "").lower()

            def _norm_ascii(s: str) -> str:
                s = (s or "").lower()
                s = re.sub(r"[^a-z0-9]+", "", s)
                return s

            def _looks_arabic(s: str) -> bool:
                return bool(re.search(r"[\u0600-\u06FF]", s or ""))

            default_limit = int(os.getenv("ASMAUL_HUSNA_DEFAULT_LIMIT", "12"))
            max_limit = int(os.getenv("ASMAUL_HUSNA_MAX_LIMIT", "99"))
            default_limit = max(3, min(default_limit, max_limit))

            requested_numbers = [int(n) for n in re.findall(r"\b(\d{1,3})\b", q)]
            wants_all = bool(re.search(r"\b(full|complete|all|entire|whole)\b", q))
            limit = max_limit if wants_all else (max(requested_numbers) if requested_numbers else default_limit)
            limit = max(3, min(limit, max_limit))

            needle = None
            for token in ["meaning of", "what is", "who is", "define", "explain"]:
                if token in q:
                    needle = q.split(token, 1)[1].strip()
                    break
            if not needle and "al-" in q:
                needle = q
            if needle:
                key = (needle or "").strip()
                key_ascii = _norm_ascii(key)
                hit = None
                for it in items:
                    ar_name = (it.get("name") or "").strip()
                    tr = (it.get("transliteration") or "").strip()
                    en = ((it.get("en") or {}).get("meaning") or "").strip()
                    desc = ((it.get("en") or {}).get("desc") or "").strip()

                    if _looks_arabic(key) and key in ar_name:
                        hit = it
                        break

                    tr_ascii = _norm_ascii(tr)
                    en_ascii = _norm_ascii(en)
                    if key_ascii and (key_ascii in tr_ascii or key_ascii in en_ascii):
                        hit = it
                        break
                    if key and (key.lower() in (desc or "").lower()):
                        hit = it
                        break
                if hit:
                    ar = hit.get("name") or ""
                    tr = hit.get("transliteration") or ""
                    meaning = ((hit.get("en") or {}).get("meaning") or "").strip()
                    desc = ((hit.get("en") or {}).get("desc") or "").strip()
                    found = (hit.get("found") or "").strip()

                    parts = []
                    parts.append("1) Answer")
                    parts.append(f"{ar} — {tr}")
                    if meaning:
                        parts.append(f"Meaning: {meaning}")
                    if desc:
                        parts.append(desc)
                    if found:
                        parts.append(f"Quran references: {found}")
                    parts.append("")
                    parts.append("2) Key points")
                    parts.append("- Learning Allah’s Names strengthens iman and improves dua and character.")
                    parts.append("- Try to reflect the meaning in daily actions (with humility).")
                    parts.append("- Use the Name in dua: “Ya Allah, You are …, so grant me …”.")
                    parts.append("")
                    parts.append("3) Next step")
                    parts.append("Pick 1 Name today, memorize its meaning, and use it in dua for 7 days.")
                    parts.append("")
                    parts.append("4) Sources")
                    parts.append("- [Source 1] Local Asma’ul Husna dataset (99_names_of_allah_full.json)")

                    return {
                        "response": "\n".join(parts).strip(),
                        "tool": "asmaul_husna_dataset",
                        "source": "local_kb",
                        "query_category": "asmaul_husna",
                        "result_count": 1,
                        "error": False,
                        "synthesis_applied": False,
                        "synthesis_used": False,
                        "local_llm_used": False,
                        "local_llm_backend": None,
                    }

            sample = []
            tokens = [t for t in re.findall(r"[a-zA-Z']+", q) if len(t) > 3]
            stop = {"show", "list", "names", "name", "allah", "asmaul", "husna", "beautiful"}
            token_set = set(t.lower() for t in tokens if t.lower() not in stop)
            ranked = []
            for it in items:
                ar = (it.get("name") or "").strip()
                tr = (it.get("transliteration") or "").strip()
                en = ((it.get("en") or {}).get("meaning") or "").strip()
                desc = ((it.get("en") or {}).get("desc") or "").strip()
                found = (it.get("found") or "").strip()
                number = it.get("number") or 0
                text_blob = f"{tr} {en} {desc}".lower()
                score = sum(1 for t in token_set if t in text_blob)
                ranked.append((score, int(number) if isinstance(number, int) else 0, ar, tr, en, desc, found))

            max_score = max((r[0] for r in ranked), default=0)
            if max_score <= 0:
                ranked.sort(key=lambda x: x[1])
            else:
                ranked.sort(key=lambda x: (-x[0], x[1]))
            picked = ranked[:limit]

            for _score, _number, ar, tr, meaning, _desc, found in picked:
                if not (ar or tr or meaning):
                    continue
                line = f"{ar} — {tr}: {meaning}".strip(": ").strip()
                if found:
                    line += f" (Quran: {found})"
                sample.append(line)

            parts = []
            parts.append("1) Answer")
            parts.append(
                "Asma’ul Husna are Allah’s beautiful Names (His perfect attributes). "
                "Learning them helps your heart know Allah better, improves your dua, and strengthens iman."
            )
            parts.append("")
            parts.append(f"Here are {len(sample)} Names (Arabic — transliteration — meaning):")
            for s in sample:
                parts.append(f"- {s}")
            parts.append("")
            parts.append("2) Key points")
            parts.append("- Use the Names in dua: “Ya Allah, Ya Ar-Rahman, have mercy on me…”.")
            parts.append("- Reflect the meaning in your character (mercy, justice, patience).")
            parts.append("- Learn slowly: 1 Name per week with meaning + action.")
            parts.append("")
            parts.append("3) Next step")
            parts.append("Say: “show 20 names”, “show full 99”, or “meaning of Al-Hakeem / الرَّحِيمُ”.")
            parts.append("")
            parts.append("4) Sources")
            parts.append("- [Source 1] Local Asma’ul Husna dataset (99_names_of_allah_full.json)")

            return {
                "response": "\n".join(parts).strip(),
                "tool": "asmaul_husna_dataset",
                "source": "local_kb",
                "query_category": "asmaul_husna",
                "result_count": max(1, len(sample)),
                "error": False,
                "synthesis_applied": False,
                "synthesis_used": False,
                "local_llm_used": False,
                "local_llm_backend": None,
            }
        except Exception:
            return await self._query_local_kb(
                query=query,
                search_query=self._build_search_query(query, classification, "asmaul_husna"),
                category="asmaul_husna",
            )
    
    async def _handle_islamic_calendar(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Islamic Calendar queries"""
        from backend.tools.enhanced_islamic_tools import get_hijri_date
        
        try:
            result = get_hijri_date()
            return {
                'response': result,
                'tool': 'hijri_calendar',
                'source': 'local_calculation',
            }
        except Exception as e:
            self.logger.warning(f"Hijri calendar error: {e}")
            return await self._query_local_kb(
                query=query,
                search_query=self._build_search_query(query, classification, "islamic_calendar"),
                category='islamic_calendar'
            )
    
    # ============ FALLBACK & GENERAL ============
    
    async def _handle_general_query(
        self,
        query: str,
        classification: ClassifiedQuery,
        use_synthesis: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Default handler - query local knowledge base"""
        return await self._query_local_kb(
            query=query,
            search_query=query,
            category='general',
            use_synthesis=use_synthesis
        )
    
    async def _handle_fallback(
        self,
        query: str,
        classification: ClassifiedQuery,
        **kwargs
    ) -> Dict[str, Any]:
        """Emergency fallback response"""
        return {
            'response': f'I encountered an error processing: "{query}". Please try rephrasing your question.',
            'tool': 'fallback',
            'error': True,
            'source': 'fallback'
        }
    
    # ============ HELPER METHODS ============
    
    async def _query_local_kb(
        self,
        query: str,
        search_query: str,
        category: str,
        use_synthesis: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Query local knowledge base with scholarly formatting and synthesis"""
        try:
            import asyncio
            import re
            from backend.knowledge.memory_optimized_loader import (
                get_memory_optimized_loader,
            )
            from backend.utils.scholarly_response_formatter import format_response_scholarly
            
            kb = get_memory_optimized_loader()
            kb_results = kb.search(search_query, k=15)

            try:
                from backend.utils.quran_mcp_provider import search_quran_knowledge

                lang = (kwargs.get("quran_translation_lang") or "").strip().lower()
                if lang == "auto":
                    lang = "en"
                lang = lang or None

                mcp_result = await asyncio.wait_for(
                    search_quran_knowledge(
                        query,
                        include_tafsir=False,
                        include_translations=[lang] if lang else None,
                    ),
                    timeout=8.0,
                )
                verses = (
                    (mcp_result.get("quran_text") or {}).get("results")
                    if isinstance(mcp_result, dict)
                    else []
                )
                verses = verses or []
                if verses:
                    label_lang = (lang or "en").upper()
                    blocks = []
                    for i, verse in enumerate(verses[:2], 1):
                        surah = verse.get("surah")
                        ayah = verse.get("ayah")
                        ref = f"Quran {surah}:{ayah} [Quran Foundation MCP]"
                        text = (verse.get("text") or "").strip()
                        translation = (verse.get("translation") or "").strip()
                        content_parts = []
                        if text:
                            content_parts.append(text)
                        if translation:
                            content_parts.append(f"Translation ({label_lang}): {translation}")
                        content = "\n".join(content_parts).strip()
                        if content:
                            blocks.append(f"[Source MCP-{i}] {ref}")
                            blocks.append(content)
                            blocks.append("")

                    if blocks:
                        kb_results = (
                            kb_results.rstrip()
                            + "\n\n"
                            + "\n".join(blocks).strip()
                        )
            except Exception:
                pass
            
            # Check if search was successful
            is_error = kb_results.startswith('❌') or kb_results.startswith('Error')
            source_count = 0
            if not is_error and isinstance(kb_results, str):
                source_count = kb_results.count("[Source ")
            
            # Apply scholarly formatting to enhance presentation
            if not is_error and use_synthesis:
                self.logger.info(f"✨ Applying scholarly formatting to {category} results")
                formatted_response = format_response_scholarly(
                    query=query,
                    kb_results=kb_results,
                    category=category,
                    include_greeting=True
                )
                local_llm_used = False
                local_llm_backend = None
                try:
                    from backend.utils.llm_provider import (
                        build_evidence_pack,
                        get_local_llm_status,
                        synthesize_from_evidence,
                    )

                    status = get_local_llm_status()
                    local_llm_backend = status.get("backend")
                    packed_evidence = build_evidence_pack(
                        kb_results,
                        max_sources=8,
                        max_chars_per_source=1000,
                    )
                    synthesized = synthesize_from_evidence(
                        question=query,
                        evidence=packed_evidence,
                        user_profile=None,
                    )
                    if isinstance(synthesized, str) and synthesized.strip():
                        formatted_response = synthesized
                        local_llm_used = True
                except Exception:
                    pass
            else:
                formatted_response = kb_results
                local_llm_used = False
                local_llm_backend = None
            
            return {
                'response': formatted_response,
                'tool': 'local_knowledge_base',
                'source': 'local_kb' if not is_error else 'error',
                'query_category': category,
                'result_count': 0 if is_error else max(1, source_count),
                'error': is_error,
                'synthesis_applied': not is_error and use_synthesis,
                'synthesis_used': bool(local_llm_used),
                'local_llm_used': bool(local_llm_used),
                'local_llm_backend': local_llm_backend,
            }
            
        except Exception as e:
            import traceback
            self.logger.error(f"KB Query error: {e}\n{traceback.format_exc()}")
            return {
                'response': f"Error querying knowledge base: {str(e)}",
                'tool': 'local_knowledge_base',
                'source': 'error',
                'query_category': category,
                'result_count': 0,
                'error': True
            }


def get_tool_router() -> IntelligentToolRouter:
    """Get singleton tool router instance"""
    global _router
    if '_router' not in globals():
        _router = IntelligentToolRouter()
    return _router

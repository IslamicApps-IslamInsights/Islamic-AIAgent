"""
Quran Foundation MCP Provider
Integrates with the Quran Foundation MCP server at https://mcp.quran.ai
Provides access to authentic Quranic data, translations, and tafsir.
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import httpx

logger = logging.getLogger("QuranMCP")

# Quran Foundation MCP Server Configuration
QURAN_MCP_URL = "https://mcp.quran.ai"

# Cache for MCP resources
_mcp_cache: Dict[str, Any] = {
    "editions": {},
    "grounding_rules": None,
    "grounding_nonce": None,
    "last_updated": None
}

_surah_meta_cache: Optional[Dict[int, int]] = None


def _load_surah_ayah_counts() -> Dict[int, int]:
    global _surah_meta_cache
    if _surah_meta_cache is not None:
        return _surah_meta_cache

    counts: Dict[int, int] = {}
    meta_path = (
        Path(__file__).resolve().parents[1]
        / "knowledge"
        / "data"
        / "quran_surah_metadata_114.json"
    )
    try:
        raw = json.loads(meta_path.read_text(encoding="utf-8"))
        data = raw.get("data") if isinstance(raw, dict) else None
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                num = item.get("number")
                ayahs = item.get("numberOfAyahs")
                try:
                    n_i = int(num)
                    a_i = int(ayahs)
                except Exception:
                    continue
                if 1 <= n_i <= 114 and a_i > 0:
                    counts[n_i] = a_i
    except Exception:
        counts = {}

    _surah_meta_cache = counts
    return counts


def _surah_range_ayahs(surah: int, ayah: Optional[int]) -> str:
    if ayah:
        return f"{surah}:{ayah}"
    counts = _load_surah_ayah_counts()
    end = counts.get(int(surah), 0) or 0
    if end <= 0:
        return f"{surah}:1"
    return f"{surah}:1-{end}"


def _extract_tool_json(payload: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not isinstance(payload, dict):
        return None, "Unexpected MCP payload type"
    if payload.get("isError") is True:
        return None, "MCP tool returned isError"

    content = payload.get("content")
    if not isinstance(content, list) or not content:
        return None, "MCP tool returned empty content"

    first = content[0] if isinstance(content[0], dict) else None
    text = (first or {}).get("text")
    if not isinstance(text, str) or not text.strip():
        return None, "MCP tool returned non-text content"

    try:
        return json.loads(text), None
    except Exception:
        return None, "Failed to parse MCP JSON text"


def _strip_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = text
    cleaned = cleaned.replace("\u200f", "").replace("\u200e", "")
    cleaned = cleaned.replace("\xa0", " ")
    cleaned = cleaned.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    import re
    cleaned = re.sub(r"<sup[^>]*>.*?</sup>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<[^>]+>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def _best_effort_pick_edition_id(editions: List[Dict[str, Any]], preferred: str) -> Optional[str]:
    if not preferred:
        return None
    p = preferred.strip().lower()
    if not p:
        return None

    def score(ed: Dict[str, Any]) -> int:
        eid = (ed.get("edition_id") or "").lower()
        code = (ed.get("code") or "").lower()
        name = (ed.get("name") or "").lower()
        author = (ed.get("author") or "").lower()
        blob = " ".join([eid, code, name, author]).strip()
        s = 0
        if p == eid or p == code:
            s += 100
        if p in blob:
            s += 50
        for token in p.replace("-", " ").split():
            if token and token in blob:
                s += 5
        return s

    best = None
    best_score = 0
    for ed in editions:
        if not isinstance(ed, dict):
            continue
        s = score(ed)
        if s > best_score:
            best_score = s
            best = ed.get("edition_id")
    return best if best_score > 0 else None


def _normalize_results(json_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = json_obj.get("results")
    if not isinstance(results, dict):
        return []
    out: List[Dict[str, Any]] = []
    for _edition, items in results.items():
        if not isinstance(items, list):
            continue
        for it in items:
            if not isinstance(it, dict):
                continue
            ayah_key = it.get("ayah")
            text = (it.get("text") or "").strip()
            if isinstance(ayah_key, str) and ":" in ayah_key:
                try:
                    s_str, a_str = ayah_key.split(":", 1)
                    s_i = int(s_str)
                    a_i = int(a_str)
                except Exception:
                    s_i = None
                    a_i = None
            else:
                s_i = None
                a_i = None
            if text:
                out.append({"surah": s_i, "ayah": a_i, "text": text})
    return out


class QuranFoundationMCP:
    """
    Wrapper for Quran Foundation MCP server interactions.
    Provides methods for searching, fetching, and analyzing Quranic content.
    """

    def __init__(self):
        self.base_url = QURAN_MCP_URL
        self.logger = logger
        self._session_id: Optional[str] = None
        self._next_id = 1

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Islamic-AIAgent/1.0",
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        return headers

    async def _post_jsonrpc(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.base_url + "/",
                json=payload,
                headers=self._headers(),
                follow_redirects=True,
            )
        response.raise_for_status()

        if not self._session_id:
            session_id = response.headers.get("mcp-session-id")
            if session_id:
                self._session_id = session_id

        content_type = (response.headers.get("content-type") or "").lower()
        if "text/event-stream" not in content_type:
            try:
                return response.json()
            except Exception:
                return {"error": "Unexpected non-JSON response"}

        result: Optional[Dict[str, Any]] = None
        for line in response.text.splitlines():
            if not line:
                continue
            if line.startswith("data:"):
                data = line[len("data:"):].strip()
                if not data:
                    continue
                try:
                    result = httpx.Response(200, content=data).json()
                except Exception:
                    continue

        if result is None:
            return {"error": "Empty MCP response"}
        return result

    async def initialize(self):
        """Initialize async HTTP client for MCP communication."""
        if not self._session_id:
            init_id = self._next_id
            self._next_id += 1
            init_payload = {
                "jsonrpc": "2.0",
                "id": init_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "Islamic-AIAgent",
                        "version": "1.0",
                    },
                },
            }
            _ = await self._post_jsonrpc(init_payload)

            notify_payload = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    await client.post(
                        self.base_url + "/",
                        json=notify_payload,
                        headers=self._headers(),
                        follow_redirects=True,
                    )
            except Exception:
                pass

        if _mcp_cache.get("grounding_nonce") is None:
            call_id = self._next_id
            self._next_id += 1
            payload = {
                "jsonrpc": "2.0",
                "id": call_id,
                "method": "tools/call",
                "params": {"name": "fetch_grounding_rules", "arguments": {}},
            }
            rules = await self._post_jsonrpc(payload)
            nonce = None
            if isinstance(rules, dict):
                nonce = rules.get("grounding_nonce")
            if nonce:
                _mcp_cache["grounding_nonce"] = nonce
                _mcp_cache["grounding_rules"] = rules

        self.logger.info("✅ Quran Foundation MCP initialized")

    async def close(self):
        """Close the async HTTP client."""
        return None

    async def list_tools(self) -> Dict[str, Any]:
        await self.initialize()
        call_id = self._next_id
        self._next_id += 1
        payload = {"jsonrpc": "2.0", "id": call_id, "method": "tools/list", "params": {}}
        return await self._post_jsonrpc(payload)

    async def call_mcp_method(
        self,
        method: str,
        **params
    ) -> Dict[str, Any]:
        """
        Call an MCP method on the Quran Foundation server.
        
        Args:
            method: The tool name, for example:
                - fetch_grounding_rules
                - search_quran
            **params: Method parameters
            
        Returns:
            Response from the MCP server
        """
        try:
            await self.initialize()
            call_id = self._next_id
            self._next_id += 1

            arguments = dict(params)
            nonce = _mcp_cache.get("grounding_nonce")
            if nonce and method not in (
                "fetch_grounding_rules",
                "fetch_skill_guide",
            ):
                arguments.setdefault("grounding_nonce", nonce)

            payload = {
                "jsonrpc": "2.0",
                "id": call_id,
                "method": "tools/call",
                "params": {"name": method, "arguments": arguments},
            }

            self.logger.debug(f"🔄 Calling MCP tool: {method}")
            result = await self._post_jsonrpc(payload)

            if "error" in result:
                return {"error": result.get("error")}

            return result.get("result", result)
        except httpx.HTTPError as e:
            self.logger.error(f"❌ HTTP Error calling MCP: {e}")
            return {"error": str(e)}
        except Exception as e:
            self.logger.error(f"❌ Error calling MCP method {method}: {e}")
            return {"error": str(e)}

    async def fetch_grounding_rules(self) -> Dict[str, Any]:
        """
        Fetch grounding rules from Quran Foundation.
        These define the proper way to reference Quranic content.
        
        Returns:
            Grounding rules metadata
        """
        if _mcp_cache["grounding_rules"]:
            return _mcp_cache["grounding_rules"]

        result = await self.call_mcp_method("fetch_grounding_rules")
        if "error" not in result:
            _mcp_cache["grounding_rules"] = result
        return result

    async def list_editions(
        self,
        edition_type: Any,
        lang: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List all available Quranic editions and translations.
        
        Returns:
            List of editions with metadata
        """
        cache_key = f"{edition_type}:{lang or ''}"
        cached = (_mcp_cache.get("editions") or {}).get(cache_key)
        if cached:
            return cached

        params: Dict[str, Any] = {"edition_type": edition_type}
        if lang:
            params["lang"] = lang
        result = await self.call_mcp_method("list_editions", **params)
        if "error" not in result:
            _mcp_cache["editions"][cache_key] = result
        return result

    async def search_quran(
        self,
        query: str,
        translations: Optional[Any] = None,
        surah: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search the Quran for a specific query across all surahs.
        
        Args:
            query: Search term or phrase
            edition: Quran edition (default: en.sahih - Sahih International)
            language: Filter by language code
            
        Returns:
            Search results with matching verses
        """
        params: Dict[str, Any] = {"query": query}
        if translations is not None:
            params["translations"] = translations
        if surah is not None:
            params["surah"] = surah

        return await self.call_mcp_method("search_quran", **params)

    async def fetch_quran(
        self,
        surah: int,
        ayah: Optional[int] = None,
        editions: Any = "ar-simple-clean"
    ) -> Dict[str, Any]:
        """
        Fetch specific Quranic verses.
        
        Args:
            surah: Surah (chapter) number (1-114)
            ayah: Specific ayah (verse) number, or None for entire surah
            edition: Quran edition
            
        Returns:
            Quranic content
        """
        ayahs = _surah_range_ayahs(surah, ayah)
        payload = await self.call_mcp_method(
            "fetch_quran",
            ayahs=ayahs,
            editions=editions,
        )
        json_obj, err = _extract_tool_json(payload)
        if err or not json_obj:
            return {"error": err or "fetch_quran failed", "raw": payload}
        return {
            "ayahs": json_obj.get("ayahs"),
            "results": _normalize_results(json_obj),
            "raw": json_obj,
        }

    async def fetch_translation(
        self,
        surah: int,
        ayah: Optional[int] = None,
        language: str = "en",
        translator: str = "abdel haleem"
    ) -> Dict[str, Any]:
        """
        Fetch translation of specific Quranic verses.
        
        Args:
            surah: Surah number
            ayah: Specific ayah, or None for entire surah
            language: Language code (en, ar, fr, etc.)
            translator: Translator identifier
            
        Returns:
            Translated content
        """
        ayahs = _surah_range_ayahs(surah, ayah)
        edition_selector: Any = translator.strip() if isinstance(translator, str) else None
        if not edition_selector:
            edition_selector = language

        try:
            ed_payload = await self.list_editions("translation", lang=language)
            ed_obj, ed_err = _extract_tool_json(ed_payload)
            if not ed_err and ed_obj:
                eds = ed_obj.get("editions") or []
                picked = _best_effort_pick_edition_id(eds, str(edition_selector))
                if picked:
                    edition_selector = picked
        except Exception:
            pass

        payload = await self.call_mcp_method(
            "fetch_translation",
            ayahs=ayahs,
            editions=edition_selector,
        )
        json_obj, err = _extract_tool_json(payload)
        if err or not json_obj:
            return {"error": err or "fetch_translation failed", "raw": payload}
        return {
            "ayahs": json_obj.get("ayahs"),
            "results": _normalize_results(json_obj),
            "raw": json_obj,
        }

    async def fetch_tafsir(
        self,
        surah: int,
        ayah: Optional[int] = None,
        tafsir_type: str = "ibn kathir"
    ) -> Dict[str, Any]:
        """
        Fetch Tafsir (Islamic exegesis) for Quranic verses.
        
        Args:
            surah: Surah number
            ayah: Specific ayah, or None for entire surah
            tafsir_type: Type of tafsir (ibn_kathir, al_tabari, etc.)
            
        Returns:
            Tafsir content
        """
        ayahs = _surah_range_ayahs(surah, ayah)
        edition_selector: Any = tafsir_type.strip() if isinstance(tafsir_type, str) else None
        if not edition_selector:
            edition_selector = "ar-ibn-kathir"

        try:
            ed_payload = await self.list_editions("tafsir", lang=None)
            ed_obj, ed_err = _extract_tool_json(ed_payload)
            if not ed_err and ed_obj:
                eds = ed_obj.get("editions") or []
                picked = _best_effort_pick_edition_id(eds, str(edition_selector))
                if picked:
                    edition_selector = picked
        except Exception:
            pass

        payload = await self.call_mcp_method(
            "fetch_tafsir",
            ayahs=ayahs,
            editions=edition_selector,
        )
        json_obj, err = _extract_tool_json(payload)
        if err or not json_obj:
            return {"error": err or "fetch_tafsir failed", "raw": payload}
        by_edition = json_obj.get("results") if isinstance(json_obj, dict) else None
        cleaned: Dict[str, str] = {}
        if isinstance(by_edition, dict):
            for ed_id, blocks in by_edition.items():
                if isinstance(blocks, dict):
                    t = _strip_html(blocks.get("text") or "")
                    if t:
                        cleaned[str(ed_id)] = t
                elif isinstance(blocks, list) and blocks:
                    first = blocks[0] if isinstance(blocks[0], dict) else None
                    t = _strip_html((first or {}).get("text") or "")
                    if t:
                        cleaned[str(ed_id)] = t

        return {"ayahs": json_obj.get("ayahs"), "tafsir": cleaned, "raw": json_obj}

    async def fetch_word_morphology(
        self,
        ayah_key: Optional[str] = None,
        word_position: Optional[int] = None,
        word_text: Optional[str] = None,
        word: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = await self.call_mcp_method(
            "fetch_word_morphology",
            ayah_key=ayah_key,
            word_position=word_position,
            word_text=word_text,
            word=word,
        )
        json_obj, err = _extract_tool_json(payload)
        if err or not json_obj:
            return {"error": err or "fetch_word_morphology failed", "raw": payload}
        return {"result": json_obj}

    async def fetch_word_concordance(
        self,
        ayah_key: Optional[str] = None,
        word_position: Optional[int] = None,
        word_text: Optional[str] = None,
        word: Optional[str] = None,
        root: Optional[str] = None,
        lemma: Optional[str] = None,
        stem: Optional[str] = None,
        match_by: str = "all",
        group_by: str = "verse",
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        payload = await self.call_mcp_method(
            "fetch_word_concordance",
            ayah_key=ayah_key,
            word_position=word_position,
            word_text=word_text,
            word=word,
            root=root,
            lemma=lemma,
            stem=stem,
            match_by=match_by,
            group_by=group_by,
            page=page,
            page_size=page_size,
        )
        json_obj, err = _extract_tool_json(payload)
        if err or not json_obj:
            return {"error": err or "fetch_word_concordance failed", "raw": payload}
        return {"result": json_obj}

    async def fetch_word_paradigm(
        self,
        ayah_key: Optional[str] = None,
        word_position: Optional[int] = None,
        word_text: Optional[str] = None,
        lemma: Optional[str] = None,
        root: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = await self.call_mcp_method(
            "fetch_word_paradigm",
            ayah_key=ayah_key,
            word_position=word_position,
            word_text=word_text,
            lemma=lemma,
            root=root,
        )
        json_obj, err = _extract_tool_json(payload)
        if err or not json_obj:
            return {"error": err or "fetch_word_paradigm failed", "raw": payload}
        return {"result": json_obj}

    async def show_mushaf(
        self,
        page: Optional[int] = None,
        surah: Optional[int] = None,
        ayah: Optional[int] = None,
        juz: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload = await self.call_mcp_method(
            "show_mushaf",
            page=page,
            surah=surah,
            ayah=ayah,
            juz=juz,
        )
        json_obj, err = _extract_tool_json(payload)
        if err or not json_obj:
            text = None
            if isinstance(payload, dict):
                content = payload.get("content")
                if isinstance(content, list) and content and isinstance(content[0], dict):
                    text = content[0].get("text")
            return {"error": err or "show_mushaf failed", "raw": payload, "text": text}
        return {"result": json_obj, "raw": payload}

    async def fetch_mushaf_page(self, page: int) -> Dict[str, Any]:
        payload = await self.call_mcp_method("fetch_mushaf", page=page)
        json_obj, err = _extract_tool_json(payload)
        if err or not json_obj:
            return {"error": err or "fetch_mushaf failed", "raw": payload}
        return {"result": json_obj}

    async def comprehensive_quran_search(
        self,
        query: str,
        include_tafsir: bool = True,
        include_translations: List[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive search combining Quran text, translations, and tafsir.
        
        Args:
            query: Search query
            include_tafsir: Include tafsir results
            include_translations: List of translation languages
            
        Returns:
            Comprehensive results
        """
        if include_translations is None:
            include_translations = ["en"]

        results = {
            "query": query,
            "quran_text": {},
            "translations": {},
            "tafsir": {},
            "timestamp": datetime.now().isoformat()
        }

        translations_param: Any = None
        if include_translations:
            if len(include_translations) == 1:
                translations_param = include_translations[0]
            else:
                translations_param = include_translations
        else:
            translations_param = "auto"

        search_payload = await self.call_mcp_method(
            "search_quran",
            query=query,
            translations=translations_param,
        )
        quran_search, err = _extract_tool_json(search_payload)
        if err or not quran_search:
            results["quran_text"] = {"error": err or "search_quran failed", "raw": search_payload}
            return results

        verses = _normalize_mcp_verses(quran_search)
        normalized_verses: List[Dict[str, Any]] = []
        for v in verses[:8]:
            surah = v.get("surah")
            ayah = v.get("ayah")
            text = (v.get("text") or "").strip()
            translation_text = ""
            translations = v.get("translations")
            if isinstance(translations, list) and translations:
                t0 = translations[0] if isinstance(translations[0], dict) else {}
                translation_text = _strip_html((t0 or {}).get("text") or "")
            normalized_verses.append(
                {
                    "surah": surah,
                    "ayah": ayah,
                    "ayah_key": v.get("ayah_key") or (f"{surah}:{ayah}" if surah and ayah else None),
                    "text": text,
                    "translation": translation_text,
                    "url": v.get("url"),
                }
            )

        results["quran_text"] = {"query": query, "results": normalized_verses, "raw": quran_search}

        if include_tafsir and normalized_verses:
            import os
            tafsir_pref = (os.getenv("QURAN_DEFAULT_TAFSIR_EDITIONS") or "").strip()
            tafsir_editions: List[str] = []
            if tafsir_pref:
                tafsir_editions = [t.strip() for t in tafsir_pref.split(",") if t.strip()]
            if not tafsir_editions:
                tafsir_editions = ["ar-ibn-kathir", "ar-saadi"]

            for v in normalized_verses[:2]:
                ak = v.get("ayah_key")
                if not isinstance(ak, str) or ":" not in ak:
                    continue
                try:
                    s_i = int(str(v.get("surah") or "").strip())
                    a_i = int(str(v.get("ayah") or "").strip())
                except Exception:
                    continue

                payload = await self.call_mcp_method(
                    "fetch_tafsir",
                    ayahs=ak,
                    editions=tafsir_editions,
                )
                obj, e2 = _extract_tool_json(payload)
                if e2 or not obj:
                    continue
                by_edition = obj.get("results")
                if not isinstance(by_edition, dict):
                    continue
                cleaned = {}
                for ed_id, ed_block in by_edition.items():
                    text_val = ""
                    if isinstance(ed_block, dict):
                        text_val = ed_block.get("text") or ""
                    elif isinstance(ed_block, list) and ed_block:
                        first = ed_block[0] if isinstance(ed_block[0], dict) else None
                        text_val = (first or {}).get("text") or ""
                    t = _strip_html(text_val)
                    if t:
                        cleaned[str(ed_id)] = t[:2200]
                if cleaned:
                    results["tafsir"][ak] = cleaned

        return results

    async def get_thematic_exploration(
        self,
        theme: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Explore a theme throughout the Quran.
        
        Args:
            theme: Thematic keyword or concept
            limit: Maximum number of results
            
        Returns:
            Verses and content related to the theme
        """
        results = {
            "theme": theme,
            "verses": [],
            "concepts": [],
            "timestamp": datetime.now().isoformat()
        }

        # Search for theme
        search_results = await self.search_quran(theme)
        if "results" in search_results:
            results["verses"] = search_results["results"][:limit]

        # Fetch tafsir for thematic understanding
        if results["verses"]:
            for verse in results["verses"][:3]:
                surah = verse.get("surah")
                ayah = verse.get("ayah")

                tafsir = await self.fetch_tafsir(surah, ayah, "ibn_kathir")
                tafsir_text = ""
                if isinstance(tafsir, dict):
                    tafsir_text = (tafsir.get("tafsir") or {}).get("ar-ibn-kathir") if isinstance(tafsir.get("tafsir"), dict) else ""
                if tafsir_text:
                    results["concepts"].append({
                        "surah": surah,
                        "ayah": ayah,
                        "insight": tafsir_text[:200]
                    })

        return results


# Singleton instance
_quran_mcp_instance = None


def get_quran_mcp() -> QuranFoundationMCP:
    """Get or create the Quran Foundation MCP instance."""
    global _quran_mcp_instance
    if _quran_mcp_instance is None:
        _quran_mcp_instance = QuranFoundationMCP()
    return _quran_mcp_instance


async def search_quran_knowledge(
    query: str,
    include_tafsir: bool = True,
    include_translations: List[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for searching Quranic knowledge.
    """
    mcp = get_quran_mcp()
    await mcp.initialize()
    try:
        return await mcp.comprehensive_quran_search(
            query,
            include_tafsir=include_tafsir,
            include_translations=include_translations or ["en"]
        )
    finally:
        await mcp.close()


async def explore_quran_theme(theme: str) -> Dict[str, Any]:
    """
    Convenience function for thematic exploration.
    """
    mcp = get_quran_mcp()
    await mcp.initialize()
    try:
        return await mcp.get_thematic_exploration(theme)
    finally:
        await mcp.close()


def _normalize_mcp_verses(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict):
        for key in ("results", "verses", "data"):
            val = payload.get(key)
            if isinstance(val, list):
                return [v for v in val if isinstance(v, dict)]
    if isinstance(payload, list):
        return [v for v in payload if isinstance(v, dict)]
    return []


async def fetch_surah_with_translation(
    surah: int,
    language: str = "en",
    translator: str = "sahih",
    max_ayah: Optional[int] = None,
) -> Dict[str, Any]:
    mcp = get_quran_mcp()
    await mcp.initialize()
    try:
        quran_payload = await mcp.fetch_quran(surah=surah, ayah=None)
        trans_payload = await mcp.fetch_translation(
            surah=surah, ayah=None, language=language, translator=translator
        )

        quran_verses = (
            quran_payload.get("results")
            if isinstance(quran_payload, dict)
            else None
        ) or []
        trans_verses = (
            trans_payload.get("results")
            if isinstance(trans_payload, dict)
            else None
        ) or []

        trans_by_ayah: Dict[int, str] = {}
        for v in trans_verses:
            a = v.get("ayah") or v.get("verse") or v.get("ayah_number")
            try:
                a_i = int(a)
            except Exception:
                continue
            t = (v.get("translation") or v.get("text") or v.get("content") or "").strip()
            if t:
                trans_by_ayah[a_i] = t

        merged: List[Dict[str, Any]] = []
        for v in quran_verses:
            a = v.get("ayah") or v.get("verse") or v.get("ayah_number")
            try:
                a_i = int(a)
            except Exception:
                a_i = None
            if max_ayah is not None and isinstance(a_i, int) and a_i > max_ayah:
                continue
            text = (v.get("text") or v.get("arabic") or v.get("content") or "").strip()
            translation = trans_by_ayah.get(a_i) if isinstance(a_i, int) else None
            merged.append(
                {
                    "surah": surah,
                    "ayah": a_i,
                    "text": text,
                    "translation": translation or "",
                }
            )

        return {
            "surah": surah,
            "verses": merged,
            "timestamp": datetime.now().isoformat(),
        }
    finally:
        await mcp.close()


if __name__ == "__main__":
    """Test the Quran Foundation MCP provider."""
    async def test():
        mcp = get_quran_mcp()
        await mcp.initialize()

        try:
            print("🔍 Testing Quran Foundation MCP Provider\n")

            # Test search
            print("1️⃣  Searching for 'compassion'...")
            results = await mcp.search_quran("compassion")
            print(f"   Found: {len(results.get('results', []))} verses\n")

            # Test fetch Quran
            print("2️⃣  Fetching Surah Al-Fatiha (1:1-7)...")
            _ = await mcp.fetch_quran(1, edition="en.sahih")
            print("   ✓ Retrieved\n")

            # Test fetch translation
            print("3️⃣  Fetching translation of Surah Al-Fatiha...")
            _ = await mcp.fetch_translation(1)
            print("   ✓ Retrieved\n")

            # Test fetch tafsir
            print("4️⃣  Fetching tafsir for Surah Al-Fatiha...")
            _ = await mcp.fetch_tafsir(1)
            print("   ✓ Retrieved\n")

            # Test thematic exploration
            print("5️⃣  Exploring theme: 'mercy'...")
            theme_results = await mcp.get_thematic_exploration(
                "mercy", limit=5
            )
            print(f"   Found {len(theme_results.get('verses', []))} verses\n")

            print("✅ All tests passed!")

        finally:
            await mcp.close()

    asyncio.run(test())

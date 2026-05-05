"""
Quran-Specific Tools for Islamic AI Agents
Enhanced tools that leverage the Quran Foundation MCP for authentic Islamic guidance.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
try:
    from agentscope.tool import ToolResponse
except Exception:
    from dataclasses import dataclass

    @dataclass
    class ToolResponse:
        status: str
        content: Any
        metadata: Optional[Dict[str, Any]] = None
from backend.utils.quran_mcp_provider import (
    get_quran_mcp,
    search_quran_knowledge,
    explore_quran_theme
)

logger = logging.getLogger("QuranTools")


def search_quran_text(query: str) -> ToolResponse:
    """
    Search the Quran for verses related to a query.
    
    Args:
        query: Search term or concept
        
    Returns:
        ToolResponse with search results and verse references
    """
    try:
        async def _search():
            return await search_quran_knowledge(query, include_tafsir=True)

        results = asyncio.run(_search())

        if "error" in results:
            return ToolResponse(
                status="error",
                content=f"❌ Search failed: {results['error']}"
            )

        verses = results.get("quran_text", {}).get("results", [])
        if not verses:
            return ToolResponse(
                status="failed",
                content=f"⚠️  No verses found for '{query}'"
            )

        formatted = f"📖 **Search Results for '{query}'**\n\n"
        for i, verse in enumerate(verses[:5], 1):
            formatted += f"{i}. Surah {verse.get('surah')}:{verse.get('ayah')}\n"
            formatted += f"   Text: {verse.get('text', '')[:150]}...\n\n"

        return ToolResponse(
            status="success",
            content=formatted
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        return ToolResponse(
            status="error",
            content=f"❌ Error searching Quran: {str(e)}"
        )


def fetch_surah(surah_number: int, ayah_start: Optional[int] = None, ayah_end: Optional[int] = None) -> ToolResponse:
    """
    Fetch specific Surah(s) and their translations.
    
    Args:
        surah_number: Surah number (1-114)
        ayah_start: Starting ayah (verse) number
        ayah_end: Ending ayah number
        
    Returns:
        ToolResponse with Surah text and translation
    """
    try:
        async def _fetch():
            mcp = get_quran_mcp()
            await mcp.initialize()
            try:
                quran_data = await mcp.fetch_quran(surah_number)
                trans_data = await mcp.fetch_translation(surah_number)
                return {"quran": quran_data, "translation": trans_data}
            finally:
                await mcp.close()

        data = asyncio.run(_fetch())

        if "error" in data.get("quran", {}):
            return ToolResponse(
                status="error",
                content=f"❌ Could not fetch Surah {surah_number}"
            )

        surah_name = f"Surah {surah_number}"
        formatted = f"📕 **{surah_name}**\n\n"

        quran = data.get("quran", {})
        trans = data.get("translation", {})

        if "verses" in quran:
            for verse in quran["verses"][:10]:  # Limit display
                ayah = verse.get("ayah")
                formatted += f"**Ayah {ayah}:**\n"
                formatted += f"Arabic: {verse.get('text', '')}\n"
                formatted += f"English: {verse.get('translation', '')}\n\n"

        return ToolResponse(
            status="success",
            content=formatted
        )

    except Exception as e:
        logger.error(f"Fetch surah error: {e}")
        return ToolResponse(
            status="error",
            content=f"❌ Error fetching Surah: {str(e)}"
        )


def fetch_tafsir(surah_number: int, ayah: Optional[int] = None, tafsir_type: str = "ibn_kathir") -> ToolResponse:
    """
    Fetch Islamic exegesis (Tafsir) for Quranic verses.
    
    Args:
        surah_number: Surah number
        ayah: Specific ayah (verse) number
        tafsir_type: Type of tafsir (ibn_kathir, al_tabari, etc.)
        
    Returns:
        ToolResponse with tafsir content
    """
    try:
        async def _fetch():
            mcp = get_quran_mcp()
            await mcp.initialize()
            try:
                return await mcp.fetch_tafsir(surah_number, ayah, tafsir_type)
            finally:
                await mcp.close()

        result = asyncio.run(_fetch())

        if "error" in result:
            return ToolResponse(
                status="error",
                content=f"❌ Could not fetch Tafsir: {result['error']}"
            )

        verse_ref = f"{surah_number}:{ayah}" if ayah else f"Surah {surah_number}"
        formatted = f"🔍 **Tafsir - {verse_ref}**\n\n"
        formatted += f"📚 Type: {tafsir_type.replace('_', ' ').title()}\n\n"

        if "content" in result:
            content = result["content"]
            # Limit length for readability
            if len(content) > 1000:
                content = content[:1000] + "...\n\n[See full tafsir in Islamic sources]"
            formatted += content

        return ToolResponse(
            status="success",
            content=formatted
        )

    except Exception as e:
        logger.error(f"Fetch tafsir error: {e}")
        return ToolResponse(
            status="error",
            content=f"❌ Error fetching Tafsir: {str(e)}"
        )


def explore_theme(theme: str) -> ToolResponse:
    """
    Explore a theme throughout the Quran with related verses and tafsir.
    
    Args:
        theme: Thematic concept (e.g., 'patience', 'mercy', 'faith')
        
    Returns:
        ToolResponse with thematic exploration
    """
    try:
        async def _explore():
            return await explore_quran_theme(theme)

        results = asyncio.run(_explore())

        verses = results.get("verses", [])
        if not verses:
            return ToolResponse(
                status="failed",
                content=f"⚠️  No verses found for theme '{theme}'"
            )

        formatted = f"🌟 **Thematic Exploration: {theme.title()}**\n\n"
        formatted += f"Total Verses Found: {len(verses)}\n\n"

        for i, verse in enumerate(verses[:5], 1):
            formatted += f"{i}. Surah {verse.get('surah')}:{verse.get('ayah')}\n"
            formatted += f"   {verse.get('text', '')[:100]}...\n\n"

        concepts = results.get("concepts", [])
        if concepts:
            formatted += "**Insights:**\n"
            for concept in concepts[:3]:
                formatted += f"- {concept.get('insight', '')}\n"

        return ToolResponse(
            status="success",
            content=formatted
        )

    except Exception as e:
        logger.error(f"Explore theme error: {e}")
        return ToolResponse(
            status="error",
            content=f"❌ Error exploring theme: {str(e)}"
        )


def get_quranic_guidance(question: str) -> ToolResponse:
    """
    Get comprehensive Quranic guidance on a specific question/topic.
    Combines search, tafsir, and thematic exploration.
    
    Args:
        question: User's question about Islamic guidance
        
    Returns:
        ToolResponse with comprehensive guidance
    """
    try:
        # Extract key terms from question
        key_terms = question.split()[:3]  # Take first 3 words as key terms

        async def _get_guidance():
            mcp = get_quran_mcp()
            await mcp.initialize()
            try:
                guidance = {
                    "question": question,
                    "search_results": [],
                    "theme_results": []
                }

                # Search for each key term
                for term in key_terms:
                    search = await mcp.search_quran(term)
                    if "results" in search:
                        guidance["search_results"].extend(search["results"][:3])

                # Explore main theme
                if key_terms:
                    theme = await mcp.get_thematic_exploration(key_terms[0], limit=5)
                    guidance["theme_results"] = theme.get("verses", [])

                return guidance
            finally:
                await mcp.close()

        guidance = asyncio.run(_get_guidance())

        formatted = f"✨ **Quranic Guidance on: {question}**\n\n"

        search_results = guidance.get("search_results", [])
        if search_results:
            formatted += "**Relevant Verses:**\n"
            for verse in search_results[:3]:
                formatted += f"- Surah {verse.get('surah')}:{verse.get('ayah')}: {verse.get('text', '')[:80]}...\n"
            formatted += "\n"

        theme_results = guidance.get("theme_results", [])
        if theme_results:
            formatted += f"**Thematic References ({len(theme_results)} verses):**\n"
            for verse in theme_results[:3]:
                formatted += f"- Surah {verse.get('surah')}:{verse.get('ayah')}\n"

        formatted += "\n💡 Consult complete Tafsir for deeper understanding."

        return ToolResponse(
            status="success",
            content=formatted
        )

    except Exception as e:
        logger.error(f"Get guidance error: {e}")
        return ToolResponse(
            status="error",
            content=f"❌ Error getting guidance: {str(e)}"
        )


def register_quran_tools(toolkit):
    """
    Register all Quran-specific tools with an AgentScope Toolkit.
    
    Args:
        toolkit: AgentScope Toolkit instance
    """
    try:
        # Search tool
        toolkit.register_tool_function(
            search_quran_text,
            name="search_quran",
            description="Search the Quran for verses related to a query. Returns matching verses with references."
        )

        # Fetch surah tool
        toolkit.register_tool_function(
            fetch_surah,
            name="fetch_surah",
            description="Fetch a complete Surah with Arabic text and English translation."
        )

        # Tafsir tool
        toolkit.register_tool_function(
            fetch_tafsir,
            name="fetch_tafsir",
            description="Fetch Islamic exegesis (Tafsir) for specific Quranic verses."
        )

        # Thematic exploration tool
        toolkit.register_tool_function(
            explore_theme,
            name="explore_theme",
            description="Explore a theme throughout the Quran with related verses and insights."
        )

        # Comprehensive guidance tool
        toolkit.register_tool_function(
            get_quranic_guidance,
            name="get_quranic_guidance",
            description="Get comprehensive Quranic guidance on any Islamic question or topic."
        )

        logger.info("✅ All Quran-specific tools registered successfully")

    except Exception as e:
        logger.error(f"Error registering Quran tools: {e}")
        raise


# Convenience functions for direct use

def quick_quran_search(query: str) -> Dict[str, Any]:
    """Quick search without verbose output."""
    try:
        async def _search():
            return await search_quran_knowledge(query)
        return asyncio.run(_search())
    except Exception as e:
        return {"error": str(e)}


def quick_theme_explore(theme: str) -> Dict[str, Any]:
    """Quick thematic exploration."""
    try:
        async def _explore():
            return await explore_quran_theme(theme)
        return asyncio.run(_explore())
    except Exception as e:
        return {"error": str(e)}


async def search_quran_mcp(query: str) -> Dict[str, Any]:
    """
    Search Quran Foundation MCP for query.
    Used by intelligent tool router for Quran queries.
    
    Args:
        query: Search query
        
    Returns:
        Dictionary with status and search results
    """
    try:
        logger.info(f"🔍 Searching Quran Foundation MCP for: {query}")
        
        # Try to get Quran MCP and search
        mcp = get_quran_mcp()
        await mcp.initialize()
        
        try:
            # Search Quran knowledge base
            results = await search_quran_knowledge(query, include_tafsir=True)
            
            if results and "quran_text" in results and results["quran_text"].get("results"):
                verses = results["quran_text"]["results"]
                
                formatted_blocks: List[str] = []
                for i, verse in enumerate(verses[:5], 1):
                    surah = verse.get("surah")
                    ayah = verse.get("ayah")
                    reference = f"Quran {surah}:{ayah} [Quran Foundation MCP]"
                    text = (verse.get("text") or "").strip()
                    translation = (verse.get("translation") or "").strip()
                    content_parts = []
                    if text:
                        content_parts.append(text)
                    if translation:
                        content_parts.append(f"Translation: {translation}")

                    content = "\n".join(content_parts).strip()
                    if content:
                        formatted_blocks.append(f"[Source {i}] {reference}")
                        formatted_blocks.append(content)
                        formatted_blocks.append("")

                formatted = "\n".join(formatted_blocks).strip()
                
                return {
                    "status": "success",
                    "data": formatted,
                    "source": "quran_foundation_mcp",
                    "verse_count": len(verses)
                }
            else:
                # No results from MCP, return graceful failure
                return {
                    "status": "failed",
                    "data": f"No Quranic verses found for '{query}'",
                    "source": "quran_foundation_mcp"
                }
        finally:
            await mcp.close()
            
    except Exception as e:
        logger.warning(f"Quran MCP search failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "source": "quran_foundation_mcp"
        }


if __name__ == "__main__":
    """Test Quran-specific tools."""
    print("🧪 Testing Quran Tools\n")

    print("1. Search Test:")
    result = search_quran_text("patience")
    print(result)

    print("\n2. Theme Exploration Test:")
    result = explore_theme("mercy")
    print(result)

    print("\n3. Guidance Test:")
    result = get_quranic_guidance("What does Islam say about honesty?")
    print(result)

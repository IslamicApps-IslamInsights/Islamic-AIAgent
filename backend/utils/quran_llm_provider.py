"""
Quran-Centric Provider
Uses Quran Foundation MCP as the only response source.
No external LLMs (Gemini/OpenAI/AgentScope).
"""

import logging
from typing import Dict, Any
from dotenv import load_dotenv
import asyncio

from backend.utils.quran_mcp_provider import (
    search_quran_knowledge,
    explore_quran_theme
)

load_dotenv()
logger = logging.getLogger("QuranLLMProvider")


def is_gemini_available() -> bool:
    """Check if Gemini synthesis is available."""
    return False


def get_gemini_client():
    """Get Gemini client if available."""
    return None


def init_agentscope():
    """Initialize AgentScope context."""
    return None


def get_agentscope_model():
    """
    Get AgentScope model - defaults to Quran Foundation powered model.
    Falls back to Gemini if needed for synthesis.
    """
    return None


async def query_quran_foundation(
    question: str,
    search_type: str = "comprehensive",
    include_tafsir: bool = True
) -> Dict[str, Any]:
    """
    Query Quran Foundation MCP for Islamic knowledge.
    
    Args:
        question: User's question
        search_type: 'comprehensive', 'quick', or 'thematic'
        include_tafsir: Include scholarly interpretation
        
    Returns:
        Response from Quran Foundation
    """
    logger.info(f"🔍 Querying Quran Foundation: {question}")

    if search_type == "thematic":
        return await explore_quran_theme(question)
    else:
        return await search_quran_knowledge(
            question,
            include_tafsir=include_tafsir,
            include_translations=["en", "ar", "ur"]
        )


def synthesize_quran_response(
    question: str,
    quran_context: Dict[str, Any],
    use_gemini: bool = True
) -> str:
    """
    Synthesize a response combining Quran Foundation data with optional Gemini synthesis.
    
    Args:
        question: Original question
        quran_context: Context from Quran Foundation
        use_gemini: Whether to use Gemini for synthesis
        
    Returns:
        Synthesized response
    """
    logger.info("📝 Synthesizing response...")

    # Format Quran context
    formatted_context = _format_quran_context(quran_context)

    if not use_gemini or not is_gemini_available():
        # Return formatted Quran context directly
        return _create_quranic_response(question, formatted_context)

    # Try to synthesize with Gemini
    try:
        client = get_gemini_client()
        if client:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""Based on Islamic sources, answer this question: {question}

Islamic Context:
{formatted_context}

Please provide a thoughtful Islamic response based on the above Islamic sources. 
Start with 'Assalamu Alaikum wa Rahmatullahi wa Barakatuh.'
End with 'May Allah guide us. 🤲'
Include verse references when mentioning Quranic content."""
            )
            return response.text
    except Exception as e:
        logger.warning(f"Gemini synthesis failed: {e}, using direct Quran response")

    # Fallback to direct Quran response
    return _create_quranic_response(question, formatted_context)


def _format_quran_context(context: Dict[str, Any]) -> str:
    """Format Quran Foundation context for display."""
    formatted = ""

    # Add search results
    if "quran_text" in context and "results" in context["quran_text"]:
        formatted += "📖 **Relevant Verses:**\n"
        for verse in context["quran_text"]["results"][:5]:
            formatted += f"\nSurah {verse.get('surah')}:{verse.get('ayah')}\n"
            formatted += f"Text: {verse.get('text', '')}\n"

    # Add tafsir insights
    if "tafsir" in context:
        formatted += "\n\n📚 **Scholarly Interpretation:**\n"
        for ref, tafsir_data in list(context["tafsir"].items())[:3]:
            if "content" in tafsir_data:
                formatted += f"\n{ref}: {tafsir_data['content'][:300]}...\n"

    # Add translations
    if "translations" in context:
        formatted += "\n\n🌐 **Translations:**\n"
        for lang, translations in context["translations"].items():
            if translations:
                formatted += f"{lang}: {translations[0].get('text', '')[:150]}...\n"

    return formatted


def _create_quranic_response(question: str, context: str) -> str:
    """Create a response directly from Quranic context."""
    response = "Assalamu Alaikum wa Rahmatullahi wa Barakatuh.\n\n"
    response += f"🕌 **Islamic Response to: {question}**\n\n"
    response += context
    response += "\n\nMay Allah guide us. 🤲"
    return response


def format_for_agent(
    response_text: str,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Format response for agent output.
    
    Args:
        response_text: The response text
        include_metadata: Include timestamp and source
        
    Returns:
        Formatted response dict
    """
    from datetime import datetime

    formatted = {
        "response": response_text,
        "source": "Quran Foundation MCP",
        "model": "Quranic Knowledge Base",
        "timestamp": datetime.now().isoformat()
    }

    if include_metadata:
        formatted["metadata"] = {
            "gemini_synthesis": is_gemini_available(),
            "primary_source": "Quran Foundation",
            "secondary_source": "Gemini (optional synthesis)" if is_gemini_available() else None
        }

    return formatted


# Async wrapper for agents
async def get_quranic_answer(
    question: str,
    use_tafsir: bool = True,
    use_synthesis: bool = True
) -> Dict[str, Any]:
    """
    Main function to get Islamic answer based on Quran Foundation.
    
    Args:
        question: User's question
        use_tafsir: Include Tafsir (Islamic exegesis)
        use_synthesis: Use Gemini synthesis if available
        
    Returns:
        Formatted response
    """
    try:
        # Query Quran Foundation
        context = await query_quran_foundation(
            question,
            search_type="comprehensive",
            include_tafsir=use_tafsir
        )

        # Synthesize response
        response_text = synthesize_quran_response(
            question,
            context,
            use_gemini=use_synthesis
        )

        return format_for_agent(response_text)

    except Exception as e:
        logger.error(f"Error getting Quranic answer: {e}")
        error_response = f"Assalamu Alaikum wa Rahmatullahi wa Barakatuh.\n\n❌ I encountered an issue retrieving Quranic knowledge: {str(e)}\n\nPlease try again or rephrase your question. May Allah guide us. 🤲"
        return format_for_agent(error_response)


# Synchronous wrapper for compatibility
def get_quranic_answer_sync(
    question: str,
    use_tafsir: bool = True,
    use_synthesis: bool = True
) -> Dict[str, Any]:
    """Synchronous wrapper for get_quranic_answer."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(
        get_quranic_answer(question, use_tafsir, use_synthesis)
    )


if __name__ == "__main__":
    """Test the Quran-centric LLM provider."""
    print("🧪 Testing Quran-Centric LLM Provider\n")

    # Test synchronous function
    result = get_quranic_answer_sync("What does Islam teach about patience?")
    print("Response:")
    print(result["response"])

"""
Unified LLM Provider for Islamic AI Agent
Uses Google Gemini as the primary LLM – no OpenAI dependency.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Singleton Gemini client
# ---------------------------------------------------------------------------
_gemini_client = None
_agentscope_initialized = False


def get_gemini_client():
    """Return a cached google.genai Client instance."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    from google import genai

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is required. Set it in your .env file."
        )

    _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


# Convenience: keep a model-name constant
GEMINI_MODEL = "models/gemini-3.1-flash-live-preview"


# ---------------------------------------------------------------------------
# AgentScope model configuration (for ReActAgent / multi-agent system)
# ---------------------------------------------------------------------------

def init_agentscope():
    """Initialize AgentScope 1.0.18 context."""
    import agentscope
    global _agentscope_initialized
    if not _agentscope_initialized:
        agentscope.init(
            project="IslamicAI", 
            name="NoorSession"
        )
        _agentscope_initialized = True
        print(f"✅ AgentScope global context initialized.")

def get_agentscope_model():
    """
    Initialize AgentScope and register the Gemini model configuration.
    Returns the config name.
    """
    import agentscope
    api_key = os.getenv("GOOGLE_API_KEY", "")
    config = {
        "config_name": "gemini_config",
        "model_type": "gemini_chat",
        "model_name": GEMINI_MODEL,
        "api_key": api_key
    }
    
    # In AgentScope 0.1.6, we use agentscope.init with model_configs
    agentscope.init(
        project="IslamicAI",
        name="NoorSession",
        model_configs=[config]
    )
    return "gemini_config"


# ---------------------------------------------------------------------------
# Toolkit helper: wrap plain-string tool functions for AgentScope v1.0.18
# ---------------------------------------------------------------------------

def register_islamic_tool(toolkit, func):
    """
    Register a tool function with the AgentScope Toolkit.
    """
    import functools
    
    @functools.wraps(func)
    def _wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        return str(result) if result is not None else "No result"

    # Use register_tool_function for AgentScope 1.0.18
    if hasattr(toolkit, 'register_tool_function'):
        toolkit.register_tool_function(_wrapped)
    else:
        # Fallback to legacy add method if still available
        toolkit.add(_wrapped)


# ---------------------------------------------------------------------------
# Scholarly synthesis (replaces OpenAI-based _synthesize_scholarly_response)
# ---------------------------------------------------------------------------

def synthesize_scholarly_response(
    question: str,
    context: str,
    *,
    client=None,
) -> str:
    """
    Generate a scholarly Islamic response using Gemini.

    Args:
        question: The user's query.
        context:  Retrieved RAG context (Quran / Hadith excerpts).
        client:   Optional pre-loaded client; uses singleton if *None*.

    Returns:
        A formatted, compassionate Islamic scholarly response.
    """
    synth_prompt = f"""\
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

You are a Senior Islamic Scholar (Imam Hassan) providing a comprehensive and authoritative response.

**User Query:** {question}

**Retrieved Authentic Context (Quran & Sunnah):**
{context}

**Your Mandate:**
1. **Direct Answer**: Provide a clear, scholarly response based primarily on the provided context.
2. **Quranic Evidence**: If the context contains Quranic verses, provide the Arabic text followed by the translation and Surah:Ayah reference.
3. **Prophetic Sunnah**: If the context contains Hadiths, cite the collection (e.g., Sahih Bukhari), the Hadith number, and its grading (Sahih/Hasan).
4. **Scholarly Synthesis**: Connect the evidences logically to form a cohesive guidance.
5. **Handling Gaps**: If the context is specific but doesn't fully answer the query, state "Based on the primary sources retrieved..." and supplement with general authentic Islamic knowledge while maintaining a cautious, scholarly tone.
6. **Tone**: Be compassionate, patient, and highly respectful. Use "We" or "Scholars advise" where appropriate.
7. **Formatting**: Use Markdown for clear structure (Bold headers, bullet points).

**Structure:**
- Greeting: "Assalamu Alaikum wa Rahmatullahi wa Barakatuh"
- Main Guidance with evidences.
- Practical Advice (Action steps).
- Closing: "May Allah guide us all to the Straight Path. Ameen!"

**Response:**
"""
    try:
        if client is None:
            client = get_gemini_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=synth_prompt,
        )
        if response and response.text:
            return response.text
        return (
            "Assalamu Alaikum. I retrieved scholarly information but "
            "could not generate a synthesis. Here is the raw context "
            f"for your benefit:\n\n{context}"
        )
    except Exception as e:
        print(f"Scholarly Synthesis error (Gemini): {e}")
        return (
            "Assalamu Alaikum. I retrieved scholarly information but "
            "encountered a synthesis error. Here is the raw context "
            f"for your benefit:\n\n{context}"
        )

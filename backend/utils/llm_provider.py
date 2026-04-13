"""
Unified LLM Provider for Islamic AI Agent
Uses Google Gemini as the primary LLM – no OpenAI dependency.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    retry_if_result,
)

load_dotenv()

# Logger setup
logger = logging.getLogger("NoorLLM")

def is_429_error(exception):
    """Check if the exception is a 429 quota error."""
    return "429" in str(exception) or "RESOURCE_EXHAUSTED" in str(exception)

# Unified retry decorator for Gemini calls
gemini_retry = retry(
    retry=retry_if_exception(is_429_error),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    before_sleep=lambda retry_state: print(f"⚠️  Quota hit (429). Retrying in {retry_state.next_action.sleep}s... (Attempt {retry_state.attempt_number})"),
    reraise=True
)

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
# Primary model for production (Using stable and fast 2.5-flash to prevent 503 errors)
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_PRO_MODEL = "gemini-2.5-pro" # For complex synthesis


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

@gemini_retry
def synthesize_scholarly_response(
    question: str,
    context: str,
    *,
    metadata: Optional[Dict] = None,
    client=None,
    include_thoughts: bool = False,
    rag_display: str = None   # Pre-formatted RAG response — primary fallback
) -> Any:
    """
    RAG-First synthesis. Gemini polishes the response when available.
    If Gemini fails, rag_display is returned — never an error string.

    Returns:
        If include_thoughts is True: Tuple[str, Optional[str]] (text, thoughts)
        Else: str (text only)
    """
    # Build metadata string for grounding
def call_local_llm(prompt: str) -> Optional[str]:
    """Helper to call local Ollama/LM Studio if available."""
    import requests
    local_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    try:
        response = requests.post(local_url, json={
            "model": "llama3", # Default but can be configured
            "prompt": prompt,
            "stream": False
        }, timeout=10)
        if response.status_code == 200:
            return response.json().get("response")
    except Exception:
        pass
    return None

def synthesize_scholarly_response(question: str, context: str, metadata: Dict = None, include_thoughts: bool = False, rag_display: str = None, force_local: bool = False) -> Any:
    """
    World-Class Scholarly Synthesis Engine 2.0.
    Ensures absolute resilience by absorbing API errors and falling back to 
    high-fidelity local knowledge base results.
    """
    if force_local:
        print("🛡️ FORCE_LOCAL Active: Bypassing AI Synthesis for Resilience Demo.")
        if rag_display:
            if include_thoughts: return rag_display, None
            return rag_display
        return "Local Resilient mode active. Synthesis bypassed."
    # ... previous setup ...
    metadata_str = ""
    if metadata:
        metadata_str = "\n**Real-Time Context:**\n"
        for k, v in metadata.items():
            metadata_str += f"- {k}: {v}\n"

    synth_prompt = f"""\
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

You are a world-class Senior Islamic Scholar and Mufti (Imam Hassan). You provide responses that are not only accurate but also deeply spiritual, respectful, and authoritative.

### INTERNAL SCHOLARLY AUDIT (THOUGHT PROCESS)
Before responding, perform this internal audit in your thoughts:
1. **Source Verification**: Does the provided context contain authentic Quranic verses or Sahih Hadiths that directly address {question}? If no, acknowledge this and provide general authentic guidance based on your deep knowledge.
2. **Context Window Check**: If the context appears expanded (Borders present), read the entire story to ensure no rulings are taken out of context.
3. **Tone Check**: Ensure the tone is compassionate (Mercy) but firm on truth (Haqq).

### SCHOLARLY MANDATE
1. **Dynamic Synthesis**: Do not just list sources. Weave them together into a beautiful narrative. Use phrases like "In the light of the Divine revelation..." or "The Prophet's ﷺ noble example teaches us...".
2. **Arabic Excellence**: Use proper Arabic terms for key concepts (e.g., *Taqwa*, *Ikhlas*, *Sabr*) followed by their English meanings. Always include ﷺ (Sallallahu Alayhi Wasallam) after the Prophet's name.
3. **Source Grounding**: Heavily prioritize the provided "Retrieved Context". If multiple sources are provided, compare and synthesize them. 
4. **Formatting (Aesthetic Excellence)**:
   - Use ****Bold Text**** for section titles and key principles.
   - Use '•' for list items. 
   - Ensure clear, spacious double-paragraphing for readability.
   - **DO NOT** use '###' or '>' in your final response.

**Real-Time Metadata:**
{metadata_str}

**User Inquiry:** {question}

**Retrieved Authentic Context (Ground Truth):**
{context}

**Response Structure:**
1. **Greeting**: Assalamu Alaikum wa Rahmatullahi wa Barakatuh.
2. **The Essence**: A bold heading summarizing the core Islamic principle.
3. **Detailed Scholarly Guidance**: Comprehensive explanation with cited evidence.
4. **Practical Application**: Bullet points on how to live this knowledge.
5. **Dua/Closing**: A beautiful closing Dua related to the topic.
6. **Sources**: Exactly "**Sources:** " followed by a clean list at the very bottom.

**Response:**
"""

    # --- Resilience Logic: Try Local LLM First if over Quota ---
    local_response = None
    if os.getenv("USE_LOCAL_LLM", "false").lower() == "true":
        local_response = call_local_llm(synth_prompt)
        if local_response:
            if include_thoughts: return local_response, None
            return local_response

    try:
        from google.api_core import exceptions
        gemini_client = get_gemini_client()
        
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=synth_prompt,
        )
        
        text = response.text if response and response.text else ""
        thoughts = None
        
        # Capture Gemini 3 thoughts if available
        try:
            if response and hasattr(response, 'candidates') and response.candidates:
                content = response.candidates[0].content
                for part in content.parts:
                    if hasattr(part, 'thought_signature') and part.thought_signature:
                        if hasattr(part, 'text') and part.text:
                            thoughts = part.text
                        elif hasattr(part, 'thought') and part.thought:
                            thoughts = part.thought
        except Exception:
            pass

        # SUCCESS: Return synthesis
        if text:
            if include_thoughts: return text, thoughts
            return text
            
        # FALLBACK: Return premium RAG display if text is empty
        raise ValueError("Empty response from AI")

    except Exception as e:
        # DETECT 429: If over quota, switch to Local Knowledge immediately
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "limit" in error_str:
            print("🛡️ Quota exceeded. Activating Resilience Fallback: Premium Local Knowledge Responder.")
        else:
            print(f"Scholarly Synthesis error (Gemini): {e}")
            
        # RAG-first: return the pre-formatted authentic response, never an error string
        if rag_display:
            if include_thoughts: return rag_display, None
            return rag_display
            
        return (
            "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
            "I apologize, but our scholarly synthesis system is currently over-taxed. "
            "Please try again in a few moments, or ask a question that can be answered directly "
            "from our local library of authentic texts."
        )

@gemini_retry
def generate_text(prompt: str, model: str = GEMINI_MODEL, include_thoughts: bool = False) -> Any:
    """Generic text generation utility."""
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        
        text = response.text if response and response.text else ""
        thoughts = None
        
        # Try to extract thoughts for Gemini 3
        try:
            if response and hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'thought_signature') and part.thought_signature:
                         thoughts = part.text if hasattr(part, 'text') else str(part)
        except:
            pass

        if include_thoughts:
            return text, thoughts
        return text
    except Exception as e:
        print(f"Generic Generation error: {e}")
        if include_thoughts:
            return "", None
        return ""

def verify_retrieval_integrity(question: str, contexts: List[str]) -> List[int]:
    """
    RAG v2 Authenticity Step: 
    Audit retrieved context chunks and return indices of truly relevant/authentic ones.
    """
    if not contexts:
        return []

    context_block = ""
    for i, c in enumerate(contexts):
        context_block += f"--- CHUNK {i} ---\n{c}\n\n"

    audit_prompt = f"""
    You are an Islamic Scholarly Auditor. Your job is to verify if retrieved context chunks 
    actually answer the user's question and are from authentic Islamic sources.
    
    User Question: {question}
    
    Retrieved Chunks:
    {context_block}
    
    INSTRUCTIONS:
    1. For each chunk, decide if it is highly relevant and provides authentic Islamic guidance for the question.
    2. Respond ONLY with a JSON list of indices (e.g., [0, 2]) for the chunks that should be kept.
    3. If none are relevant, respond with [].
    
    Response:
    """
    
    try:
        res_text = generate_text(audit_prompt, model=GEMINI_MODEL)
        import json
        import re
        # Take everything from start of first [ to end of last ]
        match = re.search(r'\[.*\]', res_text.strip(), re.DOTALL)
        if match:
            return json.loads(match.group())
        return list(range(len(contexts))) # Fallback to all if parsing fails
    except Exception as e:
        print(f"Retrieval Integrity Audit error: {e}")
        return list(range(len(contexts))) # Fallback to all

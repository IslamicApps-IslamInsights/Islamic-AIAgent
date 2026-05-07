"""
Unified LLM Provider for Islamic AI Agent
Uses Google Gemini as the primary LLM – no OpenAI dependency.
"""

import os
import logging
import threading
import re
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
)

load_dotenv()

# Logger setup
logger = logging.getLogger("NoorLLM")

_LOCAL_LLM_STOP_TOKENS = [
    "</final>",
    "<Thought>",
    "</Thought>",
    "<Output>",
    "</Output>",
    "<think>",
    "</think>",
]

_AUTO_LOCAL_LLM_BACKEND: Optional[str] = None
_AUTO_LOCAL_LLM_BACKEND_TS: float = 0.0


def _detect_local_llm_backend() -> Optional[str]:
    global _AUTO_LOCAL_LLM_BACKEND, _AUTO_LOCAL_LLM_BACKEND_TS
    now = time.time()
    if now - _AUTO_LOCAL_LLM_BACKEND_TS < 5.0:
        return _AUTO_LOCAL_LLM_BACKEND
    _AUTO_LOCAL_LLM_BACKEND_TS = now

    try:
        import requests

        base_url = (os.getenv("LLAMA_CPP_SERVER_URL") or "").strip() or "http://localhost:8080"
        models_url = base_url.rstrip("/") + "/v1/models"
        resp = requests.get(models_url, timeout=0.8)
        if resp.status_code == 200:
            _AUTO_LOCAL_LLM_BACKEND = "llama_cpp_server"
            return _AUTO_LOCAL_LLM_BACKEND
    except Exception:
        pass

    _AUTO_LOCAL_LLM_BACKEND = None
    return None


def _sanitize_user_facing_answer(text: str) -> Optional[str]:
    if not isinstance(text, str):
        return None

    cleaned = text.strip()
    if not cleaned:
        return None

    # Remove final tag if present
    cleaned = cleaned.split("</final>")[0].strip()

    # Handle various thought/think tag formats
    output_match = re.search(r"(?is)<output>(.*?)</output>", cleaned)
    if output_match:
        cleaned = (output_match.group(1) or "").strip()
    else:
        cleaned = re.sub(r"(?is)<thought>.*?</thought>", "", cleaned).strip()
        cleaned = re.sub(r"(?is)<think>.*?</think>", "", cleaned).strip()
        # Fallback split
        cleaned = re.split(r"(?i)<thought>|<think>|<output>", cleaned, maxsplit=1)[0].strip()

    # Preserve Islamic Greeting
    greeting_match = re.search(r"(?i)(Assalamu\s+Alaikum\s+wa\s+Rahmatullahi\s+wa\s+Barakatuh\.?|Assalamu\s+Alaikum\.?)", cleaned)
    greeting = ""
    if greeting_match:
        greeting = greeting_match.group(0)
        # Ensure it has a double newline after it
        greeting = greeting.rstrip() + ".\n\n"
    
    # Remove code blocks if LLM hallucinations them
    cleaned = re.sub(r"(?is)```.*?```", "", cleaned).strip()
    
    # Ensure section headers are not bolded in the raw text (frontend will handle styling)
    cleaned = re.sub(r"(?m)^\s*\*\*\s*(\d+[\)\.]\s*[^*]+?)\s*\*\*\s*$", r"\1", cleaned).strip()

    # Find where the actual content starts (either the greeting or the first section)
    # If we have a greeting, we keep everything from the greeting onwards
    # Otherwise, we start from the first "1)"
    start_pos = -1
    if greeting_match:
        start_pos = greeting_match.start()
    else:
        m = re.search(r"(?m)^\s*(?:\*\*)?\s*1[\)\.]\s+", cleaned)
        if m:
            start_pos = m.start()

    if start_pos != -1:
        cleaned = cleaned[start_pos:].strip()
    
    # Double check we have at least section 1
    if not re.search(r"(?m)^\s*(?:\*\*)?\s*1[\)\.]\s+", cleaned):
        return None

    return cleaned.strip() or None


def _inject_source_references(answer: str, evidence: str) -> str:
    if not isinstance(answer, str) or not answer.strip():
        return answer

    evidence_map: Dict[str, str] = {}
    for line in (evidence or "").splitlines():
        m = re.match(r"^\[Source\s+(\d+)\]\s+(.+)\s*$", line.strip())
        if m:
            evidence_map[m.group(1)] = m.group(2).strip()

    if not evidence_map:
        return answer

    lines = answer.splitlines()
    out: List[str] = []
    in_sources = False
    seen: set[str] = set()

    for line in lines:
        raw = line.rstrip()
        stripped = raw.strip()

        if re.match(r"(?i)^\s*4[\)\.]\s*sources\b", stripped):
            in_sources = True
            out.append(raw)
            continue

        if not in_sources:
            out.append(raw)
            continue

        m = re.search(r"\[Source\s+(\d+)\]", stripped)
        if not m:
            if stripped:
                out.append(raw)
            continue

        n = m.group(1)
        if n in seen:
            continue
        seen.add(n)

        ref = evidence_map.get(n)
        if ref:
            out.append(f"- [Source {n}] {ref}")
        else:
            out.append(f"- [Source {n}]")

    return "\n".join(out).strip()


def is_429_error(exception):
    """Check if the exception is a 429 quota error."""
    return "429" in str(exception) or "RESOURCE_EXHAUSTED" in str(exception)


def _before_sleep(retry_state):
    sleep_s = retry_state.next_action.sleep
    attempt = retry_state.attempt_number
    msg = f"⚠️  Quota hit (429). Retrying in {sleep_s}s... (Attempt {attempt})"
    print(msg)


# Unified retry decorator for Gemini calls
gemini_retry = retry(
    retry=retry_if_exception(is_429_error),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    before_sleep=_before_sleep,
    reraise=True
)

_gemini_client = None
_agentscope_initialized = False
_agentscope_lock = threading.Lock()
_agentscope_model = None


def get_gemini_client():
    """Return a cached google.genai Client instance."""
    raise RuntimeError(
        "External LLMs are disabled (local-only mode)."
    )


# Convenience: keep a model-name constant
# Primary model constants (kept for compatibility)
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_PRO_MODEL = "gemini-2.5-pro"


# ---------------------------------------------------------------------------
# AgentScope model configuration (for ReActAgent / multi-agent system)
# ---------------------------------------------------------------------------

def init_agentscope():
    """Initialize AgentScope 1.0.18 context."""
    return None


def get_agentscope_model():
    """
    Initialize AgentScope and return a GeminiChatModel instance.
    """
    return None


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
    if hasattr(toolkit, "register_tool_function"):
        toolkit.register_tool_function(_wrapped)
    else:
        toolkit.add(_wrapped)


# ---------------------------------------------------------------------------
# Scholarly synthesis (replaces OpenAI-based _synthesize_scholarly_response)
# ---------------------------------------------------------------------------

def call_local_llm(prompt: str) -> Optional[str]:
    backend = (os.getenv("LOCAL_LLM_BACKEND") or "").strip().lower()
    if not backend:
        backend = (_detect_local_llm_backend() or "").strip().lower()
    if not backend:
        return None

    if backend == "ollama":
        return _call_ollama(prompt)

    if backend == "llama_cpp_server":
        return _call_llama_cpp_server(prompt)

    if backend == "llama_cpp_python":
        return _call_llama_cpp_python(prompt)

    return None


def get_local_llm_status() -> Dict[str, Any]:
    backend = (os.getenv("LOCAL_LLM_BACKEND") or "").strip().lower()
    if not backend:
        backend = (_detect_local_llm_backend() or "").strip().lower()
    if not backend:
        return {"enabled": False, "backend": None, "reachable": False}

    if backend == "llama_cpp_server":
        import requests

        base_url = (os.getenv("LLAMA_CPP_SERVER_URL") or "").strip() or "http://localhost:8080"
        model_path = (os.getenv("LOCAL_LLM_MODEL_PATH") or "").strip()
        model_exists = bool(model_path) and os.path.exists(model_path)
        models_url = base_url.rstrip("/") + "/v1/models"
        timeout_s = float(os.getenv("LOCAL_LLM_PING_TIMEOUT", "2.5"))
        try:
            resp = requests.get(models_url, timeout=timeout_s)
            if resp.status_code != 200:
                return {
                    "enabled": True,
                    "backend": backend,
                    "reachable": False,
                    "base_url": base_url,
                    "model_path": model_path,
                    "model_exists": model_exists,
                    "error": f"HTTP {resp.status_code}",
                }
            data = resp.json()
            model_ids = []
            if isinstance(data, dict) and isinstance(data.get("data"), list):
                for item in data["data"]:
                    if isinstance(item, dict) and isinstance(item.get("id"), str):
                        model_ids.append(item["id"])
            return {
                "enabled": True,
                "backend": backend,
                "reachable": True,
                "base_url": base_url,
                "model_path": model_path,
                "model_exists": model_exists,
                "models": model_ids[:5],
            }
        except Exception as e:
            return {
                "enabled": True,
                "backend": backend,
                "reachable": False,
                "base_url": base_url,
                "model_path": model_path,
                "model_exists": model_exists,
                "error": str(e),
            }

    if backend == "llama_cpp_python":
        model_path = (os.getenv("LOCAL_LLM_MODEL_PATH") or "").strip()
        ok = bool(model_path) and os.path.exists(model_path)
        try:
            import llama_cpp  # type: ignore

            _ = llama_cpp
            import_ok = True
        except Exception as e:
            import_ok = False
            import_err = str(e)
        status = {"enabled": True, "backend": backend, "model_path": model_path, "exists": ok, "reachable": ok and import_ok}
        if not import_ok:
            status["error"] = import_err
        return status

    if backend == "ollama":
        import requests

        base_url = os.getenv("OLLAMA_URL", "http://localhost:11434").strip()
        tags_url = base_url.rstrip("/") + "/api/tags"
        timeout_s = float(os.getenv("LOCAL_LLM_PING_TIMEOUT", "2.5"))
        try:
            resp = requests.get(tags_url, timeout=timeout_s)
            if resp.status_code != 200:
                return {"enabled": True, "backend": backend, "reachable": False, "base_url": base_url, "error": f"HTTP {resp.status_code}"}
            return {"enabled": True, "backend": backend, "reachable": True, "base_url": base_url}
        except Exception as e:
            return {"enabled": True, "backend": backend, "reachable": False, "base_url": base_url, "error": str(e)}

    return {"enabled": True, "backend": backend, "reachable": False, "error": "Unsupported backend"}


def _parse_source_blocks(kb_results: str) -> List[Dict[str, str]]:
    if not isinstance(kb_results, str) or not kb_results.strip():
        return []

    blocks: List[Dict[str, str]] = []
    pattern = r"\[Source\s+([^\]]+)\]\s+([^\n]+)\n((?:[^\n]|\n(?!\[Source))*)"
    for match in re.finditer(pattern, kb_results):
        src_id = (match.group(1) or "").strip()
        reference = (match.group(2) or "").strip()
        content = (match.group(3) or "").strip()
        if content:
            blocks.append({"id": src_id, "reference": reference, "content": content})
    return blocks


def build_evidence_pack(
    kb_results: str,
    max_sources: int = 6,
    max_chars_per_source: int = 700,
) -> str:
    blocks = _parse_source_blocks(kb_results)
    if not blocks:
        return (kb_results or "").strip()

    packed: List[str] = []
    for i, b in enumerate(blocks[:max_sources], 1):
        ref = (b.get("reference") or "").strip()
        content = (b.get("content") or "").strip()
        if not content:
            continue

        content = re.sub(r"<sup[^>]*>.*?</sup>", "", content, flags=re.IGNORECASE).strip()
        content = re.sub(r"<[^>]+>", "", content).strip()
        content = " ".join(content.split())
        if len(content) > max_chars_per_source:
            content = content[:max_chars_per_source].rstrip() + "…"

        packed.append(f"[Source {i}] {ref}")
        packed.append(content)
        packed.append("")

    return "\n".join(packed).strip()


_llama_cpp_lock = threading.Lock()
_llama_cpp_instance = None


def _call_llama_cpp_python(prompt: str) -> Optional[str]:
    model_path = (os.getenv("LOCAL_LLM_MODEL_PATH") or "").strip()
    if not model_path:
        return None

    global _llama_cpp_instance
    with _llama_cpp_lock:
        if _llama_cpp_instance is None:
            try:
                from llama_cpp import Llama
            except Exception:
                return None

            n_ctx = int(os.getenv("LOCAL_LLM_CTX", "4096"))
            n_threads = int(os.getenv("LOCAL_LLM_THREADS", "4"))
            n_gpu_layers = int(os.getenv("LOCAL_LLM_GPU_LAYERS", "0"))
            _llama_cpp_instance = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                logits_all=False,
                verbose=False,
            )

    try:
        max_tokens = int(os.getenv("LOCAL_LLM_MAX_TOKENS", "2048"))
        temperature = float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.4"))
        out = _llama_cpp_instance.create_completion(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=_LOCAL_LLM_STOP_TOKENS,
        )
        if isinstance(out, dict):
            choices = out.get("choices") or [{}]
            text = (choices[0] or {}).get("text")
        else:
            text = None
        return text.strip() if isinstance(text, str) else None
    except Exception:
        return None


def _call_llama_cpp_server(prompt: str) -> Optional[str]:
    import requests

    base_url = (os.getenv("LLAMA_CPP_SERVER_URL") or "").strip()
    if not base_url:
        base_url = "http://localhost:8080"

    if base_url.endswith("/v1/chat/completions"):
        url = base_url
    elif base_url.endswith("/completion"):
        url = base_url
    else:
        url = base_url.rstrip("/") + "/v1/chat/completions"

    max_tokens = int(os.getenv("LOCAL_LLM_MAX_TOKENS", "2048"))
    temperature = float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.4"))
    http_timeout_s = float(os.getenv("LOCAL_LLM_HTTP_TIMEOUT", "180"))

    try:
        if url.endswith("/completion"):
            payload = {
                "prompt": prompt,
                "n_predict": max_tokens,
                "temperature": temperature,
                "stop": _LOCAL_LLM_STOP_TOKENS,
                "stream": False,
            }
            resp = requests.post(url, json=payload, timeout=http_timeout_s)
            if resp.status_code != 200:
                return None
            data = resp.json()
            text = data.get("content") or data.get("completion")
            return text.strip() if isinstance(text, str) else None

        payload = {
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful Islamic teacher. "
                        "Be warm, respectful, and practical. "
                        "No emojis. "
                        "Never output reasoning or planning. "
                        "Never output <Thought>/<think> tags. "
                        "Only write the final user-facing answer."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": _LOCAL_LLM_STOP_TOKENS,
            "stream": False,
        }
        resp = requests.post(url, json=payload, timeout=http_timeout_s)
        if resp.status_code != 200:
            return None
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            return None
        msg = (choices[0] or {}).get("message") or {}
        content = msg.get("content")
        return content.strip() if isinstance(content, str) else None
    except Exception:
        return None


def _call_ollama(prompt: str) -> Optional[str]:
    import requests

    local_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    model = os.getenv("OLLAMA_MODEL", "llama3")
    try:
        response = requests.post(
            local_url,
            json={
                "model": model, 
                "prompt": prompt, 
                "stream": False,
                "options": {
                    "num_predict": 2048,
                    "temperature": 0.4
                }
            },
            timeout=60,
        )
        if response.status_code == 200:
            return response.json().get("response")
    except Exception:
        pass
    return None


def _fallback_synthesize_from_evidence(question: str, packed_evidence: str) -> str:
    blocks = _parse_source_blocks(packed_evidence or "")
    top_blocks = blocks[:2]

    excerpts: List[str] = []
    cited_ids: List[str] = []
    for b in top_blocks:
        src_id = (b.get("id") or "").strip()
        content = (b.get("content") or "").strip()
        if not content:
            continue
        first_line = content.splitlines()[0].strip()
        excerpt = first_line if len(first_line) <= 260 else first_line[:260].rstrip() + "…"
        if src_id:
            cited_ids.append(src_id)
        excerpts.append(f"- {excerpt}")

    cited_ids = [c for c in cited_ids if c.isdigit()]
    cited_ids = list(dict.fromkeys(cited_ids))

    sources_lines = "\n".join([f"- [Source {n}]" for n in cited_ids[:6]]) or "- [Source 1]"

    excerpts_block = "\n".join(excerpts)
    if excerpts_block:
        excerpts_block = "\n\nMost relevant excerpts:\n" + excerpts_block

    return (
        "1) Answer\n"
        "Assalamu Alaikum wa Rahmatullahi wa Barakatuh.\n\n"
        "I found relevant Islamic guidance in the local knowledge base.\n"
        f"{excerpts_block}\n\n"
        "May Allah grant you clarity and ease as you seek the truth.\n\n"
        "2) Key points\n"
        f"- Read and reflect on the cited evidence (e.g., [Source 1]).\n"
        "- Apply what is clear, and avoid making strong claims beyond the sources.\n"
        "- If your situation is specific, share details so the guidance fits you.\n\n"
        "3) Next step\n"
        f"To guide you better, what is your situation and what outcome are you hoping for?\n\n"
        "4) Sources\n"
        f"{sources_lines}\n"
        "</final>"
    )


def synthesize_from_evidence(
    question: str,
    evidence: str,
    user_profile: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    if not evidence or not isinstance(evidence, str):
        return None

    packed_evidence = build_evidence_pack(
        evidence,
        max_sources=6,
        max_chars_per_source=700,
    )

    profile = user_profile or {}
    user_name = (profile.get("name") or "").strip()
    user_goal = (profile.get("goal") or "").strip()
    level = (profile.get("level") or "beginner").strip()

    persona = "a kind, practical Islamic teacher"
    if level:
        persona += f" teaching a {level} student"

    name_line = f"The user's name is {user_name}." if user_name else ""
    goal_line = f"The user's goal is: {user_goal}." if user_goal else ""

    prompt = (
        "You are " + persona + ".\n"
        "Write a warm, engaging answer grounded ONLY in the provided evidence.\n"
        "Use an Islamic tone that feels caring, practical, and authoritative.\n"
        "Start with: 'Assalamu Alaikum wa Rahmatullahi wa Barakatuh.'\n"
        "No emojis.\n"
        "Use Islamic terms (e.g., Taqwa, Ikhlas, Sabr, Sunnah) where appropriate.\n"
        "Add brief English meaning in parentheses if it helps the user.\n"
        "Be encouraging and academic yet accessible.\n"
        "End with 1 short follow-up question to guide their learning.\n"
        "A brief generic closing dua in English is encouraged.\n"
        "Never reveal your reasoning or internal planning.\n"
        "Never output <Thought> or <think> tags.\n"
        "Do not output anything before the required numbered sections.\n"
        "If evidence is insufficient, state that clearly.\n"
        "CITE SOURCES using specific brackets format in your text:\n"
        "- For Quran: [Quran Surah:Ayah] (e.g., [Quran 2:255])\n"
        "- For Hadith: [Collection #Number] (e.g., [Bukhari #123] or [Muslim #456])\n"
        "- If you cite multiple, use separate brackets.\n"
        f"{name_line}\n"
        f"{goal_line}\n\n"
        f"Question: {question}\n\n"
        "Evidence:\n"
        f"{packed_evidence}\n\n"
        "Return format (strictly follow this 5-part numbered structure, DO NOT use ** symbols anywhere):\n"
        "1) The Radiance of Knowledge\n"
        "(A warm, personalized scholarly introduction that acknowledges the user's query with an Islamic greeting and brief context. Do not repeat the header title.)\n\n"
        "2) The Heart of Wisdom\n"
        "(The direct, user-centric answer to the specific question asked. Focus on clarity and empathy. Do not repeat the header title.)\n\n"
        "3) Divine Light & Guidance\n"
        "(Scholarly Evidence. When citing Quran or Hadith, ALWAYS include the full Arabic text and English translation followed by the citation like [Quran 2:255] or [Bukhari #123]. Do not use labels like 'Translation:' inside the text.)\n\n"
        "4) The Path of Action\n"
        "(Personal Guidance. 3-5 practical, actionable steps the user can take immediately. Do not repeat the header title.)\n\n"
        "5) Sacred Foundations\n"
        "(Key Themes & Insights. Summarize 3-4 broader spiritual themes or scholarly insights derived from the evidence. Followed by a list of citations.)\n"
        "</final>\n"
        "\n"
        "CRITICAL: Avoid using '**' symbols. Do not repeat section headers in the content body. Focus on a warm, personal tone.\n"
    )

    text = call_local_llm(prompt)
    cleaned = _sanitize_user_facing_answer(text)
    if not cleaned:
        cleaned = _fallback_synthesize_from_evidence(question, packed_evidence)
    return _inject_source_references(cleaned, packed_evidence)


@gemini_retry
def synthesize_scholarly_response(
    question: str,
    context: str,
    metadata: Optional[Dict] = None,
    include_thoughts: bool = False,
    rag_display: Optional[str] = None,
    force_local: bool = False,
) -> Any:
    if force_local:
        if rag_display:
            if include_thoughts:
                return rag_display, None
            return rag_display
        if include_thoughts:
            return "Local resilient mode active.", None
        return "Local resilient mode active."

    metadata_str = ""
    if metadata:
        metadata_str = "\n**Real-Time Context:**\n"
        for k, v in metadata.items():
            metadata_str += f"- {k}: {v}\n"

    synth_prompt = f"""\
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

You are a world-class Senior Islamic Scholar and Mufti (Imam Hassan).
You provide responses that are accurate, deeply spiritual, respectful,
and authoritative.

### INTERNAL SCHOLARLY AUDIT (THOUGHT PROCESS)
Before responding, perform this internal audit in your thoughts:
1. **Source Verification**: Does the provided context contain authentic
   Quranic verses or Sahih Hadiths that directly address: {question}?
2. **Context Window Check**: If the context appears expanded, read the
   entire window so rulings are not taken out of context.
3. **Tone Check**: Ensure compassion (Mercy) and firmness on truth (Haqq).

### SCHOLARLY MANDATE
1. **Dynamic Synthesis**: Weave sources into a coherent narrative.
2. **Arabic Excellence**: Use Arabic terms (e.g., Taqwa, Ikhlas, Sabr)
   with English meaning. Include ﷺ after the Prophet's name.
3. **Source Grounding**: Prioritize the retrieved context. If multiple
   sources exist, compare and synthesize them.
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
2. **The Essence**: A bold heading summarizing the core Islamic
   principle.
3. **Detailed Scholarly Guidance**: Comprehensive explanation with
   cited evidence.
4. **Practical Application**: Bullet points on how to live this
   knowledge.
5. **Dua/Closing**: A beautiful closing Dua related to the topic.
6. **Sources**: Exactly "**Sources:** " followed by a clean list at the
   very bottom.

**Response:**
"""
    _ = synth_prompt

    if rag_display:
        if include_thoughts:
            return rag_display, None
        return rag_display

    if include_thoughts:
        return (
            "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
            "Local-only mode is active. Provide a local RAG context to answer."
        ), None

    return (
        "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
        "Local-only mode is active. Provide a local RAG context to answer."
    )


@gemini_retry
def generate_text(
    prompt: str, model: str = GEMINI_MODEL, include_thoughts: bool = False
) -> Any:
    """Generic text generation utility."""
    _ = (prompt, model)
    if include_thoughts:
        return "", None
    return ""


def verify_retrieval_integrity(
    question: str,
    contexts: List[str],
) -> List[int]:
    """
    RAG v2 Authenticity Step: 
    Audit retrieved context chunks and return indices of relevant ones.
    """
    if not contexts:
        return []

    context_block = ""
    for i, c in enumerate(contexts):
        context_block += f"--- CHUNK {i} ---\n{c}\n\n"

    audit_prompt = f"""
    You are an Islamic Scholarly Auditor. Verify if retrieved context
    chunks answer the user's question and are from authentic sources.
    
    User Question: {question}
    
    Retrieved Chunks:
    {context_block}
    
    INSTRUCTIONS:
    1. For each chunk, decide if it is highly relevant to the question.
    2. Respond ONLY with a JSON list of indices (e.g., [0, 2]) for the
       chunks that should be kept.
    3. If none are relevant, respond with [].
    
    Response:
    """
    
    try:
        res_text = generate_text(audit_prompt, model=GEMINI_MODEL)
        import json
        import re
        match = re.search(r'\[.*\]', res_text.strip(), re.DOTALL)
        if match:
            return json.loads(match.group())
        return list(range(len(contexts)))
    except Exception as e:
        print(f"Retrieval Integrity Audit error: {e}")
        return list(range(len(contexts)))

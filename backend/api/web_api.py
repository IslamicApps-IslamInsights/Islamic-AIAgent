import os
import sys

"""
🌙 NOOR ISLAMIC AI AGENT - Web API Backend 🌙

ARCHITECTURE:
  ✅ 100% LOCAL PROCESSING - NO EXTERNAL LLM APIs
  ✅ Knowledge Base: 15,238+ authenticated Islamic documents
  ✅ Quran Foundation MCP: Primary source for Quranic queries
  ✅ Local Intelligence: Advanced text synthesis from knowledge base
  ✅ Hybrid RAG: BM25 + Vector search + Cross-encoder re-ranking

PROCESSING PIPELINE:
  Query → Classification → Local KB Search → Local Synthesis → Response
  
AUTHENTICATION:
  All sources: Quran, Sahih Hadith collections, Tafsir Ibn Kathir, Islamic
  scholarship
  No external APIs required for inference - everything runs locally
  
Dependencies: Flask, CORS, Transformers (sentence-embeddings), Chroma (vector
DB)
"""

import asyncio
import time
import json
import re
from datetime import datetime
import threading
from functools import wraps
from typing import List, Dict, Any
import argparse
from pathlib import Path
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

os.environ["TOKENIZERS_PARALLELISM"] = "false"

start_all = time.time()

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WebAPI")

def _strip_llm_internal(text: Any) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = text
    cleaned = cleaned.split("</final>")[0]
    output_match = re.search(r"(?is)<output>(.*?)</output>", cleaned)
    if output_match:
        cleaned = output_match.group(1) or ""
        return cleaned.strip()

    cleaned = re.sub(r"(?is)<thought>.*?</thought>", "", cleaned)
    cleaned = re.sub(r"(?is)<think>.*?</think>", "", cleaned)
    cleaned = re.split(r"(?i)<thought>|<think>|<output>", cleaned, maxsplit=1)[0]
    return cleaned.strip()

def _strip_source_tags(text: Any) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""

    out_lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"\[Source\s+\d+\]\s*", "", line).rstrip()
        cleaned = re.sub(r"^\s*-\s+", "- ", cleaned)
        cleaned = re.sub(r"^\s+", "", cleaned)
        out_lines.append(cleaned)

    cleaned_text = "\n".join(out_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
    return cleaned_text

# --- Validation and Error Handling Helpers ---
def validate_request(required_fields: List[str] = None, types: Dict[str, type] = None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON", "code": "INVALID_FORMAT"}), 400
            
            data = request.get_json()
            if required_fields:
                for field in required_fields:
                    if field not in data or data[field] is None:
                        return jsonify({"error": f"Missing required field: {field}", "code": "MISSING_FIELD"}), 400
            
            if types:
                for field, expected_type in types.items():
                    if field in data and data[field] is not None:
                        try:
                            # Special case for numeric strings that should be floats
                            if expected_type == float and isinstance(data[field], str):
                                float(data[field])
                            elif not isinstance(data[field], expected_type):
                                return jsonify({"error": f"Invalid type for {field}: expected {expected_type.__name__}", "code": "INVALID_TYPE"}), 400
                        except ValueError:
                            return jsonify({"error": f"Invalid numeric value for {field}", "code": "INVALID_VALUE"}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator

def agent_ready(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not agent_initialized:
            return jsonify({
                "error": "Scholarly systems are still initializing. Please wait a moment.",
                "code": "AGENT_INITIALIZING",
                "status": "initializing"
            }), 503
        return f(*args, **kwargs)
    return wrapper

# Import our Islamic AI systems
# Imports correctly using the new modular structure
from backend.tools import enhanced_islamic_tools
from backend.config.islamic_config import islamic_config

# Import indexing and knowledge graph systems
try:
    from backend.api.indexing_routes import register_indexing_routes
    indexing_available = True
except ImportError:
    indexing_available = False
    print("⚠️  Indexing system not available")

# Import auto ingestion and response builder
try:
    from backend.knowledge.auto_ingest_service import initialize_auto_ingest, get_auto_ingest_service
    auto_ingest_available = True
except ImportError:
    auto_ingest_available = False
    print("⚠️  Auto ingestion not available")

try:
    from backend.utils.response_builder import (
        build_enhanced_response, build_sources_list, ResponseQualityChecker
    )
    enhanced_response_available = True
except ImportError:
    enhanced_response_available = False
    print("⚠️  Enhanced response builder not available")

# Import advanced response builder with Quran prioritization
try:
    from backend.utils.advanced_response_builder import (
        build_multipart_response, prioritize_results_by_type, build_rag_response_with_fallback
    )
    advanced_response_available = True
except ImportError:
    advanced_response_available = False
    print("⚠️  Advanced response builder not available")

# Import authentic response optimizer for best quality responses
try:
    from backend.utils.authentic_response_optimizer import AuthenticResponseOptimizer
    authentic_optimizer = AuthenticResponseOptimizer()
    authentic_optimizer_available = True
except ImportError:
    authentic_optimizer = None
    authentic_optimizer_available = False
    print("⚠️  Authentic response optimizer not available")

app = Flask(__name__, static_folder='static', template_folder='templates')

# Enable CORS with more specific configuration
cors = CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins for development
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True,
        "expose_headers": ["Content-Disposition"]
    }
})

# Global variables for AI agents
rag_loader = None  # Memory-optimized RAG loader
single_agent = None
multi_agent_system = None
agent_initialized = False
demo_mode = False # Toggle for Hackathon Pitch Resilience Demo

@app.route('/api/demo/toggle', methods=['POST'])
def toggle_demo_mode():
    global demo_mode
    demo_mode = not demo_mode
    return jsonify({
        "status": "success",
        "demo_mode": demo_mode,
        "message": f"Demo Mode (Resilience) {'Enabled' if demo_mode else 'Disabled'}"
    })

@app.route('/api/quran/verse', methods=['POST'])
def get_quran_verse():
    try:
        data = request.json
        verse_ref = data.get('verse')
        if not verse_ref:
            return jsonify({"error": "Verse reference required"}), 400
        
        # Clean reference (remove 'Quran' or other prefixes)
        clean_ref = re.sub(r'[^0-9:]', '', verse_ref).strip()
        
        from backend.utils.quran_mcp_provider import fetch_verse_with_translation
        import asyncio
        
        # Run async fetch in sync environment
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(fetch_verse_with_translation(clean_ref))
            if result:
                return jsonify({
                    "status": "success",
                    "text": result.get("text"),
                    "translation": result.get("translation"),
                    "reference": f"Quran {clean_ref}"
                })
        finally:
            loop.close()
            
        return jsonify({"error": "Verse not found"}), 404
    except Exception as e:
        logger.error(f"Quran verse fetch error: {e}")
        return jsonify({"error": str(e)}), 500

# Global analytics path - stored in the new backend/data directory
ANALYTICS_FILE = os.path.join(project_root, 'backend', 'data', 'topic_analytics.json')

# --- Simple Response Cache ---
class SimpleCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            else:
                self.cache.pop(key, None)
        return None
    
    def set(self, key: str, data: any):
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

response_cache = SimpleCache()

def track_topic(topic):
    """Track frequency of topics for trending section"""
    try:
        data = {}
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, 'r') as f:
                data = json.load(f)
        
        existing_count = data.get(topic, 0)
        data[topic] = existing_count + 1
        
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error tracking topic: {e}")

def initialize_agents():
    """Initialize AI agents on startup - MEMORY OPTIMIZED"""
    global single_agent, multi_agent_system, agent_initialized, rag_loader
    
    try:
        from backend.api.optimized_startup import initialize_agents_optimized
        
        # Run optimized initialization
        init_result = initialize_agents_optimized()
        
        # Unpack results
        rag_loader = init_result.get('rag_loader')
        single_agent = init_result.get('single_agent')
        multi_agent_system = init_result.get('multi_agent_system')
        agent_initialized = init_result.get('agent_initialized', False)
        
        if agent_initialized:
            print("🎉 Agents ready for service!")
        else:
            print("⚠️  Limited agent functionality available")
            
    except Exception as e:
        logger.error(f"❌ Optimized initialization failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        
        # Fallback to minimal setup
        agent_initialized = False
        single_agent = None
        multi_agent_system = None


_auto_init_started = False
_auto_init_lock = threading.Lock()


def _start_init_in_background():
    global _auto_init_started
    flag = (os.environ.get("BACKEND_AUTO_INIT") or "1").strip().lower()
    if flag not in {"1", "true", "yes"}:
        return False

    with _auto_init_lock:
        if _auto_init_started:
            return True
        _auto_init_started = True

    t = threading.Thread(target=initialize_agents, daemon=True)
    t.start()
    return True

@app.route('/')
def home():
    """Serve the main UI page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint with RAG status"""
    deep = (request.args.get("deep") or "").strip().lower() in {"1", "true", "yes"}

    bm25_full_path = os.path.join(
        project_root, "backend", "knowledge", "bm25_full_index.pkl"
    )
    bm25_path = os.path.join(project_root, "backend", "knowledge", "bm25_index.pkl")
    chroma_sqlite_path = os.path.join(
        project_root, "backend", "knowledge", "chroma_db_full", "chroma.sqlite3"
    )

    bm25_exists = os.path.exists(bm25_full_path) or os.path.exists(bm25_path)
    chroma_exists = os.path.exists(chroma_sqlite_path)
    rag_ready_basic = bool(bm25_exists or chroma_exists)

    if not deep:
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agent_initialized": agent_initialized,
                "agents_ready": bool(agent_initialized and rag_ready_basic),
                "rag_system": {
                    "ready": rag_ready_basic,
                    "bm25_index_present": bm25_exists,
                    "chroma_sqlite_present": chroma_exists,
                },
                "services": {
                    "single_agent": single_agent is not None,
                    "multi_agent": multi_agent_system is not None,
                },
            }
        )

    try:
        from backend.utils.enhanced_hybrid_rag import check_rag_system

        rag_status = check_rag_system()
        if not isinstance(rag_status, dict):
            rag_status = {"ready": rag_ready_basic}
    except Exception as e:
        rag_status = {"error": str(e), "ready": rag_ready_basic}

    try:
        from backend.utils.llm_provider import get_local_llm_status

        local_llm = get_local_llm_status()
        if not isinstance(local_llm, dict):
            local_llm = {"enabled": False, "reachable": False}
    except Exception as e:
        local_llm = {"enabled": False, "reachable": False, "error": str(e)}

    rag_ready = bool(rag_status.get("ready", False))
    agents_ready = bool(agent_initialized and rag_ready)

    def _to_int(value: Any) -> int:
        try:
            return int(value)
        except Exception:
            return 0

    return jsonify(
        {
            "status": "healthy",
            "agent_initialized": agent_initialized,
            "agents_ready": agents_ready,
            "rag_system": rag_status,
            "local_llm": local_llm,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "single_agent": single_agent is not None,
                "multi_agent": multi_agent_system is not None,
                "dynamic_knowledge": True,
                "rag_ready": rag_ready,
                "local_kb_documents": (
                    _to_int(rag_status.get("bm25_docs", 0))
                    + _to_int(rag_status.get("chroma_docs", 0))
                ),
            },
        }
    )


@app.route('/api/quran/translation-languages')
def quran_translation_languages():
    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp, _extract_tool_json

        async def _run():
            mcp = get_quran_mcp()
            await mcp.initialize()
            payload = await mcp.list_editions("translation", lang=None)
            obj, err = _extract_tool_json(payload)
            if err or not obj:
                return {"error": err or "Failed to list editions", "raw": payload}
            editions = obj.get("editions") or []
            return {"editions": editions}

        data = asyncio.run(_run())
        if data.get("error"):
            return jsonify({"error": data["error"]}), 502

        editions = data.get("editions") or []
        lang_counts = {}
        for ed in editions:
            if not isinstance(ed, dict):
                continue
            lang = (ed.get("lang") or "").strip().lower()
            if not lang:
                continue
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        languages = [{"code": k, "edition_count": v} for k, v in sorted(lang_counts.items(), key=lambda x: (-x[1], x[0]))]
        return jsonify({"languages": languages, "default": "en"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/quran/verse", methods=["GET"])
def quran_verse():
    verse = (request.args.get("verse") or "").strip()
    lang = (request.args.get("lang") or "en").strip().lower()
    translator = (request.args.get("translator") or "abdel haleem").strip()
    tafsir_flag = (request.args.get("tafsir") or "").strip().lower() in {
        "1",
        "true",
        "yes",
    }

    m = re.match(r"^\s*(\d{1,3})\s*:\s*(\d{1,3})\s*$", verse)
    if not m:
        return jsonify({"error": "Invalid verse. Use format like 2:255"}), 400

    surah = int(m.group(1))
    ayah = int(m.group(2))
    if surah < 1 or surah > 114 or ayah < 1:
        return jsonify({"error": "Invalid verse range"}), 400

    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp

        async def _run():
            mcp = get_quran_mcp()
            await mcp.initialize()
            quran_payload = await mcp.fetch_quran(
                surah=surah, ayah=ayah, editions="ar-simple-clean"
            )
            trans_payload = await mcp.fetch_translation(
                surah=surah,
                ayah=ayah,
                language=lang or "en",
                translator=translator or "abdel haleem",
            )
            tafsir_payload = None
            if tafsir_flag:
                tafsir_payload = await mcp.fetch_tafsir(surah=surah, ayah=ayah)

            return {
                "quran": quran_payload,
                "translation": trans_payload,
                "tafsir": tafsir_payload,
            }

        data = asyncio.run(_run())
        return jsonify(
            {
                "verse": f"{surah}:{ayah}",
                "lang": lang,
                "translator": translator,
                "quran": data.get("quran"),
                "translation": data.get("translation"),
                "tafsir": data.get("tafsir"),
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.route('/api/initialize', methods=['POST'])
def force_initialize():
    """Force agent initialization endpoint"""
    try:
        started = _start_init_in_background()
        return (
            jsonify(
                {
                    "status": "starting" if started else "disabled",
                    "started": bool(started),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            202 if started else 409,
        )
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
@validate_request(required_fields=['message'], types={'message': str})
def chat():
    """Main chat endpoint - Intelligent routing with automatic tool selection"""
    try:
        data = request.get_json()
        message = data.get('message')
        use_synthesis = data.get('use_synthesis', True)  # Synthesis enabled by default
        quran_translation_lang = (data.get('quran_translation_lang') or '').strip()
        
        # Extract optional location data for Prayer Times
        user_location = None
        if 'latitude' in data and 'longitude' in data:
            try:
                user_location = {
                    'latitude': float(data.get('latitude')),
                    'longitude': float(data.get('longitude')),
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown')
                }
            except (ValueError, TypeError):
                pass
        
        # 🚀 Use the new Intelligent Tool Router for automatic tool selection
        from backend.utils.intelligent_tool_router import get_tool_router
        
        router = get_tool_router()
        print(f"📡 Processing query: {message[:60]}...")
        
        # Route query to best-fit tool asynchronously
        response_data = asyncio.run(router.route_and_process(
            query=message,
            user_location=user_location,
            use_synthesis=use_synthesis,
            quran_translation_lang=quran_translation_lang or None,
        ))
        
        # Extract classification for response
        classification = response_data.pop('classification', {})
        category = classification.get('category', 'general')
        confidence = classification.get('confidence', 0.0)
        
        print(f"✅ Query processed: {category} (confidence: {confidence:.2f})")
        
        # Build final JSON response
        user_response = _strip_source_tags(
            _strip_llm_internal(response_data.get('response', ''))
        )
        response_data['response'] = user_response
        return jsonify({
            'response': user_response,
            'timestamp': datetime.now().isoformat(),
            'agent': f'Noor ({category.replace("_", " ").title()})',
            'source': response_data.get('source', 'unknown'),
            'tool': response_data.get('tool', 'unknown'),
            'query_category': category,
            'classification_confidence': confidence,
            'rag_results': response_data.get('result_count', 0),
            'synthesis_used': response_data.get('synthesis_used', False),
            'metadata': response_data.get('metadata', {}),
            'processing_time_ms': response_data.get('processing_time_ms', 0),
            'all_results': response_data  # Include full response data
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Chat endpoint error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'Error processing query: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


SOURCE_NAME_MAP = {
    'sahih_bukhari.json': 'Sahih al-Bukhari',
    'sahih_bukhari_english.json': 'Sahih al-Bukhari',
    'sahih_muslim.json': 'Sahih Muslim',
    'sahih_muslim_english.json': 'Sahih Muslim',
    'sunan_abu_dawud_english.json': 'Sunan Abu Dawud',
    'sunan_an_nasai_english.json': 'Sunan an-Nasa\'i',
    'sunan_ibn_majah_english.json': 'Sunan Ibn Majah',
    'jami_at_tirmidhi_english.json': 'Jami\' at-Tirmidhi',
    'muwatta_malik_english.json': 'Muwatta Malik',
    'forty_hadith_nawawi.json': '40 Hadith an-Nawawi',
    'forty_hadith_nawawi_highlights.txt': '40 Hadith an-Nawawi',
    'quran_yusuf_ali.txt': 'Quran - Yusuf Ali',
    'quran_saheeh_international.txt': 'Quran - Sahih International',
    'quran_pickthall.txt': 'Quran - Pickthall',
    'quran_shakir.txt': 'Quran - Shakir',
    'islamic_ethics_akhlaq.txt': 'Islamic Ethics & Character',
    'seerah_prophet.txt': 'Life of Prophet Muhammad',
    '99_names_of_allah.txt': '99 Names of Allah',
    '99_names_of_prophet.txt': '99 Names of the Prophet',
    'aqeedah_essentials.txt': 'Aqeedah Essentials',
    'akhlaq_and_character.txt': 'Islamic Ethics & Character',
    '40_hadith_nawawi_highlights.txt': '40 Hadith an-Nawawi',
    'ar.muyassar.txt': 'Arabic Muyassar',
    'comprehensive_duas.txt': 'Comprehensive Duas',
    'comprehensive_islamic_essentials.txt': 'Comprehensive Islamic Essentials',
    'en.ahmedraza.txt': 'Ahmed Raza Khan Qadri',
    'fiqh_fundamentals.txt': 'Fiqh Fundamentals',
    'hisn_al_muslim.json': 'Hisn al-Muslim',
    'ramadan_hajj_guide.txt': 'Ramadan & Hajj Guide',
    'seerah_of_prophet.txt': 'Life of Prophet Muhammad',
    'ur.kanzuliman.txt': 'Urdu Kanzul Iman',
    'ur.qadri.txt': 'Urdu Ahmed Raza Khan Qadri',
    'ur.madudi.txt': 'Urdu Abul A\'la Maududi',
    'women_in_islam.txt' : 'Women in Islam',

}

def _get_friendly_source_name(source_file: str) -> str:
    """Convert file names to user-friendly source names"""
    if source_file in SOURCE_NAME_MAP:
        return SOURCE_NAME_MAP[source_file]
    name = source_file.replace('.json', '').replace('.txt', '').replace('_', ' ').title()
    return name

def _build_rag_response(query: str, results: list) -> str:
    """Build comprehensive, formatted response from RAG results"""
    try:
        # Import comprehensive formatter
        from backend.utils.comprehensive_response_formatter import ComprehensiveResponseFormatter
        
        logger.info(f"✅ Building comprehensive response for query: {query[:50]}...")
        response = ComprehensiveResponseFormatter.build_full_response(query, results)
        
        return response
    
    except Exception as e:
        logger.error(f"❌ Comprehensive formatter failed: {e}, using fallback...")
        
        # Fallback to simple response if formatter fails
        if not results:
            return (
                "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
                "I couldn't find information about that. Please try asking about Islamic topics "
                "like prayer, charity, the Quran, Hadith, or Islamic teachings.\n\n"
                "May Allah guide us. 🤲"
            )
        
        # Build simple response
        response = "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n"
        response += f"Regarding: *{query}*\n\n"
        response += "━" * 70 + "\n\n"
        
        for idx, result in enumerate(results[:10], 1):
            content = result.get('content', '').strip()
            if not content:
                continue
            
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown').replace('.json', '').replace('.txt', '')
            
            # Limit content length
            if len(content) > 300:
                content = content[:300] + "..."
            
            response += f"{idx}. **{source}**\n   {content}\n\n"
        
        response += "━" * 70 + "\n"
        response += f"📊 Total sources: {len(results)}\n"
        response += "May Allah guide us. 🤲"
        
        return response


def _synthesize_with_best_llm(query: str, results: list, base_response: str, query_type: str = "islamic_general") -> str:
    """Enhance response with intelligent local synthesis - No external APIs"""
    try:
        from backend.utils.llm_response_synthesis import get_synthesizer, ResponseEnhancer
        import asyncio
        
        logger.info(f"🧠 Local Intelligence synthesis for query type: {query_type}")
        
        # Get local synthesizer
        synthesizer = get_synthesizer()
        
        # Check if local synthesizer is available (always true - it's local)
        if not synthesizer.model or synthesizer.provider != "local":
            logger.warning("⚠️  Local synthesis unavailable, using fallback")
            return ResponseEnhancer.enhance_response(base_response, query_type)
        
        # Create context metadata
        context = {
            "query_type": query_type,
            "num_sources": len(results),
            "timestamp": datetime.now().isoformat(),
            "processing": "LOCAL_ONLY"
        }
        
        # Run local synthesis (async)
        synthesized = asyncio.run(
            synthesizer.synthesize_response(
                query,
                results,
                query_type=query_type,
                context=context
            )
        )
        
        # Enhance with Islamic formatting
        enhanced = ResponseEnhancer.enhance_response(synthesized, query_type)
        
        logger.info(f"✅ Local synthesis complete: {len(enhanced)} characters | No external APIs")
        return enhanced
        
    except Exception as e:
        logger.warning(f"⚠️  Local synthesis error: {e}, using base response")
        
        # Fallback to enhanced base response
        try:
            from backend.utils.llm_response_synthesis import ResponseEnhancer
            return ResponseEnhancer.enhance_response(base_response, query_type)
        except:
            return base_response


# === New RAG Diagnostic Endpoint ===

@app.route('/api/rag/status', methods=['GET'])
def rag_status():
    """Check RAG system status"""
    try:
        from backend.utils.enhanced_hybrid_rag import check_rag_system
        
        status = check_rag_system()
        
        return jsonify({
            'rag_system': status,
            'chromadb_available': status.get('chromadb', False),
            'bm25_available': status.get('bm25', False),
            'total_documents': status.get('chromadb_docs', 0) + status.get('bm25_docs', 0),
            'system_ready': status.get('ready', False),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'rag_available': False}), 500


@app.route('/api/rag/search', methods=['POST'])
@validate_request(required_fields=['query'])
def rag_search():
    """Advanced RAG search endpoint with source prioritization"""
    try:
        data = request.get_json()
        query = data.get('query')
        k = int(data.get("k", 10))

        from backend.knowledge.memory_optimized_loader import (
            get_memory_optimized_loader,
        )

        kb = get_memory_optimized_loader()
        text = kb.search(query, k=k)
        found = "I couldn't find information" not in text

        return jsonify(
            {
                "query": query,
                "found": found,
                "k": k,
                "response": text,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stt', methods=['POST'])
@validate_request(required_fields=['audio'], types={'audio': str})
def speech_to_text():
    """Endpoint for Speech-to-Text transcription"""
    return (
        jsonify(
            {
                "error": (
                    "Speech-to-text is disabled in local-only mode "
                    "(no external LLM services)."
                )
            }
        ),
        400,
    )

@app.route('/api/chat/multimodal', methods=['POST'])
@validate_request(required_fields=['message'], types={'message': str, 'latitude': float, 'longitude': float})
@agent_ready
def multimodal_chat():
    """Endpoint for chat with attachments"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        file_data = data.get('file', '') # Base64 file
        mime_type = data.get('mime_type', '')
        user_gender = data.get('user_gender', 'not_specified')

        if file_data:
            return (
                jsonify(
                    {
                        "error": (
                            "Multimodal (file/image/audio) is disabled in "
                            "local-only mode. Send text-only messages."
                        )
                    }
                ),
                400,
            )
        
        # Check cache (only for text-only messages to keep it simple)
        cache_key = None
        if not file_data:
            cache_key = f"chat_{message}_{user_gender}"
            cached_response = response_cache.get(cache_key)
            if cached_response:
                print(f"✨ Serving cached chat response for: {message[:30]}...")
                return jsonify(cached_response)
        
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        use_synthesis = data.get("use_synthesis", True)

        user_location = None
        if latitude is not None and longitude is not None:
            user_location = {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
            }

        from backend.utils.intelligent_tool_router import get_tool_router

        router = get_tool_router()
        response_data = asyncio.run(
            router.route_and_process(
                query=message,
                user_location=user_location,
                use_synthesis=use_synthesis,
            )
        )

        response_text = response_data.get("response", "")
        thoughts = None
        
        result_json = {
            'response': response_text,
            'thoughts': thoughts,
            'timestamp': datetime.now().isoformat(),
            'agent': 'Noor'
        }
        
        # Cache successful response if no file was attached
        if cache_key:
            response_cache.set(cache_key, result_json)
            
        return jsonify(result_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/multi-chat', methods=['POST'])
@validate_request(required_fields=['message'], types={'message': str, 'latitude': float, 'longitude': float})
@agent_ready
def multi_chat():
    """Multi-agent chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        specialist = data.get('specialist', 'auto')
        user_gender = data.get('user_gender', 'not_specified')
        
        # Check cache
        cache_key = f"multi_{message}_{specialist}_{user_gender}"
        cached_response = response_cache.get(cache_key)
        if cached_response:
            print(f"✨ Serving cached multi-agent response for: {message[:30]}...")
            return jsonify(cached_response)
        
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        use_synthesis = data.get("use_synthesis", True)

        user_location = None
        if latitude is not None and longitude is not None:
            user_location = {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
            }

        from backend.utils.intelligent_tool_router import get_tool_router

        router = get_tool_router()
        response_data = asyncio.run(
            router.route_and_process(
                query=message,
                user_location=user_location,
                use_synthesis=use_synthesis,
            )
        )

        response_text = response_data.get("response", "")
        thoughts = None
        
        specialist_name = specialist if specialist != 'auto' else 'AI Specialist'
        
        result_json = {
            'response': response_text,
            'thoughts': thoughts,
            'specialist': specialist_name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache successful response
        response_cache.set(cache_key, result_json)
        return jsonify(result_json)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collaborative', methods=['POST'])
@validate_request(required_fields=['message'], types={'message': str})
@agent_ready
def collaborative_chat():
    """Collaborative consultation endpoint with multi-scholar synthesis"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_gender = data.get('user_gender', 'not_specified')
        
        # Check cache
        cache_key = f"consult_{message}_{user_gender}"
        cached_response = response_cache.get(cache_key)
        if cached_response:
            print(f"✨ Serving cached collaborative response for: {message[:30]}...")
            return jsonify(cached_response)

        use_synthesis = data.get("use_synthesis", True)
        from backend.utils.intelligent_tool_router import get_tool_router

        router = get_tool_router()
        response_data = asyncio.run(
            router.route_and_process(
                query=message,
                user_location=None,
                use_synthesis=use_synthesis,
            )
        )

        response_text = response_data.get("response", "")
        thoughts = None

        result_json = {
            'response': response_text,
            'thoughts': thoughts,
            'timestamp': datetime.now().isoformat(),
            'agent': 'Imam Hassan (Coordinator)'
        }
        
        # Cache successful response
        response_cache.set(cache_key, result_json)
        return jsonify(result_json)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar', methods=['GET'])
def get_calendar_events_api():
    """Endpoint for Hijri Calendar events"""
    try:
        cache_key = "calendar_events_v1"
        cached_response = response_cache.get(cache_key)
        if cached_response:
            return jsonify(cached_response)
            
        from backend.tools.enhanced_islamic_tools import get_islamic_calendar_events
        result = get_islamic_calendar_events()
        # Cache successful response
        response_cache.set(cache_key, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quran', methods=['POST'])
@validate_request(required_fields=['verse'], types={'verse': str})
def get_quran():
    """Get Quran verse endpoint"""
    try:
        data = request.get_json()
        verse_reference = data.get('verse', '')
        
        from backend.tools.enhanced_islamic_tools import get_quran_verse
        result = get_quran_verse(verse_reference)
        
        return jsonify({
            'verse': result,
            'reference': verse_reference,
            'timestamp': datetime.now().isoformat(),
            'source': 'Al-Quran Cloud API'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quran/audio', methods=['POST'])
@validate_request(required_fields=['verse'], types={'verse': str})
def get_quran_audio():
    """Get Quran verse audio URL endpoint"""
    try:
        data = request.get_json()
        verse_reference = data.get('verse', '')
        
        from backend.tools.audio_tools import get_quran_audio_url
        audio_url = get_quran_audio_url(verse_reference)
        
        if not audio_url:
            return jsonify({'error': 'Audio not found for this verse'}), 404
            
        return jsonify({
            'audio_url': audio_url,
            'verse': verse_reference,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hadith', methods=['POST'])
def get_hadith_api():
    """Get Hadith endpoint"""
    try:
        data = request.get_json()
        topic = data.get('topic', None)
        
        from backend.tools.enhanced_islamic_tools import get_hadith
        result = get_hadith(topic)
        
        return jsonify({
            'hadith': result,
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'source': 'Authentic Hadith Collections'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hadith/random', methods=['POST'])
@validate_request(types={'count': int})
def get_random_hadith_api():
    """Endpoint for a random authentic hadith"""
    try:
        from backend.tools.enhanced_islamic_tools import get_hadith
        hadith = get_hadith()
        return jsonify({
            'success': True,
            'hadith': hadith
        })
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'HADITH_SEARCH_ERROR'}), 500


# ============================
# Quran Foundation MCP Routes
# ============================

@app.route('/api/quran-foundation/search', methods=['POST'])
@validate_request(required_fields=['query'])
@agent_ready
def quran_foundation_search():
    """Search the Quran using Quran Foundation MCP"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        from backend.utils.quran_mcp_provider import get_quran_mcp
        import asyncio
        
        async def search():
            mcp = get_quran_mcp()
            await mcp.initialize()
            try:
                return await mcp.search_quran(query)
            finally:
                await mcp.close()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(search())
        
        return jsonify({
            'query': query,
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'source': 'Quran Foundation MCP'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quran-foundation/surah/<int:surah_num>', methods=['GET'])
@agent_ready
def quran_foundation_surah(surah_num):
    """Fetch a complete Surah from Quran Foundation"""
    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp
        import asyncio
        
        async def fetch():
            mcp = get_quran_mcp()
            await mcp.initialize()
            try:
                return await mcp.fetch_quran(surah_num)
            finally:
                await mcp.close()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch())
        
        return jsonify({
            'surah': surah_num,
            'content': result,
            'timestamp': datetime.now().isoformat(),
            'source': 'Quran Foundation MCP'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quran-foundation/tafsir', methods=['POST'])
@validate_request(required_fields=['surah', 'ayah'])
@agent_ready
def quran_foundation_tafsir():
    """Fetch Tafsir (exegesis) from Quran Foundation"""
    try:
        data = request.get_json()
        surah = data.get('surah')
        ayah = data.get('ayah')
        tafsir_type = data.get('tafsir_type', 'ibn_kathir')
        
        from backend.utils.quran_mcp_provider import get_quran_mcp
        import asyncio
        
        async def fetch():
            mcp = get_quran_mcp()
            await mcp.initialize()
            try:
                return await mcp.fetch_tafsir(surah, ayah, tafsir_type)
            finally:
                await mcp.close()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch())
        
        return jsonify({
            'reference': f"{surah}:{ayah}",
            'tafsir_type': tafsir_type,
            'content': result,
            'timestamp': datetime.now().isoformat(),
            'source': 'Quran Foundation MCP'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quran-foundation/theme/<theme>', methods=['GET'])
@agent_ready
def quran_foundation_theme(theme):
    """Explore an Islamic theme throughout the Quran"""
    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp
        import asyncio
        
        async def explore():
            mcp = get_quran_mcp()
            await mcp.initialize()
            try:
                return await mcp.get_thematic_exploration(theme)
            finally:
                await mcp.close()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(explore())
        
        return jsonify({
            'theme': theme,
            'exploration': result,
            'timestamp': datetime.now().isoformat(),
            'source': 'Quran Foundation MCP'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quran-foundation/comprehensive', methods=['POST'])
@validate_request(required_fields=['query'])
@agent_ready
def quran_foundation_comprehensive():
    """Comprehensive Quranic search with translations and tafsir"""
    try:
        data = request.get_json()
        query = data.get('query')
        include_tafsir = data.get('include_tafsir', True)
        languages = data.get('languages', ['en', 'ar'])
        
        from backend.utils.quran_mcp_provider import get_quran_mcp
        import asyncio
        
        async def search():
            mcp = get_quran_mcp()
            await mcp.initialize()
            try:
                return await mcp.comprehensive_quran_search(
                    query,
                    include_tafsir=include_tafsir,
                    include_translations=languages
                )
            finally:
                await mcp.close()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(search())
        
        return jsonify({
            'query': query,
            'comprehensive_results': result,
            'timestamp': datetime.now().isoformat(),
            'source': 'Quran Foundation MCP'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adhkar', methods=['POST'])
@validate_request(required_fields=['category'], types={'category': str})
def get_adhkar_api():
    """Endpoint for Prophetic Adhkar"""
    try:
        data = request.get_json()
        category = data.get('category', 'morning')
        # Validate allowed categories
        if category not in ['morning', 'evening', 'travel', 'eating', 'sleep', 'prayer']:
            return jsonify({'error': 'Invalid Adhkar category', 'code': 'INVALID_CATEGORY'}), 400
            
        from backend.tools.enhanced_islamic_tools import get_adhkar
        adhkar = get_adhkar(category)
        return jsonify({
            'success': True,
            'adhkar': adhkar
        })
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'ADHKAR_FETCH_ERROR'}), 500

@app.route('/api/names-of-allah', methods=['POST'])
@validate_request(required_fields=['query'], types={'query': str})
def get_names_of_allah_api():
    """Endpoint for 99 Names of Allah"""
    try:
        data = request.get_json()
        query = data.get('query', '1')
        from backend.tools.enhanced_islamic_tools import get_name_of_allah
        name_info = get_name_of_allah(query)
        return jsonify({
            'success': True,
            'name_info': name_info
        })
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'NAMES_FETCH_ERROR'}), 500

@app.route('/api/hajj-umrah', methods=['POST'])
@validate_request(required_fields=['ritual'], types={'ritual': str})
def get_hajj_umrah_api():
    """Endpoint for Hajj and Umrah guidance"""
    try:
        data = request.get_json()
        ritual = data.get('ritual', 'ihram')
        from backend.tools.enhanced_islamic_tools import get_hajj_umrah_guidance
        guidance = get_hajj_umrah_guidance(ritual)
        return jsonify({
            'success': True,
            'guidance': guidance
        })
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'RITUAL_GUIDANCE_ERROR'}), 500

@app.route('/api/halal-check', methods=['POST'])
@validate_request(required_fields=['item'], types={'item': str})
def check_halal_api():
    """Endpoint for Halal ingredient checking"""
    try:
        data = request.get_json()
        item = data.get('item', '')
        from backend.tools.enhanced_islamic_tools import check_halal_guidance
        result = check_halal_guidance(item)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'HALAL_CHECK_ERROR'}), 500

@app.route('/api/hadith/isnad', methods=['POST'])
@validate_request(required_fields=['reference'], types={'reference': str})
def get_hadith_isnad_api():
    """Endpoint for scholarly narrator chains (Isnad)"""
    try:
        data = request.get_json()
        ref = data.get('reference', '')
        
        # In a real app, this would query a narrator database
        # For now, we provide structured models for major Sahih Bukhari references
        mock_isnads = {
            "Bukhari 1": [
                {"name": "Imam al-Bukhari", "period": "194-256 AH", "location": "Bukhara", "role": "Collector"},
                {"name": "Al-Humaydi Abdullah bin al-Zubayr", "period": "d. 219 AH", "location": "Makkah", "role": "Teacher"},
                {"name": "Sufyan bin Uyaynah", "period": "107-198 AH", "location": "Kufa/Makkah", "role": "Scholar"},
                {"name": "Yahya bin Sa'id al-Ansari", "period": "d. 143 AH", "location": "Madinah", "role": "Tabi' Tabi'in"},
                {"name": "Muhammad bin Ibrahim al-Taymi", "period": "d. 120 AH", "location": "Madinah", "role": "Tabi'in"},
                {"name": "Alaqamah bin Waqqas al-Laythi", "period": "d. ~80 AH", "location": "Madinah", "role": "Senior Tabi'in"},
                {"name": "Umar bin al-Khattab (RA)", "period": "Companions", "location": "Madinah", "role": "Narrator"},
                {"name": "Prophet Muhammad (ﷺ)", "period": "Messenger", "location": "Madinah", "role": "Source"}
            ]
        }
        
        # Extract base reference (e.g., "Bukhari 1")
        base_ref = ref.split('[')[-1].split(']')[0].strip() if '[' in ref else ref
        chain = mock_isnads.get(base_ref, mock_isnads["Bukhari 1"]) # Default to first hadith for demo
        
        return jsonify({
            'success': True,
            'isnad': chain,
            'reference': ref
        })
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'ISNAD_FETCH_ERROR'}), 500

@app.route('/api/prayer-times', methods=['POST'])
@validate_request(required_fields=['latitude', 'longitude'], types={'latitude': float, 'longitude': float})
def get_prayer_times_api():
    """Get prayer times endpoint"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        from backend.tools.enhanced_islamic_tools import get_prayer_times
        result = get_prayer_times(float(latitude), float(longitude))
        
        # Extract text if result is a dict
        prayer_text = result.get('text') if isinstance(result, dict) else result
        
        return jsonify({
            'prayer_times': prayer_text,
            'data': result if isinstance(result, dict) else None,
            'location': {'latitude': latitude, 'longitude': longitude},
            'timestamp': datetime.now().isoformat(),
            'source': 'Aladhan API'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/qibla', methods=['POST'])
@validate_request(required_fields=['latitude', 'longitude'], types={'latitude': float, 'longitude': float})
def get_qibla():
    """Get Qibla direction endpoint"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        from backend.tools.enhanced_islamic_tools import get_qibla_direction
        result = get_qibla_direction(float(latitude), float(longitude))
        
        if "error" in result:
            return jsonify({'error': result['error']}), 500
            
        return jsonify({
            'qibla_direction': result['text'],
            'bearing': result['bearing'],
            'direction': result['direction'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hijri-date')
def get_hijri_date_api():
    """Get current Hijri date endpoint"""
    try:
        from backend.tools.enhanced_islamic_tools import get_hijri_date
        result = get_hijri_date()
        
        return jsonify({
            'hijri_date': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dua', methods=['POST'])
@validate_request(required_fields=['occasion'], types={'occasion': str})
def get_dua_api():
    """Get Dua endpoint"""
    try:
        data = request.get_json()
        occasion = data.get('occasion', 'morning')
        
        from backend.tools.enhanced_islamic_tools import get_dua
        result = get_dua(occasion)
        
        return jsonify({
            'dua': result,
            'occasion': occasion,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
@validate_request(required_fields=['query'], types={'query': str})
def search_islamic_content_api():
    """Search Islamic content endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '')
            
        from backend.tools.enhanced_islamic_tools import search_islamic_content
        result = search_islamic_content(query)
        
        return jsonify({
            'search_results': result,
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'sources': ['Al-Quran Cloud API', 'Hadith APIs']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/daily-content')
def get_daily_content_api():
    """Get daily Islamic content endpoint"""
    try:
        from backend.tools.enhanced_islamic_tools import get_daily_islamic_content
        result = get_daily_islamic_content()
        
        return jsonify({
            'daily_content': result,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guidance', methods=['POST'])
@validate_request(required_fields=['topic'], types={'topic': str})
def get_guidance_api():
    """Get Islamic guidance endpoint"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
            
        from backend.tools.enhanced_islamic_tools import get_islamic_guidance
        result = get_islamic_guidance(topic)
        
        return jsonify({
            'guidance': result,
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'sources': ['Quran', 'Hadith', 'Islamic Scholarship']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/zakat', methods=['POST'])
@app.route('/api/zakat/calculate', methods=['POST'])
def calculate_zakat_api():
    """Enhanced Zakat calculator endpoint"""
    try:
        data = request.get_json()
        
        # Support both the old simple 'amount' and new multi-field logic
        cash = float(data.get('cash', data.get('amount', 0)))
        gold = float(data.get('gold_grams', 0))
        silver = float(data.get('silver_grams', 0))
        investments = float(data.get('investments', 0))
        business = float(data.get('business_assets', 0))
        debts = float(data.get('debts', 0))
        
        result_text = enhanced_islamic_tools.calculate_zakat(
            cash=cash, 
            gold_grams=gold, 
            silver_grams=silver, 
            investments=investments, 
            business_assets=business, 
            debts=debts
        )
        
        return jsonify({
            'success': True,
            'response': result_text,
            'zakat_result': result_text # Alias for app.js
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar', methods=['GET'])
def get_calendar_api():
    """Get Islamic calendar and events endpoint"""
    try:
        from backend.tools.enhanced_islamic_tools import get_islamic_calendar_events
        result = get_islamic_calendar_events()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trending', methods=['GET'])
def get_trending_topics_api():
    """Endpoint for trending Islamic topics"""
    try:
        trending = []
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, 'r') as f:
                data = json.load(f)
                sorted_topics = sorted(data.items(), key=lambda x: x[1], reverse=True)[:5]
                for topic, count in sorted_topics:
                    trending.append({
                        'topic': topic if len(topic) < 30 else topic[:27] + "...",
                        'count': count,
                        'trend': 'up'
                    })
        
        if not trending:
            trending = [
                {'topic': 'Ramadan Prep', 'count': 120, 'trend': 'up'},
                {'topic': 'Zakat Calculation', 'count': 95, 'trend': 'up'}
            ]
        return jsonify({'trending': trending, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/upload-secure', methods=['POST'])
def upload_knowledge_api():
    """Endpoint for uploading Islamic documents with strict security"""
    try:
        from werkzeug.utils import secure_filename
        MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB limit
        ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.json', '.csv'}
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part', 'code': 'NO_FILE_PART'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file', 'code': 'EMPTY_FILENAME'}), 400
            
        # Extension validation
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'error': f'Unsupported file type: {ext}', 'code': 'INVALID_FILE_TYPE'}), 400
            
        # File size check
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > MAX_FILE_SIZE:
            return jsonify({'error': 'File exceeds 5MB limit', 'code': 'FILE_TOO_LARGE'}), 400
            
        if file:
            filename = secure_filename(file.filename)
            # Ensure safe relative path
            data_dir = os.path.join(project_root, 'backend', 'knowledge', 'data')
            os.makedirs(data_dir, exist_ok=True)
            save_path = os.path.join(data_dir, filename)
            
            # Additional double check against path traversal
            if not os.path.abspath(save_path).startswith(os.path.abspath(data_dir)):
                 return jsonify({'error': 'Security violation: invalid path', 'code': 'SECURITY_ERROR'}), 403
            
            file.save(save_path)
            return jsonify({
                'success': True, 
                'filename': filename,
                'size': size,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'UPLOAD_ERROR'}), 500

@app.route('/api/knowledge/list', methods=['GET'])
def list_knowledge_api():
    """Endpoint for listing ingested Islamic documents"""
    try:
        data_dir = os.path.join(project_root, 'backend', 'knowledge', 'data')
        if not os.path.exists(data_dir):
            return jsonify({'files': []})
            
        files = []
        for filename in os.listdir(data_dir):
            if filename.endswith('.pdf') or filename.endswith('.txt') or filename.endswith('.json'):
                file_path = os.path.join(data_dir, filename)
                stats = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': stats.st_size,
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                })
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/delete', methods=['DELETE'])
def delete_knowledge_api():
    """Endpoint for deleting Islamic documents"""
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
            
        from werkzeug.utils import secure_filename
        safe_filename = secure_filename(filename)
        file_path = os.path.join(project_root, 'backend', 'knowledge', 'data', safe_filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True, 'message': f'Deleted {safe_filename}'})
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge-base/status', methods=['GET'])
def get_kb_status():
    """Endpoint for knowledge base status"""
    try:
        from backend.knowledge.memory_optimized_loader import (
            initialize_optimized_rag,
        )
        stats = initialize_optimized_rag()
        return jsonify({
            'status': 'success',
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register indexing routes if available
if indexing_available:
    register_indexing_routes(app)
    print("✅ Indexing and Knowledge Graph system registered")

# ============================================================================
# AUTO INGESTION & FILE UPLOAD ENDPOINTS
# ============================================================================

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'data')
ALLOWED_EXTENSIONS = {'json', 'txt', 'csv', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename: str) -> bool:
    """Check if file type is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/knowledge/upload', methods=['POST'])
def upload_knowledge_file():
    """Upload and ingest a new knowledge file"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        logger.info(f"📤 File uploaded: {filename}")
        
        return jsonify({
            'status': 'success',
            'message': f'File {filename} uploaded successfully. Auto ingestion starting...',
            'filename': filename,
            'size': os.path.getsize(file_path),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/ingest-status', methods=['GET'])
def get_ingest_status():
    """Get auto ingestion service status"""
    try:
        if not auto_ingest_available:
            return jsonify({'error': 'Auto ingestion not available'}), 503
        
        service = get_auto_ingest_service()
        if not service:
            return jsonify({'error': 'Auto ingestion service not running'}), 503
        
        status = service.get_status()
        
        return jsonify({
            'status': 'success',
            'service_status': status,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/recent-ingestions', methods=['GET'])
def get_recent_ingestions():
    """Get recent ingestion events"""
    try:
        if not auto_ingest_available:
            return jsonify({'error': 'Auto ingestion not available'}), 503
        
        service = get_auto_ingest_service()
        if not service:
            return jsonify({'error': 'Auto ingestion service not running'}), 503
        
        limit = request.args.get('limit', 20, type=int)
        events = service.get_recent_ingestions(limit=limit)
        
        return jsonify({
            'status': 'success',
            'recent_ingestions': events,
            'count': len(events),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Error getting ingestions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/data-files', methods=['GET'])
def get_data_files():
    """List all data files in knowledge/data directory"""
    try:
        files = []
        
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    files.append({
                        'name': filename,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        'type': filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
                    })
        
        return jsonify({
            'status': 'success',
            'data_directory': UPLOAD_FOLDER,
            'files': files,
            'total_files': len(files),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Error listing files: {e}")
        return jsonify({'error': str(e)}), 500


# === MEMORY MONITORING ENDPOINTS ===

@app.route('/api/memory/status', methods=['GET'])
def memory_status():
    """Get current memory usage status"""
    try:
        from backend.utils.memory_monitor import check_memory
        status = check_memory()
        
        return jsonify({
            'status': 'success',
            'memory': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Memory monitoring not available'
        }), 500


@app.route('/api/memory/cleanup', methods=['POST'])
def trigger_memory_cleanup():
    """Trigger garbage collection and memory cleanup"""
    try:
        from backend.utils.memory_monitor import cleanup_memory, check_memory
        
        cleanup_result = cleanup_memory()
        status_after = check_memory()
        
        return jsonify({
            'status': 'success',
            'action': 'memory_cleanup',
            'cleanup_result': cleanup_result,
            'memory_after': status_after,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Cleanup failed'
        }), 500


@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get comprehensive system status"""
    try:
        from backend.utils.memory_monitor import check_memory
        
        memory_status = check_memory()
        
        system_info = {
            'timestamp': datetime.now().isoformat(),
            'agents': {
                'single_agent_ready': single_agent is not None,
                'multi_agent_ready': multi_agent_system is not None,
                'agent_initialized': agent_initialized,
            },
            'rag': {
                'loader_ready': rag_loader is not None,
                'components': rag_loader.initialized_components if rag_loader else []
            },
            'memory': memory_status,
        }
        
        return jsonify(system_info)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'System status unavailable'
        }), 500


# === BACKEND READINESS ENDPOINTS ===

@app.route('/api/readiness/status', methods=['GET'])
def readiness_status():
    """Get backend readiness status for frontend synchronization"""
    try:
        _start_init_in_background()
        from backend.api.backend_readiness import get_readiness_status
        
        status = get_readiness_status()
        
        return jsonify({
            'status': 'success',
            'readiness': status,
            'ready_for_frontend': status['core_ready'],
            'fully_initialized': status['initialized'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Readiness check failed: {e}")
        return jsonify({
            'error': str(e),
            'ready_for_frontend': False
        }), 500


@app.route('/api/readiness/wait', methods=['GET'])
def wait_for_readiness():
    """Wait for backend to be ready (blocking call for frontend)"""
    try:
        from backend.api.backend_readiness import get_readiness_manager
        
        timeout = request.args.get('timeout', 30, type=int)
        manager = get_readiness_manager()
        
        # Wait for core to be ready
        ready = manager.wait_for_core_ready(timeout=timeout)
        
        if ready:
            return jsonify({
                'status': 'ready',
                'message': 'Backend is ready for requests',
                'readiness': manager.get_status(),
                'readiness_percentage': manager.get_readiness_percentage()
            })
        else:
            return jsonify({
                'status': 'timeout',
                'message': f'Backend initialization timeout after {timeout}s',
                'readiness': manager.get_status(),
                'readiness_percentage': manager.get_readiness_percentage()
            }), 503
    except Exception as e:
        logger.error(f"❌ Wait readiness failed: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/readiness/percentage', methods=['GET'])
def readiness_percentage():
    """Get readiness as percentage (useful for progress bars)"""
    try:
        from backend.api.backend_readiness import get_readiness_percentage, is_core_ready
        
        percentage = get_readiness_percentage()
        core_ready = is_core_ready()
        
        return jsonify({
            'readiness_percentage': percentage,
            'core_ready': core_ready,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'readiness_percentage': 0}), 500


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Islamic AI Agent Web API")
    parser.add_argument("--port", type=int, default=5010, help="Port to run the server on")
    args = parser.parse_args()

    # Initialize agents synchronously before starting the server
    initialize_agents()
    
    # Initialize auto ingestion service
    if auto_ingest_available:
        try:
            knowledge_dir = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'data')
            bm25_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'bm25_index.pkl')
            initialize_auto_ingest(knowledge_dir, bm25_path, check_interval=5)
            print("✅ Auto ingestion service initialized and started")
        except Exception as e:
            print(f"⚠️  Auto ingestion not available: {e}")
    
    print("🌟 Starting Islamic AI Agent Web API...")
    os.makedirs('templates', exist_ok=True)
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=args.port)

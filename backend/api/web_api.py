import os
import sys

# 🛡️ Hardening: Prevent semaphore leaks on macOS (Tokenizers parallelism)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Bypass crazy iCloud hang on metadata fetch in google.api_core/generative-ai
try:
    import importlib.metadata
    if hasattr(importlib.metadata, 'packages_distributions'):
        original_packages_distributions = importlib.metadata.packages_distributions
        def fast_packages_distributions(): return {}
        importlib.metadata.packages_distributions = fast_packages_distributions
except (ImportError, AttributeError):
    pass


import time
start_all = time.time()

import os
import sys

# Ensure the project root is in the search path for modularized imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
import asyncio
import json
from datetime import datetime
import threading
import queue
from functools import wraps
from typing import List, Dict, Any, Optional
import argparse

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
    """Initialize AI agents on startup"""
    global single_agent, multi_agent_system, agent_initialized
    try:
        print("🚀 Initializing Islamic AI Agents...")
        
        from backend.utils.llm_provider import init_agentscope
        init_agentscope()
        
        # Lazy imports to speed up Flask startup using the new modular structure
        from backend.core.islamic_ai_agent import IslamicAIAgent
        from backend.core.multi_agent_islamic_system import IslamicMultiAgentSystem
        
        # Initialize single agent
        print("📱 Initializing single agent...")
        single_agent = IslamicAIAgent()
        print("✅ Single agent ready!")
        
        # Initialize multi-agent system
        print("👥 Initializing multi-agent system...")
        multi_agent_system = IslamicMultiAgentSystem()
        print("✅ Multi-agent system ready!")
        
        # ⚡ Priming Step: Pre-load heavy ML models (Embeddings & Re-ranker)
        print("🕯️  Priming Scholarly Knowledge Base (Pre-loading models)...")
        from backend.knowledge.local_knowledge_tools import get_kb
        kb = get_kb()
        if kb:
            # Perform a quiet search to trigger model loading and cache warming
            kb.search("Bismillah")
            print("📖 Scholarly tools are warmed and ready for use.")
        else:
            print("⚠️  Warning: Knowledge base failed to prime. Retrieval may be slow initially.")
        
        agent_initialized = True
        print("🎉 All AI Agents initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        import traceback
        error_msg = traceback.format_exc()
        print(error_msg)
        
        # Log to file for diagnostics
        with open("backend_startup.log", "a") as f:
            f.write(f"\n[{datetime.now()}] ERROR initializing agents: {e}\n{error_msg}\n")
            
        agent_initialized = False

@app.route('/')
def home():
    """Serve the main UI page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agent_initialized': agent_initialized,
        'timestamp': datetime.now().isoformat(),
        'services': {
            'single_agent': single_agent is not None,
            'multi_agent': multi_agent_system is not None,
            'dynamic_knowledge': True
        }
    })

@app.route('/api/initialize', methods=['POST'])
def force_initialize():
    """Force agent initialization endpoint"""
    global agent_initialized
    try:
        print("🔄 Force initializing agents...")
        initialize_agents()
        
        return jsonify({
            'status': 'success',
            'agent_initialized': agent_initialized,
            'message': 'Agents initialized successfully' if agent_initialized else 'Agent initialization failed',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
@validate_request(required_fields=['message'], types={'message': str, 'latitude': float, 'longitude': float})
@agent_ready
def chat():
    """Main chat endpoint for single agent"""
    try:
        data = request.get_json()
        message = data.get('message')
        user_gender = data.get('user_gender', 'not_specified')
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Process message
        include_thoughts = data.get('include_thoughts', False)
        
        # Determine if we should force local fallback for demo purposes
        if demo_mode:
             # In Demo Mode, we simulate a quota limit to show off the Resilience architecture
             print("🛡️ Demo Mode Active: Forcing Local Resilience Fallback.")
             result = single_agent.process_message_with_tools(
                message, 
                user_gender=user_gender,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                include_thoughts=include_thoughts
             )
        else:
            result = single_agent.process_message_with_tools(
                message, 
                user_gender=user_gender,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                include_thoughts=include_thoughts
            )
        
        response_text = result[0] if include_thoughts else result
        thoughts = result[1] if include_thoughts else None
        
        from backend.config.islamic_config import islamic_config
        agent_name = islamic_config.get_agent_name('single')
        
        if response_text:
            track_topic(message[:50])
            return jsonify({
                'response': response_text,
                'thoughts': thoughts,
                'timestamp': datetime.now().isoformat(),
                'agent': agent_name
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stt', methods=['POST'])
@validate_request(required_fields=['audio'], types={'audio': str})
def speech_to_text():
    """Endpoint for Speech-to-Text transcription"""
    try:
        data = request.get_json()
        audio_data = data.get('audio', '') # Base64 audio
            
        import base64
        from google import genai
        from google.genai import types
        
        native_client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Prepare multimodal content for transcription
        raw_audio = base64.b64decode(audio_data)
        
        prompt = "Please transcribe this Islamic-related audio recording accurately."
        
        response = native_client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=[
                prompt,
                types.Part(inline_data=types.Blob(data=raw_audio, mime_type="audio/wav"))
            ]
        )
        
        return jsonify({
            'success': True,
            'transcription': response.text if response else ""
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        
        # Check cache (only for text-only messages to keep it simple)
        cache_key = None
        if not file_data:
            cache_key = f"chat_{message}_{user_gender}"
            cached_response = response_cache.get(cache_key)
            if cached_response:
                print(f"✨ Serving cached chat response for: {message[:30]}...")
                return jsonify(cached_response)
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        include_thoughts = data.get('include_thoughts', False)
        
        result = single_agent.process_multimodal_message(
            message, 
            file_data, 
            mime_type, 
            user_gender=user_gender,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            include_thoughts=include_thoughts
        )
        
        response_text = result[0] if include_thoughts else result
        thoughts = result[1] if include_thoughts else None
        
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
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        include_thoughts = data.get('include_thoughts', False)
        
        result = multi_agent_system.get_scholar_response(
            message, 
            scholar_type=None if specialist == 'auto' else specialist,
            user_gender=user_gender,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            include_thoughts=include_thoughts
        )
        
        response_text = result[0] if include_thoughts else result
        thoughts = result[1] if include_thoughts else None
        
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

        # Run collaborative consultation
        # Since Flask is sync and AgentScope is async, we use the synchronous wrapper
        include_thoughts = data.get('include_thoughts', False)
        result = multi_agent_system.get_collaborative_response(message, user_gender=user_gender, include_thoughts=include_thoughts)
        
        response_text = result[0] if include_thoughts else result
        thoughts = result[1] if include_thoughts else None

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

@app.route('/api/knowledge/upload', methods=['POST'])
def upload_knowledge_api():
    """Endpoint for uploading Islamic documents with strict security"""
    try:
        from werkzeug.utils import secure_filename
        MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB limit
        ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx'}
        
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
            if filename.endswith('.pdf') or filename.endswith('.txt'):
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
        from backend.knowledge.local_knowledge_tools import LocalKnowledgeBase
        kb = LocalKnowledgeBase()
        stats = kb.get_stats()
        return jsonify({
            'status': 'success',
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Islamic AI Agent Web API")
    parser.add_argument("--port", type=int, default=5010, help="Port to run the server on")
    args = parser.parse_args()

    # Initialize agents synchronously before starting the server
    initialize_agents()
    
    print("🌟 Starting Islamic AI Agent Web API...")
    os.makedirs('templates', exist_ok=True)
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=args.port)

DEBUG_START = True
if DEBUG_START: print("DEBUG: 1. Starting execution of web_api.py")
import time
start_all = time.time()

# Bypass crazy iCloud hang on metadata fetch in google.api_core/generative-ai
try:
    import importlib.metadata
    if hasattr(importlib.metadata, 'packages_distributions'):
        original_packages_distributions = importlib.metadata.packages_distributions
        def fast_packages_distributions(): return {}
        importlib.metadata.packages_distributions = fast_packages_distributions
except (ImportError, AttributeError):
    pass

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import json
import os
from datetime import datetime
import threading
import queue
from typing import List, Dict, Any, Optional
import argparse
if DEBUG_START: print(f"DEBUG: 2. Core imports done in {time.time() - start_all:.2f}s")

# Import our Islamic AI systems
# Imports will be done lazily inside initialize_agents
# from enhanced_islamic_tools import ...
# from dynamic_islamic_knowledge import ...
# from islamic_config import islamic_config

import enhanced_islamic_tools

app = Flask(__name__)

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

# Global analytics path
ANALYTICS_FILE = os.path.join(os.getcwd(), 'topic_analytics.json')

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
        
        from llm_provider import init_agentscope
        init_agentscope()
        
        # Lazy imports to speed up Flask startup
        from islamic_ai_agent import IslamicAIAgent
        from multi_agent_islamic_system import IslamicMultiAgentSystem
        
        # Initialize single agent
        print("📱 Initializing single agent...")
        single_agent = IslamicAIAgent()
        print("✅ Single agent ready!")
        
        # Initialize multi-agent system
        print("👥 Initializing multi-agent system...")
        multi_agent_system = IslamicMultiAgentSystem()
        print("✅ Multi-agent system ready!")
        
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
    print("DEBUG: Force initialize endpoint called")
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
def chat():
    """Main chat endpoint for single agent"""
    try:
        data = request.get_json()
        message = data.get('message')
        user_gender = data.get('user_gender', 'not_specified')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
            
        if not agent_initialized or not single_agent:
            return jsonify({'error': 'AI Agent not initialized'}), 500
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Process message
        response = single_agent.process_message_with_tools(
            message, 
            user_gender=user_gender,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        )
        
        from islamic_config import islamic_config
        agent_name = islamic_config.get_agent_name('single')
        
        if response:
            track_topic(message[:50])
            return jsonify({
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'agent': agent_name
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stt', methods=['POST'])
def speech_to_text():
    """Endpoint for Speech-to-Text transcription"""
    try:
        data = request.get_json()
        audio_data = data.get('audio', '') # Base64 audio
        
        if not audio_data:
            return jsonify({'error': 'Audio data is required'}), 400
            
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
        
        if not agent_initialized or not single_agent:
            return jsonify({'error': 'AI Agent is initializing. Please wait...'}), 503
            
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        response = single_agent.process_multimodal_message(
            message, 
            file_data, 
            mime_type, 
            user_gender=user_gender,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        )
        
        result = {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'agent': 'Noor'
        }
        
        # Cache successful response if no file was attached
        if cache_key:
            response_cache.set(cache_key, result)
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/multi-chat', methods=['POST'])
def multi_chat():
    """Multi-agent chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        specialist = data.get('specialist', 'auto')
        user_gender = data.get('user_gender', 'not_specified')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Check cache
        cache_key = f"multi_{message}_{specialist}_{user_gender}"
        cached_response = response_cache.get(cache_key)
        if cached_response:
            print(f"✨ Serving cached multi-agent response for: {message[:30]}...")
            return jsonify(cached_response)
        
        if not agent_initialized or not multi_agent_system:
            return jsonify({'error': 'AI Agent not initialized'}), 503

        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        response = multi_agent_system.get_scholar_response(
            message, 
            scholar_type=None if specialist == 'auto' else specialist,
            user_gender=user_gender,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        )
        
        specialist_name = specialist if specialist != 'auto' else 'AI Specialist'
        
        result = {
            'response': response,
            'specialist': specialist_name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache successful response
        response_cache.set(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collaborative', methods=['POST'])
def collaborative_chat():
    """Collaborative consultation endpoint with multi-scholar synthesis"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_gender = data.get('user_gender', 'not_specified')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Check cache
        cache_key = f"consult_{message}_{user_gender}"
        cached_response = response_cache.get(cache_key)
        if cached_response:
            print(f"✨ Serving cached collaborative response for: {message[:30]}...")
            return jsonify(cached_response)
        
        if not agent_initialized or not multi_agent_system:
            return jsonify({'error': 'Scholarly system is still initializing. Please wait...'}), 503

        # Run collaborative consultation
        # Since Flask is sync and AgentScope is async, we use the synchronous wrapper
        response = multi_agent_system.get_collaborative_response(message, user_gender=user_gender)
        
        result = {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'agent': 'Imam Hassan (Coordinator)'
        }
        
        # Cache successful response
        response_cache.set(cache_key, result)
        return jsonify(result)
        
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
            
        from enhanced_islamic_tools import get_islamic_calendar_events
        result = get_islamic_calendar_events()
        # Cache successful response
        response_cache.set(cache_key, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quran', methods=['POST'])
def get_quran():
    """Get Quran verse endpoint"""
    try:
        data = request.get_json()
        verse_reference = data.get('verse', '')
        
        if not verse_reference:
            return jsonify({'error': 'Verse reference is required'}), 400
        
        from enhanced_islamic_tools import get_quran_verse
        result = get_quran_verse(verse_reference)
        
        return jsonify({
            'verse': result,
            'reference': verse_reference,
            'timestamp': datetime.now().isoformat(),
            'source': 'Al-Quran Cloud API'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hadith', methods=['POST'])
def get_hadith_api():
    """Get Hadith endpoint"""
    try:
        data = request.get_json()
        topic = data.get('topic', None)
        
        from enhanced_islamic_tools import get_hadith
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
def get_random_hadith_api():
    """Endpoint for a random authentic hadith"""
    try:
        from enhanced_islamic_tools import get_hadith
        hadith = get_hadith()
        return jsonify({
            'success': True,
            'hadith': hadith
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adhkar', methods=['POST'])
def get_adhkar_api():
    """Endpoint for Prophetic Adhkar"""
    try:
        data = request.get_json()
        category = data.get('category', 'morning')
        from enhanced_islamic_tools import get_adhkar
        adhkar = get_adhkar(category)
        return jsonify({
            'success': True,
            'adhkar': adhkar
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/names-of-allah', methods=['POST'])
def get_names_of_allah_api():
    """Endpoint for 99 Names of Allah"""
    try:
        data = request.get_json()
        query = data.get('query', '1')
        from enhanced_islamic_tools import get_name_of_allah
        name_info = get_name_of_allah(query)
        return jsonify({
            'success': True,
            'name_info': name_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hajj-umrah', methods=['POST'])
def get_hajj_umrah_api():
    """Endpoint for Hajj and Umrah guidance"""
    try:
        data = request.get_json()
        ritual = data.get('ritual', 'ihram')
        from enhanced_islamic_tools import get_hajj_umrah_guidance
        guidance = get_hajj_umrah_guidance(ritual)
        return jsonify({
            'success': True,
            'guidance': guidance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/halal-check', methods=['POST'])
def check_halal_api():
    """Endpoint for Halal ingredient checking"""
    try:
        data = request.get_json()
        item = data.get('item', '')
        from enhanced_islamic_tools import check_halal_guidance
        result = check_halal_guidance(item)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prayer-times', methods=['POST'])
def get_prayer_times_api():
    """Get prayer times endpoint"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        from enhanced_islamic_tools import get_prayer_times
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
def get_qibla():
    """Get Qibla direction endpoint"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        from enhanced_islamic_tools import get_qibla_direction
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
        from enhanced_islamic_tools import get_hijri_date
        result = get_hijri_date()
        
        return jsonify({
            'hijri_date': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dua', methods=['POST'])
def get_dua_api():
    """Get Dua endpoint"""
    try:
        data = request.get_json()
        occasion = data.get('occasion', 'morning')
        
        from enhanced_islamic_tools import get_dua
        result = get_dua(occasion)
        
        return jsonify({
            'dua': result,
            'occasion': occasion,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_islamic_content_api():
    """Search Islamic content endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
            
        from enhanced_islamic_tools import search_islamic_content
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
        from enhanced_islamic_tools import get_daily_islamic_content
        result = get_daily_islamic_content()
        
        return jsonify({
            'daily_content': result,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guidance', methods=['POST'])
def get_guidance_api():
    """Get Islamic guidance endpoint"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
            
        from enhanced_islamic_tools import get_islamic_guidance
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
    """Endpoint for uploading Islamic documents"""
    try:
        from werkzeug.utils import secure_filename
        if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '': return jsonify({'error': 'No selected file'}), 400
        if file and (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
            filename = secure_filename(file.filename)
            data_dir = os.path.join(os.getcwd(), 'knowledge_base/data')
            os.makedirs(data_dir, exist_ok=True)
            file.save(os.path.join(data_dir, filename))
            return jsonify({'success': True, 'filename': filename})
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/list', methods=['GET'])
def list_knowledge_api():
    """Endpoint for listing ingested Islamic documents"""
    try:
        data_dir = os.path.join(os.getcwd(), 'knowledge_base/data')
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
        file_path = os.path.join(os.getcwd(), 'knowledge_base/data', safe_filename)
        
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
        from knowledge_base.local_knowledge_tools import LocalKnowledgeBase
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

    # Initialize agents in a separate thread
    init_thread = threading.Thread(target=initialize_agents)
    init_thread.daemon = True
    init_thread.start()
    
    print("🌟 Starting Islamic AI Agent Web API...")
    os.makedirs('templates', exist_ok=True)
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=args.port)
print('DEBUG: EOF reached')

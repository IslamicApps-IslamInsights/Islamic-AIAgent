"""
Web API Backend for Islamic AI Agent
Provides REST API endpoints for the AgentScope Islamic AI system
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import json
import os
from datetime import datetime
import threading
import queue
import time
import argparse

# Import our Islamic AI systems
from islamic_ai_agent import IslamicAIAgent
from multi_agent_islamic_system import IslamicMultiAgentSystem
from enhanced_islamic_tools import (
    get_quran_verse, get_hadith, get_dua, get_prayer_times,
    get_qibla_direction, get_hijri_date, get_islamic_guidance,
    search_islamic_content, get_daily_islamic_content, get_surah_info,
    calculate_zakat, get_name_of_allah, get_adhkar,
    get_hajj_umrah_guidance, check_halal_guidance
)
from dynamic_islamic_knowledge import (
    get_dynamic_quran_verse, get_dynamic_hadith, search_islamic_knowledge,
    get_topic_guidance, DynamicIslamicKnowledge
)
from islamic_config import islamic_config
from knowledge_base.ingest_data import main as run_ingestion

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

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Global variables for AI agents
single_agent = None
multi_agent_system = None
agent_initialized = False

def initialize_agents():
    """Initialize AI agents on startup"""
    global single_agent, multi_agent_system, agent_initialized
    try:
        print("🚀 Initializing Islamic AI Agents...")
        
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
        traceback.print_exc()
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
        
        # For now, we'll use the tools directly since AgentScope conversation is complex
        # In a full implementation, you'd run the agent conversation asynchronously
        
        # Use the centralized agent-processing logic which includes local-first search
        response = single_agent.process_message_with_tools(message, user_gender=user_gender)
        
        # Get dynamic agent name from configuration
        agent_name = islamic_config.get_agent_name('single')
        
        if response:
            track_topic(message[:50]) # Track first 50 chars of query
            
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/multi-chat', methods=['POST'])
def multi_chat():
    """Multi-agent chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        specialist = data.get('specialist', 'auto')  # auto, quran, hadith, fiqh, spiritual
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not agent_initialized or not multi_agent_system:
            return jsonify({'error': 'AI Agent not initialized'}), 500

        user_gender = data.get('user_gender', 'not_specified')
        
        # Route to appropriate specialist or use auto-routing
        response = multi_agent_system.get_scholar_response(
            message, 
            scholar_type=None if specialist == 'auto' else specialist,
            user_gender=user_gender
        )
        
        # Extract name from the response or system
        specialist_name = specialist if specialist != 'auto' else 'AI Specialist'
        
        return jsonify({
            'response': response,
            'specialist': specialist_name,
            'timestamp': datetime.now().isoformat()
        })
        
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
        
        result = get_hadith(topic)
        
        return jsonify({
            'hadith': result,
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'source': 'Authentic Hadith Collections'
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
        
        result = get_prayer_times(float(latitude), float(longitude))
        
        return jsonify({
            'prayer_times': result,
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
        
        result = search_islamic_content(query)
        
        return jsonify({
            'search_results': result,
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'sources': ['Al-Quran Cloud API', 'Hadith APIs']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ingest', methods=['POST'])
def ingest_local_knowledge():
    """Trigger the local knowledge ingestion pipeline"""
    try:
        print("📥 Starting local knowledge ingestion...")
        # Run the ingestion main function
        run_ingestion()
        
        return jsonify({
            'status': 'success',
            'message': 'Local knowledge base updated successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/daily-content')
def get_daily_content_api():
    """Get daily Islamic content endpoint"""
    try:
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
        
        result = get_islamic_guidance(topic)
        
        return jsonify({
            'guidance': result,
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'sources': ['Quran', 'Hadith', 'Islamic Scholarship']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hadith/random', methods=['POST'])
def get_random_hadith_api():
    """Get random hadith endpoint"""
    try:
        result = get_hadith('random')
        
        return jsonify({
            'hadith': result,
            'timestamp': datetime.now().isoformat(),
            'source': 'Authentic Hadith Collections'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_message_with_tools(message):
    """Process message using appropriate tools with dynamic configuration"""
    message_lower = message.lower()
    
    # Get all keyword sets once
    quran_keywords = islamic_config.get_keywords('quran')
    hadith_keywords = islamic_config.get_keywords('hadith')
    prayer_keywords = islamic_config.get_keywords('prayer')
    qibla_keywords = islamic_config.get_keywords('qibla')
    dua_keywords = islamic_config.get_keywords('dua')
    date_keywords = islamic_config.get_keywords('date')
    daily_keywords = islamic_config.get_keywords('daily')
    guidance_keywords = islamic_config.get_keywords('guidance')
    
    # Quran-related queries
    if any(word in message_lower for word in quran_keywords):
        if 'search' in message_lower:
            search_term = extract_search_term(message, ['quran', 'verse', 'surah'])
            return search_islamic_content(search_term)
        else:
            verse_ref = extract_verse_reference(message)
            return get_quran_verse(verse_ref)
    
    # Hadith-related queries
    elif any(word in message_lower for word in hadith_keywords):
        topic = extract_topic(message)
        return get_hadith(topic)
    
    # Prayer-related queries
    elif any(word in message_lower for word in prayer_keywords):
        return islamic_config.get_response_template('location_required', service='prayer times')
    
    # Qibla queries
    elif any(word in message_lower for word in qibla_keywords):
        return islamic_config.get_response_template('location_required', service='Qibla direction')
    
    # Dua queries
    elif any(word in message_lower for word in dua_keywords):
        occasion = extract_occasion(message)
        return get_dua(occasion)
    
    # Date queries
    elif any(word in message_lower for word in date_keywords):
        return get_hijri_date()
    
    # Daily content
    elif any(word in message_lower for word in daily_keywords):
        return get_daily_islamic_content()
    
    # General guidance
    elif any(word in message_lower for word in guidance_keywords):
        topic = extract_topic(message)
        return get_islamic_guidance(topic)
    
    # Search functionality
    elif 'search' in message_lower:
        search_term = extract_search_term(message, ['search'])
        return search_islamic_content(search_term)
    
    # Default response - using dynamic template
    else:
        agent_name = islamic_config.get_agent_name('single')
        return islamic_config.get_response_template('welcome', agent_name=agent_name)

def extract_verse_reference(message):
    """Extract verse reference from message using dynamic configuration"""
    message_lower = message.lower()
    
    # Check dynamic surah mappings first
    for name, mapping in islamic_config.config['surah_mappings'].items():
        if name in message_lower:
            if 'verse' in mapping:
                return name  # Single verse like ayat-kursi
            else:
                return name  # Complete surah
    
    # Try to find number patterns like "2:255"
    import re
    pattern = r'\b(\d{1,3}):(\d{1,3})\b'
    match = re.search(pattern, message)
    if match:
        return f"{match.group(1)}:{match.group(2)}"
    
    # Check for surah numbers (complete surahs)
    surah_pattern = r'\bsurah\s+(\d{1,3})\b'
    surah_match = re.search(surah_pattern, message_lower)
    if surah_match:
        surah_num = int(surah_match.group(1))
        if surah_num == 1:
            return 'al-fatiha'
        elif surah_num == 112:
            return 'al-ikhlas'
        elif surah_num == 113:
            return 'al-falaq'
        elif surah_num == 114:
            return 'an-nas'
        else:
            return f"{surah_num}:1"  # First verse of the surah
    
    # Default to Al-Fatiha
    return 'al-fatiha'

def extract_topic(message):
    """Extract topic from message"""
    message_lower = message.lower()
    
    topics = ['kindness', 'patience', 'charity', 'prayer', 'family', 'forgiveness', 'knowledge']
    
    for topic in topics:
        if topic in message_lower:
            return topic
    
    return None

def extract_occasion(message):
    """Extract occasion for dua"""
    message_lower = message.lower()
    
    occasions = ['morning', 'evening', 'travel', 'eating', 'sleep']
    
    for occasion in occasions:
        if occasion in message_lower:
            return occasion
    
    return 'morning'

def extract_search_term(message, exclude_words):
    """Extract search term from message"""
    words = message.lower().split()
    filtered_words = [word for word in words if word not in exclude_words and len(word) > 2]
    return ' '.join(filtered_words[:3])  # Take first 3 meaningful words

def auto_route_message(message):
    """Auto-route message to appropriate specialist"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['quran', 'verse', 'surah', 'tafsir']):
        return 'Sheikh Abdullah (Quran)', process_message_with_tools(message)
    elif any(word in message_lower for word in ['hadith', 'prophet', 'sunnah']):
        return 'Sheikh Aisha (Hadith)', process_message_with_tools(message)
    elif any(word in message_lower for word in ['fiqh', 'law', 'ruling', 'halal', 'haram']):
        return 'Sheikh Omar (Fiqh)', process_message_with_tools(message)
    elif any(word in message_lower for word in ['dua', 'spiritual', 'heart', 'soul']):
        return 'Sheikh Fatima (Spiritual)', process_message_with_tools(message)
    else:
        return 'Imam Hassan (Coordinator)', process_message_with_tools(message)

def route_to_specialist(message, specialist):
    """Route to specific specialist"""
    specialist_map = {
        'quran': 'Sheikh Abdullah (Quran)',
        'hadith': 'Sheikh Aisha (Hadith)',
        'fiqh': 'Sheikh Omar (Fiqh)',
        'spiritual': 'Sheikh Fatima (Spiritual)'
    }
    
    specialist_name = specialist_map.get(specialist, 'Imam Hassan (Coordinator)')
    response = process_message_with_tools(message)
    
    return specialist_name, response

# ===== ADVANCED ISLAMIC AI FEATURES =====

@app.route('/api/quran/search', methods=['GET'])
def search_quran_api():
    """Advanced Quran search endpoint"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Use dynamic knowledge system
        knowledge_system = DynamicIslamicKnowledge()
        result = asyncio.run(knowledge_system.search_quran_verses(query))
        
        if result:
            return jsonify({
                'success': True,
                'response': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'response': f"📖 **Quran Search Results for '{query}':**\n\nNo specific verses found. Try searching for:\n• Surah names (Al-Fatiha, Yasin)\n• Topics (patience, charity, prayer)\n• Verse numbers (2:255, 36:1)\n\nFor comprehensive Quran study, visit authentic Islamic websites.",
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hadith/search', methods=['GET'])
def search_hadith_api():
    """Advanced Hadith search endpoint"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Use dynamic knowledge system
        knowledge_system = DynamicIslamicKnowledge()
        result = asyncio.run(knowledge_system.search_hadith_by_topic(query))
        
        if result:
            return jsonify({
                'success': True,
                'response': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'response': f"⭐ **Hadith Search Results for '{query}':**\n\nNo specific hadith found. Try searching for:\n• Topics (kindness, charity, prayer)\n• Narrators (Abu Huraira, Aisha)\n• Collections (Bukhari, Muslim)\n\nFor authentic hadith collections, consult Sahih Bukhari and Muslim.",
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/zakat/calculate', methods=['POST'])
def calculate_zakat_api():
    """Zakat calculator endpoint"""
    try:
        data = request.get_json()
        wealth_type = data.get('type', 'cash')
        amount = float(data.get('amount', 0))
        
        # Zakat calculation logic
        if wealth_type == 'cash':
            nisab = 5000  # Approximate USD nisab
            if amount >= nisab:
                zakat_amount = amount * 0.025  # 2.5%
                return jsonify({
                    'success': True,
                    'zakat_due': zakat_amount,
                    'nisab_met': True,
                    'response': f"💰 **Zakat Calculation:**\n\n**Wealth Amount:** ${amount:,.2f}\n**Zakat Rate:** 2.5%\n**Zakat Due:** ${zakat_amount:,.2f}\n\n✅ **Nisab Met:** Your wealth exceeds the nisab threshold.\n\n🎯 **Recipients:** Poor, needy, collectors, new Muslims, debtors, fi sabilillah, travelers.\n\n*May Allah accept your zakat and purify your wealth.*"
                })
            else:
                return jsonify({
                    'success': True,
                    'zakat_due': 0,
                    'nisab_met': False,
                    'response': f"💰 **Zakat Calculation:**\n\n**Wealth Amount:** ${amount:,.2f}\n**Nisab Threshold:** ${nisab:,.2f}\n\n❌ **No Zakat Due:** Your wealth is below the nisab threshold.\n\n💡 **Continue saving and may Allah bless your wealth.**"
                })
        
        return jsonify({'error': 'Invalid wealth type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hajj/guide', methods=['GET'])
def hajj_guide_api():
    """Hajj guide endpoint"""
    try:
        step = request.args.get('step', 'overview')
        
        guides = {
            'overview': "🕋 **Hajj - The Fifth Pillar:**\n\nHajj is the pilgrimage to Mecca, obligatory once in lifetime for able Muslims.\n\n📅 **When:** 8-12 Dhul Hijjah annually\n🌍 **Where:** Mecca, Saudi Arabia\n👥 **Who:** Adult Muslims who are physically and financially able\n\n**Essential Rituals:**\n1. Ihram - Sacred state\n2. Tawaf - Circling Kaaba\n3. Sa'i - Walking Safa-Marwah\n4. Wuquf - Standing at Arafat\n5. Muzdalifah - Night stay\n6. Jamarat - Stone throwing\n7. Sacrifice - Qurbani\n8. Halq/Taqsir - Hair cutting",
            'preparation': "📋 **Hajj Preparation Guide:**\n\n**Spiritual Preparation:**\n• Repent sincerely (Tawbah)\n• Settle debts and disputes\n• Seek forgiveness from others\n• Learn hajj rituals properly\n• Make dua for acceptance\n\n**Physical Preparation:**\n• Medical checkup\n• Required vaccinations\n• Physical fitness training\n• Comfortable walking shoes\n\n**Documentation:**\n• Valid passport\n• Hajj visa\n• Vaccination certificates\n• Travel insurance\n\n**What to Pack:**\n• Ihram clothing (men)\n• Modest clothing (women)\n• Prayer mat\n• Quran and dua books\n• Medications\n• Comfortable shoes",
            'rituals': "🤲 **Hajj Ritual Steps:**\n\n**Day 1 (8 Dhul Hijjah) - Tarwiyah:**\n• Enter Ihram state\n• Go to Mina\n• Pray Dhuhr, Asr, Maghrib, Isha\n• Stay overnight\n\n**Day 2 (9 Dhul Hijjah) - Arafat:**\n• Most important day\n• Stand at Arafat after Dhuhr\n• Make dua until sunset\n• Combined Dhuhr-Asr prayer\n\n**Day 3 (10 Dhul Hijjah) - Eid:**\n• Muzdalifah to Mina\n• Stone Jamarat al-Aqaba\n• Animal sacrifice (Qurbani)\n• Hair cutting (Halq/Taqsir)\n• Tawaf al-Ifadah\n• Sa'i (if not done in Umrah)\n\n**Days 4-5 (11-12 Dhul Hijjah):**\n• Stone all three Jamarat\n• Farewell Tawaf before leaving"
        }
        
        response_text = guides.get(step, guides['overview'])
        
        return jsonify({
            'success': True,
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/islamic-finance', methods=['GET'])
def islamic_finance_api():
    """Islamic finance guidance endpoint"""
    try:
        topic = request.args.get('topic', 'overview')
        
        finance_guides = {
            'overview': "💳 **Islamic Finance Principles:**\n\n**Core Principles:**\n• **No Riba (Interest)** - Prohibited in all forms\n• **No Gharar** - Excessive uncertainty avoided\n• **No Haram Activities** - Unlawful business prohibited\n• **Asset-backed Transactions** - Real economic activity\n• **Risk-sharing** - Profit and loss sharing\n\n**Halal Investment Sectors:**\n✅ Technology, Healthcare, Education, Halal Food, Real Estate\n\n**Haram Investment Sectors:**\n❌ Alcohol, Gambling, Pork, Conventional Banking, Adult Entertainment\n\n**Islamic Banking Products:**\n• Murabaha (Cost-plus financing)\n• Ijara (Islamic leasing)\n• Musharaka (Joint venture)\n• Mudaraba (Profit-sharing)\n• Sukuk (Islamic bonds)",
            'investment': "📊 **Halal Investment Guidelines:**\n\n**Screening Criteria:**\n• Total debt/Market cap < 33%\n• Interest income < 5% of total income\n• Haram revenue < 5% of total revenue\n• Cash + interest-bearing securities < 33%\n\n**Investment Options:**\n• Sharia-compliant mutual funds\n• Islamic REITs\n• Halal stock screening\n• Sukuk (Islamic bonds)\n• Gold and commodities\n• Real estate\n\n**Purification Process:**\n• Calculate haram income percentage\n• Donate equivalent amount to charity\n• Keep records for transparency\n\n**Recommended Platforms:**\n• Wahed Invest\n• Amanah Mutual Funds\n• Saturna Capital\n• Local Islamic banks",
            'banking': "🏦 **Islamic Banking Guide:**\n\n**Key Differences:**\n• No interest (Riba) charged or paid\n• Profit-sharing arrangements\n• Asset-backed financing\n• Ethical investment focus\n\n**Common Products:**\n• **Home Financing:** Murabaha, Ijara\n• **Business Financing:** Musharaka, Mudaraba\n• **Personal Financing:** Tawarruq\n• **Savings:** Profit-sharing accounts\n• **Insurance:** Takaful (cooperative insurance)\n\n**Major Islamic Banks:**\n• Dubai Islamic Bank\n• Al Rajhi Bank\n• Kuwait Finance House\n• Bank Islam Malaysia\n• Guidance Financial (US)\n\n**Before Choosing:**\n• Verify Sharia compliance\n• Check scholar endorsements\n• Compare profit rates\n• Understand terms clearly"
        }
        
        response_text = finance_guides.get(topic, finance_guides['overview'])
        
        return jsonify({
            'success': True,
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask_scholar', methods=['GET', 'POST', 'OPTIONS'])
def ask_scholar_api():
    """Ask Islamic scholar endpoint with CORS support"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
        
    try:
        if request.method == 'GET':
            data = request.args
        else:
            data = request.get_json() or {}
            
        question = data.get('question') or data.get('query', '')
        scholar_type = data.get('scholar_type', 'auto')
        
        if not question:
            return jsonify({
                'status': 'error',
                'message': 'Question is required',
                'timestamp': datetime.now().isoformat()
            }), 400
            
        # Initialize agents if not already done
        if not agent_initialized:
            initialize_agents()
            
        if not multi_agent_system:
            return jsonify({
                'status': 'error',
                'message': 'Scholar system not initialized',
                'timestamp': datetime.now().isoformat()
            }), 500
        specialist_responses = {
            'worship': "🕌 **Sheikh Abdullah (Worship Specialist):**\n\nThank you for your question about worship. Based on Quran and authentic Sunnah:\n\n",
            'fiqh': "⚖️ **Sheikh Omar (Fiqh Specialist):**\n\nRegarding your fiqh question, according to Islamic jurisprudence:\n\n",
            'spiritual': "💫 **Sheikh Fatima (Spiritual Guide):**\n\nFor spiritual guidance, Islam teaches us:\n\n",
            'general': "👨‍🏫 **Imam Hassan (General Guidance):**\n\nMay Allah bless you for seeking knowledge. Regarding your question:\n\n"
        }
        
        base_response = specialist_responses.get(category, specialist_responses['general'])
        
        # Add general Islamic guidance
        guidance = f"{base_response}This is a complex matter that requires detailed study of Islamic sources. I recommend:\n\n1. **Consult local scholars** who can provide personalized guidance\n2. **Study authentic sources** - Quran, Sahih Hadith, classical texts\n3. **Consider your circumstances** - Islam is practical and considers individual situations\n4. **Seek multiple opinions** from qualified scholars\n\n**Important Note:** For specific rulings, especially in personal matters, please consult qualified local scholars who can consider your full situation.\n\n*\"And whoever fears Allah - He will make for him a way out.\" (65:2)*"
        
        return jsonify({
            'success': True,
            'response': guidance,
            'scholar': category,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/guidance', methods=['POST'])
def ai_guidance_api():
    """AI-powered Islamic guidance endpoint"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        context = data.get('context', {})
        
        if not question:
            return jsonify({'error': 'Question required'}), 400
        
        # Use the enhanced AI system
        if agent_initialized and single_agent:
            # Process with AI agent
            response = single_agent.process_message(question)
            
            return jsonify({
                'success': True,
                'response': f"🤖 **AI Islamic Guidance:**\n\n{response}\n\n**AI Analysis:** This response is generated using Islamic knowledge base and AI reasoning. For definitive rulings, please consult qualified scholars.\n\n**Sources:** Quran, Authentic Hadith, Classical Islamic Texts\n\n*\"And say: My Lord, increase me in knowledge.\" (20:114)*",
                'ai_confidence': 'high',
                'sources': ['Quran', 'Hadith', 'Classical Texts'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Fallback response
            return jsonify({
                'success': True,
                'response': f"🤖 **AI Islamic Guidance:**\n\nThank you for your question: \"{question}\"\n\nThe AI system is currently initializing. Please try again in a moment, or use the specific Islamic tools available.\n\n**Available Resources:**\n• Quran search and verses\n• Authentic Hadith collections\n• Prayer times and Qibla\n• Islamic calendar and events\n• Zakat calculator\n• Hajj and Umrah guides\n\n*For immediate guidance, consult local Islamic scholars.*",
                'ai_confidence': 'low',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/allah-names', methods=['POST'])
def get_allah_names_api():
    """Endpoint for 99 Names of Allah"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        result = get_name_of_allah(query)
        return jsonify({'response': result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adhkar', methods=['POST'])
def get_adhkar_api():
    """Endpoint for Morning/Evening Adhkar"""
    try:
        data = request.get_json()
        category = data.get('category', 'morning')
        result = get_adhkar(category)
        return jsonify({'response': result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hajj-umrah', methods=['POST'])
def get_hajj_umrah_api():
    """Endpoint for Hajj & Umrah guidance"""
    try:
        data = request.get_json()
        ritual = data.get('ritual', 'ihram')
        result = get_hajj_umrah_guidance(ritual)
        return jsonify({'response': result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/halal-check', methods=['POST'])
def halal_check_api():
    """Endpoint for Halal ingredient checking"""
    try:
        data = request.get_json()
        item = data.get('item', '')
        result = check_halal_guidance(item)
        return jsonify({'response': result, 'timestamp': datetime.now().isoformat()})
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
                # Sort by frequency
                sorted_topics = sorted(data.items(), key=lambda x: x[1], reverse=True)[:5]
                for topic, count in sorted_topics:
                    trending.append({
                        'topic': topic if len(topic) < 30 else topic[:27] + "...",
                        'count': count,
                        'trend': 'up'
                    })
        
        # Fallback if no data
        if not trending:
            trending = [
                {'topic': 'Ramadan Prep', 'count': 120, 'trend': 'up'},
                {'topic': 'Zakat Calculation', 'count': 95, 'trend': 'up'},
                {'topic': 'Patience in Islam', 'count': 70, 'trend': 'stable'}
            ]
            
        return jsonify({'trending': trending, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/upload', methods=['POST'])
def upload_knowledge_api():
    """Endpoint for uploading Islamic documents to knowledge base"""
    try:
        from werkzeug.utils import secure_filename
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
            filename = secure_filename(file.filename)
            data_dir = os.path.join(os.getcwd(), 'knowledge_base/data')
            os.makedirs(data_dir, exist_ok=True)
            
            save_path = os.path.join(data_dir, filename)
            file.save(save_path)
            
            return jsonify({
                'success': True,
                'message': f'File {filename} uploaded successfully. Ready for ingestion.',
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type. Only PDF and TXT allowed.'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/ingest', methods=['POST'])
def ingest_knowledge_api():
    """Endpoint to trigger knowledge base ingestion"""
    try:
        from knowledge_base.ingest_data import main as run_ingest
        
        # Run ingestion in a separate thread to avoid blocking the API
        def trigger_ingest():
            print("📦 Starting background knowledge ingestion...")
            run_ingest()
            print("✅ Background knowledge ingestion completed.")
            
        thread = threading.Thread(target=trigger_ingest)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Ingestion process started in background. It will take a few moments to update the vector database.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/list', methods=['GET'])
def list_knowledge_api():
    """List all documents in the knowledge base"""
    try:
        data_dir = os.path.join(os.getcwd(), 'knowledge_base/data')
        if not os.path.exists(data_dir):
            return jsonify({'files': []})
            
        files = os.listdir(data_dir)
        return jsonify({
            'files': [f for f in files if f.endswith('.pdf') or f.endswith('.txt')]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Islamic AI Agent Web API")
    parser.add_argument("--port", type=int, default=5001, help="Port to run the server on")
    args = parser.parse_args()

    # Initialize agents in a separate thread to avoid blocking
    init_thread = threading.Thread(target=initialize_agents)
    init_thread.daemon = True
    init_thread.start()
    
    print("🌟 Starting Islamic AI Agent Web API...")
    print(f"🌐 Server will be available at: http://localhost:{args.port}")
    print("📱 UI will be accessible via web browser")
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=args.port)

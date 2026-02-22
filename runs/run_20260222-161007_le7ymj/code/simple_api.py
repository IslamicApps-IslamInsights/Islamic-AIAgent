"""
Enhanced Islamic AI Agent API with AgentScope Integration
Provides full AI agent capabilities with Islamic tools
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)

# Configure CORS for all origins during development
CORS(app, resources={
    r"/*": {
        "origins": [
            "*",  # Allow all origins in development
            "https://theislaminsights.com",
            "https://www.theislaminsights.com",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:*",
            "http://127.0.0.1:*",
            "file://*"  # Allow file protocol for local development
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "x-requested-with", "X-Requested-With"],
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

# Try to import AgentScope components
try:
    from islamic_ai_agent import IslamicAIAgent
    from multi_agent_islamic_system import IslamicMultiAgentSystem
    AGENTSCOPE_AVAILABLE = True
    print("✅ AgentScope components loaded successfully")
except ImportError as e:
    print(f"⚠️ AgentScope not available: {e}")
    AGENTSCOPE_AVAILABLE = False

# Try to import Gemini components
try:
    from gemini_islamic_agent import GeminiIslamicAgent
    GEMINI_AVAILABLE = True
    print("✅ Gemini Islamic Agent loaded successfully")
except ImportError as e:
    print(f"⚠️ Gemini not available: {e}")
    GEMINI_AVAILABLE = False

# Global AI agents
single_agent = None
multi_agent_system = None
gemini_agent = None
agents_initialized = False

def initialize_agents():
    """Initialize AI agents (AgentScope and Gemini) if available"""
    global single_agent, multi_agent_system, gemini_agent, agents_initialized
    
    agents_initialized = False  # Reset flag at start
    
    # Initialize Gemini agent as fallback first
    if GEMINI_AVAILABLE:
        try:
            print("🤖 Initializing Gemini Islamic AI Agent...")
            gemini_api_key = os.getenv('GOOGLE_API_KEY')
            if gemini_api_key and gemini_api_key != 'your_gemini_api_key_here':
                gemini_agent = GeminiIslamicAgent(api_key=gemini_api_key)
                print("✅ Gemini AI Agent ready!")
        except Exception as e:
            print(f"⚠️ Failed to initialize Gemini: {e}")
            gemini_agent = None
    
    # Try to initialize AgentScope agents
    if not AGENTSCOPE_AVAILABLE:
        print("⚠️ AgentScope not available, using fallback responses")
        return
    
    try:
        print("\n🚀 Initializing AgentScope Islamic AI Agents...")
        
        # Check if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️ No OpenAI API key found in environment variables")
            print("ℹ️ Set OPENAI_API_KEY in your .env file")
            return
        
        # Initialize single agent
        print("\n📱 Initializing single Islamic AI agent...")
        try:
            single_agent = IslamicAIAgent(api_key=api_key)
            print("✅ Single agent initialized successfully!")
            agents_initialized = True
        except Exception as e:
            print(f"❌ Error initializing single agent: {e}")
            single_agent = None
        
        # Initialize multi-agent system
        print("\n👥 Initializing multi-agent system...")
        try:
            multi_agent_system = IslamicMultiAgentSystem(api_key=api_key)
            print("✅ Multi-agent system initialized successfully!")
            agents_initialized = agents_initialized or True
        except Exception as e:
            print(f"⚠️ Error initializing multi-agent system: {e}")
            multi_agent_system = None
        
        if agents_initialized:
            print("\n🎉 AgentScope AI Agents initialized successfully!")
        else:
            print("\n⚠️ Could not initialize any AgentScope agents")
        
    except Exception as e:
        print(f"\n❌ Critical error in agent initialization: {e}")
        print("🔄 Falling back to available agents or basic responses")
        agents_initialized = False

@app.route('/')
def home():
    """API home page with available endpoints"""
    # Check if request is from browser (HTML) or API client (JSON)
    if request.headers.get('Accept', '').find('text/html') != -1:
        # Return HTML page for browser
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Islamic AI Agent API</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #16a085, #27ae60); color: white; }
                .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
                h1 { text-align: center; margin-bottom: 10px; font-size: 2.5em; }
                .subtitle { text-align: center; margin-bottom: 30px; opacity: 0.9; }
                .status { text-align: center; margin: 20px 0; }
                .status-badge { display: inline-block; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 20px; margin: 5px; }
                .endpoints { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; }
                .endpoint { margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; }
                .method { display: inline-block; padding: 2px 8px; background: #e74c3c; border-radius: 3px; font-size: 0.8em; margin-right: 10px; }
                .method.get { background: #3498db; }
                .method.post { background: #e74c3c; }
                .frontend-link { text-align: center; margin: 30px 0; }
                .frontend-link a { display: inline-block; padding: 15px 30px; background: #f39c12; color: white; text-decoration: none; border-radius: 25px; font-weight: bold; transition: all 0.3s; }
                .frontend-link a:hover { background: #e67e22; transform: translateY(-2px); }
                .footer { text-align: center; margin-top: 30px; opacity: 0.8; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🕌 Islamic AI Agent API</h1>
                <p class="subtitle">Enhanced Islamic AI with AgentScope Integration</p>
                
                <div class="status">
                    <div class="status-badge">✅ API Running</div>
                    <div class="status-badge">🤖 AgentScope: {{ 'Available' if agentscope_available else 'Not Available' }}</div>
                    <div class="status-badge">💎 Gemini: {{ 'Available' if gemini_available else 'Not Available' }}</div>
                    <div class="status-badge">🔧 Agents: {{ 'Initialized' if agents_initialized else 'Not Initialized' }}</div>
                </div>

                <div class="frontend-link">
                    <a href="http://localhost:3000" target="_blank">🚀 Open Islamic AI Assistant</a>
                </div>

                <div class="endpoints">
                    <h3>📡 Available API Endpoints</h3>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/api/health</strong> - Health check endpoint
                    </div>
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/api/chat</strong> - Send Islamic questions and get AI responses
                    </div>
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/api/scholar</strong> - Consult specialized Islamic scholars
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/api/quran/search</strong> - Search Quran verses
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/api/hadith/search</strong> - Search authentic Hadith
                    </div>
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/api/prayer-times</strong> - Get prayer times for location
                    </div>
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/api/qibla</strong> - Get Qibla direction
                    </div>
                </div>

                <div class="footer">
                    <p>🕌 May Allah bless this Islamic AI system and make it beneficial for Muslims worldwide</p>
                    <p><small>Last updated: {{ timestamp }}</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_template, 
            agentscope_available=AGENTSCOPE_AVAILABLE,
            gemini_available=GEMINI_AVAILABLE,
            agents_initialized=agents_initialized,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    else:
        # Return JSON for API clients
        return jsonify({
            'name': 'Islamic AI Agent API',
            'version': '2.0.0',
            'description': 'Enhanced Islamic AI Agent with AgentScope Integration',
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'features': {
                'agentscope_available': AGENTSCOPE_AVAILABLE,
                'gemini_available': GEMINI_AVAILABLE,
                'agents_initialized': agents_initialized
            },
            'endpoints': {
                'health': '/api/health',
                'chat': '/api/chat (POST)',
                'scholar': '/api/scholar (POST)',
                'quran_search': '/api/quran/search (GET)',
                'hadith_search': '/api/hadith/search (GET)',
                'prayer_times': '/api/prayer-times (POST)',
                'qibla': '/api/qibla (POST)'
            },
            'usage': {
                'chat': 'Send Islamic questions and get AI responses',
                'scholar': 'Consult specialized Islamic scholars',
                'frontend': 'http://localhost:3000'
            }
        })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Islamic AI Agent API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/scholar', methods=['POST'])
def scholar_consultation():
    """Scholar consultation endpoint with specialized Islamic scholars"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        scholar_type = data.get('scholar_type', None)  # Optional: specific scholar
        consultation_type = data.get('consultation_type', 'single')  # 'single' or 'collaborative'
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Try to use multi-agent system first
        if agents_initialized and multi_agent_system:
            try:
                if consultation_type == 'collaborative':
                    # Get collaborative response from multiple scholars
                    ai_response = multi_agent_system.get_collaborative_response(message)
                    agent_name = "Islamic Scholar Council (Collaborative)"
                else:
                    # Get response from specific scholar or auto-route
                    ai_response = multi_agent_system.get_scholar_response(message, scholar_type)
                    
                    # Determine which scholar responded
                    if scholar_type:
                        scholar_names = {
                            'quran_scholar': 'Sheikh Abdullah (Quran Specialist)',
                            'hadith_scholar': 'Sheikh Aisha (Hadith Expert)',
                            'fiqh_scholar': 'Sheikh Omar (Fiqh Scholar)',
                            'spiritual_guide': 'Sheikh Fatima (Spiritual Guide)',
                            'coordinator': 'Imam Hassan (Coordinator)'
                        }
                        agent_name = scholar_names.get(scholar_type, 'Islamic Scholar')
                    else:
                        # Auto-routed
                        determined_scholar = multi_agent_system.determine_specialist(message)
                        scholar_names = {
                            'quran_scholar': 'Sheikh Abdullah (Quran Specialist)',
                            'hadith_scholar': 'Sheikh Aisha (Hadith Expert)',
                            'fiqh_scholar': 'Sheikh Omar (Fiqh Scholar)',
                            'spiritual_guide': 'Sheikh Fatima (Spiritual Guide)',
                            'coordinator': 'Imam Hassan (Coordinator)'
                        }
                        agent_name = scholar_names.get(determined_scholar, 'Islamic Scholar')
                
                return jsonify({
                    'success': True,
                    'response': ai_response,
                    'agent': agent_name,
                    'scholar_type': scholar_type or multi_agent_system.determine_specialist(message),
                    'consultation_type': consultation_type,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Multi-agent system error: {e}")
                # Fall through to single agent fallback
        
        # Fallback to single agent if multi-agent fails
        if agents_initialized and single_agent:
            try:
                from agentscope.message import Msg
                import asyncio
                
                user_msg = Msg(name="user", content=f"[Scholar Consultation] {message}", role="user")
                response_msg = single_agent.agent(user_msg)
                
                if hasattr(response_msg, '__await__'):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response_msg = loop.run_until_complete(response_msg)
                    finally:
                        loop.close()
                
                if hasattr(response_msg, 'content'):
                    ai_response = response_msg.content
                else:
                    ai_response = str(response_msg)
                
                return jsonify({
                    'success': True,
                    'response': ai_response,
                    'agent': 'Noor (AgentScope Fallback)',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Single agent error: {e}")
        
        # Final fallback to Gemini
        if gemini_agent:
            try:
                print("🔄 Using Gemini AI for scholar consultation...")
                ai_response = gemini_agent.get_response(f"As an Islamic scholar, please provide guidance on: {message}")
                
                return jsonify({
                    'success': True,
                    'response': ai_response,
                    'agent': 'Noor (Gemini AI Scholar)',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Gemini error: {e}")
        
        # Ultimate fallback
        return jsonify({
            'success': False,
            'response': "I apologize, but our Islamic scholars are currently unavailable. Please try again later or consult your local Islamic authority.",
            'agent': 'System',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Scholar consultation error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with AgentScope integration"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        intent = data.get('intent', 'general')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Skip processing if this is a welcome message or empty
        if 'welcome' in message.lower() or not message:
            return jsonify({
                'success': True,
                'response': get_enhanced_response('welcome', 'greeting'),
                'agent': 'Noor (Welcome Bot)',
                'timestamp': datetime.now().isoformat()
            })
        
        # Try to use AgentScope AI agent first
        if agents_initialized and single_agent:
            try:
                print(f"\n📨 Received message: {message}")
                
                # Create a proper message for the agent
                from agentscope.message import Msg
                import asyncio
                
                # Create a more structured prompt with Islamic context
                prompt = f"""
                🌙 *Bismillah ar-Rahman ar-Raheem* 🌙
                
                🤲 *User's Question:*
                {message}
                
                As an Islamic scholar, please provide a detailed, authentic response based on the Quran and Sunnah. 
                
                🌟 Please include:
                - Relevant Quranic verses with references
                - Authentic Hadith with references
                - Scholarly opinions where applicable
                - Practical advice for daily life
                - Beautiful Islamic reminders
                
                Format your response with proper markdown formatting, emojis, and sections for better readability.
                """
                
                # Create the message with the appropriate parameters for AgentScope's Msg class
                user_msg = Msg(
                    name="user",
                    role="user",
                    content={
                        "text": prompt,
                        "intent": intent,
                        "language": "en",
                        "response_format": "markdown"
                    }
                )
                
                print(f"🤖 Processing with AgentScope...")
                
                # Process with the Islamic AI agent (async)
                try:
                    import asyncio
                    response_msg = asyncio.run(single_agent.agent(user_msg))
                    
                    # Get the response text and enhance it
                    if hasattr(response_msg, 'content'):
                        response = response_msg.content
                    else:
                        response = str(response_msg)
                except Exception as e:
                    print(f"❌ Error in AgentScope processing: {e}")
                    raise
                
                # Add beautiful Islamic styling if not already present
                if not response.startswith('🌙'):
                    response = f"""
                    <div style="font-family: 'Traditional Arabic', Arial, sans-serif; direction: rtl; text-align: right; line-height: 1.8;">
                        <div style="background-color: #f8f5e6; padding: 20px; border-right: 4px solid #1a5f7a; margin-bottom: 20px; border-radius: 5px;">
                            <p style="color: #1a5f7a; font-size: 1.2em; margin-bottom: 15px; text-align: center;">
                                بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
                            </p>
                            <div style="color: #333; font-size: 1.1em;">
                                {response}
                            </div>
                            <p style="text-align: left; color: #666; margin-top: 20px; font-style: italic;">
                                🤲 May Allah guide us all to the straight path. Ameen.
                            </p>
                        </div>
                    </div>
                    """.format(response=response)
                
                agent_name = "Noor (Islamic AI)"
                
            except Exception as e:
                print(f"❌ AgentScope error: {e}")
                use_agent_scope = False
        
        # Fallback to Gemini if AgentScope fails or not available
        if not agents_initialized or not single_agent or not use_agent_scope:
            print("🔄 Falling back to Gemini AI...")
            try:
                if gemini_agent:
                    # Enhanced prompt for Gemini
                    enhanced_prompt = f"""
                    🌙 *Bismillah ar-Rahman ar-Raheem* 🌙
                    
                    🤲 *User's Question:*
                    {message}
                    
                    As an Islamic scholar, please provide a detailed, authentic response based on the Quran and Sunnah. 
                    
                    🌟 Please include:
                    - Relevant Quranic verses with references (Surah:Verse)
                    - Authentic Hadith with references (e.g., Sahih Bukhari, Muslim)
                    - Scholarly opinions where applicable
                    - Practical advice for daily life
                    - Beautiful Islamic reminders
                    
                    Format your response with markdown formatting, emojis, and clear sections.
                    """
                    
                    # Try different method names for the Gemini agent
                    if hasattr(gemini_agent, 'generate_response'):
                        response = gemini_agent.generate_response(enhanced_prompt)
                    elif hasattr(gemini_agent, 'chat'):
                        response = gemini_agent.chat(enhanced_prompt)
                    elif hasattr(gemini_agent, 'get_response'):
                        response = gemini_agent.get_response(enhanced_prompt)
                    else:
                        # If no known method is found, use a default response
                        response = "I apologize, but I'm having trouble processing your request right now. Please try again later. May Allah make it easy for you. Ameen."
                    
                    # Add beautiful Islamic styling
                    response = f"""
                    <div style="font-family: 'Traditional Arabic', Arial, sans-serif; direction: rtl; text-align: right; line-height: 1.8;">
                        <div style="background-color: #f8f5e6; padding: 20px; border-right: 4px solid #1a5f7a; margin-bottom: 20px; border-radius: 5px;">
                            <p style="color: #1a5f7a; font-size: 1.2em; margin-bottom: 15px; text-align: center;">
                                بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
                            </p>
                            <div style="color: #333; font-size: 1.1em;">
                                {response}
                            </div>
                            <p style="text-align: left; color: #666; margin-top: 20px; font-style: italic;">
                                🤲 May Allah guide us all to the straight path. Ameen.
                            </p>
                        </div>
                    </div>
                    """.format(response=response)
                    
                    agent_name = "Noor (Gemini AI)"
                else:
                    response = """
                    <div style="font-family: Arial, sans-serif; color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; text-align: center;">
                        <p style="margin: 0;">
                            🤲 *Bismillah* - I'm currently experiencing technical difficulties. 
                            Please try again later or make dua for our team.
                        </p>
                    </div>
                    """
                    agent_name = "System"
            except Exception as e:
                print(f"❌ Gemini error: {e}")
                response = """
                <div style="font-family: Arial, sans-serif; color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; text-align: center;">
                    <p style="margin: 0;">
                        🤲 *SubhanAllah* - I apologize for the inconvenience. 
                        Please try again later. May Allah forgive our shortcomings. Ameen.
                    </p>
                </div>
                """
                agent_name = "System"
        
        return jsonify({
            'success': True,
            'response': response,
            'agent': agent_name,
            'agent': 'Basic Islamic Assistant',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_enhanced_response(message, intent):
    """Get enhanced response with better Islamic content"""
    message_lower = message.lower()
    
    if 'prayer' in message_lower:
        return "🕐 **Prayer Times & Guidance:**\n\nAssalamu Alaikum! For accurate prayer times, please enable location access.\n\n**Five Daily Prayers:**\n🌅 **Fajr** - Dawn prayer (before sunrise)\n☀️ **Dhuhr** - Midday prayer\n🌤️ **Asr** - Afternoon prayer\n🌅 **Maghrib** - Evening prayer (after sunset)\n🌙 **Isha** - Night prayer\n\n**Prayer Preparation:**\n• Perform Wudu (ablution)\n• Face Qibla direction\n• Make intention (Niyyah)\n\n*May Allah accept your prayers! 🤲*"
    
    elif 'quran' in message_lower:
        # Check for specific topics
        if 'patience' in message_lower or 'sabr' in message_lower:
            return "📖 **What the Quran Says About Patience (Sabr):**\n\nPatience (Sabr) is one of the most emphasized virtues in the Quran.\n\n**Key Verses:**\n\n**Surah Al-Baqarah (2:155-157):**\n\"وَلَنَبْلُوَنَّكُم بِشَيْءٍ مِّنَ الْخَوْفِ وَالْجُوعِ وَنَقْصٍ مِّنَ الْأَمْوَالِ وَالْأَنفُسِ وَالثَّمَرَاتِ ۗ وَبَشِّرِ الصَّابِرِينَ\"\n\n*\"And We will surely test you with something of fear and hunger and a loss of wealth and lives and fruits, but give good tidings to the patient.\"*\n\n**Surah Ali 'Imran (3:200):**\n\"يَا أَيُّهَا الَّذِينَ آمَنُوا اصْبِرُوا وَصَابِرُوا\"\n\n*\"O you who believe! Persevere in patience and constancy.\"*\n\n**Surah Az-Zumar (39:10):**\n\"إِنَّمَا يُوَفَّى الصَّابِرُونَ أَجْرَهُم بِغَيْرِ حِسَابٍ\"\n\n*\"Indeed, the patient will be given their reward without account.\"*\n\n**Types of Patience in Islam:**\n• **Patience in worship** - Consistency in prayers and acts of worship\n• **Patience in avoiding sins** - Restraining from what Allah has forbidden\n• **Patience in trials** - Enduring hardships with faith in Allah\n\n**Rewards for the Patient:**\n• Unlimited reward from Allah\n• Allah's companionship and support\n• Entry into Paradise\n• Leadership in faith\n\n*\"And Allah is with the patient.\" (2:249)*"
        
        elif 'charity' in message_lower or 'zakat' in message_lower:
            return "📖 **What the Quran Says About Charity:**\n\nCharity is repeatedly emphasized in the Quran as a fundamental duty.\n\n**Key Verses:**\n\n**Surah Al-Baqarah (2:261):**\n*\"The example of those who spend their wealth in the way of Allah is like a seed which grows seven spikes; in each spike is a hundred grains.\"*\n\n**Surah Al-Baqarah (2:274):**\n*\"Those who spend their wealth by night and day, secretly and publicly - they will have their reward with their Lord.\"*\n\n**Types of Charity:**\n• **Zakat** - Obligatory charity (2.5% annually)\n• **Sadaqah** - Voluntary charity\n• **Sadaqah Jariyah** - Continuous charity\n\n*\"And whatever you spend in good, it will be repaid to you in full.\" (2:272)*"
        
        elif 'prayer' in message_lower or 'salah' in message_lower:
            return "📖 **What the Quran Says About Prayer (Salah):**\n\nPrayer is the second pillar of Islam and mentioned throughout the Quran.\n\n**Key Verses:**\n\n**Surah Al-Baqarah (2:45):**\n*\"And seek help through patience and prayer, and indeed, it is difficult except for the humbly submissive [to Allah].\"*\n\n**Surah An-Nisa (4:103):**\n*\"Indeed, prayer has been decreed upon the believers a decree of specified times.\"*\n\n**Benefits of Prayer:**\n• Direct connection with Allah\n• Spiritual purification\n• Protection from evil\n• Peace and tranquility\n\n*\"And establish prayer. Indeed, prayer prohibits immorality and wrongdoing.\" (29:45)*"
        
        else:
            return "📖 **Quran - The Final Revelation:**\n\nThe Quran is Allah's final message to humanity, revealed to Prophet Muhammad (ﷺ).\n\n**Key Facts:**\n• 114 Surahs (chapters)\n• 6,236 Ayat (verses)\n• Revealed over 23 years\n• Preserved in original Arabic\n\n**Popular Verses:**\n• Ayat al-Kursi (2:255)\n• Surah Al-Fatiha (1:1-7)\n• Surah Al-Ikhlas (112:1-4)\n\n**For authentic verses and translations:**\n• Al-Quran Cloud API\n• Quran.com\n• Local Islamic center\n\n*\"And We have certainly made the Quran easy for remembrance.\" (54:17)*"
    
    elif 'hadith' in message_lower:
        return "⭐ **Authentic Hadith Collections:**\n\nHadith are the sayings and actions of Prophet Muhammad (ﷺ).\n\n**Major Collections (Kutub al-Sittah):**\n• **Sahih Bukhari** - Most authentic\n• **Sahih Muslim** - Second most authentic\n• **Sunan Abu Dawud** - Legal matters\n• **Jami' at-Tirmidhi** - Various topics\n• **Sunan an-Nasa'i** - Worship acts\n• **Sunan Ibn Majah** - Comprehensive\n\n**Famous Hadith:**\n*\"The believers in their mutual kindness, compassion, and sympathy are just one body - when a limb suffers, the whole body responds to it with wakefulness and fever.\"* - Sahih Bukhari\n\n*\"None of you truly believes until he loves for his brother what he loves for himself.\"* - Sahih Bukhari"
    
    elif 'dua' in message_lower:
        return "🤲 **Duas - Supplications to Allah:**\n\nDua is our direct connection with Allah (SWT).\n\n**Morning Dua:**\n\"أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ\"\n*Asbahna wa asbahal-mulku lillahi, walhamdu lillah*\n*\"We have reached morning and the kingdom belongs to Allah, and all praise is for Allah.\"*\n\n**Evening Dua:**\n\"أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ\"\n*Amsayna wa amsal-mulku lillahi, walhamdu lillah*\n*\"We have reached evening and the kingdom belongs to Allah, and all praise is for Allah.\"*\n\n**Best Times for Dua:**\n• Last third of the night\n• Between Maghrib and Isha\n• After obligatory prayers\n• While fasting"
    
    else:
        return f"🌟 **Islamic AI Assistant - Noor:**\n\nبِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n\nAssalamu Alaikum wa Rahmatullahi wa Barakatuh! 🕌\n\nThank you for your question: \"{message}\"\n\nI'm here to provide authentic Islamic guidance based on Quran and Sunnah. I can help with:\n\n📖 **Quran** - Verses, meanings, and tafsir\n⭐ **Hadith** - Authentic sayings of Prophet (ﷺ)\n🕐 **Prayer** - Times, guidance, and procedures\n🤲 **Duas** - Supplications for various occasions\n⚖️ **Fiqh** - Islamic jurisprudence and rulings\n🌙 **Islamic Calendar** - Hijri dates and events\n💰 **Zakat** - Charity calculations and guidance\n🕋 **Hajj & Umrah** - Pilgrimage guidance\n\n*For complex religious matters, please consult qualified Islamic scholars.*\n\nHow may I assist you in your Islamic journey today? 🌟\n\nMay Allah guide us all. Ameen! 🤲"

@app.route('/api/quran/search', methods=['GET'])
def search_quran():
    """Quran search endpoint"""
    try:
        query = request.args.get('q', '')
        
        response = f"📖 **Quran Search for '{query}':**\n\nSearching the Quran for authentic guidance...\n\nFor comprehensive Quran study with Arabic text, translations, and audio:\n• Visit Quran.com\n• Use Al-Quran Cloud API\n• Consult local Islamic scholars\n\n*\"And We have certainly made the Quran easy for remembrance.\" (54:17)*"
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hadith/search', methods=['GET'])
def search_hadith():
    """Hadith search endpoint"""
    try:
        query = request.args.get('q', '')
        
        response = f"⭐ **Hadith Search for '{query}':**\n\nSearching authentic hadith collections...\n\n**Major Collections:**\n• Sahih Bukhari - Most authentic\n• Sahih Muslim - Second most authentic\n• Sunan collections for detailed rulings\n\nFor specific hadith with full chains of narration, consult:\n• Sunnah.com\n• Local Islamic libraries\n• Qualified Islamic scholars"
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prayer-times', methods=['POST'])
def get_prayer_times():
    """Prayer times endpoint"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({
                'success': False,
                'response': "📍 **Location Required:**\n\nPlease enable location access for accurate prayer times.\n\nAlternatively, visit:\n• IslamicFinder.org\n• Your local mosque\n• Muslim Pro app"
            })
        
        # Try to get prayer times from Aladhan API
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            url = f"https://api.aladhan.com/v1/timings/{today}"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'method': 2
            }
            
            api_response = requests.get(url, params=params, timeout=10)
            if api_response.status_code == 200:
                data = api_response.json()
                timings = data['data']['timings']
                
                response = f"🕐 **Today's Prayer Times:**\n\n🌅 **Fajr**: {timings['Fajr']}\n☀️ **Dhuhr**: {timings['Dhuhr']}\n🌤️ **Asr**: {timings['Asr']}\n🌅 **Maghrib**: {timings['Maghrib']}\n🌙 **Isha**: {timings['Isha']}\n\n📍 **Location-based times** for your area\n\n💡 May Allah accept your prayers!"
                
                return jsonify({
                    'success': True,
                    'response': response,
                    'prayer_times': timings,
                    'timestamp': datetime.now().isoformat()
                })
        except:
            pass
        
        # Fallback response
        return jsonify({
            'success': False,
            'response': "🕐 **Prayer Times:**\n\nUnable to fetch exact times right now. Please check:\n• IslamicFinder.org\n• Local mosque\n• Muslim Pro app\n\nGeneral prayer times:\n• Fajr: Before sunrise\n• Dhuhr: After midday\n• Asr: Afternoon\n• Maghrib: After sunset\n• Isha: After twilight"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    PORT = 5010  # Changed to port 5010 to avoid conflicts
    print("🌟 Starting Enhanced Islamic AI Agent API...")
    print(f"🌐 Server available at: http://localhost:{PORT}")
    print(f"📱 Health check: http://localhost:{PORT}/api/health")
    
    # Initialize AgentScope agents
    initialize_agents()
    
    print("\n🎉 Islamic AI Agent API is ready!")
    print("✨ Features available:")
    if agents_initialized:
        print("  🤖 Full AgentScope AI Agent (Noor)")
        print("  👥 Multi-Agent Islamic Consultation")
        print("  🧠 Intelligent Islamic Responses")
    
    if gemini_agent:
        print("  🤖 Gemini AI Fallback (Noor)")
    
    print("  🔄 Smart AI Fallback System")
    print("  🕐 Prayer Times & Qibla")
    print("  📖 Quran & Hadith Search")
    print("  💰 Zakat Calculator")
    print("  🕋 Hajj Guide")
    print("  💳 Islamic Finance")
    print("  🎯 Multi-tier AI System:")
    print("     1️⃣ AgentScope (Primary)")
    print("     2️⃣ Gemini AI (Fallback)")
    print("     3️⃣ Enhanced Responses (Final Fallback)")
    
    # Run the app with use_reloader=False to avoid multiple instances
    app.run(host='0.0.0.0', port=PORT, debug=True, use_reloader=False)

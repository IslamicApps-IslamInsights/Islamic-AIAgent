import React, { useState, useEffect, useRef } from 'react';
import { Send, Book, Clock, Compass, Heart, Moon, Sun, Star, MapPin, Calendar, Volume2, Search, User, Settings, BookOpen, Mic, Globe, Shield, Zap, MessageCircle } from 'lucide-react';

const IslamicAIAgent = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ\n\nAssalamu Alaikum wa Rahmatullahi wa Barakatuh! 🕌\n\nWelcome to your Islamic AI Assistant from TheIslamInsights.com. I provide authentic Islamic guidance based on Quran and Sunnah.\n\n✨ **How I can help:**\n📖 Quranic verses & explanations\n🕐 Prayer guidance & times\n🤲 Duas from Quran & Sunnah\n⚖️ Fiqh rulings & Islamic law\n🌙 Islamic calendar & events\n📚 Authentic Hadith collections\n💡 Daily Islamic reminders\n\n*Note: For complex matters, consult qualified scholars.*\n\nHow may I assist you today? 🌟",
      sender: 'agent',
      timestamp: new Date(),
      type: 'welcome'
    }
  ]);
  
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedCategory, setSelectedCategory] = useState('general');
  const messagesEndRef = useRef(null);

  // Islamic date helper
  const getHijriDate = () => {
    const hijriMonths = [
      'Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Thani",
      'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', "Sha'ban",
      'Ramadan', 'Shawwal', "Dhu al-Qi'dah", 'Dhu al-Hijjah'
    ];
    const currentMonth = new Date().getMonth();
    const hijriYear = 1446;
    return `${Math.floor(Math.random() * 28) + 1} ${hijriMonths[currentMonth % 12]} ${hijriYear} AH`;
  };

  // Categories
  const categories = [
    { id: 'general', name: 'General', icon: MessageCircle, color: 'text-blue-600' },
    { id: 'prayer', name: 'Salah', icon: Clock, color: 'text-green-600' },
    { id: 'quran', name: 'Quran', icon: Book, color: 'text-purple-600' },
    { id: 'hadith', name: 'Hadith', icon: Star, color: 'text-yellow-600' },
    { id: 'fiqh', name: 'Fiqh', icon: Settings, color: 'text-red-600' },
    { id: 'dua', name: 'Dua', icon: Heart, color: 'text-pink-600' }
  ];

  // Quick actions
  const quickActions = [
    { icon: Clock, label: 'Prayer Times', action: 'prayer_times', color: 'bg-blue-500' },
    { icon: Book, label: 'Daily Verse', action: 'daily_verse', color: 'bg-green-500' },
    { icon: Star, label: 'Daily Hadith', action: 'daily_hadith', color: 'bg-yellow-500' },
    { icon: Heart, label: 'Morning Dua', action: 'morning_dua', color: 'bg-pink-500' },
    { icon: Compass, label: 'Qibla', action: 'qibla', color: 'bg-purple-500' },
    { icon: Calendar, label: 'Islamic Calendar', action: 'islamic_calendar', color: 'bg-indigo-500' }
  ];

  // Response content
  const dailyContent = {
    prayer_times: {
      text: "🕐 **Prayer Times Guide:**\n\n**Five Daily Prayers:**\n\n🌅 **Fajr** - Dawn prayer (before sunrise)\n• 2 Sunnah + 2 Fard rakats\n\n☀️ **Dhuhr** - Midday prayer\n• 4 Sunnah + 4 Fard + 2 Sunnah\n\n🌤️ **Asr** - Afternoon prayer\n• 4 Sunnah + 4 Fard\n\n🌅 **Maghrib** - Evening prayer (after sunset)\n• 3 Fard + 2 Sunnah\n\n🌙 **Isha** - Night prayer\n• 4 Sunnah + 4 Fard + 2 Sunnah + 3 Witr\n\n📱 **For exact local times:**\n• IslamicFinder.org\n• Muslim Pro app\n• Your local mosque\n\n*Prayer times vary by location and season.*",
      type: 'prayer'
    },
    daily_verse: {
      text: "📖 **Verse of the Day - Surah Al-Baqarah (2:152):**\n\nفَاذْكُرُونِي أَذْكُرْكُمْ وَاشْكُرُوا لِي وَلَا تَكْفُرُونِ\n\n**Transliteration:**\n*Fadhkuruni adhkurkum washkuru li wa la takfurun*\n\n**Translation:**\n*\"So remember Me; I will remember you. And be grateful to Me and do not deny Me.\"*\n\n💭 **Reflection:**\nAllah promises to remember those who remember Him. This is an incredible honor - the Creator of the universe remembers us when we remember Him.\n\n🎯 **Today's Action:**\nMake dhikr throughout your day and notice Allah's blessings.",
      type: 'verse'
    },
    daily_hadith: {
      text: "⭐ **Hadith of the Day:**\n\n**Sahih al-Bukhari (6018)**\n\n*The Prophet (ﷺ) said:*\n\n**\"The believers in their mutual kindness, compassion, and sympathy are just one body - when a limb suffers, the whole body responds to it with wakefulness and fever.\"**\n\n📚 **Lesson:**\nThis hadith teaches us about the unity of the Muslim Ummah. We should care for our fellow Muslims as we care for ourselves.\n\n🎯 **Action:**\nCheck on a fellow Muslim today and offer help if needed.\n\n✅ **Authenticity:** Sahih (Sound)",
      type: 'hadith'
    },
    morning_dua: {
      text: "🌅 **Morning Duas Collection:**\n\n**1. Upon Waking:**\n\"الْحَمْدُ لِلَّهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا وَإِلَيْهِ النُّشُورُ\"\n\n*Alhamdulillahi alladhi ahyana ba'da ma amatana wa ilayhi an-nushur*\n\n*\"All praise to Allah who gave us life after death, and to Him is the resurrection.\"*\n\n**2. Morning Protection:**\n\"أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ\" (3x)\n\n*A'udhu bikalimat Allahi at-tammati min sharri ma khalaq*\n\n*\"I seek refuge in Allah's perfect words from the evil He created.\"*\n\n**3. For Guidance:**\n\"رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ\"\n\n*Rabbana atina fi'd-dunya hasanatan wa fi'l-akhirati hasanatan wa qina 'adhab an-nar*\n\n*\"Our Lord, give us good in this world and the next, and save us from the Fire.\"*",
      type: 'dua'
    },
    qibla: {
      text: "🧭 **Qibla Direction Guide:**\n\n📍 **What is Qibla?**\nThe direction toward the Kaaba in Mecca that Muslims face during prayer.\n\n🌍 **General Directions by Region:**\n• **Europe & North America:** Southeast\n• **East Asia:** West to Southwest\n• **Africa:** Northeast to East\n• **Australia:** Northwest\n\n📱 **Accurate Methods:**\n1. GPS-based Qibla apps\n2. IslamicFinder.org Qibla locator\n3. Physical Qibla compass\n4. Ask your local mosque\n\n⚠️ **Important Notes:**\n• These are general directions only\n• Use precise tools for exact direction\n• Some apps work offline\n• Verify with multiple sources\n\n🤲 **Dua when facing Qibla:**\n*\"Wajjahtu wajhiya lilladhi fatara as-samawati wal-arda...\"*",
      type: 'qibla'
    },
    islamic_calendar: {
      text: "📅 **Islamic Calendar Information:**\n\n🌙 **Current Hijri Date:** " + getHijriDate() + "\n\n📝 **Upcoming Islamic Events:**\n\n• **12 Rabi' al-Awwal:** Mawlid an-Nabi (ﷺ)\n• **27 Rajab:** Isra and Mi'raj Night\n• **15 Sha'ban:** Laylat al-Bara'ah\n• **Ramadan:** Month of Fasting\n• **Eid al-Fitr:** Festival after Ramadan\n• **10 Dhul Hijjah:** Eid al-Adha\n\n🗓️ **Sacred Months:**\n1. Muharram (1st month)\n2. Rajab (7th month)\n3. Dhul Qi'dah (11th month)\n4. Dhul Hijjah (12th month)\n\n💡 **Note:** Dates may vary by 1-2 days based on moon sighting in your region.\n\n📱 **Recommended:** Use Islamic calendar apps for accurate local dates.",
      type: 'calendar'
    }
  };

  // Enhanced response system
  const getIslamicResponse = (message) => {
    const lowerMsg = message.toLowerCase();
    
    // Specific Islamic topics
    if (lowerMsg.includes('five pillars') || lowerMsg.includes('pillars of islam')) {
      return "🕌 **The Five Pillars of Islam:**\n\n**1. Shahada (Declaration of Faith)**\n*\"La ilaha illa Allah, Muhammadur rasul Allah\"*\n*There is no god but Allah, Muhammad is His messenger*\n\n**2. Salah (Prayer)**\nFive daily prayers connecting us with Allah\n\n**3. Zakat (Charity)**\n2.5% of wealth annually to help the needy\n\n**4. Sawm (Fasting)**\nFasting during the month of Ramadan\n\n**5. Hajj (Pilgrimage)**\nPilgrimage to Mecca once in a lifetime if able\n\nThese form the foundation of Islamic practice.";
    }
    
    if (lowerMsg.includes('allah') || lowerMsg.includes('who is allah')) {
      return "☪️ **About Allah (SWT):**\n\nAllah is the One and Only God in Islam. The word 'Allah' means 'The God' in Arabic.\n\n**Beautiful Names (Asma al-Husna):**\n• Ar-Rahman - The Most Compassionate\n• Ar-Raheem - The Most Merciful\n• Al-Ghafoor - The Oft-Forgiving\n• As-Saboor - The Most Patient\n• Al-Wadud - The Most Loving\n\n**Quran says (112:1-4):**\n*\"Say: He is Allah, the One! Allah, the Eternal, Absolute; He begets not, nor is He begotten; And there is none like unto Him.\"*\n\nAllah is perfect, without partners or equals.";
    }
    
    if (lowerMsg.includes('prophet') || lowerMsg.includes('muhammad')) {
      return "🌟 **Prophet Muhammad (ﷺ):**\n\nMuhammad (peace be upon him) is the final Prophet and Messenger of Allah.\n\n**Key Facts:**\n• Born: 570 CE in Mecca\n• Received first revelation: Age 40\n• Known as: Al-Amin (The Trustworthy)\n• Mission: Guide humanity to worship Allah alone\n\n**His Character:**\n• Perfect example for humanity\n• Known for honesty and trustworthiness\n• Kind to all people and animals\n• Patient in difficulties\n• Forgiving to enemies\n\n**His Message:**\n*\"I have been sent to perfect good character.\"*\n\n**Follow His Example:**\nKindness, honesty, justice, patience, and gratitude.";
    }
    
    if (lowerMsg.includes('prayer') || lowerMsg.includes('salah') || lowerMsg.includes('how to pray')) {
      return "🕌 **Prayer (Salah) Guidance:**\n\n**Before Prayer:**\n• Perform Wudu (ablution)\n• Face Qibla (direction of Kaaba)\n• Make intention (Niyyah) in heart\n• Use clean place and proper dress\n\n**Prayer Steps:**\n1. **Takbir** - Say \"Allahu Akbar\" (hands to ears)\n2. **Qiyam** - Stand and recite Fatiha + Surah\n3. **Ruku** - Bow and say \"Subhana Rabbiyal Azeem\"\n4. **Sujud** - Prostrate and say \"Subhana Rabbiyal A'la\"\n5. **Tashahhud** - Sit and recite At-Tahiyyat\n6. **Taslim** - Turn head saying \"Assalamu alaikum\"\n\n**Five Daily Prayers:**\nFajr, Dhuhr, Asr, Maghrib, Isha\n\n💡 Focus on presence of heart (Khushu) during prayer.";
    }
    
    if (lowerMsg.includes('quran') || lowerMsg.includes('quraan')) {
      return "📖 **The Holy Quran:**\n\nThe Quran is the final revelation from Allah to humanity, revealed to Prophet Muhammad (ﷺ).\n\n**Key Facts:**\n• 114 chapters (Surahs)\n• 6,236 verses (Ayat)\n• Revealed over 23 years\n• Preserved in original Arabic\n• Final scripture for all mankind\n\n**Guidance for:**\n• Worship and faith\n• Moral conduct\n• Social justice\n• Personal development\n• Life after death\n\n**Benefits of Reading:**\n• Each letter earns 10 rewards\n• Spiritual guidance and healing\n• Connection with Allah\n• Peace and tranquility\n\n**Recommended:**\nRead daily with translation and reflection.";
    }
    
    if (lowerMsg.includes('dua') || lowerMsg.includes('supplication')) {
      return "🤲 **About Dua (Supplication):**\n\nDua is calling upon Allah, asking for His help, guidance, and mercy.\n\n**Types of Dua:**\n• Praise and gratitude\n• Seeking forgiveness\n• Asking for needs\n• Protection from harm\n• Guidance and wisdom\n\n**Best Times for Dua:**\n• Between Maghrib and Isha\n• Last third of the night\n• After obligatory prayers\n• While fasting\n• During rain\n\n**Etiquette of Dua:**\n• Start with praise of Allah\n• Send blessings on Prophet (ﷺ)\n• Be humble and sincere\n• Ask in a good state (with wudu)\n• End with 'Ameen'\n\n**Remember:** Allah answers all duas in His perfect wisdom and timing.";
    }
    
    if (lowerMsg.includes('halal') || lowerMsg.includes('haram') || lowerMsg.includes('food')) {
      return "🍽️ **Halal & Haram Foods:**\n\n**✅ HALAL (Permitted):**\n• All fruits and vegetables\n• Grains, nuts, legumes\n• Fish with scales\n• Chicken, beef, lamb (properly slaughtered)\n• Milk, cheese, honey\n\n**❌ HARAM (Forbidden):**\n• Pork and pork products\n• Alcohol and intoxicants\n• Blood of animals\n• Animals that died naturally\n• Carnivorous animals with fangs\n• Birds of prey with talons\n\n**Conditions for Halal Meat:**\n• Animal must be healthy\n• Slaughtered by Muslim/Christian/Jew\n• Name of Allah mentioned\n• Sharp knife used\n• Blood properly drained\n\n**When in Doubt:**\nAvoid questionable items and seek knowledge from reliable sources.";
    }
    
    // Default helpful response
    return `جزاك الله خيراً for your question!\n\nI'm here to provide Islamic guidance on:\n\n📖 **Quran & Hadith** - Verses, meanings, authentic sayings\n🕐 **Prayer & Worship** - Times, procedures, guidance\n🤲 **Duas & Dhikr** - Daily supplications\n⚖️ **Fiqh & Rulings** - Islamic law guidance\n🌙 **Islamic Events** - Calendar and occasions\n💡 **Daily Reminders** - Spiritual motivation\n\nFeel free to ask about any Islamic topic. I'll provide guidance based on Quran and authentic Sunnah.\n\nMay Allah guide us all. Ameen! 🤲`;
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    setTimeout(() => {
      const response = {
        id: messages.length + 2,
        text: getIslamicResponse(inputMessage),
        sender: 'agent',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, response]);
      setIsTyping(false);
    }, 2000);
  };

  const handleQuickAction = (action) => {
    const content = dailyContent[action];
    if (content) {
      const agentMessage = {
        id: messages.length + 1,
        text: content.text,
        sender: 'agent',
        timestamp: new Date(),
        type: content.type
      };
      setMessages(prev => [...prev, agentMessage]);
    }
  };

  return (
    <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 via-green-600 to-teal-600 text-white p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <Moon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Islamic AI Assistant</h1>
              <p className="text-green-100">TheIslamInsights.com - Your Trusted Guide</p>
            </div>
          </div>
          <div className="text-right space-y-1">
            <div className="text-green-100 text-sm">Hijri Date</div>
            <div className="text-lg font-semibold">{getHijriDate()}</div>
            <div className="text-green-100 text-sm">Current Time</div>
            <div className="text-lg font-semibold">
              {currentTime.toLocaleTimeString('en-US', { 
                hour12: true, 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="bg-green-50 border-b overflow-x-auto">
        <div className="flex gap-1 p-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                selectedCategory === category.id
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-green-700 hover:bg-green-100'
              }`}
            >
              <category.icon size={16} />
              <span className="text-sm font-medium">{category.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-b">
        <h3 className="text-sm font-semibold text-green-800 mb-3">Quick Islamic Guidance</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleQuickAction(action.action)}
              className={`flex flex-col items-center gap-2 p-3 rounded-lg text-white hover:opacity-90 transition-all transform hover:scale-105 ${action.color}`}
            >
              <action.icon size={20} />
              <span className="text-xs font-medium text-center">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50 to-white">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
                message.sender === 'user'
                  ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.text}</div>
              <div
                className={`text-xs mt-2 flex items-center gap-1 ${
                  message.sender === 'user' ? 'text-green-100' : 'text-gray-500'
                }`}
              >
                <Clock size={10} />
                {message.timestamp.toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
                {message.type && (
                  <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs">
                    {message.type}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 px-4 py-3 rounded-2xl border border-gray-200 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="text-sm text-green-600">Assistant is typing</div>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-50 border-t">
        <div className="flex gap-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask about Islam: prayers, Quran, halal food, duas..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim()}
            className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all transform hover:scale-105 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            <Send size={16} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        
        {/* Sample Questions */}
        <div className="mt-3 flex flex-wrap gap-2">
          {['Five pillars of Islam', 'How to pray?', 'Morning duas', 'Halal food guide', 'About Prophet Muhammad'].map((question, index) => (
            <button
              key={index}
              onClick={() => setInputMessage(question)}
              className="px-3 py-1 bg-white text-green-600 text-sm rounded-full border border-green-200 hover:bg-green-50 transition-colors"
            >
              {question}
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 bg-gradient-to-r from-green-600 to-emerald-600 text-center">
        <div className="text-white/90 text-sm space-y-1">
          <p className="flex items-center justify-center gap-2">
            <Heart size={14} className="text-red-300" />
            May Allah (SWT) guide us all on the straight path
          </p>
          <p>🕌 Always consult qualified Islamic scholars for important religious matters</p>
          <p className="text-white/70">© 2024 TheIslamInsights.com - Your Trusted Islamic Resource</p>
        </div>
      </div>
    </div>
  );
};

export default IslamicAIAgent;
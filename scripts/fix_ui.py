with open("/Users/fahadiqbal/Documents/Latest_Codes/Islamic work/Islamic AI Agent/islamic-ai-agent/src/components/IslamicAIAgent.tsx", "r") as f:
    lines = f.readlines()

new_content = ""
for line in lines:
    if line.strip() == "return (":
        break
    new_content += line

new_code = """  // Helper to format text with scholarly cards
  const formatMessageText = (text: string) => {
    // Basic regex to find segments that look like Quran/Hadith citations or Arabic
    const parts = text.split(/(\[Quran\s+\d+:\d+\]|\[Bukhari\s+\d+\]|\[Muslim\s+\d+\]|Hadith\s+#\d+|Surah\s+[\w\-]+\s+\d+:\d+|[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s\d،؟؛!.]+)/g);
    
    return parts.map((part, index) => {
      if (!part) return null;
      
      // Check if Arabic
      if (/[\u0600-\u06FF]/.test(part)) {
        return <div key={index} className="arabic-text text-center my-6 text-[1.6rem] font-bold text-amber-500 drop-shadow-sm">{part}</div>;
      }
      
      // Check if Citation
      if (/(\[Quran|\[Bukhari|\[Muslim|Hadith #|Surah)/.test(part)) {
        return <span key={index} className="px-2 py-0.5 mx-1 inline-block bg-[#10664f]/10 text-[#10664f] font-bold rounded-md text-xs">{part}</span>;
      }
      
      // Regular text
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="flex h-screen bg-[#e5e5e5] p-0 sm:p-4 md:p-8 animate-scholarly-entry font-sans">
      {/* Main Container */}
      <div className="flex flex-1 max-w-[1400px] mx-auto rounded-[2rem] overflow-hidden shadow-2xl bg-white border border-gray-200/50">
        
        {/* Sidebar (Scholarly Insights) - Desktop always, Mobile toggle */}
        <div className={`${showSidebar ? 'flex' : 'hidden'} lg:flex flex-col w-[22rem] bg-moss-sidebar shrink-0 relative`}>
          {/* NOOR Branding */}
          <div className="p-8 pt-10">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-amber-400 flex items-center justify-center shadow-md">
                <Moon className="text-[#10664f] fill-[#10664f]" size={20} />
              </div>
              <div className="flex flex-col h-10 justify-center">
                <h2 className="text-[22px] font-[800] text-white tracking-widest leading-none mt-1">NOOR</h2>
                <p className="text-[9px] font-bold text-amber-400 uppercase tracking-[0.2em] mt-1">Islamic AI Chatbot</p>
              </div>
            </div>
          </div>

          {/* Scholarly Insights Label */}
          <div className="px-8 pt-6 pb-2">
            <h3 className="text-amber-400 text-[11px] font-extrabold tracking-widest uppercase">Scholarly Insights</h3>
          </div>

          {/* Insight Cards */}
          <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2 custom-scrollbar">
            <button 
              onClick={() => setInputMessage('What is the significance of the month of Ramadan according to Quran and Hadith?')}
              className="w-full text-left p-4 rounded-xl hover:bg-white/10 transition-all cursor-pointer group relative"
            >
              <h4 className="text-amber-300 text-[15px] font-bold mb-2">Ramadan Essentials</h4>
              <p className="text-[11px] text-[#55695a] font-bold leading-relaxed">What is the significance of the month of Ramadan according to Quran and Hadith?</p>
            </button>

            <button 
              onClick={() => setInputMessage('What are the best daily duas and dhikr from authentic hadith?')}
              className="w-full text-left p-4 rounded-xl hover:bg-white/10 transition-all cursor-pointer group relative"
            >
              <h4 className="text-amber-300 text-[15px] font-bold mb-2">Daily Dua & Dhikr</h4>
              <p className="text-[11px] text-[#55695a] font-bold leading-relaxed">Daily Dua & Dhikr can have positive Islamic attributes.</p>
            </button>

            <button 
              onClick={() => setInputMessage('Show me an authentic hadith from Sahih Bukhari about the importance of faith')}
              className="w-full text-left p-4 rounded-xl hover:bg-white/10 transition-all cursor-pointer group relative"
            >
              <h4 className="text-amber-300 text-[15px] font-bold mb-2">Hadith Collections</h4>
              <p className="text-[11px] text-[#55695a] font-bold leading-relaxed">Hadith collections in commons and oratory and hadith collections.</p>
            </button>

            <button 
              onClick={() => setInputMessage('Explain the tafsir of Surah Al-Fatiha from Ibn Kathir')}
              className="w-full text-left p-4 rounded-xl hover:bg-white/10 transition-all cursor-pointer group relative"
            >
              <h4 className="text-amber-300 text-[15px] font-bold mb-2">Quran Tafseer</h4>
              <p className="text-[11px] text-[#55695a] font-bold leading-relaxed">Quran tafseer on advanced Islamic all caratam, and authoritaties.</p>
            </button>

            {/* Active Indicator (Visual only, on the right edge) */}
            <div className="absolute right-0 top-40 bottom-24 w-[5px] bg-[#10b981] pointer-events-none"></div>

            {/* Today's Info */}
            <div className="mx-4 mt-8 flex flex-col items-center">
              <h4 className="text-[#647c6b] text-[11px] font-bold mb-2 uppercase tracking-[0.2em]">Today</h4>
              <div className="text-[9px] uppercase tracking-widest text-[#55695a] mb-1 font-bold">Hijri Date</div>
              <div className="text-amber-400 text-[13px] font-extrabold tracking-wide">{hijriDate}</div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 pb-8 text-center text-[#55695a]">
            <p className="text-[9px] font-bold uppercase tracking-[0.2em] italic">Authenticity Guaranteed</p>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex flex-col flex-1 relative bg-[#fcfdfc]">
          
          {/* Top Bar */}
          <div className="px-8 py-5 flex justify-between items-center border-b border-gray-200/60 bg-white shadow-sm z-10">
            <div className="flex items-center gap-4">
              <button onClick={() => setShowSidebar(!showSidebar)} className="lg:hidden text-moss-dark hover:text-emerald-700">
                <Settings size={20} />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#10664f] flex items-center justify-center">
                  <Moon className="text-amber-400 fill-amber-400" size={18} />
                </div>
                <div className="flex flex-col justify-center h-10">
                  <h1 className="text-[20px] font-[800] tracking-tight text-gray-600 leading-none mt-1">Noor <span className="text-amber-500">Al-Alimi</span></h1>
                  <p className="text-[9px] text-[#10b981] uppercase tracking-[0.25em] font-extrabold mt-1.5">Islamic Scholarly AI</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#a7f3d0] rounded-full"></div>
              <span className="text-[11px] text-[#6ee7b7] font-bold tracking-wider">{currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar bg-[#f8fafa]">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in w-full`}
              >
                <div
                  className={`max-w-[90%] lg:max-w-[75%] px-8 py-6 transition-all ${
                    message.sender === 'user'
                      ? 'bg-[#10664f] text-white rounded-[2rem] rounded-tr-md shadow-md'
                      : 'bg-white text-gray-400 rounded-[2rem] rounded-tl-md shadow-[0_4px_30px_rgba(0,0,0,0.03)] border border-gray-100 border-l-[4px] border-l-amber-400'
                  }`}
                >
                  {message.sender === 'agent' && (
                    <div className="flex items-center gap-2 mb-5">
                      <Star size={13} className="text-amber-400 fill-amber-400" />
                      <span className="text-[10px] uppercase tracking-widest text-amber-500 font-[800]">Verifiable Source Rooted</span>
                    </div>
                  )}
                  
                  <div className={`text-[15px] leading-[1.8] font-[500] tracking-wide ${message.sender === 'user' ? 'text-white' : 'text-gray-500'}`}>
                    {formatMessageText(message.text)}
                  </div>
                  
                  <div className={`text-[9px] mt-6 flex items-center gap-3 font-extrabold tracking-[0.2em] ${
                    message.sender === 'user' ? 'text-emerald-200/50' : 'text-gray-400'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    <span className="h-[1px] w-6 bg-current opacity-30"></span>
                    {message.type ? message.type.toUpperCase() : 'WELCOME'}
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white px-8 py-6 rounded-[2rem] rounded-tl-md shadow-sm border border-gray-100 border-l-[4px] border-l-amber-400">
                  <div className="flex items-center gap-3">
                    <div className="flex space-x-1">
                      <div className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-[10px] text-amber-500 uppercase tracking-widest font-extrabold px-2">Consulting Scholarly Databases...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Bottom Area (Gray Container) */}
          <div className="bg-moss-app px-8 pt-[18px] pb-6 rounded-br-[2rem]">
            {/* Quick Guidance Bar */}
            <div className="flex gap-10 overflow-x-auto no-scrollbar mb-[18px] px-2 pb-1 justify-center lg:justify-start">
              {['Five pillars', 'Perform Wudu', 'Zakat Rules', 'Prophet Seerah'].map((q, idx) => (
                <button 
                  key={idx} 
                  onClick={() => setInputMessage(q)}
                  className="whitespace-nowrap text-[12px] font-extrabold tracking-wide text-amber-500 hover:text-amber-600 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>

            {/* Input Area */}
            <div className="relative max-w-5xl mx-auto">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Seek authentic guidance on Quran, Sunnah, or Fiqh..."
                className="w-full bg-moss-input text-[#3b5247] placeholder:text-[#6a8b78] font-[600] pl-8 pr-16 py-[18px] rounded-[2rem] focus:outline-none focus:ring-2 focus:ring-amber-500/50 transition-all text-[15px] shadow-inner"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isTyping}
                className="absolute right-6 top-[18px] text-[#55695a] hover:text-[#2d3b32] transition-colors disabled:opacity-30 flex items-center justify-center -rotate-45"
              >
                <div className="rotate-90">
                  <Send size={22} strokeWidth={2.5} />
                </div>
              </button>
            </div>
            
            <p className="mt-5 text-[10px] text-center text-[#849a88] font-[800] tracking-[0.15em] uppercase">
              {kbStats.docs 
                ? `POWERED BY ${Math.round(kbStats.docs / 1000)}K+ AUTHENTIC SCHOLARLY DOCUMENTS`
                : 'POWERED BY AUTHENTIC SCHOLARLY SOURCES FROM TANZIL, SUNNAH.COM & SCHOLARS'
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IslamicAIAgent;
"""
new_content += new_code
with open("/Users/fahadiqbal/Documents/Latest_Codes/Islamic work/Islamic AI Agent/islamic-ai-agent/src/components/IslamicAIAgent.tsx", "w") as f:
    f.write(new_content)

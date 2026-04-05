import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Star, MessageSquare,
  Mic, Paperclip, Moon, Book, Scroll, Sun,
  LayoutGrid, Share2, Copy, PanelLeft, MapPin, Compass
} from 'lucide-react';
import { twMerge } from 'tailwind-merge';

// --- Utility for cleaner class names ---
type ClassValue = string | number | boolean | undefined | null | { [key: string]: any } | ClassValue[];
function clsx(...inputs: ClassValue[]): string {
  let str = '';
  for (let i = 0; i < inputs.length; i++) {
    let x = inputs[i];
    if (x) {
      if (typeof x === 'string' || typeof x === 'number') {
        str += (str && ' ') + x;
      } else if (Array.isArray(x)) {
        let y = clsx(...x);
        if (y) str += (str && ' ') + y;
      } else if (typeof x === 'object') {
        for (const k in x) {
          if (x[k]) str += (str && ' ') + k;
        }
      }
    }
  }
  return str;
}

const cn = (...inputs: ClassValue[]) => {
  return twMerge(clsx(...inputs));
};

// --- Detection Utility for Scholarly Scripts ---
const detectScript = (text: string) => {
  const arabicRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/;
  const urduRegex = /[\u0600-\u06FF]/; // Urdu shares most characters but often uses specific fonts
  
  if (arabicRegex.test(text)) {
    // Check for Urdu specific characters if needed, but for now we'll prioritize Amiri for standard Arabic
    return 'arabic';
  }
  return 'english';
};

// --- Museum-Grade Assets ---
const NoorLogo = ({ size = 32, className = "" }: { size?: number, className?: string }) => (
  <div className={cn("relative flex items-center justify-center shrink-0", className)}>
    <div className="absolute inset-[-20%] bg-gold-primary/20 blur-[20px] rounded-full animate-pulse-slow shrink-0" />
    <img
      src="/noor-logo.png"
      alt="Noor Logo"
      style={{ width: size, height: size }}
      className="relative z-10 object-contain drop-shadow-[0_0_15px_rgba(229,192,111,0.5)]"
    />
  </div>
);

const SanctuaryGreeting = ({ onSuggestionClick }: { onSuggestionClick: (query: string) => void }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 1.2, ease: [0.16, 1, 0.3, 1] as any }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-col items-center justify-center text-center space-y-20 max-w-5xl mx-auto py-24"
    >
      <motion.div variants={itemVariants} className="relative">
        <div className="absolute inset-0 bg-gold-primary/30 blur-[100px] rounded-full animate-pulse-slow scale-150" />
        <NoorLogo size={160} className="relative animate-spin-slow duration-[60s]" />
      </motion.div>

      <motion.div variants={itemVariants} className="space-y-6">
        <h6 className="font-amiri text-gold-primary text-6xl md:text-8xl leading-none drop-shadow-[0_20px_40px_rgba(229,192,111,0.4)] antialiased select-none">
          اللَّهُ نُورُ السَّمَاوَاتِ وَالْأَرْضِ
        </h6>
        <p className="text-gold-primary/50 text-[12px] font-black uppercase tracking-[0.8em] font-outfit mt-8">
          Allah is the light of the heavens and the earth
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="space-y-12 max-w-3xl px-12">
        <p className="text-white/90 text-2xl font-medium leading-relaxed tracking-tight font-outfit">
          As-Salaam Alaykum. I am <span className="text-gold-primary font-black">Noor</span>, your scholarly portal to authentic Islamic knowledge.
        </p>
        
        {/* Interactive Suggestion Chips */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16 pb-12">
          {SUGGESTIONS.slice(0, 8).map((s, i) => (
            <motion.button
              key={i}
              whileHover={{ scale: 1.05, backgroundColor: 'rgba(229, 192, 111, 0.15)' }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onSuggestionClick(s.query)}
              className="flex flex-col items-center gap-4 p-6 rounded-3xl bg-white/[0.03] border border-white/10 hover:border-gold-primary/40 transition-all group"
            >
              <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center text-white/40 group-hover:text-gold-primary transition-colors">
                <s.icon size={20} />
              </div>
              <span className="text-[11px] font-black text-white/30 group-hover:text-white/80 uppercase tracking-widest font-outfit whitespace-nowrap">
                {s.label}
              </span>
            </motion.button>
          ))}
        </div>

        <div className="w-32 h-[2px] bg-gradient-to-r from-transparent via-gold-primary/40 to-transparent mx-auto shadow-[0_0_15px_rgba(229,192,111,0.5)]" />
      </motion.div>
    </motion.div>
  );
};

const SidebarCard = ({ title, desc, icon: Icon, onClick }: { title: string, desc: string, icon: any, onClick: () => void }) => (
  <motion.div
    whileHover={{ x: 8, backgroundColor: 'rgba(229, 192, 111, 0.04)' }}
    onClick={onClick}
    className="flex items-start gap-7 p-7 mb-3 rounded-[2rem] cursor-pointer transition-all border border-transparent hover:border-gold-primary/10 group"
  >
    <div className="w-16 h-16 shrink-0 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center justify-center text-white/20 group-hover:text-gold-primary group-hover:bg-gold-primary/10 transition-all shadow-inner">
      <Icon size={28} />
    </div>
    <div className="flex flex-col space-y-2">
      <h4 className="text-[17px] font-black text-white/90 group-hover:text-gold-primary transition-colors font-outfit">{title}</h4>
      <p className="text-[12px] text-white/20 leading-relaxed font-medium line-clamp-2 group-hover:text-white/40 transition-colors uppercase tracking-wider">{desc}</p>
    </div>

  </motion.div>
);

const ScholarEvidence = ({ type, translation, reference }: { type: 'quran' | 'hadith', translation: string, reference: string }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    className="evidence-box group border-gold-primary/40 mt-12 mb-8 bg-black/40 rounded-[3rem] overflow-hidden border shadow-[0_40px_80px_rgba(0,0,0,0.4)]"
  >
    <div className="py-7 px-14 bg-gold-primary/[0.08] border-b border-gold-primary/20 flex justify-between items-center">
      <div className="flex items-center gap-6">
        <div className="w-10 h-10 rounded-xl bg-gold-primary/20 flex items-center justify-center border border-gold-primary/30">
          <Star size={18} className="text-gold-primary animate-pulse" fill="currentColor" />
        </div>
        <span className="text-[14px] font-black text-gold-primary uppercase tracking-[0.6em] font-outfit">
          {type === 'quran' ? 'Primary Divine Revelation' : 'Prophetic Scholarly Authority'}
        </span>
      </div>
      <div className="flex items-center gap-4 bg-white/5 px-6 py-3 rounded-full border border-white/10 group/ref relative">
        <span className="text-[12px] font-black text-white/40 tracking-[0.2em] font-inter">[{reference}]</span>
        <button 
          onClick={() => {
            navigator.clipboard.writeText(reference);
            // We could trigger a toast here if needed, but the main copy handle is available
          }}
          className="ml-2 p-1 text-white/10 hover:text-gold-primary transition-colors"
          title="Copy Reference"
        >
          <Copy size={12} />
        </button>
      </div>
    </div>
    <div className="p-16 relative overflow-hidden">
      {/* Subtle Geometric Watermark */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none flex items-center justify-center">
        <NoorLogo size={400} className="scale-150 rotate-12" />
      </div>
      <div className="relative z-10 text-[24px] text-white/95 font-medium leading-[2.4] italic border-l-[6px] border-gold-primary/50 pl-14 font-outfit antialiased">
        "{translation}"
      </div>
    </div>
  </motion.div>
);

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai' | 'agent';
  timestamp: Date;
}

const SUGGESTIONS = [
  { icon: Sun, label: "Daily Adhkar", query: "What are the recommended morning and evening Adhkar?" },
  { icon: MapPin, label: "Prayer Times", query: "Show me the prayer times for my location" },
  { icon: Book, label: "Surah Al-Mulk", query: "What are the benefits of reciting Surah Al-Mulk every night?" },
  { icon: Compass, label: "Qibla Finder", query: "Which direction is the Qibla from here?" },
  { icon: Star, label: "99 Names", query: "Tell me about the 99 Names of Allah and their meanings" },
  { icon: Moon, label: "Tahajjud Dua", query: "What is the best dua to make during Tahajjud prayer?" },
  { icon: Scroll, label: "Zakat Calc", query: "How do I calculate Zakat on my savings and gold?" },
  { icon: MessageSquare, label: "Dua for Parents", query: "What are some beautiful Duas from the Quran for parents?" }
];

const PlaceholderRotator = () => {
  const placeholders = [
    "Inquire about Quran, Hadith, or Fiqh...",
    "Ask about the life of Prophet Muhammad (SAW)...",
    "How to perform specific prayers and Duas?",
    "Need a Zakat or Inheritance calculation?",
    "Seeking guidance from the Four Madhabs...",
    "Authentic Hadith grading and context..."
  ];
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % placeholders.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  return (
    <motion.span
      key={index}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="absolute left-0 pointer-events-none text-white/10"
    >
      {placeholders[index]}
    </motion.span>
  );
};

const IslamicAIAgent = ({ isWidget = false, apiUrl = 'http://localhost:5010' }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "As-Salaam Alaykum. I am Noor, your scholarly companion. How may I assist you today in your journey of knowledge?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [gender] = useState<'male' | 'female' | 'not_specified'>('not_specified');
  const [toast, setToast] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<number | null>(null);
  const [selectedReference, setSelectedReference] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  
  // Real-time Islamic Data State
  const [location, setLocation] = useState<{ lat: number, lng: number } | null>(null);
  const [prayerTimes, setPrayerTimes] = useState<any>(null);
  const [qibla, setQibla] = useState<any>(null);
  const [isLoadingIslamicData, setIsLoadingIslamicData] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  useEffect(() => {
    // Request location on mount
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc = { lat: position.coords.latitude, lng: position.coords.longitude };
          setLocation(loc);
          fetchIslamicData(loc);
        },
        (error) => {
          console.error("Location access denied or failed", error);
          showToast("Location access helpful for Prayer Times 🤲");
        }
      );
    }
  }, []);

  const fetchIslamicData = async (loc: { lat: number, lng: number }) => {
    setIsLoadingIslamicData(true);
    try {
      // Fetch Prayer Times
      const pRes = await fetch(`${apiUrl}/api/prayer-times`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: loc.lat, longitude: loc.lng })
      });
      const pData = await pRes.json();
      setPrayerTimes(pData.data || pData.prayer_times);

      // Fetch Qibla
      const qRes = await fetch(`${apiUrl}/api/qibla`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: loc.lat, longitude: loc.lng })
      });
      const qData = await qRes.json();
      setQibla(qData);
    } catch (error) {
      console.error("Failed to fetch Islamic data", error);
    } finally {
      setIsLoadingIslamicData(false);
    }
  };

  const handleSendMessage = async (text?: string) => {
    const textToSend = (text || inputMessage).trim();
    if (!textToSend || isTyping) return;

    const userMsg: Message = { id: Date.now(), text: textToSend, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    if (!text) setInputMessage('');
    setIsTyping(true);

    try {
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend, user_gender: gender }),
      });

      if (!response.ok) throw new Error('Service Unavailable');
      const data = await response.json();

      const aiMsg: Message = { id: Date.now() + 1, text: data.response, sender: 'ai', timestamp: new Date() };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      console.error('Chat error:', error);
      showToast("Connection issue - Attempting to restore");
    } finally {
      setIsTyping(false);
    }
  };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      showToast("Knowledge Copied 🤲");
    } catch (err) {
      showToast("Copy failed - Please retry");
    }
  };

  const handleShare = async (text: string) => {
    const shareData = {
      title: 'Scholarly Insight from Noor',
      text: `${text}\n\n— Sent from Noor Islamic AI Agent`,
      url: window.location.href
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        await handleCopy(text);
        showToast("Link shared to clipboard 🤲");
      }
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        showToast("Sharing currently unavailable");
      }
    }
  };

  const renderMessageContent = (msg: Message) => {
    const isAI = msg.sender === 'ai' || msg.sender === 'agent';
    const text = msg.text;

    if (isAI) {
      // Enhanced regex to match broader scholarly formats like [The Holy Quran 17:78] or [Sahih Bukhari 123]
      const quranRegex = /\[(?:The\s+Holy\s+)?Quran\s*(?:\([^)]*\))?\s*(\d+:\d+)\]/i;
      const hadithRegex = /\[(?:Sahih\s+|Sunan\s+|Jami`?\s+|Muwatta\s+)?(Bukhari|Muslim|Hadith|Tirmidhi|Dawud|Nasa'i|Majah|Malik|Nawawi)\s*(?:\([^)]*\))?\s*(?:Hadith\s+)?#?(\d+)\]/i;

      return (
        <div className="space-y-12">
          {text.split('\n\n').filter((block: string) => block.trim()).map((block: string, i: number) => {
            // Case 1: Scholar Evidence (Quran/Hadith)
            if (quranRegex.test(block)) {
              const match = block.match(quranRegex);
              return <ScholarEvidence key={i} type="quran" translation={block.replace(quranRegex, "").trim()} reference={`Quran ${match![1]}`} />;
            }
            if (hadithRegex.test(block)) {
              const match = block.match(hadithRegex);
              return <ScholarEvidence key={i} type="hadith" translation={block.replace(hadithRegex, "").trim()} reference={`${match![1]} ${match![2]}`} />;
            }

            // Case 2: Script-Aware Block Parsing
            const lines = block.split('\n').filter((l: string) => l.trim());
            const processedLines = lines.map((line: string, idx: number) => {
              const lineTrimmed = line.trim();
              const scriptType = detectScript(lineTrimmed);
              const isArabic = scriptType === 'arabic';
              
              if (isArabic) {
                let content = lineTrimmed;
                // Remove prefixes if they still exist for backward compatibility or direct data
                content = content.replace(/^(?:arabic|urdu):/i, "").trim();

                // Intelligently peel off trailing transliterations in parentheses (but do not display)
                const translitMatch = content.match(/\(([^)]+)\)$/);
                if (translitMatch) {
                  content = content.replace(translitMatch[0], "").trim();
                }

                return (
                  <div key={idx} className="space-y-4 mb-14 group/script">
                    <div
                      dir="rtl"
                      className="text-right drop-shadow-2xl transition-all duration-700 py-6 arabic-text text-6xl text-gold-primary border-b border-gold-primary/10 hover:border-gold-primary/30"
                    >
                      {content}
                    </div>
                  </div>
                );
              }

              // Hide Transliteration-only lines (standalone parentheses)
              if (/^\(.*\)$/.test(lineTrimmed)) {
                return null;
              }

              // Fallback for standard English/Mixed text
              return (
                <p key={idx} className="text-[20px] text-white/90 leading-[2.2] font-medium tracking-tight mb-6 last:mb-0 antialiased">
                  {lineTrimmed.split(/(\*\*.*?\*\*)/g).map((part: string, j: number) =>
                    part.startsWith('**') && part.endsWith('**')
                      ? <strong key={j} className="text-gold-primary font-black drop-shadow-[0_0_10px_rgba(229,192,111,0.3)]">{part.slice(2, -2)}</strong>
                      : part
                  )}
                </p>
              );
            });

            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.12, duration: 1, ease: [0.16, 1, 0.3, 1] as any }}
                className="space-y-4"
              >
                {processedLines}
              </motion.div>
            );
          })}
        </div>
      );
    }
    return <div className="text-[18px] font-semibold text-white/95 leading-relaxed">{text}</div>;
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden flex flex-col items-center justify-center p-12 bg-[#011412]">
      {/* High-Fidelity Realistic Background from 2nd Image */}
      <div className="absolute inset-0 z-0 opacity-100 pointer-events-none transition-opacity duration-[2000ms]">
        <img
          src="/background-premium.png"
          alt="Noor AI Islamic Agent"
          className="w-full h-full object-cover mix-blend-screen opacity-100"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#011412]/60 via-transparent to-[#011412]/30" />

      </div>

      {/* Main Scholarly Station */}
      <div className="flex w-full h-[90vh] max-w-[1780px] bg-[#011412]/85 backdrop-blur-[80px] rounded-[4rem] border border-white/5 overflow-hidden shadow-[0_120px_240px_rgba(0,0,0,0.98)] transition-all relative z-10">

        {/* Simplified Authored Sidebar */}
        <motion.div
          animate={{
            width: isSidebarOpen ? 480 : 0,
            opacity: isSidebarOpen ? 1 : 0,
            x: isSidebarOpen ? 0 : -20
          }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col bg-black/20 border-r border-white/5 overflow-hidden relative"
        >
          <div className="w-[480px] flex flex-col px-10 pt-16 pb-12 h-full">
            <div className="flex items-center gap-6 mb-20 pl-4">
              <NoorLogo size={42} />
              <div className="flex flex-col">
                <span className="text-[18px] font-black text-white tracking-[0.3em] font-outfit uppercase">Noor</span>
                <span className="text-[10px] font-bold text-white/20 tracking-[0.6em] uppercase">Islamic AI Chatbot</span>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto no-scrollbar pr-2">
              <SidebarCard icon={Star} title="Islam & Moral Character" desc="WHAT DOES ISLAM TEACH ABOUT MORAL CHARACTER AND DAILY CONDUCT?" onClick={() => handleSendMessage("What does Islam teach about moral character and how should a Muslim conduct themselves in daily life?")} />
              <SidebarCard icon={LayoutGrid} title="The Five Pillars" desc="EXPLAIN THE FIVE PILLARS AND WHY THEY ARE OBLIGATORY FOR EVERY MUSLIM" onClick={() => handleSendMessage("Explain the five pillars of Islam and why they are considered obligatory for every Muslim.")} />
              <SidebarCard icon={Moon} title="Ramadan Essentials" desc="SIGNIFICANCE OF RAMADAN & FAST PROTOCOLS" onClick={() => handleSendMessage("Tell me about Ramadan significance")} />
              <SidebarCard icon={Sun} title="Daily Dua & Dhikr" desc="PROPHETIC SUPPLICATIONS FOR HEART PURITY" onClick={() => handleSendMessage("What are the best daily duas?")} />
              <SidebarCard icon={Book} title="Hadith Collections" desc="AUTHENTIC CHAINS FROM THE NINE BOOKS" onClick={() => handleSendMessage("How are Hadiths authenticated?")} />
              <SidebarCard icon={Scroll} title="Quran Tafseer" desc="CLASSICAL EXEGESIS & SCHOLARLY INSIGHTS" onClick={() => handleSendMessage("Tell me about Quranic interpretation")} />

              {/* Real-time Islamic Widgets */}
              <div className="mt-12 space-y-6">
                <div className="px-6 py-2">
                  <span className="text-[10px] font-black text-gold-primary/40 tracking-[0.5em] uppercase">Real-time Sacred Data</span>
                </div>
                
                {/* Prayer Times Widget */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-gold-primary/5 border border-gold-primary/10 rounded-[2.5rem] p-8 mx-2 relative overflow-hidden group shadow-2xl"
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gold-primary/10 blur-[50px] rounded-full -mr-16 -mt-16 group-hover:bg-gold-primary/20 transition-all" />
                  <div className="flex items-center gap-6 mb-6">
                    <div className="w-12 h-12 rounded-2xl bg-gold-primary/20 flex items-center justify-center text-gold-primary">
                      <MapPin size={24} />
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[14px] font-black text-white/90 font-outfit uppercase tracking-wider">Prayer Schedule</span>
                      <span className="text-[10px] font-bold text-gold-primary/60 uppercase tracking-widest">
                        {prayerTimes?.hijri || "Detecting Location..."}
                      </span>
                    </div>
                  </div>
                  
                  {prayerTimes ? (
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(prayerTimes.timings || {}).filter(([k]) => ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'].includes(k)).map(([name, time]: [any, any]) => (
                        <div key={name} className="flex flex-col p-3 bg-white/[0.03] rounded-xl border border-white/5">
                          <span className="text-[9px] font-black text-white/30 uppercase tracking-widest">{name}</span>
                          <span className="text-[14px] font-bold text-gold-primary">{time}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-[12px] text-white/20 italic animate-pulse">Requesting celestial timings...</div>
                  )}
                </motion.div>

                {/* Qibla Direction Widget */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-8 mx-2 flex items-center gap-8 shadow-xl"
                >
                  <div className="relative w-20 h-20 flex items-center justify-center bg-black/40 rounded-full border-2 border-gold-primary/20 overflow-hidden shadow-inner">
                    <motion.div 
                      animate={{ rotate: qibla?.bearing || 0 }}
                      transition={{ type: "spring", stiffness: 50 }}
                      className="text-gold-primary"
                    >
                      <Compass size={44} strokeWidth={1.5} />
                    </motion.div>
                    <div className="absolute inset-0 bg-gradient-to-t from-gold-primary/10 to-transparent pointer-events-none" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[14px] font-black text-white/90 font-outfit uppercase tracking-wider">Qibla Direction</span>
                    <span className="text-[18px] font-bold text-gold-primary tracking-tight">
                      {qibla?.bearing ? `${qibla.bearing.toFixed(1)}° ${qibla.direction}` : "Not Determined"}
                    </span>
                    <span className="text-[9px] font-bold text-white/20 uppercase tracking-[0.2em] mt-1">Facing Holy Kaaba</span>
                  </div>
                </motion.div>
              </div>
          </div>
        </div>
      </motion.div>

        {/* Chat Sanctuary Area */}
        <div className="flex-1 flex flex-col relative bg-gradient-to-br from-white/[0.015] to-transparent">
          {/* Elegant Top Header */}
          <div className="h-32 flex items-center justify-between px-20 border-b border-white/5 bg-white/[0.005]">
            <div className="flex items-center gap-6">
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="w-14 h-14 rounded-2xl flex items-center justify-center bg-white/[0.03] border border-white/10 text-white/30 hover:text-gold-primary hover:bg-gold-primary/10 transition-all shadow-xl group"
              >
                <PanelLeft size={24} className={cn("transition-transform duration-500", !isSidebarOpen && "rotate-180")} />
              </button>
              <div className="w-16 h-16 rounded-[1.5rem] bg-white/[0.03] border border-white/10 flex items-center justify-center text-white/20 shadow-2xl">
                <NoorLogo size={32} />
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-black text-white tracking-tight uppercase font-outfit">Noor Islamic Agent</span>
                <span className="text-[11px] font-bold text-white/30 tracking-[0.4em] uppercase">Scholarly Assistant Authority</span>
              </div>
            </div>

            <div className="flex items-center gap-8">
              <span className="font-amiri text-white text-3xl tracking-widest select-none drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</span>
            </div>
          </div>

          {/* Messages Sanctuary */}
          <div className="flex-1 overflow-y-auto no-scrollbar px-24 py-16 space-y-2 pb-64" ref={chatContainerRef}>
            {messages.length === 1 && !isTyping && (
              <SanctuaryGreeting onSuggestionClick={(q) => {
                setInputMessage(q);
                handleSendMessage(q);
              }} />
            )}

            <AnimatePresence mode="popLayout">
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] as any }}
                  className={cn("flex w-full", msg.sender === 'user' ? "justify-end" : "justify-start")}
                >
                  <div
                    onMouseEnter={() => setLastAction(msg.id)}
                    onMouseLeave={() => setLastAction(null)}
                    className={cn(
                      "max-w-[85%] p-14 rounded-[3.5rem] border transition-all duration-1000 backdrop-blur-3xl shadow-[0_50px_100px_rgba(0,0,0,0.5)] relative group/msg",
                      msg.sender === 'user'
                        ? "bg-white/[0.04] border-white/10 text-white"
                        : "bg-[#011412]/80 border-gold-primary/20 pb-20"
                    )}>
                    {renderMessageContent(msg)}

                    {msg.sender === 'ai' && (
                      <motion.div
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: lastAction === msg.id ? 1 : 0, y: lastAction === msg.id ? 0 : 5 }}
                        className="absolute bottom-6 right-10 flex items-center gap-3 bg-black/40 backdrop-blur-3xl rounded-full p-2 border border-white/5 shadow-2xl z-20"
                      >
                        <button
                          onClick={() => handleCopy(msg.text)}
                          className="w-10 h-10 rounded-full flex items-center justify-center text-white/30 hover:text-gold-primary hover:bg-gold-primary/10 transition-all"
                          title="Copy Full Knowledge"
                        >
                          <Copy size={16} />
                        </button>
                        <div className="w-[1px] h-4 bg-white/5" />
                        <button
                          onClick={() => handleShare(msg.text)}
                          className="w-10 h-10 rounded-full flex items-center justify-center text-white/30 hover:text-gold-primary hover:bg-gold-primary/10 transition-all"
                          title="Share Insight"
                        >
                          <Share2 size={16} />
                        </button>
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            {isTyping && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-start">
                <div className="bg-gold-primary/5 border border-gold-primary/20 rounded-[2rem] px-12 py-6 flex gap-6 items-center backdrop-blur-3xl shadow-[0_20px_40px_rgba(0,0,0,0.3)]">
                  <div className="flex gap-2">
                    {[0, 1, 2].map(i => (
                      <motion.div 
                        key={i} 
                        animate={{ 
                          scale: [1, 1.5, 1],
                          opacity: [0.3, 1, 0.3],
                          boxShadow: ["0 0 0px #E5C06F", "0 0 15px #E5C06F", "0 0 0px #E5C06F"]
                        }} 
                        transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.3, ease: "easeInOut" }} 
                        className="w-3 h-3 bg-gold-primary rounded-full" 
                      />
                    ))}
                  </div>
                  <span className="text-[13px] font-black text-gold-primary uppercase tracking-[0.5em] font-outfit">Consulting Scholarly Consensus...</span>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
          {/* Final Floating Input Pill with Suggestions */}
          <div className="absolute bottom-5 left-0 right-0 px-32 pointer-events-none">
            <div className="max-w-5xl mx-auto pointer-events-auto">
              {/* Interactive Suggestion Chips */}
              <AnimatePresence>
                {showSuggestions && !inputMessage && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="flex gap-4 mb-8 overflow-x-auto no-scrollbar pb-2"
                  >
                    {SUGGESTIONS.map((item, idx) => (
                      <motion.button
                        key={idx}
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleSendMessage(item.query)}
                        className="suggestion-chip flex items-center gap-3 shrink-0"
                      >
                        <item.icon size={16} />
                        {item.label}
                      </motion.button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="flex items-center bg-[#011412]/98 backdrop-blur-[100px] rounded-[3rem] h-28 px-10 border border-white/10 shadow-[0_80px_160px_rgba(0,0,0,0.95)] gap-8 transition-all hover:border-gold-primary/20 group/input">
                <button className="p-4 text-white/10 hover:text-gold-primary transition-all group-hover/input:text-white/20"><Paperclip size={26} /></button>
                <div className="relative flex-1 flex items-center h-full">
                  {!inputMessage && <PlaceholderRotator />}
                  <input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
                    className="w-full bg-transparent border-none outline-none text-2xl text-white font-medium z-10"
                  />
                </div>
                <div className="flex items-center gap-6 border-l border-white/5 pl-8 h-14">
                  <button className="p-4 text-white/10 hover:text-gold-primary transition-all group-hover/input:text-white/20"><Mic size={26} /></button>
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={!inputMessage.trim() || isTyping}
                    className={cn(
                      "w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-2xl",
                      inputMessage.trim() ? "bg-gold-primary text-black hover:scale-110 active:scale-95" : "bg-white/5 text-white/5"
                    )}
                  >
                    <Send size={24} fill={inputMessage.trim() ? "currentColor" : "none"} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-32 px-10 py-4 bg-gold-primary rounded-full text-black font-black uppercase tracking-widest text-xs shadow-2xl animate-bounce">
          {toast}
        </div>
      )}
    </div>
  );
};

export default IslamicAIAgent;

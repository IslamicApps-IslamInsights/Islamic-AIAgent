import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Star, MessageSquare,
  Mic, Paperclip, Moon, Book, Scroll, Sun,
  LayoutGrid, Share2, Copy, PanelLeft, MapPin, Compass,
  Play, Pause, X, Calendar, ArrowRight
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
    className="flex items-start gap-4 p-6 mb-3 rounded-[2rem] cursor-pointer transition-all border border-transparent hover:border-gold-primary/10 group overflow-hidden"
  >
    <div className="w-14 h-14 shrink-0 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center justify-center text-white/20 group-hover:text-gold-primary group-hover:bg-gold-primary/10 transition-all shadow-inner">
      <Icon size={24} />
    </div>
    <div className="flex flex-col space-y-2 min-w-0 flex-1 overflow-hidden">
      <h4 className="text-[15px] font-black text-white/90 group-hover:text-gold-primary transition-colors font-outfit text-wrap leading-snug">{title}</h4>
      <p className="text-[11px] text-white/20 leading-tight font-medium line-clamp-2 group-hover:text-white/40 transition-colors uppercase tracking-wider text-wrap">{desc}</p>
    </div>

  </motion.div>
);

const SanctuaryBackground = ({ isActive }: { isActive: boolean }) => (
  <div className={cn("absolute inset-0 z-0 overflow-hidden pointer-events-none transition-all duration-[3000ms]", isActive ? "opacity-100" : "opacity-0")}>
     <div className="absolute inset-0 bg-gradient-to-br from-[#011412] via-black to-[#011d1a]" />
     <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-gold-primary/10 blur-[150px] rounded-full animate-pulse-slow" />
     <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-gold-primary/5 blur-[200px] rounded-full animate-pulse-slow delay-1000" />
     <div className="absolute inset-0 opacity-[0.03] flex items-center justify-center">
        <NoorLogo size={800} className="scale-150 rotate-45 animate-spin-slow duration-[300s]" />
     </div>
  </div>
);

const ScholarlySkeleton = ({ height = 100 }: { height?: number }) => (
  <div className="w-full animate-pulse space-y-4 px-2">
    <div className="flex items-center gap-4">
      <div className="w-12 h-12 rounded-2xl bg-white/5" />
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-white/5 rounded-full w-3/4" />
        <div className="h-2 bg-white/5 rounded-full w-1/2 opacity-50" />
      </div>
    </div>
    <div className="grid grid-cols-2 gap-3 mt-4">
      <div className="h-12 bg-white/[0.03] rounded-xl border border-white/5" />
      <div className="h-12 bg-white/[0.03] rounded-xl border border-white/5" />
    </div>
  </div>
);

const ScholarEvidence = ({ type, translation, reference, apiUrl, onSelectReference }: { type: 'quran' | 'hadith', translation: string, reference: string, apiUrl: string, onSelectReference: (ref: string) => void }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const toggleAudio = async () => {
    if (isPlaying) {
      audioRef.current?.pause();
      setIsPlaying(false);
      return;
    }

    if (audioUrl) {
      audioRef.current?.play();
      setIsPlaying(true);
      return;
    }

    // Extract verse reference like "2:255" from "Quran 2:255"
    const versePart = reference.replace(/Quran\s+/i, "").trim();
    try {
      const res = await fetch(`${apiUrl}/api/quran/audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ verse: versePart })
      });
      const data = await res.json();
      if (data.audio_url) {
        setAudioUrl(data.audio_url);
        const audio = new Audio(data.audio_url);
        audioRef.current = audio;
        audio.onended = () => setIsPlaying(false);
        audio.play();
        setIsPlaying(true);
      }
    } catch (err) {
      console.error("Audio playback failed", err);
    }
  };

  return (
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
        <div className="flex items-center gap-4">
          {type === 'quran' && (
            <button
              onClick={toggleAudio}
              className={cn(
                "flex items-center gap-2 px-6 py-3 rounded-full border transition-all font-outfit text-[11px] font-black uppercase tracking-widest",
                isPlaying 
                  ? "bg-gold-primary text-black border-gold-primary shadow-[0_0_20px_rgba(229,192,111,0.5)]" 
                  : "bg-white/5 text-white/40 border-white/10 hover:border-gold-primary/40 hover:text-gold-primary"
              )}
            >
              {isPlaying ? <Pause size={12} fill="currentColor" /> : <Play size={12} fill="currentColor" />}
              {isPlaying ? 'Reciting...' : 'Listen to Verse'}
            </button>
          )}
            <div className="flex items-center gap-4 bg-white/5 px-6 py-3 rounded-full border border-white/10 group/ref relative">
            <button 
              onClick={() => onSelectReference(reference)}
              className="text-[12px] font-black text-white/40 tracking-[0.2em] font-inter hover:text-gold-primary transition-colors flex items-center gap-2"
            >
              [{reference}]
              <Scroll size={12} className="opacity-0 group-hover/ref:opacity-100 transition-opacity" />
            </button>
            <button 
              onClick={() => navigator.clipboard.writeText(reference)}
              className="ml-2 p-1 text-white/10 hover:text-gold-primary transition-colors"
              title="Copy Reference"
            >
              <Copy size={12} />
            </button>
          </div>
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
        {/* Simple Audio Wave Visualizer */}
        <AnimatePresence>
          {isPlaying && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 4, opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="absolute bottom-0 left-0 right-0 overflow-hidden flex items-end gap-[2px] px-10"
            >
              {[...Array(60)].map((_, i) => (
                <motion.div
                  key={i}
                  animate={{ height: [4, Math.random() * 20 + 4, 4] }}
                  transition={{ repeat: Infinity, duration: 0.5 + Math.random(), ease: "easeInOut" }}
                  className="flex-1 bg-gold-primary/40 rounded-t-full"
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

const IsnadChain = ({ reference, apiUrl, onClose }: { reference: string, apiUrl: string, onClose: () => void }) => {
  const [chain, setChain] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIsnad = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/hadith/isnad`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reference })
        });
        const data = await res.json();
        if (data.isnad) setChain(data.isnad);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    fetchIsnad();
  }, [reference]);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-0 z-[100] flex items-center justify-center p-12 bg-black/60 backdrop-blur-3xl"
    >
      <div className="bg-[#011412] border border-gold-primary/30 rounded-[4rem] w-full max-w-4xl max-h-[80vh] overflow-hidden flex flex-col shadow-[0_100px_200px_rgba(0,0,0,0.8)]">
        <div className="p-12 border-b border-white/5 flex justify-between items-center bg-gold-primary/[0.02]">
          <div>
            <h3 className="text-3xl font-black text-white font-outfit uppercase tracking-tighter">Scholarly Isnad (Chain)</h3>
            <p className="text-gold-primary/60 text-[12px] font-bold uppercase tracking-[0.4em] mt-2">Authenticity Transmission for [{reference}]</p>
          </div>
          <button onClick={onClose} className="p-4 rounded-full bg-white/5 text-white/40 hover:text-white transition-all">
            <X size={24} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto no-scrollbar p-16 space-y-0 relative">
          {/* Timeline Line */}
          <div className="absolute left-24 top-24 bottom-24 w-[2px] bg-gradient-to-b from-gold-primary/40 via-gold-primary/10 to-transparent shadow-[0_0_10px_rgba(229,192,111,0.2)]" />
          
          {loading ? (
             <div className="flex flex-col items-center justify-center h-64 space-y-6">
                <div className="w-12 h-12 border-4 border-gold-primary/20 border-t-gold-primary rounded-full animate-spin" />
                <span className="text-gold-primary/40 text-[11px] font-black uppercase tracking-widest">Verifying Chains...</span>
             </div>
          ) : chain.map((narrator, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="relative pl-32 pb-20 last:pb-0 group"
            >
              {/* Dot */}
              <div className="absolute left-[89px] top-2 w-4 h-4 rounded-full bg-[#011412] border-2 border-gold-primary group-hover:scale-150 transition-transform shadow-[0_0_10px_rgba(229,192,111,0.5)] z-10" />
              
              <div className="bg-white/[0.02] border border-white/5 p-8 rounded-[2.5rem] group-hover:border-gold-primary/30 transition-all">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-[20px] font-black text-white/90 group-hover:text-gold-primary transition-colors font-outfit">{narrator.name}</h4>
                    <p className="text-gold-primary/40 text-[10px] font-black uppercase tracking-widest mt-1">{narrator.role}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-white/20 text-[11px] font-bold uppercase tracking-widest bg-white/5 px-4 py-1 rounded-full">{narrator.period}</span>
                    <p className="text-white/10 text-[9px] font-bold uppercase tracking-widest mt-2">{narrator.location}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
        
        <div className="p-10 bg-gold-primary/[0.05] text-center border-t border-white/5">
          <p className="text-gold-primary/30 text-[10px] font-black uppercase tracking-[0.4em]">Integrated authentication from primary scholarly databases</p>
        </div>
      </div>
    </motion.div>
  );
};

const ScholarDeepDive = ({ msg, renderContent, onClose }: { msg: Message, renderContent: (m: Message, full?: boolean) => any, onClose: () => void }) => {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[150] flex items-center justify-center p-20 bg-black/80 backdrop-blur-[100px]"
    >
      <motion.div 
        initial={{ y: 50, scale: 0.95 }}
        animate={{ y: 0, scale: 1 }}
        exit={{ y: 50, scale: 0.95 }}
        className="w-full max-w-7xl h-full max-h-[90vh] bg-[#011412] border border-gold-primary/30 rounded-[5rem] flex flex-col overflow-hidden shadow-[0_150px_300px_rgba(0,0,0,0.95)]"
      >
        <div className="h-32 px-20 border-b border-white/5 flex items-center justify-between bg-gold-primary/[0.03]">
          <div className="flex items-center gap-8">
            <div className="w-16 h-16 rounded-[1.5rem] bg-gold-primary/20 flex items-center justify-center text-gold-primary">
              <NoorLogo size={32} />
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-black text-white uppercase tracking-tighter">Scholarly Deep Dive</span>
              <span className="text-[11px] font-bold text-gold-primary/60 uppercase tracking-[0.4em] mt-1">Full Authenticated Knowledge Scroll</span>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="w-16 h-16 rounded-full flex items-center justify-center bg-white/5 text-white/40 hover:text-white hover:bg-white/10 transition-all border border-white/10"
          >
            <X size={28} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto no-scrollbar px-32 py-24 bg-gradient-to-b from-transparent to-black/20">
           <div className="max-w-5xl mx-auto">
              <div className="mb-20 flex items-center gap-6 opacity-40">
                <div className="h-[2px] flex-1 bg-gradient-to-r from-transparent to-gold-primary/30" />
                <span className="text-[12px] font-black uppercase tracking-[0.6em]">Beginning of Scholarly Consensus</span>
                <div className="h-[2px] flex-1 bg-gradient-to-l from-transparent to-gold-primary/30" />
              </div>
              
              {renderContent(msg, true)}
              
              <div className="mt-40 border-t border-gold-primary/10 pt-16 flex flex-col items-center text-center opacity-40 italic">
                 <p className="text-[14px] text-white/60">This scholarly scroll has been synthesized with verified sources from the Quran, authentic Hadith chains (Isnad), and classical Fiqh consensus.</p>
                 <span className="text-[11px] uppercase tracking-[0.8em] mt-6">Knowledge is Light</span>
              </div>
           </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai' | 'agent';
  timestamp: Date;
  thoughts?: string;
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

const QiblaCompass = ({ bearing, direction }: { bearing: number, direction: string }) => {
  return (
    <div className="relative w-32 h-32 flex items-center justify-center">
      {/* Outer Glow & Atmosphere */}
      <div className="absolute inset-[-10%] bg-gold-primary/5 blur-2xl rounded-full animate-pulse-slow" />
      
      {/* Compass Face */}
      <div className="absolute inset-0 rounded-full border border-white/10 bg-black/40 shadow-inner overflow-hidden">
        {/* Degree Markers (30 degree steps) */}
        {[...Array(12)].map((_, i) => (
          <div 
            key={i} 
            className="absolute inset-0 flex flex-col items-center pt-1"
            style={{ transform: `rotate(${i * 30}deg)` }}
          >
            <div className={cn("w-[2px] h-2 rounded-full", i % 3 === 0 ? "bg-gold-primary/40 h-3" : "bg-white/10")} />
            {i % 3 === 0 && (
              <span className="text-[7px] font-black text-white/20 mt-1 uppercase tracking-tighter">
                {['N', 'E', 'S', 'W'][i / 3]}
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Rotating High-Fidelity Needle Layer */}
      <motion.div 
        animate={{ rotate: bearing }}
        transition={{ type: "spring", stiffness: 40, damping: 15 }}
        className="absolute inset-0 z-10 flex items-center justify-center"
      >
        {/* The Qibla Needle */}
        <div className="relative w-full h-full flex items-center justify-center">
          {/* Top Pointer (Gold Gradient) */}
          <div className="absolute top-[10%] w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-b-[40px] border-b-gold-primary filter drop-shadow-[0_0_8px_rgba(229,192,111,0.5)]" />
          {/* Bottom Pointer (Darker) */}
          <div className="absolute bottom-[10%] w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[40px] border-t-white/10" />
          
          {/* Center Point */}
          <div className="w-3 h-3 rounded-full bg-gold-primary border-2 border-[#011412] z-20 shadow-[0_0_10px_rgba(229,192,111,0.8)]" />
          
          {/* Target Kaaba Icon */}
          <motion.div 
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute top-[2%] bg-black border border-gold-primary/40 p-1 rounded-sm shadow-xl"
            title="Holy Kaaba Direction"
          >
            <div className="w-3 h-3 bg-black border-[0.5px] border-gold-primary/30 relative">
               <div className="absolute top-0 left-0 right-0 h-[1px] bg-gold-primary/60" />
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Outer Compass Decoration */}
      <div className="absolute inset-[-5%] border-[0.5px] border-gold-primary/10 rounded-full pointer-events-none" />
    </div>
  );
};

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

const IslamicAIAgent = ({ isWidget = false, apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5010' }) => {
  // Initialize messages from LocalStorage if available
  const [messages, setMessages] = useState<Message[]>(() => {
    const normalizeText = (value: any): string => {
      if (typeof value === 'string') return value;
      if (value === null || value === undefined) return '';
      if (typeof value === 'object') {
        try {
          return JSON.stringify(value, null, 2);
        } catch {
          return String(value);
        }
      }
      return String(value);
    };

    const saved = localStorage.getItem('noor_scholar_history');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
            return parsed.map((m: any) => ({
              ...m,
              text: normalizeText(m?.text),
              timestamp: new Date(m.timestamp)
            }));
        }
      } catch (e) { console.error("History revival failed", e); }
    }
    return [
      {
        id: 1,
        text: "As-Salaam Alaykum. I am Noor, your scholarly companion. How may I assist you today in your journey of knowledge?",
        sender: 'ai',
        timestamp: new Date()
      }
    ];
  });

  // Persist messages whenever they change
  useEffect(() => {
    if (messages) {
        localStorage.setItem('noor_scholar_history', JSON.stringify(messages));
    }
  }, [messages]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [gender] = useState<'male' | 'female' | 'not_specified'>('not_specified');
  const [toast, setToast] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<number | null>(null);
  const [selectedReference, setSelectedReference] = useState<string | null>(null);
  const [quranTranslationLang, setQuranTranslationLang] = useState<string>('en');
  const [quranTranslationLanguages, setQuranTranslationLanguages] = useState<Array<{ code: string; edition_count: number }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [isSystemInitializing, setIsSystemInitializing] = useState(true);
  const [initializationRetry, setInitializationRetry] = useState(0);
  
  // Real-time Islamic Data State
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [prayerTimes, setPrayerTimes] = useState<any>(null);
  const [qibla, setQibla] = useState<any>(null);
  const [isLoadingIslamicData, setIsLoadingIslamicData] = useState(false);
  const [calendarData, setCalendarData] = useState<any>(null);
  const [isTimelineOpen, setIsTimelineOpen] = useState(false);
  const [isAgentInitializing, setIsAgentInitializing] = useState(false);
  const [deepDiveMessage, setDeepDiveMessage] = useState<Message | null>(null);
  const [expandedThoughts, setExpandedThoughts] = useState<Record<number, boolean>>({});
  const [expandedMessages, setExpandedMessages] = useState<Record<number, boolean>>({});
  const [pageState, setPageState] = useState<Record<number, number>>({}); // blocks shown per message
  const [scholarlyStatus, setScholarlyStatus] = useState("Consulting Scholarly Consensus...");
  
  // Sanctuary & Atmosphere State
  const [isAmbiencePlaying, setIsAmbiencePlaying] = useState(false);
  const ambientAudioRef = useRef<HTMLAudioElement | null>(null);
  const [pulseIntensity, setPulseIntensity] = useState(0);
  const [isDemoMode, setIsDemoMode] = useState(true); // Forced Local Mode for Pitch

  // --- Resilience Engine Mapping ---
  // If the last message contains the "locally generated" marker, we show Local Resilient status
  const lastMsg = messages && messages.length > 0 ? messages[messages.length - 1] : null;
  const lastMsgText = typeof lastMsg?.text === 'string' ? lastMsg.text : '';
  const isLastLocal = lastMsgText.includes("locally generated locally");
  const engineStatus = isDemoMode ? "Local Mode (Pitch)" : (isLastLocal ? "Local Resilient" : "Cloud Enhanced");
  const engineColor = isDemoMode ? "text-orange-400" : (isLastLocal ? "text-gold-primary" : "text-emerald-400");
  const engineBg = isDemoMode ? "bg-orange-400/10" : (isLastLocal ? "bg-gold-primary/10" : "bg-emerald-400/10");
  const engineBorder = isDemoMode ? "border-orange-400/20" : (isLastLocal ? "border-gold-primary/20" : "border-emerald-400/20");
  const quranLangOptions = Array.from(new Set([
    'auto',
    'en',
    'ur',
    'ar',
    ...quranTranslationLanguages.map(x => x.code)
  ].filter(Boolean)));

  // Attachment & Voice State
  const supportsAttachments = false;
  const supportsVoice = false;
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [isRecording, setIsRecording] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${apiUrl}/api/quran/translation-languages`, {
          signal: AbortSignal.timeout(5000)
        });
        if (!res.ok) return;
        const data = await res.json();
        const langs = Array.isArray(data?.languages) ? data.languages : [];
        const normalized = langs
          .filter((x: any) => typeof x?.code === 'string')
          .map((x: any) => ({
            code: String(x.code).toLowerCase(),
            edition_count: Number(x.edition_count || x.editionCount || 0)
          }));
        if (!cancelled) setQuranTranslationLanguages(normalized);
        if (!cancelled && typeof data?.default === 'string' && data.default) {
          setQuranTranslationLang(String(data.default).toLowerCase());
        }
      } catch {
        if (!cancelled) setQuranTranslationLanguages([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [apiUrl]);

  const toggleAmbience = () => {
    if (!ambientAudioRef.current) {
      ambientAudioRef.current = new Audio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'); // Fallback placeholder
      ambientAudioRef.current.loop = true;
      ambientAudioRef.current.volume = 0.15;
    }
    
    if (isAmbiencePlaying) {
      ambientAudioRef.current.pause();
    } else {
      ambientAudioRef.current.play();
    }
    setIsAmbiencePlaying(!isAmbiencePlaying);
    showToast(isAmbiencePlaying ? "Sanctuary Ambience Silenced 🤲" : "Sanctuary Ambience Active 🍃");
  };

  useEffect(() => {
    // 🎭 Scholarly Status Rotator during isTyping
    if (isTyping) {
      const statuses = [
        "Retrieving authentic manuscripts...",
        "Querying the local knowledge base...",
        "Consulting scholarly consensus...",
        "Synthesizing Prophetic wisdom...",
        "Deliberating on Fiqh complexities...",
        "Verifying Isnad authenticity..."
      ];
      let i = 0;
      const interval = setInterval(() => {
        setScholarlyStatus(statuses[i % statuses.length]);
        i++;
      }, 2500);
      return () => clearInterval(interval);
    } else {
      setScholarlyStatus("Consulting Scholarly Consensus...");
    }
  }, [isTyping]);

  useEffect(() => {
    // Prayer Pulse Simulation
    const interval = setInterval(() => {
      // Calculate minutes until next prayer... (simplified logic)
      setPulseIntensity(prev => (prev + 0.05) % 1);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

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

  useEffect(() => {
    // System initialization check on mount
    const initializeSystem = async () => {
      let retries = 0;
      const maxRetries = 5;
      
      const attemptConnection = async () => {
        try {
          setInitializationRetry(retries + 1);
          
          // Check backend health
          const healthCheck = await fetch(`${apiUrl}/api/health`, { 
            signal: AbortSignal.timeout(3000) 
          }).catch(() => null);
          
          if (healthCheck && healthCheck.ok) {
            // Backend is healthy - dismiss initialization
            setIsSystemInitializing(false);
            return true;
          } else {
            // Backend not responding, retry
            retries++;
            if (retries >= maxRetries) {
              console.warn("Max retries reached. Backend may not be running.");
              showToast(`❌ Cannot connect to backend at ${apiUrl}\n💻 Start: python3 backend/api/web_api.py`);
              setIsSystemInitializing(false);
              return false;
            }
            
            // Wait before retrying (exponential backoff)
            await new Promise(resolve => setTimeout(resolve, 1000 * retries));
            return attemptConnection();
          }
        } catch (error) {
          console.error("System initialization check failed:", error);
          retries++;
          if (retries >= maxRetries) {
            showToast(`❌ Failed to initialize: ${error}`);
            setIsSystemInitializing(false);
            return false;
          }
          await new Promise(resolve => setTimeout(resolve, 1000 * retries));
          return attemptConnection();
        }
      };

      await attemptConnection();
    };

    initializeSystem();
  }, [apiUrl]);

  const fetchIslamicData = async (loc: { lat: number, lng: number }) => {
    setIsLoadingIslamicData(true);
    try {
      // Verify backend is reachable
      const healthCheck = await fetch(`${apiUrl}/api/health`, { 
        signal: AbortSignal.timeout(3000) 
      }).catch(() => null);
      
      if (!healthCheck) {
        console.warn("Backend not reachable at", apiUrl);
        showToast(`⚠️ Backend unavailable at ${apiUrl}. Please start: python3 backend/api/web_api.py`);
        setIsLoadingIslamicData(false);
        return;
      }

      // Fetch Prayer Times
      const pRes = await fetch(`${apiUrl}/api/prayer-times`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: loc.lat, longitude: loc.lng }),
        signal: AbortSignal.timeout(5000)
      });
      
      if (!pRes.ok) throw new Error(`Prayer times failed: ${pRes.status}`);
      const pData = await pRes.json();
      setPrayerTimes(pData.data || pData.prayer_times);

      // Fetch Qibla
      const qRes = await fetch(`${apiUrl}/api/qibla`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: loc.lat, longitude: loc.lng }),
        signal: AbortSignal.timeout(5000)
      });
      
      if (!qRes.ok) throw new Error(`Qibla failed: ${qRes.status}`);
      const qData = await qRes.json();
      setQibla(qData);

      // Fetch Calendar Grid
      const cRes = await fetch(`${apiUrl}/api/calendar`, {
        signal: AbortSignal.timeout(5000)
      });
      
      if (!cRes.ok) throw new Error(`Calendar failed: ${cRes.status}`);
      const cData = await cRes.json();
      setCalendarData(cData);
    } catch (error: any) {
      const errMsg = error?.message || error?.toString() || "Unknown error";
      console.error("Failed to fetch Islamic data:", errMsg);
      
      if (errMsg.includes("timeout")) {
        showToast("⏱️ Request timeout - Backend may be slow");
      } else if (errMsg.includes("Failed to fetch")) {
        showToast(`🔌 Cannot connect to backend at ${apiUrl}`);
      } else {
        showToast(`❌ Islamic data error: ${errMsg.substring(0, 40)}`);
      }
    } finally {
      setIsLoadingIslamicData(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!supportsAttachments) {
      showToast("File upload is disabled in local-only mode ⚠️");
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      showToast("File too large (max 5MB) ⚠️");
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target?.result as string;
      setSelectedFile({
        data: base64.split(',')[1],
        type: file.type,
        name: file.name
      });
      showToast("Document Attached 📎");
    };
    reader.readAsDataURL(file);
  };

  const toggleRecording = async () => {
    if (!supportsVoice) {
      showToast("Voice input is disabled in local-only mode ⚠️");
      return;
    }
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          const reader = new FileReader();
          reader.onload = async (e) => {
            const base64Audio = (e.target?.result as string).split(',')[1];
            processSTT(base64Audio);
          };
          reader.readAsDataURL(audioBlob);
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
        showToast("Listening for your question... 🎤");
      } catch (err) {
        showToast("Microphone access denied ⚠️");
      }
    }
  };

  const processSTT = async (base64Audio: string) => {
    if (!supportsVoice) {
      showToast("Voice input is disabled in local-only mode ⚠️");
      return;
    }
    setIsTyping(true);
    try {
      const response = await fetch(`${apiUrl}/api/stt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio: base64Audio })
      });
      if (response.status === 400) {
        showToast("Voice input is disabled in local-only mode ⚠️");
        return;
      }
      const data = await response.json();
      if (data.transcription) {
        setInputMessage(data.transcription);
        showToast("Transcribed! Review & Send 📝");
      }
    } catch (err) {
      showToast("Transcription failed ⚠️");
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = async (text?: string) => {
    const textToSend = (text || inputMessage).trim();
    if (!textToSend && !selectedFile && !isTyping) return;

    const userMsg: Message = { 
      id: Date.now(), 
      text: textToSend || (selectedFile ? `[Sent Attachment: ${selectedFile.name}]` : ""), 
      sender: 'user', 
      timestamp: new Date() 
    };
    
    setMessages(prev => [...prev, userMsg]);
    if (!text) setInputMessage('');
    setIsTyping(true);
    setIsAgentInitializing(false);

    try {
      const endpoint = selectedFile ? `${apiUrl}/api/chat/multimodal` : `${apiUrl}/api/chat`;
      const body = {
        message: textToSend,
        user_gender: gender,
        latitude: location?.lat,
        longitude: location?.lng
      };

      if (selectedFile) {
        (body as any).file = selectedFile.data;
        (body as any).mime_type = selectedFile.type;
        setSelectedFile(null);
      }

      // Verify backend is reachable
      const healthCheck = await fetch(`${apiUrl}/api/health`, {
        signal: AbortSignal.timeout(2000)
      }).catch(() => null);

      if (!healthCheck) {
        throw new Error(`BACKEND_NOT_REACHABLE: ${apiUrl}/api/health`);
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...body,
          quran_translation_lang: quranTranslationLang,
          include_thoughts: true,
          use_synthesis: true  // Enable scholarly formatting
        }),
        signal: AbortSignal.timeout(180000)
      });

      if (response.status === 503) {
        setIsAgentInitializing(true);
        const data = await response.json();
        throw new Error(data.error || 'Service initializing');
      }

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(`API error ${response.status}: ${errData.error || response.statusText}`);
      }

      const data = await response.json();

      const aiMsg: Message = { 
        id: Date.now() + 1, 
        text: typeof data.response === 'string' ? data.response : JSON.stringify(data.response, null, 2), 
        sender: 'ai', 
        timestamp: new Date(),
        thoughts: data.thoughts
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error: any) {
      const errMsg = error?.message || error?.toString() || "Unknown error";
      console.error('Chat error:', errMsg);

      if (errMsg.includes('BACKEND_NOT_REACHABLE')) {
        showToast(`🔌 Backend not running at ${apiUrl}\n💻 Start: python3 backend/api/web_api.py`);
      } else if (errMsg.includes('timeout')) {
        showToast("⏱️ Request timeout - Backend may be processing");
      } else if (errMsg.includes('Failed to fetch')) {
        showToast(`❌ Network error - Cannot connect to ${apiUrl}`);
      } else if (errMsg.includes('initializing')) {
        showToast("📚 Scholars are preparing the library...");
        setIsAgentInitializing(true);
      } else if (errMsg.includes('API error')) {
        showToast(`❌ Backend error: ${errMsg.substring(0, 50)}...`);
      } else {
        showToast(`❌ Error: ${errMsg.substring(0, 50)}...`);
      }
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

  const renderMessageContent = (msg: Message, forceFull = false, showLoadMore = true) => {
    const isAI = msg.sender === 'ai' || msg.sender === 'agent';
    const text = msg.text;

    if (isAI) {
      // Enhanced regex to match broader scholarly formats like [The Holy Quran 17:78] or [Sahih Bukhari 123]
      const quranRegex = /\[(?:The\s+Holy\s+)?Quran\s*(?:\([^)]*\))?\s*(\d+:\d+)\]/i;
      const hadithRegex = /\[(?:Sahih\s+|Sunan\s+|Jami`?\s+|Muwatta\s+)?(Bukhari|Muslim|Hadith|Tirmidhi|Dawud|Nasa'i|Majah|Malik|Nawawi)\s*(?:\([^)]*\))?\s*(?:Hadith\s+)?#?(\d+)\]/i;

      // Split into blocks for pagination
      const allBlocks = text.split('\n\n').filter((b: string) => b.trim());
      const isExpanded = expandedMessages[msg.id] || forceFull;
      const blocksToShow = isExpanded ? allBlocks.length : Math.min(3, allBlocks.length);
      const displayBlocks = allBlocks.slice(0, blocksToShow);

      return (
        <div className="space-y-12 relative">
          {displayBlocks.map((block: string, i: number) => {
            // Case 1: Scholar Evidence (Quran/Hadith)
            if (quranRegex.test(block)) {
              const match = block.match(quranRegex);
              return <ScholarEvidence key={i} type="quran" translation={block.replace(quranRegex, "").trim()} reference={`Quran ${match![1]}`} apiUrl={apiUrl} onSelectReference={setSelectedReference} />;
            }
            if (hadithRegex.test(block)) {
              const match = block.match(hadithRegex);
              return <ScholarEvidence key={i} type="hadith" translation={block.replace(hadithRegex, "").trim()} reference={`${match![1]} ${match![2]}`} apiUrl={apiUrl} onSelectReference={setSelectedReference} />;
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
                <p key={idx} className={cn(
                  "text-white/90 leading-[2.2] font-medium tracking-tight mb-6 last:mb-0 antialiased",
                  forceFull ? "text-[28px]" : "text-[20px]"
                )}>
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

          {/* Load More Button for Large Responses */}
          {showLoadMore && !isExpanded && allBlocks.length > 3 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-12 flex justify-center"
            >
              <button
                onClick={() => setExpandedMessages(prev => ({ ...prev, [msg.id]: true }))}
                className="px-8 py-4 bg-gold-primary/20 hover:bg-gold-primary/30 border border-gold-primary/40 hover:border-gold-primary/60 rounded-full text-gold-primary font-black uppercase tracking-[0.4em] text-[11px] transition-all shadow-[0_0_20px_rgba(229,192,111,0.1)] hover:shadow-[0_0_30px_rgba(229,192,111,0.2)]"
              >
                📖 Load More Results ({allBlocks.length - blocksToShow} remaining)
              </button>
            </motion.div>
          )}
        </div>
      );
    }
    return <div className="text-[18px] font-semibold text-white/95 leading-relaxed">{text}</div>;
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden flex flex-col items-center justify-center p-12 bg-[#011412]">
      <SanctuaryBackground isActive={isAmbiencePlaying} />
      
      {/* High-Fidelity Realistic Background */}
      <div className={cn("absolute inset-0 z-0 pointer-events-none transition-opacity duration-[2000ms]", isAmbiencePlaying ? "opacity-30" : "opacity-100")}>
        <img
          src="/background-premium.png"
          alt="Noor AI Islamic Agent"
          className="w-full h-full object-cover mix-blend-screen opacity-100"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#011412]/60 via-transparent to-[#011412]/30" />

      </div>

      {/* Main Scholarly Station */}
      <div className="flex w-full h-[90vh] max-w-[1780px] bg-[#011412]/85 backdrop-blur-[80px] rounded-[4rem] border border-white/5 overflow-hidden shadow-[0_120px_240px_rgba(0,0,0,0.98)] transition-all relative z-10">

        {/* Drawer Backdrop Overlay */}
        <AnimatePresence>
          {isSidebarOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              onClick={() => setIsSidebarOpen(false)}
              className="absolute inset-0 z-30 bg-black/60 backdrop-blur-sm rounded-[4rem] cursor-pointer"
            />
          )}
        </AnimatePresence>

        {/* Drawer Menu Sidebar */}
        <motion.div
          animate={{
            x: isSidebarOpen ? 0 : -440,
            opacity: isSidebarOpen ? 1 : 0
          }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="absolute left-0 top-0 bottom-0 w-[400px] h-full bg-black/40 backdrop-blur-[40px] border-r border-white/5 overflow-hidden z-40 rounded-l-[4rem]"
        >
          <div className="w-[400px] flex flex-col px-8 pt-16 pb-12 h-full">
            <div className="flex items-center gap-4 mb-16 pl-2">
              <NoorLogo size={38} />
              <div className="flex flex-col min-w-0">
                <span className="text-[16px] font-black text-white tracking-[0.3em] font-outfit uppercase truncate">Noor</span>
                <span className="text-[9px] font-bold text-white/20 tracking-[0.6em] uppercase">Islamic AI</span>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto no-scrollbar pr-2">
              <SidebarCard icon={Star} title="Islam & Moral Character" desc="WHAT DOES ISLAM TEACH ABOUT MORAL CHARACTER AND DAILY CONDUCT?" onClick={() => { handleSendMessage("What does Islam teach about moral character and how should a Muslim conduct themselves in daily life?"); setIsSidebarOpen(false); }} />
              <SidebarCard icon={LayoutGrid} title="The Five Pillars" desc="EXPLAIN THE FIVE PILLARS AND WHY THEY ARE OBLIGATORY FOR EVERY MUSLIM" onClick={() => { handleSendMessage("Explain the five pillars of Islam and why they are considered obligatory for every Muslim."); setIsSidebarOpen(false); }} />
              <SidebarCard icon={Moon} title="Ramadan Essentials" desc="SIGNIFICANCE OF RAMADAN & FAST PROTOCOLS" onClick={() => { handleSendMessage("Tell me about Ramadan significance"); setIsSidebarOpen(false); }} />
              <SidebarCard icon={Sun} title="Daily Dua & Dhikr" desc="PROPHETIC SUPPLICATIONS FOR HEART PURITY" onClick={() => { handleSendMessage("What are the best daily duas?"); setIsSidebarOpen(false); }} />
              <SidebarCard icon={Book} title="Hadith Collections" desc="AUTHENTIC CHAINS FROM THE NINE BOOKS" onClick={() => { handleSendMessage("How are Hadiths authenticated?"); setIsSidebarOpen(false); }} />
              <SidebarCard icon={Scroll} title="Quran Tafseer" desc="CLASSICAL EXEGESIS & SCHOLARLY INSIGHTS" onClick={() => { handleSendMessage("Tell me about Quranic interpretation"); setIsSidebarOpen(false); }} />

              {/* Real-time Islamic Widgets */}
              <div className="mt-12 space-y-6">
                <div className="px-6 py-2">
                  <span className="text-[10px] font-black text-gold-primary/40 tracking-[0.5em] uppercase">Real-time Sacred Data</span>
                </div>
                
                {/* Prayer Times Widget */}
                <motion.div 
                  whileHover={{ scale: 1.01 }}
                  className="bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-8 mx-2 shadow-xl"
                >
                  {isLoadingIslamicData ? (
                    <ScholarlySkeleton />
                  ) : prayerTimes ? (
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(prayerTimes.timings || {}).filter(([k]) => ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'].includes(k)).map(([name, time]: [any, any]) => (
                        <div key={name} className="flex flex-col p-3 bg-white/[0.03] rounded-xl border border-white/5">
                          <span className="text-[9px] font-black text-white/30 uppercase tracking-widest">{name}</span>
                          <span className="text-[14px] font-bold text-gold-primary">{time}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-6 space-y-3">
                       <MapPin size={24} className="text-white/10" />
                       <div className="text-[11px] text-white/20 uppercase tracking-widest font-bold">Location data unavailable</div>
                       <button onClick={() => window.location.reload()} className="text-[9px] text-gold-primary font-black uppercase underline tracking-widest">Retry Access</button>
                    </div>
                  )}
                </motion.div>

                {/* Qibla Direction Widget */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-8 mx-2 flex items-center gap-8 shadow-xl"
                >
                  {isLoadingIslamicData ? (
                     <div className="flex items-center gap-6 w-full">
                        <div className="w-16 h-16 rounded-full bg-white/5 animate-pulse" />
                        <div className="flex-1 h-12 bg-white/5 rounded-2xl animate-pulse" />
                     </div>
                  ) : qibla?.bearing ? (
                    <>
                      <QiblaCompass bearing={qibla?.bearing || 0} direction={qibla?.direction || ''} />
                      <div className="flex flex-col">
                        <span className="text-[14px] font-black text-white/90 font-outfit uppercase tracking-wider">Qibla Direction</span>
                        <div className="flex items-baseline gap-2">
                           <span className="text-[20px] font-black text-gold-primary tracking-tighter">
                            {qibla.bearing.toFixed(1)}°
                           </span>
                           <span className="text-[12px] font-bold text-white/40 uppercase tracking-widest">{qibla.direction}</span>
                        </div>
                        <span className="text-[9px] font-bold text-gold-primary/40 uppercase tracking-[0.2em] mt-1">Facing Holy Kaaba (Makkah)</span>
                      </div>
                    </>
                  ) : (
                    <div className="flex-1 text-[11px] text-white/20 font-bold uppercase tracking-widest text-center py-4">
                      Qibla vision pending...
                    </div>
                  )}
                </motion.div>

                {/* Hijri Vision Interactive Timeline Trigger */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  onClick={() => { setIsTimelineOpen(true); setIsSidebarOpen(false); }}
                  className="bg-gold-primary/10 border border-gold-primary/30 rounded-[2.5rem] p-8 mx-2 mt-4 cursor-pointer group relative overflow-hidden"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6">
                      <div className="w-12 h-12 rounded-2xl bg-gold-primary/20 flex items-center justify-center text-gold-primary">
                        <Calendar size={24} />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[14px] font-black text-white/90 font-outfit uppercase tracking-wider">Hijri Vision</span>
                        <span className="text-[10px] font-bold text-gold-primary/60 uppercase tracking-widest">Interactive Sacred Timeline</span>
                      </div>
                    </div>
                    <ArrowRight size={20} className="text-gold-primary group-hover:translate-x-2 transition-transform" />
                  </div>
                </motion.div>
              </div>
          </div>
        </div>
      </motion.div>

        {/* Chat Sanctuary Area */}
        <div className="flex-1 flex flex-col relative bg-gradient-to-br from-white/[0.015] via-white/[0.005] to-transparent w-full">
          {/* Elegant Top Header */}
          <div className="h-28 flex items-center justify-between px-20 border-b border-white/5 bg-gradient-to-b from-white/[0.02] to-white/[0.005]">
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
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-black text-white tracking-tight uppercase font-outfit">Noor Islamic Agent</span>
                  {/* Scholarly Engine Status Badge */}
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className={cn("px-4 py-1.5 rounded-full border flex items-center gap-2", engineBg, engineBorder)}
                  >
                    <div className={cn("w-2 h-2 rounded-full animate-pulse", engineColor.replace('text', 'bg'))} />
                    <span className={cn("text-[8px] font-black uppercase tracking-[0.4em]", engineColor)}>
                      {engineStatus}
                    </span>
                  </motion.div>
                </div>
                <span className="text-[11px] font-bold text-white/30 tracking-[0.4em] uppercase">Scholarly Assistant Authority (RAG 2.0)</span>
              </div>
            </div>

            <div className="flex items-center gap-8">
              {/* Note: Prayer Pulse and Ambience Toggle removed per user request for clean UI */}

              <div className="flex items-center gap-4">
                {/* Resilience Demo Toggle (Hidden/Subtle for Pitch) */}
                <button 
                  onClick={async () => {
                    const newMode = !isDemoMode;
                    setIsDemoMode(newMode);
                    try {
                      await fetch(`${apiUrl}/api/demo/toggle`, { method: 'POST' });
                      setToast(newMode ? "🛡️ Local Resilience Mode Active" : "🌐 Cloud Synthesis Active");
                    } catch (e) {}
                  }}
                  className={cn(
                    "w-12 h-12 rounded-full flex items-center justify-center transition-all border",
                    isDemoMode ? "bg-orange-400/20 border-orange-400 text-orange-400 shadow-[0_0_20px_rgba(251,146,60,0.3)]" : "bg-white/5 border-white/10 text-white/20 hover:text-white"
                  )}
                  title="Toggle Local Resilience Mode (Demo)"
                >
                  <Sun size={18} className={cn(isDemoMode && "animate-spin-slow")} />
                </button>
              </div>

              <span className="font-amiri text-white text-3xl tracking-widest select-none drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</span>
            </div>
          </div>

          <AnimatePresence>
            {selectedReference && (
              <IsnadChain 
                reference={selectedReference} 
                apiUrl={apiUrl} 
                onClose={() => setSelectedReference(null)} 
              />
            )}
          </AnimatePresence>

          <AnimatePresence>
            {deepDiveMessage && (
              <ScholarDeepDive 
                msg={deepDiveMessage} 
                renderContent={renderMessageContent}
                onClose={() => setDeepDiveMessage(null)} 
              />
            )}
          </AnimatePresence>

          {/* Messages Sanctuary */}
          <div className="flex-1 overflow-y-auto no-scrollbar px-20 py-12 space-y-3 pb-96" ref={chatContainerRef}>
            {messages.length === 1 && !isTyping && (
              <div className="flex-1 flex items-center justify-center">
                <SanctuaryGreeting onSuggestionClick={(q) => {
                  setInputMessage(q);
                  handleSendMessage(q);
                }} />
              </div>
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
                      "w-full max-w-4xl p-12 rounded-3xl border transition-all duration-500 backdrop-blur-2xl relative group/msg",
                      msg.sender === 'user'
                        ? "bg-gradient-to-br from-white/[0.08] to-white/[0.03] border-white/20 text-white ml-auto shadow-[0_10px_30px_rgba(0,0,0,0.2)] hover:shadow-[0_15px_40px_rgba(0,0,0,0.3)]"
                        : "bg-gradient-to-br from-[#011412]/80 to-[#0a1a17]/60 border-gold-primary/30 pb-16 shadow-[0_20px_50px_rgba(0,0,0,0.4)] hover:shadow-[0_25px_60px_rgba(0,0,0,0.5)] hover:border-gold-primary/50"
                    )}>
                    {renderMessageContent(msg)}

                    {msg.sender === 'ai' && (
                      <div className="mt-8 space-y-4">
                        {msg.thoughts && (
                          <div className="px-6">
                            <button
                              onClick={() => setExpandedThoughts(prev => ({ ...prev, [msg.id]: !prev[msg.id] }))}
                              className={cn(
                                "flex items-center gap-3 px-6 py-3 rounded-full border transition-all text-[11px] font-black uppercase tracking-[0.3em] font-outfit",
                                expandedThoughts[msg.id]
                                  ? "bg-gold-primary text-black border-gold-primary shadow-[0_10px_30px_rgba(229,192,111,0.3)]"
                                  : "bg-white/5 text-gold-primary/60 border-gold-primary/20 hover:border-gold-primary/50 hover:bg-gold-primary/5"
                              )}
                            >
                              <Scroll size={14} className={cn(expandedThoughts[msg.id] && "animate-pulse")} />
                              {expandedThoughts[msg.id] ? "Conceal Deliberation" : "View Scholarly Deliberation"}
                            </button>

                            <AnimatePresence>
                              {expandedThoughts[msg.id] && (
                                <motion.div
                                  initial={{ height: 0, opacity: 0, marginTop: 0 }}
                                  animate={{ height: 'auto', opacity: 1, marginTop: 24 }}
                                  exit={{ height: 0, opacity: 0, marginTop: 0 }}
                                  className="overflow-hidden"
                                >
                                  <div className="p-10 rounded-[2.5rem] bg-gold-primary/[0.03] border border-gold-primary/10 relative">
                                    <div className="absolute top-6 left-8 flex items-center gap-3 opacity-30">
                                      <div className="w-2 h-2 rounded-full bg-gold-primary animate-pulse" />
                                      <span className="text-[10px] font-black text-gold-primary uppercase tracking-[0.5em]">Internal Scholarly Reasoning</span>
                                    </div>
                                    <div className="mt-12 text-[14px] text-white/50 leading-relaxed font-medium italic font-outfit whitespace-pre-wrap pl-4 border-l-2 border-gold-primary/20">
                                      {msg.thoughts}
                                    </div>
                                  </div>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        )}

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
                      </div>
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
                    <span className="text-[13px] font-black text-gold-primary uppercase tracking-[0.5em] font-outfit animate-pulse">
                      {scholarlyStatus}
                    </span>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
          {/* Final Floating Input Pill with Suggestions */}
          <div className="absolute bottom-6 left-0 right-0 px-12 md:px-24 lg:px-32 pointer-events-none">
            <div className="max-w-5xl mx-auto pointer-events-auto">
              {/* Selected File Indicator */}
              <AnimatePresence>
                {supportsAttachments && selectedFile && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="flex items-center gap-3 bg-gold-primary/20 border border-gold-primary/40 rounded-full px-6 py-3 mb-3 w-fit backdrop-blur-3xl"
                  >
                    <Paperclip size={14} className="text-gold-primary" />
                    <span className="text-[11px] font-black text-white/80 uppercase tracking-widest">{selectedFile.name}</span>
                    <button onClick={() => setSelectedFile(null)} className="text-white/40 hover:text-white"><X size={14} /></button>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Interactive Suggestion Chips */}
              <AnimatePresence>
                {showSuggestions && !inputMessage && !selectedFile && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="flex gap-4 mb-6 overflow-x-auto no-scrollbar pb-2"
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

              <div className={cn(
                "flex items-center bg-[#011412]/95 backdrop-blur-[80px] rounded-[2.5rem] h-20 px-8 border shadow-[0_60px_120px_rgba(0,0,0,0.8)] gap-6 transition-all group/input",
                isRecording ? "border-red-500/50 shadow-[0_0_50px_rgba(239,68,68,0.3)]" : "border-white/10 hover:border-gold-primary/30"
              )}>
                {supportsAttachments && (
                  <>
                    <input 
                      type="file" 
                      ref={fileInputRef} 
                      onChange={handleFileUpload} 
                      className="hidden" 
                      accept=".pdf,.txt,image/*" 
                    />
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="p-3 text-white/20 hover:text-gold-primary transition-all group-hover/input:text-white/40"
                    >
                      <Paperclip size={22} />
                    </button>
                  </>
                )}
                <div className="relative flex-1 flex items-center h-full">
                  {!inputMessage && <PlaceholderRotator />}
                  <input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
                    className="w-full bg-transparent border-none outline-none text-xl text-white font-medium z-10"
                    placeholder={isRecording ? "Listening..." : ""}
                  />
                </div>
                <div className="flex items-center gap-4 border-l border-white/5 pl-6 h-12">
                  <select
                    value={quranTranslationLang}
                    onChange={(e) => setQuranTranslationLang(e.target.value)}
                    className="bg-transparent text-white/30 text-[10px] font-black uppercase tracking-[0.25em] outline-none"
                    aria-label="Quran translation language"
                  >
                    {quranLangOptions.map((code) => (
                      <option key={code} value={code} className="bg-[#011412] text-white">
                        {code.toUpperCase()}
                      </option>
                    ))}
                  </select>
                  {supportsVoice && (
                    <button 
                      onClick={toggleRecording}
                      className={cn(
                        "p-2 transition-all",
                        isRecording ? "text-red-500 animate-pulse" : "text-white/20 hover:text-gold-primary group-hover/input:text-white/40"
                      )}
                    >
                      <Mic size={20} />
                    </button>
                  )}
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={(!inputMessage.trim() && !selectedFile) || isTyping}
                    className={cn(
                      "w-14 h-14 rounded-full flex items-center justify-center transition-all shadow-lg",
                      (inputMessage.trim() || selectedFile) ? "bg-gold-primary text-black hover:scale-105 active:scale-95" : "bg-white/5 text-white/5"
                    )}
                  >
                    <Send size={20} fill={(inputMessage.trim() || selectedFile) ? "currentColor" : "none"} />
                  </button>
                </div>
              </div>
              
              {/* Agent Initializing Indicator */}
              <AnimatePresence>
                {isAgentInitializing && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 flex justify-center"
                  >
                    <div className="px-8 py-3 bg-gold-primary/10 border border-gold-primary/20 rounded-full flex items-center gap-4 backdrop-blur-3xl">
                      <div className="w-2 h-2 bg-gold-primary rounded-full animate-ping" />
                      <span className="text-[10px] font-black text-gold-primary uppercase tracking-[0.4em]">Scholarly Systems Bootloading... Please Wait</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>

      {/* System Initializing Modal */}
      <AnimatePresence>
        {isSystemInitializing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[200] flex items-center justify-center p-12 bg-black/80 backdrop-blur-3xl"
          >
            <motion.div
              initial={{ scale: 0.9, y: 30 }}
              animate={{ scale: 1, y: 0 }}
              className="flex flex-col items-center justify-center space-y-12 max-w-2xl"
            >
              {/* Animated Loading Circle */}
              <div className="relative w-32 h-32">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 rounded-full border-4 border-transparent border-t-gold-primary border-r-gold-primary shadow-[0_0_30px_rgba(229,192,111,0.4)]"
                />
                <motion.div
                  animate={{ rotate: -360 }}
                  transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-4 rounded-full border-2 border-transparent border-b-gold-primary/50 border-l-gold-primary/50"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-8 h-8 rounded-full bg-gold-primary/20 border border-gold-primary/40" />
                </div>
              </div>

              {/* Text Content */}
              <div className="text-center space-y-6">
                <div className="space-y-3">
                  <h2 className="text-4xl font-black text-white tracking-tight font-outfit uppercase">
                    ⏳ System Initializing
                  </h2>
                  <p className="text-gold-primary text-lg font-bold tracking-wide">
                    Loading scholarly resources...
                  </p>
                </div>

                {/* Status Messages */}
                <div className="space-y-3 mt-8">
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="flex items-center justify-center gap-3 text-white/60"
                  >
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                      className="w-2 h-2 rounded-full bg-gold-primary"
                    />
                    <span className="text-sm font-medium">Initializing knowledge base...</span>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="flex items-center justify-center gap-3 text-white/60"
                  >
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                      className="w-2 h-2 rounded-full bg-gold-primary"
                    />
                    <span className="text-sm font-medium">
                      Connecting to backend services... 
                      {initializationRetry > 0 && <span className="ml-2 text-gold-primary font-black">(Attempt {initializationRetry}/5)</span>}
                    </span>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 }}
                    className="flex items-center justify-center gap-3 text-white/60"
                  >
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                      className="w-2 h-2 rounded-full bg-gold-primary"
                    />
                    <span className="text-sm font-medium">Preparing sacred resources...</span>
                  </motion.div>
                </div>

                <p className="text-white/40 text-xs font-bold uppercase tracking-[0.3em] mt-8">
                  This will only happen once per session
                </p>
              </div>

              {/* Bottom Info */}
              <div className="w-full max-w-md pt-8 border-t border-white/10 mt-8">
                <div className="flex flex-col items-center justify-center gap-3">
                  <div className="flex items-center justify-center gap-2 text-white/30 text-xs font-medium">
                    <span className="w-2 h-2 rounded-full bg-gold-primary/40 animate-pulse" />
                    <span>Noor is preparing to assist you</span>
                    <span className="w-2 h-2 rounded-full bg-gold-primary/40 animate-pulse" />
                  </div>
                  <p className="text-white/20 text-[10px] font-bold uppercase tracking-[0.2em] text-center">
                    Backend: {apiUrl}
                  </p>
                  {initializationRetry > 3 && (
                    <p className="text-orange-400/80 text-[9px] font-black uppercase tracking-[0.2em] text-center mt-2">
                      ⚠️ Still connecting... Make sure backend is running
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hijri Vision Modal */}
      <AnimatePresence>
        {isTimelineOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-20 bg-black/80 backdrop-blur-2xl"
            onKeyDown={(e: React.KeyboardEvent<HTMLDivElement>) => e.key === 'Escape' && setIsTimelineOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 40 }}
              animate={{ scale: 1, y: 0 }}
              className="w-full max-w-6xl bg-[#011412] border border-white/10 rounded-[4rem] overflow-hidden shadow-[0_120px_240px_rgba(0,0,0,0.95)] flex flex-col h-[80vh]"
            >
              <div className="p-16 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                <div className="flex items-center gap-8">
                  <div className="w-20 h-20 rounded-[2rem] bg-gold-primary/10 flex items-center justify-center text-gold-primary">
                    <Calendar size={40} />
                  </div>
                  <div className="flex flex-col">
                    <h2 className="text-4xl font-black text-white uppercase tracking-tight font-outfit">Hijri Vision</h2>
                    <p className="text-gold-primary/60 font-bold uppercase tracking-[0.4em] text-[12px]">{calendarData?.month_name} {calendarData?.year} AH</p>
                  </div>
                </div>
                <button onClick={() => setIsTimelineOpen(false)} className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center text-white/40 hover:bg-white/10 hover:text-white transition-all">
                  <X size={24} />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto no-scrollbar p-20">
                <div className="grid grid-cols-7 gap-6">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="text-center text-[11px] font-black text-white/20 uppercase tracking-[0.5em] pb-8">{day}</div>
                  ))}
                  {calendarData?.month_grid.map((day: any) => (
                    <motion.div
                      key={day.day}
                      whileHover={{ scale: 1.05, backgroundColor: 'rgba(229, 192, 111, 0.05)' }}
                      className={cn(
                        "aspect-square rounded-3xl border flex flex-col p-6 transition-all relative group",
                        day.is_current ? "bg-gold-primary/10 border-gold-primary shadow-[0_0_30px_rgba(229,192,111,0.2)]" : "bg-white/[0.02] border-white/5",
                        day.is_sunnah_fast && "border-gold-primary/40"
                      )}
                    >
                      <span className={cn("text-2xl font-black", day.is_current ? "text-gold-primary" : "text-white/40")}>{day.day}</span>
                      <div className="mt-auto flex flex-col gap-2">
                        {day.events.map((e: any, idx: number) => (
                          <div key={idx} className={cn(
                            "text-[8px] font-bold uppercase tracking-widest px-3 py-1 rounded-full w-fit",
                            e.type === 'major' ? "bg-gold-primary text-black" : "bg-white/10 text-gold-primary"
                          )}>
                            {e.name}
                          </div>
                        ))}
                      </div>
                      {day.is_sunnah_fast && (
                        <div className="absolute top-4 right-4 w-2 h-2 rounded-full bg-gold-primary animate-pulse" />
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>

              <div className="p-10 bg-gold-primary text-black flex justify-between items-center">
                <div className="flex gap-10">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-black/20" />
                    <span className="text-[10px] font-black uppercase tracking-widest">Major Event</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-black/20 border-2 border-black/40" />
                    <span className="text-[10px] font-black uppercase tracking-widest">Sunnah Fast</span>
                  </div>
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest italic font-outfit">"The best of periods is the month of Ramadan, and the best of days is the Day of Arafah."</span>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {toast && (
        <div className="fixed bottom-32 px-10 py-4 bg-gold-primary rounded-full text-black font-black uppercase tracking-widest text-xs shadow-2xl animate-bounce">
          {toast}
        </div>
      )}
    </div>
  );
};

export default IslamicAIAgent;

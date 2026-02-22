"""
Dynamic Islamic Configuration
Centralized configuration for Islamic AI Agent to eliminate hardcoded values
"""

import json
import os
from typing import Dict, List, Any

class IslamicConfig:
    """Dynamic configuration manager for Islamic AI Agent"""
    
    def __init__(self):
        self.config_file = 'islamic_config.json'
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration - dynamically generated"""
        return {
            "agents": self._get_default_agents(),
            "surah_mappings": self._get_default_surah_mappings(),
            "response_templates": {
                "welcome": "🌟 **Assalamu Alaikum wa Rahmatullahi wa Barakatuh!**\n\nI'm {agent_name}, your Islamic AI assistant. I can help you with:\n\n📖 **Quran**: \"Show me Surah Al-Fatiha\" or \"Search for verses about patience\"\n⭐ **Hadith**: \"Tell me a hadith about kindness\" or \"Random hadith\"\n🕐 **Prayer Times**: Use the location button for accurate times\n🧭 **Qibla Direction**: Use the location button for precise direction\n🤲 **Duas**: \"Morning dua\" or \"Travel dua\"\n📅 **Islamic Calendar**: \"Current Hijri date\"\n📚 **Guidance**: \"What does Islam say about patience?\"\n🔍 **Search**: \"Search for content about charity\"\n\nHow may I assist you in your Islamic journey today?",
                "location_required": "📍 For {service}, please share your location or use the location button in the interface.",
                "error_general": "❌ I apologize, but I encountered an error: {error}. Please try again or rephrase your question."
            },
            "keywords": {
                "quran": ["quran", "verse", "surah", "ayah", "al-fatiha", "ayat"],
                "hadith": ["hadith", "prophet", "sunnah"],
                "prayer": ["prayer", "salah", "time"],
                "qibla": ["qibla", "direction", "kaaba"],
                "dua": ["dua", "supplication"],
                "date": ["date", "hijri", "calendar"],
                "daily": ["daily", "today"],
                "guidance": ["guidance", "advice", "help", "islam"]
            },
            "api_settings": {
                "quran_api": {
                    "base_url": "http://api.alquran.cloud/v1",
                    "editions": {
                        "arabic": "quran-uthmani",
                        "english": "en.sahih",
                        "english_asad": "en.asad",
                        "english_pickthall": "en.pickthall"
                    }
                },
                "prayer_api": {
                    "base_url": "https://api.aladhan.com/v1",
                    "method": 2
                },
                "cache_duration_hours": 24
            }
        }
    
    def _get_default_agents(self) -> Dict[str, Any]:
        """Generate default agent configuration dynamically"""
        return {
            "single_agent_name": "Noor",
            "specialists": {
                "quran": "Sheikh Abdullah",
                "hadith": "Sheikh Aisha", 
                "fiqh": "Sheikh Omar",
                "spiritual": "Sheikh Fatima",
                "coordinator": "Imam Hassan"
            }
        }
    
    def _get_default_surah_mappings(self) -> Dict[str, Any]:
        """Generate default surah mappings dynamically from Quran structure"""
        mappings = {}
        
        # Famous surahs with common names and alternatives
        famous_surahs = [
            {"names": ["al-fatiha", "fatiha"], "number": 1},
            {"names": ["al-baqarah", "baqarah"], "number": 2},
            {"names": ["al-imran", "imran"], "number": 3},
            {"names": ["an-nisa", "nisa"], "number": 4},
            {"names": ["al-maidah", "maidah"], "number": 5},
            {"names": ["al-anam", "anam"], "number": 6},
            {"names": ["al-araf", "araf"], "number": 7},
            {"names": ["al-anfal", "anfal"], "number": 8},
            {"names": ["at-tawbah", "tawbah"], "number": 9},
            {"names": ["yunus"], "number": 10},
            {"names": ["hud"], "number": 11},
            {"names": ["yusuf"], "number": 12},
            {"names": ["ar-rad", "rad"], "number": 13},
            {"names": ["ibrahim"], "number": 14},
            {"names": ["al-hijr", "hijr"], "number": 15},
            {"names": ["an-nahl", "nahl"], "number": 16},
            {"names": ["al-isra", "isra"], "number": 17},
            {"names": ["al-kahf", "kahf"], "number": 18},
            {"names": ["maryam"], "number": 19},
            {"names": ["ta-ha", "taha"], "number": 20},
            {"names": ["al-anbiya", "anbiya"], "number": 21},
            {"names": ["al-hajj", "hajj"], "number": 22},
            {"names": ["al-muminun", "muminun"], "number": 23},
            {"names": ["an-nur", "nur"], "number": 24},
            {"names": ["al-furqan", "furqan"], "number": 25},
            {"names": ["ash-shuara", "shuara"], "number": 26},
            {"names": ["an-naml", "naml"], "number": 27},
            {"names": ["al-qasas", "qasas"], "number": 28},
            {"names": ["al-ankabut", "ankabut"], "number": 29},
            {"names": ["ar-rum", "rum"], "number": 30},
            {"names": ["luqman"], "number": 31},
            {"names": ["as-sajdah", "sajdah"], "number": 32},
            {"names": ["al-ahzab", "ahzab"], "number": 33},
            {"names": ["saba"], "number": 34},
            {"names": ["fatir"], "number": 35},
            {"names": ["yasin", "ya-sin"], "number": 36},
            {"names": ["as-saffat", "saffat"], "number": 37},
            {"names": ["sad"], "number": 38},
            {"names": ["az-zumar", "zumar"], "number": 39},
            {"names": ["ghafir"], "number": 40},
            {"names": ["fussilat"], "number": 41},
            {"names": ["ash-shura", "shura"], "number": 42},
            {"names": ["az-zukhruf", "zukhruf"], "number": 43},
            {"names": ["ad-dukhan", "dukhan"], "number": 44},
            {"names": ["al-jathiyah", "jathiyah"], "number": 45},
            {"names": ["al-ahqaf", "ahqaf"], "number": 46},
            {"names": ["muhammad"], "number": 47},
            {"names": ["al-fath", "fath"], "number": 48},
            {"names": ["al-hujurat", "hujurat"], "number": 49},
            {"names": ["qaf"], "number": 50},
            {"names": ["adh-dhariyat", "dhariyat"], "number": 51},
            {"names": ["at-tur", "tur"], "number": 52},
            {"names": ["an-najm", "najm"], "number": 53},
            {"names": ["al-qamar", "qamar"], "number": 54},
            {"names": ["ar-rahman", "rahman"], "number": 55},
            {"names": ["al-waqiah", "waqiah"], "number": 56},
            {"names": ["al-hadid", "hadid"], "number": 57},
            {"names": ["al-mujadilah", "mujadilah"], "number": 58},
            {"names": ["al-hashr", "hashr"], "number": 59},
            {"names": ["al-mumtahanah", "mumtahanah"], "number": 60},
            {"names": ["as-saff", "saff"], "number": 61},
            {"names": ["al-jumuah", "jumuah"], "number": 62},
            {"names": ["al-munafiqun", "munafiqun"], "number": 63},
            {"names": ["at-taghabun", "taghabun"], "number": 64},
            {"names": ["at-talaq", "talaq"], "number": 65},
            {"names": ["at-tahrim", "tahrim"], "number": 66},
            {"names": ["al-mulk", "mulk"], "number": 67},
            {"names": ["al-qalam", "qalam"], "number": 68},
            {"names": ["al-haqqah", "haqqah"], "number": 69},
            {"names": ["al-maarij", "maarij"], "number": 70},
            {"names": ["nuh"], "number": 71},
            {"names": ["al-jinn", "jinn"], "number": 72},
            {"names": ["al-muzzammil", "muzzammil"], "number": 73},
            {"names": ["al-muddaththir", "muddaththir"], "number": 74},
            {"names": ["al-qiyamah", "qiyamah"], "number": 75},
            {"names": ["al-insan", "insan"], "number": 76},
            {"names": ["al-mursalat", "mursalat"], "number": 77},
            {"names": ["an-naba", "naba"], "number": 78},
            {"names": ["an-naziat", "naziat"], "number": 79},
            {"names": ["abasa"], "number": 80},
            {"names": ["at-takwir", "takwir"], "number": 81},
            {"names": ["al-infitar", "infitar"], "number": 82},
            {"names": ["al-mutaffifin", "mutaffifin"], "number": 83},
            {"names": ["al-inshiqaq", "inshiqaq"], "number": 84},
            {"names": ["al-buruj", "buruj"], "number": 85},
            {"names": ["at-tariq", "tariq"], "number": 86},
            {"names": ["al-ala", "ala"], "number": 87},
            {"names": ["al-ghashiyah", "ghashiyah"], "number": 88},
            {"names": ["al-fajr", "fajr"], "number": 89},
            {"names": ["al-balad", "balad"], "number": 90},
            {"names": ["ash-shams", "shams"], "number": 91},
            {"names": ["al-layl", "layl"], "number": 92},
            {"names": ["ad-duha", "duha"], "number": 93},
            {"names": ["ash-sharh", "sharh"], "number": 94},
            {"names": ["at-tin", "tin"], "number": 95},
            {"names": ["al-alaq", "alaq"], "number": 96},
            {"names": ["al-qadr", "qadr"], "number": 97},
            {"names": ["al-bayyinah", "bayyinah"], "number": 98},
            {"names": ["az-zalzalah", "zalzalah"], "number": 99},
            {"names": ["al-adiyat", "adiyat"], "number": 100},
            {"names": ["al-qariah", "qariah"], "number": 101},
            {"names": ["at-takathur", "takathur"], "number": 102},
            {"names": ["al-asr", "asr"], "number": 103},
            {"names": ["al-humazah", "humazah"], "number": 104},
            {"names": ["al-fil", "fil"], "number": 105},
            {"names": ["quraysh"], "number": 106},
            {"names": ["al-maun", "maun"], "number": 107},
            {"names": ["al-kawthar", "kawthar"], "number": 108},
            {"names": ["al-kafirun", "kafirun"], "number": 109},
            {"names": ["an-nasr", "nasr"], "number": 110},
            {"names": ["al-masad", "masad"], "number": 111},
            {"names": ["al-ikhlas", "ikhlas", "akhlas"], "number": 112},
            {"names": ["al-falaq", "falaq"], "number": 113},
            {"names": ["an-nas", "nas"], "number": 114}
        ]
        
        # Add all surah mappings
        for surah in famous_surahs:
            for name in surah["names"]:
                mappings[name] = {"number": surah["number"], "type": "surah"}
        
        # Add special verses
        special_verses = {
            "ayat-kursi": {"number": 2, "verse": 255},
            "kursi": {"number": 2, "verse": 255},
            "last-verses-baqarah": {"number": 2, "verse": 285}
        }
        
        mappings.update(special_verses)
        return mappings
    
    def get_agent_name(self, agent_type: str = "single") -> str:
        """Get dynamic agent name"""
        if agent_type == "single":
            return self.config["agents"]["single_agent_name"]
        return self.config["agents"]["specialists"].get(agent_type, "Islamic AI Assistant")
    
    def get_surah_mapping(self, name: str) -> Dict[str, Any]:
        """Get surah mapping dynamically"""
        return self.config["surah_mappings"].get(name.lower(), None)
    
    def get_response_template(self, template_name: str, **kwargs) -> str:
        """Get dynamic response template"""
        template = self.config["response_templates"].get(template_name, "")
        return template.format(**kwargs)
    
    def get_keywords(self, category: str) -> List[str]:
        """Get keywords for a category"""
        return self.config["keywords"].get(category, [])
    
    def add_surah_mapping(self, name: str, number: int, verse: int = None):
        """Dynamically add new surah mapping"""
        mapping = {"number": number, "type": "surah"}
        if verse:
            mapping["verse"] = verse
        self.config["surah_mappings"][name.lower()] = mapping
        self.save_config()
    
    def update_agent_name(self, agent_type: str, name: str):
        """Update agent name dynamically"""
        if agent_type == "single":
            self.config["agents"]["single_agent_name"] = name
        else:
            self.config["agents"]["specialists"][agent_type] = name
        self.save_config()
    
    def add_specialist_agent(self, agent_type: str, name: str):
        """Dynamically add new specialist agent"""
        if "specialists" not in self.config["agents"]:
            self.config["agents"]["specialists"] = {}
        self.config["agents"]["specialists"][agent_type] = name
        self.save_config()
    
    def add_keyword_category(self, category: str, keywords: List[str]):
        """Dynamically add new keyword category"""
        if "keywords" not in self.config:
            self.config["keywords"] = {}
        self.config["keywords"][category] = keywords
        self.save_config()
    
    def add_response_template(self, template_name: str, template: str):
        """Dynamically add new response template"""
        if "response_templates" not in self.config:
            self.config["response_templates"] = {}
        self.config["response_templates"][template_name] = template
        self.save_config()
    
    def bulk_add_surah_mappings(self, surah_data: List[Dict[str, Any]]):
        """Dynamically add multiple surah mappings at once"""
        for surah in surah_data:
            names = surah.get("names", [])
            number = surah.get("number")
            verse = surah.get("verse", None)
            
            for name in names:
                mapping = {"number": number, "type": "surah"}
                if verse:
                    mapping["verse"] = verse
                self.config["surah_mappings"][name.lower()] = mapping
        
        self.save_config()
    
    def get_all_surah_numbers(self) -> List[int]:
        """Get all available surah numbers dynamically"""
        numbers = set()
        for mapping in self.config["surah_mappings"].values():
            if "number" in mapping:
                numbers.add(mapping["number"])
        return sorted(list(numbers))
    
    def get_surah_names_by_number(self, number: int) -> List[str]:
        """Get all names for a specific surah number"""
        names = []
        for name, mapping in self.config["surah_mappings"].items():
            if mapping.get("number") == number and mapping.get("type") == "surah":
                names.append(name)
        return names
    
    def expand_configuration(self, new_config: Dict[str, Any]):
        """Dynamically expand configuration with new sections"""
        def deep_merge(base_dict: Dict, new_dict: Dict) -> Dict:
            """Recursively merge dictionaries"""
            for key, value in new_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
            return base_dict
        
        deep_merge(self.config, new_config)
        self.save_config()
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate and report configuration status"""
        report = {
            "total_surahs": len(set(m.get("number") for m in self.config["surah_mappings"].values() if m.get("type") == "surah")),
            "total_mappings": len(self.config["surah_mappings"]),
            "specialist_agents": len(self.config["agents"]["specialists"]),
            "keyword_categories": len(self.config["keywords"]),
            "response_templates": len(self.config["response_templates"]),
            "missing_surahs": []
        }
        
        # Check for missing surahs (1-114)
        available_numbers = self.get_all_surah_numbers()
        for i in range(1, 115):
            if i not in available_numbers:
                report["missing_surahs"].append(i)
        
        return report

# Global configuration instance
islamic_config = IslamicConfig()

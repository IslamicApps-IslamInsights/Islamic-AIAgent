"""
Advanced Query Classifier - Intelligent Intent Recognition
Recognizes user intent and routes to optimal tools
No external LLM required - Pure regex + pattern matching
"""

import re
import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger("AdvancedClassifier")


class QueryCategory(Enum):
    """Primary query categories for intelligent routing"""
    # Quranic & Textual
    SURAH_SPECIFIC = "surah_specific"
    QURAN_GENERAL = "quran_general"
    AYAT_SEARCH = "ayat_search"
    
    # Prophetic Traditions
    HADITH = "hadith"
    SUNNAH = "sunnah"
    
    # Daily Practices & Timing
    PRAYER_TIMES = "prayer_times"
    PRAYER_GUIDE = "prayer_guide"
    PRAYER_POSTURES = "prayer_postures"
    DAILY_ADHKAR = "daily_adhkar"
    DUAS = "duas"
    
    # Religious Obligations & Practices
    ZAKAT = "zakat"
    HAJJ = "hajj"
    UMRAH = "umrah"
    FASTING = "fasting"
    
    # Islamic Knowledge
    ISLAMIC_KNOWLEDGE = "islamic_knowledge"
    FATWA = "fatwa"
    FIQH = "fiqh"
    AQEEDAH = "aqeedah"
    ISLAMIC_ETHICS = "islamic_ethics"
    
    # Islamic History & Biography
    SEERAH = "seerah"
    SAHABA = "sahaba"
    ISLAMIC_HISTORY = "islamic_history"
    
    # Practical Information
    PERSONAL_GUIDANCE = "personal_guidance"
    ISLAMIC_CALENDAR = "islamic_calendar"
    ASMAUL_HUSNA = "asmaul_husna"
    QIBLA = "qibla"
    
    # Fallback
    GENERAL_QUERY = "general_query"


@dataclass
class ClassifiedQuery:
    """Structured result of query classification"""
    category: QueryCategory
    confidence: float  # 0.0 to 1.0
    primary_keywords: List[str]
    secondary_keywords: List[str]
    location_data: Optional[Dict] = None
    date_specified: Optional[str] = None
    numeric_param: Optional[float] = None
    language: str = "en"
    raw_query: str = ""
    extracted_entities: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extracted_entities is None:
            self.extracted_entities = {}


class AdvancedQueryClassifier:
    """
    Intelligent query classifier that recognizes user intent
    Routes to appropriate tools without external LLMs
    """
    
    def __init__(self):
        self.logger = logger
        
        # Define query patterns for each category
        self.category_patterns = {
            QueryCategory.PRAYER_TIMES: {
                "keywords": [
                    r"\b(prayer times?|salah times?|namaz times?|prayer schedule|salat times?)\b",
                    r"\b(when is|what time|prayer time)\b",
                    r"\b(asr|fajr|dhuhr|maghrib|isha|zuhr)\b.*\b(time|prayer|namaz|salah)\b",
                    r"\b(adhan times?|iqamat times?)\b",
                ],
                "confidence_boost": 0.95,
                "requires_location": True
            },
            
            QueryCategory.QIBLA: {
                "keywords": [
                    r"\b(qibla|qiblah|kibla)\b",
                    r"\b(direction\s+of\s+(?:qibla|prayer))\b",
                    (
                        r"\b(direction\s+to\s+(?:mecca|makkah|kaaba|"
                        r"ka'bah|kabah))\b"
                    ),
                    (
                        r"\b(face\s+(?:mecca|makkah|kaaba|"
                        r"ka'bah|kabah))\b"
                    ),
                    r"\b(where\s+is\s+qibla)\b",
                ],
                "confidence_boost": 0.95,
                "requires_location": True
            },
            
            QueryCategory.PRAYER_GUIDE: {
                "keywords": [
                    r"\b(how to pray|how to perform|pray properly|salah correctly|namaz properly)\b",
                    r"\b(prayer steps|salah steps|namaz steps|rakat|rakah)\b",
                    r"\b(prayer positions?|prayer postures?|standing sitting|bowing)\b",
                    r"\b(prayer method|salah method|namaz method)\b",
                ],
                "confidence_boost": 0.90,
            },
            
            QueryCategory.DAILY_ADHKAR: {
                "keywords": [
                    r"\b(adhkar|adkhar|azkar|dhikr|remembrance|glorification)\b",
                    r"\b(morning|evening|afternoon|night).*\b(prayers?|dhikr|azkar)\b",
                    r"\b(after prayer|after salah|after namaz|post-prayer)\b.*\b(dhikr|azkar)\b",
                    r"\b(subhanallah|alhamdulillah|allahu akbar)\b",
                ],
                "confidence_boost": 0.85,
            },
            
            QueryCategory.DUAS: {
                "keywords": [
                    r"\b(dua|duas|supplication|supplications|prayer\s+for|pray\s+for)\b",
                    r"\b(ya allah|ya rabb|ya muallim)\b",
                    r"\b(how to ask allah|asking allah|asking god)\b",
                    r"\b(dua for|du'a for|supplication for)\b",
                ],
                "confidence_boost": 0.85,
            },
            
            QueryCategory.SURAH_SPECIFIC: {
                "keywords": [
                    r"\b(surah|sura|chapter)\s+([\w\-]+)\b",
                    r"\b(surah|sura)#?(\d{1,3})\b",
                    r"\b(al-fatiha|al-baqarah|al-ikhlas|al-quran)\b",
                    r"\b(tell me|explain|meaning|tafsir|exegesis).*\b(surah|sura)\b",
                    r"\b(what is surah|understand surah)\b",
                ],
                "confidence_boost": 0.98,
            },
            
            QueryCategory.QURAN_GENERAL: {
                "keywords": [
                    r"\b(quran|qur'an|quran\s+says|what does quran|quran teaches)\b",
                    r"\b(quranic|quranic\s+verses?|quranic\s+wisdom)\b",
                    r"\b(ayat|ayah|verse|verses)\b.*\b(quran|quranic)\b",
                    r"\b(quran.*meaning|quran.*wisdom|quran.*guidance)\b",
                    r"\b(tafsir|exegesis|mufassir|commentary)\b",
                    r"\b(mushaf|mus'haf|page\s+\d{1,3}|juz\s+\d{1,2})\b",
                    r"\b(qiraat|qira'at|hafs|warsh|qaloon|qaaloon)\b",
                    r"\b(morphology|morphological|root|lemma|paradigm|concordance|word\s+analysis|grammar)\b",
                    r"\b(\d{1,3}:\d{1,3})\b",
                ],
                "confidence_boost": 0.88,
            },
            
            QueryCategory.HADITH: {
                "keywords": [
                    r"\b(hadith|ahadith|hadis|prophetic\s+traditions?|sunnah)\b",
                    r"\b(sahih\s+bukhari|sahih\s+muslim|tirmidhi|abu\s+dawud)\b",
                    r"\b(prophet\s+(said|narrated|reported))\b",
                    r"\b(authentic\s+narration|hadith\s+about)\b",
                ],
                "confidence_boost": 0.90,
            },
            
            QueryCategory.SUNNAH: {
                "keywords": [
                    r"\b(sunnah|sunna|prophetic\s+practice|prophet's\s+way)\b",
                    r"\b(how did prophet|what did prophet|prophet's\s+habit)\b",
                ],
                "confidence_boost": 0.85,
            },
            
            QueryCategory.ZAKAT: {
                "keywords": [
                    r"\b(zakat|zakah|alms|obligatory\s+charity)\b",
                    r"\b(zakat calculator|calculate zakat|how much zakat)\b",
                    r"\b(nisab|zakat\s+due)\b",
                ],
                "confidence_boost": 0.92,
            },
            
            QueryCategory.HAJJ: {
                "keywords": [
                    r"\b(hajj|haj|pilgrimage|pilgrim)\b",
                    r"\b(hajj steps|hajj guide|how to perform hajj|hajji)\b",
                ],
                "confidence_boost": 0.90,
            },
            
            QueryCategory.UMRAH: {
                "keywords": [
                    r"\b(umrah|umra|minor\s+pilgrimage)\b",
                    r"\b(umrah guide|how to perform umrah)\b",
                ],
                "confidence_boost": 0.90,
            },
            
            QueryCategory.FASTING: {
                "keywords": [
                    r"\b(fasting|fast|sawm|roza|ramadan|iftar)\b",
                    r"\b(fasting rules?|how to fast|fasting guide)\b",
                ],
                "confidence_boost": 0.88,
            },
            
            QueryCategory.SEERAH: {
                "keywords": [
                    r"\b(seerah|sirah|biography|life of prophet|prophet's life)\b",
                    r"\b(prophet muhammad|the prophet|rasulullah)\b.*\b(biography|life|story)\b",
                ],
                "confidence_boost": 0.85,
            },
            
            QueryCategory.SAHABA: {
                "keywords": [
                    r"\b(sahaba|companions|companion of prophet)\b",
                    r"\b(abu bakr|umar|uthman|ali|aisha)\b",
                ],
                "confidence_boost": 0.85,
            },
            
            QueryCategory.ISLAMIC_ETHICS: {
                "keywords": [
                    r"\b(akhlaq|ethics|moral|character|virtue)\b",
                    r"\b(islamic values|islamic principles|islamic conduct)\b",
                ],
                "confidence_boost": 0.80,
            },
            
            QueryCategory.ASMAUL_HUSNA: {
                "keywords": [
                    r"\b(asmaul husna|names of allah|beautiful names|99 names)\b",
                    r"\b(ar[\s-]?rahm[aā]+n|ar[\s-]?rah[iī]+m|allah'?s names)\b",
                ],
                "confidence_boost": 0.92,
            },
            
            QueryCategory.ISLAMIC_CALENDAR: {
                "keywords": [
                    r"\b(hijri|islamic calendar|lunar calendar|hijra date)\b",
                    r"\b(when is|what date).*(hijri|islamic)\b",
                ],
                "confidence_boost": 0.88,
            },
        }
        
        # Surah name mapping for entity extraction
        self.surah_names = {
            "fatiha": 1, "baqarah": 2, "imran": 3, "nisa": 4, "maidah": 5,
            "anam": 6, "araf": 7, "anfal": 8, "tawbah": 9, "yunus": 10,
            "hud": 11, "yusuf": 12, "raad": 13, "ibrahim": 14, "hijr": 15,
            "nahl": 16, "isra": 17, "kahf": 18, "maryam": 19, "taha": 20,
            "anbiya": 21, "hajj": 22, "muminun": 23, "nur": 24, "furqan": 25,
            "shoara": 26, "naml": 27, "qasas": 28, "ankabut": 29, "rum": 30,
            "luqman": 31, "sajdah": 32, "ahzab": 33, "saba": 34, "fatir": 35,
            "yasin": 36, "saffat": 37, "sad": 38, "zumar": 39, "ghafir": 40,
            "fussilat": 41, "shura": 42, "zukhruf": 43, "dukhan": 44, "jathiyah": 45,
            "ahqaf": 46, "muhammad": 47, "fath": 48, "hujurat": 49, "qaf": 50,
            "dhariyat": 51, "tur": 52, "najm": 53, "qamar": 54, "rahman": 55,
            "waqiah": 56, "hadid": 57, "mujadilah": 58, "hashr": 59, "mumtahanah": 60,
            "saff": 61, "jumah": 62, "munafiqun": 63, "taghabun": 64, "talaq": 65,
            "tahrim": 66, "mulk": 67, "qalam": 68, "haqqah": 69, "maarij": 70,
            "nuh": 71, "jinn": 72, "muzzammil": 73, "muddaththir": 74, "qiyamah": 75,
            "insan": 76, "mursalat": 77, "naba": 78, "naziat": 79, "abasa": 80,
            "takwir": 81, "infitar": 82, "mutaffifin": 83, "inshiqaq": 84, "buruj": 85,
            "tariq": 86, "ala": 87, "ghashiyah": 88, "fajr": 89, "balad": 90,
            "shams": 91, "layl": 92, "duha": 93, "inshirah": 94, "tin": 95,
            "alaq": 96, "qadr": 97, "bayyinah": 98, "zilzal": 99, "adiyat": 100,
            "qaria": 101, "takathur": 102, "asr": 103, "humaza": 104, "fil": 105,
            "quraysh": 106, "maun": 107, "kauther": 108, "kafirun": 109, "nasr": 110,
            "lahab": 111, "ikhlas": 112, "falaq": 113, "nas": 114,
        }
    
    def classify(self, query: str) -> ClassifiedQuery:
        """Classify a user query and return structured result"""
        query_lower = query.lower()
        extracted_entities = {}
        location_data = None
        date_specified = None
        numeric_param = None
        
        # Extract numeric parameters (for Zakat, amounts, etc.)
        numeric_match = re.search(r'\b(\d+(?:\.\d+)?)\b', query_lower)
        if numeric_match:
            numeric_param = float(numeric_match.group(1))
        
        # Try to extract Surah number
        surah_num = self._extract_surah_number(query_lower)
        if surah_num:
            extracted_entities['surah_number'] = surah_num
        
        # Score each category
        category_scores = {}
        
        for category, patterns_dict in self.category_patterns.items():
            score = 0
            matched_keywords = []
            
            for keyword_pattern in patterns_dict.get("keywords", []):
                if re.search(keyword_pattern, query_lower):
                    score += patterns_dict.get("confidence_boost", 0.5)
                    matched_keywords.append(keyword_pattern)
            
            if score > 0:
                category_scores[category] = {
                    'score': min(score, 1.0),  # Normalize to 0-1
                    'keywords': matched_keywords
                }
        
        # Get best match
        if category_scores:
            best_category = max(category_scores, key=lambda x: category_scores[x]['score'])
            confidence = category_scores[best_category]['score']
            primary_keywords = category_scores[best_category]['keywords'][:3]
        else:
            best_category = QueryCategory.GENERAL_QUERY
            confidence = 0.0
            primary_keywords = []
        
        # Get secondary keywords (categories with decent scores)
        secondary_keywords = []
        for cat, data in sorted(category_scores.items(), key=lambda x: x[1]['score'], reverse=True)[1:4]:
            secondary_keywords.extend(data['keywords'][:1])
        
        result = ClassifiedQuery(
            category=best_category,
            confidence=confidence,
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords,
            location_data=location_data,
            date_specified=date_specified,
            numeric_param=numeric_param,
            extracted_entities=extracted_entities,
            raw_query=query
        )
        
        self.logger.info(
            f"Query classified: {best_category.value} (confidence: {confidence:.2f}) - {query[:50]}"
        )
        
        return result
    
    def _extract_surah_number(self, query_lower: str) -> Optional[int]:
        """Extract Surah number from query"""
        # Try to match explicit number
        num_match = re.search(r'\bsurah\s*#?(\d{1,3})', query_lower)
        if num_match:
            num = int(num_match.group(1))
            if 1 <= num <= 114:
                return num
        
        # Try to match Surah by name
        normalized = (
            query_lower.replace("-", " ")
            .replace("_", " ")
            .replace("’", "'")
        )
        for name, num in self.surah_names.items():
            if (
                f"surah {name}" in normalized
                or f"sura {name}" in normalized
                or f"surah al {name}" in normalized
                or f"sura al {name}" in normalized
                or f"surah al{name}" in normalized
                or f"sura al{name}" in normalized
            ):
                return num
        
        return None


def get_classifier() -> AdvancedQueryClassifier:
    """Get singleton classifier instance"""
    global _classifier
    if '_classifier' not in globals():
        _classifier = AdvancedQueryClassifier()
    return _classifier

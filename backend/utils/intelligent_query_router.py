"""
Intelligent Query Router for Islamic AI Agent
Classifies queries and routes them to appropriate handlers (Quran, Hadith, etc.)
Detects Surah queries and provides comprehensive Quranic information
"""

import asyncio
import logging
import re
from typing import Dict, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger("QueryRouter")

# Surah names in English and Arabic
SURAH_NAMES = {
    1: ("Al-Fatiha", "الفاتحة", "The Opening"),
    2: ("Al-Baqarah", "البقرة", "The Cow"),
    3: ("Aal-e-Imran", "آل عمران", "The Family of Imran"),
    4: ("An-Nisa", "النساء", "The Women"),
    5: ("Al-Ma'idah", "المائدة", "The Table"),
    6: ("Al-An'am", "الأنعام", "The Cattle"),
    7: ("Al-A'raf", "الأعراف", "The Heights"),
    8: ("Al-Anfal", "الأنفال", "The Spoils"),
    9: ("At-Tawbah", "التوبة", "The Repentance"),
    10: ("Yunus", "يونس", "Jonah"),
    11: ("Hud", "هود", "Hud"),
    12: ("Yusuf", "يوسف", "Joseph"),
    13: ("Ar-Ra'd", "الرعد", "The Thunder"),
    14: ("Ibrahim", "إبراهيم", "Abraham"),
    15: ("Al-Hijr", "الحجر", "The Rocky Tract"),
    16: ("An-Nahl", "النحل", "The Bee"),
    17: ("Al-Isra", "الإسراء", "The Night Journey"),
    18: ("Al-Kahf", "الكهف", "The Cave"),
    19: ("Maryam", "مريم", "Mary"),
    20: ("Ta-Ha", "طه", "Ta-Ha"),
    21: ("Al-Anbiya", "الأنبياء", "The Prophets"),
    22: ("Al-Hajj", "الحج", "The Pilgrimage"),
    23: ("Al-Mu'minun", "المؤمنون", "The Believers"),
    24: ("An-Nur", "النور", "The Light"),
    25: ("Al-Furqan", "الفرقان", "The Criterion"),
    26: ("Ash-Shu'ara", "الشعراء", "The Poets"),
    27: ("An-Naml", "النمل", "The Ant"),
    28: ("Al-Qasas", "القصص", "The Stories"),
    29: ("Al-Ankabut", "العنكبوت", "The Spider"),
    30: ("Ar-Rum", "الروم", "The Romans"),
    31: ("Luqman", "لقمان", "Luqman"),
    32: ("As-Sajdah", "السجدة", "The Prostration"),
    33: ("Al-Ahzab", "الأحزاب", "The Confederates"),
    34: ("Saba", "سبأ", "Saba"),
    35: ("Fatir", "فاطر", "The Originator"),
    36: ("Ya-Sin", "يس", "Ya-Sin"),
    37: ("As-Saffat", "الصافات", "The Rows"),
    38: ("Sad", "ص", "Sad"),
    39: ("Az-Zumar", "الزمر", "The Groups"),
    40: ("Ghafir", "غافر", "The Forgiver"),
    41: ("Fussilat", "فصلت", "Distinguished"),
    42: ("Ash-Shura", "الشورى", "Consultation"),
    43: ("Az-Zukhruf", "الزخرف", "The Ornament"),
    44: ("Ad-Dukhan", "الدخان", "The Smoke"),
    45: ("Al-Jathiyah", "الجاثية", "The Kneeling"),
    46: ("Al-Ahqaf", "الأحقاف", "The Sand Dunes"),
    47: ("Muhammad", "محمد", "Muhammad"),
    48: ("Al-Fath", "الفتح", "The Victory"),
    49: ("Al-Hujurat", "الحجرات", "The Private Quarters"),
    50: ("Qaf", "ق", "Qaf"),
    51: ("Adh-Dhariyat", "الذاريات", "The Spreaders"),
    52: ("At-Tur", "الطور", "The Mount"),
    53: ("An-Najm", "النجم", "The Star"),
    54: ("Al-Qamar", "القمر", "The Moon"),
    55: ("Ar-Rahman", "الرحمن", "The Most Gracious"),
    56: ("Al-Waqiah", "الواقعة", "The Inevitable"),
    57: ("Al-Hadid", "الحديد", "The Iron"),
    58: ("Al-Mujadilah", "المجادلة", "The Pleading Woman"),
    59: ("Al-Hashr", "الحشر", "The Gathering"),
    60: ("Al-Mumtahanah", "الممتحنة", "The Woman to be Examined"),
    61: ("As-Saff", "الصف", "The Ranks"),
    62: ("Al-Jumu'ah", "الجمعة", "The Friday"),
    63: ("Al-Munafiqun", "المنافقون", "The Hypocrites"),
    64: ("At-Taghabun", "التغابن", "The Mutual Loss and Gain"),
    65: ("At-Talaq", "الطلاق", "The Divorce"),
    66: ("At-Tahrim", "التحريم", "The Prohibition"),
    67: ("Al-Mulk", "الملك", "The Sovereignty"),
    68: ("Al-Qalam", "القلم", "The Pen"),
    69: ("Al-Haqqah", "الحاقة", "The Inevitable Reality"),
    70: ("Al-Ma'arij", "المعارج", "The Ascending Stairways"),
    71: ("Nuh", "نوح", "Noah"),
    72: ("Al-Jinn", "الجن", "The Jinn"),
    73: ("Al-Muzzammil", "المزمل", "The Enshrouded One"),
    74: ("Al-Muddaththir", "المدثر", "The Cloaked One"),
    75: ("Al-Qiyamah", "القيامة", "The Resurrection"),
    76: ("Al-Insan", "الإنسان", "The Man"),
    77: ("Al-Mursalat", "المرسلات", "The Sent Forth"),
    78: ("An-Naba", "النبأ", "The Announcement"),
    79: ("An-Nazi'at", "الناعات", "Those Who Drag Forth"),
    80: ("Abasa", "عبس", "He Frowned"),
    81: ("At-Takwir", "التكوير", "The Overthrowing"),
    82: ("Al-Infitar", "الإنفطار", "The Cleaving"),
    83: ("Al-Mutaffifin", "المطففين", "The Defrauders"),
    84: ("Al-Inshiqaq", "الإنشقاق", "The Splitting Asunder"),
    85: ("Al-Buruj", "البروج", "The Constellations"),
    86: ("At-Tariq", "الطارق", "The Morning Star"),
    87: ("Al-A'la", "الأعلى", "The Most High"),
    88: ("Al-Ghashiyah", "الغاشية", "The Overwhelming"),
    89: ("Al-Fajr", "الفجر", "The Daybreak"),
    90: ("Al-Balad", "البلد", "The City"),
    91: ("Ash-Shams", "الشمس", "The Sun"),
    92: ("Al-Layl", "الليل", "The Night"),
    93: ("Ad-Duha", "الضحى", "The Morning Sunlight"),
    94: ("Ash-Sharh", "الشرح", "The Opening Up"),
    95: ("At-Tin", "التين", "The Fig"),
    96: ("Al-Alaq", "العلق", "The Clot"),
    97: ("Al-Qadr", "القدر", "The Power"),
    98: ("Al-Bayyinah", "البينة", "The Clear Proof"),
    99: ("Az-Zalzalah", "الزلزلة", "The Earthquake"),
    100: ("Al-Adiyat", "العاديات", "The Runners"),
    101: ("Al-Qari'ah", "القارعة", "The Striking Hour"),
    102: ("At-Takathur", "التكاثر", "The Rivalry"),
    103: ("Al-Asr", "العصر", "The Decline of the Day"),
    104: ("Al-Humazah", "الهمزة", "The Slanderer"),
    105: ("Al-Fil", "الفيل", "The Elephant"),
    106: ("Quraish", "قريش", "The Quraish"),
    107: ("Al-Ma'un", "الماعون", "The Assistance"),
    108: ("Al-Kawthar", "الكوثر", "The Abundance"),
    109: ("Al-Kafirun", "الكافرون", "The Disbelievers"),
    110: ("An-Nasr", "النصر", "The Help"),
    111: ("Al-Masad", "المسد", "The Flame"),
    112: ("Al-Ikhlas", "الإخلاص", "The Sincerity"),
    113: ("Al-Falaq", "الفلق", "The Daybreak"),
    114: ("An-Nas", "الناس", "The Mankind"),
}

# Reverse mapping for quick lookup
SURAH_NUMBER_LOOKUP = {}
for num, (english, arabic, meaning) in SURAH_NAMES.items():
    SURAH_NUMBER_LOOKUP[english.lower()] = num
    SURAH_NUMBER_LOOKUP[arabic] = num
    SURAH_NUMBER_LOOKUP[f"surah {english.lower()}"] = num


class QueryType(Enum):
    """Types of queries the system can handle"""
    SURAH_SPECIFIC = "surah_specific"  # Query about specific Surah
    QURAN_GENERAL = "quran_general"    # General Quranic query
    HADITH = "hadith"                  # Hadith-related query
    ISLAMIC_GENERAL = "islamic_general"  # General Islamic query
    OTHER = "other"                    # Not Islamic-related


def parse_surah_query(query: str) -> Optional[int]:
    """
    Parse a query to extract Surah number if it's a Surah-specific query.
    
    Args:
        query: User's query string
        
    Returns:
        Surah number (1-114) if found, None otherwise
    """
    query_lower = query.lower().strip()
    
    # Pattern 1: "Show me Surah Al-Fatiha"
    patterns = [
        r"show\s+(?:me\s+)?(?:the\s+)?surah\s+([^\d]+?)(?:\s|$)",
        r"(?:surah|chapter)\s+([^\d]+?)(?:\s+(?:of|from)\s+)?(?:\s|$)",
        r"(?:surah|chapter)\s+(\d+)",
        r"tell\s+(?:me|us)\s+about\s+(?:the\s+)?surah\s+([^\d]+?)(?:\s|$)",
        r"(?:what|who|explain)\s+(?:is|are)\s+(?:the\s+)?surah\s+([^\d]+?)(?:\s|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            surah_name_or_number = match.group(1).strip()
            
            # Try direct number lookup
            if surah_name_or_number.isdigit():
                num = int(surah_name_or_number)
                if 1 <= num <= 114:
                    return num
            
            # Try name lookup
            surah_name_normalized = surah_name_or_number.lower().strip()
            if surah_name_normalized in SURAH_NUMBER_LOOKUP:
                return SURAH_NUMBER_LOOKUP[surah_name_normalized]
    
    return None


def classify_query(query: str) -> Tuple[QueryType, Optional[int]]:
    """
    Classify the query type and extract relevant metadata.
    
    Args:
        query: User's query string
        
    Returns:
        Tuple of (QueryType, metadata)
    """
    query_lower = query.lower()
    
    # Check for Surah-specific query
    surah_num = parse_surah_query(query)
    if surah_num:
        return QueryType.SURAH_SPECIFIC, surah_num
    
    # Check for general Quran queries
    quran_keywords = ["quran", "qur'an", "ayah", "verse", "surahs", "chapters", "quranic"]
    if any(keyword in query_lower for keyword in quran_keywords):
        # If not specifically about a Surah, it's general Quran query
        if "surah" not in query_lower and "chapter" not in query_lower:
            return QueryType.QURAN_GENERAL, None
    
    # Check for Hadith queries
    hadith_keywords = ["hadith", "hadeeth", "sahih", "muslim", "bukhari", "tirmidhi", "nasa'i", "nasai", "abu dawud"]
    if any(keyword in query_lower for keyword in hadith_keywords):
        return QueryType.HADITH, None
    
    # Check for Islamic general queries
    islamic_keywords = [
        "islam", "muslim", "allah", "prophet", "muhammad", "salah", "prayer", "zakat",
        "hajj", "fasting", "ramadan", "dua", "islamic", "shariah", "fiqh", "fatwa",
        "halal", "haram", "ummah", "khalifah", "shahada", "wudu"
    ]
    if any(keyword in query_lower for keyword in islamic_keywords):
        return QueryType.ISLAMIC_GENERAL, None
    
    return QueryType.OTHER, None


async def fetch_surah_comprehensive(surah_number: int) -> Dict[str, Any]:
    """
    Fetch comprehensive Surah information from Quran Foundation MCP.
    
    Args:
        surah_number: Surah number (1-114)
        
    Returns:
        Dictionary with Surah text, translation, tafsir, and metadata
    """
    from backend.utils.quran_mcp_provider import get_quran_mcp
    
    mcp = get_quran_mcp()
    surah_info = SURAH_NAMES.get(surah_number)
    
    if not surah_info:
        return {"error": f"Invalid Surah number: {surah_number}"}
    
    english_name, arabic_name, meaning = surah_info
    
    try:
        # Fetch Quranic text, translation, and tafsir concurrently
        tasks = [
            mcp.fetch_quran(surah_number, edition="ar.standard"),
            mcp.fetch_translation(surah_number, language="en", translator="sahih"),
            mcp.fetch_tafsir(surah_number, tafsir_type="ibn_kathir"),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quran_text = results[0] if not isinstance(results[0], Exception) else {}
        translation = results[1] if not isinstance(results[1], Exception) else {}
        tafsir = results[2] if not isinstance(results[2], Exception) else {}
        
        return {
            "surah_number": surah_number,
            "english_name": english_name,
            "arabic_name": arabic_name,
            "meaning": meaning,
            "quran_text": quran_text,
            "translation": translation,
            "tafsir": tafsir,
            "source": "Quran Foundation MCP",
        }
    
    except Exception as e:
        logger.error(f"Error fetching Surah {surah_number}: {e}")
        return {
            "error": str(e),
            "surah_number": surah_number,
            "english_name": english_name,
            "arabic_name": arabic_name,
        }


def format_surah_response(surah_data: Dict[str, Any]) -> str:
    """
    Format comprehensive Surah information for user display.
    
    Args:
        surah_data: Dictionary with Surah information
        
    Returns:
        Formatted string response
    """
    if "error" in surah_data:
        return f"Error fetching Surah information: {surah_data['error']}"
    
    english_name = surah_data.get("english_name", "")
    arabic_name = surah_data.get("arabic_name", "")
    meaning = surah_data.get("meaning", "")
    surah_num = surah_data.get("surah_number", "")
    
    response = f"""
╔════════════════════════════════════════════════════════════╗
║                   SURAH INFORMATION                        ║
╚════════════════════════════════════════════════════════════╝

📖 **Surah #{surah_num}: {english_name}**
🕌 **Arabic Name**: {arabic_name}
✨ **Meaning**: {meaning}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    # Add Quranic text
    quran_text = surah_data.get("quran_text", {})
    if quran_text and "verses" in quran_text:
        response += "📜 **Quranic Text (Arabic)**:\n"
        verses = quran_text.get("verses", [])
        if isinstance(verses, list) and len(verses) > 0:
            # Show first few verses
            for verse in verses[:3]:
                if isinstance(verse, dict):
                    response += f"  {verse.get('verse_number', '')}: {verse.get('text', '')}\n"
                else:
                    response += f"  {verse}\n"
            if len(verses) > 3:
                response += f"  ... ({len(verses) - 3} more verses)\n"
        response += "\n"
    
    # Add translation
    translation = surah_data.get("translation", {})
    if translation and "verses" in translation:
        response += "🌍 **English Translation**:\n"
        verses = translation.get("verses", [])
        if isinstance(verses, list) and len(verses) > 0:
            for verse in verses[:2]:
                if isinstance(verse, dict):
                    response += f"  Verse {verse.get('verse_number', '')}: {verse.get('text', '')}\n"
                else:
                    response += f"  {verse}\n"
            if len(verses) > 2:
                response += f"  ... ({len(verses) - 2} more verses)\n"
        response += "\n"
    
    # Add tafsir summary
    tafsir = surah_data.get("tafsir", {})
    if tafsir:
        response += "📚 **Tafsir (Islamic Exegesis)**:\n"
        if isinstance(tafsir, dict) and "summary" in tafsir:
            response += f"  {tafsir['summary'][:300]}...\n\n"
        elif isinstance(tafsir, str):
            response += f"  {tafsir[:300]}...\n\n"
    
    response += f"📌 **Source**: {surah_data.get('source', 'Quran Foundation MCP')}\n"
    
    return response


def should_use_quran_foundation(query_type: QueryType) -> bool:
    """
    Determine if query should be routed to Quran Foundation MCP.
    
    Args:
        query_type: The classified query type
        
    Returns:
        True if should use Quran Foundation, False otherwise
    """
    return query_type in [QueryType.SURAH_SPECIFIC, QueryType.QURAN_GENERAL]

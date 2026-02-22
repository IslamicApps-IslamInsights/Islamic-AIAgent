"""
Islamic Knowledge Tools for AgentScope
These tools provide Islamic knowledge, prayer times, and religious guidance
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import math
from hijri_converter import Hijri, Gregorian

class IslamicKnowledgeTools:
    """Collection of Islamic knowledge and utility tools"""
    
    def __init__(self):
        self.quran_verses = {
            'al-fatiha': {
                'arabic': 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ الرَّحْمَٰنِ الرَّحِيمِ مَالِكِ يَوْمِ الدِّينِ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ',
                'translation': 'In the name of Allah, the Entirely Merciful, the Especially Merciful. [All] praise is [due] to Allah, Lord of the worlds - The Entirely Merciful, the Especially Merciful, Sovereign of the Day of Recompense. It is You we worship and You we ask for help. Guide us to the straight path - The path of those upon whom You have bestowed favor, not of those who have evoked [Your] anger or of those who are astray.',
                'reference': 'Surah Al-Fatiha (1:1-7)'
            },
            'ayat-kursi': {
                'arabic': 'اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَنْ ذَا الَّذِي يَشْفَعُ عِنْدَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ',
                'translation': 'Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth. Who is it that can intercede with Him except by His permission? He knows what is before them and what will be after them, and they encompass not a thing of His knowledge except for what He wills. His Kursi extends over the heavens and the earth, and their preservation tires Him not. And He is the Most High, the Most Great.',
                'reference': 'Surah Al-Baqarah (2:255)'
            }
        }
        
        self.hadith_collection = [
            {
                'text': 'The Prophet (ﷺ) said: "The believers in their mutual kindness, compassion, and sympathy are just one body - when a limb suffers, the whole body responds to it with wakefulness and fever."',
                'reference': 'Sahih al-Bukhari 6011',
                'topic': 'unity, compassion'
            },
            {
                'text': 'The Prophet (ﷺ) said: "None of you truly believes until he loves for his brother what he loves for himself."',
                'reference': 'Sahih al-Bukhari 13',
                'topic': 'brotherhood, faith'
            },
            {
                'text': 'The Prophet (ﷺ) said: "Whoever removes a worldly grief from a believer, Allah will remove from him one of the griefs of the Day of Judgment."',
                'reference': 'Sahih Muslim 2699',
                'topic': 'helping others, reward'
            }
        ]
        
        self.duas = {
            'morning': {
                'arabic': 'أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ',
                'transliteration': 'Asbahna wa asbahal-mulku lillahi, walhamdu lillah',
                'translation': 'We have reached the morning and at this very time unto Allah belongs all sovereignty, and all praise is for Allah.'
            },
            'evening': {
                'arabic': 'أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ',
                'transliteration': 'Amsayna wa amsal-mulku lillahi, walhamdu lillah',
                'translation': 'We have reached the evening and at this very time unto Allah belongs all sovereignty, and all praise is for Allah.'
            }
        }

def get_quran_verse(verse_name: str) -> str:
    """
    Get a Quran verse with Arabic text and translation
    
    Args:
        verse_name: Name of the verse (e.g., 'al-fatiha', 'ayat-kursi')
    
    Returns:
        Formatted verse with Arabic, translation, and reference
    """
    tools = IslamicKnowledgeTools()
    
    if verse_name.lower() in tools.quran_verses:
        verse = tools.quran_verses[verse_name.lower()]
        return f"""📖 **{verse['reference']}**

**Arabic:**
{verse['arabic']}

**Translation:**
{verse['translation']}

**Reference:** {verse['reference']}"""
    else:
        return f"❌ Verse '{verse_name}' not found. Available verses: {', '.join(tools.quran_verses.keys())}"

def get_hadith(topic: Optional[str] = None) -> str:
    """
    Get an authentic hadith, optionally filtered by topic
    
    Args:
        topic: Optional topic to filter hadith (e.g., 'kindness', 'faith')
    
    Returns:
        Formatted hadith with text, reference, and authenticity
    """
    tools = IslamicKnowledgeTools()
    
    if topic:
        filtered_hadith = [h for h in tools.hadith_collection if topic.lower() in h['topic'].lower()]
        if filtered_hadith:
            hadith = filtered_hadith[0]
        else:
            hadith = tools.hadith_collection[0]
    else:
        import random
        hadith = random.choice(tools.hadith_collection)
    
    return f"""⭐ **Authentic Hadith**

**The Prophet (ﷺ) said:**
"{hadith['text']}"

**Reference:** {hadith['reference']}
**Topic:** {hadith['topic']}

✅ **Authenticity:** This hadith is from Sahih collections."""

def get_dua(occasion: str) -> str:
    """
    Get a dua for specific occasions
    
    Args:
        occasion: Occasion for the dua (e.g., 'morning', 'evening')
    
    Returns:
        Formatted dua with Arabic, transliteration, and translation
    """
    tools = IslamicKnowledgeTools()
    
    if occasion.lower() in tools.duas:
        dua = tools.duas[occasion.lower()]
        return f"""🤲 **{occasion.title()} Dua**

**Arabic:**
{dua['arabic']}

**Transliteration:**
{dua['transliteration']}

**Translation:**
{dua['translation']}

**Best Time:** {occasion.title()} time or after related prayers"""
    else:
        return f"❌ Dua for '{occasion}' not found. Available occasions: {', '.join(tools.duas.keys())}"

def get_prayer_times(latitude: float, longitude: float) -> str:
    """
    Get prayer times for a specific location
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    
    Returns:
        Formatted prayer times for today
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://api.aladhan.com/v1/timings/{today}"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'method': 2  # Islamic Society of North America (ISNA)
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            timings = data['data']['timings']
            
            def format_time(time_str):
                """Convert 24-hour to 12-hour format"""
                hour, minute = time_str.split(':')
                hour = int(hour)
                ampm = 'AM' if hour < 12 else 'PM'
                if hour == 0:
                    hour = 12
                elif hour > 12:
                    hour -= 12
                return f"{hour}:{minute} {ampm}"
            
            return f"""🕐 **Today's Prayer Times**

🌅 **Fajr**: {format_time(timings['Fajr'])}
☀️ **Dhuhr**: {format_time(timings['Dhuhr'])}
🌤️ **Asr**: {format_time(timings['Asr'])}
🌅 **Maghrib**: {format_time(timings['Maghrib'])}
🌙 **Isha**: {format_time(timings['Isha'])}

📍 **Location-based times** for your area
💡 Times calculated using precise coordinates. May Allah accept your prayers!"""
        else:
            return "❌ Unable to fetch prayer times. Please try again later."
    except Exception as e:
        return f"❌ Error getting prayer times: {str(e)}"

def get_qibla_direction(latitude: float, longitude: float) -> str:
    """
    Calculate Qibla direction from given coordinates
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
    
    Returns:
        Qibla direction in degrees and compass direction
    """
    # Kaaba coordinates
    kaaba_lat = 21.4225
    kaaba_lon = 39.8262
    
    # Convert to radians
    lat1 = math.radians(latitude)
    lat2 = math.radians(kaaba_lat)
    lon1 = math.radians(longitude)
    lon2 = math.radians(kaaba_lon)
    
    # Calculate bearing
    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    # Convert to compass direction
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                 "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(bearing / 22.5) % 16
    compass_direction = directions[index]
    
    return f"""🧭 **Qibla Direction**

📍 **From your location:**
• **Bearing**: {bearing:.1f}°
• **Compass Direction**: {compass_direction}

🕌 **Toward the Kaaba in Mecca**
• Use a compass app for precise direction
• Face this direction during prayer

🤲 **Dua when facing Qibla:**
*"Wajjahtu wajhiya lilladhi fatara as-samawati wal-arda hanifan musliman wa ma ana min al-mushrikin"*"""

def get_hijri_date() -> str:
    """
    Get current Hijri date
    
    Returns:
        Current Hijri date in formatted string
    """
    try:
        today = datetime.now()
        hijri_date = Hijri.from_gregorian(today.year, today.month, today.day)
        
        hijri_months = [
            'Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Thani",
            'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', "Sha'ban",
            'Ramadan', 'Shawwal', "Dhu al-Qi'dah", 'Dhu al-Hijjah'
        ]
        
        month_name = hijri_months[hijri_date.month - 1]
        
        return f"""📅 **Current Hijri Date**

🌙 **Today**: {hijri_date.day} {month_name} {hijri_date.year} AH

📝 **Important Islamic Events:**
• **12 Rabi' al-Awwal**: Mawlid an-Nabi (ﷺ)
• **27 Rajab**: Isra and Mi'raj Night
• **15 Sha'ban**: Laylat al-Bara'ah
• **Ramadan**: Month of Fasting
• **Eid al-Fitr**: Festival after Ramadan
• **10 Dhul Hijjah**: Eid al-Adha

💡 Dates may vary by 1-2 days based on moon sighting in your region."""
    except Exception as e:
        return f"❌ Error calculating Hijri date: {str(e)}"

def get_islamic_guidance(topic: str) -> str:
    """
    Get Islamic guidance on various topics
    
    Args:
        topic: Topic for guidance (e.g., 'prayer', 'fasting', 'charity')
    
    Returns:
        Islamic guidance on the requested topic
    """
    guidance = {
        'prayer': """🕌 **Prayer (Salah) Guidance**

**Five Daily Prayers:**
• **Fajr** (2 rakats) - Dawn prayer
• **Dhuhr** (4 rakats) - Midday prayer  
• **Asr** (4 rakats) - Afternoon prayer
• **Maghrib** (3 rakats) - Sunset prayer
• **Isha** (4 rakats) - Night prayer

**Before Prayer:**
• Perform Wudu (ablution)
• Face Qibla direction
• Make intention (Niyyah)
• Use clean place and proper dress

**Prayer Steps:**
1. **Takbir** - "Allahu Akbar" (raise hands)
2. **Qiyam** - Recite Al-Fatiha + Surah
3. **Ruku** - Bow: "Subhana Rabbiyal Azeem"
4. **Sujud** - Prostrate: "Subhana Rabbiyal A'la"
5. **Tashahhud** - Sit and recite At-Tahiyyat
6. **Taslim** - "Assalamu alaikum wa rahmatullah"

🎯 Focus on Khushu (concentration) and presence of heart.""",

        'fasting': """🌙 **Fasting (Sawm) Guidance**

**Ramadan Fasting:**
• Abstain from food, drink, and marital relations from dawn to sunset
• Make intention (Niyyah) before Fajr
• Break fast at Maghrib time

**Suhur (Pre-dawn meal):**
• Eat before Fajr prayer
• The Prophet (ﷺ) said: "Take suhur, for there is blessing in it"

**Iftar (Breaking fast):**
• Break fast with dates and water (Sunnah)
• Make dua before breaking fast
• Don't overeat

**Spiritual Benefits:**
• Develops self-control and patience
• Increases empathy for the poor
• Purifies the soul
• Brings closeness to Allah""",

        'charity': """💰 **Charity (Zakat & Sadaqah) Guidance**

**Zakat (Obligatory Charity):**
• 2.5% of qualifying wealth annually
• Nisab: Equivalent to 85 grams of gold
• Must own nisab for full lunar year

**Who Receives Zakat:**
• The poor and needy
• Zakat collectors
• Those whose hearts are to be reconciled
• Slaves seeking freedom
• Debtors
• In the way of Allah
• Travelers in need

**Sadaqah (Voluntary Charity):**
• Any good deed is sadaqah
• Smile, helping others, removing harm from path
• Even a kind word is sadaqah

**Benefits:**
• Purifies wealth and soul
• Increases blessings (barakah)
• Helps the community
• Brings Allah's mercy"""
    }
    
    topic_lower = topic.lower()
    for key, value in guidance.items():
        if key in topic_lower:
            return value
    
    return f"""📚 **Islamic Guidance Available**

I can provide guidance on:
• **Prayer** - How to pray, prayer times, etc.
• **Fasting** - Ramadan fasting rules and benefits
• **Charity** - Zakat and Sadaqah guidance
• **Quran** - Verses and their meanings
• **Hadith** - Authentic sayings of Prophet (ﷺ)
• **Duas** - Supplications for different occasions

Please specify which topic you'd like guidance on."""

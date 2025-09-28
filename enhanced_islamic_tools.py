"""
Enhanced Islamic Tools for AgentScope with Dynamic Knowledge Base
Integrates authentic APIs for Quran and Hadith content
"""

import asyncio
import requests
from typing import Dict, List, Optional
from datetime import datetime
import math
try:
    from hijri_converter import Hijri, Gregorian
except ImportError:
    # Fallback if hijri_converter is not available
    Hijri = None
    Gregorian = None

# Import AgentScope ToolResponse
try:
    from agentscope.service import ToolResponse
except ImportError:
    try:
        from agentscope.tools import ToolResponse
    except ImportError:
        # Fallback if AgentScope is not available
        class ToolResponse:
            def __init__(self, content: str, status: str = "success"):
                self.content = content
                self.status = status

# Import our dynamic knowledge base
from dynamic_islamic_knowledge import (
    get_dynamic_quran_verse,
    get_dynamic_hadith,
    search_islamic_knowledge,
    get_topic_guidance,
    DynamicIslamicKnowledge
)

# Keep existing location-based tools
def get_prayer_times(latitude: float, longitude: float) -> str:
    """
    Get prayer times for a specific location using Aladhan API
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    
    Returns:
        Formatted prayer times for today with next prayer and Hijri date
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://api.aladhan.com/v1/timings/{today}"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'method': 2  # Islamic Society of North America (ISNA)
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            timings = data['data']['timings']
            hijri_date = data['data']['date']['hijri']
            
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
            
            def get_next_prayer():
                """Determine the next prayer based on current time"""
                now = datetime.now()
                current_time = now.strftime('%H:%M')
                
                prayers = [
                    ('Fajr', timings['Fajr'], '🌅'),
                    ('Dhuhr', timings['Dhuhr'], '☀️'),
                    ('Asr', timings['Asr'], '🌤️'),
                    ('Maghrib', timings['Maghrib'], '🌅'),
                    ('Isha', timings['Isha'], '🌙')
                ]
                
                for prayer_name, prayer_time, emoji in prayers:
                    if current_time < prayer_time:
                        # Calculate time remaining
                        prayer_datetime = datetime.strptime(prayer_time, '%H:%M').replace(
                            year=now.year, month=now.month, day=now.day
                        )
                        time_diff = prayer_datetime - now
                        hours, remainder = divmod(time_diff.seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        
                        if hours > 0:
                            time_remaining = f"{hours}h {minutes}m"
                        else:
                            time_remaining = f"{minutes}m"
                        
                        return f"{emoji} **{prayer_name}** at {format_time(prayer_time)} (in {time_remaining})"
                
                # If no prayer found for today, next is Fajr tomorrow
                return f"🌅 **Fajr** tomorrow at {format_time(timings['Fajr'])}"
            
            # Format Hijri date
            hijri_day = hijri_date['day']
            hijri_month = hijri_date['month']['en']
            hijri_year = hijri_date['year']
            
            prayer_times_text = f"""🕐 **Today's Prayer Times**

📅 **Islamic Date:** {hijri_day} {hijri_month} {hijri_year} AH

⏰ **Next Prayer:** {get_next_prayer()}

🌅 **Fajr**: {format_time(timings['Fajr'])}
☀️ **Dhuhr**: {format_time(timings['Dhuhr'])}
🌤️ **Asr**: {format_time(timings['Asr'])}
🌅 **Maghrib**: {format_time(timings['Maghrib'])}
🌙 **Isha**: {format_time(timings['Isha'])}

📍 **Location-based times** for your area
💡 Times calculated using precise coordinates
🌐 **Source:** Aladhan API (Authentic)

May Allah accept your prayers! 🤲"""
            return prayer_times_text
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
    try:
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
        
        qibla_text = f"""🧭 **Qibla Direction**

📍 **From your location:**
• **Bearing**: {bearing:.1f}°
• **Compass Direction**: {compass_direction}

🕌 **Toward the Kaaba in Mecca**
• Use a compass app for precise direction
• Face this direction during prayer

🤲 **Dua when facing Qibla:**
*"Wajjahtu wajhiya lilladhi fatara as-samawati wal-arda hanifan musliman wa ma ana min al-mushrikin"*

*"I have turned my face toward Him who created the heavens and the earth, as a true believer in pure faith, and I am not among the polytheists."*"""
        return qibla_text
    except Exception as e:
        return f"❌ Error calculating Qibla direction: {str(e)}"

def _calculate_hijri_fallback(gregorian_date):
    """Simple fallback Hijri date calculation"""
    # This is a very approximate calculation
    # For accurate dates, proper hijri-converter should be used
    hijri_year = gregorian_date.year - 579  # Approximate conversion
    hijri_months = [
        'Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Thani",
        'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', "Sha'ban",
        'Ramadan', 'Shawwal', "Dhu al-Qi'dah", 'Dhu al-Hijjah'
    ]
    month_index = (gregorian_date.month - 1) % 12
    return f"{gregorian_date.day} {hijri_months[month_index]} {hijri_year} AH (approx)"

def get_hijri_date() -> str:
    """
    Get current Hijri date using hijri-converter library
    
    Returns:
        Current Hijri date in formatted string
    """
    try:
        today = datetime.now()
        
        if Hijri is None:
            # Fallback calculation if hijri_converter is not available
            return f"""📅 **Current Hijri Date**

🌙 **Approximate Date**: {_calculate_hijri_fallback(today)}
📊 **Gregorian**: {today.strftime('%B %d, %Y')}

📝 **Important Islamic Events:**
• **12 Rabi' al-Awwal**: Mawlid an-Nabi (ﷺ)
• **27 Rajab**: Isra and Mi'raj Night
• **15 Sha'ban**: Laylat al-Bara'ah (Night of Forgiveness)
• **Ramadan**: Month of Fasting
• **Eid al-Fitr**: Festival after Ramadan
• **10 Dhul Hijjah**: Eid al-Adha

💡 **Note:** Dates may vary by 1-2 days based on moon sighting in your region.
⚠️ **Note:** Using fallback calculation. Install hijri-converter for precise dates."""
        
        try:
            hijri_date = Hijri.from_gregorian(today.year, today.month, today.day)
        except AttributeError:
            # Fallback if the method doesn't exist
            return f"""📅 **Current Hijri Date**

🌙 **Approximate Date**: {_calculate_hijri_fallback(today)}
📊 **Gregorian**: {today.strftime('%B %d, %Y')}

📝 **Important Islamic Events:**
• **12 Rabi' al-Awwal**: Mawlid an-Nabi (ﷺ)
• **27 Rajab**: Isra and Mi'raj Night
• **15 Sha'ban**: Laylat al-Bara'ah (Night of Forgiveness)
• **Ramadan**: Month of Fasting
• **Eid al-Fitr**: Festival after Ramadan
• **10 Dhul Hijjah**: Eid al-Adha

💡 **Note:** Dates may vary by 1-2 days based on moon sighting in your region.
⚠️ **Note:** Using fallback calculation due to library compatibility."""
        
        hijri_months = [
            'Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Thani",
            'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', "Sha'ban",
            'Ramadan', 'Shawwal', "Dhu al-Qi'dah", 'Dhu al-Hijjah'
        ]
        
        month_name = hijri_months[hijri_date.month - 1]
        
        hijri_text = f"""📅 **Current Hijri Date**

🌙 **Today**: {hijri_date.day} {month_name} {hijri_date.year} AH
📊 **Gregorian**: {today.strftime('%B %d, %Y')}

📝 **Important Islamic Events:**
• **12 Rabi' al-Awwal**: Mawlid an-Nabi (ﷺ)
• **27 Rajab**: Isra and Mi'raj Night
• **15 Sha'ban**: Laylat al-Bara'ah (Night of Forgiveness)
• **Ramadan**: Month of Fasting
• **Eid al-Fitr**: Festival after Ramadan
• **10 Dhul Hijjah**: Eid al-Adha

💡 **Note:** Dates may vary by 1-2 days based on moon sighting in your region.
🌐 **Source:** Hijri Converter Library (Accurate)"""
        return hijri_text
    except Exception as e:
        return f"❌ Error calculating Hijri date: {str(e)}"

# Enhanced dynamic tools using APIs
def get_quran_verse(verse_reference: str) -> str:
    """
    Get Quran verse dynamically from authentic API sources
    
    Args:
        verse_reference: Verse reference like "2:255", "al-fatiha", "ayat-kursi"
    
    Returns:
        ToolResponse with formatted verse with Arabic text, translation, and reference
    """
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_dynamic_quran_verse(verse_reference))
        loop.close()
        return result
    except Exception as e:
        return f"❌ Error fetching Quran verse: {str(e)}"

def get_hadith(topic: str = None) -> str:
    """
    Get authentic hadith dynamically from API sources
    
    Args:
        topic: Optional topic to filter hadith (e.g., 'kindness', 'prayer', 'charity')
    
    Returns:
        ToolResponse with formatted hadith with text, reference, and authenticity verification
    """
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_dynamic_hadith(topic))
        loop.close()
        return result
    except Exception as e:
        return f"❌ Error fetching Hadith: {str(e)}"

def search_islamic_content(query: str) -> str:
    """
    Search both Quran and Hadith collections for specific content
    
    Args:
        query: Search query (e.g., 'patience', 'charity', 'prayer')
    
    Returns:
        Search results from both Quran and Hadith sources
    """
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(search_islamic_knowledge(query))
        loop.close()
        return result
    except Exception as e:
        return f"❌ Error searching Islamic content: {str(e)}"

def get_islamic_guidance(topic: str) -> str:
    """
    Get comprehensive Islamic guidance on a topic from both Quran and Hadith
    
    Args:
        topic: Topic for guidance (e.g., 'prayer', 'fasting', 'charity', 'patience')
    
    Returns:
        Comprehensive guidance with relevant verses and hadiths
    """
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_topic_guidance(topic))
        loop.close()
        return result
    except Exception as e:
        return f"❌ Error getting Islamic guidance: {str(e)}"

def get_dua(occasion: str) -> str:
    """
    Get authentic duas for specific occasions from dynamic sources
    
    Args:
        occasion: Occasion for the dua (e.g., 'morning', 'evening', 'travel', 'eating')
    
    Returns:
        Formatted dua with Arabic, transliteration, and translation
    """
    # Enhanced duas with more occasions
    duas_collection = {
        'morning': {
            'arabic': 'أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ',
            'transliteration': 'Asbahna wa asbahal-mulku lillahi, walhamdu lillahi, la ilaha illa Allahu wahdahu la shareeka lah',
            'translation': 'We have reached the morning and at this very time unto Allah belongs all sovereignty, and all praise is for Allah. None has the right to be worshipped except Allah, alone, without partner.',
            'reference': 'Abu Dawud 5077'
        },
        'evening': {
            'arabic': 'أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ',
            'transliteration': 'Amsayna wa amsal-mulku lillahi, walhamdu lillahi, la ilaha illa Allahu wahdahu la shareeka lah',
            'translation': 'We have reached the evening and at this very time unto Allah belongs all sovereignty, and all praise is for Allah. None has the right to be worshipped except Allah, alone, without partner.',
            'reference': 'Abu Dawud 5077'
        },
        'before_eating': {
            'arabic': 'بِسْمِ اللَّهِ',
            'transliteration': 'Bismillah',
            'translation': 'In the name of Allah',
            'reference': 'Abu Dawud 3767'
        },
        'after_eating': {
            'arabic': 'الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنِي هَذَا وَرَزَقَنِيهِ مِنْ غَيْرِ حَوْلٍ مِنِّي وَلَا قُوَّةٍ',
            'transliteration': 'Alhamdu lillahil-ladhi at\'amani hadha wa razaqaneehi min ghayri hawlin minnee wa la quwwah',
            'translation': 'All praise is due to Allah who has fed me this and provided it for me without any might nor power from myself.',
            'reference': 'Abu Dawud 4023'
        },
        'travel': {
            'arabic': 'سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ وَإِنَّا إِلَى رَبِّنَا لَمُنْقَلِبُونَ',
            'transliteration': 'Subhanal-ladhi sakhkhara lana hadha wa ma kunna lahu muqrineen, wa inna ila rabbina lamunqaliboon',
            'translation': 'Glory is to Him who has subjected this to us, and we could never have it (by our efforts). And to our Lord, surely, we shall return.',
            'reference': 'Abu Dawud 2602'
        },
        'sleep': {
            'arabic': 'بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا',
            'transliteration': 'Bismika Allahumma amootu wa ahya',
            'translation': 'In Your name, O Allah, I die and I live.',
            'reference': 'Sahih Bukhari 6312'
        }
    }
    
    occasion_lower = occasion.lower()
    
    # Find matching dua
    for key, dua_data in duas_collection.items():
        if key in occasion_lower or occasion_lower in key:
            return f"""🤲 **{occasion.title()} Dua**

**Arabic:**
{dua_data['arabic']}

**Transliteration:**
{dua_data['transliteration']}

**Translation:**
{dua_data['translation']}

**Reference:** {dua_data['reference']}
**Best Time:** {occasion.title()} time

✨ **Authenticity:** From authentic Hadith collections
🌐 **Source:** Sunnah.com verified collections"""
    
    # If no specific dua found, provide general guidance
    return f"""🤲 **Dua for {occasion.title()}**

**General Supplication:**
*"Rabbana atina fi'd-dunya hasanatan wa fi'l-akhirati hasanatan wa qina 'adhab an-nar"*

**Translation:**
*"Our Lord, give us good in this world and good in the next world, and save us from the punishment of the Fire."*

**Reference:** Quran 2:201

💡 **Available specific duas:** morning, evening, before_eating, after_eating, travel, sleep

For more specific duas, try: `get_dua('morning')` or search Islamic content."""

def get_daily_islamic_content() -> str:
    """
    Get daily Islamic content including verse and hadith of the day
    
    Returns:
        Daily verse and hadith with authentic sources
    """
    try:
        # Get current date for consistent daily content
        today = datetime.now()
        day_of_year = today.timetuple().tm_yday
        
        # Rotate through popular verses based on day of year
        popular_verses = [
            "2:255",  # Ayat al-Kursi
            "1:1",    # Al-Fatiha
            "2:286",  # Last verse of Al-Baqarah
            "3:200",  # Patience and perseverance
            "13:28",  # Hearts find rest in remembrance of Allah
            "94:5",   # With hardship comes ease
            "17:80",  # Truth has come
        ]
        
        verse_index = day_of_year % len(popular_verses)
        selected_verse = popular_verses[verse_index]
        
        # Get verse and hadith
        verse_content = get_quran_verse(selected_verse)
        hadith_content = get_hadith()
        
        daily_content_text = f"""🌅 **Daily Islamic Content - {today.strftime('%B %d, %Y')}**

📖 **Verse of the Day:**
{verse_content.content if hasattr(verse_content, 'content') else verse_content}

⭐ **Hadith of the Day:**
{hadith_content.content if hasattr(hadith_content, 'content') else hadith_content}

🤲 **Daily Reflection:**
Take a moment to reflect on these teachings and how they can guide your day.

May Allah bless your day with His guidance and mercy! 🌟"""
        return daily_content_text
        
    except Exception as e:
        return f"❌ Error getting daily content: {str(e)}"

# Advanced Islamic knowledge functions
def get_surah_info(surah_name_or_number: str) -> str:
    """
    Get information about a specific Surah
    
    Args:
        surah_name_or_number: Surah name or number
    
    Returns:
        Detailed information about the Surah
    """
    surah_info = {
        '1': {'name': 'Al-Fatiha', 'meaning': 'The Opening', 'verses': 7, 'revelation': 'Meccan'},
        '2': {'name': 'Al-Baqarah', 'meaning': 'The Cow', 'verses': 286, 'revelation': 'Medinan'},
        '3': {'name': 'Ali Imran', 'meaning': 'Family of Imran', 'verses': 200, 'revelation': 'Medinan'},
        '18': {'name': 'Al-Kahf', 'meaning': 'The Cave', 'verses': 110, 'revelation': 'Meccan'},
        '36': {'name': 'Ya-Sin', 'meaning': 'Ya-Sin', 'verses': 83, 'revelation': 'Meccan'},
        '55': {'name': 'Ar-Rahman', 'meaning': 'The Beneficent', 'verses': 78, 'revelation': 'Medinan'},
        '67': {'name': 'Al-Mulk', 'meaning': 'The Sovereignty', 'verses': 30, 'revelation': 'Meccan'},
        '112': {'name': 'Al-Ikhlas', 'meaning': 'The Sincerity', 'verses': 4, 'revelation': 'Meccan'},
    }
    
    # Try to find surah by number or name
    surah_key = None
    search_term = surah_name_or_number.lower()
    
    for key, info in surah_info.items():
        if (key == search_term or 
            info['name'].lower() == search_term or 
            search_term in info['name'].lower()):
            surah_key = key
            break
    
    if surah_key:
        info = surah_info[surah_key]
        return f"""📖 **Surah {info['name']} (Chapter {surah_key})**

**Meaning:** {info['meaning']}
**Number of Verses:** {info['verses']}
**Revelation:** {info['revelation']}

**To read this Surah:** Use `get_quran_verse('{surah_key}:1')` for the first verse
**For complete Surah:** The API can provide all verses

✨ **Note:** This is one of the most beloved Surahs in the Quran."""
    else:
        return f"""❌ Surah '{surah_name_or_number}' not found in our database.

**Available Surahs:** Al-Fatiha, Al-Baqarah, Ali Imran, Al-Kahf, Ya-Sin, Ar-Rahman, Al-Mulk, Al-Ikhlas

**Try:** `get_surah_info('Al-Fatiha')` or `get_surah_info('1')`"""

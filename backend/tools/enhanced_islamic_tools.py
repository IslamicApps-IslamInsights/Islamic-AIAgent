"""
Enhanced Islamic Tools for AgentScope with Dynamic Knowledge Base
Integrates authentic APIs for Quran and Hadith content
"""

import asyncio
import requests
from typing import Dict, List, Optional
from datetime import datetime
import math
import time
from functools import wraps

# --- Global Caching System ---
class ServiceCache:
    """A simple TTL-based cache for scholarly services"""
    _cache = {}
    
    @classmethod
    def get(cls, key: str):
        if key in cls._cache:
            val, expiry = cls._cache[key]
            if time.time() < expiry:
                return val
            cls._cache.pop(key, None)
        return None
    
    @classmethod
    def set(cls, key: str, value: any, ttl: int = 3600):
        cls._cache[key] = (value, time.time() + ttl)

def cached_service(ttl: int = 3600):
    """Decorator for caching service results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique key based on function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_val = ServiceCache.get(key)
            if cached_val is not None:
                return cached_val
            
            result = func(*args, **kwargs)
            ServiceCache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

def run_async(coro):
    """Safe bridge for running async in sync context, reusing loop if available"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(asyncio.run, coro).result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

# Defer heavy imports to reduce startup latency
def _get_hijri():
    try:
        from hijri_converter import Hijri, Gregorian
        return Hijri, Gregorian
    except ImportError:
        try:
            # Try alternate library name often installed with pip
            from hijridate import Hijri, Gregorian
            return Hijri, Gregorian
        except ImportError:
            return None, None

# Import AgentScope ToolResponse
# Agentscope imports will be deferred

# Import our dynamic knowledge base
# Dynamic knowledge imports will be deferred

# Keep existing location-based tools
def calculate_zakat(cash: float = 0, gold_grams: float = 0, silver_grams: float = 0, investments: float = 0, business_assets: float = 0, debts: float = 0) -> str:
    """
    Enhanced Zakat Calculator based on Islamic Fiqh
    
    Args:
        cash: Total cash on hand/in bank
        gold_grams: Total gold weight in grams
        silver_grams: Total silver weight in grams
        investments: Total value of investments (stocks, etc.)
        business_assets: Value of business inventory/assets
        debts: Total deductible debts
    
    Returns:
        Formatted Zakat breakdown with Nisab verification
    """
    try:
        # Approximate Nisab values (should be updated via API in production)
        # Gold Nisab: 87.48 grams | Silver Nisab: 612.36 grams
        GOLD_PRICE_PER_GRAM = 85.0  # Approx USD
        SILVER_PRICE_PER_GRAM = 1.1  # Approx USD
        
        gold_value = gold_grams * GOLD_PRICE_PER_GRAM
        silver_value = silver_grams * SILVER_PRICE_PER_GRAM
        
        total_assets = cash + gold_value + silver_value + investments + business_assets
        net_assets = total_assets - debts
        
        # Nisab thresholds
        gold_nisab_threshold = 87.48 * GOLD_PRICE_PER_GRAM
        silver_nisab_threshold = 612.36 * SILVER_PRICE_PER_GRAM
        
        # In many Fiqh schools, the lower Nisab (usually silver) is used for the benefit of the poor
        nisab_met = net_assets >= silver_nisab_threshold
        
        zakat_due = 0
        if nisab_met:
            zakat_due = net_assets * 0.025  # 2.5%
            
        status_emoji = "✅" if nisab_met else "ℹ️"
        
        zakat_text = f"""⚖️ **Zakat Calculation Results**

💰 **Total Assets**: ${total_assets:,.2f}
💸 **Deductible Debts**: ${debts:,.2f}
📈 **Net Wealth**: ${net_assets:,.2f}

---
{status_emoji} **Nisab Status**: {"Above Nisab" if nisab_met else "Below Nisab"}
📊 **Current Nisab (Silver)**: Approx. ${silver_nisab_threshold:,.2f}
🧮 **Zakat Rate**: 2.5%

{"🤲 **Zakat Due: $" + f"{zakat_due:,.2f}" + "**" if nisab_met else "🤲 **No Zakat Due** (Wealth is below Nisab)"}

---
💡 **Fiqh Details:**
• Zakat is mandatory on wealth held for one lunar year (*Hawl*).
• Rate is 2.5% of net qualified assets.
• This calculation uses the Silver Nisab (preferred by many scholars for charity).

*Note: Prices are approximate. Please consult with a local scholar for complex cases.*"""
        return zakat_text
    except Exception as e:
        return f"❌ Error calculating Zakat: {str(e)}"

@cached_service(ttl=3600)
def get_prayer_times(latitude: float, longitude: float, query_date: str = None) -> Dict:
    """
    Get prayer times and Hijri date for a specific location using Aladhan API
    """
    try:
        if query_date:
            url = f"https://api.aladhan.com/v1/timings/{query_date}"
        else:
            # Use real-time coordinate-based timings (auto-determines date for the user's timezone)
            url = "https://api.aladhan.com/v1/timings"
            
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'method': 2  # ISNA
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            api_data = response.json()['data']
            timings = api_data['timings']
            hijri_info = api_data['date']['hijri']
            gregorian_info = api_data['date']['gregorian']
            
            def format_time(time_str):
                """Convert 24-hour to 12-hour format"""
                time_str = time_str.split(' ')[0] # Strip timezone tags
                hour, minute = time_str.split(':')
                hour = int(hour)
                ampm = 'AM' if hour < 12 else 'PM'
                if hour == 0:
                    hour = 12
                elif hour > 12:
                    hour -= 12
                return f"{hour}:{minute} {ampm}"
            
            def get_next_prayer():
                """Determine the next prayer and time remaining"""
                import pytz
                
                timezone_str = api_data.get('meta', {}).get('timezone', 'UTC')
                try:
                    local_tz = pytz.timezone(timezone_str)
                    now = datetime.now(local_tz)
                except:
                    now = datetime.now()
                    
                current_time = now.strftime('%H:%M')
                
                prayers_list = [
                    ('Fajr', timings['Fajr'].split(' ')[0], '🌅'),
                    ('Dhuhr', timings['Dhuhr'].split(' ')[0], '☀️'),
                    ('Asr', timings['Asr'].split(' ')[0], '🌤️'),
                    ('Maghrib', timings['Maghrib'].split(' ')[0], '🌅'),
                    ('Isha', timings['Isha'].split(' ')[0], '🌙')
                ]
                
                for prayer_name, prayer_time, emoji in prayers_list:
                    if current_time < prayer_time:
                        try:
                            h, m = map(int, prayer_time.split(':'))
                            prayer_datetime = now.replace(hour=h, minute=m, second=0, microsecond=0)
                            time_diff = prayer_datetime - now
                            hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                            minutes, _ = divmod(remainder, 60)
                            
                            time_remaining = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                            return {
                                "name": prayer_name,
                                "time": format_time(prayer_time),
                                "remaining": time_remaining,
                                "emoji": emoji,
                                "text": f"{emoji} **{prayer_name}** at {format_time(prayer_time)} (in {time_remaining})"
                            }
                        except:
                            pass
                
                # Case: After Isha, next is Fajr tomorrow
                return {
                    "name": "Fajr",
                    "time": format_time(timings['Fajr']),
                    "remaining": "Tomorrow",
                    "emoji": "🌅",
                    "text": f"🌅 **Fajr** tomorrow at {format_time(timings['Fajr'])}"
                }
            
            next_prayer_info = get_next_prayer()
            hijri_day = hijri_info['day']
            hijri_month = hijri_info['month']['en']
            hijri_year = hijri_info['year']
            
            prayer_times_text = f"""🕐 **Today's Prayer Times**

📅 **Islamic Date:** {hijri_day} {hijri_month} {hijri_year} AH

⏰ **Next Prayer:** {next_prayer_info['text']}

🌅 **Fajr**: {format_time(timings['Fajr'])}
☀️ **Dhuhr**: {format_time(timings['Dhuhr'])}
🌤️ **Asr**: {format_time(timings['Asr'])}
🌅 **Maghrib**: {format_time(timings['Maghrib'])}
🌙 **Isha**: {format_time(timings['Isha'])}

📍 **Location**: {latitude}, {longitude}
💡 Times calculated using precise coordinates
🌐 **Source:** Aladhan API (Authentic)

May Allah accept your prayers! 🤲"""

            return {
                "text": prayer_times_text,
                "hijri": f"{hijri_day} {hijri_month} {hijri_year} AH",
                "hijri_obj": hijri_info,
                "gregorian": gregorian_info['date'],
                "timings": timings,
                "next_prayer": next_prayer_info
            }
        else:
            return {"error": "Unable to fetch prayer times."}
    except Exception as e:
        return {"error": f"Error getting prayer times: {str(e)}"}

@cached_service(ttl=3600)
def get_prayer_times_by_address(address: str) -> Dict:
    """Get prayer times using a city name or address"""
    try:
        url = "https://api.aladhan.com/v1/timingsByAddress"
        params = {'address': address, 'method': 2}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            api_data = response.json()['data']
            lat = api_data['meta']['latitude']
            lng = api_data['meta']['longitude']
            
            # Forward the coordinates to the main precision function
            res = get_prayer_times(lat, lng)
            if isinstance(res, dict) and "text" in res:
                # Update the location string to show the city
                res["text"] = res["text"].replace(
                    f"📍 **Location**: {lat}, {lng}",
                    f"📍 **Location**: {address.title()} (Geocoded)"
                )
            return res
        return {"error": "City not found."}
    except Exception as e:
        return {"error": f"Error resolving city: {str(e)}"}

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
        
        qibla_text = f"""🧭 **Qibla Direction Calculated**
📍 **Bearing**: {bearing:.2f}° from North ({compass_direction})
🕌 **Target**: Holy Kaaba, Makkah

*Note: Please ensure your device is level for accuracy.*"""

        return {
            "bearing": bearing,
            "direction": compass_direction,
            "text": qibla_text
        }
    except Exception as e:
        return {"error": str(e)}

def _calculate_hijri_fallback(gregorian_date):
    """Simple fallback Hijri date calculation (Tabular)"""
    # This is a basic conversion, accurate within a day for some regions
    # 0 Hijri is approx 622-07-16
    from datetime import date
    reference_date = date(622, 7, 16)
    # Days since Hijra
    L = (gregorian_date.date() - reference_date).days
    
    # Simple tabular algorithm
    N = int(L / 10631)
    L = L % 10631
    J = int(L / 354)
    L = L % 354
    
    h_year = (N * 30) + J + 1
    # Very rough month/day for the remaining days in year
    h_month = int(L / 29.5) + 1
    h_day = int(L % 29.5) + 1

    hijri_months = [
        'Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Thani",
        'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', "Sha'ban",
        'Ramadan', 'Shawwal', "Dhu al-Qi'dah", 'Dhu al-Hijjah'
    ]
    
    month_index = min(max(h_month - 1, 0), 11)
    return f"{h_day} {hijri_months[month_index]} {h_year} AH (Approx)"

def get_islamic_calendar_events():
    """Returns upcoming major Islamic events and a full month grid for the dashboard"""
    try:
        today = datetime.now()
        Hijri, Gregorian = _get_hijri()
        
        if Hijri and Gregorian:
            h_now = Gregorian(today.year, today.month, today.day).to_hijri()
            h_month = h_now.month
            h_year = h_now.year
        else:
            # Fallback
            h_now_str = _calculate_hijri_fallback(today)
            # Rough parse: "10 Ramadan 1445 AH (Approx)"
            parts = h_now_str.split(' ')
            h_month_name = parts[1]
            h_year = int(parts[2])
            months = ['Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Thani", 'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', "Sha'ban", 'Ramadan', 'Shawwal', "Dhu al-Qi'dah", 'Dhu al-Hijjah']
            h_month = months.index(h_month_name) + 1
            h_now = None

        events = [
            {"name": "Ramadan Start", "month": 9, "day": 1, "type": "major"},
            {"name": "Eid al-Fitr", "month": 10, "day": 1, "type": "major"},
            {"name": "Hajj Season", "month": 12, "day": 1, "type": "major"},
            {"name": "Day of Arafah", "month": 12, "day": 9, "type": "sunnah"},
            {"name": "Eid al-Adha", "month": 12, "day": 10, "type": "major"},
            {"name": "Islamic New Year", "month": 1, "day": 1, "type": "major"},
            {"name": "Ashura", "month": 1, "day": 10, "type": "sunnah"},
            {"name": "Mawlid al-Nabi", "month": 3, "day": 12, "type": "commemoration"}
        ]
        
        # Generate full month grid (approx 30 days)
        month_grid = []
        for day in range(1, 31):
            day_events = [e for e in events if e['month'] == h_month and e['day'] == day]
            
            # Sunnah Fasting (White Days: 13, 14, 15)
            is_white_day = day in [13, 14, 15]
            if is_white_day:
                day_events.append({"name": "White Day Fast", "type": "sunnah_fast"})
            
            # Sunnah Fasting (Monday/Thursday - approximate as we don't have full Gregorian mapping here easily)
            # In a production app, we would map each Hijri day back to Gregorian for weekday calculation
            
            month_grid.append({
                "day": day,
                "is_current": h_now is not None and h_now.day == day,
                "events": day_events,
                "is_sunnah_fast": is_white_day
            })

        hijri_months = ['Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Thani", 'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', "Sha'ban", 'Ramadan', 'Shawwal', "Dhu al-Qi'dah", 'Dhu al-Hijjah']
        
        return {
            "current_hijri": str(h_now) if h_now else h_now_str,
            "month_name": hijri_months[h_month - 1],
            "month_number": h_month,
            "year": h_year,
            "month_grid": month_grid,
            "major_events": events
        }
    except Exception as e:
        return {"error": f"Unable to calculate events: {str(e)}"}

def get_hijri_date(latitude: Optional[float] = None, longitude: Optional[float] = None) -> str:
    """
    Get current Hijri date. Uses location-based API if coordinates provided.
    
    Args:
        latitude: User's latitude (optional)
        longitude: User's longitude (optional)
        
    Returns:
        Current Hijri date in formatted string
    """
    try:
        today = datetime.now()
        
        # If location is provided, use the precise API
        if latitude is not None and longitude is not None:
            try:
                # Reuse the prayer times logic which already fetches Hijri date
                res = get_prayer_times(latitude, longitude)
                if isinstance(res, dict) and "hijri" in res:
                    return f"""📅 **Localized Hijri Date**

🌙 **Today**: {res['hijri']}
📍 **Location**: {latitude}, {longitude}
📊 **Gregorian**: {res['gregorian']}

📝 **Note:** This date is accurately calculated for your specific location.
🌐 **Source:** Aladhan API (Authentic)"""
            except Exception as e:
                print(f"Localized Hijri Error: {e}")
                # Fall through to standard calculation
        
        Hijri, Gregorian = _get_hijri()
        if Hijri is None or Gregorian is None:
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
            # Correct API: Gregorian(y, m, d).to_hijri()
            hijri_date = Gregorian(today.year, today.month, today.day).to_hijri()
        except Exception as e:
            # Fallback if the API fails
            print(f"Hijri Conversion Error: {e}")
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
        from backend.tools.dynamic_islamic_knowledge import get_dynamic_quran_verse
        return run_async(get_dynamic_quran_verse(verse_reference))
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
        from backend.tools.dynamic_islamic_knowledge import get_dynamic_hadith
        return run_async(get_dynamic_hadith(topic))
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
        from backend.tools.dynamic_islamic_knowledge import search_islamic_knowledge
        return run_async(search_islamic_knowledge(query))
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
        from backend.tools.dynamic_islamic_knowledge import get_topic_guidance
        return run_async(get_topic_guidance(topic))
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

@cached_service(ttl=3600)
def get_daily_islamic_content() -> dict:
    """
    Get daily Islamic content including structured verse and hadith of the day
    
    Returns:
    Dict containing structured verse and hadith data
    """
    try:
        from backend.tools.dynamic_islamic_knowledge import DynamicIslamicKnowledge
        import asyncio
        from datetime import datetime
        
        # Initialize knowledge base
        knowledge = DynamicIslamicKnowledge()
        
        async def fetch_content():
            verse = await knowledge.get_verse_of_the_day()
            hadith = await knowledge.get_hadith_of_the_day()
            return verse, hadith
            
        verse_obj, hadith_obj = run_async(fetch_content())
        
        today = datetime.now()
        
        return {
            "date": today.strftime('%B %d, %Y'),
            "verse": {
                "arabic": verse_obj.text_arabic if verse_obj else "",
                "translation": verse_obj.text_english if verse_obj else "Unable to fetch verse",
                "reference": verse_obj.reference if verse_obj else "",
                "surah": verse_obj.surah_name if verse_obj else ""
            },
            "hadith": {
                "arabic": hadith_obj.text_arabic if hadith_obj else "",
                "translation": hadith_obj.text_english if hadith_obj else "Unable to fetch hadith",
                "narrator": hadith_obj.narrator if hadith_obj else "",
                "reference": hadith_obj.reference if hadith_obj else "",
                "grade": hadith_obj.grade if hadith_obj else ""
            },
            "reflection": "Take a moment to reflect on these divine teachings and how they can guide your heart today. May Allah bless you."
        }
        
    except Exception as e:
        print(f"Error in daily content: {e}")
        return {
            "error": str(e),
            "verse": {"translation": "Error fetching content"},
            "hadith": {"translation": "Error fetching content"}
        }

# Advanced Islamic knowledge functions
import os
import json

def get_surah_info(surah_name_or_number: str) -> str:
    """
    Get detailed information about any of the 114 Surahs using the expanded dataset.
    
    Args:
        surah_name_or_number: Surah name or number (1-114)
    """
    try:
        # Resolve absolute path to ensure data is found in the modular structure
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "knowledge", "data", "quran_surah_metadata_114.json")
        
        if not os.path.exists(data_path):
            return "⚠️ Surah metadata expansion in progress. Please try again in a moment."
            
        with open(data_path, "r", encoding="utf-8-sig") as f:
            full_data = json.load(f)
            surah_list = full_data.get("data", [])
            
        search_term = str(surah_name_or_number).lower().strip()
        found_surah = None
        
        # Search by number or name
        for s in surah_list:
            if (str(s["number"]) == search_term or 
                s["englishName"].lower() == search_term or 
                search_term in s["englishName"].lower() or
                s["englishNameTranslation"].lower() == search_term):
                found_surah = s
                break
                
        if found_surah:
            return f"""📖 **Surah {found_surah['englishName']} (Chapter {found_surah['number']})**
            
**Meaning:** {found_surah['englishNameTranslation']}
**Arabic Name:** {found_surah['name']}
**Total Verses:** {found_surah["numberOfAyahs"]}
**Revelation:** {found_surah["revelationType"]}

---
✨ **Scholarly Tip:** This Surah is part of the 114 chapters that form the complete Quran.
"""
        
        return f"❌ Surah '{surah_name_or_number}' not found. Please provide a valid Surah name or number (1-114)."
    except Exception as e:
        return f"❌ Error retrieving Surah info: {str(e)}"

@cached_service(ttl=86400)  # Names of Allah rarely change
def get_name_of_allah(query: str) -> str:
    """
    Get 99 Names of Allah (Asma-ul-Husna) with meanings and descriptions from the full dataset.
    
    Args:
        query: Name (Arabic/English) or Number (1-99)
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "knowledge", "data", "99_names_of_allah_full.json")
        
        if not os.path.exists(data_path):
            return "⚠️ Database of 99 Names is being synchronized. Please try again soon."
            
        with open(data_path, "r", encoding="utf-8-sig") as f:
            full_data = json.load(f)
            names_list = full_data.get("data", [])
            
        search_term = str(query).lower().strip()
        found_name = None
        
        for n in names_list:
            if (str(n["number"]) == search_term or 
                n["transliteration"].lower() == search_term or 
                search_term in n["transliteration"].lower() or
                n["en"]["meaning"].lower() == search_term):
                found_name = n
                break
                
        if found_name:
            return f"""💠 **Asma-ul-Husna: {found_name['transliteration']}**
            
## {found_name['name']}

**📖 Meaning:** {found_name['en']['meaning']}
**🌟 Description:** {found_name['en']['desc']}
**📜 Found in Quran:** {found_name['found']}

---
*\"To Allah belong the most beautiful names, so call on Him by them.\" (Quran 7:180)*"""
            
        return "💡 Name not found. Please search for names like 'Ar-Rahman', 'Al-Malik', or numbers 1-99."
    except Exception as e:
        return f"❌ Error retrieving Name of Allah: {str(e)}"

@cached_service(ttl=86400)
def get_all_99_names() -> str:
    """Get the complete list of 99 Names of Allah with meanings"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "knowledge", "data", "99_names_of_allah_full.json")
        
        with open(data_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)["data"]
            
        output = "💠 **Asma-ul-Husna: The 99 Beautiful Names of Allah**\n\n"
        output += "*\"To Allah belong the most beautiful names, so call on Him by them.\" (Quran 7:180)*\n\n"
        
        # Group into readable blocks of 10
        for i, n in enumerate(data):
            output += f"**{n['number']}. {n['name']}** — *{n['transliteration']}*\n"
            output += f"   Meaning: {n['en']['meaning']}\n"
            if (i + 1) % 10 == 0:
                output += "\n---\n"
                
        output += "\n\n🌐 **Source:** Authentic Asma-ul-Husna Collection"
        return output
    except Exception as e:
        return f"❌ Error retrieving 99 Names: {str(e)}"

@cached_service(ttl=86400)
def get_prophet_names(query: str = None) -> str:
    """Get Names of Prophet Muhammad ﷺ (Asma-un-Nabi)"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "knowledge", "data", "99_names_of_prophet.json")
        
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)["data"]
            
        if query:
            search = str(query).lower().strip()
            for n in data:
                if (str(n["number"]) == search or 
                    n["transliteration"].lower() == search or 
                    search in n["transliteration"].lower() or 
                    n["meaning"].lower() == search):
                    return f"""✨ **Asma-un-Nabi: {n['transliteration']} ﷺ**
                    
**Arabic:** {n['name']}
**Meaning:** {n['meaning']}
**Description:** {n['desc']}

---
*May Allah's Peace and Blessings be upon him.*"""

        # Return full list view if no specific query
        output = "✨ **Asma-un-Nabi: The Blessed Names of Prophet Muhammad ﷺ**\n\n"
        for i, n in enumerate(data):
            output += f"**{n['number']}. {n['name']}** — *{n['transliteration']}*\n"
            output += f"   Meaning: {n['meaning']}\n"
            if (i + 1) % 10 == 0:
                output += "\n---\n"
                
        output += "\n\n🌐 **Source:** Authentic Prophetic Traditions (Shamail)"
        return output
    except Exception as e:
        return f"❌ Error retrieving Prophetic Names: {str(e)}"

@cached_service(ttl=43200)  # Adhkar cache for 12 hours
def get_adhkar(category: str = "morning") -> str:
    """
    Get Prophetic Adhkar (Supplications) from the full Hisn al-Muslim collection.
    
    Args:
        category: Search term or category (e.g., 'morning', 'evening', 'sleep', 'travel')
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "knowledge", "data", "hisn_al_muslim.json")
        
        if not os.path.exists(data_path):
            return "⚠️ Hisn al-Muslim database is being synchronized. Please try again soon."
            
        with open(data_path, "r", encoding="utf-8-sig") as f:
            full_data = json.load(f)
            # The JSON structure has an "English" key containing the list of categories
            categories = full_data.get("English", [])
            
        search_term = category.lower().strip()
        found_category = None
        
        # Simple fuzzy matching for categories
        for cat in categories:
            if search_term in cat["TITLE"].lower():
                found_category = cat
                break
                
        if not found_category:
            # List available common categories if not found
            common = ["Morning", "Evening", "Sleep", "Travel", "Prayer", "Arafat"]
            return f"💡 Category '{category}' not found. Try searching for: {', '.join(common)}... or check 'hisn_al_muslim.json' for full titles."

        response = f"🤲 **Hisn al-Muslim: {found_category['TITLE']}**\n\n"
        
        for item in found_category.get("TEXT", []):
            repeat_info = f"*(Repeat {item['REPEAT']} times)*" if item.get("REPEAT", 0) > 1 else ""
            response += f"""### {item['ARABIC_TEXT']}

**📖 Translation:** {item['TRANSLATED_TEXT']}
{repeat_info}

---
"""
        response += "\n*Source: Hisn al-Muslim (Fortress of the Muslim) - Authentic Prophetic Supplications.*"
        return response
        
    except Exception as e:
        return f"❌ Error retrieving Adhkar: {str(e)}"

@cached_service(ttl=86400)
def get_hajj_umrah_guidance(ritual: str) -> str:
    """
    Get interactive guidance for Hajj and Umrah rituals, integrated with
    authentic supplications from Hisn al-Muslim.
    """
    rituals = {
        "ihram": {
            "title": "State of Ihram",
            "desc": "The sacred state for a pilgrim. This involves wearing two unstitched white sheets (for men), making the intention (Niyyah), and reciting the Talbiyah.",
            "steps": ["Ghusl (Purification)", "Wearing the Ihram garments", "Niyyah (Intention)", "Talbiyah (Labbayk Allahumma Labbayk)"],
            "caution": "Avoid cutting hair, nails, using perfume, or hunting/sexual activity while in Ihram.",
            "dua_category": "The pilgrim's announcement of his arrival for Hajj or Umrah"
        },
        "tawaf": {
            "title": "Tawaf (Circumambulation)",
            "desc": "Circling the Kaaba seven times counter-clockwise, starting from the Hajar al-Aswad (Black Stone).",
            "steps": ["Make intention near Black Stone", "Start circumambulation (counter-clockwise)", "Recite Duas during the rounds", "Finish 7 rounds", "Pray 2 Rakats behind Maqam Ibrahim"],
            "caution": "Ensure Wudu is maintained. Keep the Kaaba to your left.",
            "dua_category": "Between the Yemeni corner and the Black Stone" # If exists
        },
        "sai": {
            "title": "Sa'i (The Walk)",
            "desc": "Walking seven times between the hills of Safa and Marwa in remembrance of Hajar (AS).",
            "steps": ["Start at Safa", "Walk toward Marwa", "Recite Duas on the hills", "Complete 7 one-way trips"],
            "caution": "Men should jog between the green lights.",
            "dua_category": "Invocation to be recited while standing at Safa and Marwah"
        },
        "arafat": {
            "title": "Wuquf at Arafat",
            "desc": "The most important pillar of Hajj. Staying at the plain of Arafat on the 9th of Dhul-Hijjah.",
            "steps": ["Arrive after Dhuhr", "Engage in intense Dua and remembrance", "Stay until sunset"],
            "caution": "Leaving Arafat before sunset without a valid excuse requires a penalty.",
            "dua_category": "Invocation to be recited on the Day of Arafat"
        }
    }
    
    r = ritual.lower()
    if r in rituals:
        item = rituals[r]
        steps_list = "\n".join([f"• {step}" for step in item['steps']])
        
        # Try to fetch additional Duas from Hisn al-Muslim
        extra_dua = ""
        if "dua_category" in item:
            try:
                dua_content = get_adhkar(item['dua_category'])
                if "Category" not in dua_content and "⚠️" not in dua_content:
                    extra_dua = f"\n\n**🤲 Authentic Supplications:**\n{dua_content}"
            except:
                pass

        return f"""🕋 **Hajj & Umrah Guide: {item['title']}**

**📍 Description:**
{item['desc']}

**📝 Key Steps:**
{steps_list}

**⚠️ Cautions:**
{item['caution']}{extra_dua}

---
📖 *\"And perform properly the Hajj and Umrah for Allah.\" (Quran 2:196)*

✅ **Verification**: Rulings based on established Sunnah and scholarly consensus.
💡 *Try asking for: 'Tawaf', 'Sai', or 'Arafat'.*"""
    
    return "💡 Please specify a ritual: Ihram, Tawaf, Sai, Arafat, or Muzdalifah."

@cached_service(ttl=86400)
def check_halal_guidance(item: str) -> str:
    """
    Check Halal/Haram status of food items or common ingredients (E-numbers)
    using authentic local knowledge retrieval.
    """
    from backend.knowledge.local_knowledge_tools import search_local_knowledge
    from backend.utils.llm_provider import generate_text
    
    search_query = f"halal haram status of {item} ingredient fatwa"
    local_data = search_local_knowledge(search_query)
    
    if local_data and "❌ No relevant information" not in local_data:
        # Synthesize a specific response based on the retrieved data
        synthesis_prompt = f"""
        You are an Islamic Dietary Law Specialist. Based on the following retrieved scholarly data, 
        provide a clear verdict on the Halal/Haram status of '{item}'.
        
        SCHOLARLY DATA:
        {local_data}
        
        INSTRUCTIONS:
        1. State the Verdict clearly (Halal / Haram / Doubtful).
        2. Provide the Reason based on the data.
        3. Cite the Scholarly Source from the data.
        4. If the data is ambiguous, state "Inconclusive based on available local records".
        5. Format your response with emojis and clear sections.
        
        Response:
        """
        verdict = generate_text(synthesis_prompt)
        if verdict:
            return verdict

    # Fallback to general principles if no specific data found
    return f"""🔍 **Halal Guidance for '{item}'**

We couldn't find a specific scholarly fatwa for this in our authenticated local database yet. 

**General Principles:**
• All plant-based items are generally Halal.
• All sea food is generally Halal (with some Madhab variations).
• Avoid any item containing pork, carnivores, or intoxicants.

**Recommendation:** Look for reliable Halal certification logos (e.g., HMC, IFANCA) on the packaging. When in doubt, it is better to avoid (*Taqwa*).

*\"O mankind, eat from whatever is on earth [that is] lawful and good.\" (Quran 2:168)*"""

@cached_service(ttl=86400)
def get_madhab_view(topic: str) -> str:
    """
    Get the specific legal positions of the four major Madhabs on a given topic
    using authentic local knowledge retrieval and scholarly synthesis.
    """
    from backend.knowledge.local_knowledge_tools import search_local_knowledge
    from backend.utils.llm_provider import generate_text
    
    search_query = f"madhab views differences hanafi maliki shafii hanbali on {topic}"
    local_data = search_local_knowledge(search_query)
    
    if local_data and "❌ No relevant information" not in local_data:
        synthesis_prompt = f"""
        You are a Senior Fiqh Specialist. Based on the scholarly evidence below, 
        detail the views of the four major Madhabs (Hanafi, Maliki, Shafi'i, Hanbali) 
        regarding '{topic}'.
        
        SCHOLARLY EVIDENCE:
        {local_data}
        
        INSTRUCTIONS:
        1. Create a section for each Madhab.
        2. Provide the specific ruling and logic for each school.
        3. Cite the Evidence (Quran/Hadith) mentioned in the data.
        4. If a Madhab's view is not in the data, state "Specific position for this Madhab not found in current local records".
        5. Conclude with a note on 'Ikhtilaf' (Scholarly differences) as a mercy.
        6. Use Emojis (🏛️) for schools and (⚖️) for the title.
        
        Response:
        """
        madhab_views = generate_text(synthesis_prompt)
        if madhab_views:
            return madhab_views

    # Fallback to general guidance
    return f"""🔍 **Madhab View for '{topic}'**

We are currently expanding our specialized Madhab database and could not find a specific breakdown for this topic in our authenticated local records. 

**General Scholarly Approach:**
• Most core pillars are agreed upon (*Ijma*).
• Differences usually exist in the details of performance or secondary conditions.
• Follow the guidance of your local qualified Imam or the Madhab you typically follow.

**Note:** Valid differences (*Ikhtilaf*) between the schools are part of the vastness and mercy of Islamic jurisprudence.

💡 *Try asking about common topics like 'wudu intention', 'wiping over socks', or 'prayer timings'.*"""

@cached_service(ttl=43200)
def get_fiqh_ruling(topic: str, madhab: str = "general") -> str:
    """
    Get a specific Fiqh ruling on a topic.
    """
    # This tool can be expanded with more complex logic or RAG integration
    return f"⚖️ **Fiqh Ruling on {topic.title()}**\n\nFor a detailed breakdown of this ruling across different schools of thought, try using the `get_madhab_view` tool with a specific topic like 'wudu' or 'vomiting'."


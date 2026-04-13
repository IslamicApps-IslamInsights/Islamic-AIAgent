import requests
from typing import Dict, Optional

def get_quran_audio_url(verse_key: str, reciter_id: int = 7) -> Optional[str]:
    """
    Get the audio URL for a specific Quranic verse.
    
    Args:
        verse_key: Verse reference like "2:255"
        reciter_id: ID of the reciter (default: 7 is Mishary Rashid Alafasy)
        
    Returns:
        MP3 URL or None if not found
    """
    try:
        # Al-Quran Cloud API uses surah:ayah format
        url = f"https://api.alquran.cloud/v1/ayah/{verse_key}/ar.alafasy"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['audio']
        return None
    except Exception as e:
        print(f"Error fetching Quran audio: {e}")
        return None

def get_reciter_list() -> Dict[int, str]:
    """Returns a list of popular reciters"""
    return {
        7: "Mishary Rashid Alafasy",
        1: "AbdulBaset AbdulSamad",
        3: "Abdur-Rahman as-Sudais",
        6: "Mahmoud Khalil Al-Hussary"
    }

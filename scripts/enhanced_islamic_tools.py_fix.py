def get_surah_info(surah_name_or_number: str) -> str:
    """
    Get detailed information about any of the 114 Surahs using the expanded dataset.
    
    Args:
        surah_name_or_number: Surah name or number (1-114)
    """
    try:
        data_path = os.path.join(os.path.dirname(__file__), "knowledge_base/data/quran_surah_metadata_114.json")
        if not os.path.exists(data_path):
            return "⚠️ Surah metadata expansion in progress. Please try again in a moment."
            
        with open(data_path, "r") as f:
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
**Total Verses:** {found_surah['numberOfAyahs']}
**Revelation:** {found_surah['revelationType']}

---
✨ **Scholarly Tip:** This Surah is part of the 114 chapters that form the complete Quran.
💡 **To Read:** Use `get_quran_verse('{found_surah['number']}:1')` to start reading."""
        
        return f"❌ Surah '{surah_name_or_number}' not found. Please provide a valid Surah name or number (1-114)."
    except Exception as e:
        return f"❌ Error retrieving Surah info: {str(e)}"

def get_name_of_allah(query: str) -> str:
    """
    Get 99 Names of Allah (Asma-ul-Husna) with meanings and descriptions from the full dataset.
    
    Args:
        query: Name (Arabic/English) or Number (1-99)
    """
    try:
        data_path = os.path.join(os.path.dirname(__file__), "knowledge_base/data/99_names_of_allah_full.json")
        if not os.path.exists(data_path):
            return "⚠️ Database of 99 Names is being synchronized. Please try again soon."
            
        with open(data_path, "r") as f:
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
            
<div class="arabic-text" style="font-size: 2.5rem; text-align: center; margin: 20px 0;">
    {found_name['name']}
</div>

**📖 Meaning:** {found_name['en']['meaning']}
**🌟 Description:** {found_name['en']['desc']}
**📜 Found in Quran:** {found_name['found']}

---
*\"To Allah belong the most beautiful names, so call on Him by them.\" (Quran 7:180)*"""
            
        return "💡 Name not found. Please search for names like 'Ar-Rahman', 'Al-Malik', or numbers 1-99."
    except Exception as e:
        return f"❌ Error retrieving Name of Allah: {str(e)}"

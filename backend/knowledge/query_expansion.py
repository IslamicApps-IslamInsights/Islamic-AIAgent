"""
Islamic Query Expansion Engine
Maps English Islamic terms to Arabic equivalents and synonyms
to dramatically improve knowledge base retrieval quality.
"""

from typing import List, Set

# ─── English → Arabic expansion map ──────────────────────────────────
# Each key is an English term; values are Arabic/transliteration expansions
_EN_AR_MAP = {
    # Core worship
    "prayer": ["صلاة", "salah", "salat", "namaz"],
    "fasting": ["صيام", "صوم", "sawm", "siyam", "roza"],
    "charity": ["صدقة", "زكاة", "sadaqah", "zakat", "infaq"],
    "pilgrimage": ["حج", "عمرة", "hajj", "umrah"],
    "faith": ["إيمان", "iman", "aqeedah", "عقيدة"],
    "worship": ["عبادة", "ibadah"],
    # Virtues
    "patience": ["صبر", "sabr"],
    "gratitude": ["شكر", "shukr"],
    "kindness": ["إحسان", "ihsan", "birr", "بر"],
    "forgiveness": ["مغفرة", "توبة", "maghfirah", "tawbah", "istighfar"],
    "mercy": ["رحمة", "rahmah"],
    "justice": ["عدل", "adl", "qist", "قسط"],
    "trust": ["توكل", "tawakkul"],
    "repentance": ["توبة", "tawbah", "istighfar", "استغفار"],
    "sincerity": ["إخلاص", "ikhlas"],
    "humility": ["تواضع", "tawadu"],
    "truthfulness": ["صدق", "sidq"],
    "modesty": ["حياء", "haya"],
    "love": ["حب", "محبة", "hubb", "mahabbah"],
    "fear": ["خوف", "khawf", "taqwa", "تقوى"],
    "hope": ["رجاء", "raja"],
    "contentment": ["رضا", "قناعة", "rida", "qanaah"],
    # Purification & rituals
    "ablution": ["وضوء", "wudu", "wudhu"],
    "purification": ["طهارة", "غسل", "taharah", "ghusl"],
    "supplication": ["دعاء", "dua"],
    "remembrance": ["ذكر", "dhikr", "adhkar", "أذكار"],
    # Islamic law
    "halal": ["حلال"],
    "haram": ["حرام"],
    "permissible": ["مباح", "حلال", "mubah", "halal"],
    "forbidden": ["حرام", "محرم", "haram", "muharram"],
    "marriage": ["نكاح", "زواج", "nikah", "zawaj"],
    "divorce": ["طلاق", "talaq", "khula", "خلع"],
    "inheritance": ["ميراث", "إرث", "mirath", "irth"],
    "interest": ["ربا", "riba"],
    # Knowledge & prophets
    "knowledge": ["علم", "ilm"],
    "scholar": ["عالم", "شيخ", "alim", "sheikh"],
    "prophet": ["نبي", "رسول", "nabi", "rasul"],
    "companion": ["صحابي", "sahabi", "sahabah", "صحابة"],
    "revelation": ["وحي", "wahy", "tanzeel", "تنزيل"],
    # Family
    "parents": ["والدين", "walidayn", "birr al-walidayn"],
    "children": ["أطفال", "أولاد", "atfal", "awlad"],
    "family": ["أسرة", "عائلة", "usrah"],
    "mother": ["أم", "umm", "walidah"],
    "father": ["أب", "ab", "walid"],
    # Afterlife
    "paradise": ["جنة", "jannah"],
    "hellfire": ["نار", "جهنم", "nar", "jahannam"],
    "day of judgment": ["يوم القيامة", "yawm al-qiyamah"],
    "death": ["موت", "mawt"],
    "soul": ["نفس", "روح", "nafs", "ruh"],
    # Quran-related
    "quran": ["قرآن", "كتاب الله", "kitab allah"],
    "surah": ["سورة"],
    "verse": ["آية", "ayah"],
    "tafsir": ["تفسير"],
    "recitation": ["تلاوة", "tilawah", "qiraat", "قراءة"],
    # Hadith
    "hadith": ["حديث", "سنة", "sunnah"],
    "narration": ["رواية", "riwayah"],
    "chain": ["إسناد", "isnad"],
    "authentic": ["صحيح", "sahih"],
    # Ethics
    "lying": ["كذب", "kadhib"],
    "backbiting": ["غيبة", "gheebah"],
    "envy": ["حسد", "hasad"],
    "pride": ["كبر", "kibr"],
    "anger": ["غضب", "ghadab"],
    "greed": ["طمع", "tama"],
    # Fiqh & Awaqf
    "endowment": ["وقف", "waqf", "awqaf"],
    "jurisprudence": ["فقه", "fiqh"],
    "ruling": ["حكم", "hukm", "fatwa", "فتوى"],
    "obligation": ["فرض", "واجب", "fard", "wajib"],
    "recommended": ["مندوب", "mustahabb", "sunnah"],
    "disliked": ["مكروه", "makruh"],
}

# ─── Synonym expansion map ────────────────────────────────────────────
_SYNONYMS = {
    "wudu": ["ablution", "wudhu", "washing"],
    "ablution": ["wudu", "wudhu"],
    "ghusl": ["purification", "ritual bath", "bathing"],
    "salah": ["prayer", "salat", "namaz"],
    "sawm": ["fasting", "siyam", "roza"],
    "zakat": ["charity", "alms", "sadaqah"],
    "hajj": ["pilgrimage"],
    "umrah": ["minor pilgrimage"],
    "dua": ["supplication", "prayer", "invocation"],
    "dhikr": ["remembrance", "adhkar"],
    "taqwa": ["god-consciousness", "piety", "fear of allah"],
    "sabr": ["patience", "perseverance", "endurance"],
    "shukr": ["gratitude", "thankfulness"],
    "tawbah": ["repentance", "forgiveness"],
    "ikhlas": ["sincerity"],
    "ihsan": ["excellence", "kindness", "goodness"],
    "riba": ["interest", "usury"],
    "nikah": ["marriage", "wedding"],
    "talaq": ["divorce"],
    "jannah": ["paradise", "heaven", "garden"],
    "jahannam": ["hellfire", "hell"],
    "iman": ["faith", "belief"],
    "shirk": ["polytheism", "idolatry", "associating partners"],
    "tawheed": ["monotheism", "oneness of god", "unity of allah"],
    "seerah": ["biography of the prophet", "prophetic biography"],
    "fiqh": ["jurisprudence", "islamic law", "ruling"],
    "aqeedah": ["creed", "belief", "faith", "theology"],
    "sunnah": ["prophetic tradition", "hadith"],
    "bid'ah": ["innovation", "heresy"],
}


def expand_query(query: str, max_expansions: int = 8) -> List[str]:
    """
    Expand a user query with Arabic equivalents and synonyms.

    Returns a list of additional search terms that should be searched
    alongside the original query.

    Args:
        query: Original user query.
        max_expansions: Maximum number of expansion terms.

    Returns:
        Deduplicated list of expansion terms.
    """
    q_lower = query.lower()
    tokens = set(q_lower.replace("'", " ").replace("-", " ").split())
    expansions: Set[str] = set()

    # 1. English → Arabic expansions
    for eng_term, arabic_terms in _EN_AR_MAP.items():
        if eng_term in q_lower:
            expansions.update(arabic_terms)

    # 2. Synonym expansions
    for term, syns in _SYNONYMS.items():
        if term in tokens or term in q_lower:
            expansions.update(syns)

    # 3. Reverse-synonym: if query has a synonym value, add the key
    for term, syns in _SYNONYMS.items():
        if any(s in q_lower for s in syns):
            expansions.add(term)

    # Remove terms already in the query
    expansions -= tokens
    expansions.discard("")

    return list(expansions)[:max_expansions]

def generate_hyde_doc(query: str) -> str:
    """
    RAG v2 Strength Step: HyDE (Hypothetical Document Embedding).
    Generates a hypothetical authentic scholarly passage answering the query to improve 
    semantic search accuracy.
    """
    from backend.utils.llm_provider import generate_text
    
    hyde_prompt = f"""
    You are a Senior Islamic Scholar. Please write a short, highly authentic, and scholarly 
    passage that would perfectly answer the following question. 
    Use terminology common in Sahih Hadiths and Quranic Tafsir.
    
    User Question: {query}
    
    Hypothetical Scholarly Passage:
    """
    
    try:
        return generate_text(hyde_prompt)
    except Exception:
        return ""

def decompose_query(query: str) -> List[str]:
    """
    RAG v2 Strength Step: Query Decomposition.
    Splits complex queries into multiple atomic scholarly sub-questions.
    """
    from backend.utils.llm_provider import generate_text
    import json
    import re
    
    decompose_prompt = f"""
    You are an Islamic Knowledge Specialist. Break down the following complex user question 
    into 2-3 atomic, simple sub-questions that can be used for searching an Islamic database.
    
    User Question: {query}
    
    Respond ONLY with a JSON list of strings (e.g., ["When is fasting obligatory?", "What are the rewards of fasting?"]).
    
    Sub-questions:
    """
    
    try:
        res_text = generate_text(decompose_prompt)
        match = re.search(r'\[.*\]', res_text.strip(), re.DOTALL)
        if match:
            return json.loads(match.group())
        return [query]
    except Exception:
        return [query]


if __name__ == "__main__":
    # Quick tests
    tests = [
        "What does Islam say about patience?",
        "How to perform wudu?",
        "Tell me about charity in Islam",
        "What is riba?",
        "Hadith about kindness",
    ]
    for t in tests:
        exps = expand_query(t)
        print(f"\n🔍 \"{t}\"")
        print(f"   → expansions: {exps}")

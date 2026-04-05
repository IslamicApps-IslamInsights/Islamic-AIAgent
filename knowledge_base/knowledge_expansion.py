import os
import requests
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "knowledge_base/data")
os.makedirs(DATA_DIR, exist_ok=True)

EXPANSION_SOURCES = [
    {
        "name": "99_names_of_allah_full.json",
        "url": "https://raw.githubusercontent.com/KabDeveloper/99-Names-Of-Allah/master/99_Names_Of_Allah.json"
    },
    {
        "name": "quran_surah_metadata_114.json",
        "url": "https://api.alquran.cloud/v1/surah"
    },
    {
        "name": "hisn_al_muslim.json",
        "url": "https://raw.githubusercontent.com/wafaaelmaandy/Hisn-Muslim-Json/master/husn_en.json"
    },
    {
        "name": "sahih_bukhari.json",
        "url": "https://raw.githubusercontent.com/AhmedBaset/hadith-json/refs/heads/main/db/by_book/the_9_books/bukhari.json"
    },
    {
        "name": "sahih_muslim.json",
        "url": "https://raw.githubusercontent.com/AhmedBaset/hadith-json/refs/heads/main/db/by_book/the_9_books/muslim.json"
    },
    {
        "name": "forty_hadith_nawawi.json",
        "url": "https://raw.githubusercontent.com/AhmedBaset/hadith-json/refs/heads/main/db/by_book/the_9_books/nawawi.json"
    }
]

def expand_knowledge():
    print("🌍 Starting Knowledge Base Expansion (Authentic Scholarly Data)...")
    
    for source in EXPANSION_SOURCES:
        file_path = os.path.join(DATA_DIR, source['name'])
        
        # Check if already exists to save bandwidth
        if os.path.exists(file_path):
            print(f"✅ {source['name']} already exists. Skipping download.")
            continue
            
        print(f"⏳ Downloading {source['name']}...")
        try:
            response = requests.get(source['url'], timeout=60) # Increased timeout for large files
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"✨ Successfully downloaded {source['name']} ({len(response.content)} bytes)")
            else:
                print(f"⚠️ Failed to download {source['name']} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error downloading {source['name']}: {e}")

    # Create specialized TXT versions for foundational collections to optimize RAG
    # This allows the AI to 'hit' the key texts via standard similarity before tool expansion
    nawawi_json = os.path.join(DATA_DIR, "forty_hadith_nawawi.json")
    if os.path.exists(nawawi_json):
        try:
            with open(nawawi_json, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                with open(os.path.join(DATA_DIR, "40_hadith_nawawi_highlights.txt"), "w") as out:
                    out.write("FORTY HADITH OF IMAM NAWAWI — FOUNDATIONAL ISLAMIC TEACHINGS\n")
                    out.write("=" * 60 + "\n\n")
                    for h in data.get("hadiths", []):
                        eng = h.get("english", {})
                        out.write(f"HADITH #{h.get('id')}\n")
                        out.write(f"NARRATOR: {eng.get('narrator', 'Unknown')}\n")
                        out.write(f"TEXT: {eng.get('text', 'No English text available')}\n")
                        out.write("-" * 20 + "\n\n")
            print("📜 Created TXT version of 40 Hadith Nawawi for optimized RAG.")
        except Exception as e:
            print(f"⚠️ Failed to create TXT highlight for Nawawi: {e}")

    print("🚀 Knowledge expansion complete. Ready for ingestion!")

if __name__ == "__main__":
    expand_knowledge()

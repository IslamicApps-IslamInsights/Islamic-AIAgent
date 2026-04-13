#!/usr/bin/env python3
import os
import requests

DATA_DIR = "knowledge_base/data"
os.makedirs(DATA_DIR, exist_ok=True)

# Sources for 5 remaining canonical hadith books + 3 more Quran translations
NEW_DATA_SOURCES = {
    # Remaining Sihah Sitta & Major Books
    "sunan_abu_dawud_english.json": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/eng-abudawud.json",
    "jami_at_tirmidhi_english.json": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/eng-tirmidhi.json",
    "sunan_an_nasai_english.json": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/eng-nasai.json",
    "sunan_ibn_majah_english.json": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/eng-ibnmajah.json",
    "muwatta_malik_english.json": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/eng-malik.json",
    
    # Extra English Quran Translations
    "quran_yusuf_ali.txt": "https://tanzil.net/trans/en.yusufali",
    "quran_pickthall.txt": "https://tanzil.net/trans/en.pickthall",
    "quran_shakir.txt": "https://tanzil.net/trans/en.shakir",
}

def download_expanded_data():
    print(f"📥 Downloading expanded Phase 3 authentic datasets to {DATA_DIR}...")
    
    for filename, url in NEW_DATA_SOURCES.items():
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            print(f"✅ {filename} already exists. Skipping.")
            continue
            
        print(f"⏳ Downloading {filename} from {url}...")
        try:
            response = requests.get(url, timeout=120, stream=True)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ Saved {filename} ({os.path.getsize(file_path)} bytes)")
            else:
                print(f"⚠️ Failed to download {filename} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")

if __name__ == "__main__":
    download_expanded_data()

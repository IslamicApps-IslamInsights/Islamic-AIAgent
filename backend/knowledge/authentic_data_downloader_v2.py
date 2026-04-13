#!/usr/bin/env python3
import os
import requests
import json

DATA_DIR = "backend/knowledge/data"
os.makedirs(DATA_DIR, exist_ok=True)

# Actual stable URLs for authentic Islamic data
DATA_SOURCES = [
    {
        "name": "Sahih_Bukhari_English",
        "url": "https://raw.githubusercontent.com/Aki-108/hadith-api/main/editions/eng-bukhari.json",
        "type": "json_hadith"
    },
    {
        "name": "Sahih_Muslim_English",
        "url": "https://raw.githubusercontent.com/Aki-108/hadith-api/main/editions/eng-muslim.json",
        "type": "json_hadith"
    }
]

# Surah-by-surah Tafsir links
TAFSIR_BASE_URL = "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/en-tafisr-ibn-kathir/"
TAFSIR_SURAHS = [1, 2, 3, 4, 36, 55, 67] # Fatiha, Baqarah, Imran, Nisa, Yasin, Rahman, Mulk

def download_and_parse():
    print(f"📥 Downloading and parsing authentic datasets to {DATA_DIR}...")
    for source in DATA_SOURCES:
        file_path_txt = os.path.join(DATA_DIR, f"{source['name']}.txt")
        if os.path.exists(file_path_txt):
            print(f"✅ {source['name']} already exists as TXT. Skipping.")
            continue
            
        print(f"⏳ Downloading {source['name']}...")
        try:
            response = requests.get(source['url'], timeout=30)
            if response.status_code == 200:
                data = response.json()
                with open(file_path_txt, "w", encoding="utf-8") as f:
                    if source['type'] == "json_hadith":
                        hadiths = data.get("hadiths", [])
                        for h in hadiths[:1000]: # Limit to first 1000 for speed/size in this demo
                            f.write(f"Hadith Reference: {h.get('hadithnumber')}\n")
                            f.write(f"Text: {h.get('text')}\n")
                            f.write("-" * 20 + "\n")
                    elif source['type'] == "json_tafsir":
                        # Tafsir JSON structure varies; adapt based on common patterns
                        tafsirs = data.get("tafsir", [])
                        for t in tafsirs[:500]:
                            f.write(f"Tafsir Reference: {t.get('surah')}:{t.get('ayah')}\n")
                            f.write(f"Text: {t.get('text')}\n")
                            f.write("-" * 20 + "\n")
                print(f"✅ Saved parsed TXT for {source['name']} ({os.path.getsize(file_path_txt)} bytes)")
            else:
                print(f"⚠️ Failed to download {source['name']} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error processing {source['name']}: {e}")

    # Download Tafsirs
    for surah_num in TAFSIR_SURAHS:
        name = f"Tafsir_Ibn_Kathir_Surah_{surah_num}"
        file_path_txt = os.path.join(DATA_DIR, f"{name}.txt")
        if os.path.exists(file_path_txt): continue
        
        url = f"{TAFSIR_BASE_URL}{surah_num}.json"
        print(f"⏳ Downloading {name}...")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                with open(file_path_txt, "w", encoding="utf-8") as f:
                    tafsirs = data.get("tafsir", [])
                    for t in tafsirs:
                        f.write(f"Tafsir Reference: {t.get('surah')}:{t.get('ayah')}\n")
                        f.write(f"Explanation: {t.get('text')}\n")
                        f.write("-" * 20 + "\n")
                print(f"✅ Saved parsed TXT for {name}")
        except Exception as e:
            print(f"❌ Error processing {name}: {e}")

if __name__ == "__main__":
    download_and_parse()

#!/usr/bin/env python3
import os
import requests

DATA_DIR = "backend/knowledge/data"
os.makedirs(DATA_DIR, exist_ok=True)

# Final verified stable raw links
SOURCES = {
    "quran_saheeh_international.txt": "https://tanzil.net/trans/en.sahih",
}

# Authentic Hadith and Scholarly Sources
HADITH_SOURCES = [
    {
        "url": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/eng-bukhari.json",
        "filename": "sahih_bukhari_english.json"
    },
    {
        "url": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/eng-muslim.json",
        "filename": "sahih_muslim_english.json"
    }
]

def download_final_data():
    print(f"📥 Downloading final authentic datasets to {DATA_DIR}...")

    # Download Quran source
    for filename, url in SOURCES.items():
        file_path = os.path.join(DATA_DIR, filename)
        print(f"⏳ Downloading {filename} from {url}...")
        try:
            response = requests.get(url, timeout=60, stream=True)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ Saved {filename} ({os.path.getsize(file_path)} bytes)")
            else:
                print(f"⚠️ Failed to download {filename} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")

    # Download Hadith sources
    for source_info in HADITH_SOURCES:
        url = source_info["url"]
        filename = source_info["filename"]
        file_path = os.path.join(DATA_DIR, filename)
        print(f"⏳ Downloading {filename} from {url}...")
        try:
            # Using verify=False if needed, but should be fine
            response = requests.get(url, timeout=60, stream=True)
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
    download_final_data()

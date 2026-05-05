#!/usr/bin/env python3
"""
Ingest data from islamAndAi/QURAN-NLP GitHub repository
Downloads: Quran, Tafseer, Translations, Names of Allah
Integrates with existing BM25 + ChromaDB system
"""

import os
import json
import requests
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QuranNLPIngestion")

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("📥 Downloading NLTK tokenizer...")
    nltk.download('punkt', quiet=True)


class QuranNLPIngester:
    """Ingest and process data from QURAN-NLP repository"""
    
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/islamAndAi/QURAN-NLP/master/data"
        self.project_root = Path(__file__).parent.parent
        self.knowledge_dir = self.project_root / "backend" / "knowledge"
        self.data_dir = self.knowledge_dir / "data"
        self.cache_dir = self.knowledge_dir / "cache_quran_nlp"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.downloaded_texts = []
        self.downloaded_metadata = []
        self.bm25_index_path = self.knowledge_dir / "bm25_index_enhanced.pkl"
        
    def download_file(self, url: str, filename: str) -> str:
        """Download file from GitHub"""
        try:
            logger.info(f"📥 Downloading: {filename}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            cache_path = self.cache_dir / filename
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            logger.info(f"✅ Saved: {cache_path}")
            return response.text
        except Exception as e:
            logger.error(f"❌ Failed to download {url}: {e}")
            return None
    
    def ingest_quran_translations(self):
        """Ingest Quran translations from translation/english"""
        logger.info("\n" + "="*70)
        logger.info("📖 INGESTING QURAN TRANSLATIONS (English)")
        logger.info("="*70)
        
        try:
            # Get list of files
            url = f"{self.base_url}/translation/english"
            response = requests.get(url, timeout=30)
            
            # Parse GitHub HTML to get JSON files
            import re
            json_files = re.findall(r'href=".*?(\w+\.json)"', response.text)
            
            if not json_files:
                logger.warning("⚠️  No JSON files found in translation/english")
                return
            
            for json_file in json_files[:10]:  # Limit to 10 files
                try:
                    file_url = f"{self.base_url}/translation/english/{json_file}"
                    content = self.download_file(file_url, f"translation_{json_file}")
                    
                    if content:
                        data = json.loads(content)
                        self._process_quran_translation(data, json_file)
                except Exception as e:
                    logger.error(f"Error processing {json_file}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to ingest Quran translations: {e}")
    
    def _process_quran_translation(self, data: Dict, source_name: str):
        """Process Quran translation data"""
        try:
            if isinstance(data, dict) and "chapters" in data:
                # Standard Quran format
                for chapter in data.get("chapters", []):
                    surah_num = chapter.get("number", 0)
                    surah_name = chapter.get("name", f"Surah {surah_num}")
                    
                    for verse in chapter.get("verses", []):
                        verse_num = verse.get("number", 0)
                        text = verse.get("text", "")
                        
                        if text:
                            # Format: "Surah:Verse|Text"
                            formatted_text = f"{surah_name}:{verse_num}|{text}"
                            self.downloaded_texts.append(formatted_text)
                            self.downloaded_metadata.append({
                                "source": source_name,
                                "type": "quran_translation",
                                "surah": surah_num,
                                "verse": verse_num,
                                "surah_name": surah_name
                            })
                
                logger.info(f"✅ Processed {len(data.get('chapters', []))} chapters from {source_name}")
            
            elif isinstance(data, list):
                # Array of verses
                for verse in data:
                    if isinstance(verse, dict):
                        text = verse.get("text", "")
                        surah = verse.get("surah", 0)
                        ayah = verse.get("ayah", 0)
                        
                        if text:
                            formatted_text = f"Surah {surah}:{ayah}|{text}"
                            self.downloaded_texts.append(formatted_text)
                            self.downloaded_metadata.append({
                                "source": source_name,
                                "type": "quran_translation",
                                "surah": surah,
                                "verse": ayah
                            })
                
                logger.info(f"✅ Processed {len(data)} verses from {source_name}")
        
        except Exception as e:
            logger.error(f"Error processing Quran translation: {e}")
    
    def ingest_tafaseer(self):
        """Ingest Tafseer (Quranic commentary) data"""
        logger.info("\n" + "="*70)
        logger.info("📚 INGESTING TAFASEER/COMMENTARY (English)")
        logger.info("="*70)
        
        try:
            url = f"{self.base_url}/tafaseer/english"
            response = requests.get(url, timeout=30)
            
            import re
            json_files = re.findall(r'href=".*?(\w+\.json)"', response.text)
            
            for json_file in json_files[:5]:  # Limit to 5 files
                try:
                    file_url = f"{self.base_url}/tafaseer/english/{json_file}"
                    content = self.download_file(file_url, f"tafaseer_{json_file}")
                    
                    if content:
                        data = json.loads(content)
                        self._process_tafaseer(data, json_file)
                except Exception as e:
                    logger.error(f"Error processing {json_file}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to ingest Tafaseer: {e}")
    
    def _process_tafaseer(self, data: Dict, source_name: str):
        """Process Tafseer data"""
        try:
            if isinstance(data, dict) and "chapters" in data:
                for chapter in data.get("chapters", []):
                    surah_num = chapter.get("number", 0)
                    
                    for verse in chapter.get("verses", []):
                        verse_num = verse.get("number", 0)
                        commentary = verse.get("text", "")
                        
                        if commentary:
                            self.downloaded_texts.append(commentary)
                            self.downloaded_metadata.append({
                                "source": source_name,
                                "type": "tafseer",
                                "surah": surah_num,
                                "verse": verse_num
                            })
                
                logger.info(f"✅ Processed Tafaseer from {source_name}")
            
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        text = item.get("text", "") or item.get("commentary", "")
                        if text:
                            self.downloaded_texts.append(text)
                            self.downloaded_metadata.append({
                                "source": source_name,
                                "type": "tafseer"
                            })
                
                logger.info(f"✅ Processed {len(data)} items from {source_name}")
        
        except Exception as e:
            logger.error(f"Error processing Tafaseer: {e}")
    
    def ingest_names_of_allah(self):
        """Ingest Names of Allah (99 Divine Attributes)"""
        logger.info("\n" + "="*70)
        logger.info("✨ INGESTING NAMES OF ALLAH (99 Divine Attributes)")
        logger.info("="*70)
        
        try:
            # Try different common filenames
            filenames = [
                "99_names.json",
                "names_of_allah.json",
                "allah_names.json",
                "divine_names.json"
            ]
            
            for filename in filenames:
                try:
                    file_url = f"{self.base_url}/names_of_Allah/{filename}"
                    content = self.download_file(file_url, f"names_{filename}")
                    
                    if content:
                        data = json.loads(content)
                        self._process_names_of_allah(data, filename)
                        break
                except:
                    continue
        
        except Exception as e:
            logger.error(f"Failed to ingest Names of Allah: {e}")
    
    def _process_names_of_allah(self, data: Dict, source_name: str):
        """Process Names of Allah data"""
        try:
            if isinstance(data, dict) and "names" in data:
                for name in data.get("names", []):
                    arabic = name.get("name", "")
                    english = name.get("en", {}).get("name", "")
                    meaning = name.get("en", {}).get("meaning", "")
                    
                    if english and meaning:
                        text = f"Name of Allah: {english} (Arabic: {arabic})\nMeaning: {meaning}"
                        self.downloaded_texts.append(text)
                        self.downloaded_metadata.append({
                            "source": source_name,
                            "type": "names_of_allah",
                            "name": english,
                            "arabic": arabic
                        })
                
                logger.info(f"✅ Processed {len(data.get('names', []))} Names of Allah")
            
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        english = item.get("en", {}).get("name", "")
                        meaning = item.get("en", {}).get("meaning", "")
                        
                        if english and meaning:
                            text = f"Name of Allah: {english}\nMeaning: {meaning}"
                            self.downloaded_texts.append(text)
                            self.downloaded_metadata.append({
                                "source": source_name,
                                "type": "names_of_allah",
                                "name": english
                            })
                
                logger.info(f"✅ Processed {len(data)} Names of Allah")
        
        except Exception as e:
            logger.error(f"Error processing Names of Allah: {e}")
    
    def ingest_local_data(self):
        """Also process any local existing data"""
        logger.info("\n" + "="*70)
        logger.info("📂 LOADING EXISTING LOCAL DATA")
        logger.info("="*70)
        
        try:
            # Load from existing JSON files
            for json_file in self.data_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if "hadiths" in data:
                        # Hadith format
                        for h in data["hadiths"]:
                            text = h.get("english", {}).get("text", "")
                            if text:
                                self.downloaded_texts.append(text)
                                self.downloaded_metadata.append({
                                    "source": json_file.name,
                                    "type": "hadith",
                                    "id": str(h.get("id") or h.get("hadithnumber", ""))
                                })
                    
                    logger.info(f"✅ Loaded {json_file.name}")
                except Exception as e:
                    logger.error(f"Error loading {json_file.name}: {e}")
            
            # Load from TXT files
            for txt_file in self.data_dir.glob("*.txt"):
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Split by paragraphs
                    for para in content.split("\n\n"):
                        if para.strip():
                            self.downloaded_texts.append(para)
                            self.downloaded_metadata.append({
                                "source": txt_file.name,
                                "type": "text"
                            })
                    
                    logger.info(f"✅ Loaded {txt_file.name}")
                except Exception as e:
                    logger.error(f"Error loading {txt_file.name}: {e}")
        
        except Exception as e:
            logger.error(f"Error loading local data: {e}")
    
    def build_bm25_index(self):
        """Build or update BM25 index with all ingested data"""
        logger.info("\n" + "="*70)
        logger.info("🎯 BUILDING BM25 INDEX")
        logger.info("="*70)
        
        if not self.downloaded_texts:
            logger.error("❌ No texts to index!")
            return False
        
        try:
            logger.info(f"📊 Indexing {len(self.downloaded_texts)} documents...")
            
            # Tokenize
            corpus = [word_tokenize(text.lower()) for text in self.downloaded_texts]
            
            # Build BM25
            logger.info("⚙️  Building BM25 model...")
            bm25 = BM25Okapi(corpus)
            
            # Save
            payload = {
                'bm25': bm25,
                'texts': self.downloaded_texts,
                'metadata': self.downloaded_metadata,
                'total_docs': len(self.downloaded_texts),
                'last_updated': datetime.now().isoformat(),
                'source': 'quran_nlp_github'
            }
            
            logger.info(f"💾 Saving to {self.bm25_index_path}...")
            with open(self.bm25_index_path, 'wb') as f:
                pickle.dump(payload, f)
            
            index_size = os.path.getsize(self.bm25_index_path) / 1024 / 1024
            logger.info(f"✅ BM25 Index created ({index_size:.1f} MB)")
            
            # Statistics
            logger.info("\n" + "="*70)
            logger.info("📊 INGESTION STATISTICS")
            logger.info("="*70)
            logger.info(f"✅ Total Documents: {len(self.downloaded_texts)}")
            logger.info(f"✅ Index Size: {index_size:.1f} MB")
            logger.info(f"✅ Index Location: {self.bm25_index_path}")
            
            # Breakdown by source
            source_counts = {}
            for meta in self.downloaded_metadata:
                source = meta.get("source", "unknown")
                source_counts[source] = source_counts.get(source, 0) + 1
            
            logger.info("\n📂 Documents by source:")
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   • {source}: {count}")
            
            # Breakdown by type
            type_counts = {}
            for meta in self.downloaded_metadata:
                doc_type = meta.get("type", "unknown")
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            
            logger.info("\n📚 Documents by type:")
            for doc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   • {doc_type}: {count}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to build BM25: {e}")
            return False
    
    def ingest_all(self):
        """Run complete ingestion pipeline"""
        logger.info("\n" + "🌟" * 40)
        logger.info("QURAN-NLP DATA INGESTION - COMPLETE PIPELINE")
        logger.info("🌟" * 40 + "\n")
        
        # Download and process remote data
        self.ingest_quran_translations()
        self.ingest_tafaseer()
        self.ingest_names_of_allah()
        
        # Load existing local data
        self.ingest_local_data()
        
        # Build combined BM25 index
        success = self.build_bm25_index()
        
        if success:
            logger.info("\n" + "="*70)
            logger.info("✨ INGESTION COMPLETE!")
            logger.info("="*70)
            logger.info(f"\nNext steps:")
            logger.info(f"1. Restart backend: pkill -f web_api.py")
            logger.info(f"2. Start backend: python backend/api/web_api.py")
            logger.info(f"3. Query the agent with Islamic knowledge")
            return True
        else:
            logger.error("\n❌ Ingestion failed!")
            return False


def main():
    """Main entry point"""
    ingester = QuranNLPIngester()
    success = ingester.ingest_all()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

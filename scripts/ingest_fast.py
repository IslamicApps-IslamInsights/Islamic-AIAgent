#!/usr/bin/env python3
"""
Fast Islamic Knowledge Base Ingestion
Loads local data + optional GitHub data
Builds enhanced BM25 index
"""

import os
import json
import pickle
import logging
from pathlib import Path
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("FastIngestion")

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("📥 Downloading NLTK tokenizer...")
    nltk.download('punkt', quiet=True)


class FastIslamicIngester:
    """Fast ingestion of Islamic knowledge"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.knowledge_dir = self.project_root / "backend" / "knowledge"
        self.data_dir = self.knowledge_dir / "data"
        
        self.texts = []
        self.metadata = []
        
    def load_local_data(self):
        """Load existing JSON and TXT files"""
        logger.info("\n" + "="*70)
        logger.info("📂 LOADING LOCAL DATA")
        logger.info("="*70)
        
        # Load JSON files
        json_count = 0
        for json_file in sorted(self.data_dir.glob("*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                source = json_file.stem
                
                if "hadiths" in data:
                    for h in data["hadiths"]:
                        text = h.get("english", {})
                        if isinstance(text, dict):
                            text = text.get("text", "")
                        if text:
                            self.texts.append(text)
                            self.metadata.append({
                                "source": source,
                                "type": "hadith",
                                "id": str(h.get("id") or h.get("hadithnumber") or "")
                            })
                    json_count += len(data["hadiths"])
                    logger.info(f"   ✅ {source}: {len(data['hadiths'])} hadiths")
                
                elif "data" in data and isinstance(data["data"], list):
                    for entry in data["data"]:
                        if "name" in entry:
                            content = entry.get("en", {})
                            if isinstance(content, dict):
                                content = content.get("meaning", "") or content.get("text", "")
                            if content:
                                self.texts.append(content)
                                self.metadata.append({
                                    "source": source,
                                    "type": "reference"
                                })
                    json_count += len(data["data"])
                    logger.info(f"   ✅ {source}: {len(data['data'])} items")
            
            except Exception as e:
                logger.warning(f"   ⚠️  {json_file.name}: {e}")
        
        # Load TXT files
        txt_count = 0
        for txt_file in sorted(self.data_dir.glob("*.txt")):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split by paragraphs
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                
                for para in paragraphs:
                    if len(para) > 50:  # Only include substantial paragraphs
                        self.texts.append(para)
                        self.metadata.append({
                            "source": txt_file.stem,
                            "type": "text"
                        })
                
                txt_count += len(paragraphs)
                logger.info(f"   ✅ {txt_file.name}: {len(paragraphs)} paragraphs")
            
            except Exception as e:
                logger.warning(f"   ⚠️  {txt_file.name}: {e}")
        
        logger.info(f"\n✅ Total local documents loaded: {len(self.texts)}")
        return len(self.texts) > 0
    
    def load_github_data_safe(self):
        """Safely load GitHub data with timeout handling"""
        logger.info("\n" + "="*70)
        logger.info("🌐 OPTIONAL: LOADING GITHUB DATA (with 20s timeout)")
        logger.info("="*70)
        
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from requests.packages.urllib3.util.retry import Retry
            
            # Create session with retries
            session = requests.Session()
            retry = Retry(connect=2, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            logger.info("   📥 Attempting to download from GitHub...")
            logger.info("   (This may take 10-20 seconds or skip if timeout)")
            
            # Try to get one Quran translation file as test
            url = "https://raw.githubusercontent.com/islamAndAi/QURAN-NLP/master/data/translation/english/quran_en.json"
            
            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                github_count = 0
                
                if "chapters" in data:
                    for chapter in data.get("chapters", []):
                        surah_num = chapter.get("number", 0)
                        surah_name = chapter.get("name", f"Surah {surah_num}")
                        
                        for verse in chapter.get("verses", []):
                            verse_num = verse.get("number", 0)
                            text = verse.get("text", "")
                            
                            if text:
                                formatted = f"{surah_name}:{verse_num}|{text}"
                                self.texts.append(formatted)
                                self.metadata.append({
                                    "source": "github_quran_en",
                                    "type": "quran_translation",
                                    "surah": surah_num,
                                    "verse": verse_num
                                })
                                github_count += 1
                    
                    logger.info(f"   ✅ GitHub Quran English: {github_count} verses")
                    return github_count > 0
            
            except requests.exceptions.Timeout:
                logger.warning("   ⏱️  GitHub download timeout (network slow) - skipping")
                return False
            
            except requests.exceptions.ConnectionError:
                logger.warning("   🌐 GitHub connection failed - skipping")
                return False
            
            except Exception as e:
                logger.warning(f"   ⚠️  GitHub error: {e} - continuing with local data")
                return False
        
        except ImportError:
            logger.warning("   📦 requests library not available - skipping GitHub")
            return False
    
    def build_index(self):
        """Build BM25 index"""
        logger.info("\n" + "="*70)
        logger.info("🎯 BUILDING BM25 INDEX")
        logger.info("="*70)
        
        if not self.texts:
            logger.error("❌ No documents to index!")
            return False
        
        try:
            logger.info(f"   📊 Tokenizing {len(self.texts)} documents...")
            corpus = [word_tokenize(text.lower()) for text in self.texts]
            
            logger.info("   ⚙️  Building BM25 model...")
            bm25 = BM25Okapi(corpus)
            
            # Save
            payload = {
                'bm25': bm25,
                'texts': self.texts,
                'metadata': self.metadata,
                'total_docs': len(self.texts),
                'source': 'quran_nlp_enhanced'
            }
            
            index_path = self.knowledge_dir / "bm25_index_enhanced.pkl"
            logger.info(f"   💾 Saving index...")
            with open(index_path, 'wb') as f:
                pickle.dump(payload, f)
            
            index_size = os.path.getsize(index_path) / 1024 / 1024
            
            logger.info("\n" + "="*70)
            logger.info("✨ INGESTION COMPLETE!")
            logger.info("="*70)
            logger.info(f"\n📊 STATISTICS:")
            logger.info(f"   ✅ Total documents: {len(self.texts)}")
            logger.info(f"   ✅ Index size: {index_size:.1f} MB")
            logger.info(f"   ✅ Index path: {index_path}")
            
            # Breakdown
            source_counts = {}
            type_counts = {}
            for meta in self.metadata:
                source_counts[meta.get('source', 'unknown')] = source_counts.get(meta.get('source', 'unknown'), 0) + 1
                type_counts[meta.get('type', 'unknown')] = type_counts.get(meta.get('type', 'unknown'), 0) + 1
            
            logger.info(f"\n📂 By source (top 10):")
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.info(f"   • {source}: {count}")
            
            logger.info(f"\n📚 By type:")
            for doc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   • {doc_type}: {count}")
            
            logger.info("\n🚀 NEXT STEPS:")
            logger.info("   1. Restart backend: pkill -f web_api.py")
            logger.info("   2. Start backend: python backend/api/web_api.py")
            logger.info("   3. Query: curl -X POST http://localhost:5010/api/chat ...")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to build index: {e}")
            return False
    
    def run(self):
        """Run complete ingestion"""
        logger.info("\n" + "🌟" * 40)
        logger.info("FAST ISLAMIC KNOWLEDGE BASE INGESTION")
        logger.info("🌟" * 40)
        
        # Load local data (required)
        if not self.load_local_data():
            logger.error("❌ Failed to load local data!")
            return False
        
        # Try GitHub data (optional)
        self.load_github_data_safe()
        
        # Build index
        return self.build_index()


if __name__ == "__main__":
    ingester = FastIslamicIngester()
    success = ingester.run()
    exit(0 if success else 1)

"""
Islamic AI Agent - Auto Ingestion Service
Monitors knowledge/data folder and automatically ingests new files
"""

import os
import json
import time
import logging
import threading
import pickle
import glob
import hashlib
from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime
import queue

from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoIngestService")

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class FileMonitor:
    """Monitor folder for new/modified files"""
    
    def __init__(self, data_dir: str, state_file: str):
        self.data_dir = data_dir
        self.state_file = state_file
        self.file_states: Dict[str, str] = self._load_state()
    
    def _load_state(self) -> Dict[str, str]:
        """Load file hashes from state file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_state(self):
        """Save file hashes to state file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.file_states, f, indent=2)
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of file"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    
    def get_new_or_modified_files(self) -> List[str]:
        """Get list of new or modified files"""
        new_files = []
        
        # Check all supported files
        for pattern in ['*.json', '*.txt', '*.pdf', '*.csv']:
            files = glob.glob(os.path.join(self.data_dir, pattern))
            
            for file_path in files:
                file_name = os.path.basename(file_path)
                
                if not os.path.isfile(file_path):
                    continue
                
                current_hash = self._get_file_hash(file_path)
                stored_hash = self.file_states.get(file_name)
                
                # New or modified file
                if current_hash != stored_hash:
                    new_files.append(file_path)
                    self.file_states[file_name] = current_hash
        
        if new_files:
            self._save_state()
        
        return new_files


class DocumentProcessor:
    """Process different file types into documents"""
    
    @staticmethod
    def process_json(file_path: str, file_name: str) -> List[Dict]:
        """Process JSON file"""
        documents = []
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            
            # Hadiths
            if "hadiths" in data and isinstance(data["hadiths"], list):
                logger.info(f"  📖 Processing {len(data['hadiths'])} hadiths from {file_name}")
                for h in data["hadiths"]:
                    eng = h.get("english", {}) or {}
                    text = eng.get("text", "").strip()
                    if text:
                        documents.append({
                            "content": f"Hadith: {text}",
                            "metadata": {
                                "source": file_name,
                                "type": "hadith",
                                "id": str(h.get("id") or h.get("hadithnumber") or ""),
                                "book": h.get("bookName") or h.get("book_name") or "General",
                                "narrator": eng.get("narrator", ""),
                                "grade": h.get("grade") or h.get("status") or "Authentic"
                            }
                        })
            
            # Duas/Adhkar
            elif "English" in data and isinstance(data["English"], list):
                logger.info(f"  🤲 Processing Duas/Adhkar from {file_name}")
                for cat in data["English"]:
                    category = cat.get("category", "General")
                    for item in cat.get("content", []):
                        text = item.get("text", "").strip()
                        if text:
                            documents.append({
                                "content": f"Dua: {text}",
                                "metadata": {
                                    "source": file_name,
                                    "type": "dua",
                                    "category": category,
                                    "reference": item.get("reference", "")
                                }
                            })
            
            # Names/Attributes
            elif "data" in data and isinstance(data["data"], list):
                logger.info(f"  ✨ Processing {len(data['data'])} entries from {file_name}")
                for entry in data["data"]:
                    name = entry.get("name", "")
                    if name:
                        meaning = entry.get("en", {}).get("meaning", "N/A") if isinstance(entry.get("en"), dict) else "N/A"
                        documents.append({
                            "content": f"{name}: {meaning}",
                            "metadata": {
                                "source": file_name,
                                "type": "attribute",
                                "name": name
                            }
                        })
        
        except json.JSONDecodeError as e:
            logger.error(f"  ❌ JSON error in {file_name}: {e}")
        except Exception as e:
            logger.error(f"  ❌ Error processing {file_name}: {e}")
        
        return documents
    
    @staticmethod
    def process_txt(file_path: str, file_name: str) -> List[Dict]:
        """Process TXT file"""
        documents = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Split by paragraphs
            paragraphs = text.split('\n\n')
            logger.info(f"  📄 Processing {len(paragraphs)} paragraphs from {file_name}")
            
            for para in paragraphs:
                para = para.strip()
                if para and len(para) > 20:  # Minimum length
                    documents.append({
                        "content": para,
                        "metadata": {
                            "source": file_name,
                            "type": "text",
                            "length": len(para)
                        }
                    })
        
        except Exception as e:
            logger.error(f"  ❌ Error processing {file_name}: {e}")
        
        return documents
    
    @staticmethod
    def process_csv(file_path: str, file_name: str) -> List[Dict]:
        """Process CSV file"""
        documents = []
        
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                logger.info(f"  📊 Processing CSV from {file_name}")
                
                for i, row in enumerate(reader):
                    # Convert row to text
                    content = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
                    if content:
                        documents.append({
                            "content": content,
                            "metadata": {
                                "source": file_name,
                                "type": "csv",
                                "row": i
                            }
                        })
        
        except Exception as e:
            logger.error(f"  ❌ Error processing {file_name}: {e}")
        
        return documents
    
    @staticmethod
    def process_file(file_path: str) -> List[Dict]:
        """Process any supported file type"""
        file_name = os.path.basename(file_path)
        
        if file_path.endswith('.json'):
            return DocumentProcessor.process_json(file_path, file_name)
        elif file_path.endswith('.txt'):
            return DocumentProcessor.process_txt(file_path, file_name)
        elif file_path.endswith('.csv'):
            return DocumentProcessor.process_csv(file_path, file_name)
        else:
            logger.warning(f"⚠️  Unsupported file type: {file_name}")
            return []


class BM25Updater:
    """Update BM25 index with new documents"""
    
    def __init__(self, bm25_path: str):
        self.bm25_path = bm25_path
        self.data = self._load_bm25()
    
    def _load_bm25(self) -> Dict:
        """Load existing BM25 index"""
        if os.path.exists(self.bm25_path):
            try:
                with open(self.bm25_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        
        # Initialize empty
        return {
            'bm25': None,
            'texts': [],
            'metadata': [],
            'total_docs': 0
        }
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """Add documents to BM25 index"""
        try:
            for doc in documents:
                content = doc.get('content', '').strip()
                if content:
                    self.data['texts'].append(content)
                    self.data['metadata'].append(doc.get('metadata', {}))
            
            # Rebuild BM25
            if self.data['texts']:
                corpus = [word_tokenize(text.lower()) for text in self.data['texts']]
                self.data['bm25'] = BM25Okapi(corpus)
                self.data['total_docs'] = len(self.data['texts'])
                
                # Save
                with open(self.bm25_path, 'wb') as f:
                    pickle.dump(self.data, f)
                
                logger.info(f"  ✅ Updated BM25 index: {len(self.data['texts'])} documents")
                return True
        
        except Exception as e:
            logger.error(f"  ❌ Error updating BM25: {e}")
        
        return False


class AutoIngestService:
    """Main auto ingestion service"""
    
    def __init__(self, data_dir: str, bm25_path: str, check_interval: int = 5):
        self.data_dir = data_dir
        self.bm25_path = bm25_path
        self.check_interval = check_interval
        
        # Create directories if needed
        os.makedirs(data_dir, exist_ok=True)
        
        self.state_file = os.path.join(os.path.dirname(bm25_path), "auto_ingest_state.json")
        self.monitor = FileMonitor(data_dir, self.state_file)
        self.processor = DocumentProcessor()
        self.bm25_updater = BM25Updater(bm25_path)
        
        self.is_running = False
        self.thread = None
        self.ingest_queue = queue.Queue()
        
        logger.info(f"🚀 Auto Ingest Service initialized")
        logger.info(f"   Data directory: {data_dir}")
        logger.info(f"   Check interval: {check_interval}s")
    
    def start(self):
        """Start the service"""
        if self.is_running:
            logger.warning("Service already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("✅ Auto ingest service started")
    
    def stop(self):
        """Stop the service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("✅ Auto ingest service stopped")
    
    def _run(self):
        """Main service loop"""
        while self.is_running:
            try:
                # Check for new files
                new_files = self.monitor.get_new_or_modified_files()
                
                if new_files:
                    logger.info(f"\n📂 Found {len(new_files)} new/modified file(s)")
                    
                    for file_path in new_files:
                        self._ingest_file(file_path)
                
                # Sleep
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"❌ Service error: {e}")
                time.sleep(self.check_interval)
    
    def _ingest_file(self, file_path: str):
        """Ingest a single file"""
        file_name = os.path.basename(file_path)
        logger.info(f"\n🔄 Ingesting: {file_name}")
        
        try:
            # Process file
            documents = self.processor.process_file(file_path)
            
            if documents:
                # Update BM25
                if self.bm25_updater.add_documents(documents):
                    logger.info(f"✅ Successfully ingested {file_name} ({len(documents)} documents)")
                    
                    # Emit event
                    self.ingest_queue.put({
                        "status": "success",
                        "file": file_name,
                        "documents": len(documents),
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.error(f"❌ Failed to update BM25 for {file_name}")
            else:
                logger.warning(f"⚠️  No documents extracted from {file_name}")
        
        except Exception as e:
            logger.error(f"❌ Error ingesting {file_name}: {e}")
            self.ingest_queue.put({
                "status": "error",
                "file": file_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def get_status(self) -> Dict:
        """Get service status"""
        if self.bm25_updater.data.get('bm25'):
            total_docs = self.bm25_updater.data.get('total_docs', 0)
        else:
            total_docs = 0
        
        return {
            "running": self.is_running,
            "data_directory": self.data_dir,
            "total_documents": total_docs,
            "check_interval": self.check_interval,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_ingestions(self, limit: int = 10) -> List[Dict]:
        """Get recent ingestion events"""
        events = []
        while len(events) < limit and not self.ingest_queue.empty():
            try:
                events.append(self.ingest_queue.get_nowait())
            except queue.Empty:
                break
        return events


# Global service instance
_service_instance: Optional[AutoIngestService] = None


def initialize_auto_ingest(data_dir: str, bm25_path: str, check_interval: int = 5) -> AutoIngestService:
    """Initialize and start auto ingest service"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = AutoIngestService(data_dir, bm25_path, check_interval)
        _service_instance.start()
    
    return _service_instance


def get_auto_ingest_service() -> Optional[AutoIngestService]:
    """Get the service instance"""
    return _service_instance


def stop_auto_ingest():
    """Stop the service"""
    global _service_instance
    if _service_instance:
        _service_instance.stop()

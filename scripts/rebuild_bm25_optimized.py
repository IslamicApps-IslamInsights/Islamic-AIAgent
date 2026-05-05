#!/usr/bin/env python3
"""
Rebuild BM25 Index with Optimized Quran Chunking
Properly indexes Quran, Tafsir, Hadith, and Scholarly sources
"""

import os
import sys
import glob
import json
import pickle
import logging
from pathlib import Path
from collections import Counter
from typing import List, Tuple

# Project paths will be set in main()

from nltk.tokenize import word_tokenize
from rank_bm25 import BM25Okapi
import nltk

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BM25Rebuild")

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("📥 Downloading NLTK tokenizer...")
    nltk.download('punkt', quiet=True)


class OptimizedBM25Builder:
    """Build BM25 index with intelligent chunking"""
    
    def __init__(self, data_dir: str, output_path: str):
        self.data_dir = data_dir
        self.output_path = output_path
        self.texts = []
        self.metadata = []
    
    def chunk_quran(self, text: str, source: str, chunk_size: int = 300) -> List[Tuple[str, dict]]:
        """
        Intelligently chunk Quran text for better retrieval
        
        Splits by verses (format: SURAH|VERSE|TEXT) while maintaining semantic meaning
        """
        chunks = []
        
        # Split by individual verses (each line in format SURAH|VERSE|TEXT)
        lines = text.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        current_chunk = ""
        chunk_verses = []
        
        for idx, line in enumerate(lines):
            # Try to extract surah and verse info for metadata
            parts = line.split('|')
            verse_id = f"{parts[0]}:{parts[1]}" if len(parts) >= 2 else str(idx)
            
            # Check if adding this verse exceeds chunk size
            if len(current_chunk) + len(line) > chunk_size and current_chunk:
                # Save current chunk
                if chunk_verses:
                    chunks.append((
                        current_chunk.strip(),
                        {
                            'source': source,
                            'type': 'quran',
                            'verse_range': f"{chunk_verses[0]}-{chunk_verses[-1]}",
                            'chunk_size': len(current_chunk)
                        }
                    ))
                
                # Start new chunk with overlap (last verse from previous chunk + current verse)
                overlap = '\n'.join(lines[max(0, idx-2):idx])  # 2 verses overlap
                current_chunk = overlap + "\n" + line
                chunk_verses = [verse_id]
            else:
                current_chunk += "\n" + line if current_chunk else line
                chunk_verses.append(verse_id)
        
        # Don't forget last chunk
        if current_chunk.strip() and chunk_verses:
            chunks.append((
                current_chunk.strip(),
                {
                    'source': source,
                    'type': 'quran',
                    'verse_range': f"{chunk_verses[0]}-{chunk_verses[-1]}",
                    'chunk_size': len(current_chunk)
                }
            ))
        
        return chunks
    
    def chunk_tafsir(self, text: str, source: str, chunk_size: int = 400) -> List[Tuple[str, dict]]:
        """Chunk Tafsir (interpretation) content"""
        chunks = []
        
        sections = text.split('\n\n')
        sections = [s.strip() for s in sections if s.strip()]
        
        current_chunk = ""
        section_count = 0
        
        for section in sections:
            if len(current_chunk) + len(section) > chunk_size and current_chunk:
                chunks.append((
                    current_chunk.strip(),
                    {
                        'source': source,
                        'type': 'tafsir',
                        'section_count': section_count,
                        'chunk_size': len(current_chunk)
                    }
                ))
                current_chunk = section
                section_count = 1
            else:
                current_chunk += "\n\n" + section
                section_count += 1
        
        if current_chunk.strip():
            chunks.append((
                current_chunk.strip(),
                {
                    'source': source,
                    'type': 'tafsir',
                    'section_count': section_count,
                    'chunk_size': len(current_chunk)
                }
            ))
        
        return chunks
    
    def load_data(self) -> Tuple[int, int]:
        """Load and chunk all data"""
        
        # Counter for statistics
        stats = Counter()
        
        # ============================================================
        # 1. LOAD QURAN (Optimized with smart chunking)
        # ============================================================
        logger.info("📖 Loading Quran translations...")
        
        quran_files = [
            'quran_yusuf_ali.txt',
            'quran_saheeh_international.txt',
            'quran_pickthall.txt',
            'quran_shakir.txt'
        ]
        
        for filename in quran_files:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                logger.info(f"   Processing {filename}...")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    chunks = self.chunk_quran(text, filename, chunk_size=300)
                    
                    for text_chunk, meta in chunks:
                        if len(text_chunk) > 100:  # Minimum chunk size
                            self.texts.append(text_chunk)
                            self.metadata.append(meta)
                            stats['quran_chunks'] += 1
                    
                    logger.info(f"      ✅ {filename}: {len(chunks)} chunks")
                
                except Exception as e:
                    logger.error(f"      ❌ Error: {e}")
        
        # ============================================================
        # 2. LOAD TAFSIR (Quranic Interpretation)
        # ============================================================
        logger.info("📚 Loading Tafsir...")
        
        tafsir_files = ['tafsir_ibn_kathir_highlights.txt']
        
        for filename in tafsir_files:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                logger.info(f"   Processing {filename}...")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    chunks = self.chunk_tafsir(text, filename)
                    
                    for text_chunk, meta in chunks:
                        if len(text_chunk) > 100:
                            self.texts.append(text_chunk)
                            self.metadata.append(meta)
                            stats['tafsir_chunks'] += 1
                    
                    logger.info(f"      ✅ {filename}: {len(chunks)} chunks")
                
                except Exception as e:
                    logger.error(f"      ❌ Error: {e}")
        
        # Quran metadata
        filepath = os.path.join(self.data_dir, 'quran_surah_metadata_114.json')
        if os.path.exists(filepath):
            logger.info(f"   Processing quran_surah_metadata_114.json...")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for item in data:
                        text = json.dumps(item, ensure_ascii=False)
                        self.texts.append(text)
                        self.metadata.append({
                            'source': 'quran_surah_metadata_114.json',
                            'type': 'quran_metadata',
                            'surah': item.get('surah', ''),
                            'id': item.get('id', '')
                        })
                        stats['quran_metadata'] += 1
                
                logger.info(f"      ✅ Loaded {stats['quran_metadata']} Quranic metadata entries")
            
            except Exception as e:
                logger.error(f"      ❌ Error: {e}")
        
        # ============================================================
        # 3. LOAD HADITH (Prophetic Traditions)
        # ============================================================
        logger.info("📖 Loading Hadith collections...")
        
        json_files = glob.glob(os.path.join(self.data_dir, "*.json"))
        
        for filepath in json_files:
            filename = os.path.basename(filepath)
            
            # Skip Quran metadata
            if 'quran' in filename.lower():
                continue
            
            logger.info(f"   Processing {filename}...")
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                
                hadith_count = 0
                
                # Different formats for different sources
                if isinstance(data, dict):
                    # Format: {"hadiths": [...]}
                    if "hadiths" in data:
                        for h in data["hadiths"]:
                            text = h.get("english", {})
                            if isinstance(text, dict):
                                text = text.get("text", "")
                            
                            if text and len(text) > 50:
                                self.texts.append(text)
                                self.metadata.append({
                                    'source': filename,
                                    'type': 'hadith',
                                    'id': str(h.get('id') or h.get('hadithnumber') or ''),
                                    'grade': h.get('grade', ''),
                                    'book': h.get('book', '')
                                })
                                hadith_count += 1
                    
                    # Format: {"data": [...]}
                    elif "data" in data and isinstance(data["data"], list):
                        for entry in data["data"]:
                            text = entry.get("en", {})
                            if isinstance(text, dict):
                                text = text.get("meaning", "")
                            
                            if text and len(text) > 50:
                                self.texts.append(text)
                                self.metadata.append({
                                    'source': filename,
                                    'type': 'metadata',
                                    'name': entry.get('name', '')
                                })
                                hadith_count += 1
                
                elif isinstance(data, list):
                    for item in data:
                        text = json.dumps(item, ensure_ascii=False)[:500]
                        if len(text) > 50:
                            self.texts.append(text)
                            self.metadata.append({
                                'source': filename,
                                'type': 'hadith'
                            })
                            hadith_count += 1
                
                stats[filename] = hadith_count
                logger.info(f"      ✅ {filename}: {hadith_count} entries")
            
            except Exception as e:
                logger.error(f"      ❌ Error: {e}")
        
        # ============================================================
        # 4. LOAD OTHER SOURCES (Scholarly, Ethics, etc.)
        # ============================================================
        logger.info("📕 Loading scholarly sources...")
        
        txt_files = glob.glob(os.path.join(self.data_dir, "*.txt"))
        
        # Exclude already processed Quran files
        exclude = {'quran_yusuf_ali.txt', 'quran_saheeh_international.txt', 'quran_pickthall.txt', 'quran_shakir.txt', 'tafsir_ibn_kathir_highlights.txt'}
        
        for filepath in txt_files:
            filename = os.path.basename(filepath)
            
            if filename in exclude or 'quran' in filename.lower():
                continue
            
            logger.info(f"   Processing {filename}...")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Chunk by paragraphs
                paragraphs = text.split('\n\n')
                scholarly_count = 0
                
                for para in paragraphs:
                    para = para.strip()
                    if len(para) > 100:
                        self.texts.append(para)
                        self.metadata.append({
                            'source': filename,
                            'type': 'scholarly',
                            'section_size': len(para)
                        })
                        scholarly_count += 1
                
                stats[filename] = scholarly_count
                logger.info(f"      ✅ {filename}: {scholarly_count} sections")
            
            except Exception as e:
                logger.error(f"      ❌ Error: {e}")
        
        return len(self.texts), len(self.metadata)
    
    def build_bm25(self):
        """Build and save BM25 index"""
        logger.info(f"🔨 Building BM25 index from {len(self.texts)} documents...")
        
        # Tokenize all texts
        corpus = []
        for text in self.texts:
            try:
                tokens = word_tokenize(text.lower())
                corpus.append(tokens)
            except Exception as e:
                logger.warning(f"Tokenization error: {e}")
                corpus.append([])
        
        # Build BM25
        logger.info("   Initializing BM25...")
        bm25 = BM25Okapi(corpus)
        
        # Save
        logger.info(f"   Saving to {self.output_path}...")
        payload = {
            'bm25': bm25,
            'texts': self.texts,
            'metadata': self.metadata,
            'total_docs': len(self.texts),
            'corpus_size': sum(len(t) for t in self.texts)
        }
        
        with open(self.output_path, 'wb') as f:
            pickle.dump(payload, f)
        
        file_size_mb = os.path.getsize(self.output_path) / 1024 / 1024
        logger.info(f"✅ BM25 index saved: {file_size_mb:.1f} MB")
    
    def print_statistics(self):
        """Print detailed statistics"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 BM25 INDEX BUILD COMPLETE")
        logger.info("=" * 70)
        
        # Source statistics
        source_stats = Counter()
        type_stats = Counter()
        
        for meta in self.metadata:
            source_stats[meta.get('source', 'unknown')] += 1
            type_stats[meta.get('type', 'unknown')] += 1
        
        logger.info(f"\n📈 OVERALL STATISTICS:")
        logger.info(f"   Total documents: {len(self.texts):,}")
        logger.info(f"   Total corpus size: {sum(len(t) for t in self.texts):,} characters")
        logger.info(f"   Average doc size: {sum(len(t) for t in self.texts) / len(self.texts):.0f} characters")
        
        logger.info(f"\n📚 SOURCE BREAKDOWN (Top 15):")
        for source, count in source_stats.most_common(15):
            pct = (count / len(self.texts)) * 100
            logger.info(f"   {source:40s}: {count:6,d} ({pct:5.1f}%)")
        
        logger.info(f"\n🏷️  CONTENT TYPE BREAKDOWN:")
        for ctype, count in type_stats.most_common():
            pct = (count / len(self.texts)) * 100
            logger.info(f"   {ctype:30s}: {count:6,d} ({pct:5.1f}%)")
        
        logger.info("=" * 70 + "\n")


def main():
    """Main execution"""
    
    # Get proper paths
    current_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/ directory
    project_root_actual = os.path.dirname(current_dir)  # Islamic-AIAgent/
    data_dir = os.path.join(project_root_actual, "backend/knowledge/data")
    output_path = os.path.join(project_root_actual, "backend/knowledge/bm25_index.pkl")
    
    logger.info(f"🚀 Starting BM25 Index Rebuild with Optimized Quran Chunking")
    logger.info(f"   Data dir: {data_dir}")
    logger.info(f"   Output path: {output_path}\n")
    
    builder = OptimizedBM25Builder(data_dir, output_path)
    
    # Load data
    text_count, meta_count = builder.load_data()
    logger.info(f"\n✅ Loaded {text_count} texts with {meta_count} metadata records\n")
    
    # Build BM25
    builder.build_bm25()
    
    # Print statistics
    builder.print_statistics()
    
    logger.info("✨ Index rebuild complete! Your Quran is now properly indexed.")
    logger.info("🎯 Next: Restart the backend to use the new index")


if __name__ == "__main__":
    main()

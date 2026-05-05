"""
Improved Quran & Tafsir Indexing with Quran Foundation MCP Integration
Properly chunks Quran text and integrates with local training model
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger("QuranIndexing")


class QuranOptimizedIndexer:
    """Optimized indexing for Quran and Tafsir with proper chunking"""
    
    def __init__(self, data_dir: str = "backend/knowledge/data"):
        self.data_dir = data_dir
        self.quran_chunks = []
        self.quran_metadata = []
        
    def chunk_quran_text(self, text: str, source: str, chunk_size: int = 200, overlap: int = 50) -> List[Tuple[str, Dict]]:
        """
        Chunk Quran text by verses/sections intelligently
        
        Args:
            text: Full Quran text
            source: Source file name
            chunk_size: Characters per chunk
            overlap: Overlap between chunks
        """
        chunks = []
        
        # Split by verse markers (often "Verse X" or numbering)
        verses = text.split('\n\n')  # Paragraph breaks
        
        current_chunk = ""
        current_metadata = {"source": source, "type": "quran", "verses": []}
        verse_num = 0
        
        for verse in verses:
            verse = verse.strip()
            if not verse:
                continue
            
            verse_num += 1
            
            # If adding this verse exceeds chunk size, save current chunk
            if len(current_chunk) + len(verse) > chunk_size and current_chunk:
                chunks.append((
                    current_chunk.strip(),
                    {
                        **current_metadata,
                        "chunk_size": len(current_chunk),
                        "verse_range": f"{current_metadata['verses'][0]}-{current_metadata['verses'][-1]}"
                    }
                ))
                
                # Keep overlap
                current_chunk = current_chunk[-overlap:] + "\n" + verse
                current_metadata = {
                    "source": source,
                    "type": "quran",
                    "verses": [verse_num]
                }
            else:
                current_chunk += "\n" + verse
                current_metadata["verses"].append(verse_num)
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append((
                current_chunk.strip(),
                {
                    **current_metadata,
                    "chunk_size": len(current_chunk),
                    "verse_range": f"{current_metadata['verses'][0]}-{current_metadata['verses'][-1]}"
                }
            ))
        
        return chunks
    
    def load_optimized_quran(self) -> Tuple[List[str], List[Dict]]:
        """Load Quran text files with optimized chunking"""
        texts = []
        metadatas = []
        
        quran_files = [
            'quran_yusuf_ali.txt',
            'quran_saheeh_international.txt',
            'quran_pickthall.txt',
            'quran_shakir.txt'
        ]
        
        for filename in quran_files:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                logger.info(f"📖 Loading {filename}...")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        full_text = f.read()
                    
                    # Intelligently chunk the Quran
                    chunks = self.chunk_quran_text(full_text, filename, chunk_size=300, overlap=100)
                    
                    for text, metadata in chunks:
                        if len(text) > 50:  # Minimum chunk size
                            texts.append(text)
                            metadatas.append(metadata)
                    
                    logger.info(f"   ✅ {filename}: {len(chunks)} chunks created")
                
                except Exception as e:
                    logger.error(f"   ❌ Error loading {filename}: {e}")
        
        return texts, metadatas
    
    def load_tafsir(self) -> Tuple[List[str], List[Dict]]:
        """Load Tafsir (Islamic interpretation) documents"""
        texts = []
        metadatas = []
        
        tafsir_files = [
            'tafsir_ibn_kathir_highlights.txt',
            'quran_surah_metadata_114.json'
        ]
        
        for filename in tafsir_files:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                logger.info(f"📚 Loading Tafsir: {filename}...")
                try:
                    if filename.endswith('.json'):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if isinstance(data, list):
                            for item in data:
                                text = json.dumps(item, ensure_ascii=False)
                                texts.append(text)
                                metadatas.append({
                                    "source": filename,
                                    "type": "tafsir_metadata",
                                    "surah": item.get('surah', ''),
                                    "id": item.get('id', '')
                                })
                    else:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            text = f.read()
                        
                        # Chunk tafsir by sections
                        sections = text.split('\n\n')
                        for section in sections:
                            if len(section) > 50:
                                texts.append(section)
                                metadatas.append({
                                    "source": filename,
                                    "type": "tafsir",
                                    "section_size": len(section)
                                })
                    
                    logger.info(f"   ✅ {filename}: {len(metadatas)} records loaded")
                
                except Exception as e:
                    logger.error(f"   ❌ Error loading {filename}: {e}")
        
        return texts, metadatas


# Integration with Quran Foundation MCP
class QuranFoundationMCPClient:
    """Client for Quran Foundation MCP tools"""
    
    @staticmethod
    def get_quran_verse(surah: int, verse: int) -> Dict[str, Any]:
        """
        Fetch specific verse from Quran Foundation MCP
        
        Args:
            surah: Chapter number (1-114)
            verse: Verse number in chapter
        """
        try:
            # Try to import Quran Foundation tools
            from backend.tools.quran_foundation import QuranFoundationTools
            
            tools = QuranFoundationTools()
            result = tools.get_quran_verse(surah, verse)
            return result
        except Exception as e:
            logger.warning(f"⚠️  Quran Foundation MCP error: {e}")
            return None
    
    @staticmethod
    def search_quran_topic(topic: str) -> List[Dict[str, Any]]:
        """
        Search Quran Foundation MCP for topic
        
        Args:
            topic: Topic to search for (e.g., "prayer", "charity")
        """
        try:
            from backend.tools.quran_foundation import QuranFoundationTools
            
            tools = QuranFoundationTools()
            results = tools.search_quran_by_topic(topic)
            return results or []
        except Exception as e:
            logger.warning(f"⚠️  Quran Foundation search error: {e}")
            return []


# Hybrid search with Quran prioritization
def search_with_quran_priority(
    query: str,
    local_kb_results: List[Dict[str, Any]],
    k_per_source: int = 2
) -> List[Dict[str, Any]]:
    """
    Reorder search results to prioritize Quran and Tafsir
    
    Args:
        query: Search query
        local_kb_results: Results from local KB
        k_per_source: Number of results per source type
    """
    
    # Group by source type
    quran_results = [r for r in local_kb_results if r.get('metadata', {}).get('type') in ['quran', 'tafsir', 'tafsir_metadata']]
    hadith_results = [r for r in local_kb_results if r.get('metadata', {}).get('type') == 'hadith']
    other_results = [r for r in local_kb_results if r.get('metadata', {}).get('type') not in ['quran', 'tafsir', 'tafsir_metadata', 'hadith']]
    
    # Reorder: Quran → Tafsir → Hadith → Other
    reordered = []
    reordered.extend(quran_results[:k_per_source])
    reordered.extend(hadith_results[:k_per_source])
    reordered.extend(other_results[:k_per_source])
    
    # If missing Quran, try Quran Foundation MCP
    if not quran_results:
        logger.info("📖 Quran not found in local KB, checking Quran Foundation MCP...")
        mcp_results = QuranFoundationMCPClient.search_quran_topic(query)
        
        if mcp_results:
            logger.info(f"✅ Found {len(mcp_results)} results from Quran Foundation MCP")
            for result in mcp_results[:k_per_source]:
                reordered.insert(0, {
                    "content": result.get('text', ''),
                    "metadata": {
                        "source": "Quran Foundation MCP",
                        "type": "quran_mcp",
                        "surah": result.get('surah', ''),
                        "verse": result.get('verse', ''),
                    },
                    "score": result.get('relevance', 0.8)
                })
    
    return reordered


# Local model training/fine-tuning
class LocalQuranModel:
    """Local model for Quran-aware response synthesis"""
    
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        """
        Initialize local model
        
        Free best models available:
        - mistralai/Mistral-7B-Instruct-v0.1 (fast, accurate)
        - HuggingFaceH4/zephyr-7b-beta (tuned for conversational)
        - meta-llama/Llama-2-7b-chat (if HF token available)
        - teknium/OpenHermes-2.5-Mistral-7B
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        logger.info(f"🤖 Initializing {model_name}...")
    
    def load_model(self):
        """Load the model from HuggingFace"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            logger.info(f"📥 Loading model: {self.model_name}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load in 8-bit or fp16 for memory efficiency
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_8bit=False  # Set True if OOM
            )
            
            logger.info(f"✅ Model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            return False
        
        return True
    
    def synthesize_response(
        self,
        query: str,
        context: List[str],
        max_length: int = 512
    ) -> str:
        """
        Generate response using local model with Islamic context
        
        Args:
            query: User question
            context: List of relevant passages from knowledge base
            max_length: Maximum response length
        """
        if not self.model or not self.tokenizer:
            logger.warning("⚠️  Model not loaded, using fallback")
            return self._fallback_response(query, context)
        
        try:
            # Build prompt with Islamic context
            context_str = "\n\n".join([f"• {c[:200]}..." for c in context[:3]])
            
            prompt = f"""Based on the Islamic knowledge provided, answer this question clearly and accurately.

Islamic Context:
{context_str}

Question: {query}

Answer in Islamic perspective, citing sources when relevant:"""
            
            # Tokenize and generate
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=0.3,
                    top_p=0.9,
                    do_sample=True
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract answer part
            if "Answer" in response:
                response = response.split("Answer")[-1].strip()
            
            return response
        
        except Exception as e:
            logger.error(f"❌ Synthesis error: {e}")
            return self._fallback_response(query, context)
    
    @staticmethod
    def _fallback_response(query: str, context: List[str]) -> str:
        """Fallback response when model unavailable"""
        if not context:
            return "I don't have sufficient information to answer this question."
        
        return f"Based on Islamic sources: {context[0][:300]}..."


# Export key functions
def get_optimized_quran_index() -> Tuple[List[str], List[Dict]]:
    """Get optimized Quran + Tafsir index"""
    indexer = QuranOptimizedIndexer()
    
    quran_texts, quran_meta = indexer.load_optimized_quran()
    tafsir_texts, tafsir_meta = indexer.load_tafsir()
    
    all_texts = quran_texts + tafsir_texts
    all_meta = quran_meta + tafsir_meta
    
    logger.info(f"📊 Optimized Index Ready:")
    logger.info(f"   Quran chunks: {len(quran_texts)}")
    logger.info(f"   Tafsir chunks: {len(tafsir_texts)}")
    logger.info(f"   Total: {len(all_texts)}")
    
    return all_texts, all_meta

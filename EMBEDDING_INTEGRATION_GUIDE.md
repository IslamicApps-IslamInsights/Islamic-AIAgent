# 🔧 EMBEDDING INTEGRATION GUIDE - Step-by-Step Implementation

## Overview

This guide walks you through integrating the enhanced embedding system into your Islamic knowledge base retrieval pipeline.

---

## Step 1: Initialize Embedding System

### Basic Initialization

```python
from backend.config.unified_models import (
    get_embedding_config,
    get_primary_embedding_model,
)
from sentence_transformers import SentenceTransformer
import numpy as np

# Get enhanced configuration
config = get_embedding_config()

# Load model
model = SentenceTransformer(config['name'])
model.to(config['device'])

# Verify configuration
print(f"✅ Model: {config['name']}")
print(f"✅ Device: {config['device']}")
print(f"✅ Dimensions: {config['dimensions']}")
```

### Production Initialization with Caching

```python
class EmbeddingManager:
    def __init__(self):
        self.config = get_embedding_config()
        self.model = SentenceTransformer(self.config['name'])
        self.model.to(self.config['device'])
        
        # Initialize cache
        self.embedding_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_embeddings(self, texts, use_cache=True):
        """Get embeddings with caching"""
        embeddings = []
        cache_keys = []
        texts_to_embed = []
        indices = []
        
        # Check cache
        for i, text in enumerate(texts):
            key = hash(text) if use_cache else None
            cache_keys.append(key)
            
            if use_cache and key in self.embedding_cache:
                embeddings.append(self.embedding_cache[key])
                self.cache_hits += 1
            else:
                texts_to_embed.append(text)
                indices.append(i)
                self.cache_misses += 1
        
        # Embed new texts
        if texts_to_embed:
            batch_size = self.config['batch_size']
            new_embeddings = []
            
            for j in range(0, len(texts_to_embed), batch_size):
                batch = texts_to_embed[j:j+batch_size]
                batch_with_instructions = [
                    self.config['passage_instruction'] + " " + text
                    for text in batch
                ]
                embeddings_batch = self.model.encode(
                    batch_with_instructions,
                    normalize_embeddings=self.config['normalize'],
                    show_progress_bar=False
                )
                new_embeddings.extend(embeddings_batch)
            
            # Cache new embeddings
            for i, idx in enumerate(indices):
                if cache_keys[idx]:
                    self.embedding_cache[cache_keys[idx]] = new_embeddings[i]
                embeddings.insert(idx, new_embeddings[i])
        
        return np.array(embeddings)
    
    def get_cache_stats(self):
        """Get cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total * 100 if total > 0 else 0
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'cache_size': len(self.embedding_cache)
        }
```

---

## Step 2: Semantic Search Implementation

### Basic Semantic Search

```python
def semantic_search(query: str, knowledge_base_texts: list, 
                    embeddings_manager: EmbeddingManager):
    """Simple semantic search"""
    
    config = embeddings_manager.config
    
    # Embed query
    query_with_instruction = (
        config['query_instruction'] + " " + query
    )
    query_embedding = embeddings_manager.model.encode(
        query_with_instruction,
        normalize_embeddings=config['normalize']
    )
    
    # Get KB embeddings
    kb_embeddings = embeddings_manager.get_embeddings(knowledge_base_texts)
    
    # Calculate similarities
    similarities = query_embedding @ kb_embeddings.T
    
    # Get top results
    top_indices = similarities.argsort()[-config['top_k']:][::-1]
    
    results = [
        {
            'text': knowledge_base_texts[i],
            'similarity': float(similarities[i]),
            'rank': idx + 1
        }
        for idx, i in enumerate(top_indices)
    ]
    
    return results
```

### Query-Type Aware Semantic Search

```python
from backend.config.unified_models import get_optimal_embedding_for_query

def intelligent_semantic_search(query: str, query_type: str,
                                 knowledge_base_texts: list,
                                 embeddings_manager: EmbeddingManager):
    """Search with query-type specific optimizations"""
    
    # Get optimal config for query type
    optimal_config = get_optimal_embedding_for_query(query_type)
    
    # Embed query
    query_with_instruction = (
        optimal_config['instruction'] + " " + query
    )
    query_embedding = embeddings_manager.model.encode(
        query_with_instruction,
        normalize_embeddings=embeddings_manager.config['normalize']
    )
    
    # Get KB embeddings
    kb_embeddings = embeddings_manager.get_embeddings(knowledge_base_texts)
    
    # Calculate similarities
    similarities = query_embedding @ kb_embeddings.T
    
    # Filter by threshold
    valid_indices = np.where(
        similarities >= optimal_config['similarity_threshold']
    )[0]
    
    # Get top results
    top_count = min(optimal_config['top_k'], len(valid_indices))
    top_indices = valid_indices[similarities[valid_indices].argsort()][-top_count:][::-1]
    
    results = [
        {
            'text': knowledge_base_texts[i],
            'similarity': float(similarities[i]),
            'rank': idx + 1,
            'query_type': query_type
        }
        for idx, i in enumerate(top_indices)
    ]
    
    return results
```

---

## Step 3: Hybrid Search (Semantic + Keyword)

### Hybrid Search Implementation

```python
from rank_bm25 import BM25Okapi

class HybridSearcher:
    def __init__(self, knowledge_base_texts: list, 
                 embeddings_manager: EmbeddingManager):
        self.kb_texts = knowledge_base_texts
        self.embeddings_manager = embeddings_manager
        self.config = embeddings_manager.config
        
        # Prepare BM25
        tokenized_texts = [text.lower().split() for text in knowledge_base_texts]
        self.bm25 = BM25Okapi(tokenized_texts)
        
        # Pre-compute embeddings
        self.kb_embeddings = embeddings_manager.get_embeddings(knowledge_base_texts)
    
    def search(self, query: str, query_type: str = 'quranic_verse_search'):
        """Hybrid semantic + keyword search"""
        
        config = get_optimal_embedding_for_query(query_type)
        
        # Semantic search
        query_with_instruction = (
            config['instruction'] + " " + query
        )
        query_embedding = self.embeddings_manager.model.encode(
            query_with_instruction,
            normalize_embeddings=self.config['normalize']
        )
        
        semantic_scores = query_embedding @ self.kb_embeddings.T
        semantic_scores = (semantic_scores - semantic_scores.min()) / (
            semantic_scores.max() - semantic_scores.min() + 1e-8
        )
        
        # Keyword search
        bm25_scores = self.bm25.get_scores(query.lower().split())
        bm25_scores = (bm25_scores - bm25_scores.min()) / (
            bm25_scores.max() - bm25_scores.min() + 1e-8
        )
        
        # Combine scores
        semantic_weight = self.config['semantic_weight']  # 0.7
        keyword_weight = self.config['keyword_weight']    # 0.3
        combined_scores = (
            semantic_weight * semantic_scores +
            keyword_weight * bm25_scores
        )
        
        # Get top results
        top_indices = combined_scores.argsort()[-config['top_k']:][::-1]
        
        results = [
            {
                'text': self.kb_texts[i],
                'combined_score': float(combined_scores[i]),
                'semantic_score': float(semantic_scores[i]),
                'keyword_score': float(bm25_scores[i]),
                'rank': idx + 1
            }
            for idx, i in enumerate(top_indices)
        ]
        
        return results
```

---

## Step 4: Re-ranking Implementation

### Re-ranking with Cross-Encoder

```python
from sentence_transformers import CrossEncoder

class ReRanker:
    def __init__(self):
        self.model = CrossEncoder('BAAI/bge-reranker-v2-m3')
    
    def rerank(self, query: str, candidates: list):
        """Re-rank search results"""
        
        # Prepare pairs
        pairs = [[query, result['text']] for result in candidates]
        
        # Get scores
        scores = self.model.predict(pairs)
        
        # Add scores and sort
        for i, result in enumerate(candidates):
            result['rerank_score'] = float(scores[i])
        
        candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        # Update ranks
        for idx, result in enumerate(candidates):
            result['final_rank'] = idx + 1
        
        return candidates
```

### Integration with Hybrid Search

```python
class AdvancedSearcher(HybridSearcher):
    def __init__(self, knowledge_base_texts: list,
                 embeddings_manager: EmbeddingManager):
        super().__init__(knowledge_base_texts, embeddings_manager)
        self.reranker = ReRanker()
    
    def advanced_search(self, query: str, query_type: str = 'quranic_verse_search'):
        """Full pipeline: hybrid search + re-ranking"""
        
        # Hybrid search
        candidates = self.search(query, query_type)
        
        # Re-rank top results
        config = get_optimal_embedding_for_query(query_type)
        if config.get('re_rank', False):
            candidates = self.reranker.rerank(query, candidates)
        
        return candidates
```

---

## Step 5: Multilingual Support

### Multilingual Search

```python
from langdetect import detect, DetectorFactory
from google.cloud import translate_v2

DetectorFactory.seed = 0

class MultilingualSearcher(AdvancedSearcher):
    def __init__(self, knowledge_base_texts: list,
                 embeddings_manager: EmbeddingManager):
        super().__init__(knowledge_base_texts, embeddings_manager)
        self.config = embeddings_manager.config
        self.translate_client = translate_v2.Client()
    
    def detect_language(self, text: str):
        """Detect query language"""
        try:
            return detect(text)
        except:
            return 'en'
    
    def translate_text(self, text: str, source_lang: str, target_lang: str):
        """Translate text"""
        if source_lang == target_lang:
            return text
        
        result = self.translate_client.translate_text(
            text,
            source_language=source_lang,
            target_language=target_lang
        )
        return result['translatedText']
    
    def multilingual_search(self, query: str):
        """Search across all languages"""
        
        # Detect language
        query_lang = self.detect_language(query)
        
        # Search in original language
        results = self.advanced_search(query, 'multilingual_search')
        
        # Translate to other languages and search
        for lang in self.config['languages']:
            if lang == 'en' and query_lang == 'en':
                continue
            if lang == 'ar' and query_lang == 'ar':
                continue
            
            try:
                translated_query = self.translate_text(query, query_lang, lang)
                lang_results = self.advanced_search(translated_query, 'multilingual_search')
                results.extend(lang_results)
            except:
                pass
        
        # Deduplicate and re-rank
        seen = set()
        unique_results = []
        for result in results:
            text_hash = hash(result['text'])
            if text_hash not in seen:
                seen.add(text_hash)
                unique_results.append(result)
        
        return unique_results
```

---

## Step 6: Complete Integration Example

### Full Pipeline

```python
def main():
    # 1. Initialize
    embeddings_manager = EmbeddingManager()
    
    # 2. Load Islamic knowledge base
    knowledge_base = load_islamic_kb()  # Your KB loading function
    
    # 3. Create searcher
    searcher = MultilingualSearcher(knowledge_base, embeddings_manager)
    
    # 4. Process queries
    queries = [
        ("What does Islam teach about compassion?", "islamic_guidance_search"),
        ("Find Quranic verses about mercy", "quranic_verse_search"),
        ("Prophet Muhammad's teachings on kindness", "hadith_knowledge_search"),
    ]
    
    for query, query_type in queries:
        print(f"\n🔍 Query: {query}")
        print(f"📋 Type: {query_type}")
        
        # Search
        results = searcher.advanced_search(query, query_type)
        
        # Display results
        for result in results[:3]:
            print(f"\n  Rank #{result['final_rank']}")
            print(f"  Score: {result['combined_score']:.3f}")
            print(f"  Text: {result['text'][:100]}...")
    
    # 5. Print stats
    stats = embeddings_manager.get_cache_stats()
    print(f"\n📊 Cache Stats: {stats}")
```

---

## Performance Tuning

### Adjust for Your Environment

```python
from backend.config.unified_models import get_embedding_for_environment

# Production
prod_config = get_embedding_for_environment('production')
# High batch size, large cache, GPU

# Development
dev_config = get_embedding_for_environment('development')
# Smaller batch, moderate cache, CPU

# Testing
test_config = get_embedding_for_environment('testing')
# Small batch, no cache, detailed logging
```

---

## Monitoring & Debugging

### Performance Monitoring

```python
import time

class MonitoredSearcher(AdvancedSearcher):
    def __init__(self, knowledge_base_texts: list,
                 embeddings_manager: EmbeddingManager):
        super().__init__(knowledge_base_texts, embeddings_manager)
        self.metrics = {
            'queries': 0,
            'total_time': 0,
            'embedding_time': 0,
            'search_time': 0,
            'rerank_time': 0
        }
    
    def advanced_search_monitored(self, query: str, query_type: str = 'quranic_verse_search'):
        """Search with performance monitoring"""
        
        start = time.time()
        self.metrics['queries'] += 1
        
        # Embedding
        embed_start = time.time()
        query_embedding = self.embeddings_manager.model.encode(query)
        self.metrics['embedding_time'] += time.time() - embed_start
        
        # Search
        search_start = time.time()
        candidates = self.search(query, query_type)
        self.metrics['search_time'] += time.time() - search_start
        
        # Re-rank
        rerank_start = time.time()
        results = self.reranker.rerank(query, candidates)
        self.metrics['rerank_time'] += time.time() - rerank_start
        
        self.metrics['total_time'] += time.time() - start
        
        return results
    
    def print_metrics(self):
        """Print performance metrics"""
        if self.metrics['queries'] == 0:
            return
        
        avg_total = self.metrics['total_time'] / self.metrics['queries']
        avg_embed = self.metrics['embedding_time'] / self.metrics['queries']
        avg_search = self.metrics['search_time'] / self.metrics['queries']
        avg_rerank = self.metrics['rerank_time'] / self.metrics['queries']
        
        print(f"""
        📊 Performance Metrics ({self.metrics['queries']} queries):
        ├─ Total:      {avg_total*1000:.1f}ms
        ├─ Embedding:  {avg_embed*1000:.1f}ms
        ├─ Search:     {avg_search*1000:.1f}ms
        └─ Re-rank:    {avg_rerank*1000:.1f}ms
        """)
```

---

## Checklist

- [ ] Embedding manager initialized
- [ ] Caching enabled
- [ ] BM25 prepared
- [ ] Hybrid search working
- [ ] Re-ranker configured
- [ ] Multilingual support working
- [ ] Performance metrics tracked
- [ ] Monitoring enabled
- [ ] Tests passing
- [ ] Ready for production

Your embedding system is now **fully integrated and production-ready**! 🚀

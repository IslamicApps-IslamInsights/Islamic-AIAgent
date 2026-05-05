#!/usr/bin/env python3
"""
Hybrid Retrieval Validation Test
==================================
Tests the combined BM25 + Vector + MCP retrieval system once vector indexing is complete.

This script:
1. Verifies ChromaDB vector index is populated
2. Tests BM25 keyword search
3. Tests Vector semantic search
4. Tests hybrid combination
5. Validates source diversity
6. Measures performance metrics
"""

import sys
import time
import json
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.utils.advanced_hybrid_rag import (
    AdvancedHybridRAGRetriever,
    check_advanced_rag_system
)
from backend.knowledge.local_knowledge_tools import LocalKnowledgeBase


def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_system_status():
    """Verify all components are ready"""
    print_header("1️⃣  SYSTEM STATUS CHECK")
    
    status = check_advanced_rag_system()
    
    print(f"  BM25 Index Available: {'✅ YES' if status['bm25_available'] else '❌ NO'}")
    print(f"  BM25 Documents: {status.get('bm25_docs', 0):,}")
    print(f"  Vector DB Available: {'✅ YES' if status['vector_available'] else '❌ NO'}")
    print(f"  Vector Docs: {status.get('vector_docs', 0):,}")
    print(f"  MCP Bridge Available: {'✅ YES' if status['mcp_available'] else '❌ NO'}")
    print(f"  Reranker Active: {'✅ YES' if status['reranking_active'] else '❌ NO'}")
    
    return status


def test_bm25_search():
    """Test keyword-based retrieval"""
    print_header("2️⃣  BM25 KEYWORD SEARCH TEST")
    
    kb = LocalKnowledgeBase()
    if not kb.bm25_data:
        print("  ❌ BM25 not available")
        return []
    
    test_queries = [
        "prayer importance Islamic",
        "Zakat obligation alms",
        "Quran recitation Surah Fatiha"
    ]
    
    all_results = []
    for query in test_queries:
        print(f"\n  📌 Query: '{query}'")
        try:
            results = kb.search_bm25(query, k=3)
            print(f"     ✅ Retrieved {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                source = result.get('source', 'Unknown')
                print(f"     • Result {i}: {result.get('content', '')[:80]}...")
                all_results.extend(results)
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    return all_results


def test_vector_search():
    """Test semantic-based retrieval"""
    print_header("3️⃣  VECTOR SEMANTIC SEARCH TEST")
    
    kb = LocalKnowledgeBase()
    if not kb.db:
        print("  ⚠️  Vector DB not available (still ingesting?)")
        return []
    
    test_queries = [
        "importance of daily prayers",
        "almsgiving and charity in Islam",
        "Quranic verses about faith"
    ]
    
    all_results = []
    for query in test_queries:
        print(f"\n  🧠 Query: '{query}'")
        try:
            results = kb.similarity_search(query, k=3)
            print(f"     ✅ Retrieved {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                print(f"     • Result {i}: {result.page_content[:80]}...")
                all_results.append(result)
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    return all_results


def test_hybrid_retrieval():
    """Test combined BM25 + Vector + MCP system"""
    print_header("4️⃣  HYBRID RETRIEVAL SYSTEM TEST")
    
    retriever = AdvancedHybridRAGRetriever()
    
    test_cases = [
        ("What is the importance of Salah?", "prayer"),
        ("Tell me about Zakat obligations", "zakat"),
        ("Explain Al-Fatiha and its significance", "quran"),
        ("What are the Five Pillars?", "pillars"),
        ("Describe Islamic ethics and values", "ethics")
    ]
    
    results_summary = []
    
    for query, topic in test_cases:
        print(f"\n  📝 Query: '{query}' (Topic: {topic})")
        start = time.time()
        
        try:
            result = retriever.retrieve_advanced(query, k=15)
            elapsed = time.time() - start
            
            results = result.get("results", [])
            sources = result.get("sources", {})
            
            print(f"     ✅ Retrieved {len(results)} results in {elapsed:.2f}s")
            print(f"        • BM25: {sources.get('bm25', 0)} results")
            print(f"        • Vector: {sources.get('vector', 0)} results")
            print(f"        • MCP: {sources.get('mcp', 0)} results")
            
            # Show source diversity
            if results:
                sources_used = set()
                for r in results[:5]:
                    source = r.get("source_file", "unknown")
                    sources_used.add(source)
                
                print(f"        • Unique sources in top 5: {len(sources_used)}")
                for source in sorted(sources_used):
                    auth = r.get("authenticity", "")
                    print(f"          - {source}: {auth}")
            
            results_summary.append({
                "query": query,
                "topic": topic,
                "total_results": len(results),
                "bm25": sources.get("bm25", 0),
                "vector": sources.get("vector", 0),
                "mcp": sources.get("mcp", 0),
                "time_sec": elapsed
            })
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    return results_summary


def test_source_diversity():
    """Verify results come from multiple sources"""
    print_header("5️⃣  SOURCE DIVERSITY ANALYSIS")
    
    retriever = AdvancedHybridRAGRetriever()
    
    query = "Islamic knowledge and guidance"
    result = retriever.retrieve_advanced(query, k=15)
    results = result.get("results", [])
    
    source_counts = {}
    authenticity_counts = {}
    retrieval_method_counts = {}
    
    for r in results:
        source = r.get("source_file", "unknown")
        auth = r.get("authenticity", "unknown")
        method = r.get("retrieval_method", "unknown")
        
        source_counts[source] = source_counts.get(source, 0) + 1
        authenticity_counts[auth] = authenticity_counts.get(auth, 0) + 1
        retrieval_method_counts[method] = retrieval_method_counts.get(method, 0) + 1
    
    print(f"\n  📊 Sources Represented ({len(source_counts)} unique):")
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(results)) * 100
        print(f"     • {source}: {count} ({pct:.0f}%)")
    
    print(f"\n  ✅ Authenticity Distribution:")
    for auth, count in sorted(authenticity_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(results)) * 100
        print(f"     • {auth}: {count} ({pct:.0f}%)")
    
    print(f"\n  🔄 Retrieval Methods:")
    for method, count in sorted(retrieval_method_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(results)) * 100
        print(f"     • {method}: {count} ({pct:.0f}%)")
    
    # Analysis
    print(f"\n  📈 Diversity Assessment:")
    if len(source_counts) >= 3:
        print(f"     ✅ Good diversity: {len(source_counts)} unique sources")
    elif len(source_counts) >= 2:
        print(f"     ⚠️  Moderate diversity: {len(source_counts)} unique sources")
    else:
        print(f"     ❌ Low diversity: {len(source_counts)} unique source(s)")


def test_performance():
    """Measure system performance"""
    print_header("6️⃣  PERFORMANCE METRICS")
    
    retriever = AdvancedHybridRAGRetriever()
    
    queries = [
        "prayer in Islam",
        "Islamic ethics",
        "Hadith about charity",
        "Quran verses on mercy",
        "Islamic jurisprudence"
    ]
    
    times = []
    
    for query in queries:
        start = time.time()
        result = retriever.retrieve_advanced(query, k=15)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  ⏱️  Query '{query[:30]}...': {elapsed:.2f}s")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n  📊 Statistics:")
    print(f"     • Average: {avg_time:.2f}s")
    print(f"     • Min: {min_time:.2f}s")
    print(f"     • Max: {max_time:.2f}s")
    
    if avg_time < 2.0:
        print(f"     ✅ Performance target (<2s) met!")
    elif avg_time < 3.0:
        print(f"     ⚠️  Performance acceptable (~2-3s)")
    else:
        print(f"     ❌ Performance needs optimization (>3s)")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  🧪 HYBRID RETRIEVAL VALIDATION TEST SUITE")
    print("="*80)
    
    # System status
    status = test_system_status()
    
    # Component tests
    test_bm25_search()
    test_vector_search()
    
    # Integrated tests
    hybrid_results = test_hybrid_retrieval()
    test_source_diversity()
    test_performance()
    
    # Summary
    print_header("📋 TEST SUMMARY")
    
    print(f"  Components Available:")
    print(f"    • BM25: {'✅' if status['bm25_available'] else '❌'}")
    print(f"    • Vector: {'✅' if status['vector_available'] else '❌'}")
    print(f"    • MCP: {'✅' if status['mcp_available'] else '❌'}")
    
    print(f"\n  Hybrid Queries Tested: {len(hybrid_results)}")
    if hybrid_results:
        avg_results = sum(r['total_results'] for r in hybrid_results) / len(hybrid_results)
        avg_time = sum(r['time_sec'] for r in hybrid_results) / len(hybrid_results)
        print(f"    • Avg Results: {avg_results:.0f} per query")
        print(f"    • Avg Time: {avg_time:.2f}s")
    
    print(f"\n  ✅ Validation Complete!\n")


if __name__ == "__main__":
    main()

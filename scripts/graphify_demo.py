#!/usr/bin/env python3
"""
Graphify Demo Script - Comprehensive Example
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.indexing import ProjectIndexer, Graphify, AICodingAssistant, IndexStorage


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_indexing():
    """Demo 1: Project Indexing"""
    print_section("DEMO 1: Project Indexing")
    
    project_root = os.path.join(os.path.dirname(__file__), '..')
    print(f"📂 Indexing project: {project_root}")
    
    indexer = ProjectIndexer(project_root)
    index_data = indexer.index_project()
    
    print("\n✅ Indexing Complete!")
    
    return indexer, index_data


def demo_graph_building(indexer):
    """Demo 2: Knowledge Graph Building"""
    print_section("DEMO 2: Building Knowledge Graph")
    
    print("🔗 Constructing knowledge graph...\n")
    
    graphify = Graphify(indexer)
    graph = graphify.build_graph()
    
    print("✅ Knowledge Graph Built!")
    
    return graph, graphify


def demo_analysis(graph, indexer):
    """Demo 3: Analysis"""
    print_section("DEMO 3: Code Analysis")
    
    assistant = AICodingAssistant(graph, indexer)
    health = assistant.get_project_health_report()
    
    print(f"📊 Project Health: Complete")
    print(f"   Dead Code Items: {health.get('dead_code_count', 0)}")


def demo_storage(graph, index_data):
    """Demo 4: Storage"""
    print_section("DEMO 4: Storage and Export")
    
    print("💾 Storing analysis results...\n")
    
    storage = IndexStorage()
    storage.save_index(index_data, 'demo_index')
    print("✅ Index saved")
    
    storage.save_knowledge_graph(graph, 'demo_graph')
    print("✅ Graph saved")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("  🔗 GRAPHIFY & PROJECT INDEXING SYSTEM - DEMO")
    print("="*70)
    
    try:
        indexer, index_data = demo_indexing()
        graph, graphify = demo_graph_building(indexer)
        demo_analysis(graph, indexer)
        demo_storage(graph, index_data)
        
        print_section("DEMO COMPLETE! ✅")
        print("\nYou've seen:")
        print("  ✅ Project Indexing")
        print("  ✅ Knowledge Graph Construction")
        print("  ✅ Analysis")
        print("  ✅ Storage")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

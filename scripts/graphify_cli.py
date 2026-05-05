#!/usr/bin/env python3
"""
Graphify CLI

Command-line tool for project indexing and knowledge graph generation.
"""

import argparse
import sys
import json
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def _load_indexing():
    from backend.indexing import (
        ProjectIndexer,
        Graphify,
        AICodingAssistant,
        IndexStorage,
    )

    return ProjectIndexer, Graphify, AICodingAssistant, IndexStorage


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Graphify - Project Analysis and Knowledge "
            "Graph Generation"
        )
    )
    
    subparsers = parser.add_subparsers(
        dest="command", help="Command to execute"
    )
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index a project")
    index_parser.add_argument(
        "--project-path", default=".", help="Path to project root"
    )
    index_parser.add_argument("--name", default="default", help="Index name")
    
    # Build graph command
    graph_parser = subparsers.add_parser(
        "build-graph", help="Build knowledge graph"
    )
    graph_parser.add_argument(
        "--index-name", default="default", help="Index name"
    )
    graph_parser.add_argument(
        "--graph-name", default="default_graph", help="Graph name"
    )
    
    # Health command
    health_parser = subparsers.add_parser(
        "health", help="Get project health report"
    )
    health_parser.add_argument(
        "--graph-name", default="default_graph", help="Graph name"
    )
    
    # List graphs command
    subparsers.add_parser(
        "list-graphs", help="List all knowledge graphs"
    )
    
    # Export command
    export_parser = subparsers.add_parser(
        "export", help="Export knowledge graph"
    )
    export_parser.add_argument(
        "--graph-name", default="default_graph", help="Graph name"
    )
    export_parser.add_argument(
        "--format", choices=["json", "csv"], default="json"
    )
    export_parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "index":
            cmd_index(args)
        elif args.command == "build-graph":
            cmd_build_graph(args)
        elif args.command == "health":
            cmd_health(args)
        elif args.command == "list-graphs":
            cmd_list_graphs()
        elif args.command == "export":
            cmd_export(args)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def cmd_index(args):
    print(f"🔍 Indexing project from {args.project_path}...")
    ProjectIndexer, _, _, IndexStorage = _load_indexing()
    indexer = ProjectIndexer(args.project_path)
    index_data = indexer.index_project()
    
    storage = IndexStorage()
    storage.save_index(index_data, args.name)
    
    print("\n✅ Indexing complete!")


def cmd_build_graph(args):
    print("🔗 Building knowledge graph...")
    ProjectIndexer, Graphify, _, IndexStorage = _load_indexing()
    indexer = ProjectIndexer(".")
    indexer.index_project()
    graphify = Graphify(indexer)
    graph = graphify.build_graph()

    storage = IndexStorage()
    ok = storage.save_knowledge_graph(graph, args.graph_name)
    if not ok:
        raise RuntimeError("Failed to save knowledge graph")

    print("\n✅ Graph built successfully!")
    print(
        f"   Nodes: {len(getattr(graph, 'nodes', {}) or {})}, "
        f"Edges: {len(getattr(graph, 'edges', []) or [])}"
    )


def cmd_health(args):
    print("📊 Analyzing project health...")
    
    ProjectIndexer, _, AICodingAssistant, IndexStorage = _load_indexing()
    storage = IndexStorage()
    graph = storage.load_knowledge_graph(args.graph_name)
    
    if not graph:
        print(f"❌ Graph '{args.graph_name}' not found")
        return
    
    indexer = ProjectIndexer(".")
    assistant = AICodingAssistant(graph, indexer)
    health = assistant.get_project_health_report()
    
    print("\n📈 Project Health Report")
    print(f"   Dead Code: {health.get('dead_code_count', 0)} items")
    print(
        f"   Nodes: {health.get('nodes', 0)}, "
        f"Edges: {health.get('edges', 0)}"
    )


def cmd_list_graphs():
    _, _, _, IndexStorage = _load_indexing()
    storage = IndexStorage()
    graphs = storage.list_graphs()
    print("\n📚 Knowledge Graphs stored")
    if not graphs:
        print("   (none)")
        return
    for g in graphs:
        print(f"   - {g}")


def cmd_export(args):
    _, _, _, IndexStorage = _load_indexing()
    storage = IndexStorage()
    graph = storage.load_knowledge_graph(args.graph_name)
    
    if not graph:
        print(f"❌ Graph '{args.graph_name}' not found")
        return
    
    output_path = args.output or f"graph_{args.graph_name}.{args.format}"
    if args.format == "json":
        with open(output_path, "w") as f:
            json.dump(graph.to_dict(), f, indent=2)
    else:
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["source_id", "target_id", "relationship", "weight"]
            writer.writerow(header)
            for e in getattr(graph, "edges", []) or []:
                writer.writerow(
                    [
                        getattr(e, "source_id", ""),
                        getattr(e, "target_id", ""),
                        getattr(e, "relationship", ""),
                        getattr(e, "weight", 1.0),
                    ]
                )

    print(f"✅ Graph exported to: {output_path}")


if __name__ == '__main__':
    main()

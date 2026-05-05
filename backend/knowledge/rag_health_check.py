#!/usr/bin/env python3
"""
RAG System Health Check & Verification
======================================
Verifies that all files have been properly ingested into the RAG system.
Checks ChromaDB and BM25 indices, provides statistics and health status.
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAGHealthCheck")


class RAGHealthChecker:
    """Verify RAG system health and ingestion status"""

    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.data_dir = self.current_dir / "data"
        self.chroma_path = self.current_dir / "chroma_db_full"
        self.bm25_path = self.current_dir / "bm25_full_index.pkl"
        self.stats_file = self.current_dir / "ingestion_stats.json"

    def check_data_folder(self) -> Dict:
        """Check if all data files are present"""
        stats = {
            "exists": self.data_dir.exists(),
            "total_files": 0,
            "json_files": 0,
            "txt_files": 0,
            "total_size_mb": 0,
            "files": {}
        }

        if not self.data_dir.exists():
            logger.warning(f"❌ Data folder not found: {self.data_dir}")
            return stats

        # Count files
        all_files = list(self.data_dir.glob("*"))
        stats["total_files"] = len(all_files)

        for file_path in all_files:
            if file_path.is_file():
                size_mb = file_path.stat().st_size / 1024 / 1024
                stats["total_size_mb"] += size_mb

                file_info = {
                    "size_mb": round(size_mb, 2),
                    "exists": True
                }

                if file_path.suffix == ".json":
                    stats["json_files"] += 1
                    file_info["type"] = "json"
                elif file_path.suffix == ".txt":
                    stats["txt_files"] += 1
                    file_info["type"] = "txt"

                stats["files"][file_path.name] = file_info

        stats["total_size_mb"] = round(stats["total_size_mb"], 1)
        return stats

    def check_chromadb(self) -> Dict:
        """Check ChromaDB index status"""
        stats = {
            "exists": self.chroma_path.exists(),
            "initialized": False,
            "size_mb": 0,
            "document_count": 0,
            "error": None
        }

        if not self.chroma_path.exists():
            return stats

        try:
            # Calculate size
            total_size = sum(
                f.stat().st_size for f in self.chroma_path.rglob("*") if f.is_file()
            )
            stats["size_mb"] = round(total_size / 1024 / 1024, 1)

            # Try to load ChromaDB and check collection
            import chromadb
            client = chromadb.PersistentClient(path=str(self.chroma_path))
            
            try:
                collection = client.get_collection("islamic_knowledge")
                stats["initialized"] = True
                stats["document_count"] = collection.count()
            except Exception as e:
                logger.warning(f"⚠️  ChromaDB collection not accessible: {e}")

        except Exception as e:
            stats["error"] = str(e)
            logger.warning(f"⚠️  ChromaDB check failed: {e}")

        return stats

    def check_bm25(self) -> Dict:
        """Check BM25 index status"""
        stats = {
            "exists": self.bm25_path.exists(),
            "initialized": False,
            "size_mb": 0,
            "document_count": 0,
            "error": None
        }

        if not self.bm25_path.exists():
            return stats

        try:
            # Get file size
            size_bytes = self.bm25_path.stat().st_size
            stats["size_mb"] = round(size_bytes / 1024 / 1024, 1)

            # Load and check index
            with open(self.bm25_path, "rb") as f:
                index_data = pickle.load(f)

            if isinstance(index_data, dict):
                stats["initialized"] = True
                stats["document_count"] = index_data.get("total_chunks", 0)
                stats["metadata"] = {
                    "chunk_size": index_data.get("model_info", {}).get("chunk_size"),
                    "chunk_overlap": index_data.get("model_info", {}).get("chunk_overlap"),
                    "total_documents": index_data.get("model_info", {}).get("total_documents")
                }

        except Exception as e:
            stats["error"] = str(e)
            logger.warning(f"⚠️  BM25 check failed: {e}")

        return stats

    def check_ingestion_stats(self) -> Dict:
        """Check ingestion statistics file"""
        stats = {
            "exists": self.stats_file.exists(),
            "data": None,
            "error": None
        }

        if not self.stats_file.exists():
            return stats

        try:
            with open(self.stats_file, "r") as f:
                stats["data"] = json.load(f)
        except Exception as e:
            stats["error"] = str(e)
            logger.warning(f"⚠️  Stats file read failed: {e}")

        return stats

    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        print("\n" + "=" * 90)
        print("🏥 RAG SYSTEM HEALTH CHECK & VERIFICATION")
        print("=" * 90 + "\n")

        # Check each component
        data_stats = self.check_data_folder()
        chromadb_stats = self.check_chromadb()
        bm25_stats = self.check_bm25()
        ingestion_stats = self.check_ingestion_stats()

        # Generate report
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "data_folder": data_stats,
            "chromadb": chromadb_stats,
            "bm25": bm25_stats,
            "ingestion_stats": ingestion_stats,
            "overall_health": "unknown"
        }

        # Determine overall health
        if (data_stats["total_files"] > 0 and 
            chromadb_stats["initialized"] and 
            bm25_stats["initialized"]):
            report["overall_health"] = "✅ HEALTHY"
            status_color = "\033[92m"  # Green
        elif (data_stats["total_files"] > 0 and 
              (chromadb_stats["exists"] or bm25_stats["exists"])):
            report["overall_health"] = "⚠️  PARTIAL"
            status_color = "\033[93m"  # Yellow
        else:
            report["overall_health"] = "❌ DEGRADED"
            status_color = "\033[91m"  # Red

        reset_color = "\033[0m"

        # Print data folder status
        print("📁 DATA FOLDER")
        print("-" * 90)
        print(f"  Path: {self.data_dir}")
        print(f"  Exists: {'✅ Yes' if data_stats['exists'] else '❌ No'}")
        print(f"  Total Files: {data_stats['total_files']}")
        print(f"  JSON Files: {data_stats['json_files']}")
        print(f"  TXT Files: {data_stats['txt_files']}")
        print(f"  Total Size: {data_stats['total_size_mb']} MB")

        if data_stats["files"]:
            print(f"\n  Sample Files (first 10):")
            for name, info in list(data_stats["files"].items())[:10]:
                print(f"    • {name}: {info['size_mb']} MB")
            if len(data_stats["files"]) > 10:
                print(f"    ... and {len(data_stats['files']) - 10} more files")

        # Print ChromaDB status
        print("\n🗄️  CHROMADB (Vector Search)")
        print("-" * 90)
        print(f"  Path: {self.chroma_path}")
        print(f"  Exists: {'✅ Yes' if chromadb_stats['exists'] else '❌ No'}")
        print(f"  Initialized: {'✅ Yes' if chromadb_stats['initialized'] else '❌ No'}")
        print(f"  Size: {chromadb_stats['size_mb']} MB")
        print(f"  Documents Indexed: {chromadb_stats['document_count']:,}")
        if chromadb_stats["error"]:
            print(f"  Error: {chromadb_stats['error']}")

        # Print BM25 status
        print("\n🔍 BM25 (Keyword Search)")
        print("-" * 90)
        print(f"  Path: {self.bm25_path}")
        print(f"  Exists: {'✅ Yes' if bm25_stats['exists'] else '❌ No'}")
        print(f"  Initialized: {'✅ Yes' if bm25_stats['initialized'] else '❌ No'}")
        print(f"  Size: {bm25_stats['size_mb']} MB")
        print(f"  Chunks Indexed: {bm25_stats['document_count']:,}")
        if bm25_stats.get("metadata"):
            meta = bm25_stats["metadata"]
            print(f"  Chunk Config: size={meta.get('chunk_size')}, overlap={meta.get('chunk_overlap')}")
            print(f"  Total Documents: {meta.get('total_documents'):,}")
        if bm25_stats["error"]:
            print(f"  Error: {bm25_stats['error']}")

        # Print ingestion stats
        print("\n📊 INGESTION STATISTICS")
        print("-" * 90)
        if ingestion_stats["exists"]:
            data = ingestion_stats["data"]
            print(f"  Total Files Processed: {data.get('total_files', 'N/A')}")
            print(f"  Total Documents: {data.get('total_documents', 'N/A'):,}")
            print(f"  Total Chunks: {data.get('total_chunks', 'N/A'):,}")
            print(f"  Total Data Size: {data.get('total_data_size_mb', 'N/A')} MB")
            print(f"  Processing Time: {data.get('processing_time_seconds', 'N/A')} seconds")
            print(f"  Ingestion Date: {data.get('ingestion_date', 'N/A')}")
        else:
            print("  No ingestion stats file found")

        # Print overall status
        print("\n" + "=" * 90)
        print(f"{status_color}OVERALL SYSTEM STATUS: {report['overall_health']}{reset_color}")
        print("=" * 90 + "\n")

        # Print recommendations
        print("💡 RECOMMENDATIONS")
        print("-" * 90)

        if not chromadb_stats["initialized"] or not bm25_stats["initialized"]:
            print("  ⚠️  RAG indices not fully initialized.")
            print("  👉 Run: bash ingest_all_data.sh")
            print("     Or: python backend/knowledge/full_data_ingestion.py")
        elif chromadb_stats["document_count"] == 0 and bm25_stats["document_count"] == 0:
            print("  ⚠️  RAG indices exist but contain no documents.")
            print("  👉 Run: bash ingest_all_data.sh")
        elif chromadb_stats["document_count"] < 10000:
            print(f"  ⚠️  RAG indices seem incomplete ({chromadb_stats['document_count']} docs).")
            print("  👉 For best performance, run: bash ingest_all_data.sh")
        else:
            print("  ✅ RAG system is healthy and ready!")
            print(f"  ✅ {chromadb_stats['document_count']:,} documents indexed")

        print()
        return report


def run_health_check():
    """Run the health check"""
    checker = RAGHealthChecker()
    return checker.generate_health_report()


if __name__ == "__main__":
    report = run_health_check()
    
    # Save report
    import json
    with open("rag_health_report.json", "w") as f:
        # Convert Path objects to strings
        def convert_paths(obj):
            if isinstance(obj, Path):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(v) for v in obj]
            return obj
        
        json.dump(convert_paths(report), f, indent=2)
    
    print("📄 Report saved to: rag_health_report.json\n")

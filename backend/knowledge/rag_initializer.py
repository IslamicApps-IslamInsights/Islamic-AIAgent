#!/usr/bin/env python3
"""
Automatic RAG Ingestion Initialization
=======================================
Automatically ingests ALL files from knowledge/data folder on startup
Ensures the RAG system is fully populated before API requests
"""

import os
import sys
import time
import threading
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("RAGInitializer")


class RAGIngestionInitializer:
    """Manages automatic RAG ingestion on startup"""

    def __init__(self):
        self.ingestion_complete = False
        self.ingestion_thread: Optional[threading.Thread] = None
        self.current_dir = Path(__file__).parent

    def check_ingestion_needed(self) -> bool:
        """Check if ingestion is needed"""
        chromadb_path = self.current_dir / "chroma_db_full"
        bm25_path = self.current_dir / "bm25_full_index.pkl"

        # Need ingestion if either database doesn't exist or is empty
        if not chromadb_path.exists() or not bm25_path.exists():
            logger.info("📊 Ingestion needed: Databases not found")
            return True

        # Check if databases have content
        try:
            if chromadb_path.exists():
                db_files = list(chromadb_path.glob("**/*"))
                if len(db_files) < 5:  # Minimal DB has at least some files
                    logger.info("📊 Ingestion needed: ChromaDB appears empty")
                    return True

            if bm25_path.exists() and bm25_path.stat().st_size < 1000:
                logger.info("📊 Ingestion needed: BM25 index appears empty")
                return True
        except Exception as e:
            logger.warning(f"⚠️  Could not check database status: {e}")
            return True

        return False

    def run_ingestion_async(self) -> None:
        """Run ingestion in background thread"""
        logger.info("🚀 Starting RAG ingestion in background...")

        def ingest():
            try:
                from backend.knowledge.full_data_ingestion import run_full_ingestion
                
                logger.info("📥 Running full data ingestion...")
                success = run_full_ingestion()
                
                if success:
                    self.ingestion_complete = True
                    logger.info("✅ RAG ingestion completed successfully!")
                else:
                    logger.error("❌ RAG ingestion failed")
                    self.ingestion_complete = False

            except ImportError as e:
                logger.error(f"❌ Failed to import ingestion module: {e}")
                self.ingestion_complete = False
            except Exception as e:
                logger.error(f"❌ Ingestion error: {e}")
                import traceback
                traceback.print_exc()
                self.ingestion_complete = False

        # Start ingestion in background thread
        self.ingestion_thread = threading.Thread(target=ingest, daemon=True)
        self.ingestion_thread.start()

        logger.info("✅ Ingestion started in background thread")

    def wait_for_ingestion(self, timeout: int = 600) -> bool:
        """Wait for ingestion to complete (with timeout)"""
        if self.ingestion_thread is None:
            return True

        logger.info(f"⏳ Waiting for ingestion to complete (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ingestion_complete:
                logger.info("✅ Ingestion complete!")
                return True

            if not self.ingestion_thread.is_alive():
                if self.ingestion_complete:
                    logger.info("✅ Ingestion complete!")
                    return True
                else:
                    logger.warning("⚠️  Ingestion thread stopped but ingestion not marked complete")
                    return False

            time.sleep(2)  # Check every 2 seconds

        logger.warning(f"⚠️  Ingestion timeout after {timeout}s. RAG may be incomplete.")
        return False

    def initialize(self, wait: bool = False) -> bool:
        """Initialize RAG ingestion"""
        if not self.check_ingestion_needed():
            logger.info("✅ RAG already initialized and indexed")
            return True

        self.run_ingestion_async()

        if wait:
            return self.wait_for_ingestion()

        return True


# Global initializer instance
_initializer: Optional[RAGIngestionInitializer] = None


def get_rag_initializer() -> RAGIngestionInitializer:
    """Get or create RAG initializer instance"""
    global _initializer
    if _initializer is None:
        _initializer = RAGIngestionInitializer()
    return _initializer


def initialize_rag(wait: bool = False) -> bool:
    """Initialize RAG ingestion"""
    initializer = get_rag_initializer()
    return initializer.initialize(wait=wait)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run ingestion
    logger.info("🚀 Manual RAG Ingestion Started")
    initializer = get_rag_initializer()
    success = initializer.initialize(wait=True)
    
    if success:
        logger.info("✅ RAG Ingestion Successful")
        sys.exit(0)
    else:
        logger.error("❌ RAG Ingestion Failed")
        sys.exit(1)

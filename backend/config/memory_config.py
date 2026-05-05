"""
Memory Management Configuration for Islamic AI Agent
===================================================

Controls model loading strategy and memory optimization settings.
"""

import os
from typing import Dict, Any

# --- LAZY LOADING CONFIGURATION ---
# If True, models load on first use instead of at startup
LAZY_LOAD_ENABLED = True

# If True, embeddings model is loaded on first search request
LAZY_LOAD_EMBEDDINGS = True

# If True, re-ranker model is loaded on first ranking request
LAZY_LOAD_RERANKER = True

# --- BATCH PROCESSING CONFIGURATION ---
# Batch size for RAG ingestion (lower = less memory)
INGEST_BATCH_SIZE = 100  # Default: 500, for low-memory: 50-100

# Chunk size for document splitting
CHUNK_SIZE = 1000  # Default: 1000, for low-memory: 500-800

# Chunk overlap
CHUNK_OVERLAP = 200

# --- MODEL CONFIGURATION ---
# Embedding model to use (for local knowledge base training)
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"  # ~700MB

# Reranker model to use (optional, can be disabled)
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"  # ~300MB

# LLM model - DEPRECATED in Quran-first architecture
# Now using Quran Foundation MCP for all intelligence instead of external LLM
LLM_MODEL = "quran_foundation_mcp"  # No external LLM needed

# --- MEMORY OPTIMIZATION ---
# Enable explicit garbage collection after operations
ENABLE_GC = True

# Collect garbage after every N queries
GC_INTERVAL = 10

# Maximum RAM usage before warnings (in GB)
MAX_RAM_WARNING = 2.0

# Maximum RAM usage before errors (in GB)
MAX_RAM_ERROR = 3.5

# --- COMPONENT CONFIGURATION ---
COMPONENTS_CONFIG: Dict[str, Any] = {
    'quran_foundation_mcp': {
        'enabled': True,
        'lazy_load': False,  # Load immediately - critical for all queries
        'provider': 'quran_foundation',
        'purpose': 'Primary intelligence source - Quranic knowledge'
    },
    'embeddings': {
        'enabled': True,
        'lazy_load': LAZY_LOAD_EMBEDDINGS,
        'device': 'cpu',  # or 'cuda' for GPU
        'normalize': True,
        'purpose': 'Local knowledge base training and semantic search'
    },
    'reranker': {
        'enabled': True,
        'lazy_load': LAZY_LOAD_RERANKER,
        'device': 'cpu',
        'skip_on_vercel': True,
        'purpose': 'Optional result ranking'
    },
    'chromadb': {
        'enabled': True,
        'lazy_load': True,
        'persist': True,
        'purpose': 'Local knowledge base storage'
    },
    'bm25': {
        'enabled': True,
        'lazy_load': False,  # BM25 is small, load immediately
        'purpose': 'Keyword search for local knowledge base'
    },
    'ingestion': {
        'enabled': True,
        'lazy_load': True,  # Don't run on startup
        'run_on_startup': False,  # CRITICAL: Don't run full ingestion on startup
        'batch_size': INGEST_BATCH_SIZE,
        'purpose': 'Training embeddings on local Islamic knowledge base'
    }
}

# --- STARTUP SEQUENCE ORDER ---
# Quran Foundation MCP first (primary intelligence), then agents, then optional components
STARTUP_SEQUENCE = [
    'quran_foundation_mcp',     # CRITICAL - Primary intelligence source
    'memory_optimized_loader',  # Fast, lazy loads embeddings for local KB
    'single_agent',             # Critical for responses (uses Quran MCP)
    'multi_agent_system',       # Optional, can fail
]

# --- HEALTH CHECK CONFIGURATION ---
HEALTH_CHECK_CONFIG = {
    'check_memory': True,
    'check_models': False,  # Don't check model loading status
    'check_rag': True,
    'warn_threshold': 2.0,  # GB
    'error_threshold': 3.5,  # GB
}

# --- ENVIRONMENT-SPECIFIC SETTINGS ---

# Detect environment
IS_VERCEL = os.environ.get("VERCEL") == "1" or os.environ.get("VERCEL_URL") is not None
IS_PRODUCTION = os.environ.get("ENV") == "production"
IS_DEVELOPMENT = os.environ.get("ENV") == "development" or not IS_PRODUCTION

# Vercel-specific optimizations
if IS_VERCEL:
    LAZY_LOAD_ENABLED = True
    LAZY_LOAD_EMBEDDINGS = True
    LAZY_LOAD_RERANKER = True
    COMPONENTS_CONFIG['reranker']['enabled'] = False  # Skip on Vercel
    COMPONENTS_CONFIG['ingestion']['run_on_startup'] = False
    INGEST_BATCH_SIZE = 50  # Lower for cloud
    MAX_RAM_WARNING = 1.0
    MAX_RAM_ERROR = 1.5

# Development-specific optimizations
if IS_DEVELOPMENT:
    LAZY_LOAD_ENABLED = True
    COMPONENTS_CONFIG['ingestion']['run_on_startup'] = False


def get_memory_config() -> Dict[str, Any]:
    """Get complete memory configuration"""
    return {
        'lazy_loading': LAZY_LOAD_ENABLED,
        'batch_size': INGEST_BATCH_SIZE,
        'chunk_size': CHUNK_SIZE,
        'chunk_overlap': CHUNK_OVERLAP,
        'max_ram_warning': MAX_RAM_WARNING,
        'max_ram_error': MAX_RAM_ERROR,
        'components': COMPONENTS_CONFIG,
        'startup_sequence': STARTUP_SEQUENCE,
        'environment': {
            'is_vercel': IS_VERCEL,
            'is_production': IS_PRODUCTION,
            'is_development': IS_DEVELOPMENT,
        }
    }


def should_run_ingestion_on_startup() -> bool:
    """Check if ingestion should run on startup"""
    return COMPONENTS_CONFIG['ingestion'].get('run_on_startup', False)


def get_batch_size() -> int:
    """Get batch size for ingestion"""
    return COMPONENTS_CONFIG['ingestion'].get('batch_size', INGEST_BATCH_SIZE)

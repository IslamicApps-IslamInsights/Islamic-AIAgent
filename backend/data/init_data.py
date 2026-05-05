#!/usr/bin/env python3
"""
Initialize backend data directories and files
"""

import os
import json
from pathlib import Path

def init_data_dir():
    """Create necessary data files"""
    data_dir = Path(__file__).parent
    
    # Create topic_analytics.json if missing
    analytics_file = data_dir / "topic_analytics.json"
    if not analytics_file.exists():
        with open(analytics_file, 'w') as f:
            json.dump({
                "total_queries": 0,
                "popular_topics": {},
                "initialized_at": str(Path.cwd())
            }, f, indent=2)
        print(f"✅ Created {analytics_file}")
    
    # Create index_metadata.json for Graphify
    metadata_file = data_dir / "index_metadata.json"
    if not metadata_file.exists():
        with open(metadata_file, 'w') as f:
            json.dump({
                "project": "Islamic AI Agent",
                "last_indexed": None,
                "indexes": []
            }, f, indent=2)
        print(f"✅ Created {metadata_file}")
    
    print(f"✅ Data directory initialized: {data_dir}")

if __name__ == "__main__":
    init_data_dir()

"""
Index Storage - Persist and retrieve project indexing data
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from .graphify import KnowledgeGraph


class IndexStorage:
    def __init__(self, storage_path: str = "data/indexing"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def save_index(
        self, index_data: Dict[str, Any], name: str = "default"
    ) -> bool:
        try:
            json_path = self.storage_path / f"index_{name}.json"
            with open(json_path, "w") as f:
                json.dump(index_data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
    def load_index(self, name: str = "default") -> Optional[Dict[str, Any]]:
        try:
            json_path = self.storage_path / f"index_{name}.json"
            if json_path.exists():
                with open(json_path, "r") as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def list_graphs(self):
        """List all saved knowledge graphs"""
        graphs: List[str] = []
        for path in sorted(self.storage_path.glob("graph_*.json")):
            name = path.stem[len("graph_"):]
            if name:
                graphs.append(name)
        return graphs
    
    def save_knowledge_graph(self, graph: KnowledgeGraph, name: str) -> bool:
        """Save knowledge graph"""
        json_path = self.storage_path / f"graph_{name}.json"
        try:
            with open(json_path, "w") as f:
                json.dump(graph.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def load_knowledge_graph(self, name: str) -> Optional[KnowledgeGraph]:
        """Load knowledge graph"""
        try:
            json_path = self.storage_path / f"graph_{name}.json"
            if json_path.exists():
                with open(json_path, "r") as f:
                    data = json.load(f)
                return KnowledgeGraph.from_dict(data)
        except Exception:
            return None
        return None

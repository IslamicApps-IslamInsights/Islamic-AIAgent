"""
AI Coding Assistant Integration
"""

from typing import Dict, List, Any, Tuple
from pathlib import Path


class CodeContext:
    def __init__(self, knowledge_graph, project_indexer):
        self.graph = knowledge_graph
        self.indexer = project_indexer


class CodeNavigator:
    def __init__(self, knowledge_graph, project_indexer):
        self.graph = knowledge_graph
        self.indexer = project_indexer


class CodeRecommender:
    def __init__(self, knowledge_graph, project_indexer):
        self.graph = knowledge_graph
        self.indexer = project_indexer


class AICodingAssistant:
    def __init__(self, knowledge_graph, project_indexer):
        self.graph = knowledge_graph
        self.indexer = project_indexer
        self.context = CodeContext(knowledge_graph, project_indexer)
        self.navigator = CodeNavigator(knowledge_graph, project_indexer)
        self.recommender = CodeRecommender(knowledge_graph, project_indexer)
        
    def get_project_health_report(self) -> Dict[str, Any]:
        self._ensure_indexed()

        function_node_ids = [
            node_id
            for node_id, node in getattr(self.graph, "nodes", {}).items()
            if self._node_type(node) == "function"
        ]

        called_targets = {
            e.target_id
            for e in getattr(self.graph, "edges", []) or []
            if getattr(e, "relationship", None) == "calls"
        }

        dead_function_ids = sorted(
            set(function_node_ids) - set(called_targets)
        )
        dead_samples = [
            self.graph.nodes[fn_id].name
            for fn_id in dead_function_ids[:25]
            if fn_id in self.graph.nodes
        ]

        top_functions = self._top_complex_functions(limit=10)
        top_modules = self._top_complex_modules(limit=10)

        return {
            "nodes": len(getattr(self.graph, "nodes", {}) or {}),
            "edges": len(getattr(self.graph, "edges", []) or []),
            "dead_code_count": len(dead_function_ids),
            "dead_code_samples": dead_samples,
            "complexity_hotspots": {
                "functions": top_functions,
                "modules": top_modules,
            },
        }
        
    def search_code(self, query: str) -> List[Dict[str, Any]]:
        self._ensure_indexed()
        q = (query or "").strip().lower()
        if not q:
            return []

        results: List[Dict[str, Any]] = []
        for module_path, module in self.indexer.modules.items():
            if q in module_path.lower():
                results.append(
                    {
                        "type": "module",
                        "path": module_path,
                        "name": module_path,
                    }
                )

            for fn in getattr(module, "functions", []) or []:
                if q in fn.name.lower():
                    results.append(
                        {
                            "type": "function",
                            "path": module_path,
                            "name": fn.name,
                            "line_number": fn.line_number,
                        }
                    )

            for cls in getattr(module, "classes", []) or []:
                if q in cls.name.lower():
                    results.append(
                        {
                            "type": "class",
                            "path": module_path,
                            "name": cls.name,
                            "line_number": cls.line_number,
                        }
                    )
                for method in getattr(cls, "methods", []) or []:
                    full_name = f"{cls.name}.{method.name}"
                    if q in full_name.lower():
                        results.append(
                            {
                                "type": "method",
                                "path": module_path,
                                "name": full_name,
                                "line_number": method.line_number,
                            }
                        )

        return results[:50]
        
    def generate_architecture_overview(self) -> str:
        self._ensure_indexed()
        directories: Dict[str, int] = {}
        for module_path in self.indexer.modules.keys():
            parts = Path(module_path).parts
            if parts:
                directories[parts[0]] = directories.get(parts[0], 0) + 1

        lines: List[str] = []
        lines.append("Project Architecture")
        lines.append("")
        lines.append("Top-Level Areas")
        for name, count in sorted(
            directories.items(), key=lambda x: (-x[1], x[0])
        ):
            lines.append(f"- {name}: {count} python modules")

        entrypoints = [
            "backend/api/web_api.py",
            "backend/api/run_fast.py",
            "api/index.py",
            "frontend/src/main.jsx",
        ]
        existing = [
            p for p in entrypoints if (self.indexer.root_path / p).exists()
        ]
        if existing:
            lines.append("")
            lines.append("Entry Points")
            for p in existing:
                lines.append(f"- {p}")

        return "\n".join(lines)

    def _ensure_indexed(self) -> None:
        if not getattr(self.indexer, "modules", None):
            self.indexer.index_project()

    def _node_type(self, node: Any) -> str:
        t = getattr(node, "type", None)
        if hasattr(t, "value"):
            return str(t.value)
        return str(t or "")

    def _top_complex_functions(self, limit: int = 10) -> List[Dict[str, Any]]:
        scored: List[Tuple[int, str, str]] = []
        for module_path, module in self.indexer.modules.items():
            for fn in getattr(module, "functions", []) or []:
                scored.append((fn.complexity, module_path, fn.name))
            for cls in getattr(module, "classes", []) or []:
                for method in getattr(cls, "methods", []) or []:
                    name = f"{cls.name}.{method.name}"
                    scored.append((method.complexity, module_path, name))
        scored.sort(key=lambda x: (-x[0], x[1], x[2]))
        out: List[Dict[str, Any]] = []
        for complexity, module_path, name in scored[:limit]:
            out.append(
                {"name": name, "path": module_path, "complexity": complexity}
            )
        return out

    def _top_complex_modules(self, limit: int = 10) -> List[Dict[str, Any]]:
        scored = [
            (m.complexity, module_path)
            for module_path, m in self.indexer.modules.items()
        ]
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [
            {"path": module_path, "complexity": complexity}
            for complexity, module_path in scored[:limit]
        ]

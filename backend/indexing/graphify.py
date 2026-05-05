"""
Graphify - Knowledge Graph Generation and Visualization
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


class EntityType(Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"


@dataclass
class EntityNode:
    id: str
    name: str
    type: EntityType
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelationshipEdge:
    source_id: str
    target_id: str
    relationship: str = "related"
    weight: float = 1.0


class KnowledgeGraph:
    def __init__(self, name: str = "Project Knowledge Graph"):
        self.name = name
        self.nodes: Dict[str, EntityNode] = {}
        self.edges: List[RelationshipEdge] = []
        
    def add_node(self, entity: EntityNode):
        self.nodes[entity.id] = entity
        
    def add_edge(self, relationship: RelationshipEdge):
        self.edges.append(relationship)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.type.value,
                    "properties": n.properties,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "relationship": e.relationship,
                    "weight": e.weight,
                }
                for e in self.edges
            ],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "KnowledgeGraph":
        graph = KnowledgeGraph(
            name=data.get("name") or "Project Knowledge Graph"
        )
        for node in data.get("nodes", []) or []:
            try:
                entity_type = EntityType(node.get("type"))
            except Exception:
                entity_type = EntityType.FUNCTION
            graph.add_node(
                EntityNode(
                    id=node.get("id") or "",
                    name=node.get("name") or "",
                    type=entity_type,
                    properties=node.get("properties") or {},
                )
            )
        for edge in data.get("edges", []) or []:
            graph.add_edge(
                RelationshipEdge(
                    source_id=edge.get("source_id") or "",
                    target_id=edge.get("target_id") or "",
                    relationship=edge.get("relationship") or "related",
                    weight=float(edge.get("weight") or 1.0),
                )
            )
        return graph


class Graphify:
    def __init__(self, project_indexer):
        self.indexer = project_indexer
        self.graph = KnowledgeGraph()
        
    def build_graph(self) -> KnowledgeGraph:
        print("🔗 Building knowledge graph...")
        if not getattr(self.indexer, "modules", None):
            self.indexer.index_project()

        self.graph = KnowledgeGraph(name="Project Knowledge Graph")
        module_node_ids: Dict[str, str] = {}
        class_node_ids: Dict[Tuple[str, str], str] = {}
        function_node_ids: Dict[Tuple[str, str], str] = {}
        method_node_ids: Dict[Tuple[str, str, str], str] = {}

        for module_path, module in self.indexer.modules.items():
            module_id = f"module:{module_path}"
            module_node_ids[module_path] = module_id
            self.graph.add_node(
                EntityNode(
                    id=module_id,
                    name=module_path,
                    type=EntityType.MODULE,
                    properties={
                        "lines_of_code": getattr(module, "lines_of_code", 0),
                        "complexity": getattr(module, "complexity", 0),
                    },
                )
            )

        for module_path, module in self.indexer.modules.items():
            module_id = module_node_ids[module_path]

            for cls in getattr(module, "classes", []) or []:
                class_id = f"class:{module_path}:{cls.name}"
                class_node_ids[(module_path, cls.name)] = class_id
                self.graph.add_node(
                    EntityNode(
                        id=class_id,
                        name=cls.name,
                        type=EntityType.CLASS,
                        properties={
                            "module": module_path,
                            "line_number": cls.line_number,
                            "complexity": cls.complexity,
                            "parent_classes": cls.parent_classes,
                        },
                    )
                )
                self.graph.add_edge(
                    RelationshipEdge(
                        source_id=module_id,
                        target_id=class_id,
                        relationship="contains",
                    )
                )

                for method in getattr(cls, "methods", []) or []:
                    method_id = (
                        f"function:{module_path}:{cls.name}.{method.name}"
                    )
                    method_node_ids[
                        (module_path, cls.name, method.name)
                    ] = method_id
                    self.graph.add_node(
                        EntityNode(
                            id=method_id,
                            name=f"{cls.name}.{method.name}",
                            type=EntityType.FUNCTION,
                            properties={
                                "module": module_path,
                                "class": cls.name,
                                "line_number": method.line_number,
                                "complexity": method.complexity,
                                "parameters": method.parameters,
                            },
                        )
                    )
                    self.graph.add_edge(
                        RelationshipEdge(
                            source_id=class_id,
                            target_id=method_id,
                            relationship="contains",
                        )
                    )

            for fn in getattr(module, "functions", []) or []:
                fn_id = f"function:{module_path}:{fn.name}"
                function_node_ids[(module_path, fn.name)] = fn_id
                self.graph.add_node(
                    EntityNode(
                        id=fn_id,
                        name=fn.name,
                        type=EntityType.FUNCTION,
                        properties={
                            "module": module_path,
                            "line_number": fn.line_number,
                            "complexity": fn.complexity,
                            "parameters": fn.parameters,
                        },
                    )
                )
                self.graph.add_edge(
                    RelationshipEdge(
                        source_id=module_id,
                        target_id=fn_id,
                        relationship="contains",
                    )
                )

        module_name_to_path = (
            getattr(self.indexer, "_module_name_to_path", {}) or {}
        )
        for module_path, module in self.indexer.modules.items():
            module_id = module_node_ids[module_path]
            for dep in getattr(module, "dependencies", set()) or set():
                if dep in module_name_to_path:
                    target_module_path = module_name_to_path[dep]
                    target_id = module_node_ids.get(target_module_path)
                    if target_id:
                        self.graph.add_edge(
                            RelationshipEdge(
                                source_id=module_id,
                                target_id=target_id,
                                relationship="imports",
                            )
                        )

        class_name_to_ids: Dict[str, List[str]] = {}
        for (_, class_name), class_id in class_node_ids.items():
            class_name_to_ids.setdefault(class_name, []).append(class_id)

        for (module_path, class_name), class_id in class_node_ids.items():
            module = self.indexer.modules.get(module_path)
            if not module:
                continue
            cls_obj = next(
                (
                    c
                    for c in getattr(module, "classes", []) or []
                    if c.name == class_name
                ),
                None,
            )
            if not cls_obj:
                continue
            for parent in getattr(cls_obj, "parent_classes", []) or []:
                parent_simple = parent.split(".")[-1]
                candidates = class_name_to_ids.get(parent_simple) or []
                if len(candidates) == 1:
                    self.graph.add_edge(
                        RelationshipEdge(
                            source_id=class_id,
                            target_id=candidates[0],
                            relationship="inherits",
                        )
                    )

        simple_name_index: Dict[str, List[str]] = {}
        class_method_index: Dict[str, List[str]] = {}

        for (_, fn_name), fn_id in function_node_ids.items():
            simple_name_index.setdefault(fn_name, []).append(fn_id)
        for (_, cls_name, method_name), method_id in method_node_ids.items():
            simple_name_index.setdefault(method_name, []).append(method_id)
            key = f"{cls_name}.{method_name}"
            class_method_index.setdefault(key, []).append(method_id)

        def resolve_call(module_path: str, call_name: str) -> Optional[str]:
            if "." in call_name:
                if (
                    call_name in class_method_index
                    and len(class_method_index[call_name]) == 1
                ):
                    return class_method_index[call_name][0]

                left, right = call_name.rsplit(".", 1)
                if left in module_name_to_path:
                    target_module_path = module_name_to_path[left]
                    key = (target_module_path, right)
                    if key in function_node_ids:
                        return function_node_ids[key]

                if (
                    right in simple_name_index
                    and len(simple_name_index[right]) == 1
                ):
                    return simple_name_index[right][0]
                return None

            if (
                call_name in simple_name_index
                and len(simple_name_index[call_name]) == 1
            ):
                return simple_name_index[call_name][0]
            return None

        for module_path, module in self.indexer.modules.items():
            for fn in getattr(module, "functions", []) or []:
                source_id = function_node_ids.get((module_path, fn.name))
                if not source_id:
                    continue
                for call_name in getattr(fn, "calls", []) or []:
                    target_id = resolve_call(module_path, call_name)
                    if target_id:
                        self.graph.add_edge(
                            RelationshipEdge(
                                source_id=source_id,
                                target_id=target_id,
                                relationship="calls",
                            )
                        )

            for cls in getattr(module, "classes", []) or []:
                for method in getattr(cls, "methods", []) or []:
                    source_id = method_node_ids.get(
                        (module_path, cls.name, method.name)
                    )
                    if not source_id:
                        continue
                    for call_name in getattr(method, "calls", []) or []:
                        target_id = resolve_call(module_path, call_name)
                        if target_id:
                            self.graph.add_edge(
                                RelationshipEdge(
                                    source_id=source_id,
                                    target_id=target_id,
                                    relationship="calls",
                                )
                            )

        print(f"✅ Knowledge graph built with {len(self.graph.nodes)} nodes")
        return self.graph
        
    def export_to_json(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(self.graph.to_dict(), f, indent=2)
        print(f"📄 Graph exported to {filepath}")

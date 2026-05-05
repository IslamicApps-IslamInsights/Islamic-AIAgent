"""
Project Indexer - Analyzes and indexes the entire codebase
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime


@dataclass
class FunctionAnalysis:
    """Analysis of a single function"""
    name: str
    line_number: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    complexity: int = 0


@dataclass
class ClassAnalysis:
    """Analysis of a single class"""
    name: str
    line_number: int
    docstring: Optional[str] = None
    methods: List[FunctionAnalysis] = field(default_factory=list)
    parent_classes: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    complexity: int = 0


@dataclass
class ModuleAnalysis:
    """Analysis of a single Python module"""
    path: str
    filename: str
    imports: Dict[str, List[str]] = field(default_factory=dict)
    classes: List[ClassAnalysis] = field(default_factory=list)
    functions: List[FunctionAnalysis] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    docstring: Optional[str] = None
    lines_of_code: int = 0
    complexity: int = 0


class ProjectIndexer:
    """Main project indexer for analyzing the entire codebase"""
    
    def __init__(
        self, root_path: str, exclude_dirs: Optional[List[str]] = None
    ):
        self.root_path = Path(root_path)
        self.exclude_dirs = exclude_dirs or [
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "env",
            ".tox",
            ".mypy_cache",
        ]
        self.modules: Dict[str, ModuleAnalysis] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._module_name_to_path: Dict[str, str] = {}
        self.index_metadata = {
            "indexed_at": datetime.now().isoformat(),
            "root_path": str(root_path),
            "total_modules": 0,
            "total_classes": 0,
            "total_functions": 0,
            "language_breakdown": defaultdict(int)
        }
        self._build_module_name_map()
        
    def index_project(self) -> Dict[str, Any]:
        """Index the entire project"""
        print(f"🔍 Starting project indexing from {self.root_path}")
        self._index_python_files()
        self._analyze_dependencies()
        print("✅ Indexing complete!")
        return self._generate_index_report()
        
    def _build_module_name_map(self) -> None:
        self._module_name_to_path.clear()
        try:
            for py_file in self.root_path.rglob("*.py"):
                if any(
                    excluded in py_file.parts for excluded in self.exclude_dirs
                ):
                    continue
                rel = py_file.relative_to(self.root_path)
                if rel.name == "__init__.py":
                    parent_parts = rel.parent.parts
                    module_name = (
                        ".".join(parent_parts) if parent_parts else "__init__"
                    )
                else:
                    module_name = ".".join(rel.with_suffix("").parts)
                self._module_name_to_path[module_name] = str(rel)
        except Exception:
            pass

    def _index_python_files(self):
        """Index all Python files"""
        py_files = self.root_path.rglob("*.py")
        for py_file in py_files:
            if any(
                excluded in py_file.parts for excluded in self.exclude_dirs
            ):
                continue
            try:
                self._analyze_python_file(py_file)
                self.index_metadata["language_breakdown"]["python"] += 1
            except Exception as e:
                print(f"⚠️  Error analyzing {py_file}: {e}")
                
    def _unparse(self, node: ast.AST) -> str:
        unparse = getattr(ast, "unparse", None)
        if callable(unparse):
            try:
                return unparse(node)
            except Exception:
                return ast.dump(node, include_attributes=False)
        return ast.dump(node, include_attributes=False)

    def _get_call_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._get_call_name(node.value)
            if not base:
                return node.attr
            return f"{base}.{node.attr}"
        return None

    def _compute_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for sub in ast.walk(node):
            if isinstance(
                sub,
                (
                    ast.If,
                    ast.For,
                    ast.AsyncFor,
                    ast.While,
                    ast.With,
                    ast.AsyncWith,
                    ast.IfExp,
                ),
            ):
                complexity += 1
            elif isinstance(sub, ast.Try):
                complexity += max(1, len(sub.handlers))
            elif isinstance(sub, ast.ExceptHandler):
                complexity += 1
            elif isinstance(sub, ast.BoolOp):
                complexity += max(0, len(getattr(sub, "values", []) or []) - 1)
            elif isinstance(sub, ast.comprehension):
                complexity += max(0, len(getattr(sub, "ifs", []) or []))
            elif isinstance(sub, getattr(ast, "Match", ())):
                complexity += max(1, len(getattr(sub, "cases", []) or []))
        return complexity

    def _function_parameters(self, node: ast.AST) -> List[str]:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        params: List[str] = []
        args = node.args
        for a in args.posonlyargs + args.args:
            params.append(a.arg)
        if args.vararg:
            params.append(f"*{args.vararg.arg}")
        for a in args.kwonlyargs:
            params.append(a.arg)
        if args.kwarg:
            params.append(f"**{args.kwarg.arg}")
        return params

    def _resolve_import_module(
        self, current_module_name: str, module: Optional[str], level: int
    ) -> Optional[str]:
        if level <= 0:
            return module
        parts = current_module_name.split(".")
        base_parts = parts[:-1]
        up = max(0, len(base_parts) - (level - 1))
        base_parts = base_parts[:up]
        if module:
            base_parts.extend(module.split("."))
        if not base_parts:
            return module or None
        return ".".join(base_parts)

    def _analyze_python_file(self, filepath: Path):
        """Analyze a single Python file using AST"""
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source_code = f.read()
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return
            
        module_path = str(filepath.relative_to(self.root_path))
        module_name = ".".join(Path(module_path).with_suffix("").parts)
        if filepath.name == "__init__.py":
            parent_parts = Path(module_path).parent.parts
            module_name = (
                ".".join(parent_parts) if parent_parts else "__init__"
            )
        module = ModuleAnalysis(
            path=module_path,
            filename=filepath.name,
            docstring=ast.get_docstring(tree),
            lines_of_code=len(source_code.splitlines()),
        )
        self.modules[module_path] = module
        self.index_metadata["total_modules"] += 1

        class_defs: List[ClassAnalysis] = []
        function_defs: List[FunctionAnalysis] = []
        imports: Dict[str, List[str]] = defaultdict(list)
        dependencies: Set[str] = set()

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.name].append(alias.asname or alias.name)
                    dependencies.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                resolved = self._resolve_import_module(
                    module_name, node.module, node.level or 0
                )
                if resolved:
                    for alias in node.names:
                        imports[resolved].append(alias.name)
                    dependencies.add(resolved)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                calls = []
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call):
                        call_name = self._get_call_name(sub.func)
                        if call_name:
                            calls.append(call_name)
                fn = FunctionAnalysis(
                    name=node.name,
                    line_number=getattr(node, "lineno", 0) or 0,
                    docstring=ast.get_docstring(node),
                    parameters=self._function_parameters(node),
                    return_type=(
                        self._unparse(node.returns)
                        if getattr(node, "returns", None) is not None
                        else None
                    ),
                    decorators=[
                        self._unparse(d)
                        for d in getattr(node, "decorator_list", []) or []
                    ],
                    calls=sorted(set(calls)),
                    complexity=self._compute_complexity(node),
                )
                function_defs.append(fn)
                self.index_metadata["total_functions"] += 1
            elif isinstance(node, ast.ClassDef):
                parent_classes = [self._unparse(b) for b in node.bases or []]
                attributes: Set[str] = set()
                methods: List[FunctionAnalysis] = []

                for child in node.body:
                    if isinstance(
                        child, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ):
                        calls = []
                        for sub in ast.walk(child):
                            if isinstance(sub, ast.Call):
                                call_name = self._get_call_name(sub.func)
                                if call_name:
                                    calls.append(call_name)
                        method = FunctionAnalysis(
                            name=child.name,
                            line_number=getattr(child, "lineno", 0) or 0,
                            docstring=ast.get_docstring(child),
                            parameters=self._function_parameters(child),
                            return_type=(
                                self._unparse(child.returns)
                                if getattr(child, "returns", None) is not None
                                else None
                            ),
                            decorators=self._decorator_names(child),
                            calls=sorted(set(calls)),
                            complexity=self._compute_complexity(child),
                        )
                        methods.append(method)
                        self.index_metadata["total_functions"] += 1
                    elif isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                attributes.add(target.id)
                            elif isinstance(target, ast.Attribute):
                                attributes.add(target.attr)
                    elif isinstance(child, ast.AnnAssign):
                        target = child.target
                        if isinstance(target, ast.Name):
                            attributes.add(target.id)
                        elif isinstance(target, ast.Attribute):
                            attributes.add(target.attr)

                cls = ClassAnalysis(
                    name=node.name,
                    line_number=getattr(node, "lineno", 0) or 0,
                    docstring=ast.get_docstring(node),
                    methods=methods,
                    parent_classes=parent_classes,
                    attributes=sorted(attributes),
                    complexity=sum(m.complexity for m in methods) or 1,
                )
                class_defs.append(cls)
                self.index_metadata["total_classes"] += 1

        module.imports = dict(imports)
        module.dependencies = dependencies
        module.functions = function_defs
        module.classes = class_defs
        module.complexity = (
            sum(f.complexity for f in function_defs)
            + sum(c.complexity for c in class_defs)
        ) or 1
        
    def _analyze_dependencies(self):
        """Analyze module dependencies"""
        self.dependencies.clear()
        for module_path, module in self.modules.items():
            for dep in module.dependencies:
                self.dependencies[module_path].add(dep)

            for import_module in module.imports.keys():
                resolved = import_module
                if resolved and resolved in self._module_name_to_path:
                    self.dependencies[module_path].add(resolved)
                else:
                    prefix_parts = resolved.split(".") if resolved else []
                    while prefix_parts:
                        candidate = ".".join(prefix_parts)
                        if candidate in self._module_name_to_path:
                            self.dependencies[module_path].add(candidate)
                            break
                        prefix_parts.pop()
        
    def _generate_index_report(self) -> Dict[str, Any]:
        """Generate comprehensive index report"""
        dependency_graph: Dict[str, List[str]] = {}
        external_dependencies: Set[str] = set()
        internal_dependency_graph: Dict[str, List[str]] = {}

        for module_path, deps in self.dependencies.items():
            deps_list = sorted(deps)
            dependency_graph[module_path] = deps_list
            internal_paths: Set[str] = set()
            for dep in deps_list:
                if dep in self._module_name_to_path:
                    internal_paths.add(self._module_name_to_path[dep])
                else:
                    external_dependencies.add(dep)
            internal_dependency_graph[module_path] = sorted(internal_paths)

        modules_out: Dict[str, Any] = {}
        for k, v in self.modules.items():
            modules_out[k] = {
                "path": v.path,
                "filename": v.filename,
                "docstring": v.docstring,
                "lines_of_code": v.lines_of_code,
                "complexity": v.complexity,
                "imports": v.imports,
                "dependencies": sorted(v.dependencies),
                "classes": [
                    {
                        "name": c.name,
                        "line_number": c.line_number,
                        "docstring": c.docstring,
                        "parent_classes": c.parent_classes,
                        "attributes": c.attributes,
                        "complexity": c.complexity,
                        "methods": [
                            {
                                "name": m.name,
                                "line_number": m.line_number,
                                "docstring": m.docstring,
                                "parameters": m.parameters,
                                "return_type": m.return_type,
                                "decorators": m.decorators,
                                "calls": m.calls,
                                "complexity": m.complexity,
                            }
                            for m in c.methods
                        ],
                    }
                    for c in v.classes
                ],
                "functions": [
                    {
                        "name": f.name,
                        "line_number": f.line_number,
                        "docstring": f.docstring,
                        "parameters": f.parameters,
                        "return_type": f.return_type,
                        "decorators": f.decorators,
                        "calls": f.calls,
                        "complexity": f.complexity,
                    }
                    for f in v.functions
                ],
            }

        return {
            "metadata": dict(self.index_metadata),
            "modules": modules_out,
            "statistics": {
                "total_lines_of_code": sum(
                    m.lines_of_code for m in self.modules.values()
                ),
                "total_complexity": sum(
                    m.complexity for m in self.modules.values()
                ),
            },
            "dependency_graph": dependency_graph,
            "internal_dependency_graph": internal_dependency_graph,
            "external_dependencies": sorted(external_dependencies),
        }

    def _decorator_names(self, node: ast.AST) -> List[str]:
        decorators = getattr(node, "decorator_list", None) or []
        return [self._unparse(d) for d in decorators]

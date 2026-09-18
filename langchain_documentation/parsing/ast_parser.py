# parsing/ast_parser.py

import ast
from pathlib import Path


def _get_module_path(file_path: Path, package_root: Path) -> str:
    """Convert a file path into a dotted module path, e.g. 'langchain_core.agents'."""
    relative = file_path.relative_to(package_root)

    parts = list(relative.parts)
    parts[-1] = parts[-1].replace(".py", "")

    if parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def _is_overload_stub(node) -> bool:
    """Check if a function is decorated with @overload (typing stub, not real impl)."""
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "overload":
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr == "overload":
            return True
    return False


def parse_file(file_path: Path, package_root: Path) -> list[dict]:
    """Parse a single .py file and extract functions and classes with qualified names."""
    source_code = file_path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source_code, filename=str(file_path))
    except SyntaxError as e:
        print(f"Skipping {file_path} due to syntax error: {e}")
        return []

    module_path = _get_module_path(file_path, package_root)
    extracted = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_qname = f"{module_path}.{node.name}"
            extracted.append(_build_entry(node, file_path, qualified_name=class_qname))

            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if _is_overload_stub(child):
                        continue
                    method_qname = f"{class_qname}.{child.name}"
                    extracted.append(_build_entry(child, file_path, method_qname))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_overload_stub(node):
                continue
            func_qname = f"{module_path}.{node.name}"
            extracted.append(_build_entry(node, file_path, qualified_name=func_qname))

    return extracted


def _build_entry(node, file_path: Path, qualified_name: str) -> dict:
    entry = {
        "name": node.name,
        "qualified_name": qualified_name,
        "type": type(node).__name__,
        "lineno": node.lineno,
        "docstring": ast.get_docstring(node),
        "file_path": str(file_path),
    }

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        entry["signature"] = _extract_signature(node)

    return entry


def _extract_signature(node) -> str:
    """Build a human-readable signature string like 'model, temperature=0.7, *args'."""
    parts = []
    args = node.args

    defaults_offset = len(args.args) - len(args.defaults)
    for i, arg in enumerate(args.args):
        if i >= defaults_offset:
            default_val = ast.unparse(args.defaults[i - defaults_offset])
            parts.append(f"{arg.arg}={default_val}")
        else:
            parts.append(arg.arg)

    if args.vararg:
        parts.append(f"*{args.vararg.arg}")

    for i, kwarg in enumerate(args.kwonlyargs):
        if args.kw_defaults[i] is not None:
            default_val = ast.unparse(args.kw_defaults[i])
            parts.append(f"{kwarg.arg}={default_val}")
        else:
            parts.append(kwarg.arg)

    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")

    return f"({', '.join(parts)})"


if __name__ == "__main__":
    from langchain_documentation.ingestion.file_finder import find_python_files

    print("Starting...")
    files = find_python_files()
    print(f"Found {len(files)} files")

    file_path, package_root = files[0]
    result = parse_file(file_path, package_root)
    print(f"Extracted {len(result)} items")

    for item in result:
        print(item)
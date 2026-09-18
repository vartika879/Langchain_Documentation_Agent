# parsing/ast_parser.py — updated version


# parsing/ast_parser.py — updated with signature extraction

import ast
from pathlib import Path


def parse_file(file_path: Path) -> list[dict]:
    """Parse a single .py file and extract functions and classes with qualified names."""
    source_code = file_path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source_code, filename=str(file_path))
    except SyntaxError as e:
        print(f"Skipping {file_path} due to syntax error: {e}")
        return []

    extracted = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            extracted.append(_build_entry(node, file_path, qualified_name=node.name))

            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    qualified_name = f"{node.name}.{child.name}"
                    extracted.append(_build_entry(child, file_path, qualified_name))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            extracted.append(_build_entry(node, file_path, qualified_name=node.name))

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

    # regular positional/keyword args
    defaults_offset = len(args.args) - len(args.defaults)
    for i, arg in enumerate(args.args):
        if i >= defaults_offset:
            default_val = ast.unparse(args.defaults[i - defaults_offset])
            parts.append(f"{arg.arg}={default_val}")
        else:
            parts.append(arg.arg)

    # *args
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")

    # keyword-only args
    for i, kwarg in enumerate(args.kwonlyargs):
        if args.kw_defaults[i] is not None:
            default_val = ast.unparse(args.kw_defaults[i])
            parts.append(f"{kwarg.arg}={default_val}")
        else:
            parts.append(kwarg.arg)

    # **kwargs
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")

    return f"({', '.join(parts)})"

if __name__ == "__main__":
    from langchain_documentation.ingestion.file_finder import find_python_files

    print("Starting...")  # ye line add karo
    files = find_python_files()
    print(f"Found {len(files)} files")  # ye bhi

    result = parse_file(files[0])
    print(f"Extracted {len(result)} items")  # ye bhi

    for item in result:
        print(item)
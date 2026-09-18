# debug_duplicates.py (project root mein, temporary file — baad mein delete kar sakte ho)

from langchain_documentation.ingestion.file_finder import find_python_files
from langchain_documentation.parsing.ast_parser import parse_file

files = find_python_files()

seen = {}
for f in files:
    entries = parse_file(f)
    for entry in entries:
        qname = entry["qualified_name"]
        if qname in seen:
            print(f"DUPLICATE: {qname}")
            print(f"  First:  {seen[qname]}")
            print(f"  Second: {entry['file_path']}, line {entry['lineno']}")
        seen[qname] = entry["file_path"] + f", line {entry['lineno']}"
# query.py — query_function function update (tiered search)

import sys
from langchain_documentation.storage.models import SessionLocal, FunctionEntry, ChangeLog
from langchain_documentation.main import run_ingestion


def query_function(search_term: str):
    session = SessionLocal()

    # Tier 1: exact match
    exact = session.query(FunctionEntry).filter_by(qualified_name=search_term).first()
    if exact:
        _print_entry(session, exact)
        return

    # Tier 2: "ends with .search_term" — class/function-level match, methods exclude honge
    all_entries = session.query(FunctionEntry).all()
    ends_with_matches = [
        e for e in all_entries
        if e.qualified_name.endswith(f".{search_term}") or e.qualified_name == search_term
    ]

    if len(ends_with_matches) == 1:
        _print_entry(session, ends_with_matches[0])
        return
    elif len(ends_with_matches) > 1:
        print(f"{len(ends_with_matches)} matches mile:")
        for m in ends_with_matches:
            print(f"  - {m.qualified_name}")
        print("\nZyada specific naam do (jaise 'AgentAction.__init__') exact result ke liye.")
        return

    # Tier 3: fallback — contains search
    matches = [e for e in all_entries if search_term in e.qualified_name]

    if not matches:
        print(f"'{search_term}' ke liye kuch nahi mila.")
        return

    if len(matches) > 1:
        print(f"{len(matches)} matches mile (broad search):")
        for m in matches:
            print(f"  - {m.qualified_name}")
        print("\nZyada specific naam do exact result ke liye.")
        return

    _print_entry(session, matches[0])


def _print_entry(session, entry):
    print(f"\n{entry.qualified_name}")
    print(f"Type: {entry.type}")
    if entry.signature:
        print(f"Signature: {entry.signature}")
    print(f"\nDocstring:\n{entry.docstring or '(none)'}")

    changes = session.query(ChangeLog).filter_by(
        qualified_name=entry.qualified_name
    ).order_by(ChangeLog.detected_at.desc()).all()

    if changes:
        print(f"\n--- Change History ({len(changes)}) ---")
        for c in changes:
            print(f"[{c.detected_at}] {c.change_type}")
    else:
        print("\n(Koi tracked change nahi mila.)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m query <function_or_class_name>")
        sys.exit(1)

    print("Checking for updates...")
    run_ingestion()

    search_term = sys.argv[1]
    query_function(search_term)
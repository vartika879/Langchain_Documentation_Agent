# main.py

import logging
from datetime import datetime
from pathlib import Path

from langchain_documentation.ingestion.repo_manager import ensure_repo
from langchain_documentation.ingestion.file_finder import find_python_files
from langchain_documentation.parsing.ast_parser import parse_file
from langchain_documentation.storage.models import init_db, SessionLocal, FunctionEntry, ChangeLog

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


def run_ingestion():
    logging.info("Starting ingestion run")

    ensure_repo()
    init_db()
    session = SessionLocal()

    files = find_python_files()
    logging.info(f"Processing {len(files)} files...")

    seen_qualified_names = set()
    new_count = 0
    updated_count = 0
    unchanged_count = 0

    for file_path,package_root in files:
        entries = parse_file(file_path,package_root)

        for entry in entries:
            qname = entry["qualified_name"]
            seen_qualified_names.add(qname)

            existing = session.query(FunctionEntry).filter_by(qualified_name=qname).first()

            if existing is None:
                db_entry = FunctionEntry(
                    name=entry["name"],
                    qualified_name=qname,
                    type=entry["type"],
                    lineno=entry["lineno"],
                    docstring=entry["docstring"],
                    signature=entry.get("signature"),
                    file_path=entry["file_path"],
                )
                session.add(db_entry)
                session.add(ChangeLog(
                    qualified_name=qname,
                    change_type="new",
                    old_value=None,
                    new_value=entry.get("signature") or entry["docstring"],
                ))
                new_count += 1

            else:
                sig_changed = existing.signature != entry.get("signature")
                doc_changed = existing.docstring != entry["docstring"]

                if sig_changed:
                    session.add(ChangeLog(
                        qualified_name=qname,
                        change_type="signature_changed",
                        old_value=existing.signature,
                        new_value=entry.get("signature"),
                    ))
                    existing.signature = entry.get("signature")

                if doc_changed:
                    session.add(ChangeLog(
                        qualified_name=qname,
                        change_type="docstring_changed",
                        old_value=existing.docstring,
                        new_value=entry["docstring"],
                    ))
                    existing.docstring = entry["docstring"]

                if sig_changed or doc_changed:
                    updated_count += 1
                else:
                    unchanged_count += 1

    all_db_entries = session.query(FunctionEntry).all()
    removed_count = 0
    for db_entry in all_db_entries:
        if db_entry.qualified_name not in seen_qualified_names:
            session.add(ChangeLog(
                qualified_name=db_entry.qualified_name,
                change_type="removed",
                old_value=db_entry.signature or db_entry.docstring,
                new_value=None,
            ))
            session.delete(db_entry)
            removed_count += 1

    session.commit()
    logging.info(
        f"New: {new_count}, Updated: {updated_count}, "
        f"Unchanged: {unchanged_count}, Removed: {removed_count}"
    )
    logging.info("Ingestion run complete")


if __name__ == "__main__":
    run_ingestion()
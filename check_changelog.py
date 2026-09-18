# check_changelog.py (project root, temporary)

from langchain_documentation.storage.models import SessionLocal, ChangeLog

session = SessionLocal()
recent = session.query(ChangeLog).order_by(ChangeLog.id.desc()).limit(5).all()

for c in recent:
    print(f"{c.qualified_name} | {c.change_type}")
    print(f"  OLD: {c.old_value}")
    print(f"  NEW: {c.new_value}")
    print()

# storage/models.py

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from langchain_documentation.config import DATABASE_URL

Base = declarative_base()


class FunctionEntry(Base):
    __tablename__ = "function_entries"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    qualified_name = Column(String, unique=True)
    type = Column(String)
    lineno = Column(Integer)
    docstring = Column(Text, nullable=True)
    signature = Column(Text, nullable=True)
    file_path = Column(String)


class ChangeLog(Base):
    __tablename__ = "change_log"

    id = Column(Integer, primary_key=True)
    qualified_name = Column(String)
    change_type = Column(String)  # "new", "signature_changed", "docstring_changed", "removed"
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
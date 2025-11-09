"""SQLAlchemy models for the Tiwhanawhana schema."""
import datetime
import uuid

from sqlalchemy import Column, Integer, JSON, Numeric, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MauriLog(Base):
    __tablename__ = "mauri_logs"
    __table_args__ = {"schema": "tiwhanawhana"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phase = Column(Text, default="awakening")
    tohu_id = Column(Text)
    message = Column(Text)
    meta = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)


class TaskQueue(Base):
    __tablename__ = "task_queue"
    __table_args__ = {"schema": "tiwhanawhana"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(Text)
    payload = Column(JSON)
    status = Column(Text, default="pending")
    priority = Column(Integer, default=1)
    retries = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)


class OCRLog(Base):
    __tablename__ = "ocr_logs"
    __table_args__ = {"schema": "tiwhanawhana"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(Text)
    file_url = Column(Text)
    text_content = Column(Text)
    language_detected = Column(Text)
    meta = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)


class Translation(Base):
    __tablename__ = "translations"
    __table_args__ = {"schema": "tiwhanawhana"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ocr_id = Column(UUID(as_uuid=True), ForeignKey("tiwhanawhana.ocr_logs.id"))
    source_lang = Column(Text)
    target_lang = Column(Text)
    source_text = Column(Text)
    translated_text = Column(Text)
    model_used = Column(Text)
    confidence = Column(Numeric)
    meta = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)


class Embedding(Base):
    __tablename__ = "embeddings"
    __table_args__ = {"schema": "tiwhanawhana"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    translation_id = Column(UUID(as_uuid=True), ForeignKey(
        "tiwhanawhana.translations.id"))
    text_chunk = Column(Text)
    embedding = Column(VECTOR(1536))
    meta = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)


class TiMemory(Base):
    __tablename__ = "ti_memory"
    __table_args__ = {"schema": "tiwhanawhana"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    memory_type = Column(Text, default="reflection")
    content = Column(Text)
    embedding = Column(VECTOR(1536))
    related_task = Column(UUID(as_uuid=True), ForeignKey(
        "tiwhanawhana.task_queue.id"))
    meta = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

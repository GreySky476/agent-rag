from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import DATERANGE, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class KnowledgeDomain(Base):
    __tablename__ = "knowledge_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    entry_point: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default="now()"
    )

    files: Mapped[list[FileIndex]] = relationship(back_populates="domain")


class FileIndex(Base):
    __tablename__ = "file_index"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    domain_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("knowledge_domains.id"), nullable=True
    )
    file_path: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    entities: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    has_tables: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    data_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    time_range: Mapped[tuple[date, date] | None] = mapped_column(DATERANGE, nullable=True)
    hash_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    importance: Mapped[str] = mapped_column(String(2), default="L1", server_default="'L1'")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default="now()"
    )
    processing_status: Mapped[str] = mapped_column(
        String(20), default="pending", server_default="'pending'"
    )

    domain: Mapped[KnowledgeDomain | None] = relationship(back_populates="files")
    chunks: Mapped[list[ChunkIndex]] = relationship(
        back_populates="file", cascade="all, delete-orphan"
    )


class ChunkIndex(Base):
    __tablename__ = "chunk_index"
    __table_args__ = (UniqueConstraint("file_id", "chunk_order"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("file_index.id", ondelete="CASCADE"), nullable=False
    )
    chunk_order: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_type: Mapped[str] = mapped_column(String(20), default="text", server_default="'text'")
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    file: Mapped[FileIndex] = relationship(back_populates="chunks")


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    step: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tool_input: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tool_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reflection: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="running", server_default="'running'")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default="now()"
    )

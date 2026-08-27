from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Float, JSON, Index, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class SourceAuthorityLevel(str):
    OFFICIAL_PRIMARY = "official_primary"        # e.g., testcenter.kz, gov.kz/memleket/entities/sci
    OFFICIAL_SECONDARY = "official_secondary"    # e.g., edu.gov.kz, nce.kz
    TRUSTED_EDUCATIONAL = "trusted_educational"  # e.g., daryn.kz, nis.edu.kz
    SECONDARY_MEDIA = "secondary_media"          # e.g., bilimdinews.kz, tengrinews.kz (education section)
    COMMUNITY = "community"                      # user submissions, peer discussions


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    feed_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="official_portal", nullable=False)  # official_portal, rss_feed, ministry, specification_doc
    authority_level: Mapped[str] = mapped_column(String(50), default=SourceAuthorityLevel.OFFICIAL_PRIMARY, nullable=False, index=True)
    default_language: Mapped[str] = mapped_column(String(10), default="kk", nullable=False)  # kk, ru, en
    country: Mapped[str] = mapped_column(String(10), default="KZ", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    crawl_frequency_minutes: Mapped[int] = mapped_column(Integer, default=720, nullable=False)  # default: twice daily
    robots_policy: Mapped[str] = mapped_column(String(50), default="allowed", nullable=False)
    terms_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    documents: Mapped[List["SourceDocument"]] = relationship("SourceDocument", back_populates="source", cascade="all, delete-orphan")
    ingestion_runs: Mapped[List["IngestionRun"]] = relationship("IngestionRun", back_populates="source", cascade="all, delete-orphan")
    question_provenance_records: Mapped[List["QuestionProvenance"]] = relationship("QuestionProvenance", back_populates="source")
    news_sources: Mapped[List["NewsSource"]] = relationship("NewsSource", back_populates="source")


class SourceDocument(Base, TimestampMixin):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # sha256 of raw content
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="text/html", nullable=False)  # text/html, application/json, text/xml
    http_status: Mapped[int] = mapped_column(Integer, default=200, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    doc_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    source: Mapped["Source"] = relationship("Source", back_populates="documents")


class IngestionRunStatus(str):
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class IngestionRun(Base, TimestampMixin):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), index=True, nullable=False)
    job_name: Mapped[str] = mapped_column(String(100), default="daily_sync", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default=IngestionRunStatus.RUNNING, nullable=False, index=True)
    items_discovered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source: Mapped["Source"] = relationship("Source", back_populates="ingestion_runs")
    items: Mapped[List["IngestionItem"]] = relationship("IngestionItem", back_populates="run", cascade="all, delete-orphan")


class IngestionItem(Base, TimestampMixin):
    __tablename__ = "ingestion_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("ingestion_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)  # news, question, specification, rule
    external_identifier: Mapped[str] = mapped_column(String(500), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    action_taken: Mapped[str] = mapped_column(String(30), nullable=False)  # created, updated, skipped, error
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    run: Mapped["IngestionRun"] = relationship("IngestionRun", back_populates="items")

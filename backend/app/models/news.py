from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Float, JSON, Index, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class NewsCategory(str):
    UNT = "unt"
    REGISTRATION = "registration"
    DEADLINES = "deadlines"
    GRANTS = "grants"
    ADMISSIONS = "admissions"
    EXAM_RESULTS = "exam_results"
    INFORMATICS = "informatics"
    SPECIFICATION = "specification"
    EDUCATION_POLICY = "education_policy"
    UNIVERSITIES = "universities"
    ANNOUNCEMENT = "announcement"


class NewsStatus(str):
    PUBLISHED = "published"
    PENDING_REVIEW = "pending_review"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class NewsArticle(Base, TimestampMixin):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_url: Mapped[str] = mapped_column(String(1000), unique=True, index=True, nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id", ondelete="RESTRICT"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default=NewsCategory.UNT, nullable=False, index=True)
    original_language: Mapped[str] = mapped_column(String(10), default="kk", nullable=False)  # kk, ru, en
    
    # Metadata and scores
    importance_score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 1 (low) - 10 (critical alert)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 0.00 to 1.00
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default=NewsStatus.PUBLISHED, nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # sha256 of canonical text
    
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    source: Mapped["Source"] = relationship("Source")
    translations: Mapped[List["NewsTranslation"]] = relationship("NewsTranslation", back_populates="article", cascade="all, delete-orphan")
    versions: Mapped[List["NewsVersion"]] = relationship("NewsVersion", back_populates="article", cascade="all, delete-orphan", order_by="NewsVersion.version_number.desc()")
    sources_rel: Mapped[List["NewsSource"]] = relationship("NewsSource", back_populates="article", cascade="all, delete-orphan")


class NewsTranslation(Base, TimestampMixin):
    __tablename__ = "news_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), index=True, nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # kk, ru, en
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    translation_source: Mapped[str] = mapped_column(String(50), default="official", nullable=False)  # official, human, ai, hybrid
    translation_status: Mapped[str] = mapped_column(String(30), default="published", nullable=False)  # published, validated, needs_review, draft
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    article: Mapped["NewsArticle"] = relationship("NewsArticle", back_populates="translations")

    __table_args__ = (
        Index("idx_news_translations_lookup", "news_id", "locale", unique=True),
    )


class NewsVersion(Base, TimestampMixin):
    __tablename__ = "news_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    article: Mapped["NewsArticle"] = relationship("NewsArticle", back_populates="versions")


class NewsSource(Base, TimestampMixin):
    __tablename__ = "news_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), index=True, nullable=False)
    external_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    attribution_text: Mapped[str] = mapped_column(String(255), nullable=False)

    article: Mapped["NewsArticle"] = relationship("NewsArticle", back_populates="sources_rel")
    source: Mapped["Source"] = relationship("Source", back_populates="news_sources")

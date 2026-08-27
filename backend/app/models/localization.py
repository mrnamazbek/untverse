from typing import Optional
from sqlalchemy import String, Boolean, Integer, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class LocalizationGlossary(Base, TimestampMixin):
    __tablename__ = "localization_glossary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    concept_key: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    kk: Mapped[str] = mapped_column(String(255), nullable=False)  # Official Kazakh terminology
    ru: Mapped[str] = mapped_column(String(255), nullable=False)  # Russian terminology
    en: Mapped[str] = mapped_column(String(255), nullable=False)  # English terminology
    context: Mapped[Optional[str]] = mapped_column(String(255), default="educational_unt", nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="NTC_KZ", nullable=False)  # NTC_KZ, MES_KZ, ACADEMIC
    approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_glossary_search", "kk", "ru", "en"),
    )

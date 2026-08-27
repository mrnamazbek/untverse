from typing import Optional, List
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, JSON, Index, DateTime, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class ExamType(Base, TimestampMixin):
    __tablename__ = "exam_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # unt, olympiad
    name_kk: Mapped[str] = mapped_column(String(150), nullable=False)  # Ұлттық бірыңғай тестілеу
    name_ru: Mapped[str] = mapped_column(String(150), nullable=False)  # Единое национальное тестирование
    name_en: Mapped[str] = mapped_column(String(150), nullable=False)  # Unified National Testing
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    specifications: Mapped[List["ExamSpecification"]] = relationship("ExamSpecification", back_populates="exam_type")
    current_rules: Mapped[List["CurrentUntRule"]] = relationship("CurrentUntRule", back_populates="exam_type")


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # informatics, mathematics
    name_kk: Mapped[str] = mapped_column(String(150), nullable=False)  # Информатика
    name_ru: Mapped[str] = mapped_column(String(150), nullable=False)  # Информатика
    name_en: Mapped[str] = mapped_column(String(150), nullable=False)  # Informatics
    is_profile: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    specifications: Mapped[List["ExamSpecification"]] = relationship("ExamSpecification", back_populates="subject")
    bank_questions: Mapped[List["BankQuestion"]] = relationship("BankQuestion", back_populates="subject")


class SpecificationStatus(str):
    ACTIVE = "active"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


class ExamSpecification(Base, TimestampMixin):
    __tablename__ = "exam_specifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam_types.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    exam_year: Mapped[int] = mapped_column(Integer, default=2026, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), default="2026.1", nullable=False)
    title_kk: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, default=date(2025, 9, 1), nullable=False)
    valid_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default=SpecificationStatus.ACTIVE, nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_document_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    exam_type: Mapped["ExamType"] = relationship("ExamType", back_populates="specifications")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="specifications")
    sections: Mapped[List["SpecificationSection"]] = relationship("SpecificationSection", back_populates="specification", cascade="all, delete-orphan", order_by="SpecificationSection.order_index")


class SpecificationSection(Base, TimestampMixin):
    __tablename__ = "specification_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specification_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam_specifications.id", ondelete="CASCADE"), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., CS-1, ALGO-2
    title_kk: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight_percentage: Mapped[int] = mapped_column(Integer, default=15, nullable=False)  # approx share of exam
    question_count_est: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    specification: Mapped["ExamSpecification"] = relationship("ExamSpecification", back_populates="sections")
    topics: Mapped[List["SpecificationTopic"]] = relationship("SpecificationTopic", back_populates="section", cascade="all, delete-orphan", order_by="SpecificationTopic.order_index")


class SpecificationTopic(Base, TimestampMixin):
    __tablename__ = "specification_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("specification_sections.id", ondelete="CASCADE"), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    title_kk: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    learning_objectives: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # list of NCT learning outcome codes (e.g. 10.1.2.1)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    section: Mapped["SpecificationSection"] = relationship("SpecificationSection", back_populates="topics")
    bank_questions: Mapped[List["BankQuestion"]] = relationship("BankQuestion", back_populates="specification_topic")


class CurrentUntRule(Base, TimestampMixin):
    __tablename__ = "current_unt_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam_types.id", ondelete="CASCADE"), index=True, nullable=False)
    exam_year: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)  # 2026
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Official structure facts
    total_questions: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    maximum_score: Mapped[int] = mapped_column(Integer, default=140, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=240, nullable=False)
    passing_threshold_total: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    passing_threshold_per_subject: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    # Informatics specific facts
    informatics_questions_count: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    informatics_max_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    
    # Structured JSON data
    subjects_structure: Mapped[dict] = mapped_column(JSON, nullable=False)
    profile_combinations: Mapped[dict] = mapped_column(JSON, nullable=False)
    testing_periods: Mapped[dict] = mapped_column(JSON, nullable=False)
    important_deadlines: Mapped[dict] = mapped_column(JSON, nullable=False)
    grant_rules_summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    official_source_urls: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    last_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    verified_by: Mapped[str] = mapped_column(String(100), default="NTC_Official_2026", nullable=False)

    exam_type: Mapped["ExamType"] = relationship("ExamType", back_populates="current_rules")

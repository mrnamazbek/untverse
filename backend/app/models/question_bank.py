import uuid
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Float, JSON, Index, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class QuestionDifficulty(str):
    A = "A"  # Basic / Базалық деңгей (1 point, straightforward recall & basic syntax)
    B = "B"  # Intermediate / Орташа деңгей (application, trace loops, standard queries)
    C = "C"  # Advanced / Жоғары деңгей (multi-step logic, optimization, complex recursion)


class OfficialStatus(str):
    OFFICIAL = "official"                                # Direct official UNT question from verified NTC database
    OFFICIAL_SAMPLE = "official_sample"                  # Official sample / trial test published by NTC
    OFFICIAL_SPECIFICATION_BASED = "official_spec_based" # Modeled directly on NTC specification criteria
    ORIGINAL_UNTVERSE = "original_untverse"              # Created by UNTverse subject matter experts
    THIRD_PARTY = "third_party"                          # Educational Olympiads / partner collections


class BankQuestion(Base, TimestampMixin):
    __tablename__ = "bank_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid_str: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True, nullable=False)
    
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="RESTRICT"), index=True, nullable=False)
    specification_topic_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("specification_topics.id", ondelete="SET NULL"), index=True, nullable=True)
    topic_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True)
    
    question_type: Mapped[str] = mapped_column(String(50), default="single_choice", nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(5), default=QuestionDifficulty.B, nullable=False, index=True)
    difficulty_score: Mapped[float] = mapped_column(Float, default=0.50, nullable=False)  # 0.00 to 1.00 empirical difficulty
    official_status: Mapped[str] = mapped_column(String(50), default=OfficialStatus.OFFICIAL_SPECIFICATION_BASED, nullable=False, index=True)
    original_language: Mapped[str] = mapped_column(String(10), default="kk", nullable=False)  # kk, ru, en
    
    year: Mapped[int] = mapped_column(Integer, default=2026, nullable=False, index=True)
    estimated_time_seconds: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    maximum_score: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # sha256 of canonical text representation

    subject: Mapped["Subject"] = relationship("Subject", back_populates="bank_questions")
    specification_topic: Mapped[Optional["SpecificationTopic"]] = relationship("SpecificationTopic", back_populates="bank_questions")
    topic: Mapped[Optional["Topic"]] = relationship("Topic")
    
    versions: Mapped[List["QuestionVersion"]] = relationship("QuestionVersion", back_populates="question", cascade="all, delete-orphan", order_by="QuestionVersion.version_number.desc()")
    translations: Mapped[List["QuestionTranslation"]] = relationship("QuestionTranslation", back_populates="question", cascade="all, delete-orphan")
    options: Mapped[List["QuestionBankOption"]] = relationship("QuestionBankOption", back_populates="question", cascade="all, delete-orphan", order_by="QuestionBankOption.order_index")
    provenance_records: Mapped[List["QuestionProvenance"]] = relationship("QuestionProvenance", back_populates="question", cascade="all, delete-orphan")
    solutions: Mapped[List["BankSolution"]] = relationship("BankSolution", back_populates="question", cascade="all, delete-orphan")
    tags: Mapped[List["QuestionTag"]] = relationship("QuestionTag", back_populates="question", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_bank_question_query", "subject_id", "difficulty", "year", "is_active"),
    )


class QuestionVersion(Base, TimestampMixin):
    __tablename__ = "question_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_questions.id", ondelete="CASCADE"), index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    canonical_text: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    question: Mapped["BankQuestion"] = relationship("BankQuestion", back_populates="versions")


class QuestionTranslation(Base, TimestampMixin):
    __tablename__ = "question_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_questions.id", ondelete="CASCADE"), index=True, nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # kk, ru, en
    text: Mapped[str] = mapped_column(Text, nullable=False)
    code_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    translation_source: Mapped[str] = mapped_column(String(50), default="official", nullable=False)  # official, human, ai, hybrid
    translation_status: Mapped[str] = mapped_column(String(30), default="published", nullable=False)  # published, validated, needs_review, draft
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    question: Mapped["BankQuestion"] = relationship("BankQuestion", back_populates="translations")

    __table_args__ = (
        Index("idx_question_translations_locale", "question_id", "locale", unique=True),
    )


class QuestionBankOption(Base, TimestampMixin):
    __tablename__ = "question_bank_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_questions.id", ondelete="CASCADE"), index=True, nullable=False)
    option_key: Mapped[str] = mapped_column(String(10), nullable=False)  # A, B, C, D, E
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    question: Mapped["BankQuestion"] = relationship("BankQuestion", back_populates="options")
    translations: Mapped[List["QuestionBankOptionTranslation"]] = relationship("QuestionBankOptionTranslation", back_populates="option", cascade="all, delete-orphan")


class QuestionBankOptionTranslation(Base, TimestampMixin):
    __tablename__ = "question_bank_option_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    option_id: Mapped[int] = mapped_column(Integer, ForeignKey("question_bank_options.id", ondelete="CASCADE"), index=True, nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # kk, ru, en
    text: Mapped[str] = mapped_column(Text, nullable=False)

    option: Mapped["QuestionBankOption"] = relationship("QuestionBankOption", back_populates="translations")

    __table_args__ = (
        Index("idx_option_translations_locale", "option_id", "locale", unique=True),
    )


class QuestionProvenance(Base, TimestampMixin):
    __tablename__ = "question_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_questions.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id", ondelete="RESTRICT"), index=True, nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_document_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True)
    source_title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_question_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    copyright_status: Mapped[str] = mapped_column(String(50), default="public_educational_use", nullable=False)
    license_type: Mapped[str] = mapped_column(String(50), default="NTC_Public_Sample", nullable=False)
    reuse_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    official_status: Mapped[str] = mapped_column(String(50), default=OfficialStatus.OFFICIAL_SAMPLE, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    question: Mapped["BankQuestion"] = relationship("BankQuestion", back_populates="provenance_records")
    source: Mapped["Source"] = relationship("Source", back_populates="question_provenance_records")


class BankSolution(Base, TimestampMixin):
    __tablename__ = "solutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_questions.id", ondelete="CASCADE"), index=True, nullable=False)
    approach_type: Mapped[str] = mapped_column(String(50), default="standard_analytical", nullable=False)  # standard_analytical, fast_exam_trick, python_script
    complexity: Mapped[Optional[str]] = mapped_column(String(50), default="O(1)", nullable=True)

    question: Mapped["BankQuestion"] = relationship("BankQuestion", back_populates="solutions")
    translations: Mapped[List["BankSolutionTranslation"]] = relationship("BankSolutionTranslation", back_populates="solution", cascade="all, delete-orphan")


class BankSolutionTranslation(Base, TimestampMixin):
    __tablename__ = "solution_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    solution_id: Mapped[int] = mapped_column(Integer, ForeignKey("solutions.id", ondelete="CASCADE"), index=True, nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # kk, ru, en
    step_by_step_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    exam_tip: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    solution: Mapped["BankSolution"] = relationship("BankSolution", back_populates="translations")

    __table_args__ = (
        Index("idx_solution_translations_locale", "solution_id", "locale", unique=True),
    )


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="concept", nullable=False)  # concept, year, algorithm, exam_trap

    questions: Mapped[List["QuestionTag"]] = relationship("QuestionTag", back_populates="tag", cascade="all, delete-orphan")


class QuestionTag(Base, TimestampMixin):
    __tablename__ = "question_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_questions.id", ondelete="CASCADE"), index=True, nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), index=True, nullable=False)

    question: Mapped["BankQuestion"] = relationship("BankQuestion", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="questions")

    __table_args__ = (
        Index("idx_question_tag_unique", "question_id", "tag_id", unique=True),
    )

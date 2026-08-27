from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field


# 1. Current UNT Rules Schemas
class UntStructureDetails(BaseModel):
    total_questions: int
    maximum_score: int
    duration_minutes: int
    duration_formatted: str
    passing_threshold_total: int
    passing_threshold_per_subject: int


class CurrentUntRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exam_year: int
    is_active: bool
    structure: UntStructureDetails
    informatics_specifics: Dict[str, Any]
    subjects_breakdown: Dict[str, Any]
    profile_combinations: Dict[str, Any]
    testing_periods: List[Dict[str, Any]]
    important_deadlines: Dict[str, Any]
    grant_rules_summary: Dict[str, Any]
    official_source_urls: List[str]
    last_verified_at: Optional[str]
    verified_by: str


# 2. Specification & Taxonomy Schemas
class SpecificationTopicResponse(BaseModel):
    id: int
    code: str
    title: str
    learning_objectives: Optional[Dict[str, Any]] = None
    order_index: int


class SpecificationSectionResponse(BaseModel):
    id: int
    code: str
    title: str
    description: Optional[str] = None
    weight_percentage: int
    question_count_est: int
    order_index: int
    topics: List[SpecificationTopicResponse]


class ExamSpecificationResponse(BaseModel):
    id: int
    exam_year: int
    version: str
    title: str
    status: str
    valid_from: Optional[str]
    valid_to: Optional[str]
    total_questions: int
    max_score: int
    source_url: str
    content_hash: str
    sections: List[SpecificationSectionResponse]


# 3. Question Bank Schemas
class QuestionOptionResponse(BaseModel):
    id: int
    option_key: str
    text: str
    is_correct: bool
    order_index: int


class QuestionProvenanceResponse(BaseModel):
    source_title: str
    source_url: str
    official_status: str
    license_type: Optional[str] = None
    reuse_allowed: Optional[bool] = True
    retrieved_at: Optional[str] = None


class QuestionSolutionResponse(BaseModel):
    approach_type: str
    complexity: Optional[str]
    step_by_step_explanation: str
    exam_tip: Optional[str] = None


class BankQuestionResponse(BaseModel):
    id: int
    uuid: str
    text: str
    code_snippet: Optional[str] = None
    explanation: Optional[str] = None
    locale: str
    question_type: str
    difficulty: str
    difficulty_score: float
    official_status: str
    year: int
    maximum_score: int
    estimated_time_seconds: int
    topic_title: Optional[str] = None
    options: List[QuestionOptionResponse]
    provenance: List[QuestionProvenanceResponse]


class BankQuestionDetailResponse(BankQuestionResponse):
    solutions: List[QuestionSolutionResponse] = []


class QuestionListResponse(BaseModel):
    items: List[BankQuestionResponse]
    total: int
    limit: int
    offset: int


# 4. News Schemas
class NewsArticleResponse(BaseModel):
    id: int
    category: str
    importance_score: int
    relevance_score: float
    is_breaking: bool
    published_at: Optional[str]
    last_verified_at: Optional[str]
    canonical_url: str
    source_name: str
    source_authority: str
    title: str
    summary: str
    locale: str


class NewsArticleDetailResponse(NewsArticleResponse):
    content: str
    translation_source: str
    revision_count: int


class NewsListResponse(BaseModel):
    items: List[NewsArticleResponse]
    total: int
    limit: int
    offset: int


class NewsAlertResponse(BaseModel):
    id: int
    title: str
    summary: str
    published_at: Optional[str]
    canonical_url: str
    importance_score: int


# 5. Glossary & QA Schemas
class GlossaryTermResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    concept_key: str
    kk: str
    ru: str
    en: str
    context: Optional[str]
    source: str
    approved: bool


class KazakhQARequest(BaseModel):
    text: str


class KazakhQAResponse(BaseModel):
    is_valid: bool
    quality_score: float
    warnings: List[str]


# 6. Source & Ingestion Admin Schemas
class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    base_url: str
    source_type: str
    authority_level: str
    default_language: str
    is_active: bool
    crawl_frequency_minutes: int
    last_checked_at: Optional[datetime]
    last_success_at: Optional[datetime]


class IngestionRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    job_name: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    items_discovered: int
    items_created: int
    items_updated: int
    items_skipped: int
    items_failed: int
    error_summary: Optional[str]

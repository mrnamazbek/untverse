from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class TopicMasteryItem(BaseModel):
    topic_id: int
    topic_title: str
    topic_slug: str
    color_accent: str
    mastery_percentage: float
    total_answered: int
    correct_count: int


class MistakeItem(BaseModel):
    id: int
    question_id: int
    question_text: str
    question_type: str
    code_snippet: Optional[str] = None
    explanation: Optional[str] = None
    error_count: int
    is_resolved: bool
    last_mistake_at: datetime


class SpacedCardReviewItem(BaseModel):
    card_id: int
    question_id: int
    question_text: str
    code_snippet: Optional[str] = None
    question_type: str
    interval_days: int
    repetition_number: int
    options: List[dict] = []


class SpacedReviewSubmit(BaseModel):
    card_id: int
    rating: int  # 0 to 5 (SM-2 rating: 0=total blackout, 3=pass with effort, 5=perfect)


class StudentAnalyticsDashboard(BaseModel):
    total_study_time_minutes: int
    unt_readiness_score: int  # 0 - 100%
    quizzes_completed_count: int
    coding_tasks_solved_count: int
    average_quiz_accuracy: float
    strongest_topics: List[TopicMasteryItem] = []
    weakest_topics: List[TopicMasteryItem] = []
    all_topic_masteries: List[TopicMasteryItem] = []
    unresolved_mistakes_count: int
    due_reviews_count: int
    recent_activity_days: List[dict] = []  # [{date: '2026-08-27', count: 12}]

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class QuestionOptionBase(BaseModel):
    text: str
    is_correct: bool = False
    explanation: Optional[str] = None
    order_index: int = 0


class QuestionOptionResponse(BaseModel):
    id: int
    text: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class QuestionOptionAdminResponse(QuestionOptionBase):
    id: int
    question_id: int

    model_config = ConfigDict(from_attributes=True)


class QuestionBase(BaseModel):
    text: str
    code_snippet: Optional[str] = None
    explanation: Optional[str] = None
    question_type: str = "single_choice"  # single_choice, multiple_choice, true_false, fill_gap, sql, matching
    difficulty: str = "medium"
    points: int = 1
    order_index: int = 0
    extra_data: Optional[Dict[str, Any]] = None


class QuestionCreate(QuestionBase):
    quiz_id: int
    options: List[QuestionOptionBase] = []


class QuestionResponse(BaseModel):
    id: int
    quiz_id: int
    text: str
    code_snippet: Optional[str] = None
    question_type: str
    difficulty: str
    points: int
    order_index: int
    extra_data: Optional[Dict[str, Any]] = None
    options: List[QuestionOptionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class QuestionDetailResponse(QuestionResponse):
    explanation: Optional[str] = None
    options: List[QuestionOptionAdminResponse] = []


class QuizBase(BaseModel):
    title: str
    description: str
    quiz_type: str = "standard"  # standard, boss_challenge, ranked, unt_mock, daily_training
    time_limit_seconds: int = 600
    passing_score: int = 70
    xp_reward: int = 50
    is_published: bool = True


class QuizCreate(QuizBase):
    topic_id: Optional[int] = None


class QuizListItem(QuizBase):
    id: int
    topic_id: Optional[int] = None
    questions_count: int = 0
    user_best_score: Optional[int] = None
    user_completed: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class QuizResponse(QuizBase):
    id: int
    topic_id: Optional[int] = None
    questions: List[QuestionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class UserAnswerSubmit(BaseModel):
    question_id: int
    selected_option_ids: Optional[List[int]] = None
    text_answer: Optional[str] = None


class QuizSubmitRequest(BaseModel):
    time_spent_seconds: int = 0
    answers: List[UserAnswerSubmit]


class AnswerReview(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    is_correct: bool
    points_awarded: int
    max_points: int
    user_selected_options: Optional[List[int]] = None
    correct_option_ids: List[int] = []
    explanation: Optional[str] = None


class QuizSubmitResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    score: int
    max_score: int
    percentage: float
    passed: bool
    time_spent_seconds: int
    xp_earned: int
    new_total_xp: int
    new_level: int
    leveled_up: bool
    streak_extended: bool
    current_streak: int
    answers_review: List[AnswerReview] = []

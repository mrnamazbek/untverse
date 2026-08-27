from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LessonBase(BaseModel):
    title: str
    slug: str
    content: str
    summary: Optional[str] = None
    order_index: int = 0
    xp_reward: int = 25
    is_published: bool = True


class LessonCreate(LessonBase):
    topic_id: int


class LessonResponse(LessonBase):
    id: int
    topic_id: int
    is_completed_by_user: Optional[bool] = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicBase(BaseModel):
    title: str
    slug: str
    description: str
    icon: Optional[str] = "folder"
    color_accent: str = "blue"
    order_index: int = 0
    est_minutes: int = 30
    xp_reward: int = 100


class TopicCreate(TopicBase):
    course_id: int


class TopicResponse(TopicBase):
    id: int
    course_id: int
    lessons_count: Optional[int] = 0
    quizzes_count: Optional[int] = 0
    coding_tasks_count: Optional[int] = 0
    user_mastery_percentage: Optional[float] = 0.0
    lessons: Optional[List[LessonResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    title: str
    slug: str
    description: str
    icon: Optional[str] = "book"
    is_published: bool = True
    order_index: int = 0


class CourseCreate(CourseBase):
    pass


class CourseResponse(CourseBase):
    id: int
    topics: List[TopicResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LessonCompleteResponse(BaseModel):
    lesson_id: int
    is_completed: bool
    xp_earned: int
    new_total_xp: int
    new_level: int
    leveled_up: bool

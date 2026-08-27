from app.db.base import Base, TimestampMixin
from app.models.user import User, UserProfile, UserRole, RefreshToken
from app.models.course import Course, Topic, Lesson, LessonProgress, StudySession
from app.models.quiz import Quiz, Question, QuestionOption, QuizAttempt, QuizAnswer, QuizType, QuestionType
from app.models.coding import CodingTask, TestCase, CodingSubmission
from app.models.gamification import XpTransaction, Achievement, UserAchievement, DailyMission, UserMission, Streak
from app.models.analytics import TopicMastery, MistakeLog, SpacedRepetitionCard

# Data Platform Extensions
from app.models.sources import (
    Source, SourceDocument, IngestionRun, IngestionItem, SourceAuthorityLevel, IngestionRunStatus
)
from app.models.localization import LocalizationGlossary
from app.models.specification import (
    ExamType, Subject, ExamSpecification, SpecificationSection, SpecificationTopic,
    CurrentUntRule, SpecificationStatus
)
from app.models.news import (
    NewsArticle, NewsTranslation, NewsVersion, NewsSource, NewsCategory, NewsStatus
)
from app.models.question_bank import (
    BankQuestion, QuestionVersion, QuestionTranslation, QuestionBankOption,
    QuestionBankOptionTranslation, QuestionProvenance, BankSolution,
    BankSolutionTranslation, Tag, QuestionTag, QuestionDifficulty, OfficialStatus
)

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "UserProfile",
    "UserRole",
    "RefreshToken",
    "Course",
    "Topic",
    "Lesson",
    "LessonProgress",
    "StudySession",
    "Quiz",
    "Question",
    "QuestionOption",
    "QuizAttempt",
    "QuizAnswer",
    "QuizType",
    "QuestionType",
    "CodingTask",
    "TestCase",
    "CodingSubmission",
    "XpTransaction",
    "Achievement",
    "UserAchievement",
    "DailyMission",
    "UserMission",
    "Streak",
    "TopicMastery",
    "MistakeLog",
    "SpacedRepetitionCard",
    # Data Platform
    "Source",
    "SourceDocument",
    "IngestionRun",
    "IngestionItem",
    "SourceAuthorityLevel",
    "IngestionRunStatus",
    "LocalizationGlossary",
    "ExamType",
    "Subject",
    "ExamSpecification",
    "SpecificationSection",
    "SpecificationTopic",
    "CurrentUntRule",
    "SpecificationStatus",
    "NewsArticle",
    "NewsTranslation",
    "NewsVersion",
    "NewsSource",
    "NewsCategory",
    "NewsStatus",
    "BankQuestion",
    "QuestionVersion",
    "QuestionTranslation",
    "QuestionBankOption",
    "QuestionBankOptionTranslation",
    "QuestionProvenance",
    "BankSolution",
    "BankSolutionTranslation",
    "Tag",
    "QuestionTag",
    "QuestionDifficulty",
    "OfficialStatus",
]

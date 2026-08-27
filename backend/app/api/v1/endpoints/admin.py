from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.v1.deps import require_admin
from app.models.course import Course, Topic, Lesson
from app.models.quiz import Quiz, Question, QuestionOption
from app.models.coding import CodingTask, TestCase
from app.models.user import User, UserProfile
from app.schemas.course import CourseCreate, CourseResponse, TopicCreate, TopicResponse, LessonCreate, LessonResponse
from app.schemas.quiz import QuizCreate, QuizResponse, QuestionCreate, QuestionResponse
from app.schemas.coding import CodingTaskCreate, CodingTaskResponse
from app.schemas.user import UserResponse
from app.core.exceptions import NotFoundException

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/users", response_model=List[UserResponse])
async def admin_list_users(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    res = await db.execute(select(User).options(selectinload(User.profile)).order_by(User.id))
    return list(res.scalars().all())


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_course(course_in: CourseCreate, db: AsyncSession = Depends(get_db)):
    course = Course(**course_in.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return CourseResponse(
        id=course.id,
        title=course.title,
        slug=course.slug,
        description=course.description,
        icon=course.icon,
        is_published=course.is_published,
        order_index=course.order_index,
        topics=[],
        created_at=course.created_at
    )


@router.post("/topics", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_topic(topic_in: TopicCreate, db: AsyncSession = Depends(get_db)):
    topic = Topic(**topic_in.model_dump())
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return TopicResponse(
        id=topic.id,
        course_id=topic.course_id,
        title=topic.title,
        slug=topic.slug,
        description=topic.description,
        icon=topic.icon,
        color_accent=topic.color_accent,
        order_index=topic.order_index,
        est_minutes=topic.est_minutes,
        xp_reward=topic.xp_reward,
        lessons_count=0,
        lessons=[]
    )


@router.post("/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_lesson(lesson_in: LessonCreate, db: AsyncSession = Depends(get_db)):
    lesson = Lesson(**lesson_in.model_dump())
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return LessonResponse(
        id=lesson.id,
        topic_id=lesson.topic_id,
        title=lesson.title,
        slug=lesson.slug,
        content=lesson.content,
        summary=lesson.summary,
        order_index=lesson.order_index,
        xp_reward=lesson.xp_reward,
        is_published=lesson.is_published,
        is_completed_by_user=False,
        created_at=lesson.created_at
    )


@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_quiz(quiz_in: QuizCreate, db: AsyncSession = Depends(get_db)):
    quiz = Quiz(**quiz_in.model_dump())
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)
    return QuizResponse(
        id=quiz.id,
        topic_id=quiz.topic_id,
        title=quiz.title,
        description=quiz.description,
        quiz_type=quiz.quiz_type,
        time_limit_seconds=quiz.time_limit_seconds,
        passing_score=quiz.passing_score,
        xp_reward=quiz.xp_reward,
        is_published=quiz.is_published,
        questions=[]
    )


@router.post("/coding-tasks", response_model=CodingTaskResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_coding_task(task_in: CodingTaskCreate, db: AsyncSession = Depends(get_db)):
    data = task_in.model_dump()
    test_cases_data = data.pop("test_cases", [])
    
    task = CodingTask(**data)
    db.add(task)
    await db.flush()

    for tc_data in test_cases_data:
        tc = TestCase(task_id=task.id, **tc_data)
        db.add(tc)

    await db.commit()
    await db.refresh(task)
    return CodingTaskResponse(
        id=task.id,
        topic_id=task.topic_id,
        title=task.title,
        slug=task.slug,
        description=task.description,
        starter_code=task.starter_code,
        solution_code=task.solution_code,
        difficulty=task.difficulty,
        time_limit_seconds=task.time_limit_seconds,
        memory_limit_mb=task.memory_limit_mb,
        xp_reward=task.xp_reward,
        is_published=task.is_published,
        test_cases=[]
    )

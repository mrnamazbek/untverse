from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, courses, quizzes, coding, gamification, analytics, admin
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Аутентификация"])
api_router.include_router(users.router, prefix="/users", tags=["Пользователи"])
api_router.include_router(courses.router, prefix="/courses", tags=["Курсы и Уроки"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Тесты и Квизы ЕНТ"])
api_router.include_router(coding.router, prefix="/coding", tags=["Задачи по программированию"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["Геймификация"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Аналитика и Интервальное повторение"])
api_router.include_router(admin.router, prefix="/admin", tags=["Администрирование"])

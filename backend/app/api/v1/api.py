from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, courses, quizzes, coding, gamification, analytics, admin,
    unt_knowledge, questions, news, localization, data_admin, search, stream
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

# Data Platform Routes
api_router.include_router(unt_knowledge.router, prefix="/unt", tags=["База знаний и Спецификации ЕНТ/ҰБТ"])
api_router.include_router(questions.router, prefix="/questions", tags=["Банк вопросов Информатики"])
api_router.include_router(news.router, prefix="/news", tags=["Новости и оповещения ЕНТ"])
api_router.include_router(localization.router, prefix="/localization", tags=["Локализация и QA терминологии"])
api_router.include_router(data_admin.router, prefix="/admin/data", tags=["Управление данными и источниками"])
api_router.include_router(search.router, prefix="/search", tags=["Поиск"])
api_router.include_router(stream.router, prefix="/stream", tags=["Потоки данных (SSE / JSONL)"])


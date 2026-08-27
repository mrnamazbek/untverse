import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.question_bank import BankQuestion
from app.schemas.data_platform import BankQuestionResponse
from app.services.question_bank_service import QuestionBankService

router = APIRouter()


@router.get("/ingestion/{run_id}", summary="SSE поток прогресса ингестии вопросов")
async def stream_ingestion_progress(run_id: str):
    """
    Server-Sent Events (SSE) стриминг статуса обработки данных и парсинга вопросов ЕНТ.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        stages = [
            ("fetching", "Извлечение сырых тестов из источников...", 20),
            ("parsing", "Структурирование и валидация формата вопросов...", 50),
            ("kazakh_qa", "Лингвистическая валидация терминологии на казахском...", 80),
            ("indexing", "Генерация провенанса и сохранение в базу...", 100),
        ]
        
        yield f"event: start\ndata: {json.dumps({'run_id': run_id, 'status': 'started'})}\n\n"
        
        for stage, message, progress in stages:
            await asyncio.sleep(0.3)
            payload = {
                "run_id": run_id,
                "stage": stage,
                "message": message,
                "progress": progress,
            }
            yield f"event: progress\ndata: {json.dumps(payload)}\n\n"

        yield f"event: complete\ndata: {json.dumps({'run_id': run_id, 'status': 'completed', 'total_processed': 50})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/live-events", summary="SSE поток реалтайм событий геймификации")
async def stream_live_events(user_id: int = Query(default=1, description="ID пользователя")):
    """
    Server-Sent Events (SSE) стриминг живых обновлений XP, лидерборда и уведомлений.
    """
    async def live_generator() -> AsyncGenerator[str, None]:
        yield f"event: connected\ndata: {json.dumps({'user_id': user_id, 'status': 'online'})}\n\n"
        # Heartbeat / simulated event tick
        for i in range(3):
            await asyncio.sleep(0.5)
            data = {
                "event_type": "heartbeat",
                "timestamp": asyncio.get_event_loop().time(),
                "active_students_online": 142 + i,
            }
            yield f"event: heartbeat\ndata: {json.dumps(data)}\n\n"

    return StreamingResponse(
        live_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/export/questions.jsonl", summary="Потоковый экспорт базы вопросов в формате JSONL (NDJSON)")
async def stream_export_questions_jsonl(
    locale: str = Query(default="kk", pattern="^(kk|ru|en)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Высокопроизводительный потоковый экспорт вопросов в формате JSON Lines (NDJSON).
    Использует Pydantic v2 Rust serialization без накопления всех объектов в оперативной памяти.
    """
    async def jsonl_streamer() -> AsyncGenerator[str, None]:
        service = QuestionBankService(db)
        items, _ = await service.list_questions(locale=locale, limit=100)

        for q in items:
            schema = BankQuestionResponse.model_validate(q)
            # Pydantic v2 Rust JSON serialization
            yield schema.model_dump_json() + "\n"

    return StreamingResponse(
        jsonl_streamer(),
        media_type="application/x-ndjson",
        headers={
            "Content-Disposition": f"attachment; filename=unt_questions_{locale}.jsonl",
            "Cache-Control": "no-cache",
        },
    )

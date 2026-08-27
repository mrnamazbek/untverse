from dataclasses import dataclass
from typing import Callable, Dict, List, Any, Type
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent:
    user_id: int


@dataclass
class QuizCompletedEvent(DomainEvent):
    quiz_id: int
    score: int
    max_score: int
    percentage: float
    time_spent_seconds: int
    correct_count: int
    total_count: int


@dataclass
class LessonCompletedEvent(DomainEvent):
    lesson_id: int
    topic_id: int


@dataclass
class CodingTaskCompletedEvent(DomainEvent):
    task_id: int
    passed_tests: int
    total_tests: int


@dataclass
class DailyLoginEvent(DomainEvent):
    pass


class EventDispatcher:
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: DomainEvent, **kwargs):
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event, **kwargs)
                else:
                    handler(event, **kwargs)
            except Exception as e:
                logger.error(f"Error handling event {event_type.__name__} in {handler.__name__}: {e}", exc_info=True)


dispatcher = EventDispatcher()

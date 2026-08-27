from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TestCaseBase(BaseModel):
    input_data: str
    expected_output: str
    is_hidden: bool = False
    order_index: int = 0
    explanation: Optional[str] = None


class TestCaseResponse(BaseModel):
    id: int
    input_data: str
    expected_output: str
    is_hidden: bool
    order_index: int
    explanation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CodingTaskBase(BaseModel):
    title: str
    slug: str
    description: str
    starter_code: str
    solution_code: Optional[str] = None
    difficulty: str = "medium"  # easy, medium, hard
    time_limit_seconds: float = 2.0
    memory_limit_mb: int = 50
    xp_reward: int = 75
    is_published: bool = True


class CodingTaskCreate(CodingTaskBase):
    topic_id: Optional[int] = None
    test_cases: List[TestCaseBase] = []


class CodingTaskListItem(BaseModel):
    id: int
    topic_id: Optional[int] = None
    title: str
    slug: str
    difficulty: str
    xp_reward: int
    is_solved_by_user: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class CodingTaskResponse(CodingTaskBase):
    id: int
    topic_id: Optional[int] = None
    test_cases: List[TestCaseResponse] = []
    is_solved_by_user: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class CodeRunRequest(BaseModel):
    source_code: str = Field(..., max_length=50000)


class TestCaseResult(BaseModel):
    test_case_id: Optional[int] = None
    input_data: str
    expected_output: str
    actual_output: Optional[str] = None
    passed: bool
    is_hidden: bool
    execution_time_ms: float = 0.0
    error: Optional[str] = None


class CodeRunResponse(BaseModel):
    status: str  # accepted, wrong_answer, runtime_error, timeout, forbidden_syntax
    passed_tests: int
    total_tests: int
    execution_time_ms: float
    error_output: Optional[str] = None
    test_results: List[TestCaseResult] = []
    xp_earned: int = 0
    new_total_xp: int = 0
    new_level: int = 0
    leveled_up: bool = False

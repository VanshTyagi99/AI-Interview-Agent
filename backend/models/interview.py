from typing import Any, Optional

from pydantic import BaseModel, Field


class InterviewRequest(BaseModel):
    sessionId: str = Field(..., min_length=1)
    message: Optional[str] = ""
    candidate: Optional[dict[str, Any]] = None


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    difficulty: Optional[str] = "easy"
    topic: Optional[str] = "general"
    curriculumDay: Optional[int] = None
    feedback: Optional[dict[str, Any]] = None
    result: Optional[dict[str, Any]] = None
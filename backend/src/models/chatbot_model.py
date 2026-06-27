from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User input message describing the coding task",
    )
    thread_id: Optional[str] = None

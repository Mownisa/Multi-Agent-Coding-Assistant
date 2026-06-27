from __future__ import annotations
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class ChatUserRequest(BaseModel):
    """Incoming user request for the chat API."""
    message: str = Field(..., min_length=1, description="User's coding task or question")
    thread_id: Optional[str] = None


class ChatUserResponse(BaseModel):
    """Core chat response produced by the system."""
    thread_id: str
    response: str


class ChatResponse(BaseModel):
    """Standard API response format for chat endpoints."""
    code: int
    status: str
    message: str
    data: Optional[ChatUserResponse] = None
    error: Optional[Any] = None
    request_id: str
    timestamp: str


class ErrorLogPayload(BaseModel):
    """Payload used internally to log errors to the database."""
    function_name: str
    file_name: str
    error_message: str
    timestamp: str
    stack_trace: Optional[str] = None

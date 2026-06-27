"""
Chat Routes (non-streaming)
"""

import uuid
from datetime import datetime
from fastapi import APIRouter

from src.services.chatbot_service import ChatService
from src.repositories.errorLogRepository import ErrorLogRepository
from src.dto.dto import ChatUserRequest, ChatUserResponse, ChatResponse
from src.utils.logger import logger

FILE_NAME = "chatbot_route.py"

router = APIRouter(prefix="/api", tags=["Chat"])
chat_service = ChatService()


@router.post("/code", response_model=ChatResponse)
async def chat(request: ChatUserRequest) -> ChatResponse:
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    try:
        logger.info("Received chat request")

        thread_id = request.thread_id or request_id
        response_text = await chat_service.analyze_message(
            thread_id=thread_id,
            message=request.message,
        )

        return ChatResponse(
            code=200,
            status="success",
            message="Chat processed successfully",
            data=ChatUserResponse(thread_id=thread_id, response=response_text),
            error=None,
            request_id=request_id,
            timestamp=timestamp,
        )

    except Exception as error:
        logger.error("Chat error: %s", error)

        try:
            ErrorLogRepository().log_error(
                request_id=request_id,
                function_name="chat",
                file_name=FILE_NAME,
                error=error,
            )
        except Exception as log_err:
            logger.error("Failed to log error: %s", log_err)

        return ChatResponse(
            code=500,
            status="error",
            message="Internal server error",
            data=None,
            error={"type": type(error).__name__},
            request_id=request_id,
            timestamp=timestamp,
        )

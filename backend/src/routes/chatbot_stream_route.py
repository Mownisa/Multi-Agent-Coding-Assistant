import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.models.chatbot_model import ChatRequest
from src.services.chatbot_stream_service import stream_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Coding Assistant - Streaming"])


@router.post(
    "/agent/auto/stream",
    summary="Invoke Multi-Agent Code Pipeline with live SSE updates",
)
async def auto_code_pipeline_stream(request: ChatRequest):
    """
    Same pipeline as /api/code, but streams Server-Sent Events as each
    node (classify, coder, reviewer, researcher, final) completes.

    Frontend usage: connect with fetch() + ReadableStream (POST body is
    required, so the native EventSource API cannot be used directly).
    """
    return StreamingResponse(
        stream_pipeline(request.message, request.thread_id or "default"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

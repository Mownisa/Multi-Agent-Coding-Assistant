"""
Streams Server-Sent Events as each pipeline node completes, so the
frontend can show live stage cards (classify -> coder -> reviewer ->
researcher -> final) instead of waiting for one big response.
"""

import json
import logging
import traceback

from src.services.chatbot_service import ChatService
from src.utils.error_logger import log_error

logger = logging.getLogger(__name__)


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def stream_pipeline(user_message: str, thread_id: str = "default"):
    try:
        yield _sse_event("start", {"message": "Pipeline started"})

        initial_state = {
            "thread_id": thread_id,
            "message": user_message,
            "action": "",
            "result": "",
            "retries": 0,
        }

        chat_service = ChatService()
        await chat_service._initialize()

        final_output_sent = False

        async for step in chat_service.pipeline.astream(initial_state):
            # Diagnostic: remove or downgrade to debug once you've confirmed
            # the pipeline is stable. This is what tells you exactly what
            # LangGraph handed back on any future failure.
            logger.info("[STREAM] raw step: %r", step)

            for node_name, node_output in step.items():
                if node_output is None:
                    logger.warning(
                        "[STREAM] Node '%s' returned None instead of a dict; skipping update",
                        node_name,
                    )
                    continue

                if not isinstance(node_output, dict):
                    logger.warning(
                        "[STREAM] Node '%s' returned non-dict output (%r); skipping update",
                        node_name, type(node_output),
                    )
                    continue

                if node_name == "final":
                    final_output_sent = True
                    yield _sse_event("final", {
                        "node": "final",
                        "final_output": node_output.get("final_output", ""),
                    })
                else:
                    yield _sse_event("node_update", {
                        "node": node_name,
                        "output": node_output,
                    })

        # Safety net: if the graph completed without ever emitting a "final"
        # step (e.g. a routing edge case), tell the frontend explicitly
        # instead of silently never sending a "final" event.
        if not final_output_sent:
            logger.warning("[STREAM] Pipeline completed without a 'final' node output")
            yield _sse_event("final", {
                "node": "final",
                "final_output": "",
            })

        yield _sse_event("done", {"message": "Pipeline finished"})

    except Exception as exc:
        logger.error("[STREAM] Orchestration failure:\n%s", traceback.format_exc())
        log_error(
            function_name="stream_pipeline",
            file_name="chatbot_stream_service.py",
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
        )
        yield _sse_event("error", {"message": str(exc)})
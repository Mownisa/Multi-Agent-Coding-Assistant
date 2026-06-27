"""
CoderAgent

Stateless agent that generates code from a user requirement (or from
research context handed to it by the pipeline). Uses the LLM fallback
chain (Google Gemini -> Anthropic -> Together AI -> Ollama) under the hood via get_llm().
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.config import get_llm
from src.agents.prompt import CODER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class CoderAgent:
    def __init__(self):
        self.llm = get_llm(max_tokens=1200, temperature=0.2)
        logger.info("[CoderAgent] Created")

    async def run(self, thread_id: str, user_requirement: str) -> str:
        logger.info("[CoderAgent] Processing (thread=%s)", thread_id)

        messages = [
            SystemMessage(content=CODER_SYSTEM_PROMPT),
            HumanMessage(content=user_requirement),
        ]

        response = await self.llm.ainvoke(messages)
        final_code = response.content

        if isinstance(final_code, list):
            final_code = "\n".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in final_code
            )

        logger.info("[CoderAgent] Code generation completed")
        return final_code

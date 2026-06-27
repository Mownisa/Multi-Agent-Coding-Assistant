"""
ResearcherAgent

Performs web research using DuckDuckGo (free, no API key required) to
resolve knowledge gaps about libraries, frameworks, or functions before
handing context back to the CoderAgent.
"""

import logging
import re

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_community.tools import DuckDuckGoSearchRun

from src.agents.config import get_llm
from src.agents.prompt import RESEARCHER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def _get_duckduckgo_tool() -> DuckDuckGoSearchRun:
    """Free web search tool - no API key required."""
    return DuckDuckGoSearchRun(name="duckduckgo_search")


class ResearcherAgent:
    def __init__(self):
        self.llm = get_llm(max_tokens=900, temperature=0.1)
        logger.info("[ResearcherAgent] Created")

    async def run(self, thread_id: str, topic: str) -> str:
        logger.info("[ResearcherAgent] Processing (thread=%s)", thread_id)

        try:
            duckduckgo_tool = _get_duckduckgo_tool()

            research_agent = create_react_agent(
                model=self.llm,
                tools=[duckduckgo_tool],
                prompt=RESEARCHER_SYSTEM_PROMPT,
            )

            execution_config = RunnableConfig(
                configurable={"thread_id": str(thread_id)}
            )

            prompt = f"Research and summarize the topic: {topic}"

            result = await research_agent.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                execution_config,
            )

            raw = result["messages"][-1].content

        except Exception as exc:
            # DuckDuckGo can be flaky (rate limits / network blocks in some
            # cloud environments) - fall back to asking the LLM directly
            # rather than failing the whole pipeline.
            logger.warning(
                "[ResearcherAgent] Search tool unavailable (%s), "
                "falling back to direct LLM knowledge", exc
            )
            response = await self.llm.ainvoke([
                HumanMessage(
                    content=(
                        f"{RESEARCHER_SYSTEM_PROMPT}\n\n"
                        f"(Web search is unavailable right now - answer "
                        f"from your own knowledge instead.)\n\n"
                        f"Topic: {topic}"
                    )
                )
            ])
            raw = response.content

        if isinstance(raw, list):
            raw = "\n".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in raw
            )

        raw = re.sub(r"<thinking>.*?</thinking>", "", raw, flags=re.DOTALL).strip()

        logger.info("[ResearcherAgent] Research completed")
        return raw

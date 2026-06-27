"""
Chat Service - LangGraph Orchestration

Pipeline shape:
  classify -> coder -> reviewer -> (final | researcher -> coder)
  classify -> reviewer (if user submitted code directly)
  classify -> researcher (if user explicitly wants research) -> final

The classifier decides intent. The reviewer can bounce work back to the
researcher (to gather context) before retrying the coder, up to 2 retries.
"""

import traceback
from typing import TypedDict, Literal, Optional

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from src.agents.coder_agent import CoderAgent
from src.agents.reviewer_agent import ReviewerAgent
from src.agents.researcher_agent import ResearcherAgent
from src.agents.config import get_llm
from src.utils.logger import logger
from src.utils.error_logger import log_error


# ------------------------------------------------------------
# STATE
# ------------------------------------------------------------
class State(TypedDict, total=False):
    # core fields, always present from the initial state
    thread_id: str
    message: str
    action: str
    result: str
    retries: int

    # fields added by nodes as the pipeline runs
    original_task: str    # the user's original ask, never overwritten
    last_code: str         # most recent code the coder produced, survives research round-trips
    classification: str
    code: str
    review_feedback: str
    review_decision: str
    research_notes: str
    final_output: str


# ------------------------------------------------------------
# NODE LOGIC
# ------------------------------------------------------------

async def classifier_node(state: State, llm) -> dict:
    prompt = (
        "Decide the user's intent. Reply with only ONE word:\n\n"
        "general_chat -> greeting, small talk, or a general question not about code\n"
        "write_code   -> user wants new code\n"
        "review_code  -> user provided code to review\n"
        "do_research  -> user wants research first\n\n"
        f"User message:\n{state['message']}"
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    action = response.content.strip().lower()

    if action not in {"general_chat", "write_code", "review_code", "do_research"}:
        action = "write_code"

    logger.info("Action selected: %s", action)
    return {
        "action": action,
        "classification": action,    # frontend preview key
        "original_task": state["message"],  # preserved across the whole run
    }


async def general_chat_node(state: State, llm) -> dict:
    logger.info("General chat node running")
    response = await llm.ainvoke([HumanMessage(content=state["message"])])
    reply = response.content.strip()
    return {
        "result": reply,
        "final_output": reply,
    }


async def coder_node(state: State, coder: CoderAgent) -> dict:
    logger.info("CoderAgent running")
    task = state.get("original_task") or state["message"]
    feedback = state.get("review_feedback")
    notes = state.get("research_notes")

    if feedback or notes:
        # This is a retry after a failed review. Be explicit and directive:
        # the model must output a complete, corrected file with every issue
        # actually fixed in the code itself - not described in a comment.
        # Conversational research notes ("you should add blank lines...")
        # otherwise tend to get echoed back as comments instead of applied.
        parts = [
            f"Original task:\n{task}",
        ]
        if feedback:
            parts.append(f"The previous attempt FAILED review for these reasons:\n{feedback}")
        if notes:
            parts.append(f"Relevant guidance:\n{notes}")
        parts.append(
            "Rewrite the code from scratch so that EVERY issue above is "
            "actually fixed in the code itself. Do not describe the fix in "
            "a comment - apply it. Do not leave placeholder lines, trailing "
            "whitespace, or comments that merely narrate what should be "
            "done. Output ONLY the complete, corrected, runnable file."
        )
        prompt = "\n\n".join(parts)
    else:
        prompt = task

    output = await coder.run(state["thread_id"], prompt)
    return {
        "result": output,
        "code": output,       # frontend preview key
        "last_code": output,  # survives any later research round-trip
    }


async def reviewer_node(state: State, reviewer: ReviewerAgent) -> dict:
    logger.info("ReviewerAgent running")
    code = state.get("last_code") or state.get("result") or state.get("message") or ""
    review_result = await reviewer.run(state["thread_id"], code)
    review_result = review_result or ""
    decision = "PASS" if "PASS" in review_result.upper() else "FAIL"
    return {
        "result": review_result,
        "review_feedback": review_result,  # frontend preview key
        "review_decision": decision,       # frontend PASS/FAIL pill
    }


async def researcher_node(state: State, researcher: ResearcherAgent) -> dict:
    logger.info("ResearcherAgent running")
    if state["action"] == "do_research":
        topic = state["message"]
    else:
        # Research the failure, not the raw code blob: feedback is more useful
        # context for "what should I look up" than the code itself.
        topic = state.get("review_feedback") or state.get("last_code") or state.get("result", "")

    context = await researcher.run(state["thread_id"], topic)
    return {
        "result": context,
        "research_notes": context,  # frontend preview key
        "retries": state.get("retries", 0) + 1,
    }


async def final_node(state: State) -> dict:
    # Prefer the actual code artifact over review text or research notes,
    # so the user gets their code back even if the last loop iteration
    # was a research/review step.
    output = state.get("last_code") or state.get("result", "")
    return {"final_output": output}


# ------------------------------------------------------------
# ROUTERS
# ------------------------------------------------------------

def route_classifier(state: State) -> Literal["general_chat", "coder", "reviewer", "researcher"]:
    if state["action"] == "general_chat":
        return "general_chat"
    if state["action"] == "review_code":
        return "reviewer"
    if state["action"] == "do_research":
        return "researcher"
    return "coder"


def route_reviewer(state: State) -> Literal["final", "researcher"]:
    if state.get("review_decision") == "PASS":
        return "final"
    if state.get("retries", 0) >= 2:
        return "final"
    return "researcher"


def route_researcher(state: State) -> Literal["final", "coder"]:
    if state["action"] == "do_research":
        return "final"
    return "coder"


# ------------------------------------------------------------
# GRAPH BUILDER
# ------------------------------------------------------------

def build_graph(coder: CoderAgent, reviewer: ReviewerAgent, researcher: ResearcherAgent, llm, chat_llm):
    graph = StateGraph(State)

    async def classify(state):
        return await classifier_node(state, llm)

    async def chat(state):
        return await general_chat_node(state, chat_llm)

    async def coder_run(state):
        return await coder_node(state, coder)

    async def review(state):
        return await reviewer_node(state, reviewer)

    async def research(state):
        return await researcher_node(state, researcher)

    async def final(state):
        return await final_node(state)

    graph.add_node("classify", classify)
    graph.add_node("general_chat", chat)
    graph.add_node("coder", coder_run)
    graph.add_node("reviewer", review)
    graph.add_node("researcher", research)
    graph.add_node("final", final)

    graph.set_entry_point("classify")

    graph.add_conditional_edges("classify", route_classifier, {
        "general_chat": "general_chat",
        "coder": "coder",
        "reviewer": "reviewer",
        "researcher": "researcher",
    })

    graph.add_edge("general_chat", "final")

    graph.add_edge("coder", "reviewer")

    graph.add_conditional_edges("reviewer", route_reviewer, {
        "final": "final",
        "researcher": "researcher",
    })

    graph.add_conditional_edges("researcher", route_researcher, {
        "final": "final",
        "coder": "coder",
    })

    graph.add_edge("final", END)

    return graph.compile()


# ------------------------------------------------------------
# CHAT SERVICE
# ------------------------------------------------------------

class ChatService:

    def __init__(self):
        self.pipeline = None
        self.initialized = False

    async def _initialize(self):
        if self.initialized:
            return

        coder = CoderAgent()
        reviewer = ReviewerAgent()
        researcher = ResearcherAgent()
        llm = get_llm(max_tokens=20, temperature=0.0)        # classifier: one-word decisions
        chat_llm = get_llm(max_tokens=1024, temperature=0.7)  # general_chat: real replies

        self.pipeline = build_graph(coder, reviewer, researcher, llm, chat_llm)
        self.initialized = True
        logger.info("Pipeline ready")

    async def analyze_message(self, thread_id: str, message: str) -> str:
        try:
            await self._initialize()

            result = await self.pipeline.ainvoke({
                "thread_id": thread_id or "default",
                "message": message,
                "action": "",
                "result": "",
                "retries": 0,
            })

            return result.get("final_output") or result.get("result", "")

        except Exception as error:
            logger.error("ChatService error: %s", error)
            log_error(
                function_name="analyze_message",
                file_name="chatbot_service.py",
                error_message=str(error),
                stack_trace=traceback.format_exc(),
            )
            return "Something went wrong. Please try again."
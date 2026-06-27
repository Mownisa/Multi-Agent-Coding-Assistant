"""
ReviewerAgent

- Lints the generated code with PEP8 tools (pycodestyle + pyflakes)
- Executes the code in a sandboxed subprocess
- Both run IN-PROCESS in this container - no separate MCP subprocess,
  no hardcoded machine-specific paths, works on any cloud host.
- Every run gets a brand-new uniquely-named temp_review.py file under
  runs/ so past runs are never overwritten.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.config import get_llm
from src.agents.prompt import REVIEWER_SYSTEM_PROMPT
from src.agents.code_review_tools import new_review_workspace, lint_code, execute_code

logger = logging.getLogger(__name__)


class ReviewerAgent:
    def __init__(self):
        self.llm = get_llm(max_tokens=500, temperature=0.0)
        logger.info("[ReviewerAgent] Created")

    async def run(self, thread_id: str, code_to_review: str) -> str:
        logger.info("[ReviewerAgent] Reviewing (thread=%s)", thread_id)

        if isinstance(code_to_review, list):
            code_to_review = "\n".join(str(c) for c in code_to_review)

        # Strip markdown code fences if the coder wrapped the output
        code_to_review = _strip_code_fences(code_to_review)

        # Fresh, unique file for THIS run only - never reused/overwritten
        temp_file = new_review_workspace(str(thread_id))
        logger.info("[ReviewerAgent] Writing candidate code to %s", temp_file)

        lint_report = lint_code(code_to_review, temp_file)
        exec_report = await execute_code(code_to_review, temp_file)

        report_text = (
            f"PEP8 LINT REPORT:\n"
            f"  Passed: {lint_report['passed']}\n"
            f"  Issue count: {lint_report['issue_count']}\n"
            f"  Issues: {lint_report['issues']}\n\n"
            f"EXECUTION REPORT:\n"
            f"  Exit code: {exec_report['exit_code']}\n"
            f"  Timed out: {exec_report['timed_out']}\n"
            f"  Stdout: {exec_report['stdout']}\n"
            f"  Stderr: {exec_report['stderr']}\n"
        )

        messages = [
            SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Here is the candidate code:\n\n{code_to_review}\n\n"
                    f"Here are the tool results:\n\n{report_text}\n\n"
                    f"Give your verdict."
                )
            ),
        ]

        response = await self.llm.ainvoke(messages)
        result_text = response.content

        if isinstance(result_text, list):
            result_text = "\n".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in result_text
            )

        logger.info("[ReviewerAgent] Review completed")
        return result_text


def _strip_code_fences(text: str) -> str:
    """Removes ```python / ``` wrapper if the coder included it."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)
    return stripped

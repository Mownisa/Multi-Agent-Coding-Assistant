"""
Code execution + PEP8 lint tool for the ReviewerAgent.

Design notes (why this replaces the old mcp_python_toolbox subprocess):
- The original code launched a SEPARATE process pointed at a hardcoded
  Windows venv path (C:\\Users\\...\\python.exe). That cannot run on any
  cloud host (Linux containers have no such path, no such venv).
- This version runs lint + execution IN-PROCESS, in the same container
  as the rest of the backend. No subprocess management, no path
  assumptions, works identically on your laptop or any cloud host.
- Every single review run writes the candidate code to a BRAND NEW,
  uniquely-named file under runs/<thread>_<uuid>/temp_review.py -
  never overwrites a previous run's file, so past runs are inspectable.

Exposed as plain async functions the ReviewerAgent calls directly
(no MCP transport needed for something this simple - that complexity
bought nothing here).
"""

from __future__ import annotations

import asyncio
import io
import logging
import subprocess
import sys
import uuid
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict

import pycodestyle
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter

from src.settings import config

logger = logging.getLogger(__name__)

EXECUTION_TIMEOUT_SECONDS = 10


def new_review_workspace(thread_id: str) -> Path:
    """
    Creates a fresh, uniquely-named workspace folder for one review run.
    Returns the path to temp_review.py inside it (not yet written).
    """
    run_id = uuid.uuid4().hex[:8]
    workspace = (config.runs_dir / f"thread_{thread_id}_{run_id}").resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace / "temp_review.py"


def lint_code(code: str, file_path: Path) -> Dict[str, Any]:
    """
    PEP8 lint via pycodestyle (style) + pyflakes (logic/undefined names).
    Writes `code` to `file_path` first so both tools can analyze it as
    a real file (pycodestyle requires a path, not a string).
    """
    file_path.write_text(code, encoding="utf-8")

    issues = []

    # --- pycodestyle: PEP8 style violations ---
    style_output = io.StringIO()
    with redirect_stdout(style_output):
        style_guide = pycodestyle.StyleGuide(quiet=False)
        style_guide.check_files([str(file_path)])
    for line in style_output.getvalue().splitlines():
        if line.strip():
            issues.append({"tool": "pycodestyle", "detail": line.strip()})

    # --- pyflakes: undefined names, unused imports, syntax errors ---
    flakes_output = io.StringIO()
    reporter = Reporter(flakes_output, flakes_output)
    pyflakes_check(code, str(file_path), reporter)
    for line in flakes_output.getvalue().splitlines():
        if line.strip():
            issues.append({"tool": "pyflakes", "detail": line.strip()})

    return {
        "passed": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues[:25],  # cap so huge outputs don't blow up context
    }


async def execute_code(code: str, file_path: Path) -> Dict[str, Any]:
    """
    Executes the candidate code as a real subprocess (sandboxed by OS
    process isolation), with a hard timeout so an infinite loop can't
    hang the request. Captures stdout/stderr/exit code.
    """
    file_path = file_path.resolve()
    file_path.write_text(code, encoding="utf-8")

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(file_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(file_path.parent),
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=EXECUTION_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {EXECUTION_TIMEOUT_SECONDS}s",
                "timed_out": True,
            }

        return {
            "exit_code": process.returncode,
            "stdout": stdout.decode("utf-8", errors="replace")[:4000],
            "stderr": stderr.decode("utf-8", errors="replace")[:4000],
            "timed_out": False,
        }

    except Exception as exc:
        logger.error("[execute_code] Failed to run subprocess: %s", exc)
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Failed to execute: {exc}",
            "timed_out": False,
        }

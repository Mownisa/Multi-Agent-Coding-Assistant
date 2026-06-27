from __future__ import annotations
import logging

from src.repositories.Database import Database
from src.repositories.user_repository import save_error_log

logger = logging.getLogger(__name__)


def log_error(
    function_name: str,
    file_name: str,
    error_message: str,
    stack_trace: str | None = None,
) -> None:
    db = None
    try:
        db = Database().get_session()
        save_error_log(
            db=db,
            function_name=function_name,
            file_name=file_name,
            error_message=error_message,
            stack_trace=stack_trace,
        )
    except Exception as e:
        logger.error("log_error failed: %s", e)
    finally:
        if db is not None:
            db.close()

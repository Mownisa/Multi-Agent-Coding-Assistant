from __future__ import annotations
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from src.repositories.schema.schema import ErrorLogger

logger = logging.getLogger(__name__)
FILE_NAME = "user_repository.py"


def save_error_log(
    db: Session,
    function_name: str,
    file_name: str,
    error_message: str,
    stack_trace: str | None = None,
) -> None:
    try:
        log = ErrorLogger(
            function_name=function_name,
            file_name=file_name,
            error_message=error_message,
            stack_trace=stack_trace,
            created_at=datetime.utcnow(),
            created_by="system",
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error("Failed to save error log: %s", e)
        db.rollback()

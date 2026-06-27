import logging

from src.repositories.Database import Database
from src.repositories.user_repository import save_error_log

logger = logging.getLogger(__name__)


class ErrorLogRepository:
    def __init__(self, db=None):
        self.db = db or Database().get_session()

    def log_error(
        self,
        request_id: str,
        function_name: str,
        file_name: str,
        error: Exception,
        stack_trace: str | None = None,
    ) -> None:
        try:
            save_error_log(
                db=self.db,
                function_name=function_name,
                file_name=file_name,
                error_message=str(error),
                stack_trace=stack_trace,
            )
        except Exception as e:
            logger.error("ErrorLogRepository failed: %s", e)
        finally:
            self.db.close()

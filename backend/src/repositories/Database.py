from __future__ import annotations
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.settings import config
import src.repositories.schema.schema  # noqa: F401 (registers models)

logger = logging.getLogger(__name__)


class Database:
    """
    Singleton SQLAlchemy engine and session factory.
    Uses SQLite by default (DATABASE_URL env var) - zero setup, file
    based, works the same locally and on any cloud host. Swap to
    Postgres later by just changing DATABASE_URL.
    """

    _instance: "Database | None" = None

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self) -> None:
        connect_args = {}
        if config.database_url.startswith("sqlite"):
            # Needed because FastAPI may use the connection across threads
            connect_args = {"check_same_thread": False}

        self.engine = create_engine(
            config.database_url,
            pool_pre_ping=True,
            echo=config.debug,
            connect_args=connect_args,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Database engine initialized: %s", config.database_url)

    def test_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test passed.")
            return True
        except Exception as e:
            logger.error("Database connection test failed: %s", e)
            return False

    def get_session(self) -> Session:
        return self.SessionLocal()

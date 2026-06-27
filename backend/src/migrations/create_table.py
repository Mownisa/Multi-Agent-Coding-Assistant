"""
Migration - Create database tables if they do not exist.
"""
from __future__ import annotations
import logging
from sqlalchemy import inspect

from src.repositories.Database import Database
from src.repositories.schema.schema import Base

logger = logging.getLogger(__name__)


class Migration:
    """Handles database table creation using the shared database engine."""

    def __init__(self) -> None:
        db = Database()
        self.engine = db.engine
        self.inspector = inspect(self.engine)

    def create_tables(self) -> None:
        logger.info("Starting database table creation")
        try:
            Base.metadata.create_all(bind=self.engine)
            tables = self.inspector.get_table_names()
            if tables:
                logger.info("Database tables are ready:")
                for table in tables:
                    logger.info(" - %s", table)
            else:
                logger.info("No tables found in the database")
        except Exception as error:
            logger.error("Failed to create database tables: %s", error)
            raise

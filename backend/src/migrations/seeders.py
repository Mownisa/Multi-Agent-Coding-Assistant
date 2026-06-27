"""
seeders.py
Seeds a default user if the users table is empty.
"""

from __future__ import annotations
import logging
from datetime import datetime

from src.repositories.Database import Database
from src.repositories.schema.schema import User

logger = logging.getLogger(__name__)


class Seeder:
    def __init__(self) -> None:
        self.db = Database()

    def seed_data(self) -> None:
        session = self.db.get_session()
        try:
            self._seed_users(session)
            session.commit()
            logger.info("Seeding completed successfully.")
        except Exception as e:
            session.rollback()
            logger.error("Seeding failed: %s", e)
        finally:
            session.close()

    def _seed_users(self, session) -> None:
        if session.query(User).count() > 0:
            logger.info("Users already seeded - skipping.")
            return

        default_user = User(
            username="system",
            created_at=datetime.utcnow(),
            created_by="seeder",
        )
        session.add(default_user)
        session.flush()
        logger.info("Seeded default user.")

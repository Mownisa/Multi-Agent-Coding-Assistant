"""
schema.py

Tables:
- users          : lightweight user identity / session reference
- error_loggers  : centralized error logging
"""

from __future__ import annotations
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id    = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String(150), unique=True, nullable=True)
    email      = Column(String(150), unique=True, nullable=True)
    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100), default="system", nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    updated_by = Column(String(100), default="system", nullable=True)


class ErrorLogger(Base):
    __tablename__ = "error_loggers"

    error_id      = Column(Integer, primary_key=True, autoincrement=True)
    function_name = Column(String(150), nullable=False)
    file_name     = Column(String(150), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace   = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by    = Column(String(100), default="system", nullable=False)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    updated_by    = Column(String(100), default="system", nullable=True)

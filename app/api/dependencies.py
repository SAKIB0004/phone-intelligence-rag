from typing import Generator
from app.database.connection import SessionLocal
from app.rag.engine import SamsungChatEngine
from app.agents.workflow import SamsungReviewOrchestrator
from sqlalchemy.orm import Session

# Singleton instances for API lifecycles
_chat_engine: SamsungChatEngine | None = None
_orchestrator: SamsungReviewOrchestrator | None = None


def get_db_session():
    """FastAPI dependency for thread-safe database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_chat_engine():
    """Dependency providing the singleton RAG conversational engine."""
    global _chat_engine
    if _chat_engine is None:
        _chat_engine = SamsungChatEngine()
    return _chat_engine


def get_review_orchestrator():
    """Dependency providing the singleton Multi-Agent orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SamsungReviewOrchestrator()
    return _orchestrator
from app.database.connection import SessionLocal
from app.rag.engine import SamsungChatEngine

_chat_engine: SamsungChatEngine | None = None


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

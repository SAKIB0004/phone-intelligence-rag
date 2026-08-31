from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from app.api.dependencies import get_chat_engine
from app.api.schemas import ChatRequest, ChatResponse
from app.rag.engine import SamsungChatEngine

router = APIRouter(prefix="/chat", tags=["Conversational RAG Chatbot"])


@router.post(
    "/query",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about Samsung phones (JSON response)",
)
def chat_query(
    payload: ChatRequest,
    engine: SamsungChatEngine = Depends(get_chat_engine),
):
    """Executes a complete RAG retrieval and returns the synthesized answer in a single JSON payload."""
    if payload.reset_history:
        engine.reset_chat()

    full_response = "".join(list(engine.answer_query_stream(payload.query)))
    return ChatResponse(query=payload.query, response=full_response)


@router.post(
    "/stream",
    status_code=status.HTTP_200_OK,
    summary="Ask a question about Samsung phones (Server-Sent Event token stream)",
)
def chat_stream(
    payload: ChatRequest,
    engine: SamsungChatEngine = Depends(get_chat_engine),
):
    """Streams the RAG response token-by-token in real time using text/event-stream."""
    if payload.reset_history:
        engine.reset_chat()

    def event_generator():
        for token in engine.answer_query_stream(payload.query):
            # Send raw token chunks
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
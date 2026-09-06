from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_chat_engine
from app.api.schemas import ChatRequest, ChatResponse
from app.rag.engine import SamsungChatEngine


router = APIRouter(prefix="/chat", tags=["Conversational RAG Chatbot"])


def _query(payload: ChatRequest, engine: SamsungChatEngine) -> ChatResponse:
	_reset_history(payload, engine)
	response = "".join(engine.answer_query_stream(payload.query))
	return ChatResponse(query=payload.query, response=response)


def _reset_history(payload: ChatRequest, engine: SamsungChatEngine) -> None:
	if payload.reset_history:
		engine.reset_chat()


@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_query(
	payload: ChatRequest,
	engine: SamsungChatEngine = Depends(get_chat_engine),
):
	return _query(payload, engine)


@router.post("/stream", status_code=status.HTTP_200_OK)
def chat_stream(
	payload: ChatRequest,
	engine: SamsungChatEngine = Depends(get_chat_engine),
):
	_reset_history(payload, engine)
	return StreamingResponse(engine.answer_query_stream(payload.query), media_type="text/plain")

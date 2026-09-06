from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_chat_engine, get_db_session
from app.api.schemas import HealthResponse
from app.api.v1.routes import agents, chat, phones, scraper
from app.database.connection import init_db
from app.database.crud import get_all_phones
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(_application: FastAPI):
	logger.info("Initializing application database and vector indices...")
	init_db()
	get_chat_engine()
	logger.info("Samsung AI API server startup complete.")
	yield
	logger.info("Shutting down Samsung AI API server.")


app = FastAPI(
	title="Samsung Phone Intelligence API",
	description=(
		"Production API powering automated specification scraping, "
		"conversational RAG querying via Groq, and multi-agent product reviews via LangChain."
	),
	version="1.0.0",
	lifespan=lifespan,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(phones.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(scraper.router, prefix="/api/v1")


@app.get(
	"/health",
	response_model=HealthResponse,
	status_code=status.HTTP_200_OK,
	tags=["System"],
	summary="System health and database connectivity check",
)
def health_check(db: Session = Depends(get_db_session)):
	db_connected = False
	phone_count = 0
	try:
		db.execute(text("SELECT 1"))
		db_connected = True
		phone_count = len(get_all_phones(db))
	except Exception as error:
		logger.error(f"Database health check failure: {error}")

	return HealthResponse(
		status="healthy" if db_connected else "degraded",
		database_connected=db_connected,
		total_indexed_phones=phone_count,
		timestamp=datetime.now(timezone.utc),
	)


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)

# Samsung Phone Query and Review System

An API service for collecting Samsung phone specifications from GSMArena, storing structured records in PostgreSQL, indexing those records in ChromaDB, answering specification questions with RAG, and generating grounded phone reviews with a LangGraph workflow.

## Objectives

- Scrape Samsung phone specification pages from GSMArena.
- Parse, clean, validate, and persist phone records in PostgreSQL.
- Build a ChromaDB vector index from the validated PostgreSQL records.
- Answer phone questions with retrieved database context and Groq.
- Generate technical dossiers and reviews through a two-node LangGraph workflow.
- Expose the functionality through a versioned FastAPI application.

## Architecture

### Scraping and indexing pipeline

```text
GSMArena HTTP response
        |
        v
HTML parser (app/scraper/parser.py)
        |
        v
Cleaner (app/scraper/cleaners.py)
        |
        v
Validator (app/scraper/validator.py)
        |
        v
PostgreSQL
        |
        v
ChromaDB vector index
```

`app/scraper/pipeline.py` coordinates this flow. PostgreSQL is the source of structured phone records. The RAG retriever indexes those records and does not scrape independently.

### RAG chat flow

```text
Chat request
    |
    v
ChromaDB retriever + conversation memory
    |
    v
Grounded prompt
    |
    v
Groq streaming client
    |
    v
Chat response
```

### Multi-agent review flow

```text
Review request
    |
    v
Specification Agent
    |
    v
Verified technical dossier
    |
    v
Review Agent
    |
    v
Final review
```

The workflow in `app/agents/workflow.py` is a compiled LangGraph:

```text
START -> specification_agent -> review_agent -> END
```

When `phone_name` is supplied, the Specification Agent directly uses the existing PostgreSQL-backed tool for that model. Requests without an explicit model can use the query-based tool-routing path.

## Key Features

- GSMArena scraping with a persistent `requests.Session`.
- Retry and exponential backoff through Tenacity.
- Parsing with BeautifulSoup and LXML.
- Text and numeric normalization for scraped records.
- Validation of required fields, source URLs, and numeric ranges.
- SQLAlchemy models and PostgreSQL upserts.
- ChromaDB persistence with Sentence Transformer embeddings.
- Semantic retrieval and a SQL-based highest-battery query.
- Groq-powered streaming responses.
- Bounded conversation memory with reset support.
- LangChain tools for phone lookup and available-phone listing.
- LangGraph specification-to-review orchestration.
- FastAPI OpenAPI, Swagger UI, ReDoc, CORS, and health check support.

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.10+ |
| API | FastAPI, Uvicorn |
| HTTP scraping | Requests, Tenacity |
| HTML parsing | BeautifulSoup4, LXML |
| Structured database | PostgreSQL, SQLAlchemy, psycopg2-binary |
| Vector database | ChromaDB |
| Embeddings | ChromaDB Sentence Transformer embedding function |
| LLM provider | Groq |
| Agent tools/prompts | LangChain Core, LangChain Groq |
| Agent orchestration | LangGraph |
| Configuration | Pydantic Settings, python-dotenv |
| Tests | Pytest, FastAPI TestClient, HTTPX |

## Repository Structure

Generated caches, virtual environments, Git metadata, and local vector/database artifacts are intentionally omitted from this tree.

```text
samsung-scraper/
├── app/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── prompts.py       # Agent prompts and review templates
│   │   ├── review_agent.py  # Generates grounded reviews
│   │   ├── spec_agent.py    # Retrieves verified phone specifications
│   │   ├── state.py         # Shared LangGraph AgentState definition
│   │   ├── tools.py         # PostgreSQL and retriever-backed tools
│   │   └── workflow.py      # Compiled specification-to-review graph
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py  # Database and chat-engine dependencies
│   │   ├── schemas.py       # Pydantic API request/response models
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routes/
│   │           ├── __init__.py
│   │           ├── agents.py # Multi-agent review endpoints
│   │           ├── chat.py   # RAG chat endpoints
│   │           ├── phones.py # Phone catalog endpoints
│   │           └── scraper.py# Scraping pipeline endpoint
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py      # Environment-backed settings
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py    # SQLAlchemy engine and sessions
│   │   ├── crud.py          # Phone upsert and list operations
│   │   └── models.py        # PhoneSpec ORM model
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py    # ChromaDB embedding factory
│   │   ├── engine.py        # Conversational RAG orchestration
│   │   ├── groq_client.py   # Groq completion streaming client
│   │   ├── memory.py        # Conversation history
│   │   ├── prompts.py       # RAG grounding prompts
│   │   └── retriever.py     # PostgreSQL-to-Chroma indexing and retrieval
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── cleaners.py      # Text and numeric normalization
│   │   ├── parser.py        # GSMArena HTML extraction
│   │   ├── pipeline.py      # Scrape, validate, store, and index flow
│   │   ├── scraper.py       # HTTP fetching and target URLs
│   │   └── validator.py     # Pre-persistence record validation
│   └── utils/
│       ├── __init__.py
│       └── logger.py        # Application logger
├── data/
│   ├── chroma_db/           # Local ChromaDB persistence
│   ├── processed/           # Generated processed JSON snapshots
│   └── raw/                 # Reserved raw-data directory
├── tests/
│   ├── __init__.py
│   └── test_api.py          # FastAPI integration tests
├── .env                     # Local environment variables; not committed
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── run.py                   # FastAPI application and direct entry point
```

## Installation

### Requirements

- Python 3.10 or newer.
- PostgreSQL running locally or remotely.
- A Groq API key.
- Network access to GSMArena when running the scraper.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install the declared dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Environment Configuration

Create `.env` in the project root. The application reads these values through `app/config/settings.py`.

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/samsung_db
USER_AGENT=Mozilla/5.0
REQUEST_DELAY_MIN=2.0
REQUEST_DELAY_MAX=4.0
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=data/chroma_db
```

Do not commit `.env` or expose `GROQ_API_KEY` in source control.

## Database Setup

Create the PostgreSQL database before starting the application:

```sql
CREATE DATABASE samsung_db;
```

On startup, `run.py` calls `init_db()`, which creates the SQLAlchemy tables if they do not exist.

The `samsung_phones` table is represented by `app.database.models.PhoneSpec` and stores:

- Model identity and source URL.
- Release date, dimensions, weight, and display data.
- Operating system, chipset, CPU, GPU, and storage/RAM.
- Main and selfie camera fields.
- Battery capacity, charging speed, and price.
- Raw parsed specifications as JSON.
- Creation and update timestamps.

## Running the Application

Start directly with Python:

```powershell
python run.py
```

Or start Uvicorn with reload enabled:

```powershell
python -m uvicorn run:app --reload
```

The service listens on `http://127.0.0.1:8000` by default.

Interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Reference

All business routes are registered under `/api/v1`.

### Health

```text
GET /health
```

Checks database connectivity and returns the number of stored phones.

### Phone catalog

```text
GET /api/v1/phones/
GET /api/v1/phones/{model_name}
```

The list endpoint accepts `skip` and `limit` query parameters. The model endpoint performs a case-insensitive partial match.

Example:

```powershell
curl "http://127.0.0.1:8000/api/v1/phones/?limit=5"
curl "http://127.0.0.1:8000/api/v1/phones/Galaxy%20S24"
```

### RAG chat

```text
POST /api/v1/chat/query
POST /api/v1/chat/stream
```

Request body:

```json
{
  "query": "What is the chipset in the Galaxy S24?",
  "reset_history": false
}
```

`/query` returns JSON. `/stream` returns a plain-text token stream. Set `reset_history` to `true` to clear the singleton chat engine's conversation memory before answering.

### Multi-agent review

```text
POST /api/v1/agents/review
POST /api/v1/agents/review/stream
```

Explicit phone review:

```json
{
  "phone_name": "Galaxy S24",
  "review_focus": "General Consumer & Performance Review"
}
```

The response contains `technical_dossier` and `final_review`. A request may alternatively provide `query` for the specification agent to interpret:

```json
{
  "query": "Compare Galaxy S24 and Galaxy S23 performance",
  "review_focus": "Performance and battery"
}
```

### Scraper

```text
POST /api/v1/scraper/run
```

This triggers the existing scrape pipeline. Each scraped record is parsed, cleaned, validated, upserted into PostgreSQL, included in `data/processed/samsung_phones.json`, and then indexed into ChromaDB from PostgreSQL.

## RAG and Agent Details

The retriever creates a ChromaDB collection named `samsung_phones`. It converts PostgreSQL `PhoneSpec` rows into searchable specification documents and supports:

- Semantic ChromaDB retrieval for natural-language questions.
- Structured PostgreSQL matching for phone-name lookups.
- SQL ranking for best/highest/longest battery queries.
- Comparison retrieval for multiple phone names.

The chat engine adds retrieved context to a grounding prompt, includes recent conversation messages, and streams the Groq response. The agent tools use the existing database session and retriever rather than creating a second database or vector implementation.

## Testing

Run the available test suite from the repository root:

```powershell
pytest -q
```

The repository currently contains API integration coverage in `tests/test_api.py`. No `pyproject.toml`, Makefile, Dockerfile, or dedicated lint/format configuration is present, so no additional project-defined lint or formatting command is documented.

## Data and Generated Files

- `data/processed/samsung_phones.json` is generated by the scraper pipeline.
- `data/chroma_db/` contains persistent local ChromaDB state.
- `data/raw/` is available for raw scrape data but is not populated by the current pipeline.
- `.env`, caches, virtual environments, and local database/vector artifacts should remain uncommitted.

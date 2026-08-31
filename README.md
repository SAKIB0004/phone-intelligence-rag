# Samsung Mobile Intelligence & Multi-Agent Review System

A full-stack, AI-powered Samsung smartphone intelligence platform that combines web scraping, structured relational storage, vector search, conversational RAG, multi-agent review generation, and REST APIs.

The system collects Samsung smartphone specifications from GSMArena, stores normalized data in PostgreSQL, creates a semantic vector index with ChromaDB, and uses Groq-hosted LLMs for conversational question answering and multi-agent technical review generation.

---

## System Architecture

```text
                         +----------------------------------+
                         |       GSMArena Web Scraper       |
                         |  Requests + BeautifulSoup + LXML |
                         |       Tenacity Retry Logic       |
                         +----------------+-----------------+
                                          |
                                          v
                         +----------------+-----------------+
                         |       PostgreSQL Database        |
                         |       SQLAlchemy ORM + CRUD      |
                         |  Structured Specs + Raw JSON     |
                         +-------------+--------------------+
                                       |
                       +---------------+----------------+
                       |                                |
                       v                                v
          +-------------------------+       +-------------------------+
          |       ChromaDB          |       |   LangChain DB Tools    |
          |   Vector Search Layer   |       |   Exact SQL Lookup      |
          | Sentence Transformers   |       |      ILIKE Search       |
          +------------+------------+       +------------+------------+
                       |                                 |
                       v                                 v
          +-------------------------+       +-------------------------+
          | Conversational RAG      |       |   Multi-Agent System    |
          | Groq LLM                |       |                         |
          | Context Retrieval       |       | 1. Spec Retrieval      |
          | Conversation Memory     |       | 2. Review Generation   |
          | Token Streaming         |       | Sequential Workflow     |
          +------------+------------+       +------------+------------+
                       |                                 |
                       +-----------------+---------------+
                                         |
                                         v
                         +---------------+----------------+
                         |          FastAPI API           |
                         |                                |
                         | Catalog | RAG | Agents | SSE  |
                         | Swagger / OpenAPI / ReDoc      |
                         +--------------------------------+
```

---

## Key Features

### 1. Resilient Web Scraping

- Extracts Samsung smartphone specifications from GSMArena.
- Uses a persistent `requests.Session`.
- Configurable request delays to reduce request pressure.
- Exponential-backoff retries with `tenacity`.
- Handles HTTP failures and rate limiting.
- Parses and normalizes values such as:
  - Battery capacity
  - Display size
  - Weight
  - Chipset
  - Camera specifications
  - Charging speed
  - Price

### 2. Dual Data Storage

The project uses PostgreSQL and ChromaDB for different purposes.

#### PostgreSQL

Stores authoritative structured records:

- Device identity
- Release information
- Dimensions and weight
- Display specifications
- Operating system
- Chipset, CPU, and GPU
- RAM and storage
- Camera specifications
- Battery and charging
- Price
- Raw specification JSON
- Timestamps

#### ChromaDB

Stores vector representations of phone specification profiles for semantic retrieval.

This enables natural-language queries such as:

```text
Which phone has the best battery capacity?
```

or:

```text
Which Samsung phone is suitable for gaming?
```

### 3. Conversational RAG

The RAG pipeline combines:

- PostgreSQL structured data
- ChromaDB semantic retrieval
- Sentence-Transformer embeddings
- Groq LLM inference
- Multi-turn conversation memory
- Streaming responses

The system is instructed to answer from retrieved database context and avoid unsupported claims.

### 4. Multi-Agent Review System

The review workflow consists of two specialized agents:

#### Spec Retrieval Agent

Responsible for:

- Identifying the requested phone
- Calling database lookup tools
- Retrieving exact specifications
- Building a verified technical dossier

#### Review Generation Agent

Responsible for:

- Consuming the technical dossier
- Producing a balanced editorial review
- Discussing strengths and weaknesses
- Focusing on the requested review criteria
- Streaming the generated review

### 5. FastAPI REST Service

Provides:

- Phone catalog APIs
- Individual specification lookup
- Synchronous RAG responses
- Streaming RAG responses
- Multi-agent review generation
- Streaming review generation
- Swagger/OpenAPI documentation

---

# Project Structure

```text
samsung-phone-scraper/
│
├── app/
│   │
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── cleaners.py          # Value parsing and normalization
│   │   ├── parser.py            # GSMArena HTML extraction
│   │   └── scraper.py           # HTTP session and scraping logic
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py        # SQLAlchemy engine/session management
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   └── crud.py              # Insert, update and query operations
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── prompts.py           # RAG system prompts
│   │   ├── retriever.py         # SQL + ChromaDB retrieval
│   │   ├── groq_client.py       # Groq LLM client and streaming
│   │   └── engine.py            # Conversational RAG manager
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── prompts.py           # Agent prompts
│   │   ├── tools.py             # LangChain database tools
│   │   ├── spec_agent.py        # Technical specification agent
│   │   ├── review_agent.py      # Editorial review agent
│   │   └── workflow.py          # Multi-agent workflow orchestration
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── dependencies.py      # FastAPI dependency injection
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── phones.py        # Phone catalog endpoints
│   │       ├── chat.py          # Conversational RAG endpoints
│   │       └── agents.py        # Multi-agent review endpoints
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Application configuration
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py             # Logging configuration
│
├── data/
│   ├── raw/                      # Raw scraping cache
│   ├── processed/                # Exported JSON snapshots
│   └── chroma_db/                # Persistent ChromaDB storage
│
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py           # Scraper tests
│   ├── test_parser.py            # Parser tests
│   ├── test_database.py          # Database tests
│   ├── test_rag.py               # RAG tests
│   ├── test_agents.py             # Agent workflow tests
│   └── test_api.py                # API integration tests
│
├── .env                          # Environment variables
├── .gitignore
├── requirements.txt
├── main.py                       # Scraper pipeline entry point
├── chat.py                       # Interactive RAG CLI
├── review_cli.py                 # Multi-agent review CLI
├── server.py                     # FastAPI application entry point
└── README.md
```

---

# Technology Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Web Scraping** | Requests, BeautifulSoup4, LXML, Tenacity |
| **Relational Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Database Driver** | Psycopg2 |
| **Vector Database** | ChromaDB |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **LLM Provider** | Groq API |
| **LLM Model** | `llama-3.3-70b-versatile` |
| **Agent Framework** | LangChain |
| **API Framework** | FastAPI |
| **Validation** | Pydantic v2 |
| **ASGI Server** | Uvicorn |
| **Testing** | Pytest, HTTPX |

---

# Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/samsung-phone-scraper.git
cd samsung-phone-scraper
```

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file in the project root.

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/samsung_db

USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36

REQUEST_DELAY_MIN=2.0
REQUEST_DELAY_MAX=4.0
TARGET_PHONE_COUNT=15

GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=data/chroma_db
```

> Never commit `.env` or API keys to GitHub. Add `.env` to `.gitignore`.

---

# PostgreSQL Setup

Make sure PostgreSQL is running.

Create the database:

```sql
CREATE DATABASE samsung_db;
```

The application will use the configured `DATABASE_URL` to connect to PostgreSQL.

---

# Usage

## Step 1 — Scrape Samsung Phone Specifications

Run:

```bash
python main.py
```

The scraper will:

1. Discover or use the configured target phone URLs.
2. Fetch GSMArena pages.
3. Parse phone specifications.
4. Clean and normalize extracted values.
5. Upsert records into PostgreSQL.
6. Export the processed dataset to:

```text
data/processed/samsung_phones.json
```

---

## Step 2 — Run the Conversational RAG Chatbot

Start the CLI:

```bash
python chat.py
```

Example:

```text
You: What are the camera specifications of the Galaxy S23?

Assistant:
...
```

Other example queries:

```text
What is the screen size of the Galaxy S22?

Which Samsung phone has the highest battery capacity?

Compare the Galaxy S23 and Galaxy S22 in terms of performance.

What chipset does the Galaxy S24 use?

Which phone has the fastest charging?
```

Available CLI commands:

```text
exit
quit
clear
```

`clear` resets the conversation memory.

---

# Step 3 — Run the Multi-Agent Review System

Start:

```bash
python review_cli.py
```

The workflow is:

```text
User Request
     |
     v
Spec Retrieval Agent
     |
     v
Database Tool Calling
     |
     v
Verified Technical Dossier
     |
     v
Review Generation Agent
     |
     v
Editorial Review
```

Example review request:

```text
Phone:
Galaxy S24

Focus:
Compact ergonomics, battery endurance, and thermal behavior
```

---

# Step 4 — Run the FastAPI Server

Start the server:

```bash
python server.py
```

Or:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

```text
http://localhost:8000
```

### API Documentation

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Health check:

```text
http://localhost:8000/health
```

---

# API Reference

## Phone Catalog

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/phones/` | Return stored Samsung phones |
| `GET` | `/api/v1/phones/{model_name}` | Return complete specifications for a phone |

---

## Conversational RAG

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat/query` | Return a complete RAG response |
| `POST` | `/api/v1/chat/stream` | Stream the RAG response using SSE |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is the charging speed of the Galaxy S24 Ultra?",
       "reset_history": false
     }'
```

---

# Multi-Agent Review API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/agents/review` | Generate technical dossier and editorial review |
| `POST` | `/api/v1/agents/review/stream` | Stream the generated review |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/agents/review" \
     -H "Content-Type: application/json" \
     -d '{
       "phone_name": "Galaxy S24",
       "review_focus": "Compact ergonomics, battery endurance, and thermal behavior"
     }'
```

---

# Data Flow

The complete application pipeline is:

```text
                    GSMArena
                       |
                       v
                Web Scraper
                       |
                       v
             HTML Parser/Cleaner
                       |
                       v
                 PostgreSQL
                       |
          +------------+------------+
          |                         |
          v                         v
      ChromaDB                LangChain Tools
          |                         |
          v                         v
   Semantic Retrieval        Exact SQL Lookup
          |                         |
          +------------+------------+
                       |
             +---------+---------+
             |                   |
             v                   v
        RAG Engine          Spec Agent
             |                   |
             |                   v
             |             Technical Dossier
             |                   |
             |                   v
             |             Review Agent
             |                   |
             +---------+---------+
                       |
                       v
                  FastAPI API
                       |
                       v
                  User / Client
```

---

# Retrieval Strategy

The system uses different retrieval strategies depending on the query.

### Exact / Entity-Based Queries

Database lookup can retrieve a specific phone using SQLAlchemy statements and case-insensitive matching.

Example:

```text
What is the screen size of the Galaxy S22?
```

The system can perform an exact database lookup instead of relying only on vector similarity.

### Semantic Queries

ChromaDB is used when the question requires semantic matching.

Example:

```text
Which Samsung phone is suitable for long battery usage?
```

### Ranking Queries

Structured SQL queries are preferred for numerical ranking operations.

Example:

```text
Which Samsung phone has the highest battery capacity?
```

This avoids relying on vector similarity for numerical comparisons.

---

# Testing

Run the complete test suite:

```bash
pytest
```

Verbose mode:

```bash
pytest -v -s
```

Run individual test modules:

```bash
pytest tests/test_scraper.py
pytest tests/test_parser.py
pytest tests/test_database.py
pytest tests/test_rag.py
pytest tests/test_agents.py
pytest tests/test_api.py
```

From the project root, you can also run a test module directly:

```bash
python -m tests.test_agents
```

---

# Design Principles

The project follows several important principles:

- **Database-first factual retrieval:** structured specifications should come from PostgreSQL whenever exact values are required.
- **Vector search for semantic relevance:** ChromaDB is used to identify relevant documents, not as the source of truth for numerical operations.
- **Agent specialization:** each agent has a focused responsibility.
- **No unsupported claims:** the LLM should acknowledge missing information instead of inventing specifications.
- **Session-safe database access:** SQLAlchemy ORM objects are accessed while their database session is active.
- **Modern SQLAlchemy style:** use `select()` statements with `Session.execute()` for database queries.
- **Streaming support:** long LLM responses can be streamed through CLI and SSE API interfaces.
- **Separation of concerns:** scraping, storage, retrieval, agents, and API layers remain independently testable.

---

# Project Goals

The project demonstrates an end-to-end production-oriented AI application combining:

```text
Web Scraping
     +
Data Cleaning
     +
PostgreSQL
     +
Vector Search
     +
RAG
     +
LLM Tool Calling
     +
Multi-Agent Architecture
     +
FastAPI
     +
Streaming
     +
Automated Testing
```

It can serve as a foundation for a larger Samsung product intelligence platform with additional models, pricing sources, benchmark data, recommendation systems, and production deployment.

---

# License

This project is licensed under the MIT License.

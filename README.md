# AgentLab

This repository is a FastAPI service built around a LangGraph-based supervisor and research workflow. The application records chat messages in PostgreSQL, invokes a supervisor agent, and uses tool-backed agents for research, email handling, and report generation.

## Overview

The backend is implemented under `backend/src` and starts as a FastAPI app with CORS enabled and a database initialization step in its lifespan handler. The main runtime path is:

- `backend/src/main.py` creates the app and mounts the chat router at `/api/chat`.
- `backend/src/api/chat/router.py` accepts chat messages, stores them in SQLModel tables, and invokes the supervisor.
- `backend/src/api/ai/agents.py` wires together a research team, a report agent, and an email assistant behind a `langgraph-supervisor` supervisor.
- `backend/src/api/ai/tools.py` defines the actual tool functions used by the agents, including web research, arXiv search, image downloads, email dispatch, Gmail inbox reads, and Word report generation.

## What is implemented today

The current implementation includes:

- A FastAPI API with health and chat endpoints.
- SQLModel persistence against PostgreSQL.
- An OpenAI-compatible LLM client via `langchain_openai.ChatOpenAI`.
- A research graph with a `research_node` and `synthesis_node` built with `StateGraph`.
- A supervisor that delegates to research, report, and email agents.
- SMTP-based emailing and Gmail IMAP inbox reading.
- Optional report generation to `.docx` files.

## Architecture

The app is organized as a thin HTTP layer over a set of AI agent modules and integrations.

- `api.db` initializes the SQLModel engine and creates tables.
- `api.chat.models` defines the persisted chat message schema.
- `api.chat.router` performs the request/response loop for chat messages.
- `api.ai.llms` configures the shared LLM client.
- `api.ai.agents` assembles the supervisor and its child agents.
- `api.ai.tools` provides the tool interface for the LLMs.
- `api.myemailer` handles SMTP sending and IMAP reading.

In practical terms, the request flow is:

1. A client sends a message to `POST /api/chat/`.
2. The message is saved in the database.
3. The router calls `get_supervisor()`.
4. The supervisor delegates to the research graph or helper agents as appropriate.
5. The final content from the last message in the graph response is returned to the client.

See [docs/architecture.md](docs/architecture.md) for a more detailed implementation view and [docs/agents.md](docs/agents.md) for the agent workflow.

## Project structure

```text
.
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── api/
│       │   ├── ai/
│       │   │   ├── agents.py
│       │   │   ├── assistants.py
│       │   │   ├── llms.py
│       │   │   ├── prompts.py
│       │   │   ├── research.py
│       │   │   ├── research_context.py
│       │   │   ├── schemas.py
│       │   │   ├── services.py
│       │   │   └── tools.py
│       │   ├── chat/
│       │   │   ├── models.py
│       │   │   └── router.py
│       │   ├── db.py
│       │   └── myemailer/
│       │       ├── gmail_imap_parser.py
│       │       ├── inbox_reader.py
│       │       ├── sender.py
│       │       └── template.html
│       └── main.py
├── docker-compose.yaml
├── .env
├── .env.sample
├── .env.db
├── README.md
├── CODE_DOCUMENTATION.md
└── docs/
   ├── architecture.md
   └── agents.md
```

## Quick start

### Prerequisites

- Docker and Docker Compose
- Python 3.12 is used in the container image, and the backend dependencies are pinned in `backend/requirements.txt`
- A valid OpenAI-compatible API endpoint or model runner
- An email account and app password if you want the email features to work
- A PostgreSQL instance or the included `db_service` container

### Configuration

The repository loads environment variables from the root `.env` file in Docker Compose. The runtime expects the following names:

```env
MY_PROJECT_NAME=Hello World Project
API_KEY=abc123
DATABASE_URL=postgresql+psycopg://dbuser:dbpass@db_service:5432/mydb
OPENAI_BASE_URL=http://model-runner.docker.internal/engines/v1
OPENAI_MODEL_NAME=qwen2.5:3B-Q4_K_M
OPENAI_API_KEY=not-needed
EMAIL_ADDRESS=you@example.com
EMAIL_PASSWORD=your-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
PARALLEL_API_KEY=your-parallel-api-key
```

Notes:

- `api.db` currently defines `DATABASE_URL` directly as a string instead of reading the environment variable, so the value in the code is effectively a fixed Postgres host.
- `api.ai.llms` raises `NotImplementedError` if `OPENAI_BASE_URL` is missing.
- `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `EMAIL_HOST`, and `EMAIL_PORT` are used by the mail sending utilities.

### Run with Docker Compose

From the repository root:

```bash
docker compose up --build
```

This starts:

- `backend` on `http://localhost:8080`
- `db_service` on `localhost:5432`

The backend container runs:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The app endpoint is also reachable at:

- `http://localhost:8080/`
- `http://localhost:8080/health`
- `http://localhost:8080/api/chat/`

### Run locally without Docker

```bash
cd backend
python -m venv .venv
# PowerShell on Windows
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API surface

The application currently exposes the following endpoints from the FastAPI app created in `backend/src/main.py`.

### `GET /`

Returns a simple greeting and the configured project name.

Example response:

```json
{
  "message": "Docker Learn API is running",
  "project_name": "Hello World Project"
}
```

### `GET /health`

Returns:

```json
{ "status": "ok" }
```

### `GET /api/chat/`

Returns:

```json
{ "status": "ok" }
```

### `GET /api/chat/recent/`

Returns the 10 most recent saved chat messages.

### `POST /api/chat/`

Accepts a payload shaped like:

```json
{ "message": "Research the latest update on ..." }
```

The route:

- validates the message payload,
- stores the message in PostgreSQL,
- invokes the supervisor,
- returns the final content from the supervisor response.

This is the main application workflow in the current codebase.

## How the multi-agent workflow works

The supervisor is built in `api.ai.agents.get_supervisor()` using `langgraph_supervisor.create_supervisor` and includes:

- `research_team`
- `report_agent`
- `email_agent`

The research team itself is a LangGraph workflow in `api.ai.research.build_research_team()`:

- `research` node: extracts the user's question and executes tools such as `web_search` and `search_arxiv`
- `synthesis` node: builds an evidence summary and calls the configured LLM with a structured `ResearchResult` schema

The assistant tools are defined in `api.ai.tools` and are registered with the LangChain agent factory through `create_agent`.

## Agent and tool responsibilities

### Research agent

The research workflow is defined by `RESEARCH_SYSTEM_PROMPT` and uses:

- `web_search` for general and current information
- `search_arxiv` for academic papers
- `search_and_save_images` when a visual asset is needed

The `research_context.current_sources` object tracks the sources collected during tool execution, and the synthesis step returns a `ResearchResult` with:

- `answer`
- `sources`
- `confidence`

### Report agent

The report agent uses `generate_report_docx` and the prompt `You generate reports from research results.` It writes a `.docx` report to `/app/reports`.

### Email agent

The email agent uses `send_me_email`, `get_unread_emails`, and `search_and_save_images`. It is designed to compose and send email content related to research or reports.

### Supervisor

The supervisor prompt explicitly instructs it to delegate research tasks to the research agent and email tasks to the email agent. It only routes to the report agent when the request calls for a report or document.

## Data flow and persistence

The app persists chat messages using SQLModel and PostgreSQL.

`backend/src/api/chat/models.py` defines:

- `ChatMessagePayload`: request body schema, with a `message` field
- `ChatMessage`: database table with `id`, `message`, and `created_at`
- `ChatMessageResponseList`: response schema for recent messages

`backend/src/api/db.py` creates the engine and calls `SQLModel.metadata.create_all(engine)` during app startup.

## Email and mailbox integration

The mail functionality is split into two areas:

- `api.myemailer.sender.send_mail` sends email via SMTP to Gmail.
- `api.myemailer.inbox_reader.read_inbox` reads recent unread Gmail messages via IMAP.
- `api.myemailer.gmail_imap_parser.GmailImapParser` contains the lower-level mailbox logic.

The `send_me_email` tool wraps the SMTP sender and accepts:

- `subject`
- `content`
- `attachment_path` (optional)
- `to_email` (optional override)

The `get_unread_emails` tool reads recent inbox data and returns a formatted string for agent consumption.

## Dependencies and external services

The backend depends on:

- FastAPI and uvicorn
- SQLModel and PostgreSQL
- LangChain / LangGraph / LangGraph Supervisor
- OpenAI-compatible models
- `parallel-web` for web search
- `arxiv` for arXiv paper search
- `python-docx` for .docx generation
- Gmail SMTP/IMAP for email features

## Development notes

- The Postgres URL is effectively hard-coded in `backend/src/api/db.py`.
- The app relies on environment variables and a local `.env` file when run via Docker Compose.
- The OpenAI-compatible client has required settings (`OPENAI_BASE_URL`, `OPENAI_MODEL_NAME`, `OPENAI_API_KEY`) and will fail loudly if the base URL is missing.
- The application is set up to run with Docker Compose, which configures the PostgreSQL service and injects environment variables.

## Contributing

Contributions are welcome through GitHub Issues and pull requests. Ongoing improvements are tracked as issues for topics such as async refactors, concurrency fixes, frontend work, error handling, tests, and other incremental enhancements.

## Additional documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/agents.md](docs/agents.md)


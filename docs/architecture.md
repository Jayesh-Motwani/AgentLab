# Architecture

This document describes the repository as it exists in the current codebase, not as a hypothetical target design.

## Runtime entry points

The backend starts from `backend/src/main.py`.

- It builds a FastAPI app using `FastAPI(lifespan=lifespan, title="Docker Learn API", version="1.0.0")`.
- It adds CORS middleware using `CORS_ALLOWED_ORIGINS` from the environment.
- It calls `init_db()` during the app startup lifespan.
- It includes the chat router at `/api/chat`.
- It exposes `/` and `/health` endpoints.

## Database layer

The database layer is implemented in `backend/src/api/db.py`.

- It builds a SQLModel engine using a Postgres URL.
- `init_db()` runs `SQLModel.metadata.create_all(engine)`.
- `get_session()` yields a SQLModel session for dependency injection.

The actual model definitions live in `backend/src/api/chat/models.py`.

- `ChatMessagePayload` is the API request model.
- `ChatMessage` is the persisted SQLModel table.
- `ChatMessageResponseList` is used by the `recent` endpoint.

## Chat API

The API router is in `backend/src/api/chat/router.py`.

The current routes are:

- `GET /api/chat/` -> status response
- `GET /api/chat/recent/` -> last 10 messages
- `POST /api/chat/` -> save a message and invoke the supervisor

The POST route:

1. Accepts a JSON payload with a `message` field.
2. Stores the message in Postgres.
3. Builds a minimal message payload for the supervisor.
4. Calls `get_supervisor().invoke(...)`.
5. Extracts the final `messages[-1]` content and returns it as the HTTP response.

## AI configuration

The LLM configuration lives in `backend/src/api/ai/llms.py`.

It reads:

- `OPENAI_MODEL_NAME`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`

and creates a `ChatOpenAI` client. The file explicitly raises `NotImplementedError` if `OPENAI_BASE_URL` is missing.

## Agent orchestration

The supervisor and agents are assembled in `backend/src/api/ai/agents.py`.

The structure is:

- `get_email_assistant()` -> `create_agent` using the email tools
- `get_report_agent()` -> `create_agent` with report tooling
- `get_supervisor()` -> `create_supervisor(...).compile()` with `research_team`, `report_agent`, `email_agent`

The supervisor uses the shared OpenAI model that comes from `get_openai_llm()`.

## Research workflow

The research workflow is implemented in `backend/src/api/ai/research.py`.

`ResearchState` is a `MessagesState` with:

- `messages`
- `sources`
- `result`

`research_node`:

- reads the latest human question from the conversation state,
- sets a `current_sources` context variable,
- runs a research agent with the configured tools,
- resets the source context before returning the collected source list.

`synthesis_node`:

- reads the latest question,
- assembles retrieved evidence for the LLM,
- calls the model with structured output for `ResearchResult`,
- returns the result and a final AI message containing the JSON payload.

`build_research_team()` compiles a state graph with edges:

- `START -> research`
- `research -> synthesis`
- `synthesis -> END`

## Tools and integrations

`backend/src/api/ai/tools.py` contains the tool functions registered with the agent layer.

### Mail tools

- `send_me_email` -> calls `api.myemailer.sender.send_mail`
- `get_unread_emails` -> calls `api.myemailer.inbox_reader.read_inbox`

### Search tools

- `web_search` -> uses `parallel-web` and a query-rewriting LLM to return `Source` objects
- `search_arxiv` -> uses `arxiv.Client` to collect paper details
- `search_and_save_images` -> downloads Wikimedia Commons images into `/app/images`

### Report tool

- `generate_report_docx` -> writes a Word document into `/app/reports`

## Email subsystem

The mail subsystem is in `backend/src/api/myemailer`.

- `sender.py` sends emails over SMTP to Gmail.
- `inbox_reader.py` reads recent unread emails from Gmail via IMAP using the parser class.
- `gmail_imap_parser.py` handles connection and search logic for the mailbox.
- `template.html` is used to render the HTML email body.

## Configuration assumptions in this repo

The project uses environment-driven configuration for runtime behavior, but not all settings are centralized in the same way.

- `docker-compose.yaml` loads the root `.env` file into the backend container.
- `backend/src/api/db.py` currently uses a hard-coded Postgres URL instead of reading from `DATABASE_URL`.
- `backend/src/api/ai/llms.py` expects the OpenAI-like configuration to exist in the environment.
- Email-related settings are read directly from environment variables by the mail utilities.

This means the repository is designed to be run as a local Dockerized application with a model endpoint and email credentials present in the environment.

## Major design constraint

The current code is a working local backend with a set of agent tools and a supervisor, not a fully generalized multi-service architecture. The HTTP layer is thin, the tool layer is explicit, and the agent graph is assembled in Python rather than being fully separated into multiple microservices.

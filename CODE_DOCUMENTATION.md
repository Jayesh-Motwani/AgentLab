# Current implementation notes

This repository currently contains a FastAPI application with a PostgreSQL-backed chat endpoint and a LangGraph supervisor that can delegate research, email, and report tasks. The documentation here reflects the implementation that is present in the code, not a future state.

## Entry point

- `backend/src/main.py` creates the FastAPI app and includes the chat router.
- The app lifetime calls `init_db()` during startup.
- CORS is configured from the `CORS_ALLOWED_ORIGINS` environment variable.
- The root path (`GET /`) returns a greeting and the configured project name.
- The health endpoint (`GET /health`) returns `{ "status": "ok" }`.

## Database

- `backend/src/api/db.py` creates a SQLModel engine using a Postgres URL and calls `create_all` during initialization.
- `backend/src/api/chat/models.py` defines `ChatMessage`, `ChatMessagePayload`, and `ChatMessageResponseList`.
- Chat messages are stored with an `id` and `created_at` timestamp.

## Chat API

The routes are mounted under `/api/chat` in `backend/src/api/chat/router.py`.

- `GET /api/chat/` -> returns the health response for the chat module.
- `GET /api/chat/recent/` -> returns up to 10 recent messages in descending access order by the current query logic.
- `POST /api/chat/` -> accepts a JSON object with a `message` field, stores it, and then invokes the supervisor.

The call to the supervisor returns the last message content in the result graph state. That string is returned directly to the client as the HTTP response.

## LLM configuration

`backend/src/api/ai/llms.py` builds a `ChatOpenAI` client from environment variables:

- `OPENAI_BASE_URL`
- `OPENAI_MODEL_NAME`
- `OPENAI_API_KEY`

The file raises `NotImplementedError` if `OPENAI_BASE_URL` is not set.

## Research and supervisor workflow

The AI stack is assembled in `backend/src/api/ai/agents.py`.

- `get_email_assistant()` creates an email-focused agent.
- `get_report_agent()` creates a report-focused agent.
- `get_supervisor()` creates a LangGraph supervisor with:
  - `research_team`
  - `report_agent`
  - `email_agent`

The research graph is built in `backend/src/api/ai/research.py`.

- `research_node` extracts the latest human message and executes tools.
- `synthesis_node` reduces the collected evidence into a `ResearchResult`.
- `build_research_team()` connects the nodes in a simple graph: `START -> research -> synthesis -> END`.

## Tools

`backend/src/api/ai/tools.py` contains the tool implementations used by the agents.

- `web_search` - calls `parallel-web` and returns `Source` objects
- `search_arxiv` - queries arXiv and returns `Source` objects
- `search_and_save_images` - downloads Wikimedia Commons images into `/app/images`
- `send_me_email` - wraps the SMTP sender in `api.myemailer.sender`
- `get_unread_emails` - reads received messages via Gmail IMAP
- `generate_report_docx` - writes a `.docx` file to `/app/reports`

## Data schemas

`backend/src/api/ai/schemas.py` defines the core Pydantic models used by the AI layer.

- `EmailMessage`
- `SearchQueries`
- `Source`
- `ResearchResult`
- `ReportFile`
- `SupervisorMessageSchema`

## Email subsystem

The mail functionality is implemented in `backend/src/api/myemailer`.

- `sender.py` sends email through SMTP using the configured Gmail account.
- `inbox_reader.py` reads recent unread messages from Gmail via IMAP.
- `gmail_imap_parser.py` has the lower-level connection and search logic.
- `template.html` is used to format the email body.

## Runtime configuration

The repository expects these environment variables to be present when the application is started:

- `MY_PROJECT_NAME`
- `API_KEY`
- `CORS_ALLOWED_ORIGINS`
- `DATABASE_URL` (effectively fixed in the code today)
- `OPENAI_BASE_URL`
- `OPENAI_MODEL_NAME`
- `OPENAI_API_KEY`
- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `PARALLEL_API_KEY`

## Docker

`docker-compose.yaml` defines:

- `backend` service built from `./backend` and mapped to `localhost:8080`
- `db_service` using PostgreSQL `17.5` and a named volume

The backend container runs `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` and mounts the source directory into the container.

## Important caveats

- `backend/src/api/db.py` uses a hard-coded Postgres URL rather than the environment variable.
- The chat system is synchronous and directly invokes the supervisor on each request.
- The project includes research and email automation, but it is still tightly coupled to the environment and to a specific local deployment setup.

## Related documents

- `README.md`
- `docs/architecture.md`
- `docs/agents.md`


Code Documentation
==================

Purpose
-------
This file documents the current code structure and the intended module responsibilities for the Multi-Agent LangGraph Research & Supervisor System. It reflects the desired completed architecture; as the repository matures this document will be updated with concrete file-level references, function/class signatures, and examples.

Top-level layout (intended)
---------------------------
- app/
  - main.py             # FastAPI app creation and startup events
  - api/
    - v1/
      - tasks.py        # Endpoints for task creation and retrieval
      - agents.py       # Agent management endpoints
  - agents/
    - supervisor.py     # Supervisor agent orchestration logic
    - research_agent.py # Research agent implementation (LangGraph integration)
  - tools/
    - mailer.py         # Email sending wrapper (SMTP or third-party)
    - web_fetch.py      # Simple web fetch/crawler tool used by research agent
  - services/
    - queue.py          # Task queue interface (in-memory or backed by Redis)
    - storage.py        # Result persistence (file or DB)
  - models/
    - schemas.py        # Pydantic models for request/response

Key modules (current responsibilities)
-------------------------------------
- app.main
  - Creates FastAPI app instance
  - Registers routers from app.api.v1
  - Configures startup/shutdown hooks (connect to storage, initialize agents)

- app.api.v1.tasks
  - POST /tasks/research: accept research prompts and enqueue tasks
  - GET /tasks/{id}: return task status and structured results
  - The endpoint function validates input via Pydantic schemas and returns JSON responses consistent with the project's API spec.

- app.api.v1.agents
  - Endpoints to list agents, inspect agent state, and trigger agent-specific actions (e.g., send email)

- app.agents.research_agent
  - Encapsulates LangGraph agent logic: building research plans, invoking tools, composing structured responses.
  - Exposes a minimal interface: run_research(prompt, params) -> ResearchResult

- app.agents.supervisor
  - Manages Agent instances, assigns tasks, monitors progress, and triggers retries or escalations.
  - Interfaces with a task queue and storage to persist progress and final outputs.

- app.tools.mailer
  - Abstracts email sending. Accepts recipients, subject, and body and handles retry/failure semantics.
  - Environment-driven configuration for SMTP or external provider.

- app.services.queue
  - Minimal queue abstraction supporting enqueue/dequeue with acknowledgment semantics. Implementation may be in-memory (for dev) or backed by Redis/RQ for production.

- app.services.storage
  - Simple storage API to save and retrieve task results. Initially file-backed storage is acceptable; a DB-backed implementation can be swapped in later.

Pydantic models
---------------
- TaskCreate
  - prompt: str
  - params: Optional[dict]
  - callback_email: Optional[str]

- TaskStatus
  - task_id: str
  - state: Enum["pending","in_progress","done","failed"]
  - result: Optional[dict]

- AgentInfo
  - id: str
  - kind: str
  - status: str

Tools & integration
-------------------
- LangGraph: the research/supervisor logic assumes a LangGraph-compatible agent interface for creating multi-step plans and chaining tool calls.
- Mailer: composable tool the research agent uses to send final reports or notifications.
- Web fetcher: optional tool for retrieving external references and scraping content.

Docker & deployment
-------------------
- docker-compose.yaml is included to orchestrate the API and worker/agent services.
- Each service should have an associated Dockerfile producing a small, production-ready image.
- Environment variables should be passed using an .env file or CI/CD secret management.

Environment variables (current/expected)
----------------------------------------
- FASTAPI_HOST=0.0.0.0
- FASTAPI_PORT=8000
- DATABASE_URL=file://./data/db.sqlite (optional)
- MAILER_SMTP_HOST
- MAILER_SMTP_PORT
- MAILER_USERNAME
- MAILER_PASSWORD
- REDIS_URL (if Redis queue used)

Testing
-------
- Unit tests should cover: agent orchestration logic, task enqueuing, API request/response validation, and mailer stub behavior.
- Integration tests should validate that a submitted task goes through the queue, is processed by a research agent (mocked LangGraph), and that results are stored and retrievable via the API.

Extending the project
---------------------
- Add persistent storage and a migrations strategy.
- Add authentication & RBAC for API endpoints.
- Add a worker service for long-running research tasks.
- Add observability: request tracing, structured logging, and metrics.

Notes & TODOs
-------------
- Add concrete file-level documentation once modules and functions are implemented.
- Insert docstrings for all public functions and classes.
- Provide example cURL and Python client snippets in the README.

Contact & maintenance
---------------------
As components are implemented, update this file with:
- real module paths
- function/class signatures
- examples and code snippets


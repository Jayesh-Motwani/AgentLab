Multi-Agent Research & Supervisor System

Project overview
----------------
This repository implements a multi-agent system designed to run research tasks and supervised coordination using LangGraph-based agents. The project is wrapped in FastAPI endpoints and is prepared for containerized deployment with Docker and docker-compose.

High-level components
---------------------
- LangGraph Research Agent
  - A research-focused agent that can perform layered research tasks, gather references and data, and invoke outgoing actions such as sending emails through integrated tools.
  - Integrates with external "tools" (e.g., mailer, web fetchers, knowledge stores) to expand capabilities beyond pure language reasoning.

- LangGraph Supervisor
  - Supervises one or more research agents, coordinates their workload, validates outputs, and escalates or re-routes tasks when needed.

- FastAPI wrapper
  - HTTP API endpoints to create tasks, query agent status, request research jobs, and retrieve results.
  - Endpoints are organized and ready for extension as agents and tooling expand.

- Docker deployment
  - Dockerfile(s) and docker-compose configuration are provided to containerize the API and agents for easy deployment and scaling.

Project status
--------------
The codebase is an early-stage implementation. The README and code documentation assume the final architecture described above; however, some features and integrations are still incomplete and planned to be added incrementally. The documentation will be updated as the code matures.

Key features (planned / partial)
- Research agent capable of running multi-step research plans and returning structured output.
- Supervisor agent capable of managing task queues and agent orchestration.
- Email-tool integration for sending reports and notifications.
- FastAPI endpoints to submit tasks and retrieve results.
- Docker and docker-compose manifests to deploy services as containers.

Quickstart (local development)
-----------------------------
Prerequisites
- Docker and docker-compose installed
- Python 3.10+ (for local dev without containers)
- Git and a GitHub remote configured

Run with docker-compose (recommended)
1. From the repository root:

   docker-compose up --build

2. Once services are up, the FastAPI service should be accessible at:

   http://localhost:8000/

3. Open the automatic docs (if enabled) at:

   http://localhost:8000/docs

Run locally without Docker (development)
1. Create and activate a virtual environment

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # PowerShell on Windows

2. Install dependencies (project's requirements file may be added later):

   pip install -r requirements.txt

3. Start the FastAPI app (example using uvicorn):

   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

API overview (example)
----------------------
Note: the API surface below reflects the intended, completed project - some endpoints may be placeholders in the current code.

- POST /tasks/research
  - Create a new research task. Body: research prompt, parameters, callback email (optional).

- GET /tasks/{task_id}
  - Retrieve the status and results for a specific research task.

- POST /agents/{agent_id}/email
  - Ask an agent to send an email using the configured mail tool. Body: subject, recipients, body (text or HTML).

- GET /agents
  - List registered agents and status summary.

Architecture diagram
--------------------
(Planned)

[Client] <--> [FastAPI HTTP Layer] <--> [Supervisor Agent] <--> [Research Agents]
                                         \--> [Tools: Mailer, Web fetch, Storage]

Contributing
------------
Currently not accepting Contributions until desired v1 stage is reached.

License
-------
N/A

Acknowledgements
----------------
This project scaffolds a LangGraph-based multi-agent research system. Documentation will be expanded as components are implemented. Only the Documentation and Readme has been created using Copilot or AI, everything else being completely Human Generated/Written.

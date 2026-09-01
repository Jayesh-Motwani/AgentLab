# Agents and workflow

This repository defines a small multi-agent setup around a supervisor and a research graph.

## Supervisor

The supervisor is created in `backend/src/api/ai/agents.py`:

```python
supervisor = create_supervisor(
    agents=[
        research_team,
        report_agent,
        email_agent,
    ],
    model=llm,
    prompt=SUPERVISOR_PROMPT,
).compile()
```

It is exposed as `get_supervisor()` and is called by the chat router after a message is saved.

The supervisor prompt tells the model to:

- route research requests to the research agent,
- route email-related work to the email agent,
- only involve the report agent when a report is explicitly requested.

## Research team

The `research_team` is built by `build_research_team()` in `backend/src/api/ai/research.py`.

The graph has two functional nodes:

- `research`: gathers evidence with tool calls
- `synthesis`: turns evidence into a structured `ResearchResult`

The `research` node reads the latest user message from the graph state and calls the research agent. The research agent uses the tools registered in `get_research_agent()`:

- `web_search`
- `search_arxiv`
- `search_and_save_images`

`current_sources` is a context-local list used to accumulate all discovered sources during research. The final synthesis step returns evidence-backed results with citations-like metadata in the `Source` objects.

## Report agent

The report agent is created in `backend/src/api/ai/agents.py` and uses:

- `generate_report_docx`
- the prompt `You generate reports from research results.`

The report tool writes a `.docx` file into `/app/reports`.

## Email agent

The email agent is created in the same file and uses:

- `search_and_save_images`
- `send_me_email`
- `get_unread_emails`

The prompt in `backend/src/api/ai/prompts.py` tells the model to:

- send the email only when the user asked for it,
- attach a saved image when the request includes one,
- never claim an email was sent unless the tool returns success.

## Message flow from HTTP to agent response

The current request path is:

1. Client posts to `POST /api/chat/`.
2. The router saves the message in the database.
3. The router calls `get_supervisor()`.
4. The supervisor delegates based on the user prompt.
5. The last message from the returned graph state is extracted and sent back as the HTTP response.

This means the chat API is acting as the orchestrator for the LangGraph workflow, even though the data model is still very lightweight.

## Tool-backed responsibilities

The repo uses a direct tool model rather than a separate orchestrator service:

- The agents are plain LangChain agents generated with `create_agent`.
- The tools are Python functions decorated with `@tool` when they are meant to be invoked by the LLM.
- Some tool outputs are plain strings, while others return structured `Source` or `ResearchResult` models.

This is the exact mechanism used to rebuild and return research results and email/report content.

## Relevant code locations

- `backend/src/api/chat/router.py` - entry point for the user message
- `backend/src/api/ai/agents.py` - setup of supervisor and agents
- `backend/src/api/ai/research.py` - research graph and synthesis
- `backend/src/api/ai/tools.py` - concrete tool implementations
- `backend/src/api/ai/prompts.py` - prompts used to steer the agents
- `backend/src/api/ai/schemas.py` - structured outputs for research and report data

## Important runtime note

The repository does not currently provide a dedicated status API or task queue for the agents. The user request is handled synchronously through the chat endpoint, and each call invokes the supervisor and tools directly.

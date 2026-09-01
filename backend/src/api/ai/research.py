from typing import TypedDict

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState

from api.ai.llms import get_openai_llm
from api.ai.tools import (
    web_search,
    search_arxiv,
    search_and_save_images,
)
from api.ai.prompts import RESEARCH_SYSTEM_PROMPT
from api.ai.schemas import Source, ResearchResult
import json
from api.ai.research_context import current_sources
import ast


class ResearchState(MessagesState):
    sources: list[Source]
    result: ResearchResult


def get_research_agent():
    model = get_openai_llm()

    return create_agent(
        model=model,
        tools=[
            web_search,
            search_arxiv,
            search_and_save_images,
        ],
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        name="research_agent",
    )


def research_node(state: ResearchState):
    query = next(
        message.content
        for message in reversed(state["messages"])
        if isinstance(message, HumanMessage)
    )

    print(f"[RESEARCH] query: {query}")

    sources = []

    token = current_sources.set(sources)

    try:
        agent = get_research_agent()

        agent.invoke({
            "messages": [HumanMessage(content=query)]
        })

    finally:
        current_sources.reset(token)

    print(f"[RESEARCH] collected {len(sources)} sources")

    return {
        "sources": sources
    }


def synthesis_node(state: ResearchState):
    query = next(
        message.content
        for message in reversed(state["messages"])
        if isinstance(message, HumanMessage)
    )

    llm = get_openai_llm().with_structured_output(ResearchResult)

    evidence = "\n\n".join(
        f"""
SOURCE {i}
Title: {source.title}
URL: {source.url}
Publisher: {source.publisher}
Evidence:
{source.excerpt}
"""
        for i, source in enumerate(state["sources"], 1)
    )

    result = llm.invoke([
        (
            "system",
            """
You are a grounded research synthesizer.

Answer the research question using ONLY the supplied retrieved evidence.

Rules:
- Answer the actual research question.
- Every factual claim must be supported by the supplied evidence.
- Never invent facts, papers, authors, dates, URLs, experiments, measurements,
  or results.
- Do not discuss the research team's workflow, transfers, or agent orchestration.
- Do not use pretrained knowledge as evidence.
- Only cite sources present in the supplied evidence.
- Preserve source titles and URLs exactly.
- If evidence is insufficient, say exactly what information is missing.
"""
        ),
        (
            "human",
            f"""
Research question:
{query}

Retrieved evidence:
{evidence}
"""
        ),
    ])

    return {
        "result": result,
        "messages": [
            AIMessage(content=result.model_dump_json())
        ],
    }


def build_research_team():
    graph = StateGraph(ResearchState)

    graph.add_node("research", research_node)
    graph.add_node("synthesis", synthesis_node)

    graph.add_edge(START, "research")
    graph.add_edge("research", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile(name="research_team")

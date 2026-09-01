from langchain.agents import create_agent

from api.ai.llms import get_openai_llm
from api.ai.tools import *
from api.ai.prompts import (
    EMAIL_SYSTEM_PROMPT,
    SUPERVISOR_PROMPT,
)

from api.ai.research import build_research_team

from langgraph_supervisor import create_supervisor


EMAIL_TOOLS = {
    "search_and_save_images": search_and_save_images,
    "send_me_email": send_me_email,
    "get_unread_emails": get_unread_emails,
}

EMAIL_TOOLS_LIST = list(EMAIL_TOOLS.values())


REPORT_TOOLS = {
    "generate_report_docx": generate_report_docx,
}

REPORT_TOOLS_LIST = list(REPORT_TOOLS.values())


def get_email_assistant():
    model = get_openai_llm()

    return create_agent(
        model=model,
        tools=EMAIL_TOOLS_LIST,
        system_prompt=EMAIL_SYSTEM_PROMPT,
        name="email_agent",
    )


def get_report_agent():
    model = get_openai_llm()

    return create_agent(
        model=model,
        tools=REPORT_TOOLS_LIST,
        system_prompt="You generate reports from research results.",
        name="report_agent",
    )


def get_supervisor():
    llm = get_openai_llm()

    research_team = build_research_team()
    report_agent = get_report_agent()
    email_agent = get_email_assistant()

    supervisor = create_supervisor(
        agents=[
            research_team,
            report_agent,
            email_agent,
        ],
        model=llm,
        prompt=SUPERVISOR_PROMPT,
    ).compile()

    return supervisor
